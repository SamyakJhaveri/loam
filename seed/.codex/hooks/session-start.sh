#!/usr/bin/env bash
# Codex SessionStart hook. Emits a compact project brief using Codex-native paths.

set -euo pipefail

SKILL_COUNT=$(find -L .agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')

cat <<BRIEF
=== Codex session brief ===

CORE SKILLS (.agents/skills curated Codex view; ${SKILL_COUNT} visible):
  Daily loop:    catchup, feature-dev, fix-bug, multi-review, validate, commit, pr, handoff
  Ship pipeline: run critique-swarm/multi-review -> validate -> commit -> pr manually
  Knowledge:     catchup, dream; use Codex web/search directly for current external research
  Quality gate:  validate, multi-review, critique-swarm, techdebt
                 session-critique fallback: docs/codex-session-critique.md
  Agent tooling: .codex/agents wrappers; paper-assembly-codex is a root-session skill

PIPELINE GATE: /validate is non-negotiable before every commit. The Codex
PreToolUse policy enforces a .validation_passed sentinel for git commit.

Codex-native setup:
  .codex/config.toml      MCP and agent defaults
                           includes GitHub streamable HTTP MCP
  .codex/hooks.json       lifecycle hooks
  .codex/rules/           command execution policy
  .codex/agents/          custom agent wrappers

When stuck, default sequence:
  1. Read AGENTS.md
  2. Read the relevant .claude/rules/X.md
  3. Ask before broad exploration sweeps

=== end brief ===
BRIEF
