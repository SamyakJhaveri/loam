#!/usr/bin/env bash
# test_base_survives_gc.sh
# Codex Critical C1: a recorded merge base must survive `git gc --prune=now`.
# refs/agent-sync/bases keeps every base blob reachable, so a later clean
# three-way merge still preserves a hub-only generalization instead of falling
# back to the legacy overwrite. Leg 2: --bootstrap-bases re-records a base whose
# blob is missing (a stale sha) rather than trusting the stale value.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"

# --- Leg 1: base blob survives gc; generalization survives the later merge. ---
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

# Hub copy = base + a hub-only generalization on line 1.
mkdir -p "$HUB_SETUP/skills/foo"
printf 'alpha GENERALIZED\nbeta\ngamma\ndelta\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project copy = the shared base content.
mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'alpha\nbeta\ngamma\ndelta\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
BASE_SHA=$(git hash-object "$TMP/proj/.claude/$REL")

# 1) bootstrap records the base for the shared path.
set +e
bout=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
brc=$?
set -e
if [ "$brc" -ne 0 ]; then echo "FAIL: bootstrap exit $brc"; echo "$bout"; exit 1; fi

# Assertion 1: the durable ref exists (this is what keeps the blob past gc).
if ! git -C "$TMP/hub" rev-parse -q --verify refs/agent-sync/bases >/dev/null; then
  echo "FAIL: refs/agent-sync/bases not created by bootstrap"; echo "$bout"; exit 1
fi

# 2) garbage-collect the hub, pruning every unreachable object.
git -C "$TMP/hub" gc --prune=now -q

# Assertion 2: the base blob is still a blob in the object store.
if [ "$(git -C "$TMP/hub" cat-file -t "$BASE_SHA" 2>/dev/null)" != blob ]; then
  echo "FAIL: base blob $BASE_SHA pruned by gc (ref did not keep it reachable)"; exit 1
fi

# 3) an unrelated project edit on the last line, committed.
printf 'alpha\nbeta\ngamma\ndelta PROJECTEDIT\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git -c user.email=t@t -c user.name=t commit -q -am edit)

# 4) scan: y = accept the merge, then commit (EOF defaults commit=Y, push=N).
# H2 group 3: a declined commit now rolls the merge back, so the merged content
# lands only after a commit - this run commits.
set +e
out=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

HUB_FILE="$HUB_SETUP/$REL"

# Assertion 3: the clean-merge path was taken (base survived, no overwrite).
if ! echo "$out" | grep -q 'clean three-way merge'; then
  echo "FAIL: clean three-way merge not taken after gc"; echo "rc=$rc"; echo "$out"; exit 1
fi

# Assertion 4: the hub copy carries BOTH the generalization and the project edit.
EXPECT=$(printf 'alpha GENERALIZED\nbeta\ngamma\ndelta PROJECTEDIT\n')
if [ "$(cat "$HUB_FILE")" != "$EXPECT" ]; then
  echo "FAIL: merged hub copy wrong"; echo "--- got ---"; cat "$HUB_FILE"; exit 1
fi

# --- Leg 2: --bootstrap-bases re-records a base whose blob is missing. --------
TMP2="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP2"' EXIT

HUB2="$TMP2/hub/cultivation/marketplace/sam-cc-setup"
REL2="skills/bar/SKILL.md"

mkdir -p "$HUB2/skills/bar"
echo "hub bar" > "$HUB2/$REL2"
(cd "$TMP2/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP2/proj/.claude/skills/bar"
echo "project bar" > "$TMP2/proj/.claude/$REL2"
(cd "$TMP2/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Seed a stale (well-formed but absent) base sha.
BOGUS="deaddeaddeaddeaddeaddeaddeaddeaddeaddead"
{
  echo "session=1"
  echo "base:$REL2:$BOGUS"
} > "$TMP2/hub/.sync-state"

cd "$TMP2/proj"
REAL_SHA=$(git hash-object "$TMP2/proj/.claude/$REL2")

set +e
bout2=$(SAM_CC_HUB_REPO="$TMP2/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
brc2=$?
set -e
if [ "$brc2" -ne 0 ]; then echo "FAIL: leg2 bootstrap exit $brc2"; echo "$bout2"; exit 1; fi

# Assertion 5: the base line now carries the REAL blob sha, not the stale one.
if ! grep -qE "^base:$REL2:$REAL_SHA\$" "$TMP2/hub/.sync-state"; then
  echo "FAIL: stale base not re-recorded to $REAL_SHA"; cat "$TMP2/hub/.sync-state"; exit 1
fi
if grep -q "$BOGUS" "$TMP2/hub/.sync-state"; then
  echo "FAIL: stale base sha still present in state"; cat "$TMP2/hub/.sync-state"; exit 1
fi

# Assertion 6: the bootstrap counted it as recorded (not "already present").
if ! echo "$bout2" | grep -qE '1 bases recorded, 0 already present'; then
  echo "FAIL: stale-sha path not counted as recorded"; echo "$bout2"; exit 1
fi

echo "PASS: test_base_survives_gc"
