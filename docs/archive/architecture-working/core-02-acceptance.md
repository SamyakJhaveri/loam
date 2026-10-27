# CORE-02 accepted and merged

Verified: [PR #139](https://github.com/SamyakJhaveri/loam/pull/139) merged as `a5466f9d731e8a97eff51d527866fac6d4c82311` and [CORE-02 #104](https://github.com/SamyakJhaveri/loam/issues/104) is closed. The fetched merge has tree `6f482d721cf3c6b5ced0ae7a1b468255d30d4cb2`, exactly the tree reviewed and qualified as candidate `031795f1463f9409ec06a4a89faaf0c9656288be`. The PR's `verify` job passed before the merge.

This record is a documentation successor. It does not change the qualified factory payload or relabel an older candidate's results.

## What the final repair established

Verified: the recovered review repaired worker failure and closure handling, ambiguous SQLite URI paths, startup environment overrides, runtime identity admission and exposed/protected path overlap. A later scratch probe demonstrated a preexisting hard-link alias that the earlier named suite missed. The final candidate refuses multiply linked non-directory entries beneath workspace, runtime and protected roots before constructing a command, without reading file contents or removing user files.

The new regression failed on the old implementation and again with the guard removed. Native tests attempt protected/runtime link creation after startup. The descendant case first proves the same contained shell can read a workspace marker, avoiding a false denial caused by a missing shell or tool.

## Verified results for the same candidate

| Check | Mac arm64 | Linux x64 |
|---|---|---|
| Recipient suite | 48 passed, 0 failed, 0 skipped | 48 passed, 0 failed, 0 skipped |
| Package | 14/14 | 14/14 |
| Platform | 34/34 | 34/34 |
| Native boundary | 14/14 | 14/14 |
| Independent rebuild | 9/9 | 9/9 |
| Unchanged payload and matching executable digest | yes | yes |

Verified: both hosts used Node `v24.21.0` and bundled SQLite `3.53.4`. The designated full `bin/check` exited zero with `check: PASSED`. Native case counts include positive controls, not only denials.

Supplemental probes observed a stopped owner before a separate contender was refused on both hosts. The Mac also denied the alternate `/System/Volumes/Data` path to the same scratch protected marker with `EPERM`. Both source module digests were bound to the frozen payload. The Mac helper's final integrity check passed.

## Review and evidence

Verified: fresh Astra source review gave conditional code approval. Its stopped-owner evidence condition is satisfied by the supplemental host probes. Fresh native Claude Fable 5.1 reviewed the integrated source; its two possible source blockers were cleared by a native evidence-supplement review of the compiled module and actual qualification records. Its required Mac alias observation passed. Raw adverse verdicts and dispositions remain preserved.

Operator evidence on the Mac lives under `outputs/core-02-hardlink-repair/`: `candidate.json`, `review-manifest.json`, `two-host-acceptance.json`, `full-check.log`, `worker-evidence/`, raw review packets/results, `linux/`, and `mac-run-4i8p9p5k/`. The latter contains the native host report, supplemental results and final integrity result. Linux also retains its evidence at `~/.local/state/loam/build-evidence/CORE-02/candidate-05-031795f/jhaveris/`. Earlier candidates and failed probes were preserved.

## Limits and next step

Verified: `supportedRuntime` remains false. These are mechanical foundation results, not production managed-execution acceptance. The Mac protects registered paths while permitting reads elsewhere. Native host gates remain separate from CI. Prelaunch admission is not atomic with execution; trusted callers must prevent uncontained concurrent mutation and extra inherited protected descriptors, and filesystem link counts must be truthful. The conservative guard also refuses legitimate hard-linked dependencies. Previously copied data or an alias whose original name was removed is not identified by current link count.

Next implement [CORE-04 #105](https://github.com/SamyakJhaveri/loam/issues/105) in a fresh checkout from current main, with the ticket's source reading and independent opposite-model plan review. It establishes independently trusted installed-runtime admission. Then CORE-05 supplies typed authoritative transactions, CORE-06 explicit recoverable setup, and CORE-07 a bounded deterministic check with durable evidence. Keep the receipt experiment separate until that path exists. The proposed first application command is recording a deterministic check result; its final API is not yet implemented. Unresolved execution must not be treated as rollback or blindly retried.
