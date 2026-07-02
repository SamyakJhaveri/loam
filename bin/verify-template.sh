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
# Cleanup must not decide the exit code: a rendered project can leave a .git the
# teardown rm can't fully empty, and a non-zero last command in an EXIT trap becomes the script's exit status, which
# would mask
# a green run as a failure (the gate would print ALL OK yet exit 1).
trap 'rm -rf "$TMP" 2>/dev/null || true' EXIT

cd "$TEMPLATE_ROOT"

# shellcheck disable=SC2034
LIB_PREFIX="verify"
# shellcheck source=bin/lib.sh
source "$(dirname "$0")/lib.sh"

# --- Invariant 1: seed/ subdirectory exists ---------------------------------
test -d seed || fail "seed/ subdirectory missing — v3.0 structure broken"
pass "seed/ subdirectory exists"

# --- Invariant 1b: .claude symlink resolves to seed/.claude -----------------
test -L .claude || fail ".claude is not a symlink — expected .claude → seed/.claude"
test -d .claude/skills || fail ".claude symlink does not resolve (seed/.claude/skills missing)"
pass ".claude symlink resolves to seed/.claude"

# --- Invariant 1c: pre-commit-gate.sh is registered in settings.json --------
if ! grep -q 'pre-commit-gate.sh' seed/.claude/settings.json; then
  fail "pre-commit-gate.sh not registered in settings.json — Pipeline Gate is unenforced"
fi
pass "pre-commit-gate.sh registered in settings.json"

# --- Invariant 2: .claude/settings.json is valid JSON -----------------------
python3 -m json.tool seed/.claude/settings.json >/dev/null || fail "invalid seed/.claude/settings.json"
pass "seed/.claude/settings.json is valid JSON"

# --- Invariant 3: shellcheck on .sh files -----------------------------------
if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh seed/*.sh seed/.claude/hooks/*.sh seed/_research/hooks/*.sh 2>&1 || fail "shellcheck failed"
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
  if ! extract_frontmatter "$skill" | grep -q '^name:'; then
    echo "FAIL: $skill missing name in front-matter"
    SKILL_ERRORS=$((SKILL_ERRORS+1))
  fi
  if ! extract_frontmatter "$skill" | grep -q '^description:'; then
    echo "FAIL: $skill missing description in front-matter"
    SKILL_ERRORS=$((SKILL_ERRORS+1))
  fi
done < <(find seed/.claude/skills seed/_research/skills cultivation/marketplace -name SKILL.md -print0 2>/dev/null)
[[ $SKILL_ERRORS -eq 0 ]] || fail "$SKILL_ERRORS SKILL.md files violate agentskills.io schema"
pass "agentskills.io schema (every SKILL.md has name + description)"

# --- Invariant 5: skill description quality ---------------------------------
if [[ -x "$SCRIPT_DIR/lint-skill-descriptions.sh" ]]; then
  if bash "$SCRIPT_DIR/lint-skill-descriptions.sh" seed >/dev/null; then
    pass "skill descriptions (seed)"
  else
    fail "seed skill descriptions have lint errors (run: bin/lint-skill-descriptions.sh seed)"
  fi
  bash "$SCRIPT_DIR/lint-skill-descriptions.sh" marketplace >/dev/null 2>&1 || \
    echo "WARN: marketplace skill descriptions have lint warnings (run: bin/lint-skill-descriptions.sh marketplace)"
fi

# --- Invariant 6: skill-count docs + LICENSE (guards the recurring drift) ----
# known-issues.md: count skills by SKILL.md, never by directory. This guard
# fails if any onboarding doc states a "NN core skills" that disagrees with the
# actual SKILL.md count — the exact regression that has recurred across releases.
CORE_SKILLS=$(find seed/.claude/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')
test -f LICENSE || fail "top-level LICENSE missing"
# Scope to current onboarding docs only (docs/*.md — NOT docs/plans|adr|specs,
# which are historical session records that accurately cite past counts).
BAD_COUNTS=$(grep -rniE '[0-9]+ core skills' README.md docs/*.md cultivation/marketplace/README.md 2>/dev/null \
  | grep -viE "(^|[^0-9])$CORE_SKILLS core skills" || true)
if [[ -n "$BAD_COUNTS" ]]; then
  echo "$BAD_COUNTS"
  fail "doc(s) above state a core-skill count != actual ($CORE_SKILLS) — fix them (known-issues.md: count by SKILL.md)"
fi
pass "skill-count docs agree with actual ($CORE_SKILLS core) and LICENSE present"

# --- Invariant 7: no accidental large plain blobs under docs/assets ----------
# docs/assets is kept LFS-free by choice; a demo gif or screenshot committed as a plain
# blob bloats every clone's history. Grandfather the one gif already shipped in
# v1.0.0 (removing it needs a history rewrite); flag any NEW asset >1MB.
BIG_ASSETS=$(git ls-files docs/assets 2>/dev/null | while read -r f; do
  [ -f "$f" ] || continue
  sz=$(wc -c < "$f" | tr -d ' ')
  if [ "$sz" -gt 1048576 ] && [ "$f" != "docs/assets/bootstrap.gif" ]; then echo "  $f (${sz}B)"; fi
done)
if [[ -n "$BIG_ASSETS" ]]; then
  echo "$BIG_ASSETS"
  fail "large non-LFS asset(s) above — optimize to <1MB or use a GitHub Release asset"
fi
pass "no oversized non-LFS assets under docs/assets"

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
# Copier clones the repo at --vcs-ref HEAD before rendering; that clone smudges the
# LFS-tracked docs/diagrams/loam-hero-*.png (~20MB 4K art). The render verification never
# inspects image bytes — and in CI the runner holds only LFS pointers (actions/checkout does
# not fetch LFS by default), so the smudge filter fails and, under `set -o pipefail`, exits 1.
# Skip the smudge: the clone carries pointers, the render still validates structure.
export GIT_LFS_SKIP_SMUDGE=1
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
test -x "$TMP/default/.claude/hooks/superpowers-plan-location.sh" || fail "default: superpowers-plan-location hook missing"
grep -q 'superpowers-plan-location.sh' "$TMP/default/.claude/settings.json" || fail "default: superpowers-plan-location hook not registered"
grep -qF '.superpowers/' "$TMP/default/.gitignore" || fail "default: .superpowers/ not gitignored"
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
test -f "$TMP/research/.claude/rules/research-consistency.md" || fail "research: research-consistency rule missing"
test -f "$TMP/research/CHANGELOG.research.md"          || fail "research: CHANGELOG.research.md not rendered"
test ! -d "$TMP/research/_research"                    || fail "research: _research overlay not cleaned up"
pass "Copier render (research)"

# Research-specific: protect-results.sh must be registered in settings.json
grep -q 'protect-results.sh' "$TMP/research/.claude/settings.json" || fail "research: protect-results.sh not registered in settings.json"
test ! -f "$TMP/research/.claude/hooks/result-immutability.sh" || echo "WARN: research: base result-immutability.sh still present (should be removed by research overlay)"
test -x "$TMP/research/.claude/hooks/superpowers-plan-location.sh" || fail "research: superpowers-plan-location hook missing"
grep -q 'superpowers-plan-location.sh' "$TMP/research/.claude/settings.json" || fail "research: superpowers-plan-location hook not registered"
grep -qF '.superpowers/' "$TMP/research/.gitignore" || fail "research: .superpowers/ not gitignored"
pass "Copier render (research hook wiring)"

echo "ALL OK"
