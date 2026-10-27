# NATIVE-05 accepted and merged

Verified: [PR #142](https://github.com/SamyakJhaveri/loam/pull/142) merged into `main` as merge commit `aef2d892f0abc24f24a9d08f5cd6e97ed7fc27f4`.
The merged `seed/.loam/factory` tree is `1ff30fb7ad386cc4bde5c48265f0d7f13198263e`, identical to candidate-05 `9b134d344dfcaf10498bd760b321f79e6609a6e8` and to the PR head `d0660aad8ad7515a3657977ce97b7d29d76575ec` (candidate-05 plus a docs-only merge of main `8f0655b`).
This record is a documentation successor.
It does not change the qualified payload or relabel an older candidate's results.

## What was accepted

The curated catalog described in `seed/docs/factory/ASSETS.md`: every curated method and supporting native asset recorded with its conservation obligations, compiled from a frozen and independently reviewed obligation table (frozen-v3).
Nothing is delivered, activated, moved or installed; every method stays pending; the full recipient groups stay unavailable.
Read [native-05-handoff.md](native-05-handoff.md) for what the branch contains.

## Evidence

Verified on candidate-05 `9b134d3`, both hosts, same frozen bytes:

| Gate | Mac arm64 (sandbox-exec) | jhaveris Linux x64 (bwrap) |
|---|---|---|
| package / catalog / platform | 14/14, 5/5, 34/34 | 14/14, 5/5, 34/34 |
| native-boundary | 14/14 | 14/14 |
| catalog provenance / independent rebuild | 3/3, 9/9 | 3/3, 9/9 |
| CORE-04 runtime admission / containment, rerun on the merge | 35/35, 11/11 | 35/35, 11/11 |

Isolated-clone `bin/check`: `check: PASSED` on `9b134d3` and again on `d0660aa`.
CI verify passed on the PR head.
The docs-only merge was accepted without repeating the host runs or the review because the factory tree is byte-identical (operator decision, option 1).

## Review dispositions

Codex finished-work reviews: candidate-01, -02 and -03 BLOCK, all findings repaired into the next candidate; candidate-04 not separately reviewed (merged with main before qualification).
Candidate-05 was reviewed twice on the same bytes.
The first run returned BLOCK with one major and three minors; the second run returned APPROVE with two minors and overwrote the first file.
Both are recorded in the packet's `identity.json`; only the first verdict's SHA-256 survives as a trace.
The operator merged on the APPROVE and filed the open findings:

- [#143](https://github.com/SamyakJhaveri/loam/issues/143): split agent-team snapshot unit u3 so the role-profile config is an explicit exclusion and the self-critic lesson maps to an exact section of `method:session-critique` (plan D7/D10). A record defect; nothing is activated.
- [#144](https://github.com/SamyakJhaveri/loam/issues/144): the tilde prose scanner misses adjacent-word personal paths.
- [#145](https://github.com/SamyakJhaveri/loam/issues/145): the CORE-04 host qualifier omits the tracked digest and per-case counts.

## Limits that stay

The catalog is a record, not permission.
Delivery of any method belongs to NATIVE-06, NATIVE-07, NATIVE-08 and NATIVE-12.
The obligation table changes only through source evidence and a fresh independent source review.

## Next

[CORE-03](tickets/04-core-03.md) (#106) starts from this main; its worktree at `8f0655b` must rebase onto `aef2d892`.
[CORE-05](tickets/05-core-05.md) is also eligible.
