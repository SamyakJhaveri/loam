#!/usr/bin/env bash
# test_hub_ci_skips_untracked.sh  (Codex round 3, FIX 1)
# hub-ci validates the worktree, but release.sh tags COMMITTED objects. So the
# gate must run only git-TRACKED hook tests: a gitignored or untracked test_*.py
# under the plugin would run in the gate yet never ship in the tag (and the mirror
# - the gate could pass on a test the tag omits). Filesystem `find` discovery runs
# it; git-tracked discovery skips it.
#
# Fixture: a TRACKED passing test_ok.py plus an UNTRACKED failing test_evil.py
# that records a marker when it runs. Correct gate: green, marker absent (evil not
# run). find-based gate: runs test_evil -> red + marker present.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/verify-template.sh"
printf '#!/usr/bin/env bash\necho "Total warnings: 0"\necho "ALL OK"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
printf 'import sys\nsys.exit(0)\n' > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
chmod +x "$TMP/bin/"*.sh

# Track everything built so far (test_ok.py is now indexed), THEN drop the
# untracked evil test so it is never added to the index.
"$REALGIT" -C "$TMP" init -q
"$REALGIT" -C "$TMP" add -A
EVIL_MARKER="$TMP/evil_ran"
cat > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_evil.py" <<PY
import os, sys
open(os.environ["EVIL_MARKER"], "w").write("ran")
sys.exit(1)
PY

set +e
out="$(EVIL_MARKER="$EVIL_MARKER" bash "$TMP/bin/hub-ci.sh" 2>&1)"
rc=$?
set -e

if [ -f "$EVIL_MARKER" ]; then
  echo "FAIL: the UNTRACKED test_evil.py was executed by the gate (it is not in the tag)"; echo "$out"; exit 1
fi
if [ "$rc" -ne 0 ]; then
  echo "FAIL: gate is red though the only TRACKED hook test passes (untracked test must be ignored)"; echo "$out"; exit 1
fi
# The tracked test WAS discovered and run.
if ! grep -q 'test_ok.py' <<<"$out"; then
  echo "FAIL: the tracked test_ok.py was not discovered/run"; echo "$out"; exit 1
fi

echo "PASS test_hub_ci_skips_untracked.sh"
