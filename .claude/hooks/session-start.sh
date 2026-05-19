#!/usr/bin/env bash
# SessionStart hook — inject framework brief synchronously before the model's
# first turn. Based on Superpowers' session-start pattern, which reports
# improvements in skill activation reliability when a brief is injected
# rather than relying on description-match alone.
#
# Claude Code feeds this hook's stdout into the session context.

set -euo pipefail

cat <<'BRIEF'
=== loam session brief ===

You are working in a project bootstrapped from Loam.

CORE SKILLS (.claude/skills/ — 25 total):
  Daily loop:    catchup, feature-dev, fix-bug, multi-review, validate, commit, pr, handoff
  Memory/style:  know-me, reflect, dream, karpathy-guidelines
  Research:      researcher
  Framework:     create-skill, template-sync, scaffold-context
  Quality gate:  security, scalability, techdebt
  Spec workflow: gen-spec, spec-check, spec-validator
  Agent tooling: agent-team, model-route, session-critique

PIPELINE GATE: /validate is non-negotiable before every commit. The pre-commit
hook enforces a .validation_passed sentinel. Critical ordering:
  Implement → /multi-review → /validate (Pipeline Gate) → commit → push

ICM ROUTING (.claude/rules/):
  L0  CLAUDE.md            always loaded   ~800 tok    "where am I?"
  L1  <subdir>/CONTEXT.md  on entry        ~300 tok    "where do I go?"
  L2  stage contract       per task        200-500 tok "what do I do?"
  L3  path-scoped rules    when matched    varies      "what rules apply?"

The Skip column in CONTEXT.md tables matters more than the Load column.

LAYER TRIAGE before automating: 60/30/10 — deterministic / rule-based /
probabilistic. If the AI portion of a task exceeds ~15%, the design is likely
over-assigning. See .claude/rules/layer-triage.md.

When stuck, default sequence:
  1. Read CLAUDE.md
  2. Read the relevant .claude/rules/X.md (consult the Reference Docs table)
  3. Ask the user before broad exploration sweeps

=== end brief ===
BRIEF

# Inject TEMPLATE-CLAUDE.md (the renamed working CLAUDE.md) into context
# since the file rename means Claude Code no longer auto-loads it.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "$REPO_ROOT" ] && [ -f "$REPO_ROOT/TEMPLATE-CLAUDE.md" ]; then
    echo ""
    echo "=== TEMPLATE-CLAUDE.md (detailed framework map) ==="
    cat "$REPO_ROOT/TEMPLATE-CLAUDE.md"
    echo "=== end TEMPLATE-CLAUDE.md ==="
fi

# Dream-due check: stop-hook stdout is not user-visible in Claude Code, so
# the check is duplicated here in the SessionStart brief (whose stdout
# IS injected into the model's context). The dream-hook.sh Stop hook
# remains in place as a no-op fallback for the log.
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$HOOK_DIR/should-dream.sh" ] && bash "$HOOK_DIR/should-dream.sh" 2>/dev/null; then
    echo ""
    echo "NOTE: Memory consolidation is due (24+ hours since last /dream)."
    echo "Run /dream when convenient — see .claude/skills/dream/SKILL.md."
fi
