# CORE-04 handoff: admit an isolated installed runtime from an independent trust source

Status: candidate-09 (`f410b509b912fa42bfad8371aade7ae6656ffdfe`, factory tree `b6866decdfd5817155c94a9becaf01f367d546a0`) on branch `core-04-runtime-admission` from main `e4c6f47`, on top of candidate-08 `edf0ccd`. Both hosts qualified the same frozen candidate (Mac arm64 under sandbox-exec, jhaveris Linux x64 under bwrap); full check passed. Pull request: https://github.com/SamyakJhaveri/loam/pull/141 (open, head candidate-09, not merged). Codex: the candidate-08 review was BLOCK with repairs B1-B3; candidate-09 answers them. The candidate-09 Codex review (`reviews/CORE-04/candidate-09/codex-verdict.md`, GPT-6) is BLOCK: R1, R4, R5 and R6 repaired; R2, R3, B1, B2 and B3 partially repaired; one new item B4. Remaining repairs: B1 require every imported startup module in the checksum record and derive the metadata scan only after that closure is complete; B2 validate the full admission record contract and its identity relationships (missing fields, false digests and a truncated release map still report healthy); B3 build the grammar-only checksum regressions from real disposable targets with matching digests; B4 refuse a non-executable selected Node before dispatch and turn inventory hash/stat failures into structured diagnostics. This was the third and last Codex round by the operator's decision, so the ticket is STOPPED with this handoff; reopening it is the operator's call. Do not merge.

## What shipped

- `scripts/loam-control.sh`: the trusted operator setup and control entrypoint. POSIX `sh`, dependency free. It re-executes itself under `/usr/bin/env -i` with a fixed `PATH`, verifies the toolchain `bin/node` bytes against the trusted runtime manifest before running them, dispatches a finite verb table (`admit`, `status`, `doctor`) with `--no-global-search-paths`, and verifies the snapshot entrypoint set with the host digest tool before any snapshot code runs.
- `src/installation/admit.ts`: admission from a trusted source into an operator-selected control root: trusted-source shape guard, release identity recorded from the trusted source, Node and npm identities, lock-origin and `allowScripts` checks, a scripts-disabled `npm ci` fetch phase with pinned configuration, a contained build phase through CORE-02 `containedCommand` for allowlisted packages (empty in production), post-build release binding, an exact installed inventory, and a single fail-closed publication order with an exclusive-create lock and no reselection.
- `src/commands/doctor.ts`: read-only installed diagnostics run only through the controller: state table, exact inventory, release binding, own-executable identity, environment check, checkout attestation, `providerReadiness` kept separate.
- `src/contracts/installation.ts`: frozen record fields and the diagnostic list.
- Fixtures: `runtime-admission` (35 offline cases, in `bin/check`) and `admission-containment` (11 host-only cases under a real sandbox mechanism), both registered in `verify.ts`; fixture packages under `assets/admission-fixtures/`.
- `launcher.mjs` gains `qualify runtime-admission`, `qualify admission-containment`, `status` and `doctor`; no `admit` verb. `assets/runtime-manifest.json` gains an `admission` block. `SETUP.md` documents the trust root, commands, layout, states and residuals.

Repairs answering the candidate-05 review (R2-R5): the pre-dispatch digest set covers `payload/package.json` and doctor validates the registry records; the controller validates the checksum grammar, the selection trailing newline and control characters; a contained child writes a start marker so a wrapper refusal classifies `containment-unavailable`; a fixture-only pause seam proves the late contender. Candidate-08 closed four pre-screen minors.

Repairs answering the candidate-08 Codex review (B1-B3): the controller verifies startup metadata presence and absence before Node dispatch by deriving the directory set from the checksum record and refusing any unexpected nearer `package.json` or `node_modules` (B1); doctor validates the complete admission and inventory record shapes before reporting healthy or dereferencing fields, so an empty release map no longer certifies and a wrong-shape value no longer throws (B2); `contains_control` now catches a newline at any position including trailing, and rotated `--protect-*` values are validated, with the checksum grammar regressions made independent of the altered-doctor setup (B3).

## Verified results (candidate-09)

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

Full `bin/check` from a `$TMPDIR` clone of candidate-09 on the Mac: `check: PASSED` (the full check runs on one host; the qualification above ran on both). Render gate 2/2. Fixture tarballs drift-free. `candidateUnchanged` and `digestMatches` true on both hosts.

Evidence on the Mac: `~/.local/state/loam/build-evidence/CORE-04/` (baseline, reconciled packet, reading records, both-host probes, advisors, builders, red and green logs, negative probes, `candidate-09/{candidate.json,render-gate.log,fixture-drift.json,departures.md,repairs.md,mac/,linux/}`; `candidate-09/mac/` and `candidate-09/linux/` hold the qualification records and walkthrough logs once the runs seal); reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan verdicts, the candidate-05 and candidate-08 Codex verdicts, the candidate-07 pre-screen, and the candidate-09 Codex verdict once written). Linux keeps its own copy under the same path on jhaveris.

## Unmet and deferred

- "Both provider payloads ship" is unmet by operator decision (2026-09-16). Successor: https://github.com/SamyakJhaveri/loam/issues/140 (CORE-04b). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately.

## Departures from plan-03 and the review R-list

See `candidate-09/departures.md`, items 1-32. Items 1-8 carry from candidate-06; items 9-20 record candidate-07; items 21-27 record candidate-08 (item 1 drops `registry` from the asserted effective-config values and item 11 drops the false claim that doctor catches every extra file, per the candidate-08 Codex corrections); items 28-32 record candidate-09. In one line each, the candidate-09 items:

- 28: B1 derives the directory set from the checksum record and checks it with the trusted helpers, not `find`; `node_modules` refusal is hardening because the import graph has no bare imports.
- 29: B2 validates `files` (the map whose emptiness caused the false healthy) as a non-empty release map and `release` as a ReleaseIdentity with four 64-hex digest fields.
- 30: the B1 metadata cases prove non-dispatch by the shell's top-level unavailable line and the absence of Node loader errors, because a marker would alter doctor.js bytes and the digest check would refuse first.
- 31: the `is_absolute` guard on `--protect-*` values has no positive shell case; `admit.js` re-validates.
- 32: candidate rounds are candidate-05 BLOCK, candidate-08 BLOCK, and candidate-09 as the third and last Codex round by the operator's decision on 2026-09-17.

## Limits that stay

- `supportedRuntime` remains false. This is mechanical foundation work, not managed-execution acceptance.
- Between runs any same-user process can rewrite the snapshot, both inventories, the registry records and the controller copy together, undetectably. The trust boundary is the operator's review at admission plus CORE-02 containment during a contained build.
- The controller cannot protect its own first startup (native loader variables and the shell's startup) and trusts `/bin/sh`, `/usr/bin/env`, `/usr/bin/mktemp`, `/usr/bin/uname`, the digest tool, `grep`, `sed`, `cut` and `sort` as operating-system components.
- One admission per control root; a complete but unselected snapshot is reported as interrupted; recovery is manual removal.
- The Mac containment profile protects only registered paths. CORE-02's limits (non-atomic prelaunch admission, truthful link counts, hard-link refusal, no discovery of removed-original aliases) are unchanged.

## Follow-ups (not in this ticket)

- The landed sanitizers disagree: `native-boundary.ts` `shouldStrip` does not strip `npm_config_*`; `toolchain.mjs` `cleanEnvironment` and `verify.ts` `cleanTestEnvironment` do not strip `LD_PRELOAD`, `DYLD_*`, `NODE_TLS_REJECT_UNAUTHORIZED`, `NODE_EXTRA_CA_CERTS` or `OPENSSL_CONF`. CORE-04 uses its own allowlists and did not edit those modules.
- `json_escape` (`loam-control.sh:36`) still does not escape the C0 range, so the staging-glob echo at `loam-control.sh:166` would emit a raw control byte if a same-user writer planted a control-character filename under `runtimes/`. Within the accepted same-user residual and not caller-reachable; noted for a future hardening pass.
- Garbage collection of superseded snapshots (about 120 MB each with the copied Node and npm).
- `admission.snapshot-collision` was dropped as unreachable under the one-admission rule.

## Next

The ticket is stopped at the review gate. To reopen: start from `candidate-09/round2-uncommitted.patch` (stricter B2 validators and grammar-only records built with real digests, uncommitted, never reviewed) and the candidate-09 verdict's B1-B4, freeze a candidate-10, requalify both hosts, and run a fresh Codex review. CORE-05 (typed authoritative transactions) per core-02-acceptance.md follows the CORE-04 merge. NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md`; whichever merges second rebases, rebuilds and requalifies both hosts.
