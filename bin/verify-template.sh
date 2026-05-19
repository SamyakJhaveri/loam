#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
#
# v2.0 single-tree: the repo itself is the Copier template. This script
# checks invariants that protect the rework's structural properties:
# 1. The legacy template/ subdir does not return.
# 2. The mirror cannot drift (no template/.claude/ to differ from .claude/).
# 3. Every SKILL.md parses as agentskills.io-conformant (name + description
#    in front-matter).
# 4. Copier render produces a project whose .claude/ is structurally valid
#    in both default and research-flavor variants.
# 5. Template-author working files do not leak into rendered projects.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cd "$TEMPLATE_ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "OK: $*"; }

# --- Invariant 1: single-tree (template/ subdir must not exist) -------------
test ! -d template || fail "template/ subdirectory exists — single-tree invariant broken"
pass "single-tree (no template/ subdir)"

# --- Invariant 1b: TEMPLATE-CLAUDE.md exists (session-start.sh depends on it)
test -f TEMPLATE-CLAUDE.md || fail "TEMPLATE-CLAUDE.md missing — session-start.sh injection will silently fail"
test -s TEMPLATE-CLAUDE.md || fail "TEMPLATE-CLAUDE.md is empty"
pass "TEMPLATE-CLAUDE.md exists and is non-empty"

# --- Invariant 1c: session-start.sh skill count matches actual ---------------
ACTUAL_SKILL_COUNT=$(find .claude/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
BRIEF_SKILL_COUNT=$(grep -oE '[0-9]+ total' .claude/hooks/session-start.sh 2>/dev/null | grep -oE '[0-9]+' || echo "0")
if [[ "$ACTUAL_SKILL_COUNT" != "$BRIEF_SKILL_COUNT" ]]; then
  fail "session-start.sh says $BRIEF_SKILL_COUNT skills but .claude/skills/ has $ACTUAL_SKILL_COUNT"
fi
pass "session-start.sh skill count matches actual ($ACTUAL_SKILL_COUNT)"

# --- Invariant 1d: pre-commit-gate.sh is registered in settings.json --------
if ! grep -q 'pre-commit-gate.sh' .claude/settings.json; then
  fail "pre-commit-gate.sh not registered in settings.json — Pipeline Gate is unenforced"
fi
pass "pre-commit-gate.sh registered in settings.json"

# --- Invariant 2: .claude/settings.json is valid JSON -----------------------
python3 -m json.tool .claude/settings.json >/dev/null || fail "invalid .claude/settings.json"
pass ".claude/settings.json is valid JSON"

# --- Invariant 3: shellcheck on .sh files -----------------------------------
if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh .claude/hooks/*.sh _research/hooks/*.sh 2>&1 || fail "shellcheck failed"
  pass "shellcheck"
else
  echo "SKIP: shellcheck not installed"
fi

# --- Invariant 4: agentskills.io schema (name + description present) --------
SKILL_ERRORS=0
while IFS= read -r -d '' skill; do
  # Extract front-matter (between first --- and second ---)
  if ! head -20 "$skill" | grep -q '^---$'; then
    echo "WARN: $skill has no front-matter"
    SKILL_ERRORS=$((SKILL_ERRORS+1))
    continue
  fi
  if ! awk '/^---$/{n++; if(n==2) exit} n==1 && /^name:/{found=1} END{exit !found}' "$skill"; then
    echo "FAIL: $skill missing name in front-matter"
    SKILL_ERRORS=$((SKILL_ERRORS+1))
  fi
  if ! awk '/^---$/{n++; if(n==2) exit} n==1 && /^description:/{found=1} END{exit !found}' "$skill"; then
    echo "FAIL: $skill missing description in front-matter"
    SKILL_ERRORS=$((SKILL_ERRORS+1))
  fi
done < <(find .claude/skills _research/skills seed-skills -name SKILL.md -print0 2>/dev/null)
[[ $SKILL_ERRORS -eq 0 ]] || fail "$SKILL_ERRORS SKILL.md files violate agentskills.io schema"
pass "agentskills.io schema (every SKILL.md has name + description)"

# --- Invariant 5: skill description quality (warn-only) ---------------------
if [[ -x "$SCRIPT_DIR/lint-skill-descriptions.sh" ]]; then
  if bash "$SCRIPT_DIR/lint-skill-descriptions.sh" >/dev/null 2>&1; then
    pass "skill descriptions"
  else
    echo "WARN: skill description lint has warnings (run bin/lint-skill-descriptions.sh for details)"
  fi
fi

# --- Copier render tests ----------------------------------------------------
COPIER_CMD=""
if command -v copier >/dev/null 2>&1; then
  COPIER_CMD="copier"
elif command -v uvx >/dev/null 2>&1; then
  COPIER_CMD="uvx copier"
fi

if [[ -z "$COPIER_CMD" ]]; then
  echo "SKIP: copier not installed; skipping render tests"
  echo "ALL OK"
  exit 0
fi

echo "--- Copier render tests ---"
COPIER_FLAGS="--trust --defaults --vcs-ref HEAD"

# Default flavor (is_research=false)
# COPIER_FLAGS contains multiple args that must word-split
# shellcheck disable=SC2086
$COPIER_CMD copy $COPIER_FLAGS --data "project_name=default-test" . "$TMP/default" 2>&1 | tail -5
test -f "$TMP/default/CLAUDE.md"                       || fail "default: CLAUDE.md missing"
test -f "$TMP/default/.claude/settings.json"           || fail "default: .claude/settings.json missing"
test -f "$TMP/default/.claude/rules/L0-budget.md"      || fail "default: L0-budget rule missing"
test -f "$TMP/default/.claude/rules/stage-contract.md" || fail "default: stage-contract rule missing"
test -f "$TMP/default/.claude/hooks/session-start.sh"  || fail "default: session-start hook missing"
test -d "$TMP/default/.claude/skills/validate"         || fail "default: validate skill missing"
test -d "$TMP/default/.claude/skills/template-sync"    || echo "WARN: default: template-sync skill missing (experimental — not blocking)"
test ! -d "$TMP/default/_research"                     || fail "default: _research overlay not cleaned up"
test ! -d "$TMP/default/template"                      || fail "default: template/ leaked"
test ! -d "$TMP/default/seed-skills"                   || fail "default: seed-skills/ leaked into rendered project"
test ! -d "$TMP/default/claude_code_course_files"      || fail "default: course files leaked"
# internal_docs/ is created by _tasks mkdir as a seed dir; check it's empty (no source content propagated)
test -d "$TMP/default/internal_docs"                   || fail "default: internal_docs seed dir missing"
count_internal=$(find "$TMP/default/internal_docs" -type f ! -name .gitkeep 2>/dev/null | wc -l)
[[ "$count_internal" -eq 0 ]]                          || fail "default: internal_docs has $count_internal non-gitkeep files (source leaked)"
test ! -f "$TMP/default/HANDOFF.md.jinja"              || fail "default: HANDOFF.md.jinja not rendered"
# Top-level CLAUDE.md/README.md/HANDOFF.md should be rendered from .jinja
test -f "$TMP/default/CLAUDE.md"                       || fail "default: CLAUDE.md not rendered from .jinja"
test -f "$TMP/default/README.md"                       || fail "default: README.md not rendered from .jinja"
test -f "$TMP/default/HANDOFF.md"                      || fail "default: HANDOFF.md not rendered from .jinja"
test -f "$TMP/default/CONTEXT.md"                      || fail "default: CONTEXT.md not rendered from .jinja"
test -f "$TMP/default/PROJECT-BACKGROUND.md"           || fail "default: PROJECT-BACKGROUND.md not rendered from .jinja"
# CONTEXT.md must carry the 6 ICM L1 anatomy section headers (per .claude/rules/context-md-anatomy.md)
for header in "## What this area is" "## What to Load" "## Folder" "## The Process" "## Skills & Tools" "## What NOT to Do"; do
  grep -qF "$header" "$TMP/default/CONTEXT.md" || fail "default: CONTEXT.md missing section header '$header'"
done
test ! -f "$TMP/default/.claude/audit.log"             || fail "default: audit.log leaked"
pass "Copier render (default)"

# Research flavor (is_research=true)
# COPIER_FLAGS contains multiple args that must word-split
# shellcheck disable=SC2086
$COPIER_CMD copy $COPIER_FLAGS --data "project_name=research-test" --data "is_research=true" . "$TMP/research" 2>&1 | tail -5
test -d "$TMP/research/.claude/skills/paper-write"     || fail "research: paper-write skill missing"
test -d "$TMP/research/.claude/skills/citation-audit"  || fail "research: citation-audit skill missing"
test -f "$TMP/research/.claude/rules/research-memory.md" || fail "research: research-memory rule missing"
test -f "$TMP/research/REFERENCES.md"                  || fail "research: REFERENCES.md not rendered"
test -f "$TMP/research/EXPERIMENT-PROTOCOL.md"         || fail "research: EXPERIMENT-PROTOCOL.md not rendered"
test ! -d "$TMP/research/_research"                    || fail "research: _research overlay not cleaned up"
pass "Copier render (research)"

echo "ALL OK"
