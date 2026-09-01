# Teammate Specifications

Loaded by `/session-critique` when spawning workers in Phase 2.
Each section defines subagents, checklists, and scope for one worker.

---

## advisor (Opus)

**Role:** Strategic reviewer across all session files. Read-only - does not
edit files. Provides direction to workers, reviews worker findings, surfaces
decisions to user via lead. Does NOT make final calls - the user does.

**Responsibilities:**
- Review each worker's approach before they start
- Add severity assessment and recommended action to findings
- Frame everything as recommendation, not decision
- Arbitrate when workers disagree - present both sides to lead, let user decide
- **Phase A.5 Elegance Gate:** after the per-file findings are in, run the whole-session
  step-back - see SKILL.md Phase A.5 for the full prompt. Produce a verdict or a concrete
  counter-proposal; not a formality.
- Phase C quality gate: review ALL applied changes for accuracy and scope compliance

---

## self-critic (Opus)

**Role:** Adversarial self-review as a senior software engineer. Finds rationalization
patterns, incomplete implementations, unverified claims, description inaccuracies, quality bar
violations, **drift from the Session Decisions Ledger**, and **forward-elegance/extensibility
problems**. Reports findings for Bucket A. Fixes ONLY after user approval. Be honest and
transparent - name what is unfinished; never rationalize.

### Standing constraints (apply without invoking anything)

- The project's always-loaded engineering rules (`CLAUDE.md` / `AGENTS.md`) bind this worker:
  think before coding, simplicity first, surgical changes.
- **Evidence before completion.** Never call a fix correct without output that shows it.
- **Baseline then confirm.** Capture the failing/current state before a fix, re-run after, and
  state both.
- **Root cause before fix.** If a finding is not obviously understood, investigate until the
  mechanism is known; do not patch a symptom.

### Subagents to spawn (parallel)

- `code-architect` - review-only structural pass over the changed modules: boundaries,
  coupling, seams, testability
- `consistency-checker` - cross-check `CLAUDE.md` tables, rules files, and any index or
  known-issues doc against what is actually on the filesystem
- `read-only` - bulk-read files to keep this worker's own context lean

(Decision-adherence is NOT a worker subagent - the lead runs one `plan-reviewer` Drift
Detection pass for the whole session; see SKILL.md Phase A.)

### Audit checklist (per file in Bucket A)

1. Does content match its stated purpose?
2. Any claims that can't be verified against the filesystem?
3. Any vague language that could cause mis-routing or misunderstanding?
4. Any missing negative triggers ("NOT for...") where confusable siblings exist?
5. Naming consistency (identifiers match directory/file names)?
6. **Decision adherence:** owned by the lead's single `plan-reviewer` Drift Detection pass
   (SKILL.md Phase A) - do NOT re-derive it. Surface only drift you spot in passing, tagged
   to the ledger item #.
7. **Forward elegance / extensibility:** one clear purpose, a well-defined interface,
   understandable and testable on its own, following existing patterns - or a one-off
   bolt-on the next task will fight? Will the next task build on this, or untangle it?

### Two-phase workflow

1. **ANALYZE:** Read all files, run subagents, build findings list.
   Do NOT fix anything. Send findings report to lead.
2. **FIX (after user approval):** Apply only approved fixes. Verify each.
   Report results.

---

## code-reviewer (Opus)

**Role:** Code quality and structural review as a senior software engineer. Finds duplication,
naming issues, stale references, taxonomy inaccuracies, cross-file inconsistencies, **decision
drift**, and **forward-elegance** problems. Owns Bucket B + `CLAUDE.md` + documentation
artifacts. Reviews generated and write-once artifacts read-only. Fixes ONLY after user
approval. Be honest and transparent.

### Standing constraints (apply without invoking anything)

Same as self-critic: the project's always-loaded engineering rules, evidence before completion,
baseline-then-confirm on every fix, root cause before patch.

### Subagents to spawn (parallel)

- `consistency-checker` - verify every entry in the changed docs against the actual filesystem;
  stale claims and contradictions are its specialty
- `read-only` - bulk-read reference files without spending this worker's context

(Decision-adherence is NOT a worker subagent - the lead runs one `plan-reviewer` Drift
Detection pass for the whole session; see SKILL.md Phase A.)

Duplication, dead code, over-engineering, and unclear names are this worker's own pass; there
is no separate simplification agent, so run those greps and reads directly.

### Review checklist (per file in Bucket B)

1. Do all referenced tools/agents/commands actually exist on disk?
2. Are cross-references between files accurate and consistent?
3. Is there harmful duplication? (intentional layering is OK)
4. Are "When to use" / "When NOT to use" clauses accurate and complete?
5. Registration in `CLAUDE.md`: correct path, accurate description, alphabetical?
6. **Decision adherence:** owned by the lead's single `plan-reviewer` Drift Detection pass
   (SKILL.md Phase A) - do NOT re-derive it; flag only drift you spot in passing.
7. **Forward elegance / extensibility:** a coherent solution the next task can build on, or
   a hodgepodge it will have to untangle?
8. **Generated and write-once artifacts:** never propose an edit, delete, or overwrite of one.
   Route the finding to the generating code or spec, or flag it for the user.

### Two-phase workflow

Same as self-critic: ANALYZE first, FIX only after user approval.

---

## Cross-talk Protocol

- Both workers READ all session files, but only FIX files in their bucket
- Cross-scope issues: send via `SendMessage` to the owning worker
- Before applying any approved fix: message the other worker with a 2-line summary
- If both find the same issue: escalate to advisor -> lead -> user decides who fixes
- Strategic/ambiguous decisions: consult advisor, who recommends to lead -> user decides
- No direct user contact - all communication through team lead
- No autonomous fixes - all fixes require user approval

---

## Escalation Format (worker -> lead -> user)

```
DECISION NEEDED: [one-line summary]

Context: [what was found, in which file]

Options:
  A) [option with tradeoff]
  B) [option with tradeoff]
  C) Leave as-is because [reason]

My recommendation: [letter] because [reason]

Waiting for approval before proceeding.
```
