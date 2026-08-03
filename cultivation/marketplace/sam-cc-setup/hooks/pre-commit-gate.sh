#!/usr/bin/env bash
# pre-commit-gate.sh
#
# PreToolUse hook — blocks `git commit` unless post-session validation has passed.
#
# Mechanism:
#   - Reads hook event JSON from stdin (Claude Code hook protocol)
#   - Extracts the bash command being run
#   - Only acts on commands containing "git commit"
#   - Checks for .validation_passed sentinel file in project root
#   - Sentinel must exist, be < 30 min old, and not be stale (files unchanged since)
#
# Exit codes (Claude Code hook protocol):
#   0 = allow the command
#   2 = BLOCK the command (stderr shown to Claude as error)
#
# Origin: post-session validation loop (battle-tested in a research repo, 2026)
# Pattern from: Trail of Bits claude-code-config, disler/claude-code-hooks-mastery

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
SENTINEL="$PROJECT_ROOT/.validation_passed"

# Detect OS once — reused in steps 4 and 5
if [ "$(uname)" = "Linux" ]; then
    IS_LINUX=1
else
    IS_LINUX=0
fi

# ── 1. Read and parse the hook event JSON ────────────────────────────────────
INPUT=$(cat)

COMMAND=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    # Claude Code sends tool_input as the top-level or nested object
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")

# ── 2. Only gate on git commit commands ──────────────────────────────────────
# Rewritten 2026-08-02 (second pass). History of this check:
#
#   v1  '^\s*git\s+commit'  — start-anchored, so it FAILED OPEN on every
#       compound or qualified form the Bash tool routinely emits:
#       `cd X && git commit`, `git -c user.email=a commit`, `/usr/bin/git commit`.
#   v2  a command-position regex — closed those bypasses but FAILED CLOSED too
#       often: a regex cannot see shell quoting, so `echo "a; git commit"` and
#       any heredoc or -c script whose *text* contained the phrase got gated.
#       Caught by diff-reviewer, which tripped it on its own test commands.
#   v3  (this) tokenize with shlex, which respects quoting, then look for `git`
#       in command position with `commit` as its subcommand.
#
# Fails CLOSED on anything it cannot parse (unbalanced quotes) or cannot see
# through (command substitution), because a spurious block costs one rephrase
# while a miss costs an unvalidated commit.
#   v4  (current) detection moved to gate_detect.py — three independent
#       detectors, any one gates. See that file's docstring for the full
#       history and for why each detector exists.
#
# The detector lives in its own file so that no shell escaping sits between the
# command text and the tokenizer, and so it can be tested directly. The command
# reaches it only on stdin; it is never interpolated into a shell string.
DETECT="$(dirname "${BASH_SOURCE[0]}")/gate_detect.py"
GATE=$(python3 "$DETECT" <<< "$COMMAND" 2>/dev/null || echo "GATE")

if [ "$GATE" != "GATE" ]; then
    exit 0
fi

# ── 3. Check sentinel exists ─────────────────────────────────────────────────
if [ ! -f "$SENTINEL" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Post-session validation has not been run.         ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Run /validate before committing.                           ║" >&2
    echo "║  This gate enforces the validation loop protocol.           ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Quick check (Wave 1 only, ~30s): /validate quick           ║" >&2
    echo "║  Full check (all waves, ~3min):   /validate                 ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 4. Check sentinel is not stale (< 30 minutes old) ────────────────────────
if [ "$IS_LINUX" = "1" ]; then
    SENTINEL_MTIME=$(stat -c %Y "$SENTINEL" 2>/dev/null || echo "0")
else
    # macOS
    SENTINEL_MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null || echo "0")
fi

NOW=$(date +%s)
AGE=$(( NOW - SENTINEL_MTIME ))
MAX_AGE=1800  # 30 minutes

if [ "$AGE" -gt "$MAX_AGE" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Validation sentinel is stale.                     ║" >&2
    echo "║  Age: ${AGE}s  Limit: ${MAX_AGE}s                                   ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Re-run /validate — files may have changed since last run.  ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 4b. Check that both validation waves were run (not just quick) ──────────
# The plugin's /validate is two-wave (deterministic + rule-based); both required.
# Fail-open: if waves_passed field is missing, skip this check (backward compat).
WAVES=$(grep '^waves_passed=' "$SENTINEL" 2>/dev/null | cut -d= -f2 | tr -d ' ')
if [ -n "$WAVES" ] && [ "$WAVES" -lt 2 ] 2>/dev/null; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Only ${WAVES}/2 required validation waves passed.       ║" >&2
    echo "║                                                              ║" >&2
    echo "║  /validate quick is not sufficient for committing.          ║" >&2
    echo "║  Run full /validate (both waves).                            ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 5. Check sentinel is not outdated by new file changes ─────────────────────
# Find the most recently modified tracked file in the diff.
# `|| true`: in a repo with no commits yet, HEAD is unresolvable and git exits 128;
# under `set -euo pipefail` that killed the hook with a non-verdict exit code.
NEWEST_CHANGE=$({ git -C "$PROJECT_ROOT" diff --name-only HEAD 2>/dev/null || true; } | while read f; do
    FULL="$PROJECT_ROOT/$f"
    if [ -f "$FULL" ]; then
        if [ "$IS_LINUX" = "1" ]; then
            stat -c %Y "$FULL" 2>/dev/null
        else
            stat -f %m "$FULL" 2>/dev/null
        fi
    fi
done | sort -rn | head -1)

if [ -n "$NEWEST_CHANGE" ] && [ "$NEWEST_CHANGE" -gt "$SENTINEL_MTIME" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Files changed after validation passed.            ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Re-run /validate to cover the latest changes.              ║" >&2
    echo "║  Quick re-check: /validate fix                              ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 6. All checks passed — allow the commit ───────────────────────────────────
echo "✓ Validation sentinel OK (age: ${AGE}s, max: ${MAX_AGE}s). Commit allowed." >&2
exit 0
