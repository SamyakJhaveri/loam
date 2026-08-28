#!/usr/bin/env bash
# test_ledger_unterminated_final_line.sh
# L2: a .sync-state whose FINAL line has no trailing newline is silently dropped by
# `while IFS= read -r line` (read returns non-zero at EOF-without-delimiter, so the
# body never runs for that line), then permanently erased by the next write_state.
# Fix: `while IFS= read -r line || [ -n "$line" ]` processes the final line.
# RED: the seeded never: record on the unterminated final line is dropped and does
# NOT reappear in the rewritten ledger. GREEN: it survives, re-keyed to PROJ_ID.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REL="skills/keep/S.md"
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

# Hub and project hold identical content at REL, so the scan is a genuine no-op
# (no adds/changes/prunes) and only the EXIT-trap write_state rewrites the ledger.
mkdir -p "$HUB_SETUP/skills/keep"
echo "same body" > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/keep"
echo "same body" > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Seed the ledger with a FINAL line that has NO trailing newline. printf without a
# trailing \n on the last record is the exact L2 trigger (a hand edit).
STATE="$TMP/hub/.sync-state"
printf 'session=3\nnever:%s' "$REL" > "$STATE"
# Assert the fixture really lacks a trailing newline (guards the test itself).
if [ "$(tail -c1 "$STATE" | wc -l | tr -d ' ')" != "0" ]; then
  echo "FAIL(fixture): seeded ledger unexpectedly ends with a newline"; exit 1
fi

cd "$TMP/proj"
set +e
out=$(printf '' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then echo "FAIL: no-op scan exit $rc"; echo "$out"; exit 1; fi

# The never: record on the unterminated final line must survive the read+write
# round-trip: present in the rewritten ledger, re-keyed to this project (M3 form).
if ! grep -qE "^never:[^$T]*${T}$REL\$" "$STATE"; then
  echo "FAIL: never: record on the unterminated final line was dropped and erased (L2)"
  echo "--- rewritten ledger ---"; cat "$STATE"; echo "--- scan output ---"; echo "$out"
  exit 1
fi

echo "PASS: test_ledger_unterminated_final_line"
