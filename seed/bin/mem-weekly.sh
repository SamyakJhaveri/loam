#!/usr/bin/env bash
# mem-weekly.sh - weekly maintenance for the memory store (run from cron).
#
# Deletes traces older than a year, regenerates the recurring-errors and counts
# reports from the captured traces, commits the store as a git baseline, then
# pulls and pushes the shared remote when one is set. Reports stay local: they are
# gitignored, so two machines' regenerated reports never conflict on a pull and
# the working tree is clean for the rebase. Zero model calls. The cron line is
# documented in docs/HARNESS.md; nothing installs it.
#
# The error-signature normalizer (first 100 chars, digits -> N) is ported from
# SuperClaude src/superclaude/pm_agent/reflexion.py (_create_error_signature, MIT);
# license text in THIRD_PARTY_NOTICES. Commit hash not pinned here.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Usage: mem-weekly.sh [--dry-run]
#   --dry-run  print the traces the retention step would delete, then exit;
#              nothing is deleted, written, committed or pushed.

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

# Retention picks trace files older than 365 days by mtime. Never INDEX.md, never
# anything under notes/ or reports/.
old_traces() { find traces -type f -mtime +365 ! -name 'INDEX.md' -print 2>/dev/null; }

case "${1:-}" in
  "") ;;
  --dry-run)
    cd "$STORE" 2>/dev/null && [ -d traces ] || exit 0
    old_traces | sed 's/^/would delete /'
    exit 0 ;;
  *) echo "usage: mem-weekly.sh [--dry-run]" >&2; exit 2 ;;
esac

mkdir -p "$STORE" || exit 0
cd "$STORE" || exit 0
STORE="$PWD"
mkdir -p reports
[ -d .git ] || git init -q -b main 2>/dev/null
[ -d .git ] || exit 0

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
# --- end of the store lock block.

# Retention and the baseline commit run under the store lock, so they never
# land inside a hook's rebase. A store busy for ten seconds skips them and the
# sync this week (one log line) and still regenerates the reports.
LOCKED=0
if store_lock 10; then
  LOCKED=1
  # Retention: drop old traces (old_traces above) before the reports read them.
  # Each deletion is logged so a forgotten transcript leaves an audit line.
  if [ -d traces ]; then
    old_traces | while IFS= read -r old; do
      printf '%s deleted %s\n' "$(date +%F)" "$old" >> reports/retention.log
      rm -f -- "$old" 2>/dev/null || true
    done
  fi

  # Commit the store as a git baseline. Traces and INDEX.md are tracked and
  # pushed once mem-capture.sh's secret scrub has run over them. The ephemeral
  # throttle marks and reports/ stay out of git: every report is regenerated
  # wholesale from this machine's traces and has no meaning on another machine.
  # The .gitignore and the .gitattributes (INDEX.md merges by union, so two
  # machines' appended lines both survive a rebase) are byte-identical to the
  # ones mem-capture.sh writes, so the two never ping-pong a change. git rm -r
  # --cached un-tracks reports an older run committed (a no-op otherwise).
  printf '.throttle/\nreports/\n' > .gitignore
  printf 'traces/*/INDEX.md merge=union\n' > .gitattributes
  "${SGIT[@]}" rm -r --cached -q reports 2>/dev/null || true
  "${SGIT[@]}" add -A 2>/dev/null \
    && bounded 30 "${SGIT[@]}" commit -qm "weekly $(date +%F)" >/dev/null 2>&1 || true
  exec 9>&-
else
  printf '%s weekly: store busy or not recoverable; skipped retention and sync\n' "$(date +%F)" >> reports/sync.log
fi

# Recurring errors: extract error lines from every trace (gzipped and plain),
# normalize each to a signature (first 100 chars, digits -> N) so runs that differ
# only in a port or pid collapse into one recurrence, and count the top 20.
python3 - <<'PY' > reports/recurring-errors.md
import collections, glob, gzip, re

ERR = re.compile(r'(?:Error: |RuntimeError|Traceback)[^"\\\n]{0,60}')
DIGITS = re.compile(r'\d')
counts = collections.Counter()
for fp in glob.glob('traces/*/*.jsonl') + glob.glob('traces/*/*.jsonl.gz'):
    opener = gzip.open if fp.endswith('.gz') else open
    try:
        with opener(fp, 'rt', encoding='utf-8', errors='replace') as fh:
            for line in fh:
                for match in ERR.findall(line):
                    counts[DIGITS.sub('N', match[:100])] += 1
    except Exception:
        continue
for sig, n in counts.most_common(20):
    print('%2d %s' % (n, sig))
PY

# Capture, retrieval, and application counts, so the weekly report says whether the
# memory layer is used, not only which errors recur. All three read gzipped traces.
# The recall manifest (mem-recall.sh) itself names memsearch and every trust word,
# so its lines are skipped first - otherwise every session would score one
# retrieval and one application from the injected manifest, not from real use.
# Application requires the label form the manifest asks for (a "label" word near a
# trust word), not the bare word, which occurs in ordinary prose ("not supported").
read -r capture retrieval application < <(python3 - <<'PY'
import glob, gzip, re

files = glob.glob('traces/*/*.jsonl') + glob.glob('traces/*/*.jsonl.gz')
RET = re.compile('memsearch')
APP = re.compile(r'\blabel\w*\b[^\n]{0,40}\b(supported|contradicts|near-match|insufficient)\b', re.I)
# Markers unique to the recall manifest (mem-recall.sh); a line carrying one is the
# injected manifest, not the agent's own use, so it is not counted.
MANIFEST = re.compile('Not loaded:|Label every recalled item')
retrieval = application = 0
for fp in files:
    opener = gzip.open if fp.endswith('.gz') else open
    try:
        with opener(fp, 'rt', encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if MANIFEST.search(line):
                    continue
                if RET.search(line):
                    retrieval += 1
                if APP.search(line):
                    application += 1
    except Exception:
        continue
print(len(files), retrieval, application)
PY
)

sessions="n/a"
CLAUDE_PROJECTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
CODEX_SESSIONS="${CODEX_HOME:-$HOME/.codex}/sessions"
if [ -d "$CLAUDE_PROJECTS" ] || [ -d "$CODEX_SESSIONS" ]; then
  claude_n=0; codex_n=0
  [ -d "$CLAUDE_PROJECTS" ] && claude_n=$(ls "$CLAUDE_PROJECTS"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
  [ -d "$CODEX_SESSIONS" ] && codex_n=$(find "$CODEX_SESSIONS" -type f -name 'rollout-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
  sessions=$((claude_n + codex_n))
fi
{
  printf 'capture %s traces, %s sessions seen\n' "${capture:-0}" "$sessions"
  printf 'retrieval %s\n' "${retrieval:-0}"
  printf 'application %s\n' "${application:-0}"
} > reports/counts.md

# Share the store: fetch the remote, rebase onto it under the store lock, then
# push this baseline. Foreground (this runs from cron, not a hook); the fetch and
# push stay outside the lock. Rename detection is off, as in recall's pull, so a
# handoff two machines archived under two names does not conflict; see
# mem-recall.sh for why the rebase names `-s recursive`. With no origin every
# step is skipped; a conflict or unreachable remote aborts the rebase under the
# lock, logs one line, and leaves the tree as it is.
export GIT_TERMINAL_PROMPT=0
sync_rebase() {
  "${SGIT[@]}" rev-parse -q --verify refs/remotes/origin/main >/dev/null || return 0
  store_lock 10 || return 1
  bounded 30 "${SGIT[@]}" -c merge.renames=false rebase -q -s recursive refs/remotes/origin/main \
    || { store_recover; exec 9>&-; return 1; }
  exec 9>&-
}
if [ "$LOCKED" = 1 ] && "${SGIT[@]}" remote get-url origin >/dev/null 2>&1; then
  { "${SGIT[@]}" fetch -q origin && sync_rebase && "${SGIT[@]}" push -q origin main ; } >> reports/sync.log 2>&1 \
    || printf '%s weekly sync failed\n' "$(date +%F)" >> reports/sync.log
fi
exit 0
