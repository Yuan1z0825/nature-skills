#!/usr/bin/env bash
#
# update-codex-skills.sh — install / update Nature Skills into Codex.
#
# Codex loads skills from ~/.codex/skills/. This script copies every top-level
# skill folder shipped in this repository's skills/ directory, including the
# nature-shared support package, into that location.
#
# It is intended for users who install the skills by manual copy rather than
# via the Codex plugin marketplace. Running it again later updates an existing
# install to the current contents of this checkout.
#
# Safety: by default it syncs ONLY the skill folders found in this repo, each in
# isolation. Any other skills you keep in ~/.codex/skills/ (e.g. pdf, playwright)
# are left untouched. With --prune, it removes only directories previously
# recorded by this script and no longer shipped by this repo.
#
# Usage:
#   scripts/update-codex-skills.sh                 # copy this checkout's skills into Codex
#   scripts/update-codex-skills.sh --pull          # git pull --ff-only first
#   scripts/update-codex-skills.sh --check         # verify install without copying
#   scripts/update-codex-skills.sh --prune         # remove stale dirs managed by this script
#   scripts/update-codex-skills.sh --dest /path    # override destination
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/skills"
DST="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
PULL="${PULL:-0}"
PRUNE="${PRUNE:-0}"
CHECK_ONLY="${CHECK_ONLY:-0}"
MANIFEST_NAME=".nature-skills-install.txt"
DIFF_EXCLUDES=(
  -x '.DS_Store'
  -x '__pycache__'
  -x '.pytest_cache'
  -x '*.pyc'
  -x '*.pyo'
)
RSYNC_EXCLUDES=(
  --exclude='.DS_Store'
  --exclude='__pycache__'
  --exclude='.pytest_cache'
  --exclude='*.py[cod]'
)

usage() {
  cat <<'USAGE'
update-codex-skills.sh - install / update Nature Skills into Codex.

Usage:
  scripts/update-codex-skills.sh                 Copy this checkout's skills into Codex.
  scripts/update-codex-skills.sh --pull          Run git pull --ff-only first.
  scripts/update-codex-skills.sh --check         Verify install without copying.
  scripts/update-codex-skills.sh --prune         Remove stale dirs managed by this script.
  scripts/update-codex-skills.sh --dest /path    Override destination.

Environment:
  CODEX_SKILLS_DIR=/path    Default destination override.
  PULL=1                    Same as --pull.
  PRUNE=1                   Same as --prune.
  CHECK_ONLY=1              Same as --check.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed"
}

is_safe_managed_name() {
  case "$1" in
    ""|"."|".."|*/*|*\\*|*[!A-Za-z0-9._-]*) return 1 ;;
    *) return 0 ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pull)
      PULL=1
      ;;
    --prune)
      PRUNE=1
      ;;
    --check|--verify-only)
      CHECK_ONLY=1
      ;;
    --dest)
      shift
      [ "$#" -gt 0 ] || die "--dest requires a directory"
      DST="$1"
      ;;
    --dest=*)
      DST="${1#*=}"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
  shift
done

if [ ! -d "$SRC" ]; then
  die "skills directory not found at $SRC"
fi

# Optionally refresh this checkout to the latest commit before copying.
if [ "$PULL" = "1" ]; then
  if git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "==> Pulling latest (git pull --ff-only) ..."
    git -C "$REPO_ROOT" pull --ff-only
  else
    echo "==> Skipping pull: $REPO_ROOT is not a git checkout"
  fi
fi

need_cmd diff
[ "$CHECK_ONLY" = "1" ] || need_cmd rsync

SKILL_LIST="$(mktemp "${TMPDIR:-/tmp}/nature-skills-list.XXXXXX")"
DIFF_OUT="$(mktemp "${TMPDIR:-/tmp}/nature-skills-diff.XXXXXX")"
DEPLOYED_LIST="$(mktemp "${TMPDIR:-/tmp}/nature-skills-deployed.XXXXXX")"
PRUNED_LIST="$(mktemp "${TMPDIR:-/tmp}/nature-skills-pruned.XXXXXX")"
STAGE_ROOT=""
BACKUP_ROOT=""
MANIFEST_TMP=""
TRANSACTION_ACTIVE=0
CURRENT_NAME=""

path_exists() {
  [ -e "$1" ] || [ -L "$1" ]
}

rollback_transaction() {
  local name had_previous backup_path dst_path

  # CURRENT_NAME covers an interruption between the two rename operations.
  if [ -n "$CURRENT_NAME" ]; then
    backup_path="$BACKUP_ROOT/current/$CURRENT_NAME"
    dst_path="$DST/$CURRENT_NAME"
    if path_exists "$backup_path"; then
      rm -rf "$dst_path"
      mv "$backup_path" "$dst_path" 2>/dev/null || true
    elif [ -n "$STAGE_ROOT" ] && ! path_exists "$STAGE_ROOT/$CURRENT_NAME"; then
      rm -rf "$dst_path"
    fi
  fi

  while IFS=$'\t' read -r name had_previous; do
    [ -n "$name" ] || continue
    backup_path="$BACKUP_ROOT/current/$name"
    dst_path="$DST/$name"
    if path_exists "$backup_path"; then
      rm -rf "$dst_path"
      mv "$backup_path" "$dst_path" 2>/dev/null || true
    elif [ "$had_previous" = "0" ]; then
      rm -rf "$dst_path"
    fi
  done < "$DEPLOYED_LIST"

  while IFS= read -r name; do
    [ -n "$name" ] || continue
    backup_path="$BACKUP_ROOT/pruned/$name"
    if path_exists "$backup_path" && ! path_exists "$DST/$name"; then
      mv "$backup_path" "$DST/$name" 2>/dev/null || true
    fi
  done < "$PRUNED_LIST"
}

cleanup() {
  local status=$?
  trap - EXIT HUP INT TERM
  set +e
  if [ "$TRANSACTION_ACTIVE" = "1" ]; then
    rollback_transaction
  fi
  [ -z "$MANIFEST_TMP" ] || rm -f "$MANIFEST_TMP"
  [ -z "$STAGE_ROOT" ] || rm -rf "$STAGE_ROOT"
  [ -z "$BACKUP_ROOT" ] || rm -rf "$BACKUP_ROOT"
  rm -f "$SKILL_LIST" "$DIFF_OUT" "$DEPLOYED_LIST" "$PRUNED_LIST"
  exit "$status"
}

trap cleanup EXIT
trap 'exit 130' HUP INT TERM

for path in "$SRC"/*/; do
  [ -d "$path" ] || continue
  name="$(basename "$path")"
  if [ ! -f "$path/SKILL.md" ]; then
    die "unexpected skills/$name directory without SKILL.md"
  fi
  printf '%s\n' "$name" >> "$SKILL_LIST"
done

[ -s "$SKILL_LIST" ] || die "no skill directories found under $SRC"
sort -o "$SKILL_LIST" "$SKILL_LIST"

repo_commit="unknown"
if git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  repo_commit="$(git -C "$REPO_ROOT" rev-parse HEAD)"
fi

verify_install() {
  status=0
  while IFS= read -r name; do
    src_path="$SRC/$name"
    dst_path="$DST/$name"
    if [ ! -d "$dst_path" ]; then
      echo "MISSING  $name"
      status=1
    elif diff -qr "${DIFF_EXCLUDES[@]}" "$src_path" "$dst_path" >"$DIFF_OUT"; then
      echo "MATCH    $name"
    else
      echo "DIFF     $name"
      sed 's/^/         /' "$DIFF_OUT"
      status=1
    fi
  done < "$SKILL_LIST"
  return "$status"
}

print_dependency_notes() {
  notes=0
  if [ -f "$SRC/nature-figure/requirements.txt" ]; then
    notes=1
    echo "    # required for automatic rendered collision QA in nature-figure"
    echo "    python -m pip install -r $SRC/nature-figure/requirements.txt"
  fi
  if [ -f "$SRC/nature-image2ppt/requirements.txt" ]; then
    notes=1
    echo "    # required before using nature-image2ppt (Python 3.10+)"
    echo "    python -m pip install -r $SRC/nature-image2ppt/requirements.txt"
  fi
  if [ -f "$SRC/nature-paper-to-patent/requirements.txt" ]; then
    notes=1
    echo "    python -m pip install -r $SRC/nature-paper-to-patent/requirements.txt"
    if [ -f "$SRC/nature-paper-to-patent/scripts/disclosure/requirements-cnipa.txt" ]; then
      echo "    # optional: CNIPA published-patent search"
      echo "    python -m pip install -r $SRC/nature-paper-to-patent/scripts/disclosure/requirements-cnipa.txt"
      echo "    python -m playwright install chromium"
    fi
  fi
  if [ -f "$SRC/nature-academic-search/mcp-server/requirements.txt" ]; then
    notes=1
    echo "    python -m pip install -r $SRC/nature-academic-search/mcp-server/requirements.txt"
    echo "    Configure PUBMED_EMAIL and any optional Elsevier credentials separately."
  fi
  [ "$notes" = "0" ] || echo "    Python dependencies are not installed automatically."
}

if [ "$CHECK_ONLY" = "1" ]; then
  echo "==> Verifying Codex skills in $DST"
  verify_install
  echo "==> Verified against $repo_commit"
  exit 0
fi

mkdir -p "$DST"
STAGE_ROOT="$(mktemp -d "$DST/.nature-skills-stage.XXXXXX")"
BACKUP_ROOT="$(mktemp -d "$DST/.nature-skills-backup.XXXXXX")"
mkdir -p "$BACKUP_ROOT/current" "$BACKUP_ROOT/pruned"

echo "==> Staging skills from $SRC"
echo "    for $DST"
while IFS= read -r name; do
  mkdir -p "$STAGE_ROOT/$name"
  rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$SRC/$name/" "$STAGE_ROOT/$name/"
  if ! diff -qr "${DIFF_EXCLUDES[@]}" "$SRC/$name" "$STAGE_ROOT/$name" >"$DIFF_OUT"; then
    sed 's/^/         /' "$DIFF_OUT" >&2
    die "staged copy of $name failed verification"
  fi
  echo "    staged $name"
done < "$SKILL_LIST"

manifest="$DST/$MANIFEST_NAME"
TRANSACTION_ACTIVE=1

echo "==> Activating staged skills"
while IFS= read -r name; do
  CURRENT_NAME="$name"
  had_previous=0
  if path_exists "$DST/$name"; then
    had_previous=1
    mv "$DST/$name" "$BACKUP_ROOT/current/$name"
  fi
  mv "$STAGE_ROOT/$name" "$DST/$name"
  printf '%s\t%s\n' "$name" "$had_previous" >> "$DEPLOYED_LIST"
  CURRENT_NAME=""
  echo "    activated $name"
done < "$SKILL_LIST"

if [ "$PRUNE" = "1" ]; then
  if [ -f "$manifest" ]; then
    echo "==> Pruning stale directories previously managed by this script"
    while IFS= read -r old_name; do
      case "$old_name" in
        ""|\#*) continue ;;
      esac
      if ! is_safe_managed_name "$old_name"; then
        printf 'warning: ignoring unsafe managed skill name: %q\n' "$old_name" >&2
        continue
      fi
      if ! grep -Fxq "$old_name" "$SKILL_LIST" && [ -d "$DST/$old_name" ]; then
        printf '%s\n' "$old_name" >> "$PRUNED_LIST"
        mv "$DST/$old_name" "$BACKUP_ROOT/pruned/$old_name"
        echo "    pruned $old_name"
      fi
    done < "$manifest"
  else
    echo "==> No previous $MANIFEST_NAME manifest; skipping prune"
  fi
fi

MANIFEST_TMP="$(mktemp "$DST/.nature-skills-install.XXXXXX")"
{
  echo "# Managed by nature-skills scripts/update-codex-skills.sh"
  echo "# source=$REPO_ROOT"
  echo "# commit=$repo_commit"
  date '+# updated_at=%Y-%m-%dT%H:%M:%S%z'
  cat "$SKILL_LIST"
} > "$MANIFEST_TMP"

echo "==> Verifying copied skills"
verify_install

mv "$MANIFEST_TMP" "$manifest"
MANIFEST_TMP=""
TRANSACTION_ACTIVE=0
rm -rf "$STAGE_ROOT" "$BACKUP_ROOT"
STAGE_ROOT=""
BACKUP_ROOT=""

echo "==> Done. Other skills in $DST were left untouched."
echo "==> Installed from $repo_commit"
print_dependency_notes
