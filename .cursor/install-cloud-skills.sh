#!/usr/bin/env bash
# Install public jsolly/agent-skills into the Cursor Cloud Agent home skills path.
# Cursor searches /home/ubuntu/.cursor/skills on cloud VMs (forum confirmation 2026-06).
# Idempotent: safe to re-run from environment.json install/update.
set -euo pipefail

SKILLS_HOME="${CURSOR_CLOUD_SKILLS_HOME:-${HOME}/.cursor/skills}"
MIRROR_URL="${AGENT_SKILLS_MIRROR_URL:-https://github.com/jsolly/agent-skills.git}"
MIRROR_REF="${AGENT_SKILLS_MIRROR_REF:-main}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

echo "cloud-skills: cloning ${MIRROR_URL}@${MIRROR_REF} (shallow)"
git clone --depth 1 --branch "$MIRROR_REF" "$MIRROR_URL" "$tmpdir/agent-skills"

src="$tmpdir/agent-skills/skills"
if [[ ! -d "$src" ]]; then
  echo "cloud-skills: ERROR — no skills/ directory in mirror checkout" >&2
  exit 1
fi

mkdir -p "$SKILLS_HOME"
installed=0
for skill_dir in "$src"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "$skill_dir")"
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "cloud-skills: skip ${name} (no SKILL.md)"
    continue
  fi
  dest="$SKILLS_HOME/$name"
  rm -rf "$dest"
  cp -R "$skill_dir" "$dest"
  installed=$((installed + 1))
  echo "cloud-skills: installed ${name} → ${dest}"
done

echo "cloud-skills: done (${installed} skill(s) under ${SKILLS_HOME})"
