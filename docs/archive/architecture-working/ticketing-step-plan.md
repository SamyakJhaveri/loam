# Source inventory and ticketing work plan

Runtime implementation remains deferred. Preserve the accepted delivery checkpoint and current main.

1. Verify saved records and live main. Check: SHA-256 comparison of delivery-checkpoint.json has zero mismatches; git ls-remote origin refs/heads/main matches local main. Completed before changes.
2. Acquire and inspect Matt Pocock skills; choose the appropriate planning tool. Check: compare every staged file against pinned clone and verify released manifest skill population, with zero missing or unequal files. Do not claim active installation when discovery directories cannot be written.
3. Draft source inventory and bounded tickets from current contracts using independent agents. Check: a ticket validator verifies unique IDs, existing dependencies, acyclic graph, local source paths, acceptance sections and nonempty tickets; expected zero errors.
4. Review the integrated packet for correctness, repair confirmed gaps, and update living records. Check: rerun validator, verify recorded review packet hashes, and review git status for only intended planning/tooling changes.
5. Present complete ticket bodies and dependency map for publication approval. Check: gh issue list records current open work; no new issues are published or marked ready-for-agent during planning. Runtime starts only after a separate explicit instruction.
