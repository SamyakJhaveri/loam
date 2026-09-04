#!/usr/bin/env bash
# stop-verify-gate.sh - Stop hook: deterministic turn-end verification gate.
# Fast checks on CHANGED files only: git diff --check, ruff on .py, bash -n on .sh.
# Blocks the turn with exit 2 + evidence on stderr; no-ops when nothing changed.
# Reads the JSON envelope on stdin (hooks get JSON on stdin, not env vars).
# Deliberately excludes slow checks (mypy/pytest) - this is the fast signal only.

set -uo pipefail   # no -e: collect all failures, don't abort on the first

PAYLOAD="$(cat)"

# Loop guard: if we're already inside a stop-hook continuation, pass.
ACTIVE=$(printf '%s' "$PAYLOAD" | python3 -c "import sys, json
try:
    print(str(json.load(sys.stdin).get('stop_hook_active', False)).lower())
except Exception:
    print('false')" 2>/dev/null)
[ "$ACTIVE" = "true" ] && exit 0

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
# A repo with no commits has no HEAD; diff against git's empty tree so the first
# session is still gated instead of skipped.
BASE=HEAD
git rev-parse --verify HEAD >/dev/null 2>&1 || BASE=$(git hash-object -t tree /dev/null)

# Dirty = tracked diffs vs BASE + untracked (excluding gitignored).
DIRTY=$( { git diff --name-only "$BASE"; git ls-files --others --exclude-standard; } 2>/dev/null)

# The Fable 5.1 guide tells the model not to fix pre-existing problems, so the
# gate judges only files this session edited, not every dirty file in the tree.
SESSION="$(python3 - "$ROOT" "$PAYLOAD" "$DIRTY" 2>/dev/null <<'PY'
import sys, json, os
root = os.path.realpath(sys.argv[1])
tools = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
out = []
dirty = [d for d in sys.argv[3].split("\n") if d]
try:
    tp = json.loads(sys.argv[2]).get("transcript_path") or ""
    data = open(tp, encoding="utf-8", errors="ignore") if os.path.isfile(tp) else []
except Exception:
    data = []
for line in data:
    try:
        e = json.loads(line)
        if e.get("type") != "assistant": continue
        for it in e["message"]["content"]:
            if it.get("type") == "tool_use" and it.get("name") in tools:
                fp = it["input"]["file_path"]
                rel = os.path.relpath(os.path.realpath(fp if os.path.isabs(fp) else os.path.join(root, fp)), root)
                if not rel.startswith("..") and rel not in out: out.append(rel)
            elif it.get("type") == "tool_use" and it.get("name") == "Bash":
                # A shell command that names a dirty file (sed -i, redirects, generators)
                # is a session edit too; text match is deliberate and cheap.
                cmd = str(it.get("input", {}).get("command", ""))
                for d in dirty:
                    if d in cmd and d not in out: out.append(d)
    except Exception:
        continue
print("\n".join(out))
PY
)"
# Empty SESSION (no transcript, or it recorded no edits) → judge all dirty files.
if [ -n "$SESSION" ]; then
    CHANGED="$(printf '%s\n' "$DIRTY" | grep -Fxf <(printf '%s\n' "$SESSION") || true)"
else
    CHANGED="$DIRTY"
fi
# No early exit on empty CHANGED: the claim leg (4) must run every turn, and
# legs 1-3 already no-op when CHANGED is empty.
FAIL=""

# 1. Whitespace errors / leftover conflict markers (instant).
if [ -n "$CHANGED" ]; then
    DC=$(printf '%s\n' "$CHANGED" | tr '\n' '\0' | xargs -0 git diff --check "$BASE" -- 2>/dev/null) || true
    [ -n "$DC" ] && FAIL="${FAIL}\n[git diff --check]\n${DC}\n"
fi

# 2. Ruff on changed, still-present Python files (fast).
# uv/brew installs ship ruff as a PATH binary, not an importable module, so run
# the module form first; only a missing module (not a ruff finding) falls back to
# the PATH binary, so a failing ruff is never masked as "ruff unavailable".
PY=$(printf '%s\n' "$CHANGED" | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$PY" ]; then
    if OUT=$(printf '%s\n' "$PY" | xargs python3 -m ruff check 2>&1); then
        :
    elif printf '%s' "$OUT" | grep -q "No module named ruff"; then
        if command -v ruff >/dev/null 2>&1; then
            OUT=$(printf '%s\n' "$PY" | xargs ruff check 2>&1) || FAIL="${FAIL}\n[ruff check]\n${OUT}\n"
        else
            echo "NOTE: ruff unavailable; the stop gate skipped its ruff leg." >&2
        fi
    else
        FAIL="${FAIL}\n[ruff check]\n${OUT}\n"
    fi
fi

# 3. Shell syntax on changed, still-present .sh files (instant).
SH=$(printf '%s\n' "$CHANGED" | grep -E '\.sh$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$SH" ]; then
    while read -r f; do
        [ -z "$f" ] && continue
        if ! ERR=$(bash -n "$f" 2>&1); then
            FAIL="${FAIL}\n[bash -n] ${f}:\n${ERR}\n"
        fi
    done <<< "$SH"
fi

# 4. Claims verification with no Bash or delegated-agent result this turn to back it.
CLAIM=$(python3 - "$PAYLOAD" <<'PY'
import sys, json, re
def load(l):  # one bad transcript line must not disable the leg
    try: return json.loads(l)
    except Exception: return None
try:
    p = json.loads(sys.argv[1])
    E = [x for x in map(load, open(p.get("transcript_path") or "", encoding="utf-8", errors="ignore")) if x]
except Exception:
    sys.exit(0)
msg = p.get("last_assistant_message") or ""
if not msg:
    a = [e for e in E if e.get("type") == "assistant"]
    c = a[-1].get("message", {}).get("content", []) if a else []
    msg = "".join(i.get("text", "") for i in c if isinstance(i, dict) and i.get("type") == "text")
m = re.search(r"\b(?:verified|all tests pass|tests pass|passes|confirmed|re-verified|PASSED)\b", msg, re.I) if msg and "not verified" not in msg.lower() else None
if not m: sys.exit(0)
def human(e):
    c = e.get("message", {}).get("content") if e.get("type") == "user" else None
    return isinstance(c, str) or (isinstance(c, list) and not any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c))
turn = E[max([i for i, e in enumerate(E) if human(e)] + [-1]) + 1:]
ids = {i.get("id") for e in turn if e.get("type") == "assistant"
       for i in e.get("message", {}).get("content", []) if isinstance(i, dict) and i.get("type") == "tool_use" and i.get("name") in ("Bash", "Agent", "Task", "Workflow")}
out = []
for e in turn:
    c = e.get("message", {}).get("content") if e.get("type") == "user" else None
    for i in (c if isinstance(c, list) else []):
        if isinstance(i, dict) and i.get("type") == "tool_result" and i.get("tool_use_id") in ids:
            rc = i.get("content")
            out += [rc] if isinstance(rc, str) else ([x.get("text", "") for x in rc if isinstance(x, dict) and x.get("type") == "text"] if isinstance(rc, list) else [])
ok, bad = r"\b(?:PASSED|OK|exit[ =]0)\b|" + re.escape(m.group(0)), r"\b[1-9]\d* failed\b|\bFAILED\b|\bFAIL\b|\bTraceback\b"
if not any(re.search(ok, t, re.I) and not re.search(bad, t) for t in out):  # pytest prints "5 passed", never "0 failed"
    print("CLAIM")
PY
)
if [ "$CLAIM" = "CLAIM" ]; then
    FAIL="${FAIL}\n[unverified claim]\nFinal message claims verification without command output in this turn. Run the check and paste its output, or write 'not verified'.\n"
fi

if [ -n "$FAIL" ]; then
    {
        echo "Turn-end verification gate FAILED — fix these before ending the turn:"
        printf '%b\n' "$FAIL"
        echo "(Fast deterministic checks on changed files only."
        echo " To bypass intentionally, disable the Stop hook in .claude/settings.json.)"
    } >&2
    exit 2
fi

exit 0
