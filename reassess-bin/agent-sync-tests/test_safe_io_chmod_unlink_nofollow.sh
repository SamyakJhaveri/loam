#!/usr/bin/env bash
# test_safe_io_chmod_unlink_nofollow.sh
# CX-4 (High): mode propagation (scan.sh) did a plain chmod after the symlink
# check, and rollback / untracked-prune did a plain rm - both FOLLOW a symlink
# swapped in after the check (TOCTOU, the OD-10c class closed for install). The fix
# adds no-follow chmod and unlink subcommands to agent-sync-safe-io.py (the same
# _descend/_open_dir fd chain as install). Proven directly:
#   (positive) helper chmod sets a normal file's mode; helper unlink removes a
#              normal file - the RED flip (subcommands absent in the old helper).
#   (negative+baseline chmod) a final component that is a symlink to an outside
#              file: plain chmod FOLLOWS and changes the outside mode; the helper
#              chmod REFUSES and leaves it.
#   (negative+baseline unlink) a symlink DIRECTORY component: plain rm FOLLOWS and
#              removes an outside file; the helper unlink REFUSES and leaves it.
#   (rm -f semantics) helper unlink of a missing file exits 0.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HELPER="$SCRIPT_DIR/../agent-sync-safe-io.py"
TMP="$(mktemp -d)"
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

mode_of() { stat -c '%a' "$1" 2>/dev/null || stat -f '%Lp' "$1" 2>/dev/null; }
HP="cultivation/marketplace/sam-cc-setup"

# ---- Positive chmod: helper chmod sets a normal hub file's mode (RED flip) ----
HUB="$TMP/hub"; mkdir -p "$HUB/$HP/skills/x"
F="$HP/skills/x/h.sh"; printf '#!/bin/sh\n' > "$HUB/$F"; chmod 644 "$HUB/$F"
set +e; python3 "$HELPER" chmod "$HUB" "$F" 755 >/dev/null 2>&1; pc=$?; set -e
if [ "$pc" -ne 0 ]; then echo "FAIL: helper chmod of a normal file failed (rc $pc) - subcommand missing or broken"; exit 1; fi
if [ "$(mode_of "$HUB/$F")" != "755" ]; then echo "FAIL: helper chmod did not set the mode (got $(mode_of "$HUB/$F"))"; exit 1; fi

# ---- Positive unlink: helper unlink removes a normal hub file (RED flip) ----
G="$HP/skills/x/gone.md"; echo x > "$HUB/$G"
set +e; python3 "$HELPER" unlink "$HUB" "$G" >/dev/null 2>&1; pu=$?; set -e
if [ "$pu" -ne 0 ]; then echo "FAIL: helper unlink of a normal file failed (rc $pu) - subcommand missing or broken"; exit 1; fi
if [ -e "$HUB/$G" ]; then echo "FAIL: helper unlink did not remove the file"; exit 1; fi

# ---- rm -f semantics: unlink of a missing file exits 0 ----
set +e; python3 "$HELPER" unlink "$HUB" "$HP/skills/x/never.md" >/dev/null 2>&1; pm=$?; set -e
if [ "$pm" -ne 0 ]; then echo "FAIL: helper unlink of a missing file did not exit 0 (rm -f semantics)"; exit 1; fi

# ---- unlink of a DIRECTORY refuses CLEANLY (EISDIR on Linux, EPERM on macOS) ----
# The refusal must be a clean _die, never a Python traceback, on both platforms.
set +e; derr=$(python3 "$HELPER" unlink "$HUB" "$HP/skills/x" 2>&1); dc=$?; set -e
if [ "$dc" -eq 0 ]; then echo "FAIL: helper unlink of a directory did not refuse"; exit 1; fi
if echo "$derr" | grep -q "Traceback"; then
  echo "FAIL: helper unlink of a directory raised a traceback instead of a clean error"; echo "$derr"; exit 1
fi
if [ ! -d "$HUB/$HP/skills/x" ]; then echo "FAIL: helper unlink removed a directory"; exit 1; fi

# ---- Negative+baseline chmod: a final component that is a symlink to outside ----
HUB2="$TMP/hub2"; mkdir -p "$HUB2/$HP/skills/y"
OUT="$TMP/outside.txt"; echo secret > "$OUT"; chmod 600 "$OUT"
LN="$HP/skills/y/link.sh"; ln -s "$OUT" "$HUB2/$LN"        # final component is a symlink to outside
# Baseline: a plain chmod FOLLOWS the symlink and changes the outside file's mode.
chmod 755 "$HUB2/$LN"
if [ "$(mode_of "$OUT")" != "755" ]; then
  echo "FAIL: baseline plain chmod did NOT follow the symlink - fixture not follow-vulnerable, test vacuous"; exit 1
fi
chmod 600 "$OUT"                                            # reset for the helper attempt
# The helper chmod must REFUSE (no-follow) and leave the outside mode unchanged.
set +e; python3 "$HELPER" chmod "$HUB2" "$LN" 700 >/dev/null 2>&1; hc=$?; set -e
if [ "$hc" -eq 0 ]; then echo "FAIL: helper chmod followed a symlink target (did not refuse)"; exit 1; fi
if [ "$(mode_of "$OUT")" != "600" ]; then echo "FAIL: helper chmod changed the OUTSIDE file's mode through a symlink (got $(mode_of "$OUT"))"; exit 1; fi

# ---- Negative+baseline unlink: a symlink DIRECTORY component ----
HUB3="$TMP/hub3"; mkdir -p "$HUB3/$HP/skills"
OUTD="$TMP/outdir"; mkdir -p "$OUTD"; echo keep > "$OUTD/victim.md"
ln -s "$OUTD" "$HUB3/$HP/skills/z"                          # a symlink dir component
REL3="$HP/skills/z/victim.md"
# Baseline: a plain rm FOLLOWS the symlink dir and removes the outside file.
cp "$OUTD/victim.md" "$TMP/victim.bak"
rm -f "$HUB3/$REL3"
if [ -e "$OUTD/victim.md" ]; then
  echo "FAIL: baseline plain rm did NOT follow the symlink dir - fixture not follow-vulnerable, test vacuous"; exit 1
fi
cp "$TMP/victim.bak" "$OUTD/victim.md"                      # restore for the helper attempt
# The helper unlink must REFUSE (no-follow parent) and leave the outside file.
set +e; python3 "$HELPER" unlink "$HUB3" "$REL3" >/dev/null 2>&1; hu=$?; set -e
if [ "$hu" -eq 0 ]; then echo "FAIL: helper unlink followed a symlink dir component (did not refuse)"; exit 1; fi
if [ ! -e "$OUTD/victim.md" ]; then echo "FAIL: helper unlink removed the OUTSIDE file through a symlink dir component"; exit 1; fi

echo "PASS: test_safe_io_chmod_unlink_nofollow"
