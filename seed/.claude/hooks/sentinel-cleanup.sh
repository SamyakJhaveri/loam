#!/usr/bin/env bash
# sentinel-cleanup.sh - PostToolUse hook on Edit|Write.
#
# Deletes the .validation_passed sentinel whenever a real repo file is edited
# after validation, forcing re-validation before the next commit. The write is
# a real edit only when the target is a tracked or untracked file inside the
# repo; an edit invisible to the commit gate is skipped:
#   (a) a path outside the repo, or
#   (b) a still-gitignored in-repo path (scratch or build artifact).
# On any parse uncertainty the sentinel is deleted (fail-safe: an unrecognized
# edit forces re-validation). .codex_review_done is swept the same way.
#
# The repo root comes from the envelope's cwd field, not CLAUDE_PROJECT_DIR
# (which stays at the launch root; the active worktree path is cwd).
#
# Exit: always 0 (advisory; never blocks).

set -uo pipefail

INPUT="$(cat)"

# Repo root = cwd field when it is a directory, else the git toplevel here.
CWD="$(printf '%s' "$INPUT" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    assert isinstance(d, dict)
except Exception:
    sys.exit(0)
sys.stdout.write(d.get("cwd") or "")
' 2>/dev/null)" || CWD=""
if [ -n "$CWD" ] && [ -d "$CWD" ]; then
    ROOT="$CWD"
else
    ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
fi
[ -n "$ROOT" ] || exit 0

# Keep the sentinel when the edit is invisible to the commit gate: a path
# outside the repo, or a still-gitignored in-repo path. Any parse failure falls
# through to deletion (fail-safe).
if ROOT="$ROOT" python3 -c '
import json, os, subprocess, sys
root = os.path.realpath(os.environ["ROOT"])
try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(1)
if not isinstance(data, dict):
    sys.exit(1)
tool_input = data.get("tool_input")
if not isinstance(tool_input, dict):
    sys.exit(1)
fp = tool_input.get("file_path", "")
if not isinstance(fp, str) or not fp:
    sys.exit(1)
target = fp if os.path.isabs(fp) else os.path.join(root, fp)
target = os.path.realpath(target)
if not target.startswith(root + os.sep):
    sys.exit(0)  # outside the repo -> invisible to the gate -> keep sentinel
rc = subprocess.run(
    ["git", "-C", root, "check-ignore", "-q", "--", target],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
).returncode
sys.exit(0 if rc == 0 else 1)  # gitignored -> keep; anything else -> delete
' <<<"$INPUT"; then
    exit 0
fi

SENTINEL="$ROOT/.validation_passed"
if [ -f "$SENTINEL" ]; then
    rm -f "$SENTINEL"
    echo "sentinel-cleanup: .validation_passed deleted (file edited after validation)" >&2
fi

CODEX_SENTINEL="$ROOT/.codex_review_done"
if [ -f "$CODEX_SENTINEL" ]; then
    rm -f "$CODEX_SENTINEL"
    echo "sentinel-cleanup: .codex_review_done deleted (file edited after Codex review)" >&2
fi

exit 0
