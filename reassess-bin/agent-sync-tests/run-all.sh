#!/usr/bin/env bash
# run-all.sh - run every agent-sync engine test in this directory and summarize.
# set -u and pipefail but NOT -e: a failing test must be counted and reported,
# never abort the runner. Wired into CI (.github/workflows/test.yml) and
# bin/verify-template.sh so the agent-sync engine suite cannot silently rot (M1).
set -uo pipefail

# L4: the runner must not inherit the engine's own knobs from the caller's
# environment - an exported SAM_CC_DEFER_SESSIONS (e.g. via verify-template.sh
# invariant 3b) or SAM_CC_HUB_REPO would skew or break individual tests, a false RED
# for a developer who legitimately exports one. Each test sets what it needs on its
# own invocation, so scrub every SAM_CC_* knob before the loop. `"${!SAM_CC_@}"` is
# set-u-safe (expands to nothing when none are set).
for _v in "${!SAM_CC_@}"; do unset "$_v"; done

DIR="$(cd "$(dirname "$0")" && pwd)"
passed=0
failed=0
fail_names=()

for t in "$DIR"/test_*.sh; do
  [ -e "$t" ] || continue
  name="$(basename "$t")"
  if out="$(bash "$t" 2>&1)"; then
    echo "PASS $name"
    passed=$((passed + 1))
  else
    echo "FAIL $name"
    while IFS= read -r line; do echo "    $line"; done <<< "$out"
    fail_names+=("$name")
    failed=$((failed + 1))
  fi
done

echo "agent-sync tests: $passed passed, $failed failed"
if [ "$failed" -gt 0 ]; then
  echo "failed: ${fail_names[*]}" >&2
  exit 1
fi
exit 0
