# Approved campaign publication

The user selected Option A: publish the campaign parent and all prepared tickets. Runtime implementation is still deferred. The durable publication ledger records individual returned issue identities, exact submitted body hashes and relationship results. Publication is complete. The ledger reports `published-verified-runtime-deferred`. Live readback printed `Publication: PASSED; 35 children; 102 dependencies; exact bodies; unassigned; no labels; 0 recorded endpoint fallbacks`, exit 0. All parent and dependency relationships were established through native GitHub endpoints.

Parent: https://github.com/SamyakJhaveri/loam/issues/102

First implementation ticket: https://github.com/SamyakJhaveri/loam/issues/103

Read [Codex implementation runbook](codex-implementation-runbook.md) for the decided lead assignments and repeatable plan, implement, review, verify and sequential integration cycle. The coordinator is a proposed use of native tools, not an already qualified unattended launcher.

## Preservation

The approved draft remains unchanged in ticket-backlog.json and tickets/. Its historical publication-pending wording describes the draft. Submitted issue bodies carry the approved publication status. Exact publication inputs and source files are preserved under publication/approved-source-packet/, with a manifest. Later living handoff changes do not retroactively change the approved packet.

The full packet is local and uncommitted. A fresh worktree still needs a verified accessible copy before implementation. Start from current main and reconcile the packet against current accepted decisions and completed predecessor changes before independent plan review. Do not rely on broken GitHub links to uncommitted source files.

## Checks

`python3 docs/architecture-working/tooling/validate-ticket-packet.py --source-root docs/architecture-working/publication/approved-source-packet` verifies the approved ticket packet against its preserved sources.

`python3 docs/architecture-working/tooling/publish-ticket-packet.py verify` reads the issues back from GitHub, checks exact submitted bodies and hashes, checks parent/dependency relationships or explicit endpoint fallbacks, and requires no labels or assignees.

The original main baseline is unchanged. This continuation only publishes issues and updates planning records. It does not run runtime implementation, a native agent task or a GPU job. There is no commit, push, release or deployment.

## Next decision

Recommendation: authorize the first bounded implementation ticket, CORE-01, with its plan review, checks, finished-work review and sequential integration cycle. Alternatively authorize the foundation stage with a pause at its acceptance checkpoint, or keep runtime work deferred. Publication approval alone authorizes none of those implementation options.

Latest preservation checkpoint: `publication-checkpoint.json`. Original draft checkpoints remain historical. The only intentional changes to files in ticketing-checkpoint.json are README.md, START-NEXT-SESSION.md and tooling/validate-ticket-packet.py.
