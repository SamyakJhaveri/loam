#!/usr/bin/env bash
# test_safe_io_nofollow.sh
# TOCTOU (group 12): the atomic no-follow install helper closes the check-then-act
# gap between reject_symlink_path and install_file's cp/mkdir. Proven directly:
#   (positive) a NORMAL install through the helper lands the file with its mode;
#   (negative) an install/mkdir through a SYMLINK directory component is REFUSED
#              and writes NOTHING outside the hub root;
#   (baseline) a plain cp/mkdir -p through the SAME symlink DOES write outside -
#              so the scenario is genuinely follow-vulnerable and the test is not
#              vacuous.
# RED (no helper yet): the positive install assertion fails (helper missing).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HELPER="$SCRIPT_DIR/../agent-sync-safe-io.py"
TMP="$(mktemp -d)"
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

mode_of() { stat -c '%a' "$1" 2>/dev/null || stat -f '%Lp' "$1" 2>/dev/null; }

# ---- Positive: a normal install lands the file with its source mode ----
HUB="$TMP/hub"; mkdir -p "$HUB"
SRC="$TMP/src.sh"; printf '#!/bin/sh\necho hi\n' > "$SRC"; chmod 755 "$SRC"
REL="cultivation/marketplace/sam-cc-setup/skills/x/h.sh"
set +e; python3 "$HELPER" install "$HUB" "$REL" "$SRC" >/dev/null 2>&1; pi=$?; set -e
if [ "$pi" -ne 0 ]; then echo "FAIL: helper install of a normal file failed (rc $pi) - helper missing or broken"; exit 1; fi
if [ ! -f "$HUB/$REL" ]; then echo "FAIL: helper did not create the file"; exit 1; fi
if [ "$(cat "$HUB/$REL")" != "$(cat "$SRC")" ]; then echo "FAIL: helper wrote wrong content"; exit 1; fi
if [ "$(mode_of "$HUB/$REL")" != "755" ]; then echo "FAIL: helper did not preserve the source mode (got $(mode_of "$HUB/$REL"))"; exit 1; fi

# ---- Large file: the write-all loop must not short-write / truncate ----
BIG="$TMP/big.bin"; dd if=/dev/urandom of="$BIG" bs=1048576 count=5 status=none
BREL="cultivation/marketplace/sam-cc-setup/assets/big.bin"
set +e; python3 "$HELPER" install "$HUB" "$BREL" "$BIG" >/dev/null 2>&1; bi=$?; set -e
if [ "$bi" -ne 0 ]; then echo "FAIL: helper install of a 5MB file failed (rc $bi)"; exit 1; fi
if ! cmp -s "$BIG" "$HUB/$BREL"; then echo "FAIL: 5MB install is NOT byte-identical (short write / truncation)"; exit 1; fi

# ---- Negative + baseline: a SYMLINK directory component must not be followed ----
HUB2="$TMP/hub2"; mkdir -p "$HUB2"
OUT="$TMP/outside"; mkdir -p "$OUT"                     # the escape target
ln -s "$OUT" "$HUB2/cultivation"                        # a symlink component in the hub path
REL2="cultivation/marketplace/sam-cc-setup/skills/y/h.sh"

# Baseline sanity: a plain mkdir -p + cp FOLLOWS the symlink and writes outside.
mkdir -p "$HUB2/$(dirname "$REL2")" 2>/dev/null && cp "$SRC" "$HUB2/$REL2" 2>/dev/null || true
if [ ! -e "$OUT/marketplace/sam-cc-setup/skills/y/h.sh" ]; then
  echo "FAIL: baseline plain cp did NOT write through the symlink - fixture not follow-vulnerable, test would be vacuous"; exit 1
fi
rm -rf "${OUT:?}"/* 2>/dev/null || true                    # clear the baseline's escape

# The helper must REFUSE the same install (no-follow) and write nothing outside.
set +e; python3 "$HELPER" install "$HUB2" "$REL2" "$SRC" >/dev/null 2>&1; hi=$?; set -e
if [ "$hi" -eq 0 ]; then echo "FAIL: helper install followed a symlink component (did not refuse)"; exit 1; fi
if [ -e "$OUT/marketplace/sam-cc-setup/skills/y/h.sh" ]; then
  echo "FAIL: helper install wrote OUTSIDE the hub through a symlink component (TOCTOU not closed)"; exit 1
fi

# The mkdir helper must refuse the symlink component too.
set +e; python3 "$HELPER" mkdir "$HUB2" "cultivation/marketplace/sam-cc-setup/skills/z" >/dev/null 2>&1; hm=$?; set -e
if [ "$hm" -eq 0 ]; then echo "FAIL: helper mkdir followed a symlink component (did not refuse)"; exit 1; fi
if [ -e "$OUT/marketplace/sam-cc-setup/skills/z" ]; then
  echo "FAIL: helper mkdir created a dir OUTSIDE the hub through a symlink component"; exit 1
fi

echo "PASS: test_safe_io_nofollow"
