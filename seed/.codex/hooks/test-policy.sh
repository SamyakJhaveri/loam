#!/usr/bin/env bash
# Deterministic smoke tests for Codex hook policies.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOK="$ROOT/.codex/hooks/pre-tool-policy.py"
POST_HOOK="$ROOT/.codex/hooks/post-tool-policy.py"
ROOT_BASENAME="$(basename "$ROOT")"
PARENT_RESULTS="../$ROOT_BASENAME/results/example.json"
PARENT_ENV="../$ROOT_BASENAME/.env.local"
unset CODEX_HOOK_AUDIT

TMPDIR="${TMPDIR:-/tmp}"
TEST_SENTINEL="$(mktemp "$TMPDIR/codex-validation-sentinel.XXXXXX")"
TEST_REVIEW_SENTINEL="$(mktemp "$TMPDIR/codex-review-sentinel.XXXXXX")"
rm -f "$TEST_SENTINEL"
rm -f "$TEST_REVIEW_SENTINEL"
export CODEX_VALIDATION_SENTINEL="$TEST_SENTINEL"
export CODEX_REVIEW_SENTINEL="$TEST_REVIEW_SENTINEL"
FIXTURE_ROOTS=()

cleanup() {
    local fixture
    rm -f /tmp/codex-hook-test.out /tmp/codex-hook-test.err "$TEST_SENTINEL" "$TEST_REVIEW_SENTINEL" "${AUDIT_LOG:-}"
    for fixture in "${FIXTURE_ROOTS[@]}"; do
        rm -rf "$fixture"
    done
}
trap cleanup EXIT

run_hook_in_dir() {
    local cwd="$1"
    local payload="$2"
    (
        cd "$cwd"
        printf '%s' "$payload" | python3 "$HOOK"
    ) >/tmp/codex-hook-test.out 2>/tmp/codex-hook-test.err
}

run_post_hook() {
    local payload="$1"
    printf '%s' "$payload" | python3 "$POST_HOOK" >/tmp/codex-hook-test.out 2>/tmp/codex-hook-test.err
}

expect_block_in_dir() {
    local cwd="$1"
    local name="$2"
    local payload="$3"
    local expected="${4:-}"
    set +e
    run_hook_in_dir "$cwd" "$payload"
    local status=$?
    set -e
    if [ "$status" -ne 2 ]; then
        echo "FAIL: $name expected block (2), got $status" >&2
        cat /tmp/codex-hook-test.err >&2
        exit 1
    fi
    if [ -n "$expected" ] && ! grep -F "$expected" /tmp/codex-hook-test.err >/dev/null; then
        echo "FAIL: $name did not print expected message: $expected" >&2
        cat /tmp/codex-hook-test.err >&2
        exit 1
    fi
    echo "PASS: $name blocked"
}

expect_block() {
    expect_block_in_dir "$ROOT" "$1" "$2" "${3:-}"
}

expect_allow_in_dir() {
    local cwd="$1"
    local name="$2"
    local payload="$3"
    set +e
    run_hook_in_dir "$cwd" "$payload"
    local status=$?
    set -e
    if [ "$status" -ne 0 ]; then
        echo "FAIL: $name expected allow (0), got $status" >&2
        cat /tmp/codex-hook-test.err >&2
        exit 1
    fi
    echo "PASS: $name allowed"
}

expect_allow() {
    expect_allow_in_dir "$ROOT" "$1" "$2"
}

expect_post_allow() {
    local name="$1"
    local payload="$2"
    set +e
    run_post_hook "$payload"
    local status=$?
    set -e
    if [ "$status" -ne 0 ]; then
        echo "FAIL: $name expected post-hook allow (0), got $status" >&2
        cat /tmp/codex-hook-test.err >&2
        exit 1
    fi
    echo "PASS: $name"
}

write_sentinel() {
    printf '%s\n' "$1" >"$TEST_SENTINEL"
}

write_review_sentinel() {
    printf '%s\n' "$1" >"$TEST_REVIEW_SENTINEL"
}

git_index_lock_path() {
    git -C "$1" rev-parse --absolute-git-dir 2>/dev/null | sed 's#$#/index.lock#'
}

make_git_fixture() {
    local fixture
    fixture="$(mktemp -d "$TMPDIR/codex-hook-git.XXXXXX")"
    FIXTURE_ROOTS+=("$fixture")
    git -C "$fixture" init -q
    git -C "$fixture" config user.email codex@example.invalid
    git -C "$fixture" config user.name "Codex Hook Test"
    mkdir -p "$fixture/results"
    printf '{"ok": true}\n' >"$fixture/results/example.json"
    printf 'baseline\n' >"$fixture/notes.txt"
    git -C "$fixture" add results/example.json notes.txt
    git -C "$fixture" commit -q -m initial
    GIT_FIXTURE="$fixture"
}

expect_block \
    "apply_patch result update" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Update File: results/example.json\n@@\n+{}\n*** End Patch\n"}}'

expect_block \
    "apply_patch superpowers docs add" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Add File: docs/superpowers/plans/example.md\n+plan\n*** End Patch\n"}}'

expect_block \
    "bash git commit without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

expect_block \
    "bash git dash-C commit without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git -C . commit -m test"}}'

expect_block \
    "bash shell-wrapped git commit without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"bash -lc '\''git commit -m test'\''"}}'

expect_block \
    "bash git merge without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge topic-branch"}}'

expect_block \
    "bash git merge commit override without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --no-commit --commit topic-branch"}}'

expect_block \
    "bash git merge no-ff override without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --ff-only --no-ff topic-branch"}}'

expect_block \
    "bash git merge no-squash override without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --squash --no-squash topic-branch"}}'

expect_block \
    "bash git cherry-pick continue without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git cherry-pick --continue"}}'

expect_block \
    "bash git revert continue without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git revert --continue"}}'

expect_allow \
    "bash git merge no-commit without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --no-commit topic-branch"}}'

expect_allow \
    "bash git merge squash without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --squash topic-branch"}}'

expect_allow \
    "bash git merge ff-only without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --ff-only topic-branch"}}'

expect_allow \
    "bash git merge ff-only final without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --no-ff --ff-only topic-branch"}}'

expect_allow \
    "bash git merge squash final without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --no-squash --squash topic-branch"}}'

expect_allow \
    "bash git merge abort without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge --abort"}}'

expect_allow \
    "bash git cherry-pick no-commit without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git cherry-pick --no-commit abc1234"}}'

expect_allow \
    "bash git revert abort without validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git revert --abort"}}'

write_sentinel "validation_ok=1"
expect_block \
    "bash git commit missing waves_passed" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

write_sentinel "waves_passed=bad"
expect_block \
    "bash git commit malformed waves_passed" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

write_sentinel "waves_passed=1"
expect_block \
    "bash git commit incomplete waves_passed" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

write_sentinel "waves_passed=2"
expect_allow \
    "bash git commit with valid validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

expect_allow \
    "bash git merge with valid validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge topic-branch"}}'

expect_allow \
    "bash git cherry-pick continue with valid validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git cherry-pick --continue"}}'

expect_allow \
    "bash git revert continue with valid validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git revert --continue"}}'

make_git_fixture
touch "$(git_index_lock_path "$GIT_FIXTURE")"
expect_block_in_dir \
    "$GIT_FIXTURE" \
    "fresh index lock blocks git add" \
    '{"tool_name":"Bash","tool_input":{"command":"git add notes.txt"}}' \
    "another writer holds this checkout's git index"

expect_allow_in_dir \
    "$GIT_FIXTURE" \
    "fresh index lock allows git status" \
    '{"tool_name":"Bash","tool_input":{"command":"git status --short"}}'

expect_block_in_dir \
    "$GIT_FIXTURE" \
    "fresh index lock blocks file write" \
    '{"tool_name":"Write","tool_input":{"file_path":"notes.txt","content":"changed"}}' \
    "another writer holds this checkout's git index"

touch -t 200001010000 "$(git_index_lock_path "$GIT_FIXTURE")"
expect_allow_in_dir \
    "$GIT_FIXTURE" \
    "stale index lock allows git add" \
    '{"tool_name":"Bash","tool_input":{"command":"git add notes.txt"}}'

make_git_fixture
printf '{"ok": false}\n' >"$GIT_FIXTURE/results/example.json"
expect_block_in_dir \
    "$GIT_FIXTURE" \
    "bash git commit blocks tracked result json diff" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}' \
    "Existing result JSON files changed."

make_git_fixture
mkdir -p "$GIT_FIXTURE/subdir"
printf '{"ok": false}\n' >"$GIT_FIXTURE/results/example.json"
expect_block_in_dir \
    "$GIT_FIXTURE/subdir" \
    "bash git commit blocks tracked result json diff from subdir" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}' \
    "Existing result JSON files changed."

make_git_fixture
write_sentinel "waves_passed=2"
sleep 1
printf 'changed after validation\n' >"$GIT_FIXTURE/notes.txt"
expect_block_in_dir \
    "$GIT_FIXTURE" \
    "bash git commit blocks files changed after validation" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}' \
    "Files changed after validation passed."

# A commit message that merely mentions an env file must not trip the .env guard.
expect_allow \
    "bash git commit message mentions env file" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"update .env handling\""}}'

write_sentinel "waves_passed=2"
touch -t 200001010000 "$TEST_SENTINEL"
expect_block \
    "bash git commit stale sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}'

expect_block \
    "bash git merge stale sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"git merge topic-branch"}}'

expect_block \
    "bash rm dot-slash results" \
    '{"tool_name":"Bash","tool_input":{"command":"rm ./results/example.json"}}'

expect_block \
    "bash rm parent path results" \
    "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"rm $PARENT_RESULTS\"}}"

expect_block_in_dir \
    "$ROOT/.codex" \
    "bash subdir parent rm results" \
    '{"tool_name":"Bash","tool_input":{"command":"rm ../results/example.json"}}'

expect_block \
    "bash tee results" \
    '{"tool_name":"Bash","tool_input":{"command":"tee results/example.json"}}'

expect_block \
    "bash touch results" \
    '{"tool_name":"Bash","tool_input":{"command":"touch results/example.json"}}'

expect_block \
    "bash cp results" \
    '{"tool_name":"Bash","tool_input":{"command":"cp x results/example.json"}}'

expect_block \
    "bash mv results" \
    '{"tool_name":"Bash","tool_input":{"command":"mv x results/example.json"}}'

expect_block \
    "bash sed in-place results" \
    '{"tool_name":"Bash","tool_input":{"command":"sed -i s/a/b/ results/example.json"}}'

expect_block \
    "bash find delete results" \
    '{"tool_name":"Bash","tool_input":{"command":"find results/ -delete"}}'

expect_block \
    "bash python writes results" \
    '{"tool_name":"Bash","tool_input":{"command":"python -c \"open(\\\"results/example.json\\\",\\\"w\\\").write(\\\"x\\\")\""}}'

expect_block \
    "bash touch validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"touch .validation_passed"}}'

expect_block \
    "bash tee validation sentinel" \
    '{"tool_name":"Bash","tool_input":{"command":"tee .validation_passed"}}'

write_sentinel "waves_passed=2"
write_review_sentinel "review_ok=1"
expect_post_allow \
    "post-tool cleanup deletes sentinels after ordinary file edit" \
    '{"tool_name":"Write","tool_input":{"file_path":"notes.txt","content":"changed"}}'
if [ -e "$TEST_SENTINEL" ] || [ -e "$TEST_REVIEW_SENTINEL" ]; then
    echo "FAIL: post-tool cleanup left stale sentinels after ordinary file edit" >&2
    exit 1
fi

write_sentinel "waves_passed=2"
write_review_sentinel "review_ok=1"
expect_post_allow \
    "post-tool cleanup preserves deliberate sentinel-only write" \
    "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$TEST_SENTINEL\",\"content\":\"waves_passed=2\\n\"}}"
if [ ! -e "$TEST_SENTINEL" ] || [ ! -e "$TEST_REVIEW_SENTINEL" ]; then
    echo "FAIL: post-tool cleanup deleted sentinels after sentinel-only write" >&2
    exit 1
fi

expect_block \
    "file tool blocks env file" \
    '{"tool_name":"Read","tool_input":{"path":".env"}}'

expect_block \
    "file tool blocks envrc file" \
    '{"tool_name":"Read","tool_input":{"path":".envrc"}}'

expect_block \
    "file tool blocks nested env file" \
    '{"tool_name":"Write","tool_input":{"file_path":"config/.env.local","content":"SECRET=x"}}'

expect_block \
    "apply_patch blocks env file add" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Add File: .env.local\n+SECRET=x\n*** End Patch\n"}}'

expect_block \
    "bash blocks env file read" \
    '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}'

expect_block \
    "bash blocks envrc file read" \
    '{"tool_name":"Bash","tool_input":{"command":"cat .envrc"}}'

expect_block \
    "bash blocks env file write" \
    '{"tool_name":"Bash","tool_input":{"command":"echo SECRET=x > .env.local"}}'

expect_block \
    "bash blocks quoted env file write" \
    '{"tool_name":"Bash","tool_input":{"command":"echo SECRET=x > \".env.local\""}}'

expect_block \
    "bash blocks parent env file write" \
    "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"echo SECRET=x > $PARENT_ENV\"}}"

expect_block \
    "shell-wrapped bash blocks env file read" \
    '{"tool_name":"Bash","tool_input":{"command":"bash -lc '\''sed -n 1p .env'\''"}}'

# --- Regression: .env Bash guard must not false-positive on non-file-access ---
expect_allow \
    "bash echo mentions env example" \
    '{"tool_name":"Bash","tool_input":{"command":"echo see .env.example for setup"}}'

expect_allow \
    "bash env-var assignment is not env access" \
    '{"tool_name":"Bash","tool_input":{"command":"FOO=.env make"}}'

expect_allow \
    "bash dot-environment dir is not an env file" \
    '{"tool_name":"Bash","tool_input":{"command":"ls .environment/"}}'

expect_allow \
    "bash read sentinel into elsewhere" \
    '{"tool_name":"Bash","tool_input":{"command":"cat .validation_passed > /tmp/codex-sentinel-copy"}}'

# --- Regression: results/ immutability must catch redirect + extra verbs ---
expect_block \
    "bash no-space redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x>results/example.json"}}'

expect_block \
    "bash quoted redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x > \"results/example.json\""}}'

expect_block \
    "bash parent redirect into results" \
    "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"printf x > $PARENT_RESULTS\"}}"

expect_block_in_dir \
    "$ROOT/.codex" \
    "bash subdir parent redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x > ../results/example.json"}}'

expect_block \
    "bash append redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"echo y>>results/example.json"}}'

expect_block \
    "bash combined redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x &>results/example.json"}}'

expect_block \
    "bash combined append redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x &>>results/example.json"}}'

expect_block \
    "bash clobber redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x >|results/example.json"}}'

expect_block \
    "bash read-write redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"cat <>results/example.json"}}'

expect_block \
    "bash stdout redirect into results" \
    '{"tool_name":"Bash","tool_input":{"command":"printf x >&results/example.json"}}'

expect_block \
    "bash dd writes results" \
    '{"tool_name":"Bash","tool_input":{"command":"dd of=results/example.json if=/dev/null"}}'

expect_block \
    "bash install writes results" \
    '{"tool_name":"Bash","tool_input":{"command":"install -m644 x results/example.json"}}'

expect_block \
    "bash hardlink over results" \
    '{"tool_name":"Bash","tool_input":{"command":"ln -f x results/example.json"}}'

# --- D7: audit logging is opt-in and writes OUTSIDE the repo ---
AUDIT_LOG="$(mktemp "$TMPDIR/codex-audit.XXXXXX")"
rm -f "$AUDIT_LOG"
export CODEX_HOOK_AUDIT_LOG="$AUDIT_LOG"
unset CODEX_HOOK_AUDIT
expect_allow \
    "default bash audit is disabled" \
    '{"tool_name":"Bash","tool_input":{"command":"printf ok"}}'
if [ -e "$AUDIT_LOG" ]; then
    echo "FAIL: audit log written while audit disabled" >&2
    exit 1
fi
echo "PASS: default bash audit wrote no log"
make_git_fixture
expect_allow_in_dir \
    "$GIT_FIXTURE" \
    "default bash audit does not create claude audit log" \
    '{"tool_name":"Bash","tool_input":{"command":"printf ok"}}'
if [ -e "$GIT_FIXTURE/.claude/audit.log" ]; then
    echo "FAIL: default audit created .claude/audit.log" >&2
    exit 1
fi
echo "PASS: default bash audit did not create .claude/audit.log"

export CODEX_HOOK_AUDIT=1
expect_allow \
    "opt-in bash audit is enabled" \
    '{"tool_name":"Bash","tool_input":{"command":"printf ok"}}'
if [ ! -e "$AUDIT_LOG" ]; then
    echo "FAIL: audit log not written while audit enabled" >&2
    exit 1
fi
case "$AUDIT_LOG" in
    "$ROOT"/*)
        echo "FAIL: audit log path is inside the repo: $AUDIT_LOG" >&2
        exit 1
        ;;
esac
echo "PASS: opt-in bash audit wrote log outside the repo"
unset CODEX_HOOK_AUDIT
rm -f "$AUDIT_LOG"

expect_block \
    "bash git push force after branch" \
    '{"tool_name":"Bash","tool_input":{"command":"git push origin main --force"}}'

expect_block \
    "bash git push force-with-lease after branch" \
    '{"tool_name":"Bash","tool_input":{"command":"git push origin main --force-with-lease"}}'

expect_block \
    "bash git push short force" \
    '{"tool_name":"Bash","tool_input":{"command":"git push origin main -f"}}'

expect_block \
    "bash git push clustered short force" \
    '{"tool_name":"Bash","tool_input":{"command":"git push -uf origin main"}}'

expect_block \
    "bash git push plus refspec" \
    '{"tool_name":"Bash","tool_input":{"command":"git push origin +main"}}'

expect_block \
    "bash git dash-C push force" \
    '{"tool_name":"Bash","tool_input":{"command":"git -C . push origin main --force"}}'

expect_block \
    "bash git dash-c push force" \
    '{"tool_name":"Bash","tool_input":{"command":"git -c core.hooksPath=/tmp push origin main --force"}}'

expect_block \
    "bash git work-tree push force" \
    '{"tool_name":"Bash","tool_input":{"command":"git --work-tree=. --git-dir=.git push origin +main"}}'

expect_block \
    "apply_patch invalid experiment config" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Add File: experiments/runs/demo/config.json\n+{\"schema_version\":1}\n*** End Patch\n"}}'

expect_block \
    "apply_patch parent path result update" \
    "{\"tool_name\":\"apply_patch\",\"tool_input\":{\"patch\":\"*** Begin Patch\\n*** Update File: $PARENT_RESULTS\\n@@\\n+{}\\n*** End Patch\\n\"}}"

expect_block_in_dir \
    "$ROOT/.codex" \
    "apply_patch subdir parent path result update" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Update File: ../results/example.json\n@@\n+{}\n*** End Patch\n"}}'

expect_allow \
    "apply_patch regular docs add" \
    '{"tool_name":"apply_patch","tool_input":{"patch":"*** Begin Patch\n*** Add File: docs/example.md\n+ok\n*** End Patch\n"}}'
