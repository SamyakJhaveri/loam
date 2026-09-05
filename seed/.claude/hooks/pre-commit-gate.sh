#!/usr/bin/env bash
# pre-commit-gate.sh - PreToolUse hook on Bash; fires only on a `git commit`.
#
# Blocks a commit unless run-validate-waves.sh has written a fresh
# .validation_passed sentinel at the repo root. The sentinel must exist, be
# under 30 minutes old, record both validation waves (waves_passed>=2), and be
# newer than every modified or untracked file in the working tree. Any failure
# blocks with the fix named. sentinel-cleanup.sh deletes the sentinel on the
# next edit, so this gate re-fires after any change.
#
# Exit codes (hook protocol): 0 = allow, 2 = BLOCK (stderr shown to Claude).

set -uo pipefail
PAYLOAD="$(cat)"
# Extract command (line 1..) and cwd (line 0) in one pass. Malformed JSON -> empty.
EXTRACT="$(printf '%s' "$PAYLOAD" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    assert isinstance(d, dict)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
cmd = ti.get("command", "") if isinstance(ti, dict) else ""
sys.stdout.write((d.get("cwd") or "") + "\n" + (cmd or ""))
' 2>/dev/null)" || EXTRACT=""
CWD="$(printf '%s' "$EXTRACT" | head -n1)"
CMD="$(printf '%s' "$EXTRACT" | tail -n +2)"
# Fire only on a real `git commit`: git, optional global options (-C dir,
# -c k=v), then the commit subcommand. `git grep commit` must not fire.
printf '%s' "$CMD" | grep -qE '\bgit\s+(-\S+\s+(\S+\s+)?)*commit\b' || exit 0
# Root = cwd field, fallback git toplevel, else pass.
if [ -n "$CWD" ] && [ -d "$CWD" ]; then
    ROOT="$CWD"
else
    ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
fi
[ -n "$ROOT" ] || exit 0
cd "$ROOT" 2>/dev/null || exit 0
# Outside a git repo -> nothing to gate.
git rev-parse --show-toplevel >/dev/null 2>&1 || exit 0

SENTINEL="$ROOT/.validation_passed"
FIX="Run .claude/hooks/run-validate-waves.sh, then commit."

# Detect OS once - reused in the staleness checks below.
if [ "$(uname)" = "Linux" ]; then IS_LINUX=1; else IS_LINUX=0; fi

gate_fail() {
    echo "" >&2
    echo "BLOCKED: $1" >&2
    echo "  $2" >&2
    echo "  $FIX" >&2
    echo "" >&2
    exit 2
}

# 3. Sentinel must exist.
if [ ! -f "$SENTINEL" ]; then
    HINT="Post-session validation has not been run; no .validation_passed sentinel."
    if printf '%s' "$CMD" | grep -qF -e '.validation_passed' -e 'run-validate-waves'; then
        HINT="Bundled sentinel-write + commit detected. This gate runs BEFORE the command, so that can never pass. Run the writer in its OWN Bash call, then commit in the NEXT."
    fi
    gate_fail "Validation sentinel missing." "$HINT"
fi

# 4. Sentinel must be under 30 minutes old.
if [ "$IS_LINUX" = "1" ]; then
    SENTINEL_MTIME=$(stat -c %Y "$SENTINEL" 2>/dev/null || echo 0)
else
    SENTINEL_MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null || echo 0)
fi
NOW=$(date +%s)
AGE=$(( NOW - SENTINEL_MTIME ))
MAX_AGE=1800  # 30 minutes
if [ "$AGE" -gt "$MAX_AGE" ]; then
    gate_fail "Validation sentinel is stale (age ${AGE}s, limit ${MAX_AGE}s)." "Files may have changed since validation."
fi

# 4b. Both waves must be recorded (fail-closed): a sentinel without a numeric
# waves_passed>=2 is treated as insufficient.
WAVES=$(grep '^waves_passed=' "$SENTINEL" 2>/dev/null | head -1 | cut -d= -f2 | tr -d ' ' || true)
if printf '%s' "$WAVES" | grep -qE '^[0-9]+$' && [ "$WAVES" -ge 2 ]; then
    :  # both waves recorded - OK
else
    gate_fail "Validation sentinel records insufficient waves_passed (need >=2, got '${WAVES:-<missing>}')." "A partial validation cannot clear the gate."
fi

# 5. No changed or untracked file may be newer than the sentinel. Include
# untracked-unignored files so a brand-new file edited after validation still
# re-triggers the gate.
NEWEST_MTIME=$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null | while read -r f; do
    FULL="$ROOT/$f"
    if [ -f "$FULL" ]; then
        if [ "$IS_LINUX" = "1" ]; then
            stat -c %Y "$FULL" 2>/dev/null
        else
            stat -f %m "$FULL" 2>/dev/null
        fi
    fi
done | sort -rn | head -1)
if [ -n "$NEWEST_MTIME" ] && [ "$NEWEST_MTIME" -gt "$SENTINEL_MTIME" ]; then
    gate_fail "Files changed after validation passed." "The sentinel no longer covers the working tree."
fi

# 6. All checks passed - allow the commit.
echo "pre-commit-gate: validation sentinel OK (age ${AGE}s, max ${MAX_AGE}s). Commit allowed." >&2
exit 0
