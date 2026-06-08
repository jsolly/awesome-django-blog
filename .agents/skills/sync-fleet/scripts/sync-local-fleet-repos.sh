#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: sync-local-fleet-repos.sh [options]

Discover app repos with .agents/FLEET.lock and run scripts/update-agents-subtree.sh
in each clean checkout.

Options:
  --scan-root <path>   Directory to search. Default: ~/code (or FLEET_SCAN_ROOT).
  --repo <name>        Sync one repo basename under the scan root.
  --dry-run            Print actions without running updaters.
  --with-local-runtime Re-run install-local-agent-runtime.sh personal after sync.
  --help               Show this help.

Environment:
  FLEET_SCAN_ROOT      Default scan root when --scan-root is omitted.
  DOTAGENTS_ROOT       dotagents checkout for --with-local-runtime. Default: ~/code/dotagents.

Stdout: JSON summary. Stderr: per-repo progress.
USAGE
}

SCAN_ROOT="${FLEET_SCAN_ROOT:-$HOME/code}"
DOTAGENTS_ROOT="${DOTAGENTS_ROOT:-$HOME/code/dotagents}"
DRY_RUN=0
WITH_LOCAL_RUNTIME=0
ONLY_REPO=""
MATCHED_ONLY_REPO=0
FAILED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scan-root)
      SCAN_ROOT="$2"
      shift 2
      ;;
    --repo)
      ONLY_REPO="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --with-local-runtime)
      WITH_LOCAL_RUNTIME=1
      shift
      ;;
    --help | -h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$SCAN_ROOT" ]]; then
  echo "Scan root not found: $SCAN_ROOT" >&2
  exit 1
fi

TARGET_FLEET_SHA=""

discover_lockfiles() {
  find "$SCAN_ROOT" -maxdepth 4 -path '*/.agents/FLEET.lock' 2>/dev/null | sort -u
}

repo_from_lockfile() {
  local lockfile="$1"
  (cd "$(dirname "$lockfile")/.." && pwd)
}

repo_name() {
  basename "$1"
}

read_fleet_sha() {
  local repo="$1"
  grep '^sha:' "$repo/.agents/FLEET.lock" 2>/dev/null | awk '{print $2}' || true
}

list_skills() {
  local repo="$1"
  if [[ -d "$repo/.agents/skills" ]]; then
    ls -1 "$repo/.agents/skills" 2>/dev/null | tr '\n' ' ' | sed 's/ $//'
  fi
}

ahead_of_origin() {
  local repo="$1"
  git -C "$repo" rev-list --count @{u}..HEAD 2>/dev/null || echo "0"
}

fetch_target_fleet_sha() {
  local probe="$1"
  if ! git -C "$probe" remote get-url dotagents &>/dev/null 2>&1; then
    return 1
  fi
  git -C "$probe" fetch dotagents fleet >/dev/null 2>&1
  git -C "$probe" rev-parse dotagents/fleet^{commit} 2>/dev/null
}

sync_repo() {
  local repo="$1"
  local name status note sha skills ahead

  name="$(repo_name "$repo")"
  sha="$(read_fleet_sha "$repo")"
  skills="$(list_skills "$repo")"
  ahead="$(ahead_of_origin "$repo")"

  if [[ -n "$ONLY_REPO" && "$name" != "$ONLY_REPO" ]]; then
    return 0
  fi
  if [[ -n "$ONLY_REPO" ]]; then
    MATCHED_ONLY_REPO=1
  fi

  if [[ ! -f "$repo/scripts/update-agents-subtree.sh" ]]; then
    status="skipped_no_shim"
    note="missing scripts/update-agents-subtree.sh"
    emit_repo_json "$name" "$status" "$sha" "$skills" "$ahead" "$note"
    return 0
  fi

  if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
    status="skipped_dirty"
    note="uncommitted changes"
    emit_repo_json "$name" "$status" "$sha" "$skills" "$ahead" "$note"
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    status="dry_run"
    note="would run update-agents-subtree.sh"
    emit_repo_json "$name" "$status" "$sha" "$skills" "$ahead" "$note"
    return 0
  fi

  echo "Syncing $name ..." >&2
  local before="$sha"
  if (cd "$repo" && bash scripts/update-agents-subtree.sh); then
    sha="$(read_fleet_sha "$repo")"
    skills="$(list_skills "$repo")"
    ahead="$(ahead_of_origin "$repo")"
    if [[ "$before" == "$sha" && "$before" == "$TARGET_FLEET_SHA" ]]; then
      status="already_current"
      note="converge only or no-op"
    else
      status="synced"
      note=""
    fi
    emit_repo_json "$name" "$status" "$sha" "$skills" "$ahead" "$note"
    return 0
  fi

  status="failed"
  note="update-agents-subtree.sh exited non-zero"
  FAILED=1
  emit_repo_json "$name" "$status" "$sha" "$skills" "$ahead" "$note"
  return 0
}

emit_repo_json() {
  local name="$1" status="$2" sha="$3" skills="$4" ahead="$5" note="$6"
  REPO_JSON+=("$(node -e '
const [name, status, fleetSha, skills, ahead, note] = process.argv.slice(1);
process.stdout.write(JSON.stringify({ name, status, fleetSha, skills: skills.split(/\s+/).filter(Boolean), aheadOfOrigin: Number(ahead), note }));
' "$name" "$status" "$sha" "$skills" "$ahead" "$note")")
}

REPO_JSON=()
PROBE_REPO=""
while IFS= read -r lockfile; do
  repo="$(repo_from_lockfile "$lockfile")"
  if [[ -z "$PROBE_REPO" && -f "$repo/scripts/update-agents-subtree.sh" ]]; then
    PROBE_REPO="$repo"
  fi
done < <(discover_lockfiles)

if [[ -n "$PROBE_REPO" ]]; then
  TARGET_FLEET_SHA="$(fetch_target_fleet_sha "$PROBE_REPO" || true)"
fi

while IFS= read -r lockfile; do
  sync_repo "$(repo_from_lockfile "$lockfile")"
done < <(discover_lockfiles)

if [[ "$WITH_LOCAL_RUNTIME" -eq 1 && "$DRY_RUN" -eq 0 ]]; then
  if [[ -x "$DOTAGENTS_ROOT/scripts/install-local-agent-runtime.sh" ]]; then
    echo "Wiring local agent runtime from $DOTAGENTS_ROOT ..." >&2
    bash "$DOTAGENTS_ROOT/scripts/install-local-agent-runtime.sh" personal >&2
  else
    echo "Missing $DOTAGENTS_ROOT/scripts/install-local-agent-runtime.sh" >&2
  fi
fi

node -e '
const [scanRoot, targetFleetSha, dryRun, ...repoLines] = process.argv.slice(1);
const repos = repoLines.map((line) => JSON.parse(line));
process.stdout.write(JSON.stringify({
  scanRoot,
  targetFleetSha: targetFleetSha || null,
  dryRun: dryRun === "1",
  count: repos.length,
  repos,
}, null, 2) + "\n");
' "$SCAN_ROOT" "$TARGET_FLEET_SHA" "$DRY_RUN" "${REPO_JSON[@]}"

if [[ -n "$ONLY_REPO" && "$MATCHED_ONLY_REPO" -eq 0 ]]; then
  echo "No fleet repo named '$ONLY_REPO' under $SCAN_ROOT" >&2
  exit 1
fi

if [[ "$FAILED" -ne 0 ]]; then
  exit 1
fi
