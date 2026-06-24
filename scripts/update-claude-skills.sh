#!/usr/bin/env bash
#
# update-claude-skills.sh — install / update Nature Skills into Claude Code.
#
# Claude Code loads personal skills from ~/.claude/skills/. This script copies
# every skill folder shipped in this repository's skills/ directory (the
# nature-* skills plus the shared _shared/ dir) into that location.
#
# This is the manual-copy fallback. The recommended way to install for Claude
# Code is the plugin marketplace (see README "Claude Code 安装"):
#   /plugin marketplace add Yuan1z0825/nature-skills
#   /plugin install nature-skills@nature-skills
# Use this script only if you prefer a plain copy into ~/.claude/skills/.
#
# Safety: it syncs ONLY the skill folders found in this repo, each in isolation.
# Any other skills you keep in ~/.claude/skills/ are left completely untouched.
#
# Usage:
#   scripts/update-claude-skills.sh           # copy this checkout's skills into Claude Code
#   PULL=1 scripts/update-claude-skills.sh    # `git pull --ff-only` first, then copy
#   CLAUDE_SKILLS_DIR=/path scripts/update-claude-skills.sh   # override destination
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/skills"
DST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

if [ ! -d "$SRC" ]; then
  echo "error: skills directory not found at $SRC" >&2
  exit 1
fi

# Optionally refresh this checkout to the latest commit before copying.
if [ "${PULL:-0}" = "1" ] && git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "==> Pulling latest (git pull --ff-only) ..."
  git -C "$REPO_ROOT" pull --ff-only
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "error: rsync is required but not installed" >&2
  exit 1
fi

mkdir -p "$DST"
echo "==> Syncing skills from $SRC"
echo "    into $DST"
for path in "$SRC"/*/; do
  d="$(basename "$path")"
  mkdir -p "$DST/$d"
  rsync -a --delete "$path" "$DST/$d/"
  echo "    ✓ $d"
done

echo "==> Done. Other skills in $DST were left untouched."
