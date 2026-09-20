# Prompt for the CORE-02 implementation session

CORE-01 is merged (main `1ed2261`, PR #138). Paste the following into a new Codex session opened in `/Users/samyakjhaveri/Desktop/loam`:

```text
Continue with Astra at my selected effort in /Users/samyakjhaveri/Desktop/loam.

Read AGENTS.md, then docs/architecture-working/START-NEXT-SESSION.md and its
first linked record, docs/architecture-working/core-01-handoff.md. Then read
codex-implementation-runbook.md, delivery-workflow.md and ticket-campaign.md.
Historical "deferred" or "untracked" wording in older records is provenance,
not current status. CORE-01 is merged; do not redo any of it.

Verify first: git fetch, then confirm local main equals origin/main and that
bin/check passes on main with these exports:
  export LOAM_FACTORY_TOOLCHAIN=~/.local/state/loam/toolchains/node-v24.21.0-darwin-arm64
  export LOAM_FACTORY_COPIER=~/Desktop/loam/.venv/check/bin/copier
Require check: PASSED before any new work. If it fails, stop and report.

Implement CORE-02 only: https://github.com/SamyakJhaveri/loam/issues/104
(Qualify storage, lifetime locks and candidate containment on both hosts).
Campaign: https://github.com/SamyakJhaveri/loam/issues/102. Do not start
CORE-03 or CORE-04.

Use a fresh branch and worktree from the latest fetched main. Codex/Astra
leads implementation. Read the ticket, its named sources and the accepted
decisions. Reconcile the frozen source packet with what CORE-01 actually
landed under seed/.loam/factory/. Record the reconciled packet you used.

Require a fresh independent Claude Code Fable 5.1 review of the concrete plan
before code, and a fresh independent review of the exact finished candidate
before integration. Fresh, tool-free contexts; no author conversation. Stop if
the reviewer is unavailable; do not substitute models or accounts.

Both hosts are required: this Mac (darwin arm64) and jhaveris (linux x64), with
the task-owned Node 24.21.0 toolchains under ~/.local/state/loam/toolchains on
each host. Record environment identities and exact results per host. Mac-only
evidence cannot certify Linux locking, storage or containment behavior.

Keep evidence outside worktrees under ~/.local/state/loam/build-evidence/CORE-02
and .../reviews/CORE-02. Give one integration owner the final candidate and one
validation owner the single full bin/check run. Require check: PASSED. Refresh
reviews and checks if the candidate or main changes. Run every test through
fixed case accounting; a skipped or missing case must fail the gate, as CORE-01
does with runFixedFixture.

I authorize the commits, pull request, push and merge needed for CORE-02 after
its required reviews and checks pass, and after the CI verify job passes. Merge
by squash so the merged tree equals the reviewed tree. Verify remote main, update
issue #104, tick CORE-02 in #102, add core-02-handoff.md and point
START-NEXT-SESSION.md at it, then stop before CORE-03. No release tag. Do not
bypass permissions or force-push.

Keep TypeScript and the accepted architecture settled unless new evidence shows
a concrete problem. Use simple, direct English. End with verified results,
risks, any decision you need from me, the options and consequences, your
recommendation, and the next step.
```

Saving this prompt does not start CORE-02.

## Variant chosen on 2026-09-15: Claude Code implements, Codex reviews before merge

Codex credits are exhausted until 2026-09-19. Samyak chose: a Claude Code session implements and qualifies CORE-02 this week, and a fresh Codex/Astra review of the finished candidate gates the merge on or after 2026-09-19. This keeps the opposite-model gate and delays only the merge. Record this departure from the runbook's "Codex leads core tickets" in `core-02-handoff.md`.

Start the session from `/Users/samyakjhaveri/Desktop/loam` with:

```
claude --model claude-fable-5-1
```

Then paste:

```text
Goal and why
Implement Loam ticket CORE-02 only: https://github.com/SamyakJhaveri/loam/issues/104
(Qualify storage, lifetime locks and candidate containment on both hosts).
Campaign: https://github.com/SamyakJhaveri/loam/issues/102. CORE-01 is merged
(main 1ed2261, PR #138); do not redo any of it. You are the implementation lead
because Codex credits are exhausted until 2026-09-19. The finished candidate
must wait for a fresh Codex/Astra review before merge. Do not merge in this
session.

Read first, in order: AGENTS.md; docs/architecture-working/START-NEXT-SESSION.md
and its first link core-01-handoff.md; codex-implementation-runbook.md;
delivery-workflow.md; ticket-campaign.md; the CORE-02 issue body and every
source file it names. Older "deferred" or "untracked" wording is provenance,
not current status. The previous ticket's evidence and the fixed-case-accounting
pattern are in ~/.local/state/loam/build-evidence/CORE-01 and
seed/.loam/factory/src/testing/verify.ts (runFixedFixture, assertCaseResults).

Constraints
- Verify before working: git fetch; local main equals origin/main; bin/check
  passes on main with
    export LOAM_FACTORY_TOOLCHAIN=~/.local/state/loam/toolchains/node-v24.21.0-darwin-arm64
    export LOAM_FACTORY_COPIER=~/Desktop/loam/.venv/check/bin/copier
  Stop and report if it does not print check: PASSED.
- Fresh branch core-02-storage-containment and worktree
  /private/tmp/loam-core-02 from latest fetched main. The sandbox allows writes
  there and under ~/.local/state/loam.
- Reconcile the ticket's frozen source packet against what CORE-01 landed under
  seed/.loam/factory/. Record the reconciled packet you used.
- Blind plan review before code: a fresh Claude Fable 5.1 context via the
  sam-cc-setup:plan-reviewer agent, given only the plan, ticket, and sources,
  never your reasoning. Fold in its required amendments and re-review until
  APPROVE. Save each round under
  ~/.local/state/loam/build-evidence/reviews/CORE-02/plan-NN/.
- Delegate reading, probing, and mechanical implementation to
  claude-opus-4-8[1m] workers at xhigh effort via the Agent tool or a dynamic
  Workflow. Never Haiku or Sonnet. Keep your own context for judgment and
  integration. Use sam-cc-setup:lean-critic on prose and tickets you write.
- Do not feed CORE-02 to the legacy bin/factory runner; the runbook says its
  contracts are unqualified for this campaign.
- Both hosts are required: this Mac (darwin arm64) and jhaveris (linux x64),
  each with its task-owned Node 24.21.0 under ~/.local/state/loam/toolchains.
  gh works only through bin/runner; ssh and scp are sandbox-excluded. Record
  environment identities and exact results per host. Mac-only evidence cannot
  certify Linux locking, storage or containment.
- Every new test runs through fixed case accounting. A skipped, missing or
  renamed case must fail its gate, as CORE-01 does.
- Keep evidence outside worktrees under
  ~/.local/state/loam/build-evidence/CORE-02 and .../reviews/CORE-02.
- No live provider or GPU probes, no release tag, no CORE-03 or CORE-04 work,
  no runtime support claim. TypeScript and the accepted architecture stay
  settled unless new evidence shows a concrete problem.
- Commits are authored by Samyak with no agent co-author trailer.

Done check per task
1. Baseline: bin/check on main prints check: PASSED; evidence file
   CORE-02/baseline.json records main SHA and the check log.
2. Plan: reviews/CORE-02/plan-NN/ holds an APPROVE verdict from a fresh Fable
   reviewer with its amendments folded into the plan file.
3. Implementation: the ticket's acceptance cases exist as named flat tests,
   failing first for the intended reason (red logs saved), then passing.
4. Both-host qualification: CORE-02/candidate-NN/mac/qualification.json and
   .../jhaveris/qualification.json both show status passed and payload digests
   unchanged; adapt CORE-01/qualify-host.py for the new gates.
5. Full check: one owner runs bin/check on the frozen candidate in a $TMPDIR
   clone with .venv/check symlinked from the main checkout; log shows
   check: PASSED.
6. Finished-work review: a fresh Fable reviewer returns APPROVE on the exact
   frozen candidate; verdict saved under reviews/CORE-02/candidate-NN/.
7. Push the branch and open the PR with gh via bin/runner. Title starts with
   "CORE-02:". Body lists what shipped, per-host results, review evidence, and
   states in bold that merge waits for a fresh Codex/Astra review on or after
   2026-09-19. Confirm the CI verify job passes on the PR.
8. Records: add docs/architecture-working/core-02-handoff.md (what shipped,
   evidence paths, the Claude-implements Codex-reviews departure and why, open
   items, the exact Codex review prompt to run on 2026-09-19). Point
   START-NEXT-SESSION.md's current-handoff section at it. Commit these docs
   directly to main after bin/check passes. Comment on #104 with the PR link
   and the pending-review status. Do not tick CORE-02 in #102.
9. Stop. Do not merge.

Session conduct
Plain, direct English. Short sentences. Define a technical term the first
time it appears. Report verified results separately from assumptions. If a
gate is blocked, say so and stop rather than substituting a weaker check. End
with: what was implemented and verified; remaining risks; the exact commands
Samyak runs on 2026-09-19 to request the Codex review and merge; the next
decision.

Target model and effort
Lead: Claude Fable 5.1 at high effort. Workers: claude-opus-4-8[1m] at xhigh.
Reviewers: fresh Claude Fable 5.1 contexts. Codex/Astra reviews the finished
candidate on or after 2026-09-19, before merge.
```

### On 2026-09-19, after Codex credits reset

Open a Codex session in `/Users/samyakjhaveri/Desktop/loam` and paste:

```text
Continue with Astra at my selected effort. You are the independent reviewer,
not the implementer. Read AGENTS.md, docs/architecture-working/core-02-handoff.md
and the CORE-02 issue https://github.com/SamyakJhaveri/loam/issues/104.

Review the exact finished candidate on the open CORE-02 pull request against
the ticket, the accepted decisions and the approved plan in
~/.local/state/loam/build-evidence/reviews/CORE-02/. Do not read the
implementer's conversation. Run the candidate's own gates on this Mac with the
declared LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER exports from
core-02-handoff.md. Never run a build that rewrites the frozen candidate.

Return APPROVE or BLOCK with file:line findings, a concrete failure scenario
and exact fix for each, and a coverage ledger over the ticket's acceptance
bullets. Save the verdict under
~/.local/state/loam/build-evidence/reviews/CORE-02/codex-final/.

If APPROVE and the CI verify job is green: I authorize the squash merge so the
merged tree equals the reviewed tree. Verify remote main, update issue #104,
tick CORE-02 in #102, update core-02-handoff.md, then stop before CORE-03. If
BLOCK: post the findings on the PR and stop.
```
