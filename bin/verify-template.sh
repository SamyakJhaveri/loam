#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
#
# v3.0 seed-subdirectory: Copier renders from seed/. The repo root has a
# symlink .claude → seed/.claude for local dev experience. This script
# checks invariants that protect the structural properties:
# 1. The seed/ subdirectory exists and .claude symlink resolves.
# 2. Every SKILL.md parses as agentskills.io-conformant (name + description).
# 3. Copier render produces a project whose .claude/ is structurally valid
#    in both default and research-flavor variants.
# 4. Template-author working files do not leak into rendered projects.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cd "$TEMPLATE_ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "OK: $*"; }

# --- Invariant 1: seed/ subdirectory exists ---------------------------------
test -d seed || fail "seed/ subdirectory missing — v3.0 structure broken"
pass "seed/ subdirectory exists"

# --- Invariant 1b: .claude symlink resolves to seed/.claude -----------------
test -L .claude || fail ".claude is not a symlink — expected .claude → seed/.claude"
test -d .claude/skills || fail ".claude symlink does not resolve (seed/.claude/skills missing)"
pass ".claude symlink resolves to seed/.claude"

# --- Invariant 1c: session-start.sh skill count matches actual ---------------
ACTUAL_SKILL_COUNT=$(find seed/.claude/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
BRIEF_SKILL_COUNT=$(grep -oE '[0-9]+ total' seed/.claude/hooks/session-start.sh 2>/dev/null | grep -oE '[0-9]+' || echo "0")
if [[ "$ACTUAL_SKILL_COUNT" != "$BRIEF_SKILL_COUNT" ]]; then
  fail "session-start.sh says $BRIEF_SKILL_COUNT skills but seed/.claude/skills/ has $ACTUAL_SKILL_COUNT"
fi
pass "session-start.sh skill count matches actual ($ACTUAL_SKILL_COUNT)"

# --- Invariant 1e: CLAUDE.md.jinja skill count matches actual ----------------
JINJA_SKILL_COUNT=$(grep -oE '[0-9]+ core skills' seed/CLAUDE.md.jinja 2>/dev/null | grep -oE '[0-9]+' || echo "0")
if [[ "$ACTUAL_SKILL_COUNT" != "$JINJA_SKILL_COUNT" ]]; then
  fail "CLAUDE.md.jinja says $JINJA_SKILL_COUNT core skills but seed/.claude/skills/ has $ACTUAL_SKILL_COUNT"
fi
pass "CLAUDE.md.jinja skill count matches actual ($ACTUAL_SKILL_COUNT)"

# --- Invariant 1d: pre-commit-gate.sh is registered in settings.json --------
if ! grep -q 'pre-commit-gate.sh' seed/.claude/settings.json; then
  fail "pre-commit-gate.sh not registered in settings.json — Pipeline Gate is unenforced"
fi
pass "pre-commit-gate.sh registered in settings.json"

# --- Invariant 2: .claude/settings.json is valid JSON -----------------------
python3 -m json.tool seed/.claude/settings.json >/dev/null || fail "invalid seed/.claude/settings.json"
pass "seed/.claude/settings.json is valid JSON"

# --- Invariant 3: shellcheck on .sh files -----------------------------------
if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh seed/.claude/hooks/*.sh seed/_research/hooks/*.sh 2>&1 || fail "shellcheck failed"
  pass "shellcheck"
else
  echo "SKIP: shellcheck not installed"
fi

# --- Invariant 4: agentskills.io schema (name + description present) --------
SKILL_ERRORS=0
while IFS= read -r -d '' skill; do
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
done < <(find seed/.claude/skills seed/_research/skills cultivation/marketplace -name SKILL.md -print0 2>/dev/null)
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
test ! -d "$TMP/default/seed"                          || fail "default: seed/ leaked into rendered project"
test ! -d "$TMP/default/cultivation"                   || fail "default: cultivation/ leaked into rendered project"
test ! -d "$TMP/default/soil"                          || fail "default: soil/ leaked into rendered project"
test ! -d "$TMP/default/bin"                           || fail "default: bin/ leaked into rendered project"
test ! -f "$TMP/default/.claude/audit.log"             || fail "default: audit.log leaked"
# Top-level CLAUDE.md/README.md should be rendered from .jinja
test -f "$TMP/default/CLAUDE.md"                       || fail "default: CLAUDE.md not rendered from .jinja"
test -f "$TMP/default/README.md"                       || fail "default: README.md not rendered from .jinja"
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

# Research-specific: protect-results.sh must be registered in settings.json
grep -q 'protect-results.sh' "$TMP/research/.claude/settings.json" || fail "research: protect-results.sh not registered in settings.json"
test ! -f "$TMP/research/.claude/hooks/result-immutability.sh" || echo "WARN: research: base result-immutability.sh still present (should be removed by research overlay)"
pass "Copier render (research hook wiring)"

echo "ALL OK"
