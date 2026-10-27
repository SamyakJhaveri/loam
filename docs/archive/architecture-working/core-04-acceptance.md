# CORE-04 accepted and merged

Verified: [PR #141](https://github.com/SamyakJhaveri/loam/pull/141) merged into `main` as merge commit `750a43a88481e73897f41eefcd81292d2213add4`. Its two parents are `8488af8b5afecde3782d3feec269d21be5d02011` (the previous main) and `06ce3e84f547464fc6ce6126908469de8022461c` (candidate-11). The merged main's `seed/.loam/factory` tree is `591535694bcc3611b18d2398c5eab02b288251d3`, exactly the factory tree reviewed and qualified as candidate-11. This record is the closure reference for [CORE-04 #105](https://github.com/SamyakJhaveri/loam/issues/105). The recorded full check exited zero with `check: PASSED`, and the branch handoff reports the PR `verify` job passing before the merge.

This record is a documentation successor. It does not change the qualified factory payload or relabel an older candidate's results. Candidate-11 was the fifth Codex finished-work round; the operator authorized each round after the earlier cap.

## What was accepted

Verified against the ticket acceptance clauses in `docs/architecture-working/tickets/03-core-04.md` and the candidate-11 handoff. Each clause with its disposition:

- **Independent trusted source and separate installed identity.** Satisfied within the operator precondition. Human review at admission supplies authority; the source shape is a mistake guard, not authorship authentication. The expected release identity and the installed file identities are recorded separately.
- **Fresh isolated staging, controlled npm configuration, explicit scripts and origins, complete verified closure.** Satisfied for the shipped script-free lock. Admission uses an explicit prefix, empty user and global configuration, a fresh cache, disabled install scripts and no bin links; origin and script gates precede fetching; only a complete immutable closure is published and selected.
- **Trusted wrapper chooses the admitted executable and strips overrides before Node; the checkout launcher is convenience only.** Satisfied for the frozen startup graph. `scripts/loam-control.sh` re-executes under `/usr/bin/env -i` with a fixed `PATH`, verifies the toolchain Node bytes, the startup import closure, the startup metadata and the selected Node's executability, then dispatches a finite verb table. `launcher.mjs` only resolves fixed installed entrypoints.
- **Fixture-only scratch entrypoints, no project or cache fallback, no implicit install, changed launcher/program/manifest stays an unadmitted fork.** Satisfied. Status and doctor never trigger admission; a consistent checkout fork is refused.
- **Both provider payloads ship; readiness separate.** Unmet by operator decision (2026-09-16), moved to successor [#140 (CORE-04b)](https://github.com/SamyakJhaveri/loam/issues/140). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately.
- **Specific diagnostics for interrupted install, altered manifest/program/launcher, injected environment, missing dependency or compiler, wrong digest and collision; detached diagnostics; ordinary commands leave installation unchanged.** Satisfied for the required cases across the `runtime-admission` and `admission-containment` populations.

## Final review dispositions

Verified: the candidate-11 Codex finished-work review (`reviews/CORE-04/candidate-11/codex-verdict.md`, GPT-6) is APPROVE. Repairs R1 through R6 and B1 through B4 are all repaired against source, current host evidence and fresh probes. R1 restored the complete Mac containment gate; R2 through R6 answered pre-Node metadata, shell validation, prerequisite execution, contender and SETUP fidelity. B1 sealed the startup import closure as a checksummed input; B2 added the full identity relationships, whose single remaining candidate-10 item candidate-11 closes; B3 covered every newline position and independent checksum grammar; B4 covered mode-only and unreadable-file diagnostics.

Verified: a separate merge-readiness review (`reviews/CORE-04/final/codex-verdict.md`) is READY. It recomputed the frozen identities, hashes, exact case counts and the proposed merge tree, and found no blocking merge fact. Its two non-blocking notes were:

- SETUP.md should list `startup-closure` in the snapshot layout. Still open; carried as a follow-up.
- The handoff line reading "did not edit those modules" was too broad, because the branch registers the admission populations in `verify.ts`. Corrected on main to "did not change those sanitizer functions" (`docs/architecture-working/core-04-handoff.md:57`).

## Verified results for the same candidate

Both hosts qualified the same frozen candidate-11. Source: `candidate-11/two-host-acceptance.json` and the host seals under `candidate-11/{mac,linux}/`.

| Check | Mac arm64 | Linux x64 (jhaveris) |
|---|---|---|
| Recipient `node --test` (package + admission) | 49 passed, 0 failed, 0 skipped; exit 0 | 49 passed, 0 failed, 0 skipped; exit 0 |
| `qualify package` | 14/14 | 14/14 |
| `qualify platform` | 34/34 | 34/34 |
| `qualify runtime-admission` (in `bin/check`) | 35/35 | 35/35 |
| `qualify admission-containment` (host-only) | 11/11, mechanism `sandbox-exec`, not skipped | 11/11, mechanism `bwrap`, not skipped |
| Independent rebuild | 9/9 | 9/9 |
| Operator walkthrough (admit, status, doctor, detached-dist doctor) | all exit 0 | all exit 0 |
| Payload unchanged, node digest equals the manifest | yes | yes |

Verified: both hosts used Node `v24.21.0`, npm `11.19.0` and bundled SQLite `3.53.4`. The recorded Node digests are Mac `e4b5a3af0e05c75de2eae013904145f40fe7fc2a6e6f17510128bf45cca4e79b` and Linux `7fde7b8afa198da66257f42ee2001d874c7355631e6d1579a5fb5ef1f246df4c`, each equal to its platform entry in the runtime manifest. The designated full `bin/check` ran from a `$TMPDIR` clone on the Mac and printed `check: PASSED` with `exit=0`; the full check runs on one host while the qualification above ran on both. Render gate 2/2. The committed fixture tarballs are drift-free. `admission-containment` is a separate host-only gate, not part of CI.

## Departures

Verified: candidate-11 records 41 numbered departures from the plan and the reviewer R-list in `candidate-11/departures.md`. The material ones:

- Item 1: an ancestor `.npmrc` is allowed and is not a collision, because npm reads project config only from the explicit prefix and the user file only through the pinned-empty `--userconfig`.
- Item 10: the fetch-only proxy proof is an observation at the environment-function boundary, not a live network proxy-use test.
- Item 12: record corruption reuses the `install-interrupted` status with no snapshot field.
- Item 13: the proxy sentinel is generated at run time so a static literal cannot become a false positive.
- Item 14: the wrapper-refusal seam runs a real contained child that exits without the start marker; it is fixture-only and does not reproduce a real namespace failure.
- Items 33 and 34: admission writes a sealed, checksummed startup-closure manifest; the guarantee is that the exact current closure is asserted by a fixed test, not that every future import change is caught.
- Item 35: the doctor identity relationships are internal consistency checks against already verified installed material, not authorship authentication.

## Unmet and deferred

Verified: "both provider payloads ship" is unmet by operator decision and moved to successor [#140](https://github.com/SamyakJhaveri/loam/issues/140). `supportedRuntime` remains false. This is mechanical foundation work, not managed-execution acceptance.

## Limits that stay

Verified from the candidate-11 handoff:

- Between runs any same-user process can rewrite the snapshot, both inventories, the registry records and the controller copy together, undetectably. The trust boundary is the operator's review at admission plus CORE-02 containment during a contained build.
- The controller cannot protect its own first startup and trusts `/bin/sh`, `/usr/bin/env`, `/usr/bin/mktemp`, `/usr/bin/uname`, the digest tool, `grep`, `sed`, `cut` and `sort` as operating-system components.
- One admission per control root; a complete but unselected snapshot reports as interrupted; recovery is manual removal.
- The Mac containment profile protects only registered paths. CORE-02's limits stay unchanged: non-atomic prelaunch admission, truthful link counts, conservative hard-link refusal, and no discovery of removed-original aliases.

## Follow-ups (not in this ticket)

- The landed sanitizers use their own allowlists and disagree with each other; CORE-04 did not change those sanitizer functions.
- `json_escape` (`loam-control.sh:36`) does not escape the C0 range; within the accepted same-user residual and not caller-reachable, noted for a future hardening pass.
- SETUP.md should list `startup-closure` in the snapshot layout.
- Garbage collection of superseded snapshots, about 120 MB each with the copied Node and npm.

## Evidence

Verified: the Mac evidence lives under `~/.local/state/loam/build-evidence/CORE-04/`, with the sealed candidate under `candidate-11/{candidate.json,two-host-acceptance.json,departures.md,repairs.md,handoff.md,mac/,linux/}` and the reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan verdicts, the candidate-05 through candidate-11 Codex verdicts, the candidate-07 pre-screen, and the READY final merge-readiness verdict). Linux keeps its own copy under the same path on jhaveris.

## Next step

Verified: by the campaign topological order, the next ticket is [CORE-03 #? (04-core-03.md)](tickets/04-core-03.md), qualify actual native profile and lead evidence. `tickets/README.md` lists it at order 4, before CORE-05 at order 5, and its "Blocked by" names CORE-02 and CORE-04, both now merged. [CORE-05 (05-core-05.md)](tickets/05-core-05.md) is also dependency-eligible, blocked only by CORE-04, and is the storage spine the CORE-02 acceptance and the CORE-04 handoff pointed to next; those handoffs named CORE-05 because CORE-03 was still blocked by the unmerged CORE-04 at the time. The operator picks between the native-profile gate (CORE-03) and the store-ownership line (CORE-05); both start from refreshed main with source reading and an opposite-model plan review.

Verified: NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md` with this branch. Whichever of NATIVE-05 or the next CORE ticket merges second rebases, rebuilds and requalifies both hosts.
