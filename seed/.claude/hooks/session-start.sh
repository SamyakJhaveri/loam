#!/usr/bin/env bash
# SessionStart hook — inject framework brief synchronously before the model's
# first turn. Based on Superpowers' session-start pattern, which reports
# improvements in skill activation reliability when a brief is injected
# rather than relying on description-match alone.
#
# Claude Code feeds this hook's stdout into the session context.

set -euo pipefail

# Count by SKILL.md, not by directory (known-issues.md): a bare dir count inflates
# the number if a support/bundle dir without a SKILL.md ever lands under skills/.
SKILL_COUNT=$(find -L .claude/skills -mindepth 2 -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')

cat <<BRIEF
=== loam session brief ===

You are working in a project bootstrapped from Loam.

CORE SKILLS (.claude/skills/ — ${SKILL_COUNT} total):
  Daily loop:    catchup, feature-dev, fix-bug, multi-review, validate, commit, pr, handoff
  Ship pipeline: ship (orchestrates critique→validate→commit→PR)
  Knowledge:     researcher, dream
  Framework:     create-skill, template-sync, scaffold-context
  Quality gate:  session-critique, techdebt
  Spec workflow: gen-spec
  Agent tooling: agent-team
  Specialized:   critique-swarm, render-gate, auto-phase (invoke with /name)

PIPELINE GATE: /validate is non-negotiable before every commit. The pre-commit
hook enforces a .validation_passed sentinel. Critical ordering:
  Implement → /session-critique → /validate (Pipeline Gate) → /commit → /pr
  Use /ship to enforce this ordering automatically.

CONTEXT ROUTING (.claude/rules/):
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

# Dream-due check (sole location — former dream-hook.sh Stop hook was removed
# because Stop hook stdout is not surfaced to users in Claude Code)
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
LOCAL_PATHS="$PROJECT_ROOT/.claude/.local-paths"
MEMORY_DIR="$(grep '^MEMORY_DIR=' "$LOCAL_PATHS" 2>/dev/null | cut -d= -f2)"
if [ -z "$MEMORY_DIR" ]; then
    PROJ_KEY=$(echo -n "$PROJECT_ROOT" | (md5sum 2>/dev/null || md5) | cut -c1-16)
    MEMORY_DIR="$HOME/.claude/projects/$PROJ_KEY/memory"
fi
LAST_DREAM="$MEMORY_DIR/.last-dream"

SHOULD_DREAM=false
if [ ! -f "$LAST_DREAM" ]; then
    SHOULD_DREAM=true
else
    LAST_TS=$(head -1 "$LAST_DREAM")
    LAST_EPOCH=$(python3 -c "import sys; from datetime import datetime; print(int(datetime.fromisoformat(sys.argv[1].replace('Z','+00:00')).timestamp()))" "$LAST_TS" 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    HOURS_SINCE=$(( (NOW_EPOCH - LAST_EPOCH) / 3600 ))
    if [ "$HOURS_SINCE" -ge 24 ]; then
        SHOULD_DREAM=true
    fi
fi

if [ "$SHOULD_DREAM" = true ]; then
    echo ""
    echo "NOTE: Memory consolidation is due (24+ hours since last /dream)."
    echo "Run /dream when convenient — see .claude/skills/dream/SKILL.md."
fi
