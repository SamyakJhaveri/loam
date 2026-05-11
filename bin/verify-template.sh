#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

cd "$TEMPLATE_ROOT"

if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh .claude/hooks/*.sh || { echo "FAIL: shellcheck"; exit 1; }
  echo "OK: shellcheck"
else
  echo "SKIP: shellcheck not installed"
fi

bin/init-project.sh "$TMP/no-flavor" >/dev/null
test -f "$TMP/no-flavor/CLAUDE.md"              || { echo "FAIL: no CLAUDE.md (no-flavor)"; exit 1; }
test -f "$TMP/no-flavor/.claude/settings.json"   || { echo "FAIL: no settings.json (no-flavor)"; exit 1; }
python3 -m json.tool "$TMP/no-flavor/.claude/settings.json" >/dev/null || { echo "FAIL: invalid settings.json (no-flavor)"; exit 1; }
test ! -f "$TMP/no-flavor/.claude/audit.log"     || { echo "FAIL: audit.log propagated (no-flavor)"; exit 1; }
echo "OK: flavor (none)"

for flavor in research software-eng ml hpc; do
  bin/init-project.sh "$TMP/$flavor" --flavor "$flavor" >/dev/null
  test -f "$TMP/$flavor/.claude/settings.json"   || { echo "FAIL: $flavor missing settings.json"; exit 1; }
  python3 -m json.tool "$TMP/$flavor/.claude/settings.json" >/dev/null || { echo "FAIL: $flavor invalid settings.json"; exit 1; }
  echo "OK: flavor $flavor"
done

echo "ALL OK"
