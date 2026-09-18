# CORE-04 handoff: admit an isolated installed runtime from an independent trust source

Status: candidate-11 (`06ce3e84f547464fc6ce6126908469de8022461c`, factory tree `591535694bcc3611b18d2398c5eab02b288251d3`) on branch `core-04-runtime-admission` from main `e4c6f47`, on top of candidate-10 `0f24cf2`. Both hosts qualified the same frozen candidate (Mac arm64 under sandbox-exec, jhaveris Linux x64 under bwrap); full check passed. Pull request: https://github.com/SamyakJhaveri/loam/pull/141 (open, head candidate-11, not merged). Codex history: candidate-05 BLOCK (R1-R6), candidate-08 BLOCK (B1-B3), candidate-09 BLOCK (B1-B3 remaining, new B4), candidate-10 BLOCK (one remaining B2 identity-relationship item); candidate-11 answers it and its review is APPROVE (`reviews/CORE-04/candidate-11/codex-verdict.md`). Candidate-11 is a fifth Codex round by the operator's decision on 2026-09-18. Not merged; merge waits for the operator.

## What shipped

- `scripts/loam-control.sh`: the trusted operator setup and control entrypoint. POSIX `sh`, dependency free. It re-executes under `/usr/bin/env -i` with a fixed `PATH`, verifies the toolchain `bin/node` bytes against the trusted runtime manifest, dispatches a finite verb table (`admit`, `status`, `doctor`) with `--no-global-search-paths`, and before dispatch verifies the snapshot entrypoint set with the host digest tool, the startup import closure, the startup metadata and the selected Node's executability.
- `src/installation/admit.ts`: admission from a trusted source into a control root, with a computed startup-closure manifest, and `computeId` exported for the doctor identity relationship.
- `src/commands/doctor.ts`: read-only installed diagnostics with complete admission-record shape validation and full internal-consistency identity relationships (aggregate release digests, platform/arch/node/sqlite/npm identities, the complete file map, and the deterministic snapshot-ID relationship) checked against the byte-verified installed material before reporting healthy.
- `src/contracts/installation.ts`: frozen record fields and the diagnostic list.
- Fixtures: `runtime-admission` (35 offline cases, in `bin/check`) and `admission-containment` (11 host-only cases under a real sandbox mechanism); fixture packages under `assets/admission-fixtures/`.
- `launcher.mjs` gains `qualify runtime-admission`, `qualify admission-containment`, `status` and `doctor`. `assets/runtime-manifest.json` gains an `admission` block. `SETUP.md` documents the trust root, commands, layout, states and residuals.

Repairs answering the candidate-05, candidate-08 and candidate-09 reviews (R2-R5, B1-B4) are carried; see the candidate-07 through candidate-10 handoffs.

Repair answering the candidate-10 review (B2 remaining): doctor now compares the recorded aggregate release digests and the recorded platform, architecture, Node, SQLite and npm identity fields against the byte-verified installed material and the running admitted executable, validates the complete recorded file map against the installed manifest before the payload byte re-hash, and checks the deterministic snapshot-ID relationship via `computeId`, so an incomplete or inconsistent admission record is `install-interrupted` and never reports healthy.

## Verified results (candidate-11)

| Check | Mac arm64 | Linux x64 (jhaveris) |
|---|---|---|
| Recipient `node --test` (package + admission fixtures) | exit 0 | exit 0 |
| `qualify package` | 14/14 | 14/14 |
| `qualify platform` | 34/34 | 34/34 |
| `qualify runtime-admission` | 35/35 | 35/35 |
| `qualify admission-containment` | 11/11, ran under mechanism `sandbox-exec` (not skipped) | 11/11, ran under mechanism `bwrap` (not skipped) |
| Independent rebuild | 9/9 | 9/9 |
| Operator walkthrough with the real lock (admit, status, doctor with checkout, doctor after the checkout dist is moved away) | all exit 0 | all exit 0 |
| Payload unchanged, node digest equals the manifest, SQLite 3.53.4 | yes | yes |

Full `bin/check` from a `$TMPDIR` clone of candidate-11 on the Mac: `check: PASSED` (the full check runs on one host; the qualification above ran on both). Render gate 2/2. Fixture tarballs drift-free. `candidateUnchanged` and `digestMatches` true on both hosts.

Evidence on the Mac: `~/.local/state/loam/build-evidence/CORE-04/` (baseline, reconciled packet, reading records, both-host probes, advisors, builders, red and green logs, negative probes, `candidate-11/{candidate.json,render-gate.log,fixture-drift.json,independent-probe-results.json,departures.md,repairs.md,mac/,linux/}`; the host records seal under `candidate-11/mac/` and `candidate-11/linux/`); reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan verdicts, the candidate-05 through candidate-10 Codex verdicts, the candidate-07 pre-screen, and the candidate-11 Codex verdict at `reviews/CORE-04/candidate-11/codex-verdict.md`, APPROVE). Linux keeps its own copy under the same path on jhaveris.

## Unmet and deferred

- "Both provider payloads ship" is unmet by operator decision (2026-09-16). Successor: https://github.com/SamyakJhaveri/loam/issues/140 (CORE-04b). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately.

## Departures from plan-03 and the review R-list

See `candidate-11/departures.md`, items 1-41. Items 1-8 carry from candidate-06; 9-20 from candidate-07; 21-27 from candidate-08; 28-32 from candidate-09; 33-38 from candidate-10 (item 34 narrows the closure guarantee to "the exact current closure is asserted by the fixed test" and item 35 now records that the aggregate release digests and tool identity fields are compared with the installed material, per the candidate-10 corrections); 39-41 record candidate-11. In one line each, the candidate-11 items:

- 39: the deterministic ID-relationship check imports `computeId` from `admit.ts` and is exercised by a forked admission record under a wrong id with the selection and runtime record repointed, the only corruption that passes the earlier field checks.
- 40: the record file-map check moved before the payload byte loop, so a record-only per-file digest mismatch is `install-interrupted`, not `build-altered-release`.
- 41: candidate-11 is a fifth Codex round by the operator's decision on 2026-09-18.

## Limits that stay

- `supportedRuntime` remains false. This is mechanical foundation work, not managed-execution acceptance.
- Between runs any same-user process can rewrite the snapshot, both inventories, the registry records and the controller copy together, undetectably. The trust boundary is the operator's review at admission plus CORE-02 containment during a contained build.
- The controller cannot protect its own first startup (native loader variables and the shell's startup) and trusts `/bin/sh`, `/usr/bin/env`, `/usr/bin/mktemp`, `/usr/bin/uname`, the digest tool, `grep`, `sed`, `cut` and `sort` as operating-system components.
- One admission per control root; a complete but unselected snapshot is reported as interrupted; recovery is manual removal.
- The Mac containment profile protects only registered paths. CORE-02's limits (non-atomic prelaunch admission, truthful link counts, hard-link refusal, no discovery of removed-original aliases) are unchanged.

## Follow-ups (not in this ticket)

- The landed sanitizers disagree: `native-boundary.ts` `shouldStrip` does not strip `npm_config_*`; `toolchain.mjs` `cleanEnvironment` and `verify.ts` `cleanTestEnvironment` do not strip `LD_PRELOAD`, `DYLD_*`, `NODE_TLS_REJECT_UNAUTHORIZED`, `NODE_EXTRA_CA_CERTS` or `OPENSSL_CONF`. CORE-04 uses its own allowlists and did not edit those modules.
- `json_escape` (`loam-control.sh:36`) still does not escape the C0 range, so the staging-glob echo at `loam-control.sh:173` would emit a raw control byte if a same-user writer planted a control-character filename under `runtimes/`. Within the accepted same-user residual and not caller-reachable; noted for a future hardening pass.
- SETUP.md should list `startup-closure` in the snapshot layout (Codex candidate-11, non-blocking).
- Garbage collection of superseded snapshots (about 120 MB each with the copied Node and npm).
- `admission.snapshot-collision` was dropped as unreachable under the one-admission rule.

## Next

The candidate-11 Codex review (`reviews/CORE-04/candidate-11/codex-verdict.md`, GPT-6) is APPROVE: no remaining blocking defect within the approved scope; R1-R6 and B1-B4 repaired; non-blocking documentation notes only (departures wording; SETUP.md may list `startup-closure`). Merge waits for the operator. On APPROVE, the merge still waits for the operator's explicit instruction. On BLOCK, the operator decides whether to run a further round. After merge: CORE-05 (typed authoritative transactions) per core-02-acceptance.md. NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md`; whichever merges second rebases, rebuilds and requalifies both hosts.
