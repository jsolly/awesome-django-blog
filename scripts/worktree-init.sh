#!/usr/bin/env bash
# Provision a checkout (especially a fresh git worktree) so the pre-push gate can
# run: create a .venv against the repo-pinned Python and install the pinned deps.
#
# Run after EnterWorktree / `git worktree add`:  npm run worktree:init
#
# Fresh worktrees branch from origin/master and carry no gitignored files, so
# .venv does not exist in them. The pre-push gate refuses to run against system
# Python (it must use the pinned requirements.txt), so a worktree needs either
# its own .venv (this script) or — for the common code-only change — it transpar-
# ently borrows the main checkout's .venv (see .git-hooks/pre-push). Use this
# script when you've changed requirements.txt, since the borrowed venv would then
# be stale and the hook will refuse to reuse it.
#
# The pip wheel cache is warm on any machine that has installed these once
# (numpy/scipy/scikit-learn/pandas/matplotlib), so the install is fast.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# --- Allowlist copy (parity with dotagents' WorktreeCreate hook) -------------
# The hook copies the repo's `.worktreeinclude` gitignored files into worktrees
# it creates (EnterWorktree / --worktree / subagent isolation). The MANUAL
# `git worktree add` path bypasses the hook, so do the same copy here. COPY,
# never symlink (the .venv bootstrap below is the only "real install" — env
# files are plain config). Non-fatal: a missing manifest or unmatched glob must
# never block provisioning. Invoked via `|| true` so errexit is suppressed for
# the whole body (a failed cp can't abort the script).
copy_worktree_includes() {
  local manifest="$ROOT/.worktreeinclude"
  [ -f "$manifest" ] || return 0

  # First `worktree` entry of `git worktree list --porcelain` is the primary
  # (main) checkout — the source of truth for gitignored local files.
  local primary
  # Strip the literal `worktree ` prefix rather than field-splitting — a worktree
  # path can contain spaces, which `$2` would truncate (silent no-op copy).
  primary="$(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{sub(/^worktree /, ""); print; exit}')"
  [ -n "$primary" ] || { echo "⚠ could not resolve primary worktree — skipped .worktreeinclude copy" >&2; return 0; }
  [ "$primary" != "$ROOT" ] || return 0  # we ARE the primary; nothing to copy

  local line pattern src rel dest copied=0
  while IFS= read -r line || [ -n "$line" ]; do
    pattern="${line%%#*}"                       # drop inline/full-line comments
    pattern="$(printf '%s' "$pattern" | tr -d '[:space:]')"
    [ -n "$pattern" ] || continue
    # Glob-expand against the primary; unmatched globs stay literal and are
    # skipped by the -e test below (tolerate zero matches).
    for src in "$primary"/$pattern; do
      [ -e "$src" ] || continue
      rel="${src#"$primary"/}"
      dest="$ROOT/$rel"
      mkdir -p "$(dirname "$dest")"
      cp -p "$src" "$dest" && { echo "  • copied $rel from primary worktree"; copied=$((copied + 1)); }
    done
  done <"$manifest"
  [ "$copied" -gt 0 ] && echo "✓ copied $copied gitignored file(s) per .worktreeinclude" || true
}
copy_worktree_includes || true

# Idempotency keys on a sentinel written only after a SUCCESSFUL install — not
# on .venv's mere existence. `python -m venv` writes bin/activate before pip
# runs, so an interrupted install would otherwise look "done" and leave a venv
# that activates but is missing deps (the gate then fails deep in pytest).
SENTINEL=".venv/.worktree-init-complete"
if [ -f "$SENTINEL" ]; then
  echo "✓ .venv already provisioned in $ROOT — nothing to do."
  echo "  (re-provision with: rm -rf .venv && npm run worktree:init)"
  exit 0
fi

# Resolve the repo-pinned interpreter (.python-version → e.g. 3.14). Prefer an
# explicitly-versioned binary; otherwise plain python3 (a pyenv shim honors
# .python-version, so python3 already resolves to the pin). The result is
# verified below — we never trust the name alone.
PY="python3"
PINNED=""
if [ -f .python-version ]; then
  PINNED="$(tr -d '[:space:]' <.python-version)"
  if command -v "python${PINNED}" >/dev/null 2>&1; then
    PY="python${PINNED}"
  fi
fi

if [ ! -d .venv ]; then
  echo "• creating .venv with $PY ($("$PY" --version 2>&1))"
  "$PY" -m venv .venv
fi

# Fail loud on an off-pin interpreter — never let the gate validate a push on a
# Python that differs from what Heroku runs. Catches both a wrong $PY here and a
# pre-existing off-pin .venv left by an earlier run.
if [ -n "$PINNED" ]; then
  venv_ver="$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
  if [ "$venv_ver" != "$PINNED" ]; then
    echo "✗ .venv Python is $venv_ver but .python-version pins $PINNED." >&2
    echo "  Install Python $PINNED (e.g. 'pyenv install $PINNED'), then: rm -rf .venv && npm run worktree:init" >&2
    exit 1
  fi
fi

echo "• installing pinned deps (requirements.txt) — fast on a warm pip cache"
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt

# The pre-push gate also runs the markdown sub-gate via the pinned dev tooling
# (markdownlint-cli2). Install node_modules so it runs offline too; npm ci is
# fast on a warm npm cache. lint-md.sh can otherwise borrow the main checkout's
# binary, but a fully-provisioned worktree is self-contained.
if [ -f package-lock.json ]; then
  echo "• npm ci (dev tooling: markdownlint-cli2, heroku) — fast on a warm npm cache"
  npm ci
else
  echo "⚠ no package-lock.json — skipped npm ci; the markdown lint will need network (npx) until installed" >&2
fi

# Mark complete only now, after deps installed — see SENTINEL note above.
touch "$SENTINEL"
echo "✓ worktree provisioned — pre-push gate can now run in $ROOT"
