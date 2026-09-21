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
# it, and the four trust labels every recalled item must carry (layers 3 and 5 of
# docs/research/memory-design-v2-2026-09-21.md). Output is capped at 4000 bytes.
#
# Before building the manifest it pulls the shared store from its `origin` remote
# (when one is set), bounded to five seconds, so a line another machine committed
# shows up here; a timeout or failure logs one line to reports/sync.log and falls
# back to the local store. It then claims a single per-repo handoff note left by
# an earlier session on any machine: injects it once, archives it, and pushes.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

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

# Sync: pull the shared remote first, so an INDEX line another machine committed is
# visible below. Bounded to five seconds through python3; a timeout or non-zero
# exit logs one line to reports/sync.log and leaves the local store as it is.
if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
  GIT_TERMINAL_PROMPT=0 python3 -c '
import subprocess, sys, os, datetime
store = sys.argv[1]
try:
    r = subprocess.run(sys.argv[2:], stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, timeout=5)
    if r.returncode != 0:
        raise Exception((r.stderr or b"").decode("utf-8", "replace").strip()[:200] or "nonzero exit")
except Exception as e:
    # A conflicted or timed-out rebase must leave the tree untouched, so undo it.
    # Harmless ("no rebase in progress") when the pull failed before rebasing.
    try:
        subprocess.run(["git", "-C", store, "rebase", "--abort"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception:
        pass
    os.makedirs(os.path.join(store, "reports"), exist_ok=True)
    with open(os.path.join(store, "reports", "sync.log"), "a", encoding="utf-8") as fh:
        fh.write("%s recall pull: %s\n" % (datetime.date.today().isoformat(), " ".join(str(e).split())[:200]))
' "$STORE" git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost pull --rebase -q origin main 2>/dev/null || true
fi

# Handoff: claim the one per-repo handoff note, if present. Read it (cut at 1500
# bytes), archive it under the claiming session so the next session never re-reads
# it, then commit and background-push the archive. One writer, read once.
HANDOFF_FILE="$STORE/handoff/$REPO.md"
HANDOFF_TEXT=""
HANDOFF_N=0
if [ -f "$HANDOFF_FILE" ]; then
  HANDOFF_TEXT="$(head -c 1500 "$HANDOFF_FILE" 2>/dev/null)"
  HANDOFF_N=1
  mkdir -p "$STORE/handoff/$REPO/archive" 2>/dev/null || true
  mv "$HANDOFF_FILE" "$STORE/handoff/$REPO/archive/$(date +%F)-$SID8.md" 2>/dev/null || true
  export GIT_TERMINAL_PROMPT=0
  if [ -d "$STORE/.git" ]; then
    mkdir -p "$STORE/reports" 2>/dev/null || true
    git -C "$STORE" add -A 2>/dev/null || true
    git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost \
      commit -qm "handoff $(date +%F) $REPO $SID8" 2>/dev/null || true
    if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
      ( git -C "$STORE" push -q origin main </dev/null >>"$STORE/reports/sync.log" 2>&1 & )
    fi
  fi
fi

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

# The newest note's first three hint bullets, when MEM-03 has written notes here.
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
