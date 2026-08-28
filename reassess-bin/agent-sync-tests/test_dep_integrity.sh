#!/usr/bin/env bash
# test_dep_integrity.sh
# Verifies the dependency-integrity guard: a 'travels' consumer whose
# column-5 `requires` cell names a helper that is NOT itself 'travels' must
# be withheld, even though the consumer's own verdict is 'travels'. Without
# this guard, sync.sh offers a consumer purely on its own manifest_verdict,
# shipping a half-broken gate to the hub (e.g. pre-commit-gate.sh without
# gate_tier.py). Leg 4 covers directory rows: a file offered under a
# directory row must inherit that row's `requires` cell via the same
# longest-prefix walk manifest_verdict uses (Codex review 2026-08-05 High:
# an exact-match lookup silently skipped the guard for such files).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Run sync.sh declining every prompt; capture output AND assert exit 0.
# (A post-diagnostic crash must fail the test, not hide behind `|| true`.)
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

# Synthetic leg: consumer.sh is 'travels' but requires helper.sh, which is
# 'rework' (withheld). consumer.sh must therefore also be withheld.
build_proj_synthetic() {
  local proj="$1"
  rm -rf "$proj"
  mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
  echo "c" > "$proj/.claude/hooks/consumer.sh"
  echo "h" > "$proj/.claude/hooks/helper.sh"
  printf 'path\tkind\tverdict\treason\trequires\n' > "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/consumer.sh\thook\ttravels\ttest consumer\thooks/helper.sh\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/helper.sh\thook\trework\ttest helper, not yet generalized\t\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  (cd "$proj" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# Real-rows leg: pre-commit-gate.sh (travels) requires gate_tier.py (rework
# in the real repo manifest) -> pre-commit-gate.sh must be withheld. Copies
# the real project's manifest rows for these two paths, ties the control to
# the actual defect this session fixed.
build_proj_real() {
  local proj="$1"
  rm -rf "$proj"
  mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
  echo "g" > "$proj/.claude/hooks/pre-commit-gate.sh"
  echo "t" > "$proj/.claude/hooks/gate_tier.py"
  printf 'path\tkind\tverdict\treason\trequires\n' > "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/pre-commit-gate.sh\thook\ttravels\ttest\thooks/gate_tier.py\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/gate_tier.py\thook\trework\ttest, project prefixes hardcoded\t\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  (cd "$proj" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# Positive leg: consumer2.sh requires helper2.sh, which IS 'travels' AND is
# already present in the hub (seeded below with different bytes - the guard
# checks presence, never byte identity) -> consumer2 offered as Add, helper2
# offered as Update. (Updated 2026-08-05: the closure guard now also requires
# hub presence, so the old expectation - consumer offered while its dep is
# absent from the hub - was the exact defect test_hub_presence.sh pins down.)
build_proj_satisfied() {
  local proj="$1"
  rm -rf "$proj"
  mkdir -p "$proj/.claude/hooks" "$proj/.claude/reference"
  echo "c" > "$proj/.claude/hooks/consumer2.sh"
  echo "h" > "$proj/.claude/hooks/helper2.sh"
  printf 'path\tkind\tverdict\treason\trequires\n' > "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/consumer2.sh\thook\ttravels\ttest consumer\thooks/helper2.sh\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/helper2.sh\thook\ttravels\ttest helper\t\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  (cd "$proj" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# Directory-row leg: the manifest classifies the DIRECTORY skills/validate as
# travels with a rework dep; the file offered by rsync is skills/validate/SKILL.md.
# The guard must inherit `requires` through the longest-prefix walk and withhold it.
build_proj_dirrow() {
  local proj="$1"
  rm -rf "$proj"
  mkdir -p "$proj/.claude/skills/validate" "$proj/.claude/hooks" "$proj/.claude/reference"
  echo "s" > "$proj/.claude/skills/validate/SKILL.md"
  echo "t" > "$proj/.claude/hooks/gate_tier.py"
  printf 'path\tkind\tverdict\treason\trequires\n' > "$proj/.claude/reference/portability-manifest.tsv"
  printf 'skills/validate\tskill\ttravels\ttest dir row\thooks/gate_tier.py\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  printf 'hooks/gate_tier.py\thook\trework\ttest, project prefixes hardcoded\t\n' >> "$proj/.claude/reference/portability-manifest.tsv"
  (cd "$proj" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# --- Leg 1: synthetic withheld-dep ---
build_hub "$TMP/hub1"; build_proj_synthetic "$TMP/proj1"
cd "$TMP/proj1"
run_sync "$TMP/hub1"
echo "$out" | grep -q "Add hooks/consumer.sh" && { echo "FAIL: consumer.sh was offered despite its dep (helper.sh) being 'rework'"; exit 1; }
echo "$out" | grep -q "withheld: hooks/consumer.sh requires hooks/helper.sh" || { echo "FAIL: no withheld-dep message for consumer.sh"; exit 1; }

# --- Leg 2: real rows (pre-commit-gate.sh / gate_tier.py) ---
build_hub "$TMP/hub2"; build_proj_real "$TMP/proj2"
cd "$TMP/proj2"
run_sync "$TMP/hub2"
echo "$out" | grep -q "Add hooks/pre-commit-gate.sh" && { echo "FAIL: pre-commit-gate.sh was offered despite gate_tier.py being 'rework'"; exit 1; }
echo "$out" | grep -q "withheld: hooks/pre-commit-gate.sh requires hooks/gate_tier.py" || { echo "FAIL: no withheld-dep message for pre-commit-gate.sh"; exit 1; }

# --- Leg 3: satisfied dep (positive control) ---
build_hub "$TMP/hub3"; build_proj_satisfied "$TMP/proj3"
mkdir -p "$TMP/hub3/cultivation/marketplace/sam-cc-setup/hooks"
echo "h-generalized-hub-copy" > "$TMP/hub3/cultivation/marketplace/sam-cc-setup/hooks/helper2.sh"
(cd "$TMP/hub3" && git add -A && git -c user.email=t@t -c user.name=t commit -q -m seed)
cd "$TMP/proj3"
run_sync "$TMP/hub3"
echo "$out" | grep -q "Add hooks/consumer2.sh" || { echo "FAIL: consumer2.sh was withheld despite its dep (helper2.sh) being 'travels' and present in the hub"; exit 1; }
echo "$out" | grep -q "Update hooks/helper2.sh" || { echo "FAIL: helper2.sh (a plain travels path, changed vs hub) was not offered"; exit 1; }

# --- Leg 4: directory row (longest-prefix requires inheritance) ---
build_hub "$TMP/hub4"; build_proj_dirrow "$TMP/proj4"
cd "$TMP/proj4"
run_sync "$TMP/hub4"
echo "$out" | grep -q "Add skills/validate/SKILL.md" && { echo "FAIL: SKILL.md under dir row was offered despite the row's dep (gate_tier.py) being 'rework'"; exit 1; }
echo "$out" | grep -q "withheld: skills/validate/SKILL.md requires hooks/gate_tier.py" || { echo "FAIL: no withheld-dep message for skills/validate/SKILL.md (dir-row requires not inherited)"; exit 1; }

echo "PASS test_dep_integrity.sh"
