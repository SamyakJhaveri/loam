#!/usr/bin/env bash
# test_hub_ci_discovery_strict.sh  (Codex H1)
# Hub hook-test discovery must fail LOUD, not pass silently. Two broken-checkout
# states that a naive `done < <(find ...)` + warn-on-zero lets through:
#   leg1: the hub plugin directory is missing entirely.
#   leg2: the plugin dir exists but ships zero test_*.py.
# Both are broken checkouts, not quiet days - hub-ci must record_fail, not warn.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

base() { # build bin/ with all OTHER checks passing; caller sets up the plugin tree
  rm -rf "${TMP:?}/bin" "${TMP:?}/cultivation"
  mkdir -p "$TMP/bin"
  cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
  cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
  printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/verify-template.sh"
  printf '#!/usr/bin/env bash\necho "Total warnings: 0"\necho "ALL OK"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
  chmod +x "$TMP/bin/"*.sh
}
run() { git -C "$TMP" init -q 2>/dev/null || true; git -C "$TMP" add -A; set +e; out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"; rc=$?; set -e; }

# --- leg1: plugin dir missing entirely -> FAIL ------------------------------
base   # no cultivation/ at all
run
if [ "$rc" -eq 0 ]; then echo "FAIL leg1: hub-ci exited 0 with the hub plugin dir missing"; echo "$out"; exit 1; fi
if ! grep -qiE 'plugin|discover|sam-cc-setup' <<<"$out"; then
  echo "FAIL leg1: report does not name the missing/undiscoverable plugin"; echo "$out"; exit 1
fi

# --- leg2: plugin dir present but zero test_*.py -> FAIL --------------------
base
mkdir -p "$TMP/cultivation/marketplace/sam-cc-setup/hooks"   # exists, but empty of tests
run
if [ "$rc" -eq 0 ]; then echo "FAIL leg2: hub-ci exited 0 with zero hub hook tests discovered"; echo "$out"; exit 1; fi
if ! grep -qiE 'no .*hook|zero|discover' <<<"$out"; then
  echo "FAIL leg2: report does not flag zero discovered tests"; echo "$out"; exit 1
fi

# --- sanity: one passing test present -> gate green -------------------------
base
mkdir -p "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
printf 'import sys\nsys.exit(0)\n' > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
run
if [ "$rc" -ne 0 ]; then echo "FAIL sanity: hub-ci failed although a passing hook test was discovered"; echo "$out"; exit 1; fi

echo "PASS test_hub_ci_discovery_strict.sh"
