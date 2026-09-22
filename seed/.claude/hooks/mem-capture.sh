#!/usr/bin/env bash
# mem-capture.sh - scrub, gzip, and store the session transcript in the memory store.
#
# Hook events: SessionEnd, PreCompact, and Stop (Stop is throttled). Reads the
# hook JSON on stdin (transcript_path, session_id, cwd), scrubs known secret
# shapes from the transcript before anything is written, and stores the result
# gzipped at $STORE/traces/<repo>/<date>-<sid8>.jsonl.gz plus one INDEX.md line.
# Zero model calls. Idempotent on the scrubbed content's sha256 (kept beside the
# trace as <date>-<sid8>.sha), so a repeat capture adds no file and no line.
# After a capture it links <repo-toplevel>/.loam/memory -> $STORE when absent.
# It then commits the store and, when an `origin` remote is set, pushes it in the
# background so a second machine sees what this session learned. Prints nothing.
#
# Usage: mem-capture.sh [--throttle SECONDS]
#   --throttle SECONDS  exit 0 without capturing when this session_id was captured
#                       less than SECONDS ago (used by the Stop entry). The gate
#                       runs before any python3, so a throttled Stop spawns none.
#
# The secret scrubber ports key patterns from agentmemory src/functions/privacy.ts
# (Apache-2.0) and the PEM-block and URL-credential patterns from Hindsight
# hindsight-api-slim/tests/test_memory_defense.py (MIT); see the memory-v2 plan's
# "Borrowed code" note. Commit hashes are not pinned in this checkout.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook, never blocks).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

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

SID8="$(printf '%s' "$SID" | cut -c1-8)"
# One session maps to one trace file no matter which calendar day it resumes on:
# reuse an existing *-<sid8>.jsonl.gz if this session was captured before, else
# name a fresh file with today's date.
OUT=""
for existing in "$DST"/*-"$SID8".jsonl.gz; do
  [ -f "$existing" ] && { OUT="$existing"; break; }
done
[ -n "$OUT" ] || OUT="$DST/$(date +%F)-$SID8.jsonl.gz"
SHAFILE="${OUT%.jsonl.gz}.sha"

# The one transcript-reading pass: scrub secrets, hash the scrubbed bytes, and
# gzip them to OUT only when they differ from the recorded sha. Prints
# "<changed>\t<first-user-line>" where changed is 1 when a file was written.
RES="$(python3 - "$TP" "$OUT" "$SHAFILE" <<'PY'
import sys, os, re, gzip, hashlib, json

tp, out, shafile = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(tp, "rb") as fh:
        raw = fh.read()
except Exception:
    sys.exit(0)
text = raw.decode("utf-8", "replace")

# Compiled scrubbers, most specific first. Each match becomes [REDACTED:<kind>];
# the generic, Bearer, and URL-credential subs keep a capture group so only the
# secret value is replaced and the surrounding JSON stays valid.
SUBS = [
    (re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----", re.DOTALL),
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
                item = payload.get("item")
                if isinstance(item, dict) and item.get("type") == "user_message":
                    txt = item.get("text")
                    if txt is None:
                        txt = item.get("message")
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
        prev = fh.read().strip()
except Exception:
    prev = ""

if prev == digest and os.path.exists(out):
    sys.stdout.write("0\t" + first)
    sys.exit(0)
try:
    with gzip.open(out, "wb") as gz:
        gz.write(data)
    with open(shafile, "w", encoding="utf-8") as fh:
        fh.write(digest)
except Exception:
    sys.exit(0)
sys.stdout.write("1\t" + first)
PY
)"

CHANGED="${RES%%$'\t'*}"
FIRST="${RES#*$'\t'}"
[ "$RES" = "$CHANGED" ] && FIRST=""

# Nothing was written and nothing exists -> a failed or empty capture; bail.
[ -f "$OUT" ] || exit 0

# Give the checkout a gitignored path into the store, so agents navigate memory
# by path. Only when this cwd is a git checkout and .loam/memory is not already a
# file or link; never replace an existing one.
TOP="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$TOP" ] && [ ! -e "$TOP/.loam/memory" ] && [ ! -L "$TOP/.loam/memory" ]; then
  mkdir -p "$TOP/.loam" 2>/dev/null && ln -s "$STORE" "$TOP/.loam/memory" 2>/dev/null || true
fi

# Only an actual write earns an INDEX line, and one session gets one line: a
# transcript keeps growing after Stop fires, so SessionEnd re-copies under the
# same name (sha unchanged -> changed=0, exited above) and must not add a second
# line. A resumed session that changed only its trace skips the line but still
# syncs the new trace below.
[ "$CHANGED" = "1" ] || exit 0
if ! grep -q " | $SID8 | " "$DST/INDEX.md" 2>/dev/null; then
  BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
  SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
  HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
  printf '%s | %s | %s@%s | %s | %s\n' \
    "$(date +%F)" "$SID8" "$BRANCH" "$SHORT" "$HOST" "$FIRST" >> "$DST/INDEX.md"
fi

# Sync the store through git: commit the new trace and INDEX line, then push to the
# shared remote in the background so the hook never waits on the network. With no
# origin every step is a local commit and nothing leaves the machine. The scrub
# (above) runs before this, so only scrubbed transcripts ever reach the history.
export GIT_TERMINAL_PROMPT=0
if [ ! -d "$STORE/.git" ]; then
  git -C "$STORE" init -q -b main 2>/dev/null || true
  if [ -n "${LOAM_MEMSTORE_REMOTE:-}" ] && ! git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
    git -C "$STORE" remote add origin "$LOAM_MEMSTORE_REMOTE" 2>/dev/null || true
  fi
fi
if [ -d "$STORE/.git" ]; then
  # Keep the ephemeral throttle marks and the sync log out of git: the marks are
  # local per-session timestamps, and the log is appended on every failed push and
  # by recall, so tracking it would dirty the tree and make the next pull --rebase
  # refuse. Written on every capture, not only on init, so a store an older
  # mem-weekly left with a stale 'traces/' ignore line is corrected and its traces
  # resume syncing. Byte-identical to the string mem-weekly.sh writes.
  printf '.throttle/\nreports/sync.log\n' > "$STORE/.gitignore" 2>/dev/null || true
  mkdir -p "$STORE/reports" 2>/dev/null || true
  git -C "$STORE" add -A 2>/dev/null || true
  git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost \
    commit -qm "capture $(date +%F) $REPO $SID8" 2>/dev/null || true
  if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
    ( git -C "$STORE" push -q origin main </dev/null >>"$STORE/reports/sync.log" 2>&1 & )
  fi
fi
exit 0
