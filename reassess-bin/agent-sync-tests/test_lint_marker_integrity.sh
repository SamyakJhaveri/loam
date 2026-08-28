#!/usr/bin/env bash
# test_lint_marker_integrity.sh  (Codex H10)
# The "Total warnings: N" marker is now load-bearing: hub-ci trusts it as proof
# the linter scanned. So the marker must NOT print after a partial or empty scan.
# The round-1 guard only caught a MISSING directory; an existing-but-EMPTY root
# (or a find discovery error) still printed "Total warnings: 0" exit 0. The linter
# must fail closed (no marker) unless every requested root yielded >=1 SKILL.md.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/bin"
cp "$REAL_BIN/lint-skill-descriptions.sh" "$TMP/bin/lint-skill-descriptions.sh"
cp "$REAL_BIN/lib.sh"                      "$TMP/bin/lib.sh"
chmod +x "$TMP/bin/lint-skill-descriptions.sh"

# --- NEGATIVE: marketplace root EXISTS but holds zero SKILL.md ---------------
mkdir -p "$TMP/cultivation/marketplace/empty-plugin"   # exists, no SKILL.md anywhere
set +e; out="$(bash "$TMP/bin/lint-skill-descriptions.sh" marketplace 2>&1)"; rc=$?; set -e
if [ "$rc" -eq 0 ]; then echo "FAIL: linter exited 0 on an empty (SKILL.md-less) root - marker would lie"; echo "$out"; exit 1; fi
if grep -qE '^Total warnings: [0-9]+' <<<"$out"; then echo "FAIL: linter printed a completion marker after an empty scan"; echo "$out"; exit 1; fi

# --- POSITIVE: a real SKILL.md present -> scans, prints the marker -----------
mkdir -p "$TMP/cultivation/marketplace/real-plugin/skills/foo"
cat > "$TMP/cultivation/marketplace/real-plugin/skills/foo/SKILL.md" <<'MD'
---
name: foo
description: Use when you need a foo. NOT for bar. This is a sufficiently long description.
---
body
MD
set +e; out2="$(bash "$TMP/bin/lint-skill-descriptions.sh" marketplace 2>&1)"; set -e
if ! grep -qE '^Total warnings: [0-9]+' <<<"$out2"; then echo "FAIL: linter did not print the marker on a real scan"; echo "$out2"; exit 1; fi

echo "PASS test_lint_marker_integrity.sh"
