#!/usr/bin/env bash
# test_round2_chmod_and_prune_failures.sh
# Codex round-2 hardening, three legs:
#   A (High, safe-io chmod): a FIFO or directory raced into a mode-change target
#      must be refused - O_NONBLOCK prevents the FIFO open from blocking forever,
#      and the fstat regular-file check rejects both.
#   B (Medium, scan untracked prune): a failed no-follow unlink must KEEP the
#      ledger record (clearing it would orphan the leftover forever) and must not
#      report the path as pruned; the next scan re-offers it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
SAFE_IO="$SCRIPT_DIR/../agent-sync-safe-io.py"
TMP="$(mktemp -d)"
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

if [ "$(id -u)" -eq 0 ]; then
  echo "FAIL: this test must run as a non-root user (root bypasses the chmod-based injection)"
  exit 1
fi

# ---- Leg A: helper chmod refuses non-regular targets, without hanging ----
H="$TMP/hubA"
mkdir -p "$H/d"
mkfifo "$H/d/pipe"
mkdir "$H/d/subdir"
set +e
outA1=$(python3 "$SAFE_IO" chmod "$H" "d/pipe" 755 2>&1)
rcA1=$?
outA2=$(python3 "$SAFE_IO" chmod "$H" "d/subdir" 755 2>&1)
rcA2=$?
set -e
if [ "$rcA1" -eq 0 ] || ! echo "$outA1" | grep -q "non-regular"; then
  echo "FAIL(A): chmod of a FIFO was not refused (rc=$rcA1)"; echo "$outA1"; exit 1
fi
# (Reaching this line at all proves the FIFO open did not block: O_NONBLOCK works.)
if [ "$rcA2" -eq 0 ]; then
  echo "FAIL(A): chmod of a directory was not refused"; echo "$outA2"; exit 1
fi

# ---- Leg B: untracked-prune unlink failure keeps the ledger record ----
HUB="$TMP/hub"
HUB_SETUP="$HUB/cultivation/marketplace/sam-cc-setup"
P="skills/x/old.md"
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$HUB" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
# The leftover is UNTRACKED (created after the commit), with a legacy synced:
# record making it a prune candidate once the project side is gone.
echo "leftover" > "$HUB_SETUP/$P"
{ echo "session=3"; echo "synced:$P:2"; } > "$HUB/.sync-state"

mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Injection: the leftover's parent directory is read-only, so unlink gets EACCES.
chmod 0555 "$HUB_SETUP/skills/x"

cd "$TMP/proj"
set +e
out1=$(yes | SAM_CC_HUB_REPO="$HUB" bash "$SYNC_SH" 2>&1)
set -e
chmod 0755 "$HUB_SETUP/skills/x"

# 1: the leftover is still there (unlink genuinely failed).
if [ ! -e "$HUB_SETUP/$P" ]; then
  echo "FAIL(B): unexpected - the unlink succeeded despite the read-only parent"; exit 1
fi
# 2 (RED flip): the failure was announced and the path NOT reported pruned.
if ! echo "$out1" | grep -q "could not remove untracked hub copy"; then
  echo "FAIL(B): no unlink-failure warning"; echo "$out1"; exit 1
fi
if echo "$out1" | grep -q "pruned untracked hub copy: removed $P"; then
  echo "FAIL(B): the path was reported pruned despite the failed unlink"; echo "$out1"; exit 1
fi
# 3 (RED flip, the orphan bug): the ledger record survives (adopted into the
# group-11 prefixed format), keeping the path in prune candidacy.
if ! grep -Eq "^synced:.*[[:space:]]$P:" "$HUB/.sync-state" 2>/dev/null; then
  echo "FAIL(B): the ledger record was cleared despite the failed unlink (orphaned forever)"
  cat "$HUB/.sync-state"; exit 1
fi
# 4: the next scan re-offers the same prune (writable again now).
set +e
out2=$(yes | SAM_CC_HUB_REPO="$HUB" bash "$SYNC_SH" 2>&1)
set -e
if ! echo "$out2" | grep -qi "delete"; then
  echo "FAIL(B): run 2 did not re-offer the prune"; echo "$out2"; exit 1
fi
if [ -e "$HUB_SETUP/$P" ]; then
  echo "FAIL(B): run 2 approved the prune but the leftover is still there"; echo "$out2"; exit 1
fi

echo "PASS: test_round2_chmod_and_prune_failures"
