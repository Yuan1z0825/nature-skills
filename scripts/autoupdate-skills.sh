#!/usr/bin/env bash
#
# autoupdate-skills.sh — keep an installed copy of the skills in sync with
# upstream, cheaply enough to run on every agent/editor session start.
#
# This script lives inside a dedicated clone of this repository. On each run it
# fast-forwards the clone to its upstream, verifies the installed destination,
# and re-syncs via update-codex-skills.sh when upstream moved or local drift is found.
#
# Typical use is a Claude Code SessionStart hook (see the README), but it works
# anywhere you can run a command at startup (a shell profile, cron, etc.).
#
# It is safe to run constantly:
#   - Throttled: skips the network if it checked within THROTTLE seconds, while
#     still verifying and repairing the local destination on every invocation.
#   - Offline-tolerant: a stalled/failed fetch is ignored and the run exits 0, so
#     it never blocks or errors a session start (handy on flaky or blocked links).
#   - Non-destructive: it only ever fast-forwards this clone. It refuses to run if
#     the clone has local commits or a dirty tree, so a working dev checkout is
#     never rewritten — keep this on a dedicated skills-only clone.
#   - Cheap: it re-syncs skills only when upstream changed or destination drift
#     is detected.
#
# Usage:
#   scripts/autoupdate-skills.sh                      # sync into ~/.claude/skills
#   scripts/autoupdate-skills.sh --dest ~/.codex/skills
#   scripts/autoupdate-skills.sh --throttle 3600      # check at most hourly
#   scripts/autoupdate-skills.sh --force              # ignore throttle, always sync
#
# Environment (flags take precedence):
#   SKILLS_DEST=/path      Destination skills dir  (default ~/.claude/skills)
#   SKILLS_THROTTLE=SECS   Min seconds between upstream checks (default 3600 = 1h; 0 = always)
#   SKILLS_STATE_DIR=/path Base state dir (default $XDG_STATE_HOME/nature-skills)
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DEST="${SKILLS_DEST:-$HOME/.claude/skills}"
THROTTLE="${SKILLS_THROTTLE:-3600}"
FORCE=0

usage() { sed -n '2,32p' "$0"; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dest) DEST="${2:?--dest needs a path}"; shift 2 ;;
    --dest=*) DEST="${1#*=}"; shift ;;
    --throttle) THROTTLE="${2:?--throttle needs seconds}"; shift 2 ;;
    --throttle=*) THROTTLE="${1#*=}"; shift ;;
    --force) FORCE=1; THROTTLE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "autoupdate-skills.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
done

case "$THROTTLE" in
  ''|*[!0-9]*)
    echo "autoupdate-skills.sh: --throttle must be a non-negative integer" >&2
    exit 2
    ;;
esac

# Keep throttle and logs independent for each destination. A user may install
# the same repository into Codex and Claude Code; one client's recent check
# must not prevent the other destination from being verified and repaired.
STATE_ROOT="${SKILLS_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/nature-skills}"
DEST_KEY=$(printf '%s' "$DEST" | cksum | awk '{print $1}')
STATE_DIR="$STATE_ROOT/$DEST_KEY"
STAMP="$STATE_DIR/last-check"
LOG="$STATE_DIR/autoupdate.log"
LOCK_DIR="$STATE_DIR/update.lock"
LOCK_OWNED=0

mkdir -p "$STATE_DIR" 2>/dev/null || true
log() { printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >>"$LOG" 2>/dev/null; }

release_lock() {
  if [ "$LOCK_OWNED" = "1" ]; then
    if [ "$(cat "$LOCK_DIR/pid" 2>/dev/null || true)" = "$$" ]; then
      rm -rf "$LOCK_DIR" 2>/dev/null || true
    fi
    LOCK_OWNED=0
  fi
}

handle_signal() {
  trap - HUP INT TERM
  release_lock
  exit 130
}

acquire_lock() {
  local attempt owner
  for attempt in 1 2; do
    if mkdir "$LOCK_DIR" 2>/dev/null; then
      printf '%s\n' "$$" >"$LOCK_DIR/pid"
      LOCK_OWNED=1
      return 0
    fi

    owner=$(cat "$LOCK_DIR/pid" 2>/dev/null || true)
    case "$owner" in
      ''|*[!0-9]*) ;;
      *)
        if kill -0 "$owner" 2>/dev/null; then
          log "another updater is already running for $DEST (pid $owner) — skip"
          return 1
        fi
        ;;
    esac

    # A terminated updater can leave its mkdir-based lock behind. Remove only
    # this destination-scoped lock and retry the atomic mkdir once.
    rm -rf "$LOCK_DIR" 2>/dev/null || true
  done

  log "could not acquire updater lock for $DEST — skip"
  return 1
}

if ! acquire_lock; then
  exit 0
fi
trap release_lock EXIT
trap handle_signal HUP INT TERM

installer="$REPO_ROOT/scripts/update-codex-skills.sh"
if [ ! -x "$installer" ]; then
  log "update-codex-skills.sh missing or not executable — skip sync"
  exit 0
fi

sync_destination() {
  if "$installer" --dest "$DEST" --prune >>"$LOG" 2>&1; then
    log "sync OK -> $(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
    return 0
  fi
  log "sync FAILED"
  return 1
}

# --- throttle: skip only the network; still verify the destination ---------
now=$(date +%s)
if [ "$THROTTLE" -gt 0 ] && [ -f "$STAMP" ]; then
  last=$(cat "$STAMP" 2>/dev/null || echo 0)
  case "$last" in ''|*[!0-9]*) last=0 ;; esac
  if [ $(( now - last )) -lt "$THROTTLE" ]; then
    if "$installer" --dest "$DEST" --check >>"$LOG" 2>&1; then
      exit 0
    fi
    log "network check throttled but destination drift detected; re-syncing skills into $DEST"
    sync_destination
    exit 0
  fi
fi

command -v git >/dev/null 2>&1 || { log "git not found — skip"; exit 0; }

# Refuse to touch a dev checkout: don't fast-forward over uncommitted work.
# Only TRACKED changes block us — untracked files (e.g. macOS .DS_Store) are
# ignored so a normal clone doesn't silently stop updating. Local commits ahead
# of upstream are handled safely by the --ff-only pull below (it just fails).
if ! git -C "$REPO_ROOT" diff --quiet 2>/dev/null \
   || ! git -C "$REPO_ROOT" diff --cached --quiet 2>/dev/null; then
  log "clone has uncommitted changes to tracked files — skip"
  exit 0
fi

# Portable timeout (macOS ships no `timeout`); git also self-aborts stalled fetches.
run_guarded() {
  local secs="$1"; shift
  "$@" &
  local pid=$!
  ( sleep "$secs"; kill -TERM "$pid" 2>/dev/null; sleep 3; kill -KILL "$pid" 2>/dev/null ) &
  local watch=$!
  wait "$pid" 2>/dev/null; local rc=$?
  kill "$watch" 2>/dev/null; wait "$watch" 2>/dev/null
  return "$rc"
}
git_slow=(
  git
  -c http.lowSpeedLimit=1024
  -c http.lowSpeedTime=20
  -C "$REPO_ROOT"
)

before=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo none)

# Fast-forward the clone. A failure here (offline, blocked, diverged) is non-fatal.
if ! run_guarded 60 "${git_slow[@]}" pull --ff-only >>"$LOG" 2>&1; then
  log "pull failed — skip (offline, blocked, or diverged clone)"
  exit 0
fi
echo "$now" >"$STAMP"

after=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo none)

if [ "$before" = "$after" ] && [ "$FORCE" != "1" ]; then
  if "$installer" --dest "$DEST" --check >>"$LOG" 2>&1; then
    log "up to date and destination verified ($after)"
    exit 0
  fi
  log "upstream unchanged but destination drift detected; re-syncing skills into $DEST"
else
  log "upstream ${before} -> ${after}; syncing skills into $DEST"
fi

sync_destination
exit 0
