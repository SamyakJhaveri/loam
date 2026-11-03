#!/usr/bin/env bash
# mem-capture.sh - scrub, gzip, and store the session transcript in the memory store.
#
# Hook events: SessionEnd, PreCompact, and Stop (Stop is throttled). Reads the
# hook JSON on stdin (transcript_path, session_id, cwd), scrubs known secret
# shapes from the transcript before anything is written, and stores the result
# gzipped at $STORE/traces/<repo>/<date>-<session_id>.jsonl.gz plus one INDEX.md
# line. Zero model calls. Idempotent on the scrubbed content's sha256 (kept beside
# the trace as <date>-<session_id>.sha), so a repeat capture adds no file and no line.
# After a capture it links <repo-toplevel>/.loam/memory -> $STORE when absent.
# The capture lands first in a spool inside the store's .git, then, under the
# store lock, in the working tree and a commit; when an `origin` remote is set it
# rebases onto the remote and pushes in the background so a second machine sees
# what this session learned. Prints nothing.
#
# Usage: mem-capture.sh [--throttle SECONDS]
#   --throttle SECONDS  exit 0 without capturing when this session_id was captured
#                       less than SECONDS ago (used by the Stop entry). The gate
#                       runs before any python3, so a throttled Stop spawns none.
#
# The secret scrubber ports the key patterns and the private-key block pattern from
# agentmemory src/functions/privacy.ts (Apache-2.0). Its URL-credential pattern joins
# agentmemory's any-scheme prefix to the user and password classes of Hindsight's
# database-URL patterns in hindsight-api-slim/hindsight_api/extensions/memory_defense.py
# (MIT). License texts in THIRD_PARTY_NOTICES. Commit hashes are not pinned in this checkout.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook, never blocks).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
# The registered timeout is ten seconds; the lock wait, the drain and every
# bounded step under the lock end by this epoch time, leaving room for the scrub.
DEADLINE="$(python3 -c 'import time; print(time.time() + 8.5)')"

# First capture on a new machine with no local store: clone the shared remote so
# this machine starts from what other machines already learned, not from empty.
# When the remote is empty or unreachable the clone is a no-op and the sync step
# below inits a fresh main branch instead.
if [ ! -d "$STORE" ] && [ -n "${LOAM_MEMSTORE_REMOTE:-}" ]; then
  GIT_TERMINAL_PROMPT=0 git clone -q -b main "$LOAM_MEMSTORE_REMOTE" "$STORE" 2>/dev/null || true
fi

THROTTLE=0
if [ "${1:-}" = "--throttle" ]; then
  THROTTLE="${2:-600}"
fi

PAYLOAD="$(cat)"

# Throttle gate first, so a burst of Stop events copies at most once per THROTTLE
# seconds for a session. The session_id is read with pure bash (no subprocess),
# so a throttled Stop runs no python3.
if [ "$THROTTLE" -gt 0 ] 2>/dev/null; then
  sid_tail="${PAYLOAD#*\"session_id\"}"
  if [ "$sid_tail" != "$PAYLOAD" ]; then
    sid_tail="${sid_tail#*:}"; sid_tail="${sid_tail#*\"}"
    SID_CHEAP="${sid_tail%%\"*}"
    if [ -n "$SID_CHEAP" ]; then
      MARK="$STORE/.throttle/$SID_CHEAP"
      NOW="$(date +%s)"
      if [ -f "$MARK" ]; then
        PREV="$(cat "$MARK" 2>/dev/null || echo 0)"
        case "$PREV" in ''|*[!0-9]*) PREV=0;; esac
        [ $((NOW - PREV)) -lt "$THROTTLE" ] && exit 0
      fi
      mkdir -p "$STORE/.throttle" 2>/dev/null || true
      echo "$NOW" > "$MARK" 2>/dev/null || true
    fi
  fi
fi

# Parse the hook payload (transcript_path, session_id, cwd) as three tab-separated
# fields. This python does not read the transcript; the single transcript-reading
# pass is the scrubber below.
FIELDS="$(printf '%s' "$PAYLOAD" | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)
tp = payload.get("transcript_path") or ""
sid = payload.get("session_id") or ""
cwd = payload.get("cwd") or ""
sys.stdout.write("\t".join((str(tp), str(sid), str(cwd))))
' 2>/dev/null)"

TP="${FIELDS%%$'\t'*}"; REST="${FIELDS#*$'\t'}"
SID="${REST%%$'\t'*}"; CWD="${REST#*$'\t'}"
[ -n "$CWD" ] || CWD="$PWD"

# Exit before the scrubber spawns when there is nothing to capture (the model-only
# startup payload the smoke test pipes in has no transcript_path).
[ -n "$TP" ] || exit 0
[ -f "$TP" ] || exit 0
[ -n "$SID" ] || exit 0

# Key a session's traces by the origin remote, not the checkout directory: the
# factory renders many worktrees (loam-154, loam-161, ...) of one repo, and a
# per-directory key would scatter their memory. Fall back to the toplevel
# basename with no origin, then to the cwd basename with no git.
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
DST="$STORE/traces/$REPO"
mkdir -p "$DST" 2>/dev/null || exit 0

# The store is a git repo (with origin when LOAM_MEMSTORE_REMOTE is set) before
# anything is written into it, so the lock and the spool below live in its .git.
export GIT_TERMINAL_PROMPT=0
if [ ! -d "$STORE/.git" ]; then
  git -C "$STORE" init -q -b main 2>/dev/null || true
  if [ -n "${LOAM_MEMSTORE_REMOTE:-}" ] && ! git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
    git -C "$STORE" remote add origin "$LOAM_MEMSTORE_REMOTE" 2>/dev/null || true
  fi
fi
[ -d "$STORE/.git" ] || exit 0

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
# Store git runs no hook, so no hook child can inherit fd 9 and keep the lock
# after git returns: core.hooksPath=/dev/null turns off the store's, global and
# template hook files, and hook.<name>.enabled=false each hook defined in any
# config (git 2.54 and later), which core.hooksPath does not reach.
SGIT=(git -C "$STORE" -c gc.auto=0 -c maintenance.auto=false -c core.fsmonitor=false
  -c core.hooksPath=/dev/null -c user.name=memstore -c user.email=memstore@localhost)
while IFS= read -r k; do k=${k#hook.}; SGIT+=(-c "hook.${k%.*}.enabled=false"); done \
  < <(git -C "$STORE" config --name-only --get-regexp '^hook\..*\.(command|event)$' 2>/dev/null)
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

# The spool: a capture never writes the working tree directly. It writes its
# scrubbed trace, sha and INDEX line as one entry under .git/loam-spool/,
# outside the working tree, where no rebase, abort or reset reaches it. Whoever
# then holds the lock with a recovered store drains the entries into the tree
# and commits. A capture that finds the store busy, or holds a
# rebase it cannot recover, exits 0 and its entry waits for the next holder.
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
# seconds before it, leaving time for the bounded add, commit and status; the
# rest wait for the next holder. Applied entries are removed only once the
# tree's traces match the commit, so a failed copy or commit leaves them for the
# next drain, and draining one twice is harmless. Call only under the lock,
# after store_recover.
drain_spool() {
  local e x repo sid day gen tgen out st sids="" by=""
  local applied=()
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
    applied+=("$e"); sids="$sids $sid"
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
  bounded 3 "${SGIT[@]}" commit -qm "capture $(date +%F)$sids" >/dev/null 2>&1
  st="$(bounded 2 "${SGIT[@]}" status --porcelain -- traces 2>/dev/null)" && [ -z "$st" ] && rm -rf "${applied[@]}"
  return 0
}

# Key by the whole session id, not a prefix: Codex thread ids are time-ordered
# UUIDv7, so Codex sessions started within about 65 s share their first 8
# characters. Traces captured under the older 8-character key keep their names;
# mem-inspect still resolves them by prefix.
# One session maps to one trace file no matter which calendar day it resumes on:
# drain_spool reuses an existing *-<session_id>.jsonl.gz if this session was
# captured before, else names a fresh file with the capture's date. OUT and
# SHAFILE here are only read, to skip a capture whose content is unchanged.
OUT=""
for existing in "$DST"/*-"$SID".jsonl.gz; do
  [ -f "$existing" ] && { OUT="$existing"; break; }
done
[ -n "$OUT" ] || OUT="$DST/$(date +%F)-$SID.jsonl.gz"
SHAFILE="${OUT%.jsonl.gz}.sha"
BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"

# The one transcript-reading pass: scrub secrets, hash the scrubbed bytes, and,
# only when they differ from the recorded sha, write one spool entry: the gzip,
# the sha and generation, the session's INDEX line and its meta (repo, sid, day,
# generation), built in a temporary directory and renamed into place whole.
# Prints "<changed>\t<first-user-line>" where changed is 1
# when an entry was written.
RES="$(python3 - "$TP" "$OUT" "$SHAFILE" "$SPOOL" "$REPO" "$SID" "$(date +%F)" "$BRANCH" "$SHORT" "$HOST" <<'PY'
import sys, os, re, gzip, hashlib, json, time

tp, out, shafile, spool, repo, sid, day, branch, short, host = sys.argv[1:11]
try:
    with open(tp, "rb") as fh:
        mtime = os.fstat(fh.fileno()).st_mtime_ns
        raw = fh.read()
except Exception:
    sys.exit(0)
# The transcript only grows, so its length, then its mtime, orders two reads of
# it; zero-padded, the string order is the numeric order.
gen = "%020d.%020d" % (len(raw), mtime)
text = raw.decode("utf-8", "replace")

# Compiled scrubbers, most specific first. Each match becomes [REDACTED:<kind>];
# the generic, Bearer, and URL-credential subs keep a capture group so only the
# secret value is replaced and the surrounding JSON stays valid.
SUBS = [
    # A key with no END line loses only its header lines and its base64 body. Line
    # breaks and indents may be real or JSON-escaped at any depth (\n, \\n, \t); a
    # quote or any other escape stops it, so every JSON string stays valid and a
    # BEGIN marker named in prose costs a few words, not the rest of the trace.
    (re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----(?:.*?-----END [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----|(?:(?:\r?\n|(?:\\+r)?\\+n)(?:[ \t]|\\+t)*[A-Za-z][A-Za-z0-9-]*: [^\"\\\r\n]*)*(?:(?:\s|\\+[nrt])+[A-Za-z0-9+/=]+)*)", re.DOTALL),
     "[REDACTED:private_key]"),
    (re.compile(r"([a-zA-Z][a-zA-Z0-9+.\-]*://[^:@/\s]+:)[^@/\s]+@"),
     r"\1[REDACTED:url_credentials]@"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"), "[REDACTED:anthropic_key]"),
    # Dashes and underscores cover the sk-proj- and sk-svcacct- formats. The
    # lookbehind skips kebab-case words (task-runner-...) but still matches after a
    # JSON-escaped \n, \r, or \t, where the character before sk- is a letter.
    (re.compile(r"(?:(?<=\\[nrt])|(?<![A-Za-z0-9]))sk-[A-Za-z0-9_-]{20,}"), "[REDACTED:openai_key]"),
    (re.compile(r"ghp_[A-Za-z0-9]{36,255}"), "[REDACTED:github_token]"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{22,}"), "[REDACTED:github_token]"),
    (re.compile(r"gh[ousr]_[A-Za-z0-9]{36,255}"), "[REDACTED:github_token]"),
    (re.compile(r"xox[abpr]-[A-Za-z0-9-]{10,}"), "[REDACTED:slack_token]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED:aws_key]"),
    (re.compile(r"AIza[0-9A-Za-z_-]{35}"), "[REDACTED:google_key]"),
    (re.compile(r"npm_[A-Za-z0-9]{36}"), "[REDACTED:npm_token]"),
    (re.compile(r"glpat-[A-Za-z0-9_-]{20,}"), "[REDACTED:gitlab_token]"),
    (re.compile(r"dop_v1_[a-f0-9]{64}"), "[REDACTED:digitalocean_token]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}"), "[REDACTED:jwt]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{10,}"), r"\1[REDACTED:bearer]"),
    # The key and value may be wrapped in a bare or JSON-escaped quote (\" inside a
    # JSONL transcript), so allow an optional \? before each quote. The value class
    # excludes the backslash too, so an escaped newline (\n) or the closing \" ends
    # the value instead of being swallowed into the next transcript line.
    (re.compile(r"(?i)((?:api[_-]?key|secret|token|password|passwd|pwd)(?:\\?[\"'])?\s*[:=]\s*(?:\\?[\"'])?)([^\s\\\"',;]{6,})"),
     r"\1[REDACTED:secret]"),
]
for rx, rep in SUBS:
    text = rx.sub(rep, text)

data = text.encode("utf-8")
digest = hashlib.sha256(data).hexdigest()


def user_text(rec):
    # The user-message text for a transcript record, or None. Two shapes:
    #   Claude - {"type":"user","message":{"content": str | [text blocks]}}
    #   Codex  - {"type":"event_msg","payload": ...} rollout line.
    if not isinstance(rec, dict):
        return None
    kind = rec.get("type")
    if kind == "user":
        msg = rec.get("message", rec)
        content = msg.get("content") if isinstance(msg, dict) else msg
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    parts.append(str(block.get("text", "")))
                else:
                    parts.append(str(block))
            content = " ".join(parts)
        return str(content)
    if kind == "event_msg":
        payload = rec.get("payload")
        if isinstance(payload, dict):
            ptype = payload.get("type")
            if ptype == "user_message":
                return str(payload.get("message", ""))
            if ptype == "item_completed":
                # codex exec (0.153) records the prompt only as a UserMessage item
                # whose content is a list of text blocks, with no user_message event.
                item = payload.get("item")
                if isinstance(item, dict) and item.get("type") in ("user_message", "UserMessage"):
                    txt = item.get("text")
                    if txt is None:
                        txt = item.get("message")
                    if txt is None and isinstance(item.get("content"), list):
                        txt = " ".join(str(b.get("text", "")) for b in item["content"] if isinstance(b, dict))
                    return str(txt if txt is not None else "")
    return None


first = ""
for line in text.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except Exception:
        continue
    txt = user_text(rec)
    if txt is None:
        continue
    txt = txt.strip()
    if not txt or txt.startswith("<"):
        continue
    first = txt
    break
first = " ".join(first.split())[:90]

prev = ""
try:
    with open(shafile, encoding="utf-8") as fh:
        prev = fh.readline().strip()
except Exception:
    prev = ""

if prev == digest and os.path.exists(out):
    sys.stdout.write("0\t" + first)
    sys.exit(0)
tmp = os.path.join(spool, ".tmp-%d" % os.getpid())
try:
    os.makedirs(tmp, exist_ok=True)
    with gzip.open(os.path.join(tmp, "trace.jsonl.gz"), "wb") as gz:
        gz.write(data)
    with open(os.path.join(tmp, "sha"), "w", encoding="utf-8") as fh:
        fh.write("%s\n%s\n" % (digest, gen))
    with open(os.path.join(tmp, "index"), "w", encoding="utf-8") as fh:
        fh.write("%s | %s | %s@%s | %s | %s\n" % (day, sid, branch, short, host, first))
    with open(os.path.join(tmp, "meta"), "w", encoding="utf-8") as fh:
        fh.write("%s\n%s\n%s\n%s\n" % (repo, sid, day, gen))
    os.rename(tmp, os.path.join(spool, "%020d-%d" % (time.time_ns(), os.getpid())))
except Exception:
    sys.exit(0)
sys.stdout.write("1\t" + first)
PY
)"

CHANGED="${RES%%$'\t'*}"

# Give the checkout a gitignored path into the store, so agents navigate memory
# by path. Only when this cwd is a git checkout and .loam/memory is not already a
# file or link; never replace an existing one.
if [ "$CHANGED" = "1" ] || [ -f "$OUT" ]; then
  TOP="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)"
  if [ -n "$TOP" ] && [ ! -e "$TOP/.loam/memory" ] && [ ! -L "$TOP/.loam/memory" ]; then
    mkdir -p "$TOP/.loam" 2>/dev/null && ln -s "$STORE" "$TOP/.loam/memory" 2>/dev/null || true
  fi
fi

# Only an actual change earns a spool entry, and one session gets one INDEX line:
# a transcript keeps growing after Stop fires, so SessionEnd re-scrubs it (sha
# unchanged -> no entry) and drain_spool never adds a second line for a session.
# A resumed session that changed only its trace still syncs the new trace.
# With no entry pending there is nothing to commit. A busy store, or a leftover
# rebase that cannot be recovered, leaves the entry for the next holder.
spool_pending || exit 0
store_lock 3 || exit 0
drain_spool
exec 9>&-
mkdir -p "$STORE/reports" 2>/dev/null || true

# Pull before push, in the background so the hook never waits on the network:
# fetch, rebase this machine's commits onto the remote's, then push, so a
# capture made while another machine pushed first is not rejected and left
# behind. Traces are per-session files and INDEX.md merges by union, so the
# rebase does not conflict; rename detection is off and the strategy is
# `-s recursive`, as in recall's pull (see mem-recall.sh). Only the drain and the
# rebase hold the store lock; the fetch and push stay outside it, so a slow
# remote never stalls another session. The rebase is bounded, and a failed or
# timed-out one is aborted under the lock before it is released. A failure logs
# to reports/sync.log and keeps the capture committed locally for the next sync
# to carry. With no origin every step is a local commit and nothing leaves the
# machine; the scrub (above) runs first, so only scrubbed transcripts ever reach
# the history.
if "${SGIT[@]}" remote get-url origin >/dev/null 2>&1; then
  ( {
    DEADLINE=''  # the background is outside the hook's timeout; each step keeps its own bound
    "${SGIT[@]}" fetch -q origin || exit 0
    if "${SGIT[@]}" rev-parse -q --verify refs/remotes/origin/main >/dev/null; then
      store_lock 30 || { printf '%s capture sync: store busy or not recoverable\n' "$(date +%F)"; exit 0; }
      drain_spool
      if ! bounded 20 "${SGIT[@]}" -c merge.renames=false rebase -q -s recursive refs/remotes/origin/main; then
        store_recover
        printf '%s capture sync: rebase failed\n' "$(date +%F)"
        exit 0
      fi
      exec 9>&-
    fi
    "${SGIT[@]}" push -q origin main
  } </dev/null >>"$STORE/reports/sync.log" 2>&1 & )
fi
exit 0
