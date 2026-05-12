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

for flavor in research software-eng; do
  bin/init-project.sh "$TMP/$flavor" --flavor "$flavor" >/dev/null
  test -f "$TMP/$flavor/.claude/settings.json"   || { echo "FAIL: $flavor missing settings.json"; exit 1; }
  python3 -m json.tool "$TMP/$flavor/.claude/settings.json" >/dev/null || { echo "FAIL: $flavor invalid settings.json"; exit 1; }
  echo "OK: flavor $flavor"
done

# Rule placement assertions
test -f "$TMP/research/.claude/rules/python.md"          || { echo "FAIL: research missing python.md"; exit 1; }
test -f "$TMP/research/.claude/rules/tech-stack.md"       || { echo "FAIL: research missing tech-stack.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/architecture.md"   || { echo "FAIL: research has architecture.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/frontend-design.md" || { echo "FAIL: research has frontend-design.md"; exit 1; }
echo "OK: research rules"

for rule in python.md tech-stack.md architecture.md frontend-design.md; do
  test -f "$TMP/software-eng/.claude/rules/$rule" || { echo "FAIL: software-eng missing $rule"; exit 1; }
done
echo "OK: software-eng rules"

# HPC skills are now part of research
test -f "$TMP/research/.claude/skills/cuda-omp-translator/SKILL.md" || { echo "FAIL: research missing cuda-omp-translator"; exit 1; }
test -f "$TMP/research/.claude/skills/hpc-code-reviewer/SKILL.md"   || { echo "FAIL: research missing hpc-code-reviewer"; exit 1; }
echo "OK: research HPC skills"

# Duplication guard — python.md and tech-stack.md must be identical across flavors
cmp --silent "$TEMPLATE_ROOT/flavors/research/rules/python.md" "$TEMPLATE_ROOT/flavors/software-eng/rules/python.md" \
  || { echo "FAIL: python.md diverged between research and software-eng"; exit 1; }
cmp --silent "$TEMPLATE_ROOT/flavors/research/rules/tech-stack.md" "$TEMPLATE_ROOT/flavors/software-eng/rules/tech-stack.md" \
  || { echo "FAIL: tech-stack.md diverged between research and software-eng"; exit 1; }
echo "OK: duplicated rules identical"

# Skill placement assertions (Session H) — skills in generic core, available to all bootstraps
SESSION_H_SKILLS="council create-skill decision-matrix frontend-design know-me process-optimizer prompt-improver researcher scalability security self-healing sop-writer weekly-review workflow-mapper"
for skill in $SESSION_H_SKILLS; do
  test -d "$TMP/no-flavor/.claude/skills/$skill"    || { echo "FAIL: no-flavor missing skill $skill"; exit 1; }
  test -d "$TMP/research/.claude/skills/$skill"     || { echo "FAIL: research missing skill $skill"; exit 1; }
  test -d "$TMP/software-eng/.claude/skills/$skill" || { echo "FAIL: software-eng missing skill $skill"; exit 1; }
done
echo "OK: Session H skills in generic core"

echo "ALL OK"
