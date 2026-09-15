# Consolidating the implementation plan

Critical point: a usable-looking installation must not bypass independent runtime admission, single ownership or truthful recovery. Runtime implementation remains deferred.

1. Verify current main and preserve all prior work; inspect the existing source and accepted contracts. Check: Git identities/status plus SHA-256 comparison with `queue-decision-checkpoint.json`. Expected: `Consolidation baseline: PASSED`. Completed before edits; the local and live remote main identities match.
2. Write a dependency-ordered delivery plan with source ownership, stage outputs, specific failure/success evidence, old-controller transition and coverage of existing tickets. Check: `python3 /private/tmp/loam-consolidation-check.py design`. Expected: `Consolidation design: PASSED`, working links and all required stage/ticket mappings.
3. Update the handoff/index/current decisions to point to the consolidated plan; independently review correctness and repair confirmed gaps. Check: final mode of the same checker, changed-document whitespace scan and `git diff --check`. Expected: `Consolidation final: PASSED`, preserved earlier snapshots/intake and no tracked source edits.
4. Record self-attack, limitations and request coverage, then write and verify `consolidated-plan-checkpoint.json`. Expected: `Consolidation checkpoint: PASSED`. No source implementation, dependencies, services, model/GPU launches, commits or publishing.
