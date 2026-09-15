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
