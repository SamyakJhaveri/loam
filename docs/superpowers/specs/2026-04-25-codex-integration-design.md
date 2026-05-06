# Codex CLI Integration for ParBench Cross-Model Review

**Date:** 2026-04-25
**Status:** Design approved, pending implementation

## Problem

Claude Code is the sole AI agent working on ParBench. All code, analysis, and documentation is produced and reviewed within the same model family. This creates a single-point-of-failure for correctness — sycophancy patterns, blind spots, and rationalization can go undetected. For NeurIPS 2026 defensibility, an independent cross-model review layer is needed.

## Solution

Configure the already-installed Codex CLI (GPT-5.4) with project context and review profiles so it can independently review Claude's work on demand.

## Deliverables

### 1. AGENTS.md

A project-root file that gives Codex the same situational awareness CLAUDE.md gives Claude. Under 150 lines. Contains:

- **Project overview:** 5 benchmark suites, 87 curated specs, NeurIPS 2026 target
- **Architecture table:** specs/, harness/, scripts/, results/, c_augmentation/
- **Key invariants:** manifest append-only, result immutability, KNOWN_FAIL exclusion, run arg verification
- **KNOWN_FAIL list:** 9 specs to exclude from eval batches and pass-rate denominators
- **Build/test commands:** harness verify, eval batch, pytest, schema validation
- **Review guidelines:** what to flag (security, correctness, consistency, immutability violations, HPC correctness)
- **Usage cheat sheet:** scenario-to-command mapping for common review tasks

### 2. .codex/config.toml

Project-level Codex configuration with 3 named profiles:

| Profile | Effort | Use case |
|---------|--------|----------|
| `code-review` | medium | Standard review of uncommitted changes |
| `results-audit` | high | Audit eval result JSONs for consistency |
| `deep-review` | xhigh | Adversarial review challenging design decisions |

Default model: gpt-5.4. Tracked in git (shared config, same pattern as .claude/settings.json).

### 3. Hook verification

Verify the existing `codex-review-reminder.sh` pre-commit hook works correctly:
- Fires reminder when `.codex_review_done` sentinel is missing or stale (>30 min)
- Stays silent when sentinel is fresh
- Never blocks (always exits 0)

### 4. Usage workflow

Manual on-demand review triggered by the user. Common patterns:

| Scenario | Command |
|----------|---------|
| Review uncommitted changes | `/codex:rescue review the uncommitted changes` |
| Adversarial review | `/codex:adversarial-review` |
| Audit eval results | `codex exec -p results-audit -s read-only "audit results/evaluation/"` |
| Standard code review | `/codex:review` |

## Non-goals

- No automated gates (review is advisory, not blocking)
- No custom Codex skills (AGENTS.md + profiles are sufficient for on-demand use)
- No changes to the existing validation loop or pre-commit hooks

## Verification

1. AGENTS.md under 150 lines and under 32 KiB
2. Codex recognizes project context when asked
3. All 3 profiles load without config errors
4. Hook fires reminder when sentinel is missing
5. `/validate` passes before commit
