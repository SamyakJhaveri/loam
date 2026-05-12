#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

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
for rule in python.md tech-stack.md architecture.md frontend-design.md; do
  test ! -f "$TMP/no-flavor/.claude/rules/$rule" || { echo "FAIL: $rule leaked to no-flavor"; exit 1; }
done
echo "OK: flavor (none)"

for flavor in research software-eng ml hpc; do
  bin/init-project.sh "$TMP/$flavor" --flavor "$flavor" >/dev/null
  test -f "$TMP/$flavor/.claude/settings.json"   || { echo "FAIL: $flavor missing settings.json"; exit 1; }
  python3 -m json.tool "$TMP/$flavor/.claude/settings.json" >/dev/null || { echo "FAIL: $flavor invalid settings.json"; exit 1; }
  echo "OK: flavor $flavor"
done

# Rule placement assertions (Session D — P0-3)
test -f "$TMP/research/.claude/rules/python.md"          || { echo "FAIL: research missing python.md"; exit 1; }
test -f "$TMP/research/.claude/rules/tech-stack.md"       || { echo "FAIL: research missing tech-stack.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/architecture.md"   || { echo "FAIL: research has architecture.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/frontend-design.md" || { echo "FAIL: research has frontend-design.md"; exit 1; }
echo "OK: research rules"

for rule in python.md tech-stack.md architecture.md frontend-design.md; do
  test -f "$TMP/software-eng/.claude/rules/$rule" || { echo "FAIL: software-eng missing $rule"; exit 1; }
done
echo "OK: software-eng rules"

test -f "$TMP/ml/.claude/rules/python.md"                  || { echo "FAIL: ml missing python.md"; exit 1; }
test -f "$TMP/ml/.claude/rules/tech-stack.md"               || { echo "FAIL: ml missing tech-stack.md"; exit 1; }
test ! -f "$TMP/ml/.claude/rules/architecture.md"           || { echo "FAIL: ml has architecture.md"; exit 1; }
test ! -f "$TMP/ml/.claude/rules/frontend-design.md"        || { echo "FAIL: ml has frontend-design.md"; exit 1; }
echo "OK: ml rules"

test -f "$TMP/hpc/.claude/rules/python.md"                 || { echo "FAIL: hpc missing python.md"; exit 1; }
test -f "$TMP/hpc/.claude/rules/tech-stack.md"              || { echo "FAIL: hpc missing tech-stack.md"; exit 1; }
test ! -f "$TMP/hpc/.claude/rules/architecture.md"          || { echo "FAIL: hpc has architecture.md"; exit 1; }
test ! -f "$TMP/hpc/.claude/rules/frontend-design.md"       || { echo "FAIL: hpc has frontend-design.md"; exit 1; }
echo "OK: hpc rules"

# Duplication guard — all copies of python.md and tech-stack.md must be identical
ref_py=$(md5 -q "$TEMPLATE_ROOT/flavors/research/rules/python.md" 2>/dev/null || echo "MISSING")
ref_ts=$(md5 -q "$TEMPLATE_ROOT/flavors/research/rules/tech-stack.md" 2>/dev/null || echo "MISSING")
if [[ "$ref_py" != "MISSING" ]]; then
  for f in software-eng ml hpc; do
    cmp_py=$(md5 -q "$TEMPLATE_ROOT/flavors/$f/rules/python.md")
    cmp_ts=$(md5 -q "$TEMPLATE_ROOT/flavors/$f/rules/tech-stack.md")
    [[ "$ref_py" == "$cmp_py" ]] || { echo "FAIL: python.md diverged in $f"; exit 1; }
    [[ "$ref_ts" == "$cmp_ts" ]] || { echo "FAIL: tech-stack.md diverged in $f"; exit 1; }
  done
  echo "OK: duplicated rules identical"
fi

echo "ALL OK"
