#!/usr/bin/env bash
# Install the full public jsolly/agent-skills package into Cursor Cloud Agent home paths.
# Skills → ~/.cursor/skills; agents → ~/.cursor/agents; cited rules → ~/.cursor/agent-skills-package/rules
# Idempotent: safe to re-run from environment.json install/update.
set -euo pipefail

SKILLS_HOME="${CURSOR_CLOUD_SKILLS_HOME:-${HOME}/.cursor/skills}"
AGENTS_HOME="${CURSOR_CLOUD_AGENTS_HOME:-${HOME}/.cursor/agents}"
RULES_HOME="${CURSOR_CLOUD_PACKAGE_RULES:-${HOME}/.cursor/agent-skills-package/rules}"
MIRROR_URL="${AGENT_SKILLS_MIRROR_URL:-https://github.com/jsolly/agent-skills.git}"
MIRROR_REF="${AGENT_SKILLS_MIRROR_REF:-main}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

echo "cloud-package: cloning ${MIRROR_URL}@${MIRROR_REF} (shallow)"
git clone --depth 1 --branch "$MIRROR_REF" "$MIRROR_URL" "$tmpdir/agent-skills"
root="$tmpdir/agent-skills"

# --- skills (required) ---
src_skills="$root/skills"
if [[ ! -d "$src_skills" ]]; then
  echo "cloud-package: ERROR — no skills/ directory in mirror checkout" >&2
  exit 1
fi

mkdir -p "$SKILLS_HOME"
installed_skills=0
for skill_dir in "$src_skills"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "$skill_dir")"
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "cloud-package: skip skill ${name} (no SKILL.md)"
    continue
  fi
  dest="$SKILLS_HOME/$name"
  rm -rf "$dest"
  cp -R "$skill_dir" "$dest"
  installed_skills=$((installed_skills + 1))
  echo "cloud-package: installed skill ${name} → ${dest}"
done

if [[ "$installed_skills" -eq 0 ]]; then
  echo "cloud-package: ERROR — no skills installed from mirror" >&2
  exit 1
fi

# --- agents (optional during mirror transition) ---
src_agents="$root/agents"
installed_agents=0
if [[ ! -d "$src_agents" ]]; then
  echo "cloud-package: WARN — no agents/ in mirror; skills only (republish with /publish-skills)" >&2
else
  mkdir -p "$AGENTS_HOME"
  shopt -s nullglob
  for agent_file in "$src_agents"/*.md; do
    name="$(basename "$agent_file")"
    dest="$AGENTS_HOME/$name"
    cp -f "$agent_file" "$dest"
    installed_agents=$((installed_agents + 1))
    echo "cloud-package: installed agent ${name} → ${dest}"
  done
  shopt -u nullglob
  if [[ "$installed_agents" -eq 0 ]]; then
    echo "cloud-package: WARN — agents/ present but empty; continuing with skills only" >&2
  fi
fi

# --- cited rules (optional during mirror transition) ---
src_rules="$root/rules"
installed_rules=0
if [[ ! -d "$src_rules" ]]; then
  echo "cloud-package: WARN — no rules/ in mirror; read cited rules from republished package later" >&2
else
  mkdir -p "$RULES_HOME"
  shopt -s nullglob
  for rule_file in "$src_rules"/*.md; do
    name="$(basename "$rule_file")"
    dest="$RULES_HOME/$name"
    cp -f "$rule_file" "$dest"
    installed_rules=$((installed_rules + 1))
    echo "cloud-package: installed rule ${name} → ${dest}"
  done
  shopt -u nullglob
  if [[ "$installed_rules" -eq 0 ]]; then
    echo "cloud-package: WARN — rules/ present but empty; continuing with skills only" >&2
  fi
fi

echo "cloud-package: done (${installed_skills} skill(s), ${installed_agents} agent file(s), ${installed_rules} rule file(s))"
