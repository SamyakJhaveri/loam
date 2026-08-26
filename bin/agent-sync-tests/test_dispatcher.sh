#!/usr/bin/env bash
# test_dispatcher.sh
# L5: bin/agent-sync.sh (the documented entry point) had zero coverage - every test
# invoked agent-sync-scan.sh directly. Three mutations (dropping "$@", typoing the
# target, replacing the file with `exit 0`) all left the suite green. A dropped "$@"
# would turn "agent-sync.sh scan --bootstrap-bases" into a full interactive scan.
# These smoke tests exercise the scan + prune subcommands and, critically, "$@"
# forwarding (scan --bootstrap-bases must actually bootstrap).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPATCH="$SCRIPT_DIR/../agent-sync.sh"
HP="cultivation/marketplace/sam-cc-setup"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ---- scan subcommand reached: a no-op fixture prints "No changes" ----
mkdir -p "$TMP/hub/$HP/skills/keep"
echo "same" > "$TMP/hub/$HP/skills/keep/S.md"
(cd "$TMP/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$TMP/proj/.claude/skills/keep"
echo "same" > "$TMP/proj/.claude/skills/keep/S.md"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=3" > "$TMP/hub/.sync-state"

cd "$TMP/proj"
set +e
out_scan=$(printf '' | SAM_CC_HUB_REPO="$TMP/hub" bash "$DISPATCH" scan 2>&1)
rc_scan=$?
set -e
if [ "$rc_scan" -ne 0 ]; then echo "FAIL(scan): dispatcher scan exit $rc_scan"; echo "$out_scan"; exit 1; fi
if ! echo "$out_scan" | grep -qF "No changes"; then
  echo "FAIL(scan): dispatcher did not reach agent-sync-scan.sh"; echo "$out_scan"; exit 1; fi

# ---- "$@" forwarding: scan --bootstrap-bases must actually bootstrap ----
# A dropped "$@" would run a full interactive scan and never print "bootstrap:".
set +e
out_boot=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$DISPATCH" scan --bootstrap-bases 2>&1 </dev/null)
rc_boot=$?
set -e
if [ "$rc_boot" -ne 0 ]; then echo "FAIL(fwd): dispatcher scan --bootstrap-bases exit $rc_boot"; echo "$out_boot"; exit 1; fi
if ! echo "$out_boot" | grep -qE "^bootstrap: [0-9]+ bases recorded"; then
  echo "FAIL(fwd): --bootstrap-bases was not forwarded ('\$@' dropped?)"; echo "$out_boot"; exit 1; fi
cd - >/dev/null

# ---- prune subcommand reached: a travels orphan is offered ----
P="$(mktemp -d)"
mkdir -p "$P/hub/$HP/skills/gone"
echo "orphan" > "$P/hub/$HP/skills/gone/S.md"
(cd "$P/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$P/proj/.claude/reference"
{ printf 'path\tkind\tverdict\treason\trequires\n'; printf 'skills/gone/S.md\tfile\ttravels\tretired\t\n'; } > "$P/proj/.claude/reference/portability-manifest.tsv"
(cd "$P/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$P/proj"
set +e
out_prune=$(printf 'n\n' | SAM_CC_HUB_REPO="$P/hub" bash "$DISPATCH" prune 2>&1)
rc_prune=$?
set -e
cd - >/dev/null
rm -rf "$P"
if [ "$rc_prune" -ne 0 ]; then echo "FAIL(prune): dispatcher prune exit $rc_prune"; echo "$out_prune"; exit 1; fi
if ! echo "$out_prune" | grep -qF "Hub file with no project source: sam-cc-setup/skills/gone/S.md"; then
  echo "FAIL(prune): dispatcher did not reach agent-sync-prune.sh"; echo "$out_prune"; exit 1; fi

# ---- unknown subcommand: usage + exit 1 ----
set +e
out_bad=$(bash "$DISPATCH" nonsense 2>&1)
rc_bad=$?
set -e
if [ "$rc_bad" -eq 0 ]; then echo "FAIL(usage): unknown subcommand exited 0"; echo "$out_bad"; exit 1; fi
if ! echo "$out_bad" | grep -qF "usage: agent-sync.sh"; then
  echo "FAIL(usage): no usage message for an unknown subcommand"; echo "$out_bad"; exit 1; fi

echo "PASS: test_dispatcher"
