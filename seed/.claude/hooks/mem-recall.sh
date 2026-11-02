#!/usr/bin/env bash
# mem-recall.sh - inject a short memory manifest at SessionStart.
#
# Hook event: SessionStart (matcher startup|resume|clear). Reads the hook JSON
# on stdin (cwd, session_id) and prints to stdout; Claude Code adds stdout to the
# context. Zero model calls. Prints nothing when the store has neither an INDEX
# nor a claimed handoff for this repo.
#
# The manifest names what it loaded (recent sessions, hint bullets, handoff), the
# last INDEX lines, what exists but was not loaded and the one command to reach
# it, and the four trust labels every recalled item must carry. Output is capped
# at 4000 bytes.
#
# Before building the manifest it pulls the shared store from its `origin` remote
# (when one is set), so a line another machine committed shows up here: a fetch
# bounded to two seconds, then a rebase onto origin/main under the store lock
# mem-capture.sh describes, bounded so the whole hook ends within its five-second
# timeout. A timeout or failure logs one line to reports/sync.log and falls back
# to the local store. The rebase runs with rename
# detection off, so a handoff two machines claimed at once rebases as two
# independent archive adds plus a delete both sides agree on, not a rename/rename
# conflict. `-s recursive` is what makes the switch hold: before git 2.50 the
# default ort backend ignores merge.renames=false and the recursive backend
# honors it; from 2.50 `recursive` names ort, which honors it. It then claims a single per-repo handoff note left
# by an earlier session on any machine: injects it once, archives it, and pushes.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
# The registered timeout is five seconds; every bounded step below ends by this
# epoch time, leaving room for startup and the manifest.
DEADLINE="$(python3 -c 'import time; print(time.time() + 3.8)')"

FIELDS="$(cat | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if isinstance(payload, dict):
    cwd = str(payload.get("cwd") or "")
    sid = str(payload.get("session_id") or "")
    sys.stdout.write(cwd + "\t" + sid)
' 2>/dev/null)"

CWD="${FIELDS%%$'\t'*}"
SID="${FIELDS#*$'\t'}"
[ "$FIELDS" = "$CWD" ] && SID=""
[ -n "$CWD" ] || CWD="$PWD"
SID8="$(printf '%s' "$SID" | cut -c1-8)"
[ -n "$SID8" ] || SID8="nosession"

# Key by the origin remote so recall reads the same directory mem-capture writes
# across the factory's per-worktree checkouts. Fall back to the toplevel basename
# with no origin, then to the cwd basename with no git.
repo_key() {
  local dir="$1" url top
  url="$(git -C "$dir" remote get-url origin 2>/dev/null)"
  if [ -n "$url" ]; then
    url="${url%/}"; url="${url%.git}"
    basename "$url"
    return
  fi
  top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)"
  [ -n "$top" ] && { basename "$top"; return; }
  basename "$dir"
}

REPO="$(repo_key "$CWD")"

# Sync: fetch the shared remote first, so an INDEX line another machine committed
# is visible below. Bounded to two seconds through python3; a timeout or non-zero
# exit logs one line to reports/sync.log and leaves the local store as it is.
FETCHED=0
if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
  GIT_TERMINAL_PROMPT=0 python3 -c '
import subprocess, sys, os, signal, tempfile, datetime
store = sys.argv[1]

def logline(msg):
    os.makedirs(os.path.join(store, "reports"), exist_ok=True)
    with open(os.path.join(store, "reports", "sync.log"), "a", encoding="utf-8") as fh:
        fh.write("%s recall pull: %s\n" % (datetime.date.today().isoformat(), " ".join(str(msg).split())[:200]))

# Run the fetch in its own session so a real ssh remote that hangs can be killed
# whole: killpg reaches the git fetch and ssh grandchildren, which a plain
# subprocess timeout leaves running (they inherit the pipe and keep it open, so
# the two-second bound would not hold). stderr goes to a file, not a pipe, so
# there is nothing to drain after the kill and wait() returns at once. Exits 0
# only when the fetch succeeded.
rc = 1
fd, errpath = tempfile.mkstemp()
os.close(fd)
try:
    ef = open(errpath, "wb")
    p = subprocess.Popen(sys.argv[2:], stdout=subprocess.DEVNULL,
                         stderr=ef, start_new_session=True)
    try:
        rc = p.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass
        try:
            p.wait(timeout=1)
        except Exception:
            pass
        ef.close()
        logline("timeout")
    else:
        ef.close()
        if rc != 0:
            try:
                with open(errpath, "rb") as rf:
                    msg = rf.read().decode("utf-8", "replace").strip()[:200]
            except Exception:
                msg = ""
            logline(msg or "nonzero exit")
finally:
    try:
        os.unlink(errpath)
    except Exception:
        pass
sys.exit(1 if rc else 0)
' "$STORE" git -C "$STORE" fetch -q origin 2>/dev/null && FETCHED=1
fi

# --- The store lock: the same block sits in mem-capture.sh, mem-recall.sh and
# mem-weekly.sh. One flock(2) on .git/loam-mem.lock serializes every local write
# to the store: capture's spool drain and commit, every rebase and its abort,
# recall's handoff commit, and mem-weekly.sh's retention and commit. A write or
# commit landing in another session's rebase would be lost to its abort.
# python3 takes the lock (macOS ships no flock(1)) on this shell's fd 9. It
# holds while any process keeps fd 9 open, and the kernel frees it when the last
# one exits: no stale lock. Every store git call keeps fd 9, so killing this
# shell never frees the lock while its git still runs; the -c flags keep git
# from starting a gc, maintenance or fsmonitor daemon that would hold it on.
SGIT=(git -C "$STORE" -c gc.auto=0 -c maintenance.auto=false -c core.fsmonitor=false
  -c user.name=memstore -c user.email=memstore@localhost)
# bounded SECS CMD...: run CMD in its own process group and kill the group after
# SECS seconds, or at $DEADLINE (an epoch time) when that comes first; exit 124.
bounded() {
  python3 -c '
import os, signal, subprocess, sys, time
cap = float(sys.argv[1])
if sys.argv[2]:
    cap = min(cap, float(sys.argv[2]) - time.time())
if cap <= 0:
    sys.exit(124)
p = subprocess.Popen(sys.argv[3:], close_fds=False, start_new_session=True)
try:
    sys.exit(p.wait(timeout=cap))
except subprocess.TimeoutExpired:
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass
    p.wait()
    sys.exit(124)
' "$1" "${DEADLINE:-}" "${@:2}"
}
# Under the lock no other store git runs, so an index.lock is a killed git's and
# a rebase in progress is a killed holder's: remove the one, abort the other
# (which restores main with every commit). The abort ignores $DEADLINE, since a
# half-done rebase is worse than a late hook. Succeeds only when neither is
# left; a caller whose recovery failed writes nothing to the working tree.
store_recover() {
  rm -f "$STORE/.git/index.lock" 2>/dev/null
  if [ -d "$STORE/.git/rebase-merge" ] || [ -d "$STORE/.git/rebase-apply" ]; then
    DEADLINE='' bounded 1 "${SGIT[@]}" rebase --abort >/dev/null 2>&1
  fi
  [ ! -e "$STORE/.git/index.lock" ] && [ ! -d "$STORE/.git/rebase-merge" ] && [ ! -d "$STORE/.git/rebase-apply" ]
}
# store_lock SECS: take the lock within SECS seconds (and by $DEADLINE), then
# recover; on failure hold nothing. A directory at the lock path is the earlier
# mkdir lock, which holds nothing, so it is removed first.
store_lock() {
  [ -d "$STORE/.git/loam-mem.lock" ] && rmdir "$STORE/.git/loam-mem.lock" 2>/dev/null
  { exec 9>>"$STORE/.git/loam-mem.lock"; } 2>/dev/null || return 1
  python3 -c '
import fcntl, signal, sys, time
cap = float(sys.argv[1])
if sys.argv[2]:
    cap = min(cap, float(sys.argv[2]) - time.time())
signal.signal(signal.SIGALRM, lambda *_: sys.exit(1))
if cap > 0:
    signal.setitimer(signal.ITIMER_REAL, cap)
    fcntl.flock(9, fcntl.LOCK_EX)
else:
    fcntl.flock(9, fcntl.LOCK_EX | fcntl.LOCK_NB)
' "$1" "${DEADLINE:-}" 2>/dev/null && store_recover && return 0
  exec 9>&-
  return 1
}
# --- end of the store lock block.

HANDOFF_FILE="$STORE/handoff/$REPO.md"
LOCKED=0
if [ -d "$STORE/.git" ] && { [ "$FETCHED" = 1 ] || [ -f "$HANDOFF_FILE" ]; } && store_lock 1; then
  LOCKED=1
  # A conflicted or timed-out rebase must leave the tree untouched, so abort it;
  # under the lock the only rebase in progress is this one. When even the abort
  # fails, write nothing: the next holder recovers it.
  if [ "$FETCHED" = 1 ] && "${SGIT[@]}" rev-parse -q --verify refs/remotes/origin/main >/dev/null \
    && ! bounded 3 "${SGIT[@]}" -c merge.renames=false rebase -q -s recursive refs/remotes/origin/main >/dev/null 2>&1; then
    store_recover || LOCKED=0
    mkdir -p "$STORE/reports" 2>/dev/null
    printf '%s recall pull: rebase failed\n' "$(date +%F)" >>"$STORE/reports/sync.log" 2>/dev/null
  fi
elif [ ! -d "$STORE/.git" ] && [ -f "$HANDOFF_FILE" ]; then
  LOCKED=1  # a store with no git has nothing to lock or commit
fi

# Handoff: claim the one per-repo handoff note, if present. Read it (cut at 1500
# bytes), archive it under the claiming session so the next session never re-reads
# it, then commit and background-push the archive. One writer, read once. Only
# under the store lock; a busy store leaves the note for the next session.
HANDOFF_TEXT=""
HANDOFF_N=0
if [ "$LOCKED" = 1 ] && [ -f "$HANDOFF_FILE" ]; then
  HANDOFF_TEXT="$(head -c 1500 "$HANDOFF_FILE" 2>/dev/null)"
  HANDOFF_N=1
  mkdir -p "$STORE/handoff/$REPO/archive" 2>/dev/null || true
  mv "$HANDOFF_FILE" "$STORE/handoff/$REPO/archive/$(date +%F)-$SID8.md" 2>/dev/null || true
  export GIT_TERMINAL_PROMPT=0
  if [ -d "$STORE/.git" ]; then
    mkdir -p "$STORE/reports" 2>/dev/null || true
    bounded 1 "${SGIT[@]}" add -A >/dev/null 2>&1 || true
    bounded 1 "${SGIT[@]}" commit -qm "handoff $(date +%F) $REPO $SID8" >/dev/null 2>&1 || true
    if "${SGIT[@]}" remote get-url origin >/dev/null 2>&1; then
      ( "${SGIT[@]}" push -q origin main </dev/null >>"$STORE/reports/sync.log" 2>&1 9>&- & )
    fi
  fi
fi
exec 9>&-

INDEX="$STORE/traces/$REPO/INDEX.md"
# Nothing to show only when there is neither an index nor a claimed handoff.
[ -f "$INDEX" ] || [ "$HANDOFF_N" -eq 1 ] || exit 0

INDEX_LINES=""
N_SESS=0
if [ -f "$INDEX" ]; then
  INDEX_LINES="$(tail -n 5 "$INDEX")"
  N_SESS="$(printf '%s\n' "$INDEX_LINES" | grep -c .)"
fi

TRACES_DIR="$STORE/traces/$REPO"
TRACES_COUNT="$(find "$TRACES_DIR" -type f \( -name '*.jsonl' -o -name '*.jsonl.gz' \) 2>/dev/null | wc -l | tr -d ' ')"

# The newest note's first three hint bullets, when the store holds notes here.
NOTES_DIR="$STORE/notes/$REPO"
NOTES_COUNT=0
HINT_BULLETS=""
HINT_N=0
if [ -d "$NOTES_DIR" ]; then
  NOTES_COUNT="$(find "$NOTES_DIR" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  NEWEST="$(ls -t "$NOTES_DIR"/*.md 2>/dev/null | head -1)"
  if [ -n "$NEWEST" ]; then
    HINT_BULLETS="$(awk '
      tolower($0) ~ /hint/ { inhint=1; next }
      inhint && /^#/ { inhint=0 }
      inhint && /^[[:space:]]*[-*] / && c<3 { print; c++ }
    ' "$NEWEST")"
    HINT_N="$(printf '%s\n' "$HINT_BULLETS" | grep -c .)"
  fi
fi

# The handoff sits right after Loaded: and before the INDEX lines and hint
# bullets, so head -c 4000 trims those before it ever reaches the handoff.
{
  printf '## Memory (%s)\n' "$REPO"
  printf 'Loaded: %s recent sessions, %s hint bullets, %s handoff\n' "$N_SESS" "$HINT_N" "$HANDOFF_N"
  if [ -n "$HANDOFF_TEXT" ]; then
    printf '## Handoff (claimed now)\n'
    printf '%s\n' "$HANDOFF_TEXT"
  fi
  [ -n "$INDEX_LINES" ] && printf '%s\n' "$INDEX_LINES"
  [ -n "$HINT_BULLETS" ] && printf '%s\n' "$HINT_BULLETS"
  printf 'Not loaded: %s notes, %s traces under .loam/memory; reach them with memsearch <pattern> or mem-inspect <session>; do not grep the raw traces. To hand off to the next session on any machine, write .loam/memory/handoff/%s.md.\n' "$NOTES_COUNT" "$TRACES_COUNT" "$REPO"
  printf 'Label every recalled item before acting on it: supported (the trace shows it), contradicts (the current repo or host disagrees), near-match (similar task, different conditions), insufficient (not enough to act); check git log -1, hostname, and tool versions first.\n'
} | head -c 4000
exit 0
