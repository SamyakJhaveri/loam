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
# (when one is set), so a line another machine committed shows up here: it waits
# at most two seconds for a fetch, then rebases onto origin/main under the store
# lock mem-capture.sh describes, bounded so the whole hook ends within its
# five-second timeout. A fetch still running after two seconds is not killed: it
# finishes in the background and the next session rebases onto what it fetched.
# A timeout or failure logs one line to reports/sync.log and falls back to the
# local store. The rebase runs with rename
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

# --- The store lock: the same block sits in mem-capture.sh, mem-recall.sh and
# mem-weekly.sh. One flock(2) on .git/loam-mem.lock serializes every local write
# to the store: capture's spool drain and commit, every rebase and its abort,
# recall's handoff commit, and mem-weekly.sh's retention and commit. A write or
# commit landing in another session's rebase would be lost to its abort.
# python3 takes the lock (macOS ships no flock(1)) on this shell's fd 9. It
# holds while any process keeps fd 9 open, and the kernel frees it when the last
# one exits: no stale lock. Every store git call keeps fd 9, so killing this
# shell never frees the lock while its git still runs; the -c flags keep git
# from starting a gc, maintenance or fsmonitor daemon that would hold it on,
# and commit.gpgsign=false keeps a global signing setting with no usable key
# from failing every commit, which would leave captures in the spool for good.
# Store git runs no hook (NOHOOKS), so no hook child can inherit fd 9 and keep
# the lock after git returns: core.hooksPath=/dev/null turns off the store's,
# global and template hook files, and hook.<name>.enabled=false each hook
# defined in any config (git 2.54 and later), which core.hooksPath misses. That
# goes through --config-env, since -c splits at the first `=` and a hook name
# may hold one; a nameless `[hook] command` is the hook named "".
export LOAM_MEM_FALSE=false
NOHOOKS=(-c core.hooksPath=/dev/null)
while IFS= read -r -d '' k; do
  case $k in hook.command | hook.event) k= ;; *) k=${k#hook.}; k=${k%.*} ;; esac
  NOHOOKS+=("--config-env=hook.$k.enabled=LOAM_MEM_FALSE")
done < <(git -C "$STORE" config -z --name-only --get-regexp '^hook\.(.*\.)?(command|event)$' 2>/dev/null)
SGIT=(git -C "$STORE" -c gc.auto=0 -c maintenance.auto=false -c core.fsmonitor=false
  -c commit.gpgsign=false -c user.name=memstore -c user.email=memstore@localhost "${NOHOOKS[@]}")
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
# Under the lock no other hook runs store git, but a git outside it can (a
# person, an editor or a script in the store), so an index.lock is removed only
# when index_lock_free finds no holder; one that is held, or that no scan
# could clear, stays and fails the recovery, and the next holder scans again.
# A rebase in progress is a killed holder's: abort it (which restores
# main with every commit). With a rebase in progress the scan and the abort
# ignore $DEADLINE and share a window that ends one second after it, or after
# now once it has passed (recall's rebase can run to $DEADLINE): a half-done
# rebase is worse than a late hook, and they end no later than an abort
# started at $DEADLINE would.
# Succeeds only when neither is left; a caller whose recovery failed writes
# nothing to the working tree.
store_recover() {
  local rebase= end=${DEADLINE:-}
  if [ -d "$STORE/.git/rebase-merge" ] || [ -d "$STORE/.git/rebase-apply" ]; then
    rebase=1
    [ -n "$end" ] && end=$(python3 -c 'import sys, time; print(max(float(sys.argv[1]), time.time()) + 1)' "$end")
  fi
  if [ -e "$STORE/.git/index.lock" ]; then
    DEADLINE=$end index_lock_free "$STORE/.git/index.lock" "$STORE" || return 1
    rm -f "$STORE/.git/index.lock" 2>/dev/null
  fi
  if [ -n "$rebase" ]; then
    DEADLINE=$end bounded 1 "${SGIT[@]}" rebase --abort >/dev/null 2>&1
  fi
  [ ! -e "$STORE/.git/index.lock" ] && [ ! -d "$STORE/.git/rebase-merge" ] && [ ! -d "$STORE/.git/rebase-apply" ]
}
# index_lock_free LOCK STORE: succeed only when a holder scan, bounded to five
# seconds (and $DEADLINE), runs to its end and finds no holder; a held LOCK, a
# scanner error and a timeout all fail. A holder has LOCK open, or is a git
# whose working directory is STORE: `git commit -a` closes the index.lock it
# wrote and keeps it through the hooks and the message editor. With /proc
# (Linux) python3 reads every thread's exe, cwd and fd list under
# /proc/<pid>/task/<tid>: a process whose main thread has exited is a zombie
# leader with an unreadable /proc/<pid>/fd, while another of its threads still
# holds the shared fds. A pid, thread or fd that vanishes mid-scan, and an entry
# that cannot be read (another user's process, pid 1, a zombie, a non-dumpable
# process), are passed over; any other error (EMFILE, say) ends the scan
# without a result. Files match on (st_dev, st_ino), not link text,
# which differs in another mount namespace; a git matches on its exe's name,
# since one host can have several git binaries. Without /proc (macOS) lsof
# scans, for LOCK and for a git's cwd: exit 1 with no pid printed is no holder,
# and no lsof is no scan.
index_lock_free() {
  local out rc
  if [ -d /proc/self/fd ]; then
    bounded 5 python3 -c '
import os, sys
st = os.stat(sys.argv[1])
lock = (st.st_dev, st.st_ino)
st = os.stat(sys.argv[2])
top = (st.st_dev, st.st_ino)
for pid in os.listdir("/proc"):
    if not pid.isdigit():
        continue
    try:
        tids = os.listdir("/proc/" + pid + "/task")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        continue
    for tid in tids:
        tdir = "/proc/" + pid + "/task/" + tid + "/"
        try:
            if os.readlink(tdir + "exe").rsplit("/", 1)[-1] in ("git", "git (deleted)"):
                st = os.stat(tdir + "cwd")
                if (st.st_dev, st.st_ino) == top:
                    sys.exit(1)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
        try:
            fds = os.listdir(tdir + "fd")
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        for fd in fds:
            try:
                st = os.stat(tdir + "fd/" + fd)
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
            if (st.st_dev, st.st_ino) == lock:
                sys.exit(1)
' "$1" "$2" >/dev/null 2>&1
    return
  fi
  command -v lsof >/dev/null 2>&1 || return 1
  out=$(bounded 5 lsof -t -n -P -- "$1" 2>/dev/null)
  rc=$?
  [ "$rc" = 1 ] && [ -z "$out" ] || return 1
  out=$(bounded 5 lsof -t -n -P -a -c '/^git$/' -d cwd -- "$2" 2>/dev/null)
  rc=$?
  [ "$rc" = 1 ] && [ -z "$out" ]
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
# The spool: a capture never writes the working tree directly. It writes its
# scrubbed trace, sha and INDEX line as one entry under .git/loam-spool/,
# outside the working tree, where no rebase, abort or reset reaches it. Whoever
# then holds the lock with a recovered store (the next capture, or mem-weekly.sh)
# drains the entries into the tree and commits. A capture that finds the store
# busy, or holds a rebase it cannot recover, exits 0 and its entry waits for the
# next holder. mem-recall.sh carries these functions but does not drain.
SPOOL="$STORE/.git/loam-spool"
spool_pending() {
  local e
  for e in "$SPOOL"/[0-9]*; do [ -d "$e" ] && return 0; done
  return 1
}
# Copy each entry into traces/<repo>/, under the name the session's trace
# already has there (else <day>-<sid>), append its INDEX line unless the session
# has one, and commit. Each entry carries its transcript's generation (byte
# length, then mtime, when it was read), also kept as the second line of the
# tree's .sha; an entry older than the session's trace in the tree is dropped
# unapplied, so whatever order overlapping captures publish in, the newest
# transcript wins. With $DEADLINE set, entries are applied only until three
# seconds before it, leaving time for the bounded adds, commit and HEAD lookup;
# the rest wait for the next holder. Each applied entry's own trace, sha and
# INDEX.md are force-added, so an exclude rule that ignores traces (a global
# '*.gz', the store's .git/info/exclude) does not keep them out of the commit,
# and an entry is removed only once HEAD holds its trace's exact bytes, so a
# failed copy or commit leaves it for the next drain, and draining one twice is
# harmless. Call only under the lock, after store_recover. The drain first
# removes .tmp-* directories older than five minutes, the leftovers of a killed
# or failed capture.
drain_spool() {
  local e x i repo sid day gen tgen out rel sids="" by="" head=""
  local applied=() paths=() rels=()
  find "$SPOOL" -maxdepth 1 -name '.tmp-*' -mmin +5 -exec rm -rf {} + 2> /dev/null
  [ -n "${DEADLINE:-}" ] && by=$(( ${DEADLINE%.*} - 3 ))
  for e in "$SPOOL"/[0-9]*; do
    [ -f "$e/meta" ] || continue
    [ -z "$by" ] || [ "$(date +%s)" -lt "$by" ] || break
    gen=""; { read -r repo; read -r sid; read -r day; read -r gen; } < "$e/meta"
    mkdir -p "$STORE/traces/$repo" || return 1
    out="$STORE/traces/$repo/$day-$sid.jsonl.gz"
    for x in "$STORE/traces/$repo"/*-"$sid".jsonl.gz; do
      [ -f "$x" ] && { out="$x"; break; }
    done
    tgen="$(sed -n 2p "${out%.jsonl.gz}.sha" 2>/dev/null)"
    if [[ "$gen" < "$tgen" ]]; then
      rm -rf "$e"
      continue
    fi
    cp "$e/trace.jsonl.gz" "$out" && cp "$e/sha" "${out%.jsonl.gz}.sha" || return 1
    grep -qF " | $sid | " "$STORE/traces/$repo/INDEX.md" 2>/dev/null \
      || cat "$e/index" >> "$STORE/traces/$repo/INDEX.md" || return 1
    rel="traces/$repo/${out##*/}"
    applied+=("$e"); rels+=("$rel"); sids="$sids $sid"
    paths+=("$rel" "${rel%.jsonl.gz}.sha" "traces/$repo/INDEX.md")
  done
  [ "${#applied[@]}" -gt 0 ] || return 0
  # Keep the ephemeral throttle marks and reports/ out of git: the marks are local
  # per-session timestamps, the sync log is appended on every failed push and by
  # recall, and mem-weekly regenerates the other reports wholesale from this
  # machine's traces, so tracking any of them would dirty the tree or conflict on
  # the next rebase. The attributes line merges INDEX.md by union, so two
  # machines that each append a line before pulling both keep both lines instead
  # of conflicting. Both files are written on every drain, not only on init, so
  # a store an older mem-weekly left with a stale 'traces/' ignore line is
  # corrected and its traces resume syncing. Byte-identical to what mem-weekly.sh
  # writes.
  printf '.throttle/\nreports/\n' > "$STORE/.gitignore" 2>/dev/null || true
  printf 'traces/*/INDEX.md merge=union\n' > "$STORE/.gitattributes" 2>/dev/null || true
  bounded 3 "${SGIT[@]}" add -A >/dev/null 2>&1
  bounded 3 "${SGIT[@]}" add -f -- "${paths[@]}" >/dev/null 2>&1
  bounded 3 "${SGIT[@]}" commit -qm "capture $(date +%F)$sids" >/dev/null 2>&1
  # An entry goes once HEAD's blob for its trace is the entry's own bytes,
  # hashed as git hashes that path, so a clean filter (git-lfs) matches; one that
  # hangs is cut off by the bound and the entry stays. The shell opens the entry,
  # so a relative store path is not resolved twice. Past $DEADLINE the rest stay.
  for i in "${!applied[@]}"; do
    [ -z "${DEADLINE:-}" ] || [ "$(date +%s)" -lt "${DEADLINE%.*}" ] || break
    head="$(bounded 2 "${SGIT[@]}" rev-parse -q --verify "HEAD:${rels[$i]}" 2>/dev/null)" \
      && x="$(bounded 2 "${SGIT[@]}" hash-object --path="${rels[$i]}" --stdin < "${applied[$i]}/trace.jsonl.gz" 2>/dev/null)" \
      && [ -n "$x" ] && [ "$x" = "$head" ] && rm -rf "${applied[$i]}"
  done
  return 0
}
# --- end of the store lock block.

# Sync: fetch the shared remote first, so an INDEX line another machine committed
# is visible below. python3 waits at most two seconds for it; a timeout or non-zero
# exit logs one line to reports/sync.log and leaves the local store as it is.
# It holds no lock but runs no hook either (NOHOOKS); it keeps gc on, since the
# store's only automatic gc runs after this fetch.
FETCHED=0
if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
  GIT_TERMINAL_PROMPT=0 python3 -c '
import subprocess, sys, os, tempfile, datetime
store = sys.argv[1]

def logline(msg):
    os.makedirs(os.path.join(store, "reports"), exist_ok=True)
    with open(os.path.join(store, "reports", "sync.log"), "a", encoding="utf-8") as fh:
        fh.write("%s recall pull: %s\n" % (datetime.date.today().isoformat(), " ".join(str(msg).split())[:200]))

# Run the fetch in its own session, holding none of the hook pipes (stdin and
# stdout to /dev/null, stderr to a file), so a fetch still running after the
# two-second wait outlives the hook without holding it open. It is never killed:
# a killed index-pack leaves its tmp_pack_* in the store and the next fetch
# receives the same objects again, while a fetch left to finish lands them for
# the next session. One against a hung remote runs until ssh or TCP gives up.
# Exits 0 only when the fetch succeeded within the wait.
rc = 1
fd, errpath = tempfile.mkstemp()
os.close(fd)
try:
    ef = open(errpath, "wb")
    p = subprocess.Popen(sys.argv[2:], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=ef, start_new_session=True)
    try:
        rc = p.wait(timeout=2)
    except subprocess.TimeoutExpired:
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
' "$STORE" git -C "$STORE" "${NOHOOKS[@]}" fetch -q origin 2>/dev/null && FETCHED=1
fi

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
