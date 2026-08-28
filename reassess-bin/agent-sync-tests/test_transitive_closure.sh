#!/usr/bin/env bash
# test_transitive_closure.sh
# The dependency guard must resolve the COMPLETE transitive closure of the
# manifest `requires` graph, not just the consumer's direct cell:
#   Leg 1: A -> B -> C where C is 'rework': A must be withheld even though A
#          lists only B directly (B is present in the hub so the failure can
#          only come from following B's own requires cell).
#   Leg 2: a dependency cycle (a <-> b) must fail closed with a diagnostic,
#          never loop or silently offer.
#   Leg 3: a dependency with NO manifest row must fail closed.
# Every leg asserts sync.sh's exit status via run_sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

run_sync() {
  local hub="$1" rc=0
  out=$(printf 'n\nn\nn\n' | SAM_CC_HUB_REPO="$hub" bash "$SYNC_SH" 2>&1) || rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FAIL: sync.sh exited $rc (expected 0). Output:"; echo "$out"; exit 1
  fi
}

build_hub() {
  local hub="$1"
  rm -rf "$hub"
  mkdir -p "$hub/cultivation/marketplace/sam-cc-setup"
  (cd "$hub" && git init -q && \
    git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)
}

manifest_header() { printf 'path\tkind\tverdict\treason\trequires\n'; }

# Commit a file into a hub so the dirty-hub warning does not fire.
hub_commit() {
  (cd "$1" && git add -A && git -c user.email=t@t -c user.name=t commit -q -m seed)
}

# --- Leg 1: A -> B -> C, C is rework, B already in the hub ---
build_hub "$TMP/hub1"
mkdir -p "$TMP/hub1/cultivation/marketplace/sam-cc-setup/hooks"
echo "b" > "$TMP/hub1/cultivation/marketplace/sam-cc-setup/hooks/b.sh"
hub_commit "$TMP/hub1"
proj="$TMP/proj1"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a" > "$proj/.claude/hooks/a.sh"
echo "b" > "$proj/.claude/hooks/b.sh"
echo "c" > "$proj/.claude/hooks/c.sh"
{ manifest_header
  printf 'hooks/a.sh\thook\ttravels\ttest\thooks/b.sh\n'
  printf 'hooks/b.sh\thook\ttravels\ttest\thooks/c.sh\n'
  printf 'hooks/c.sh\thook\trework\ttest, not generalized\t\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
run_sync "$TMP/hub1"
echo "$out" | grep -q "Add hooks/a.sh" && { echo "FAIL leg1: a.sh was offered despite transitive dep c.sh being 'rework'"; exit 1; }
echo "$out" | grep -q "withheld: hooks/a.sh requires hooks/c.sh" || { echo "FAIL leg1: no withheld message naming a.sh's TRANSITIVE dep c.sh"; echo "$out"; exit 1; }

# --- Leg 2: dependency cycle a <-> b, both travels, both present in hub ---
build_hub "$TMP/hub2"
mkdir -p "$TMP/hub2/cultivation/marketplace/sam-cc-setup/hooks"
echo "a" > "$TMP/hub2/cultivation/marketplace/sam-cc-setup/hooks/cyc_a.sh"
echo "b" > "$TMP/hub2/cultivation/marketplace/sam-cc-setup/hooks/cyc_b.sh"
hub_commit "$TMP/hub2"
proj="$TMP/proj2"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a2" > "$proj/.claude/hooks/cyc_a.sh"
echo "b2" > "$proj/.claude/hooks/cyc_b.sh"
{ manifest_header
  printf 'hooks/cyc_a.sh\thook\ttravels\ttest\thooks/cyc_b.sh\n'
  printf 'hooks/cyc_b.sh\thook\ttravels\ttest\thooks/cyc_a.sh\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
run_sync "$TMP/hub2"
echo "$out" | grep -q "Update hooks/cyc_a.sh\|Add hooks/cyc_a.sh" && { echo "FAIL leg2: cyc_a.sh was offered despite a dependency cycle"; exit 1; }
echo "$out" | grep -qi "cycle" || { echo "FAIL leg2: no cycle diagnostic printed"; echo "$out"; exit 1; }

# --- Leg 3: dependency with no manifest row fails closed ---
build_hub "$TMP/hub3"
proj="$TMP/proj3"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a" > "$proj/.claude/hooks/norow.sh"
echo "x" > "$proj/.claude/hooks/ghost.sh"
{ manifest_header
  printf 'hooks/norow.sh\thook\ttravels\ttest\thooks/ghost.sh\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
run_sync "$TMP/hub3"
echo "$out" | grep -q "Add hooks/norow.sh" && { echo "FAIL leg3: norow.sh was offered despite its dep having no manifest row"; exit 1; }
echo "$out" | grep -q "withheld: hooks/norow.sh" || { echo "FAIL leg3: norow.sh not withheld (missing-row must fail closed)"; echo "$out"; exit 1; }

# --- Leg 4: cycle whose members are ABSENT from the hub must still report the
# cycle diagnostic (graph validation runs before hub-presence, so an absent
# node cannot mask the cycle) ---
build_hub "$TMP/hub4"
proj="$TMP/proj4"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a" > "$proj/.claude/hooks/cyc_a.sh"
echo "b" > "$proj/.claude/hooks/cyc_b.sh"
{ manifest_header
  printf 'hooks/cyc_a.sh\thook\ttravels\ttest\thooks/cyc_b.sh\n'
  printf 'hooks/cyc_b.sh\thook\ttravels\ttest\thooks/cyc_a.sh\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
run_sync "$TMP/hub4"
echo "$out" | grep -q "Add hooks/cyc_a.sh" && { echo "FAIL leg4: cyc_a.sh was offered despite a cycle with absent members"; exit 1; }
echo "$out" | grep -qi "cycle" || { echo "FAIL leg4: absent cycle member masked the cycle diagnostic (absence reported instead)"; echo "$out"; exit 1; }

# --- Leg 5: malformed dependency path (../escape or absolute) fails closed
# without hanging the rowkey walk ---
build_hub "$TMP/hub5"
proj="$TMP/proj5"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a" > "$proj/.claude/hooks/badpath.sh"
{ manifest_header
  printf 'hooks/badpath.sh\thook\ttravels\ttest\t../escape.sh\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
run_sync "$TMP/hub5"
echo "$out" | grep -q "Add hooks/badpath.sh" && { echo "FAIL leg5: badpath.sh was offered despite a malformed ../ dep path"; exit 1; }
echo "$out" | grep -q "malformed dependency path" || { echo "FAIL leg5: no malformed-path diagnostic"; echo "$out"; exit 1; }

# --- Leg 6: ABSOLUTE dep path fails closed. This is the malformed-path
# guard's headline case: without the `//*` alternative, an absolute path makes
# the dirname walk in manifest_rowkey loop forever (dirname / = /), hanging
# the sync. Run under a watchdog so a regression fails instead of hanging. ---
build_hub "$TMP/hub6"
proj="$TMP/proj6"
rm -rf "$proj"; mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
echo "a" > "$proj/.claude/hooks/abspath.sh"
{ manifest_header
  printf 'hooks/abspath.sh\thook\ttravels\ttest\t/abs/escape.sh\n'
} > "$proj/.claude/reference/portability-manifest.tsv"
(cd "$proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$proj"
# The watchdog must kill sync.sh's own PID, not a wrapper subshell (Codex
# review: a killed wrapper leaves sync.sh alive holding stdout, so the hang
# survives). $! after the pipeline is the bash "$SYNC_SH" process itself; the
# watchdog's stdout goes to /dev/null so its orphaned sleep cannot hold the
# command substitution open.
rc=0
out=$(
  printf 'n\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub6" bash "$SYNC_SH" 2>&1 & spid=$!
  ( sleep 30; kill "$spid" 2>/dev/null ) >/dev/null 2>&1 & wpid=$!
  wait "$spid"; st=$?
  kill "$wpid" 2>/dev/null
  exit "$st"
) || rc=$?
if [ "$rc" -ne 0 ]; then
  echo "FAIL leg6: sync.sh exited $rc (expected 0; 143 = watchdog kill -> infinite loop regression). Output:"; echo "$out"; exit 1
fi
echo "$out" | grep -q "Add hooks/abspath.sh" && { echo "FAIL leg6: abspath.sh was offered despite an absolute dep path"; exit 1; }
echo "$out" | grep -q "malformed dependency path" || { echo "FAIL leg6: no malformed-path diagnostic for absolute dep"; echo "$out"; exit 1; }

echo "PASS test_transitive_closure.sh"
