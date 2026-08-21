#!/usr/bin/env bash
# Federate this Cloud Agent VM into IAM role agent-readonly via vendor OIDC.
# Laptop agents use Identity Center AgentReadOnly instead — this script no-ops
# when no cloud OIDC identity is present.
#
# Install/start writes ~/.aws/config with credential_process (no static keys).
# `aws` then mints a JWT and assumes the role at use time; the CLI caches until
# Expiration. Do not persist Build-time STS keys — they expire in 1h and install
# does not re-run on later agent starts.
set -euo pipefail

ROLE_ARN="${AWS_ROLE_ARN:-arn:aws:iam::730335616323:role/agent-readonly}"
SESSION_NAME="${AWS_ROLE_SESSION_NAME:-cloud-agent}"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
CURSOR_SOCK="${CURSOR_AGENT_SOCKET:-/run/cursor/api.sock}"
HELPER="${HOME}/.local/bin/aws-oidc-login.sh"
CREDENTIAL_PROCESS=0
if [[ "${1:-}" == "--credential-process" ]]; then
  CREDENTIAL_PROCESS=1
fi

log() {
  if [[ "$CREDENTIAL_PROCESS" -eq 1 ]]; then
    echo "aws-oidc-login: $*" >&2
  else
    echo "aws-oidc-login: $*"
  fi
}

install_aws_cli() {
  if command -v aws >/dev/null 2>&1; then
    return 0
  fi
  log "installing AWS CLI v2"
  local arch bundle dest
  arch="$(uname -m)"
  case "$arch" in
    aarch64 | arm64) bundle="awscli-exe-linux-aarch64.zip" ;;
    x86_64) bundle="awscli-exe-linux-x86_64.zip" ;;
    *)
      log "unsupported arch ${arch}; install aws CLI manually" >&2
      return 1
      ;;
  esac
  dest="$(mktemp -d)"
  curl -fsSL "https://awscli.amazonaws.com/${bundle}" -o "${dest}/awscliv2.zip"
  unzip -q "${dest}/awscliv2.zip" -d "$dest"
  if [[ "$(id -u)" -eq 0 ]]; then
    "${dest}/aws/install"
  elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
    sudo "${dest}/aws/install"
  else
    mkdir -p "${HOME}/.local/bin"
    "${dest}/aws/install" -i "${HOME}/.local/aws-cli" -b "${HOME}/.local/bin"
    if [[ -d /etc/profile.d && -w /etc/profile.d ]]; then
      printf 'export PATH="%s/.local/bin:$PATH"\n' "$HOME" >/etc/profile.d/aws-local-bin.sh
    fi
    # Non-login bash -c still misses ~/.local/bin; prefer sudo install above.
    export PATH="${HOME}/.local/bin:${PATH}"
    if [[ -w /usr/local/bin ]]; then
      ln -sfn "${HOME}/.local/bin/aws" /usr/local/bin/aws
    elif command -v sudo >/dev/null 2>&1; then
      sudo ln -sfn "${HOME}/.local/bin/aws" /usr/local/bin/aws || true
    fi
  fi
  rm -rf "$dest"
  command -v aws >/dev/null 2>&1 || {
    log "aws CLI not on PATH after install" >&2
    return 1
  }
}

extract_oidc_token() {
  python3 -c '
import json, sys
raw = sys.stdin.read().strip()
if raw.startswith("eyJ"):
    print(raw)
    raise SystemExit(0)
data = json.loads(raw)
for key in ("token", "oidc_token", "id_token", "access_token"):
    value = data.get(key)
    if isinstance(value, str) and value:
        print(value)
        raise SystemExit(0)
raise SystemExit("no token in OIDC response")
'
}

jwt_sub() {
  python3 -c '
import base64, json, sys
parts = sys.argv[1].split(".")
if len(parts) < 2:
    raise SystemExit(0)
pad = "=" * ((4 - len(parts[1]) % 4) % 4)
payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
print(payload.get("sub", ""))
' "$1"
}

prefer_oidc_chain() {
  # Env static keys and Cursor's proprietary AssumeRole beat credential_process.
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  unset CURSOR_AWS_ASSUME_IAM_ROLE_ARN
  export AWS_CONFIG_FILE="${HOME}/.aws/config"
  export AWS_PROFILE=agent-readonly
  export AWS_REGION="$REGION"
  export AWS_DEFAULT_REGION="$REGION"
}

append_aws_exports() {
  local rc="$1"
  touch "$rc"
  if ! grep -q 'AWS_PROFILE=agent-readonly' "$rc" 2>/dev/null; then
    cat >> "$rc" <<EOF

# Cloud Agent AWS read role (vendor OIDC → agent-readonly)
export AWS_PROFILE=agent-readonly
export AWS_REGION=${REGION}
export AWS_DEFAULT_REGION=${REGION}
export PATH="\$HOME/.local/bin:/usr/local/bin:\$PATH"
EOF
  fi
  if ! grep -q 'unset AWS_ACCESS_KEY_ID' "$rc" 2>/dev/null; then
    cat >> "$rc" <<'EOF'
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
unset CURSOR_AWS_ASSUME_IAM_ROLE_ARN
export AWS_CONFIG_FILE="$HOME/.aws/config"
EOF
  fi
}

install_helper() {
  mkdir -p "$(dirname "$HELPER")"
  local src
  src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
  if [[ "$src" != "$HELPER" ]]; then
    cp "$src" "$HELPER"
  fi
  chmod 0755 "$HELPER"
}

write_profile() {
  mkdir -p "${HOME}/.aws"
  umask 077
  rm -f "${HOME}/.aws/credentials"
  # credential_process so later agent starts (and calls after 1h) mint fresh
  # STS creds. [default] covers non-login bash -c that never sources bashrc.
  cat > "${HOME}/.aws/config" <<EOF
[default]
credential_process = ${HELPER} --credential-process
region = ${REGION}
output = json

[profile agent-readonly]
credential_process = ${HELPER} --credential-process
region = ${REGION}
output = json
EOF
  append_aws_exports "${HOME}/.bashrc"
  append_aws_exports "${HOME}/.profile"
  prefer_oidc_chain
}

assume_web_identity_json() {
  local token="$1"
  # Do not load this profile's credential_process (infinite recursion).
  env -u AWS_PROFILE -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
    AWS_EC2_METADATA_DISABLED=true \
    AWS_CONFIG_FILE=/dev/null \
    AWS_SHARED_CREDENTIALS_FILE=/dev/null \
    aws sts assume-role-with-web-identity \
    --role-arn "$ROLE_ARN" \
    --role-session-name "$SESSION_NAME" \
    --web-identity-token "$token" \
    --duration-seconds 3600 \
    --region "$REGION" \
    --output json
}

mint_cursor_jwt() {
  local raw
  raw="$(
    curl --fail --silent --show-error --unix-socket "$CURSOR_SOCK" \
      -H "Content-Type: application/json" \
      -d '{"aud":"sts.amazonaws.com"}' \
      http://localhost/v1/tokens/oidc
  )"
  printf '%s' "$raw" | extract_oidc_token
}

wait_for_cursor_sock() {
  on_cursor_host=0
  if [[ -n "${CURSOR_AGENT_SOCKET:-}" || -d /run/cursor ]]; then
    on_cursor_host=1
    i=0
    while [[ ! -S "$CURSOR_SOCK" && "$i" -lt 6 ]]; do
      log "waiting for OIDC socket ${CURSOR_SOCK}"
      sleep 2
      i=$((i + 1))
    done
  fi
}

emit_credential_process() {
  local token creds
  token="$(mint_cursor_jwt)"
  creds="$(assume_web_identity_json "$token")"
  python3 -c '
import json, sys
c = json.loads(sys.argv[1])["Credentials"]
print(json.dumps({
    "Version": 1,
    "AccessKeyId": c["AccessKeyId"],
    "SecretAccessKey": c["SecretAccessKey"],
    "SessionToken": c["SessionToken"],
    "Expiration": c["Expiration"],
}))
' "$creds"
}

wait_for_cursor_sock

if [[ "$CREDENTIAL_PROCESS" -eq 1 ]]; then
  if [[ ! -S "$CURSOR_SOCK" ]]; then
    log "OIDC socket missing (${CURSOR_SOCK})" >&2
    exit 1
  fi
  emit_credential_process
  exit 0
fi

if [[ -S "$CURSOR_SOCK" ]]; then
  install_aws_cli
  install_helper
  log "Cursor Cloud OIDC socket at ${CURSOR_SOCK}"
  token="$(mint_cursor_jwt)"
  sub="$(jwt_sub "$token")"
  log "minted JWT sub=${sub:-unknown}"
  write_profile
  identity="$(aws sts get-caller-identity --profile agent-readonly --region "$REGION" --output json)"
  printf '%s\n' "$identity"
  arn="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["Arn"])' "$identity")"
  case "$arn" in
    *:assumed-role/agent-readonly/*) ;;
    *)
      log "expected assumed-role/agent-readonly, got ${arn}" >&2
      exit 1
      ;;
  esac
  log "assumed ${ROLE_ARN} as profile agent-readonly"
  exit 0
fi

if [[ "${on_cursor_host:-0}" -eq 1 ]]; then
  log "Cursor Cloud OIDC socket missing after wait (${CURSOR_SOCK}); fail" >&2
  exit 1
fi

if [[ -n "${CLAUDE_CODE:-}" || -n "${CLAUDE_CODE_REMOTE:-}" || -n "${ANTHROPIC_CLOUD_AGENT:-}" ]]; then
  log "Claude cloud OIDC issuer not configured yet; skip"
  exit 0
fi

if [[ -n "${CODEX_CLOUD:-}" || -n "${OPENAI_CODEX_CLOUD:-}" ]]; then
  log "Codex cloud OIDC issuer not configured yet; skip"
  exit 0
fi

log "no cloud-agent OIDC identity; skip"
exit 0
