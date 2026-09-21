#!/usr/bin/env bash
# mem-capture.sh - copy the session transcript into the per-user memory store.
#
# Hook events: SessionEnd, PreCompact, and Stop (Stop is throttled). Reads the
# hook JSON on stdin (transcript_path, session_id, cwd), copies the transcript
# verbatim into $STORE/traces/<repo>/ and appends one INDEX.md line. Zero model
# calls. Idempotent: a re-copy of the same transcript (same sha256) adds no file
# and no INDEX line. Prints nothing.
#
# Usage: mem-capture.sh [--throttle SECONDS]
#   --throttle SECONDS  exit 0 without copying when this session_id was captured
#                       less than SECONDS ago (used by the Stop entry).
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook, never blocks).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

THROTTLE=0
if [ "${1:-}" = "--throttle" ]; then
  THROTTLE="${2:-600}"
fi

PAYLOAD="$(cat)"

# One python3 read: emit transcript_path, session_id, cwd, and the first user
# message (whitespace collapsed, cut to 90 chars) as four tab-separated fields.
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

first = ""
if tp:
    try:
        with open(tp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if not isinstance(rec, dict) or rec.get("type") != "user":
                    continue
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
                first = str(content)
                break
    except Exception:
        first = ""
first = " ".join(first.split())[:90]
sys.stdout.write("\t".join((tp, sid, cwd, first)))
' 2>/dev/null)"

# Split the four tab-separated fields.
TP="${FIELDS%%$'\t'*}"; REST="${FIELDS#*$'\t'}"
SID="${REST%%$'\t'*}"; REST="${REST#*$'\t'}"
CWD="${REST%%$'\t'*}"; FIRST="${REST#*$'\t'}"

[ -n "$TP" ] || exit 0
[ -f "$TP" ] || exit 0
[ -n "$SID" ] || exit 0

REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
DST="$STORE/traces/$REPO"
mkdir -p "$DST" 2>/dev/null || exit 0

# Throttle: skip when this session was captured within THROTTLE seconds.
if [ "$THROTTLE" -gt 0 ] 2>/dev/null; then
  MARK="$DST/.last-$SID"
  NOW="$(date +%s)"
  if [ -f "$MARK" ]; then
    PREV="$(cat "$MARK" 2>/dev/null || echo 0)"
    [ $((NOW - PREV)) -lt "$THROTTLE" ] && exit 0
  fi
  echo "$NOW" > "$MARK" 2>/dev/null || true
fi

sha() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

SID8="$(printf '%s' "$SID" | cut -c1-8)"
OUT="$DST/$(date +%F)-$SID8.jsonl"

# Copy and index only when the transcript differs from the existing copy.
if [ -f "$OUT" ] && [ "$(sha "$OUT")" = "$(sha "$TP")" ]; then
  exit 0
fi
cp "$TP" "$OUT" 2>/dev/null || exit 0

BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
printf '%s | %s | %s@%s | %s | %s\n' \
  "$(date +%F)" "$SID8" "$BRANCH" "$SHORT" "$HOST" "$FIRST" >> "$DST/INDEX.md"
exit 0
