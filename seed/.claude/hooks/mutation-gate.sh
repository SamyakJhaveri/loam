#!/usr/bin/env bash
# mutation-gate.sh - PreToolUse on Bash: diff-scoped mutation gate for commits.
#
# Purpose: before a git commit lands, run cosmic-ray mutation testing scoped to
# the lines this commit changes (git-filter branch = HEAD) over the staged
# non-test Python files, and block the commit when any mutant on a changed line
# survives the test suite. Line coverage does not predict test effectiveness for
# LLM-written suites (r near zero within a model, arXiv 2607.22880), so this gate
# scores surviving mutants on the lines the commit changed, not coverage.
#
# The gate never touches the project checkout. cosmic-ray mutates a module in
# place and restores it after each mutant, so a kill (the 600s timeout, or the
# user stopping mid-mutant) would leave a mutated source file behind, and a
# concurrent editor would meanwhile read mutated code. The whole run therefore
# happens in a throwaway linked worktree holding the staged tree, removed on
# exit; the project checkout is only ever read.
# A run killed with SIGTERM still runs that trap. A SIGKILLed run does not: it
# leaves its scratch directory and worktree entry behind. The next run sweeps
# entries named mutation-gate.* that are older than 30 minutes, so the leak
# heals itself; a fresh entry is left alone because it may belong to a live run
# in another session.
#
# The whole gate is OPT-IN by tool presence: with no cosmic-ray reachable (a
# project .venv/bin or PATH), it silently no-ops. No cosmic-ray, no gate.
# [tool.mutation-gate] test-command is split with shlex by cosmic-ray, not a
# shell: one command and its arguments, no `&&`, pipes, or redirects.
# Escape hatch: put a "Mutants:" line in the commit message to justify survivors.
#
# Triggered by: PreToolUse on Bash (settings wires timeout 600).
#
# Exit codes (Claude Code hook protocol):
#   0 = allow (not a commit, escape hatch, a guard tripped, a tool step failed,
#       or zero surviving mutants on changed lines)
#   2 = block; stderr lists the surviving mutants on the changed lines

set -uo pipefail

PAYLOAD="$(cat)"

# --- Parse the command and cwd from the JSON envelope on stdin ---------------
CMD="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json
try:
    d = json.load(sys.stdin); ti = d.get("tool_input", {}) or {}
    print(ti.get("command", ""))
except Exception:
    pass' 2>/dev/null || true)"

CWD="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json
try:
    print(json.load(sys.stdin).get("cwd", "") or "")
except Exception:
    pass' 2>/dev/null || true)"

# --- Fire only on a real `git commit`; else pass at once --------------------
# git, optional global options (-C dir, -c k=v), then the commit subcommand.
# `git grep commit` and `git log --grep=commit` must not start a mutation run.
echo "$CMD" | grep -qE '\bgit\s+(-\S+\s+(\S+\s+)?)*commit\b' || exit 0
# Escape hatch: the justification lives in the commit message.
printf '%s' "$CMD" | grep -q 'Mutants:' && exit 0

# --- Resolve the project root: cwd field, then git toplevel ------------------
ROOT="$CWD"
if [ -z "$ROOT" ] || [ ! -d "$ROOT" ]; then
    ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
[ -n "$ROOT" ] && [ -d "$ROOT" ] || exit 0
cd "$ROOT" 2>/dev/null || exit 0

# Escape hatch, message-file form: `git commit -F <path>` / `--file <path>`
# cannot carry the marker in the command string, so read it from the file
# (resolved relative to ROOT, which is now the cwd).
MSGFILE="$(printf '%s\n' "$CMD" | grep -oE -- '(^| )(-F ?|--file[ =])[^ ]+' | head -n1 | sed -E 's/^ ?(-F ?|--file[ =])//')"
if [ -n "$MSGFILE" ] && [ -f "$MSGFILE" ] && grep -q 'Mutants:' "$MSGFILE" 2>/dev/null; then
    exit 0
fi

# --- Guards: each a silent exit 0 with a one-line NOTE on stderr -------------
if [ ! -f pyproject.toml ]; then
    echo "NOTE: mutation gate skipped: no pyproject.toml in $ROOT" >&2
    exit 0
fi

# cosmic-ray is opt-in by presence: project .venv first, then PATH. The sibling
# tools (cr-filter-git) live next to whichever cosmic-ray we find.
if [ -x "$ROOT/.venv/bin/cosmic-ray" ]; then
    CR="$ROOT/.venv/bin/cosmic-ray"
    CRBIN="$ROOT/.venv/bin"
elif command -v cosmic-ray >/dev/null 2>&1; then
    CR="$(command -v cosmic-ray)"
    CRBIN="$(dirname "$CR")"
else
    echo "NOTE: mutation gate skipped: cosmic-ray not installed (no .venv/bin or PATH)" >&2
    exit 0
fi
CRFILTER="$CRBIN/cr-filter-git"

# --- Work area (removed on exit) ---------------------------------------------
WORK="$(mktemp -d "${TMPDIR:-/tmp}/mutation-gate.XXXXXX")" || exit 0
trap 'rm -rf "$WORK"' EXIT

# --- Staging the command will do before it commits ---------------------------
# Same rule as test-tamper-scan.sh: this hook runs before `git add ... &&
# git commit` or `commit -a` stages anything, so replay that staging into a
# copy of the index (`add -A` for an explicit add, `add -u` for -a/--all) and
# read the copy. A plain commit reads the real index.
TMPI=""
STAGE=""
if printf '%s' "$CMD" | grep -qE '\bgit\s+add\b'; then
    STAGE="-A"
elif printf '%s' "$CMD" | grep -qE '\bcommit\b[^&|;]*\s(--all|-[a-zA-Z]*a[a-zA-Z]*)\b'; then
    STAGE="-u"
fi
if [ -n "$STAGE" ]; then
    TMPI="$WORK/index"
    IDX="$(git rev-parse --git-path index)"
    # No index file yet (nothing ever staged): the copy starts empty.
    if [ -f "$IDX" ]; then
        cp -- "$IDX" "$TMPI" 2>/dev/null || exit 0
    fi
    GIT_INDEX_FILE="$TMPI" git add "$STAGE" >/dev/null 2>&1
fi
# git against the index the commit will use (the copy when one was made).
staged_git() {
    if [ -n "$TMPI" ]; then GIT_INDEX_FILE="$TMPI" git "$@"; else git "$@"; fi
}

# Staged, non-test Python files (Added or Modified). Drop test files: a
# test_*.py / *_test.py / conftest.py basename, or any tests/ or test/ segment.
STAGED="$(staged_git diff --cached --name-only --diff-filter=AM -- '*.py' 2>/dev/null || true)"
NONTEST="$(printf '%s\n' "$STAGED" \
    | grep -E '\.py$' \
    | grep -vE '(^|/)(test_[^/]*\.py|[^/]*_test\.py|conftest\.py)$' \
    | grep -vE '(^|/)tests?/' || true)"
if [ -z "$NONTEST" ]; then
    echo "NOTE: mutation gate skipped: no staged non-test .py files" >&2
    exit 0
fi

# --- Test command and per-mutant timeout from [tool.mutation-gate] -----------
CONF="$(python3 - <<'PY' 2>/dev/null || true
import tomllib
try:
    with open("pyproject.toml", "rb") as f:
        t = tomllib.load(f).get("tool", {}).get("mutation-gate", {})
except Exception:
    t = {}
print(t.get("test-command", "python3 -m pytest -q -x"))
print(t.get("timeout", 60))
PY
)"
TEST_CMD="$(printf '%s\n' "$CONF" | sed -n '1p')"
GATE_TIMEOUT="$(printf '%s\n' "$CONF" | sed -n '2p')"
[ -n "$TEST_CMD" ] || TEST_CMD="python3 -m pytest -q -x"
[ -n "$GATE_TIMEOUT" ] || GATE_TIMEOUT=60

# --- The survivor parser -----------------------------------------------------
PARSE="$WORK/parse.py"
cat > "$PARSE" <<'PY'
import sys, json
# cosmic-ray dump prints one JSON line per job: a two-element list
# [work_item, result]. result is null when not run; otherwise it carries
# worker_outcome ("normal"/"skipped"/...) and test_outcome ("survived"/...).
# A survivor: worker_outcome == "normal" and test_outcome == "survived".
for raw in open(sys.argv[1], encoding="utf-8", errors="ignore"):
    raw = raw.strip()
    if not raw:
        continue
    try:
        rec = json.loads(raw)
    except Exception:
        continue
    if not isinstance(rec, list) or len(rec) != 2:
        continue
    work_item, result = rec
    if not result:
        continue
    if result.get("worker_outcome") != "normal":
        continue
    if result.get("test_outcome") != "survived":
        continue
    for m in (work_item.get("mutations") or []):
        mp = m.get("module_path", "?")
        pos = m.get("start_pos")
        line = pos[0] if isinstance(pos, list) and pos else "?"
        op = m.get("operator_name", "?")
        occ = m.get("occurrence", "?")
        print(f"{mp}:{line} {op} #{occ}")
PY

# TOML basic-string escaping for values we interpolate into the config.
toml_esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
ESC_CMD="$(toml_esc "$TEST_CMD")"

# --- Scratch worktree: cosmic-ray mutates in place, never in the checkout ----
# A detached worktree at HEAD, overlaid with the staged index, so `git diff
# HEAD` inside it shows exactly the staged lines and cr-filter-git's
# branch = "HEAD" still scopes the mutants to this commit's changes.
TREE="$WORK/tree"
# Sweep stale scratch worktrees left by a SIGKILLed run (see header): entries
# named mutation-gate.*/tree whose directory is gone or older than 30 minutes.
# `git worktree prune` alone cannot drop an entry while its directory survives.
# A fresh entry may belong to a live run in another session, so it is left alone.
dir_mtime() {
    if [ "$(uname)" = "Linux" ]; then
        stat -c %Y "$1" 2>/dev/null || echo 0
    else
        stat -f %m "$1" 2>/dev/null || echo 0
    fi
}
sweep_stale_worktrees() {
    local now p parent
    now="$(date +%s)"
    git worktree list --porcelain 2>/dev/null | while IFS= read -r line; do
        case "$line" in
            "worktree "*) p="${line#worktree }" ;;
            *) continue ;;
        esac
        [ "$(basename "$p")" = "tree" ] || continue
        parent="$(dirname "$p")"
        case "$(basename "$parent")" in
            mutation-gate.*) ;;
            *) continue ;;
        esac
        if [ ! -d "$p" ] || [ "$(( now - $(dir_mtime "$p") ))" -ge 1800 ]; then
            git worktree remove --force "$p" >/dev/null 2>&1 || true
            rm -rf "$parent"
        fi
    done
    git worktree prune >/dev/null 2>&1 || true
}
sweep_stale_worktrees
if ! git worktree add --detach --quiet "$TREE" HEAD 2>/dev/null; then
    echo "NOTE: mutation gate skipped: could not create a scratch worktree" >&2
    exit 0
fi
trap 'cd "$ROOT" 2>/dev/null && { git worktree remove --force "$TREE" >/dev/null 2>&1; git worktree prune >/dev/null 2>&1; }; rm -rf "$WORK"' EXIT
if ! staged_git checkout-index -a -f --prefix="$TREE/" 2>/dev/null; then
    echo "NOTE: mutation gate skipped: could not stage the scratch worktree" >&2
    exit 0
fi
# checkout-index writes files but not the scratch index, so a newly added
# module would be untracked there and `git diff HEAD` (what cr-filter-git
# reads) would skip every mutant in it. Index the overlay.
if ! git -C "$TREE" add -A 2>/dev/null; then
    echo "NOTE: mutation gate skipped: could not index the scratch worktree" >&2
    exit 0
fi
# The worktree has no .venv of its own, so the project's interpreter has to
# come along for the test command to resolve.
if [ -d "$ROOT/.venv/bin" ]; then
    export PATH="$ROOT/.venv/bin:$PATH"
fi
cd "$TREE" || exit 0

SURVIVORS=""
FAILED_STEP=""
FAILED_LOG=""
BASELINE_DONE=""

while IFS= read -r f; do
    [ -z "$f" ] && continue
    d="$WORK/$(printf '%s' "$f" | tr '/' '_')"
    mkdir -p "$d"
    cfg="$d/config.toml"
    sess="$d/session.sqlite"
    log="$d/run.log"
    esc_f="$(toml_esc "$f")"
    {
        echo '[cosmic-ray]'
        printf 'module-path = "%s"\n' "$esc_f"
        printf 'timeout = %s\n' "$GATE_TIMEOUT"
        echo 'excluded-modules = []'
        printf 'test-command = "%s"\n' "$ESC_CMD"
        echo ''
        echo '[cosmic-ray.distributor]'
        echo 'name = "local"'
        echo ''
        echo '[cosmic-ray.filters.git-filter]'
        echo 'branch = "HEAD"'
    } > "$cfg"

    # Each tool step logs to $log; any non-zero exit means a broken tool, which
    # must never block a commit - NOTE and pass.
    # One-time baseline: the test command must pass on unmutated code, else
    # every mutant is "killed" and the gate passes blind (a failing suite, or
    # a test-command with shell operators, which shlex does not run).
    if [ -z "$BASELINE_DONE" ]; then
        if ! "$CR" baseline "$cfg" >>"$log" 2>&1; then
            FAILED_STEP="cosmic-ray baseline (test command does not pass on unmutated code)"; FAILED_LOG="$log"; break
        fi
        BASELINE_DONE=1
    fi
    if ! "$CR" init "$cfg" "$sess" >>"$log" 2>&1; then
        FAILED_STEP="cosmic-ray init"; FAILED_LOG="$log"; break
    fi
    if ! "$CRFILTER" "$sess" --config "$cfg" >>"$log" 2>&1; then
        FAILED_STEP="cr-filter-git"; FAILED_LOG="$log"; break
    fi
    if ! "$CR" exec "$cfg" "$sess" >>"$log" 2>&1; then
        FAILED_STEP="cosmic-ray exec"; FAILED_LOG="$log"; break
    fi
    if ! "$CR" dump "$sess" >"$d/dump.json" 2>>"$log"; then
        FAILED_STEP="cosmic-ray dump"; FAILED_LOG="$log"; break
    fi
    out="$(python3 "$PARSE" "$d/dump.json" 2>/dev/null || true)"
    [ -n "$out" ] && SURVIVORS="${SURVIVORS}${out}
"
done <<< "$NONTEST"

if [ -n "$FAILED_STEP" ]; then
    echo "NOTE: mutation gate skipped: $FAILED_STEP failed; see:" >&2
    tail -5 "$FAILED_LOG" 2>/dev/null | sed 's/^/  /' >&2
    exit 0
fi

# --- Verdict ----------------------------------------------------------------
N="$(printf '%s' "$SURVIVORS" | grep -c . || true)"
if [ "${N:-0}" -gt 0 ]; then
    {
        echo "Mutation gate: $N surviving mutant(s) on lines this commit changes:"
        printf '%s\n' "$SURVIVORS" | grep . | head -20 | sed 's/^/  /'
        if [ "$N" -gt 20 ]; then
            echo "  ... and $((N - 20)) more"
        fi
        echo "Add a test that kills each, or justify under a 'Mutants:' line in the commit message."
    } >&2
    exit 2
fi

exit 0
