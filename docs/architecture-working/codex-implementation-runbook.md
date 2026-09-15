# How this campaign will be implemented from Codex

Status: delivery approach decided. Runtime implementation has not started. Publishing the campaign is not permission to execute it.

## Lead and engineering choices

Codex/Astra leads the core, Codex integration, assets, remote execution, maintenance and verification tickets. Claude Code/Fable leads NATIVE-03, the Claude-native bridge. Preserve Samyak's selected effort and model. The other provider independently reviews both the plan and the finished candidate. An advisor or helper who contributed cannot supply the independent review.

The product is TypeScript compiled to JavaScript with locked factory dependencies. The supported hosts are Mac and Linux. Begin with this Mac and jhaveris. The accepted detailed architecture and each ticket's source packet govern the work. Sources and cookbooks provide methods, with justified departures allowed. Do not reopen settled choices without new evidence.

## Repeatable ticket cycle

1. Select an authorized ticket whose predecessors are verified and merged. Fetch current main. Create its own branch and worktree from that main. Supply the exact digest-verified source packet and read the named files before planning. Reconcile the old packet with current accepted decisions and predecessor changes; record any revised packet used for review.
2. Write a bounded implementation plan and ask a fresh opposite-model reviewer to check it. Preserve the requested and actually observed model/effort, the reviewed inputs and any model attribution uncertainty.
3. Establish the relevant failing cases. Implement the ticket with native Codex or Claude tools. Delegate independent pieces only when useful. Declare required outputs before dispatch. Use advisors for a concrete uncertainty and the lean critic when simpler engineering needs examination.
4. Run the ticket's focused checks and affected regressions. Obtain fresh opposite-model review of the exact finished candidate. Repair confirmed problems within declared limits and repeat affected checks and reviews. Missing outputs or exhausted repair limits stop the ticket.
5. One integration owner prepares the candidate. One validation owner runs the full bin/check for that snapshot and requires check: PASSED. Refresh review and check evidence if main moves or the candidate changes. Keep evidence outside worktrees under operator control.
6. After explicit implementation authority covers integration, merge only that reviewed and verified candidate. Verify the merged result, update issue/evidence records and start the next dependent ticket from refreshed main. Do not infer push/merge authority from the current publication approval.

## What can be automated

Use native CLI execution for the repeatable work. The local `codex exec --help` and official non-interactive documentation confirm `--cd`, model selection, JSON event output, structured final output and saved final messages. A ticket prompt can be supplied from a file. An external coordinator can invoke fresh Codex runs and separate Claude review processes, capture outputs and run deterministic Git/check commands.

Start by operating this cycle in Codex with existing tools. Extract repetitive preparation, process invocation, checks and receipt bookkeeping into a small coordinator only where useful. Do not build another general workflow platform first. The coordinator enforces prerequisites and review/check results; native agents do planning and implementation. Do not feed this new packet directly to the legacy bin/factory runner without qualifying its contracts.

This document is a runbook, not an implemented or qualified campaign launcher. CLI feature availability does not prove the complete unattended cycle works. The initial foundation tickets qualify packaging, storage, containment and actual native identity. Subsequent automation must respect that evidence and the declared ticket boundaries.

For NATIVE-03, Codex can coordinate the same outer cycle while Claude implements and a fresh Codex reviewer checks it. Mixed-provider implementation requires independent full-candidate review from both providers or a scope split.

## Where the cycle stops

Stop for missing source access, unavailable required model/account, confirmed review blockers, failed checks, exhausted repair/work limits or a material user-level design tradeoff. Report the cause and saved progress. Do not silently switch accounts/models. Live native or GPU probes need a separately declared bounded plan within user authority. They are never implicit in install/build/check.

## Next authorization

Recommendation: authorize CORE-01 as the first bounded implementation step after the source packet is supplied and the plan receives opposite-model review. Complete its review/check/integration cycle before expanding to sequential stage-level automation. Samyak may instead authorize the foundation stage with a stop after its acceptance checkpoint, or keep implementation deferred.

## Evidence

- Local `codex exec --help` checked during this publication continuation.
- Official guide: https://learn.chatgpt.com/docs/non-interactive-mode
- Governing campaign: ticket-campaign.md and delivery-workflow.md.
- Exact per-ticket leads, prerequisites and acceptance populations: ticket-backlog.json.
