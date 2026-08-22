#!/usr/bin/env bash
# run-all.sh - run every agent-sync engine test in this directory and summarize.
# set -u and pipefail but NOT -e: a failing test must be counted and reported,
# never abort the runner. Wired into CI (.github/workflows/test.yml) and
# bin/verify-template.sh so the agent-sync engine suite cannot silently rot (M1).
set -uo pipefail

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
