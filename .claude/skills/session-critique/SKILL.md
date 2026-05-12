---
name: session-critique
description: Use when a session's implementation work is complete and needs adversarial critique and code quality review before committing. Triggers — after multi-file changes, after feature implementation, before final commit on significant work, when independent review of own work is needed. NOT for single-file trivial edits (use /validate directly) or standard code review without fixes (use /multi-review).
auto-activate: false
---
ultrathink
# Session Critique: Adversarial Review via Agent Team

Spawns an advisor-pattern agent team that adversarially reviews all work done
in the current session, surfaces every finding for user approval, and applies
only the fixes the user authorizes.

## When to use

- Session produced multi-file changes that should be stress-tested
- You want adversarial self-critique + code quality review before committing
- Changes span documentation, skills, specs, or cross-cutting concerns
- You need independent verification that nothing was missed or mis-stated

## When NOT to use

- Single-file trivial edit — run `/validate` directly
- Standard code review without fix authority — use `/multi-review`
- Only need diff/security/schema checks — use `/validate quick`
- Work is not yet complete — finish implementation first

## Decision Authority

**The user approves ALL non-trivial decisions. No teammate decides autonomously.**

Teammates CAN without asking: read files, run verification commands, spawn
subagents, report findings.

Teammates MUST escalate (via lead → user): applying any fix, dismissing
any finding, resolving disagreements, any file content change.

## Procedure

### Phase 0: Scope Detection

```bash
# Find this session's commits
git log --oneline -10

# Get all changed files
git diff <first-session-commit>~1..HEAD --name-only
```

Split files into two ownership buckets (no overlap):
- **Bucket A** (self-critic): modifications of existing files
- **Bucket B** (code-reviewer): newly created files + CLAUDE.md/index files
- If split is unclear: ask the user

### Phase 1: Team Design + User Approval

Present team design table to user. **WAIT for approval before launching.**

```
| Teammate      | Model  | Role                           | Owns        |
|---------------|--------|--------------------------------|-------------|
| advisor       | opus   | Strategic direction, read-only | All (read)  |
| self-critic   | opus | Adversarial self-review        | Bucket A    |
| code-reviewer | sonnet | Code quality + structural      | Bucket B    |

Cost: ~45-55% of all-Opus equivalent
```

### Phase 2: Launch (advisor pattern)

1. `TeamCreate(team_name="session-critique")`
2. Create tasks with `TaskCreate` for each work unit
3. Spawn advisor (Opus) FIRST — use `advisor-prompt.md` from `/agent-team` skill
4. Wait for "ADVISOR READY"
5. Spawn workers with filled prompts from [teammates.md](teammates.md)
6. Every `Agent` call MUST include `team_name`

### Phase A: Analysis (parallel, no edits)

Both workers analyze simultaneously. Advisor reviews as findings arrive.
**No files are modified.** Output: two findings reports.

Workers consult advisor (Section 7 of teammate-prompt.md):
- Before starting: brief approach, wait for advisor approval
- At decision points: present options to advisor
- After 2 failed attempts: escalate to advisor
- After completing analysis: send findings to lead + advisor

### Phase B: Decision Batch (user approves)

Lead collects all findings from both workers + advisor recommendations.
Presents to user as a single numbered decision list:

```
=== SESSION REVIEW: DECISIONS NEEDED ===

Self-critic found N issues. Code-reviewer found M issues.

#1. [file:line] Issue description
    Recommendation: [A/B/C] because [reason]
    -> Approve fix? (A/B/C/skip)

#2. ...

Type approvals (e.g., "1A, 2B, 3-skip") or "approve all"
```

### Phase C: Fix Execution (after approval only)

Workers apply ONLY approved fixes. Each fix verified before/after.
Advisor reviews all applied changes (Phase 4 quality gate).

### Phase D: Handback

Lead reverts any out-of-scope changes:
```bash
git diff --stat HEAD
git checkout HEAD -- <any-out-of-scope-file>
```
Presents final summary of all applied fixes to user.
User runs `/validate` and commits at their own discretion.

## Report Format (each worker sends to lead after Phase A)

```
## [Role] Findings (AWAITING APPROVAL)

### Issues Found: N
| # | File | Issue | Severity | Proposed Fix | Alternatives |
|---|------|-------|----------|-------------|-------------|
| 1 | ...  | ...   | low/med/high | [fix A] | [fix B], [skip] |

### Advisor consultations: N
### Subagent results: [agent: PASS/FAIL (N issues)]
### Cross-team issues flagged: [list if any]
```

## Common Mistakes

| Mistake | Prevention |
|---------|-----------|
| Teammates fix files without user approval | Two-phase workflow: ANALYZE then FIX after approval |
| Teammates edit out-of-scope files | Explicit bucket ownership + lead reverts in Phase D |
| Advisor makes final calls instead of user | Decision authority rule: advisor recommends, user decides |
| Workers skip advisor consultation | Section 7 protocol: brief before starting, consult at decision points |
| Lead commits without user running /validate | Phase D hands back — user owns validation and commit |

## Red Flags — STOP and Escalate to User

- Worker editing a file before Phase B approval
- Worker dismissing a finding as "not worth fixing" without escalating
- Advisor approving fixes on user's behalf
- Any teammate contacting the user directly (all goes through lead)
- Out-of-scope files appearing in `git diff --stat HEAD`

See [teammates.md](teammates.md) for detailed worker specifications, skills,
subagents, and audit checklists.
