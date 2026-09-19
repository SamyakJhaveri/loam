# Native profile and lead-binding design work

Status: design only. Runtime implementation and live native probes remain deferred.

Critical point: a worker must not acquire lead decision authority through a claimed role, copied session identifier or forged tool payload.

1. Verify current main and preserve the preceding design. Checks: `git rev-parse HEAD main origin/main`, `git ls-remote origin refs/heads/main`, and Python SHA-256 comparison with `resume-checkpoint.json`. Expected: matching main identity and every checkpoint entry matching. Completed before editing; before-edit copies are in `/private/tmp/loam-native-binding-before/`.
2. Specify native configuration, actual lead attribution and recovery, with provider evidence and failure cases. Check: `python3 /private/tmp/loam-native-binding-doc-check.py design`. Expected: `Native binding design checks: PASSED`, including required authority clauses, local links and unchanged historical records. Complete before updating living navigation.
3. Update accepted first-run direction, decision presentation, current navigation and restart order. Check: `python3 /private/tmp/loam-native-binding-doc-check.py final`. Expected: `Native binding final checks: PASSED`, including links from the living records and documentation-only scope.
4. Obtain a fresh-context correctness review and write the self-attack and scope mapping. Check: rerun the final document check, `git diff --check`, and validate the new checkpoint digests. Expected: PASS, exit 0 and matching hashes. Root owns integration and final checks. No repeat of the previous full repository suite for prose-only changes.

Temporary document checks are validation aids, not factory implementation. Preserve the original snapshots and all previous checkpoints. New native details remain recommendations until the user accepts them. The user's request for decision options is a standing communication instruction, not approval of an unpresented design.

Verified outcome: baseline, design and final document checks passed. Independent review found a Claude native withdrawal case; the specification was repaired and the bounded rereview confirmed it. The evidence, self-attack and requirement mapping are in [native validation](native-binding-validation.md). Native finality and configuration enforcement remain live probe gates.
