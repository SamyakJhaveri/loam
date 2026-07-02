---
name: session-critique
auto-activate: false
description: >
  Use when you explicitly want adversarial, decision-aware critique of a session's completed
  work before committing — invoke it manually with /session-critique. Reviews every changed
  artifact (code, data, report) as a senior software engineer and AI researcher, asking: did
  the work follow the decisions you made this session, follow repo rules, stay
  un-over-engineered, and leave the codebase maintainable and extensible? Stops at each
  HIGH/MEDIUM finding to discuss the fix with you before applying it, batches LOW nits, and
  applies only the fixes you authorize. NOT for single-file trivial edits (use /validate
  directly) or standard code review without fixes (use /multi-review).
---

# Session Critique: Decision-Aware Adversarial Review

Spawn an advisor-pattern agent team that reviews **all** work done this session — code, data,
and report artifacts — acting as a **senior software engineer and AI researcher**. The bar is
not only "is it correct and finished?" but two forward-looking questions:

1. **Decision adherence** — did the implementation follow the decisions the user made *during
   this session*?
2. **Build-on-top, not patch-on-patch** — did the work leave a codebase the next task can
   extend, or a hodgepodge the next task must spend its time untangling? Elegant solutions,
   not a regression backlog.

Surface every finding for user approval; apply only the fixes the user authorizes.

**Be honest and transparent.** Surface uncertainty explicitly. Never rationalize an incomplete
or "good enough" result as done — name what is unfinished and why.

## When to use

- Session produced multi-file changes (code / data / report) that should be stress-tested
- You want adversarial self-critique + code quality review before committing
- You want to confirm the implementation honored the decisions you made this session
- You need independent verification that nothing was missed, mis-stated, or over-built

## When NOT to use

- Single-file trivial edit — run `/validate` directly
- Standard code review without fix authority — use `/multi-review`
- Only need diff/security/schema checks — use `/validate`
- Work is not yet complete — finish implementation first

## Decision Authority

**The user approves ALL non-trivial decisions. No teammate decides autonomously.**

Teammates CAN without asking: read files, run verification commands, spawn subagents, report
findings.

Teammates MUST escalate (via lead -> user): applying any fix, dismissing any finding, resolving
disagreements, any file content change.

## Procedure

### Phase 0: Scope + Session Decisions Ledger

**Scope the changed artifacts:**

```bash
git log --oneline -10                      # find where this session started
git diff HEAD --name-only                  # uncommitted changes — covers a session with no commits yet
git status --porcelain                     # + untracked session files
# If the session already produced commits, also fold them in:
git diff <first-session-commit>~1..HEAD --name-only
```

Split files into ownership buckets (no overlap), by artifact type:

- **Bucket A** (self-critic): modifications to existing **code** + docs
- **Bucket B** (code-reviewer): newly created files, CLAUDE.md / index files, and **report/output**
  artifacts. For generated reports, defer domain-specific number/citation verification to the
  appropriate specialized skill — do not reimplement it here.
- **Data artifacts** (`results/`, generated data): review **read-only**. NEVER propose editing,
  deleting, or overwriting an existing result file — the result-protection PreToolUse hook
  blocks it. A wrong-looking data file is a finding against the *generating code/spec*, or a
  flag for the user — never an edit under `results/`.
- If a split is unclear: ask the user.

**Build the Session Decisions Ledger.** The user's in-session decisions live in this
conversation, not in git — and the teammates you spawn will not have the conversation. So you
(the lead) extract them first. Write a numbered ledger of every explicit choice or direction
the user gave this session:

```
SESSION DECISIONS LEDGER
1. Chose X over Y because <reason>
2. Directed: use approach Z for <component>
3. Constraint: do NOT do W
...
```

Confirm the ledger with the user before spawning teammates: "Here are the N decisions I'll hold
the work against — anything missing or misremembered?" This ledger is the contract the team
measures implementation drift against.

> **Cross-session caveat:** this reconstruction works because `/session-critique` runs at the
> end of the *same* session. If invoked in a fresh session the conversation is gone — fall back
> to commit messages + handoff docs for the ledger, and say so explicitly.

### Phase 1: Team Design + User Approval

Present the team design table to the user. **WAIT for approval before launching.**

```
| Teammate      | Model  | Role                                            | Owns       |
|---------------|--------|-------------------------------------------------|------------|
| advisor       | opus   | Strategic direction + Elegance Gate, read-only  | All (read) |
| self-critic   | opus   | Adversarial self-review                         | Bucket A   |
| code-reviewer | sonnet | Code quality + structural + report              | Bucket B   |

The lead runs ONE plan-reviewer subagent in Drift Detection mode, fed the Session Decisions
Ledger, as the single decision-adherence check (workers do not each re-run it).

Cost: ~65-75% of all-Opus equivalent
```

### Phase 2: Launch (advisor pattern)

1. `TeamCreate(team_name="session-critique")`
2. Create tasks with `TaskCreate` for each work unit
3. Spawn advisor (Opus) FIRST — use `advisor-prompt.md` from `/agent-team` skill
4. Wait for "ADVISOR READY"
5. Spawn workers using the model assignments above (self-critic Opus, code-reviewer Sonnet)
   with filled prompts from [teammates.md](teammates.md) — **include the Session Decisions
   Ledger verbatim in each worker's brief**
6. Every `Agent` call MUST include `team_name`

### Phase A: Analysis (parallel, no edits)

Both workers analyze simultaneously. Advisor reviews as findings arrive. **No files are
modified.** Each worker runs its audit checklist from [teammates.md](teammates.md), plus the
**forward-elegance** audit (per changed unit: one clear purpose? a well-defined interface?
understandable and testable on its own? follows existing patterns or a one-off bolt-on? will
the next task build on this, or fight it?).

**Decision-adherence is a single session-level pass — not a per-worker one.** The lead spawns
**one** `plan-reviewer` subagent in Drift Detection mode with the Session Decisions Ledger; it
checks the whole implementation against each ledger item (Done-sentence mismatch, scope drift,
Must-NOT violation) and returns one authoritative adherence report. Workers do not each re-run
it — they only flag drift they happen to spot in passing.

Output: two worker findings reports + one drift report (all severity-tagged).

Workers consult advisor (Section 7 of teammate-prompt.md): brief approach before starting,
present options at decision points, escalate after 2 failed attempts, send findings to lead +
advisor when done.

### Phase A.5: Elegance Gate (advisor — whole-session step-back)

After the per-file findings are in, the advisor runs ONE whole-session Elegance Gate. **Think
carefully. Step back** from the individual changes and look at what this session set out to
accomplish:

- Is the work solving the right problem, or has it drifted into solving a side-effect?
- Is there a fundamentally simpler or more coherent shape the whole body of work should have
  taken — a different structure, an existing utility, a known pattern — that would make much of
  it unnecessary?
- Would an experienced engineer look at the session and say "why not just do X instead?"

Output one of: "the overall shape is right because <reason>," or a concrete counter-proposal
(what the alternative is, why it's better, its tradeoffs, what in the session's work it would
replace). This is not a formality — do not skip it.

### Phase B: Decision Loop (user decides, one issue at a time)

The lead collects all findings + advisor recommendations + the Elegance Gate verdict, then
**normalizes every finding to one canonical 4-tier scale** (incoming findings use different
vocabularies) and sorts by severity:

| Canonical | Means | Sources map in | Loop treatment |
|-----------|-------|----------------|----------------|
| **BLOCK** | Halt — must be fixed or explicitly waived before commit | self-critic `BLOCK`; plan-reviewer `critical` | serial, first |
| **HIGH** | Serious; discuss before deciding | plan-reviewer `high`; self-critic `HIGH` | serial |
| **MEDIUM** | Worth a decision | `medium` | serial |
| **LOW** | Nit / advisory | self-critic `WARN`; `low` | batched at end |

**BLOCK, HIGH, and MEDIUM findings — serial, one at a time** (BLOCK first). For each:

```
=== ISSUE k of N  [BLOCK|HIGH|MEDIUM] ===
[file:line] <issue>
Why it matters: <consequence if unfixed — regression risk, decision drift, maintainability cost>
Decision-Ledger link: <which ledger decision this violates, or "none">
Advisor recommendation: <approach> because <reason>
Options: A) <fix>   B) <alternative>   C) leave as-is because <when that is right>
```

**STOP. Discuss with the user.** The user decides the approach. Apply the chosen fix, verify it
(state before/after), then move to the next issue. Do NOT batch BLOCK/HIGH/MEDIUM — each gets
its own discussion. A BLOCK left unresolved and unwaived halts the commit.

**LOW / advisory findings — one batch at the end.** After the High/Med loop completes, present
all LOW findings as a single numbered list for approve-all / cherry-pick:

```
=== LOW / ADVISORY (batch) ===
1. [file:line] <nit> -> <suggested fix>
2. ...
Type approvals (e.g., "1,3,5", "all", or "none").
```

### Phase C: Fix Verification

Every applied fix — BLOCK/HIGH/MEDIUM (in-loop) or LOW (post-batch) — is verified before/after
by the owning worker. The advisor reviews all applied changes (Phase C quality gate) for
accuracy and scope compliance.

### Phase D: Handback

Lead reviews any out-of-scope changes introduced by this critique. Do not revert
pre-existing local work or ambiguous changes without explicit user approval:

```bash
git diff --stat HEAD
git diff --name-only HEAD
```

If a file is out-of-scope and the critique introduced the change, ask the user
before reverting it. If a file was dirty before the critique began or ownership
is unclear, report it and leave it untouched.

Confirm no existing file under `results/` was modified. Present the final summary:
ledger decisions checked (adhered / drifted), Elegance Gate verdict, fixes applied
(High/Med + Low), findings dismissed (with reasons). The user runs `/validate`
and commits at their own discretion.

## Critique is Done when

- Every BLOCK/HIGH/MEDIUM finding has been discussed with the user and resolved (fixed or
  dismissed with a recorded reason); no BLOCK remains unresolved or unwaived
- Every LOW finding has been presented in the batch and dispositioned
- Each Session Decisions Ledger item has been marked adhered or drifted
- The advisor's whole-session Elegance Gate has produced a verdict
- No existing `results/` file was modified; out-of-scope changes introduced by
  the critique were resolved with user approval, and pre-existing local work was
  left untouched

## Report Format (each worker sends to lead after Phase A)

```
## [Role] Findings (AWAITING APPROVAL)

### Issues Found: N
| # | File | Issue | Severity | Decision-Ledger link | Proposed Fix | Alternatives |
|---|------|-------|----------|----------------------|--------------|--------------|
| 1 | ...  | ...   | high/med/low | #2 (drift) / none | [fix A] | [fix B], [skip] |

### Decision adherence (plan-reviewer drift pass): [adhered / drifted on #k, ...]
### Forward elegance: [units that the next task will build on / fight, with reasons]
### Advisor consultations: N
### Subagent results: [agent: PASS/FAIL (N issues)]
### Cross-team issues flagged: [list if any]
```

## Common Mistakes

| Mistake | Prevention |
|---------|-----------|
| Teammates fix files without user approval | Two-phase workflow: ANALYZE then FIX after approval |
| Batching BLOCK/HIGH/MEDIUM into one approval list | Phase B is serial for those — one issue, one discussion, one fix |
| Skipping the Session Decisions Ledger | Phase 0 builds + confirms it before any teammate spawns |
| Treating the Elegance Gate as a formality | Phase A.5 must produce a real verdict or counter-proposal |
| Proposing edits to `results/` data files | Data is read-only; fix the generating code/spec or flag for user |
| Teammates edit out-of-scope files | Explicit bucket ownership + Phase D review; revert only critique-introduced changes with user approval |
| Advisor makes final calls instead of user | Decision authority rule: advisor recommends, user decides |
| Lead commits without user running /validate | Phase D hands back — user owns validation and commit |

## Red Flags — STOP and Escalate to User

- Worker editing a file before Phase B approval
- Worker dismissing a finding as "not worth fixing" without escalating
- Any proposed Edit/Write/rm targeting an existing file under `results/`
- BLOCK/HIGH/MEDIUM findings presented as a batch instead of one at a time
- Advisor approving fixes on the user's behalf
- Any teammate contacting the user directly (all goes through lead)
- Out-of-scope files appearing in `git diff --stat HEAD`

See [teammates.md](teammates.md) for detailed worker specifications, skills, subagents, and
audit checklists.
