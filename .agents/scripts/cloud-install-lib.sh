#!/usr/bin/env bash
# Shared Cursor Cloud install helpers. Source from repo scripts/cloud-agent-install.sh:
#   source "$(cd "$(dirname "$0")/.." && pwd)/.agents/scripts/cloud-install-lib.sh"
#
# Provides: ensure_node_version, use_node_for_cursor_cloud, install_zip_unzip, install_aws_cli, install_sam, install_yaml_linters

ensure_node_version() {
	local required_major
	required_major="$(cat .nvmrc 2>/dev/null || echo 24)"
	required_major="${required_major%%.*}"

	if command -v node >/dev/null 2>&1; then
		local major
		major="$(node -p "process.versions.node.split('.')[0]")"
		if [[ "$major" -ge "$required_major" ]]; then
			node -v
			return 0
		fi
	fi

	if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
		# shellcheck source=/dev/null
		. "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
		nvm install "$required_major"
		nvm use "$required_major"
		node -v
		return 0
	fi

	echo "Node ${required_major} required but nvm unavailable" >&2
	exit 1
}

# Cursor cloud VMs put /exec-daemon Node 22 ahead of nvm on PATH — ensure_node_version alone is not enough.
use_node_for_cursor_cloud() {
	local required_major
	required_major="$(tr -d '[:space:]' < .nvmrc 2>/dev/null || echo 24)"
	required_major="${required_major%%.*}"

	ensure_node_version

	if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
		# shellcheck source=/dev/null
		. "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
		export PATH="$(dirname "$(nvm which "$required_major")"):$PATH"
	fi

	local major
	major="$(node -p "process.versions.node.split('.')[0]")"
	if [[ "$major" -lt "$required_major" ]]; then
		echo "Expected Node >= ${required_major}, got: $(node -v)" >&2
		exit 1
	fi

	persist_cursor_node_shell "$required_major"
	node -v
}

persist_cursor_node_shell() {
	local required_major="${1:-24}"
	local marker="cursor-cloud-agent-node${required_major}"
	local profile="$HOME/.bashrc"

	if [[ ! -f "$profile" ]] || grep -q "$marker" "$profile" 2>/dev/null; then
		return 0
	fi

	cat >>"$profile" <<EOF

# --- ${marker} (fleet cloud-install-lib.sh) ---
export NVM_DIR="\${NVM_DIR:-\$HOME/.nvm}"
[ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"
nvm install ${required_major} >/dev/null 2>&1 || true
nvm use ${required_major} >/dev/null 2>&1 || true
if nvm which ${required_major} >/dev/null 2>&1; then
  export PATH="\$(dirname "\$(nvm which ${required_major})"):\$PATH"
fi
# --- end ${marker} ---
EOF
}

install_zip_unzip() {
	if ! command -v apt-get >/dev/null 2>&1; then
		return 0
	fi
	for pkg in zip unzip; do
		if ! command -v "$pkg" >/dev/null 2>&1; then
			sudo apt-get update -qq
			sudo apt-get install -y -qq zip unzip
			break
		fi
	done
}

install_sam() {
	install_zip_unzip
	if command -v sam >/dev/null 2>&1; then
		sam --version
		return 0
	fi
	local arch sam_arch
	arch="$(uname -m)"
	case "$arch" in
		aarch64 | arm64) sam_arch=arm64 ;;
		x86_64 | amd64) sam_arch=x86_64 ;;
		*)
			echo "Unsupported architecture for SAM CLI install: $arch" >&2
			exit 1
			;;
	esac
	curl -fsSL "https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-${sam_arch}.zip" \
		-o /tmp/sam.zip
	unzip -q /tmp/sam.zip -d /tmp/sam
	sudo /tmp/sam/install
	sam --version
}

install_aws_cli() {
	if command -v aws >/dev/null 2>&1; then
		aws --version
		return 0
	fi
	install_zip_unzip
	local arch aws_arch
	arch="$(uname -m)"
	case "$arch" in
		aarch64 | arm64) aws_arch=aarch64 ;;
		x86_64 | amd64) aws_arch=x86_64 ;;
		*)
			echo "Unsupported architecture for AWS CLI install: $arch" >&2
			exit 1
			;;
	esac
	curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${aws_arch}.zip" -o /tmp/awscliv2.zip
	# Zip root is `aws/` — extract to /tmp so install lands at /tmp/aws/install.
	rm -rf /tmp/aws
	unzip -q /tmp/awscliv2.zip -d /tmp
	sudo /tmp/aws/install
	aws --version
}

install_yaml_linters() {
	# Pin versions to match stocktextalerts CI (noDeploy.yml).
	if ! command -v yamllint >/dev/null 2>&1; then
		if command -v pipx >/dev/null 2>&1; then
			pipx install yamllint==1.38.0
		elif command -v pip3 >/dev/null 2>&1; then
			pip3 install --user yamllint==1.38.0
		else
			echo "yamllint not found and pipx/pip3 unavailable" >&2
			exit 1
		fi
	fi
	if ! command -v actionlint >/dev/null 2>&1; then
		bash <(curl -sSf https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 1.7.12
		sudo mv actionlint /usr/local/bin/actionlint
	fi
	yamllint --version
	actionlint -version
}
