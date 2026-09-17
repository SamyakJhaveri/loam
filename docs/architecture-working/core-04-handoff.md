# CORE-04 handoff: admit an isolated installed runtime from an independent trust source

Status: candidate-07 (`90aafd9be08b9fa3fa42ec55d00028d5756dcf45`, factory tree `5589907c1b3937e7fe526c2f3593f0aa7c145d0c`) on branch `core-04-runtime-admission` from main `e4c6f47`. Both hosts qualified the same frozen candidate (Mac arm64 under sandbox-exec, jhaveris Linux x64 under bwrap). The Codex finished-work review of candidate-07 has NOT run: the operator paused Codex usage on 2026-09-17; it is the one open gate. Pull request: https://github.com/SamyakJhaveri/loam/pull/141 (open, not merged). Merge waits for the operator and for that review.

## What shipped

- `scripts/loam-control.sh`: the trusted operator setup and control entrypoint. POSIX `sh`, dependency free. It re-executes itself under `/usr/bin/env -i` with a fixed `PATH`. It verifies the toolchain `bin/node` bytes against the trusted runtime manifest before running them. It dispatches a finite verb table (`admit`, `status`, `doctor`) with `--no-global-search-paths`. Before any snapshot code runs it validates the checksum record's grammar and verifies the snapshot entrypoint set with the host digest tool.
- `src/installation/admit.ts`: admission from a trusted source into an operator-selected control root. It guards the trusted-source shape, records the release identity from the trusted source, and records the Node and npm identities. It checks lock origins and `allowScripts`. The fetch phase is a scripts-disabled `npm ci` with pinned configuration: `--no-bin-links`, empty user and global config, a pinned registry, and proxy variables only here. The build phase runs allowlisted packages (none in production) through CORE-02 `containedCommand`. It then binds the release after the build, records an exact installed inventory, and publishes in one fail-closed order under an exclusive-create lock with no reselection.
- `src/commands/doctor.ts`: read-only installed diagnostics run only through the controller: state table, exact inventory, release binding, own-executable identity, environment check, checkout attestation (`matches-admitted-release` or `unadmitted-fork`), `providerReadiness` kept separate.
- `src/contracts/installation.ts`: frozen record fields (admission record, snapshot record, installed files, runtime record, selection) and the diagnostic list.
- Fixtures: `runtime-admission` (35 offline cases, in `bin/check`) and `admission-containment` (11 host-only cases under a real sandbox mechanism), both registered in `verify.ts`; fixture packages under `assets/admission-fixtures/` built by `scripts/admission-fixtures.mjs`.
- `launcher.mjs` gains `qualify runtime-admission`, `qualify admission-containment`, `status` and `doctor` (forwarded to `<control-root>/loam-control`); no `admit` verb. `assets/runtime-manifest.json` gains an `admission` block. `SETUP.md` documents the trust root, commands, layout, states and residuals.

- Answers to the candidate-05 review's six repairs: `payload/package.json` joins the pre-dispatch digest set; doctor validates the registry records; the controller validates the checksum-record grammar, the selection's trailing newline and control characters in paths; a failed fetch leaves no proxy-bearing log; the contained child writes a start marker so a wrapper refusal is `containment-unavailable`; the `cc` shim runs inside containment; a fixture-only pause seam proves the late-contender refusal. Details: `candidate-07/repairs.md`.

## Verified results (candidate-07)

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

Full `bin/check` from a `$TMPDIR` clone of candidate-07 on the Mac: `check: PASSED` (the full check runs on one host; the qualification above ran on both). Render gate 2/2. Fixture tarballs drift-free. `candidateUnchanged` and `digestMatches` true on both hosts.

Evidence on the Mac: `~/.local/state/loam/build-evidence/CORE-04/` (baseline, reconciled packet, reading records, both-host probes, advisors, builders, red and green logs, negative probes, `candidate-07/{candidate.json,full-check.log,render-gate.log,fixture-drift.json,departures.md,repairs.md,mac/}`; `candidate-07/mac/` holds `qualification.json`, `containment-mechanism.json` and the walkthrough logs); reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan-01 to plan-03 with Codex verdicts, candidate-01/lean-critic-setup.md, candidate-04 handoff lean-critic, the candidate-05 Codex verdict, and the candidate-07 Codex verdict once written). Linux keeps its own copy under the same path on jhaveris.

## Unmet and deferred

- "Both provider payloads ship" is unmet by operator decision (2026-09-16). Successor: https://github.com/SamyakJhaveri/loam/issues/140 (CORE-04b). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately from installation availability.

## Departures from plan-03 and the review R-list

See `candidate-07/departures.md`, items 1-20. Items 1-8 carry from candidate-06 (item 5 now records the Mac population running unsandboxed inside `qualify-host.py`; item 6 stays closed by item 8). The new items 9-20:

- 9: the candidate-05 verdict was complete with R1-R6, candidate-06 was never sent for review, and candidate-07 is the first candidate to answer all six.
- 10: R3's proxy fetch-only proof is at the `trustedSpawnEnvironment` boundary because the offline fetch runs `--ignore-scripts` and `--offline`; the executed-child negative half stays in `contain.build-no-proxy-or-credentials`.
- 11: the shell checksum grammar validates the four fixed entries plus the digest tool's per-file check; it does not re-derive the payload/dist set (doctor's inventory does).
- 12: record corruption reuses `install-interrupted` rather than a new diagnostic.
- 13: the proxy sentinel in `admission.dependency-missing` is generated at run time because a static literal would appear in test sources copied into the payload.
- 14: the wrapper-refusal seam runs a real contained child that exits without the start marker; it does not reproduce a real bwrap namespace failure.
- 15: `admission.snapshot-runs-without-checkout` removes the checkout and a disposable toolchain copy; cache and home are workspace transients removed at seal, so there is no external name to remove.
- 16: `/usr/bin/sort` joins the trusted OS program list, used only for duplicate-path detection.
- 17: the `cc` execution proof asserts the shim ran (exec'd without ENOENT), not that `cc` exited zero, because a sandboxed `cc` can fail on a denied cache write.
- 18: doctor parses the registry records as `unknown` then narrows and double-casts (the spec's TypeScript-narrowing fallback), and drops the optional `HEX16` constant to avoid an unused-variable lint.
- 19: the public `--clean` refusal is a test-only addition; the code already refused both placements.
- 20: the contained-child start marker lives at `<workspace>/tmp/.loam-contained-started`, written by the `/bin/sh` prologue and computed with `realpathSync` so it survives on both hosts.

## Limits that stay

- `supportedRuntime` remains false. This is mechanical foundation work, not managed-execution acceptance.
- Between runs any same-user process can rewrite the snapshot, both inventories, the registry records and the controller copy together, undetectably. The trust boundary is the operator's review at admission plus CORE-02 containment during a contained build.
- The controller cannot protect its own first startup (native loader variables and the shell's startup) and trusts `/bin/sh`, `/usr/bin/env`, `/usr/bin/mktemp`, `/usr/bin/uname`, the digest tool, `grep`, `sed`, `cut` and `sort` as operating-system components.
- One admission per control root; a complete but unselected snapshot is reported as interrupted; recovery is manual removal.
- The Mac containment profile protects only registered paths. CORE-02's limits (non-atomic prelaunch admission, truthful link counts, hard-link refusal, no discovery of removed-original aliases) are unchanged.

## Follow-ups (not in this ticket)

- `SETUP.md` says the controller's scratch directory is created under `TMPDIR`; the controller falls back to `/tmp` when `TMPDIR` is unset (`loam-control.sh`, the `mktemp` line). Wording fix only (lean-critic, candidate-07).
- The landed sanitizers disagree: `native-boundary.ts` `shouldStrip` does not strip `npm_config_*`; `toolchain.mjs` `cleanEnvironment` and `verify.ts` `cleanTestEnvironment` do not strip `LD_PRELOAD`, `DYLD_*`, `NODE_TLS_REJECT_UNAUTHORIZED`, `NODE_EXTRA_CA_CERTS` or `OPENSSL_CONF`. CORE-04 uses its own allowlists and did not edit those modules.
- The controller leaves its `mktemp` scratch home behind after each run.
- Garbage collection of superseded snapshots (about 120 MB each with the copied Node and npm).
- `admission.snapshot-collision` was dropped as unreachable under the one-admission rule.

## Next

CORE-05 (typed authoritative transactions) per core-02-acceptance.md, after the CORE-04 PR merges. NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md`; whichever merges second rebases, rebuilds and requalifies both hosts.
