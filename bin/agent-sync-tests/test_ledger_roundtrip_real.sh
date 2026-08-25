#!/usr/bin/env bash
# test_ledger_roundtrip_real.sh
# R5 (group 11): running a legacy (un-prefixed) ledger through the per-project
# parser + write_state as the adopting project must lose ZERO records - each is
# ADOPTED (rewritten with the adopting project's identity). Round-trips a COPY of
# the real ledger if present (never the real hub), else a synthetic legacy ledger
# of the same shapes. The new format is uniformly the old record with
# "<PROJ_ID>\t" inserted right after the type colon; session=N -> session:<PROJ_ID>\tN.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Seed the legacy ledger: a READ-ONLY copy of the real one if it exists, else a
# synthetic legacy ledger covering every record type.
REAL="$HOME/Desktop/loam/.sync-state"
LEGACY="$TMP/hub/.sync-state"
if [ -s "$REAL" ] && ! grep -q $'\t' "$REAL"; then
  cp "$REAL" "$LEGACY"          # legacy (un-prefixed) real ledger
else
  {
    echo "session=3"
    echo "never:skills/a/S.md"
    echo "defer:skills/b/S.md:5"
    echo "synced:skills/c/S.md:2"
    echo "base:skills/d/S.md:$(printf 'd%.0s' {1..40})"
    echo "prune-never:skills/e/S.md"
    echo "prune-defer:skills/f/S.md:7"
  } > "$LEGACY"
fi

# Snapshot the original records (everything but blank lines).
grep -v '^[[:space:]]*$' "$LEGACY" > "$TMP/orig.txt"
ORIG_N=$(wc -l < "$TMP/orig.txt" | tr -d ' ')

# Adopting project (empty .claude so bootstrap records no new bases and does not
# bump the session - a clean round-trip of the loaded ledger).
mkdir -p "$TMP/proj/.claude"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)
PROJ_ID=$(git -C "$TMP/proj" rev-parse --show-toplevel)

set +e
out=$(cd "$TMP/proj" && SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: bootstrap exit $rc"; echo "$out"; exit 1; fi

# Every original record must survive, re-keyed to PROJ_ID. Transform each original
# line to its expected new-format form and grep -qF for it.
TAB=$'\t'
missing=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  case "$line" in
    session=*)
      want="session:${PROJ_ID}${TAB}${line#session=}" ;;
    *:*)
      want="${line%%:*}:${PROJ_ID}${TAB}${line#*:}" ;;   # insert PROJ_ID\t after the type colon
    *)
      want="$line" ;;
  esac
  if ! grep -qF -- "$want" "$LEGACY"; then
    echo "LOST/NOT-ADOPTED: $line  (expected: $want)"; missing=$((missing+1))
  fi
done < "$TMP/orig.txt"

if [ "$missing" -ne 0 ]; then
  echo "FAIL: $missing of $ORIG_N records were lost or not re-keyed on adoption (R5)"; echo "--- ledger after ---"; cat "$LEGACY"; exit 1
fi

# The session was adopted under PROJ_ID (not left as a bare global session=).
if ! grep -qF -- "session:${PROJ_ID}${TAB}" "$LEGACY"; then
  echo "FAIL: session not adopted under the project identity"; cat "$LEGACY"; exit 1
fi

echo "PASS: test_ledger_roundtrip_real ($ORIG_N records round-tripped)"
