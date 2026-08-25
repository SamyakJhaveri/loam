#!/usr/bin/env bash
# test_hub_ci_discovery_complete.sh  (Codex round 5, R5-H1)
# Check 2 must run EVERY git-tracked hook test. The old `grep -z ... | sort -z >
# list || true` swallowed a partial-pipeline failure: a broken grep/sort could
# leave a non-empty PARTIAL list and the `|| true` let the gate proceed on it,
# so a tracked hook test silently never ran. The fix reads the checked ls-files
# NUL file directly (no grep/sort/|| true), so discovery is all-or-fail.
#
# Fixture: two tracked tests, each writing a marker when run. A `sort` shim
# (active only for the hub-ci run) emits ONLY the first NUL record then exits 1 -
# the exact partial-output-plus-failure the old code swallowed. The second test
# must still run (its marker present); the old pipeline drops it.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks" "$TMP/shim"
cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/verify-template.sh"
printf '#!/usr/bin/env bash\necho "Total warnings: 0"\necho "ALL OK"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
H="$TMP/cultivation/marketplace/sam-cc-setup/hooks"
# Both tests pass; each records that it ran. ls-files sorts, so test_aaa is the
# first NUL record the shim keeps and test_zzz is the one a partial sort drops.
printf 'import os,sys\nopen(os.environ["RANDIR"]+"/aaa","w").write("x")\nsys.exit(0)\n' > "$H/test_aaa.py"
printf 'import os,sys\nopen(os.environ["RANDIR"]+"/zzz","w").write("x")\nsys.exit(0)\n' > "$H/test_zzz.py"
chmod +x "$TMP/bin/"*.sh
# Partial-failure sort shim: pass through the first NUL record, then fail.
cat > "$TMP/shim/sort" <<'SORTSHIM'
#!/usr/bin/env bash
IFS= read -r -d '' first && printf '%s\0' "$first"
exit 1
SORTSHIM
chmod +x "$TMP/shim/sort"

"$REALGIT" -C "$TMP" init -q
"$REALGIT" -C "$TMP" add -A
RANDIR="$TMP/ran"; mkdir -p "$RANDIR"

set +e
out="$(PATH="$TMP/shim:$PATH" RANDIR="$RANDIR" bash "$TMP/bin/hub-ci.sh" 2>&1)"
rc=$?
set -e

# The completeness property: BOTH tracked tests ran, whatever the sort shim did.
if [ ! -f "$RANDIR/aaa" ]; then echo "FAIL: test_aaa.py never ran (fixture broken?)"; echo "$out"; exit 1; fi
if [ ! -f "$RANDIR/zzz" ]; then
  echo "FAIL: test_zzz.py was NOT run - the gate accepted a PARTIAL tracked-test list"; echo "$out"; exit 1
fi
# And with both tracked tests passing, the gate is green.
if [ "$rc" -ne 0 ]; then echo "FAIL: gate red though both tracked tests pass"; echo "$out"; exit 1; fi

echo "PASS test_hub_ci_discovery_complete.sh"
