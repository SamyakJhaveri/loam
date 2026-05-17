# Stage contract (L2)

> Read when: invoking `/validate`, `feature-dev`, `fix-bug`, or any skill that opens a planning sub-session. Also when authoring the contract for a new skill.

## What a stage contract is

In the ICM routing model (JVC `constraints/02-output-drift.md:54-76`), an L2 stage contract is a per-task agreement loaded only for that task. It answers: **what do I do for this specific task, and what does done look like?** Budget: 200-500 tokens.

The contract exists to prevent "filling gaps with inference" — the failure mode where the model invents requirements that weren't stated, because the prompt was specific about what to do but silent about what NOT to do, and the model treats absence as permission.

## Five required sections

```markdown
# Stage contract: <task name>

## Inputs
- <source file / artifact / data — each with a path or a precise origin>

## Process
1. <step>
2. <step>
3. <step>

## Output
<single artifact path or git delta the stage produces>

## Must NOT include
- <specific thing the output must not contain>
- <specific thing the output must not contain>

## Done looks like
<one anchor sentence that is verifiable by reading the Output>
```

## The Must NOT list is the part most prompts skip

Most prompts say what they want. Few say what they reject. Without an explicit exclusion list the model treats novel-but-plausible content as in-scope by default. Example for a `/fix-bug` stage:

> **Must NOT include**:
> - Refactors of code not on the bug path (out of scope).
> - "While we're here" cleanups of unrelated tests.
> - Migration to a different library, even if the original choice is suboptimal.
> - Tests for cases not exercised by the reported bug.

The exclusions should be specific to this task type and this codebase, not generic ("don't do bad things"). Generic exclusions are noise; specific exclusions catch real drift.

## "Done looks like" must be verifiable from the Output

Bad: "Done looks like a working feature."
Good: "Done looks like `tests/test_user_login.py` adds three new test cases (success, expired token, missing scope), all passing, and the existing 47 tests still pass."

The anchor is what `/validate` checks. If the anchor cannot be objectively verified, the contract is loose enough to drift.

## Applies to engineering loops, not just one-pass pipelines

In JVC's source (content production, client delivery), a stage runs once and hands off. In an engineering loop, the same stage runs N times until the gate (`/validate`) passes — that's the **Pipeline Gate pattern** with iteration. The contract still applies: each iteration's Output must satisfy "Done looks like" before the next gate firing.

If `/validate` fails after 3 iterations on the same contract, the issue is the contract, not the implementation. Stop iterating; re-author the contract with more specific Inputs / tighter Must NOT / sharper Done.

## Source

JVC `constraints/02-output-drift.md:54-76` (contract structure); `constraints/08-handoff-readiness.md:51-69` (Pipeline Gate pattern and iteration semantics adapted from the source).
