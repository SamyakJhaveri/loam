# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-09)

**Core value:** Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.
**Current focus:** Phase 1: Pipeline Testing & Uniformity

## Current Position

Phase: 1 of 4 (Pipeline Testing & Uniformity)
Status: In progress
Last activity: 2026-04-09 -- Phase 1a complete: 104 spec_loader tests passing (32 unit + 71 integration + 1 degenerate-behavior doc test); conftest.py added for integration auto-skip

Progress: [###░░░░░░░] ~15% (Phase 1a spec loading complete: 103 tests passing; Phase 1b-1e pending)

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Campaign separation via `campaign_for()` helper on existing fields -- no folder restructuring
- AskSage is BLOCKED -- do not speculatively build adapter
- Portability (hardcoded compiler paths in specs) deferred to post-NeurIPS
- 4-phase plan replaces old 6-phase, 26-requirement structure

### Blockers/Concerns

- AskSage blocked on Le providing API docs/credentials (affects Phase 2-3)
- NeurIPS deadline May 1, 2026 -- hard constraint on Phase 4

## Session Continuity

Last session: 2026-04-09
Stopped at: Planning docs rewritten to 4-phase structure; Phase 1 execution starting
Resume file: None
