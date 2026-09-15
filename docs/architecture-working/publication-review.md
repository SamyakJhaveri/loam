# Publication correctness review and repairs

Scope: planning publication tooling and the Codex implementation runbook. No runtime implementation.

A fresh-context Codex reviewer read the publication helper and campaign contract. It confirmed that ticket bodies preserve the approved requirements apart from the authorized status substitution and added metadata. It found three publication correctness gaps: resumed identities could skip readback validation, the frozen source manifest did not include the publication inputs, and unavailable native relationship endpoints lacked the promised fallback. These were repaired before the corresponding operation was used.

A follow-up review found that parent finalization needed its own durable pending transition. The helper now records old/new body hashes and the intended body before updating the parent, then reconciles readback against those known states. Foreign content is rejected. An isolated in-memory check covered old remote body, new remote body and foreign-body rejection, and printed `Parent update recovery: 3 passed, 0 failed (old body, new body, foreign-body rejection)` with exit 0. It did not call GitHub.

The reviewer reported no runbook/campaign conflict. This review is of publication correctness, not an opposite-model approval to implement any runtime ticket. Existing per-ticket cross-model plan/work review requirements remain in force.

## Self-attack

- Input that breaks publication: an unrelated edit to a saved issue or approved input. Readback/hash checks reject it rather than overwrite it.
- Unchecked path: endpoint fallback behavior is not proven by a live unsupported endpoint; the ledger reports whether a fallback was actually used. Authentication failures remain errors.
- Changed material not exercised by runtime tests: documentation, frozen source copies and publication tooling. Packet checks and live issue readback are the relevant verification. No runtime claim is made.
- Evidence limit: the Codex runbook describes a chosen delivery cycle. It does not claim that a full unattended campaign launcher exists or has passed qualification.
