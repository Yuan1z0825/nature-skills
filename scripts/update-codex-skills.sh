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
#   scripts/update-codex-skills.sh --check --check-deps
#                                                  # also verify the managed Python runtime
#   scripts/update-codex-skills.sh --with-python-deps
#                                                  # install declared deps in an isolated venv
#   scripts/update-codex-skills.sh --with-cnipa-browser
#                                                  # also install Playwright Chromium
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
CHECK_DEPS="${CHECK_DEPS:-0}"
INSTALL_PY_DEPS="${INSTALL_PY_DEPS:-0}"
INSTALL_CNIPA_BROWSER="${INSTALL_CNIPA_BROWSER:-0}"
PYTHON_BIN="${NATURE_SKILLS_PYTHON:-python3}"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
VENV_PATH="${NATURE_SKILLS_VENV:-$DATA_HOME/nature-skills/venv}"
MANIFEST_NAME=".nature-skills-install.txt"
RUNTIME_MANIFEST_NAME=".nature-skills-python-runtime"

[ "$CHECK_DEPS" = "1" ] && CHECK_ONLY=1

usage() {
  cat <<'USAGE'
update-codex-skills.sh - install / update Nature Skills into Codex.

Usage:
  scripts/update-codex-skills.sh                 Copy this checkout's skills into Codex.
  scripts/update-codex-skills.sh --pull          Run git pull --ff-only first.
  scripts/update-codex-skills.sh --check         Verify install without copying.
  scripts/update-codex-skills.sh --check-deps    Verify the isolated Python runtime.
  scripts/update-codex-skills.sh --with-python-deps
                                                Install declared Python dependencies.
  scripts/update-codex-skills.sh --with-cnipa-browser
                                                Also install Playwright Chromium.
  scripts/update-codex-skills.sh --prune         Remove stale dirs managed by this script.
  scripts/update-codex-skills.sh --dest /path    Override destination.
  scripts/update-codex-skills.sh --python /path  Python used to create the isolated venv.
  scripts/update-codex-skills.sh --venv /path    Override the managed venv location.

Environment:
  CODEX_SKILLS_DIR=/path    Default destination override.
  PULL=1                    Same as --pull.
  PRUNE=1                   Same as --prune.
  CHECK_ONLY=1              Same as --check.
  CHECK_DEPS=1              Same as --check-deps.
  INSTALL_PY_DEPS=1         Same as --with-python-deps.
  INSTALL_CNIPA_BROWSER=1   Same as --with-cnipa-browser.
  NATURE_SKILLS_PYTHON=...  Python used to create the isolated venv.
  NATURE_SKILLS_VENV=/path  Managed venv location.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed"
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
    --check-deps)
      CHECK_DEPS=1
      CHECK_ONLY=1
      ;;
    --with-python-deps)
      INSTALL_PY_DEPS=1
      ;;
    --with-cnipa-browser)
      INSTALL_CNIPA_BROWSER=1
      INSTALL_PY_DEPS=1
      ;;
    --dest)
      shift
      [ "$#" -gt 0 ] || die "--dest requires a directory"
      DST="$1"
      ;;
    --dest=*)
      DST="${1#*=}"
      ;;
    --python)
      shift
      [ "$#" -gt 0 ] || die "--python requires an executable"
      PYTHON_BIN="$1"
      ;;
    --python=*)
      PYTHON_BIN="${1#*=}"
      ;;
    --venv)
      shift
      [ "$#" -gt 0 ] || die "--venv requires a directory"
      VENV_PATH="$1"
      ;;
    --venv=*)
      VENV_PATH="${1#*=}"
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

RUNTIME_MANIFEST="$DST/$RUNTIME_MANIFEST_NAME"

if [ "$CHECK_ONLY" = "1" ] && { [ "$INSTALL_PY_DEPS" = "1" ] || [ "$INSTALL_CNIPA_BROWSER" = "1" ]; }; then
  die "--check is read-only and cannot be combined with dependency installation flags"
fi

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
REQ_LIST="$(mktemp "${TMPDIR:-/tmp}/nature-skills-reqs.XXXXXX")"
trap 'rm -f "$SKILL_LIST" "$DIFF_OUT" "$REQ_LIST"' EXIT

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

# A top-level requirements.txt belongs to that skill. MCP servers may keep
# their runtime declaration one level deeper. Heavy browser support remains a
# separate opt-in group and is deliberately excluded here.
for requirement_file in "$SRC"/*/requirements.txt "$SRC"/*/mcp-server/requirements.txt; do
  [ -f "$requirement_file" ] || continue
  printf '%s\n' "$requirement_file" >> "$REQ_LIST"
done
sort -u -o "$REQ_LIST" "$REQ_LIST"

CNIPA_REQUIREMENTS="$SRC/nature-paper-to-patent/scripts/disclosure/requirements-cnipa.txt"
DEPS_CHECKER="$REPO_ROOT/scripts/check-python-deps.py"
RUNTIME_HOOK="$REPO_ROOT/scripts/nature_skills_runtime.py"
RUNTIME_PTH="$REPO_ROOT/scripts/nature_skills_runtime.pth"

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
    elif diff -qr "$src_path" "$dst_path" >"$DIFF_OUT"; then
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
  [ -s "$REQ_LIST" ] || return 0
  echo "==> Optional Python runtime"
  echo "    Dependencies were not installed. To install them in an isolated venv:"
  echo "    $0 --dest $DST --with-python-deps"
  echo "    Add --with-cnipa-browser for CNIPA published-patent browser support."
  echo "    Managed venv: $VENV_PATH"
}

venv_python_path() {
  if [ -x "$VENV_PATH/bin/python" ]; then
    printf '%s\n' "$VENV_PATH/bin/python"
  elif [ -x "$VENV_PATH/Scripts/python.exe" ]; then
    printf '%s\n' "$VENV_PATH/Scripts/python.exe"
  else
    return 1
  fi
}

runtime_has_cnipa_browser() {
  [ -f "$RUNTIME_MANIFEST" ] && grep -Fxq 'cnipa_browser=1' "$RUNTIME_MANIFEST"
}

configure_python_runtime() {
  [ -f "$RUNTIME_HOOK" ] || die "runtime hook not found at $RUNTIME_HOOK"
  [ -f "$RUNTIME_PTH" ] || die "runtime path file not found at $RUNTIME_PTH"
  site_packages="$("$venv_python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
  [ -d "$site_packages" ] || die "Python site-packages directory not found at $site_packages"
  cp "$RUNTIME_HOOK" "$site_packages/nature_skills_runtime.py"
  cp "$RUNTIME_PTH" "$site_packages/nature_skills_runtime.pth"
  echo "==> Configured sandbox-writable Matplotlib cache startup hook"
}

verify_python_deps() {
  if [ ! -s "$REQ_LIST" ]; then
    echo "==> No declared Python dependencies"
    return 0
  fi
  if ! venv_python="$(venv_python_path)"; then
    echo "MISSING  managed Python runtime at $VENV_PATH" >&2
    echo "         Run $0 --dest $DST --with-python-deps" >&2
    return 1
  fi
  [ -f "$DEPS_CHECKER" ] || die "dependency checker not found at $DEPS_CHECKER"

  checker_args=()
  check_cnipa_browser=0
  if [ "$INSTALL_CNIPA_BROWSER" = "1" ] || runtime_has_cnipa_browser; then
    check_cnipa_browser=1
    checker_args+=(--playwright-chromium)
  fi
  while IFS= read -r requirement_file; do
    checker_args+=("$requirement_file")
  done < "$REQ_LIST"
  if [ "$check_cnipa_browser" = "1" ] && [ -f "$CNIPA_REQUIREMENTS" ]; then
    checker_args+=("$CNIPA_REQUIREMENTS")
  fi

  echo "==> Verifying Python dependencies in $VENV_PATH"
  "$venv_python" "$DEPS_CHECKER" "${checker_args[@]}"
  "$venv_python" -m pip check
}

install_python_deps() {
  [ -s "$REQ_LIST" ] || return 0
  need_cmd "$PYTHON_BIN"
  if ! venv_python="$(venv_python_path)"; then
    echo "==> Creating isolated Python runtime at $VENV_PATH"
    "$PYTHON_BIN" -m venv "$VENV_PATH"
    venv_python="$(venv_python_path)" || die "venv creation did not produce a Python executable"
  else
    echo "==> Reusing isolated Python runtime at $VENV_PATH"
  fi
  configure_python_runtime

  pip_args=(install --disable-pip-version-check)
  while IFS= read -r requirement_file; do
    pip_args+=(-r "$requirement_file")
  done < "$REQ_LIST"
  if [ "$INSTALL_CNIPA_BROWSER" = "1" ]; then
    [ -f "$CNIPA_REQUIREMENTS" ] || die "CNIPA requirements not found at $CNIPA_REQUIREMENTS"
    pip_args+=(-r "$CNIPA_REQUIREMENTS")
  fi

  echo "==> Installing declared Python dependencies"
  "$venv_python" -m pip "${pip_args[@]}"
  if [ "$INSTALL_CNIPA_BROWSER" = "1" ]; then
    echo "==> Installing Playwright Chromium for CNIPA support"
    "$venv_python" -m playwright install chromium
  fi
  verify_python_deps

  cnipa_browser_state=0
  if [ "$INSTALL_CNIPA_BROWSER" = "1" ] || runtime_has_cnipa_browser; then
    cnipa_browser_state=1
  fi
  {
    echo "# Managed by nature-skills scripts/update-codex-skills.sh"
    echo "venv=$VENV_PATH"
    echo "python=$venv_python"
    echo "cnipa_browser=$cnipa_browser_state"
    date '+updated_at=%Y-%m-%dT%H:%M:%S%z'
  } > "$RUNTIME_MANIFEST"
  echo "==> Python runtime ready: $venv_python"
}

if [ "$CHECK_ONLY" = "1" ]; then
  echo "==> Verifying Codex skills in $DST"
  status=0
  verify_install || status=1
  if [ "$CHECK_DEPS" = "1" ]; then
    verify_python_deps || status=1
  fi
  echo "==> Verified against $repo_commit"
  exit "$status"
fi

mkdir -p "$DST"
echo "==> Syncing skills from $SRC"
echo "    into $DST"
while IFS= read -r name; do
  mkdir -p "$DST/$name"
  rsync -a --delete "$SRC/$name/" "$DST/$name/"
  echo "    synced $name"
done < "$SKILL_LIST"

manifest="$DST/$MANIFEST_NAME"
if [ "$PRUNE" = "1" ]; then
  if [ -f "$manifest" ]; then
    echo "==> Pruning stale directories previously managed by this script"
    while IFS= read -r old_name; do
      case "$old_name" in
        ""|\#*) continue ;;
      esac
      if ! grep -Fxq "$old_name" "$SKILL_LIST" && [ -d "$DST/$old_name" ]; then
        rm -rf "$DST/$old_name"
        echo "    pruned $old_name"
      fi
    done < "$manifest"
  else
    echo "==> No previous $MANIFEST_NAME manifest; skipping prune"
  fi
fi

{
  echo "# Managed by nature-skills scripts/update-codex-skills.sh"
  echo "# source=$REPO_ROOT"
  echo "# commit=$repo_commit"
  date '+# updated_at=%Y-%m-%dT%H:%M:%S%z'
  cat "$SKILL_LIST"
} > "$manifest"

echo "==> Verifying copied skills"
verify_install

if [ "$INSTALL_PY_DEPS" = "1" ]; then
  install_python_deps
elif [ "$CHECK_DEPS" = "1" ]; then
  verify_python_deps
else
  print_dependency_notes
fi
echo "==> Done. Other skills in $DST were left untouched."
echo "==> Installed from $repo_commit"
