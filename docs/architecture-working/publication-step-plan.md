# Approved publication steps

Scope: publish the approved parent and child tickets. Runtime implementation remains deferred.

1. Verify the approved draft and main before publication. Check: `python3 docs/architecture-working/tooling/validate-ticket-packet.py` prints `Ticket packet: PASSED`; local and live main identities match. Completed before edits.
2. Preserve the source packet and preview the exact publication scope. Check: publication helper `preview` verifies all source digests and prints the parent, child count and dependency count with no assignments or execution labels.
3. Publish with a durable receipt after every issue creation, then add relationships. Check: publication helper `verify` reads every body, label, assignee, parent link and dependency back from GitHub and reports `Publication: PASSED`.
4. Update the handoff and automation explanation. Check: revalidate the frozen approved source packet, the publication readback, and `git diff --check`. Preserve the original draft and historical records.

Completion: all steps completed. Live readback returned Publication: PASSED with no endpoint fallbacks. The frozen packet validator passed. The final Git diff whitespace check exited 0. See publication-handoff.md and publication-review.md for evidence and limits.
