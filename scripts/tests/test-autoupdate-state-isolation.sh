#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$TMP_DIR/bin" "$TMP_DIR/home" "$TMP_DIR/state"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'case " $* " in' \
  '  *" rev-parse HEAD "*) printf "test-revision\\n" ;;' \
  'esac' \
  'exit 0' >"$TMP_DIR/bin/git"
chmod +x "$TMP_DIR/bin/git"

run_update() {
  HOME="$TMP_DIR/home" \
  XDG_STATE_HOME="$TMP_DIR/state" \
  PATH="$TMP_DIR/bin:$PATH" \
    bash "$REPO_ROOT/scripts/autoupdate-skills.sh" \
      --dest "$1" \
      --throttle 3600
}

run_update "$TMP_DIR/codex-skills"
run_update "$TMP_DIR/claude-skills"

stamp_count=$(find "$TMP_DIR/state/nature-skills" -name last-check -type f | wc -l | tr -d ' ')
if [ "$stamp_count" != "2" ]; then
  echo "Expected one independent throttle stamp per destination; found $stamp_count." >&2
  exit 1
fi

RETRY_REPO="$TMP_DIR/retry-repo"
mkdir -p "$RETRY_REPO/scripts" "$TMP_DIR/retry-home" "$TMP_DIR/retry-state"
cp "$REPO_ROOT/scripts/autoupdate-skills.sh" "$RETRY_REPO/scripts/autoupdate-skills.sh"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'printf "called\\n" >>"$AUTOUPDATE_TEST_CALLS"' \
  'exit 1' >"$RETRY_REPO/scripts/update-codex-skills.sh"
chmod +x "$RETRY_REPO/scripts/update-codex-skills.sh"

run_failing_update() {
  AUTOUPDATE_TEST_CALLS="$TMP_DIR/retry-calls" \
  HOME="$TMP_DIR/retry-home" \
  XDG_STATE_HOME="$TMP_DIR/retry-state" \
  PATH="$TMP_DIR/bin:$PATH" \
    bash "$RETRY_REPO/scripts/autoupdate-skills.sh" \
      --dest "$TMP_DIR/retry-dest" \
      --throttle 3600
}

run_failing_update
calls_after_first=$(wc -l <"$TMP_DIR/retry-calls" | tr -d ' ')
run_failing_update
calls_after_second=$(wc -l <"$TMP_DIR/retry-calls" | tr -d ' ')

if [ "$calls_after_second" -le "$calls_after_first" ]; then
  echo "A failed destination sync was suppressed by the network throttle." >&2
  exit 1
fi

CONCURRENT_REPO="$TMP_DIR/concurrent-repo"
mkdir -p "$CONCURRENT_REPO/scripts" "$TMP_DIR/concurrent-home" "$TMP_DIR/concurrent-state"
cp "$REPO_ROOT/scripts/autoupdate-skills.sh" "$CONCURRENT_REPO/scripts/autoupdate-skills.sh"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'printf "called\n" >>"$AUTOUPDATE_TEST_CALLS"' \
  'touch "$AUTOUPDATE_TEST_STARTED"' \
  'sleep 2' \
  'exit 0' >"$CONCURRENT_REPO/scripts/update-codex-skills.sh"
chmod +x "$CONCURRENT_REPO/scripts/update-codex-skills.sh"

run_concurrent_update() {
  AUTOUPDATE_TEST_CALLS="$TMP_DIR/concurrent-calls" \
  AUTOUPDATE_TEST_STARTED="$TMP_DIR/concurrent-started" \
  HOME="$TMP_DIR/concurrent-home" \
  XDG_STATE_HOME="$TMP_DIR/concurrent-state" \
  PATH="$TMP_DIR/bin:$PATH" \
    bash "$CONCURRENT_REPO/scripts/autoupdate-skills.sh" \
      --dest "$TMP_DIR/concurrent-dest" \
      --force
}

run_concurrent_update &
first_pid=$!
for _ in 1 2 3 4 5; do
  [ -f "$TMP_DIR/concurrent-started" ] && break
  sleep 1
done
if [ ! -f "$TMP_DIR/concurrent-started" ]; then
  echo "The first updater did not reach the installer." >&2
  exit 1
fi
run_concurrent_update &
second_pid=$!
wait "$first_pid"
wait "$second_pid"

concurrent_calls=$(wc -l <"$TMP_DIR/concurrent-calls" | tr -d ' ')
if [ "$concurrent_calls" != "1" ]; then
  echo "Concurrent updaters entered the installer $concurrent_calls times." >&2
  exit 1
fi

state_dir=$(find "$TMP_DIR/concurrent-state/nature-skills" -mindepth 1 -maxdepth 1 -type d | head -n 1)
mkdir "$state_dir/update.lock"
printf '%s\n' 999999 >"$state_dir/update.lock/pid"
run_concurrent_update

calls_after_stale_lock=$(wc -l <"$TMP_DIR/concurrent-calls" | tr -d ' ')
if [ "$calls_after_stale_lock" != "2" ]; then
  echo "A stale updater lock prevented the next update." >&2
  exit 1
fi

echo "Auto-update state isolation, retry, and locking passed."
