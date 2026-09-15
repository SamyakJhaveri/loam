# Prompt for the first implementation session

Paste the following into a new Codex session opened in `/Users/samyakjhaveri/Desktop/loam`:

```text
Continue with Astra at my selected effort. Read AGENTS.md and docs/architecture-working/START-NEXT-SESSION.md, then follow its linked reading order. Read docs/architecture-working/save-to-main-handoff.md and codex-implementation-runbook.md. Preserve all existing changes and verify the current remote main before working.

First inspect Git status. If these planning records are still untracked, finish their already-authorized documentation-only commit and push to main. Preserve unrelated changes, validate the packet, inspect the exact staged scope and run bin/check before committing. Do not force-push. If Git writes remain blocked, stop and report the restriction before implementation.

After the documentation is safely on main, implement CORE-01 only: https://github.com/SamyakJhaveri/loam/issues/103. The campaign is https://github.com/SamyakJhaveri/loam/issues/102. Do not start later tickets.

Create a fresh branch and worktree from the latest fetched main. Read the ticket, accepted decisions, campaign contract, consolidated implementation plan and its exact named sources. Validate the approved packet using:
python3 docs/architecture-working/tooling/validate-ticket-packet.py --source-root docs/architecture-working/publication/approved-source-packet
Make that packet accessible to every implementing and reviewing seat. Reconcile it with current main and the latest accepted decisions. Frozen publication snapshots retain historical status wording; current authority comes from this prompt and the current handoff.

Codex/Astra is the implementation lead. Obtain a fresh Claude Code Fable 5.1 review of the concrete plan before implementation and a fresh independent review of the finished candidate. Preserve my selected effort. Use bounded subagents, dynamic workflows, advisors and the lean critic where they improve the work. A contributor cannot independently review its own work. Stop and report if the required reviewer is unavailable; do not silently substitute models or accounts.

Implement the agreed TypeScript package and compiled JavaScript delivery defined by CORE-01. Verify its package and rebuild requirements on this Mac and jhaveris within the ticket's scope. Do not launch GPU experiments or unrelated live provider probes. Follow the ticket's focused checks, failing cases and source/build comparison rules. Keep the implementation bounded to CORE-01.

Keep source, plan, review and check evidence in a durable operator-controlled location outside candidate worktrees. Give one integration owner the final candidate and one validation owner the final bin/check run. Require check: PASSED. Refresh relevant reviews and checks if the candidate or main changes.

I authorize the commits, pull request, push and merge needed for CORE-01 after its required reviews and checks pass. Verify the merged result and remote main, update the ticket and living records, then stop before CORE-02. Do not bypass branch protections or force-push main.

End with what was implemented and verified, any remaining risks, what you need my input for, the options and their consequences, your recommendation, and the next decision. Use simple, direct English.
```

This is a future-session instruction. Saving this prompt does not start implementation in the documentation session.
