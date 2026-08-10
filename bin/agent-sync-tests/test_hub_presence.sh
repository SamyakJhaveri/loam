#!/usr/bin/env bash
# test_hub_presence.sh
# Every dependency in a consumer's closure must ALREADY EXIST at its declared
# path under the hub plugin (presence only, never byte identity — hub copies
# intentionally diverge after de-projectization):
#   Leg 1: consumer (travels) requires helper (travels), helper ABSENT from
#          the hub: the helper may be offered, the consumer must be withheld
#          with a sync-the-dependency-first explanation.
#   Leg 2: rerun after the helper exists in the hub (different bytes than the
#          project copy, proving presence-only): the consumer must be offered.
# Both legs assert sync.sh's exit status via run_sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

run_sync() {
  local hub="$1" rc=0
  out=$(printf 'n\nn\nn\n' | SAM_CC_HUB_REPO="$hub" bash "$SYNC_SH" 2>&1) || rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FAIL: sync.sh exited $rc (expected 0). Output:"; echo "$out"; exit 1
  fi
}

hub="$TMP/hub"
rm -rf "$hub"
mkdir -p "$hub/cultivation/marketplace/sam-cc-setup"
(cd "$hub" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)

proj="$TMP/proj"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "consumer" > "$proj/.claude/hooks/consumer.sh"
echo "helper-project-copy" > "$proj/.claude/hooks/helper.sh"
{ printf 'path\tkind\tverdict\treason\trequires\n'
  printf 'hooks/consumer.sh\thook\ttravels\ttest consumer\thooks/helper.sh\n'
  printf 'hooks/helper.sh\thook\ttravels\ttest helper\t\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"

# --- Leg 1: helper absent from hub -> consumer withheld, helper offered ---
run_sync "$hub"
echo "$out" | grep -q "Add hooks/helper.sh" || { echo "FAIL leg1: helper.sh (travels, deps-free) was not offered"; echo "$out"; exit 1; }
echo "$out" | grep -q "Add hooks/consumer.sh" && { echo "FAIL leg1: consumer.sh was offered while its dep helper.sh is absent from the hub"; exit 1; }
echo "$out" | grep -q "withheld: hooks/consumer.sh requires hooks/helper.sh" || { echo "FAIL leg1: no withheld message for consumer.sh"; echo "$out"; exit 1; }
echo "$out" | grep -qi "sync the dependency first\|not yet in the hub" || { echo "FAIL leg1: withheld message does not explain the dependency must be synced first"; echo "$out"; exit 1; }

# --- Leg 2: helper now present in hub (DIFFERENT bytes) -> consumer offered ---
mkdir -p "$hub/cultivation/marketplace/sam-cc-setup/hooks"
echo "helper-generalized-hub-copy" > "$hub/cultivation/marketplace/sam-cc-setup/hooks/helper.sh"
(cd "$hub" && git add -A && git -c user.email=t@t -c user.name=t commit -q -m seed)
run_sync "$hub"
echo "$out" | grep -q "Add hooks/consumer.sh" || { echo "FAIL leg2: consumer.sh was not offered after its dep exists in the hub (presence-only check violated?)"; echo "$out"; exit 1; }

# --- Leg 3: dep present ONLY as an untracked hub working-tree file (not in
# HEAD) does NOT count as present — the scoped sync commit would not include
# it. The untracked file also dirties the hub, so answer y to the dirty-hub
# warning, then decline the prompts. ---
hub3="$TMP/hub3"
rm -rf "$hub3"
mkdir -p "$hub3/cultivation/marketplace/sam-cc-setup/hooks"
(cd "$hub3" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)
echo "helper-untracked-wip" > "$hub3/cultivation/marketplace/sam-cc-setup/hooks/helper.sh"
rc=0
out=$(printf 'y\nn\nn\nn\n' | SAM_CC_HUB_REPO="$hub3" bash "$SYNC_SH" 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  echo "FAIL leg3: sync.sh exited $rc (expected 0). Output:"; echo "$out"; exit 1
fi
echo "$out" | grep -q "Add hooks/consumer.sh" && { echo "FAIL leg3: consumer.sh was offered although its dep exists only as an untracked hub file (not in HEAD)"; exit 1; }
echo "$out" | grep -q "withheld: hooks/consumer.sh requires hooks/helper.sh" || { echo "FAIL leg3: no withheld message for consumer.sh with untracked-only dep"; echo "$out"; exit 1; }

echo "PASS test_hub_presence.sh"
