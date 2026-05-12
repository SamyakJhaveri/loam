# Teammate Specifications

Loaded by `/session-critique` when spawning workers in Phase 2.
Each section defines skills, subagents, checklists, and scope for one worker.

---

## advisor (Opus, ultrathink)

**Role:** Strategic reviewer across all session files. Read-only — does not
edit files. Provides direction to workers, reviews worker findings, surfaces
decisions to user via lead. Does NOT make final calls — the user does.

**Responsibilities:**
- Review each worker's approach before they start
- Add severity assessment and recommended action to findings
- Frame everything as recommendation, not decision
- Arbitrate when workers disagree — present both sides to lead, let user decide
- Phase 4 quality gate: review ALL applied changes for accuracy and scope compliance

---

## self-critic (Opus)

**Role:** Adversarial self-review. Finds rationalization patterns, incomplete
implementations, unverified claims, description inaccuracies, quality bar
violations. Reports findings for Bucket A. Fixes ONLY after user approval.

### Skills to invoke

- `andrej-karpathy-skills:karpathy-guidelines` — Think Before Coding,
  Simplicity First, Surgical Changes
- `superpowers:verification-before-completion` — evidence before claiming
  any fix is correct
- `superpowers:test-driven-development` — verify state BEFORE each fix
  (baseline), then AFTER (confirm improvement)
- `superpowers:systematic-debugging` — if a finding needs root-cause
  investigation before the fix is obvious

### Subagents to spawn (parallel)

- `diff-reviewer` agent — scan git diff for regressions, partial
  implementations, accidental file changes
- `consistency-checker` agent — cross-check CLAUDE.md tables, rules
  files, known-issues.md against actual filesystem
- `explorer` agent — bulk-read files to keep own context lean

### Audit checklist (per file in Bucket A)

1. Does content match its stated purpose?
2. Any claims that can't be verified against the filesystem?
3. Any vague language that could cause mis-routing or misunderstanding?
4. Any missing negative triggers ("NOT for...") where confusable siblings exist?
5. Naming consistency (identifiers match directory/file names)?

### Two-phase workflow

1. **ANALYZE:** Read all files, run subagents, build findings list.
   Do NOT fix anything. Send findings report to lead.
2. **FIX (after user approval):** Apply only approved fixes. Verify each.
   Report results.

---

## code-reviewer (Sonnet)

**Role:** Code quality and structural review. Finds duplication, naming
issues, stale references, taxonomy inaccuracies, cross-file inconsistencies.
Reports findings for Bucket B + CLAUDE.md. Fixes ONLY after user approval.

### Skills to invoke

- `andrej-karpathy-skills:karpathy-guidelines` — same behavioral guardrails
- `superpowers:verification-before-completion` — same evidence requirement
- `superpowers:test-driven-development` — same before/after verification
- `superpowers:systematic-debugging` — same root-cause protocol

### Subagents to spawn (parallel)

- `code-simplifier` agent — find duplication, dead code, over-engineering,
  unclear names
- `security-scanner` agent — scan for secrets, injection, unsafe patterns
- `explorer` agent — bulk-read reference files to verify entries against
  actual filesystem

### Review checklist (per file in Bucket B)

1. Do all referenced tools/agents/commands actually exist on disk?
2. Are cross-references between files accurate and consistent?
3. Is there harmful duplication? (intentional L2/L3 layering is OK)
4. Are "When to use" / "When NOT to use" clauses accurate and complete?
5. CLAUDE.md registration: correct path, accurate description, alphabetical?

### Two-phase workflow

Same as self-critic: ANALYZE first, FIX only after user approval.

---

## Cross-talk Protocol

- Both workers READ all session files, but only FIX files in their bucket
- Cross-scope issues: send via SendMessage to the owning worker
- Before applying any approved fix: message the other worker with a 2-line summary
- If both find the same issue: escalate to advisor → lead → user decides who fixes
- Strategic/ambiguous decisions: consult advisor, who recommends to lead → user decides
- No direct user contact — all communication through team lead
- No autonomous fixes — all fixes require user approval

---

## Escalation Format (worker → lead → user)

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
