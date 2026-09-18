# CORE-04 handoff: admit an isolated installed runtime from an independent trust source

Status: candidate-10 (`0f24cf202806c9292cf38af389f9f4e6db93fd65`, factory tree `2bdb500988e334f0dfc9e05edef37f2508332de3`) on branch `core-04-runtime-admission` from main `e4c6f47`, on top of candidate-09 `f410b50`. Both hosts qualified the same frozen candidate (Mac arm64 under sandbox-exec, jhaveris Linux x64 under bwrap); full check passed. Pull request: https://github.com/SamyakJhaveri/loam/pull/141 (open, head candidate-10, not merged). Codex history: candidate-05 BLOCK (R1-R6), candidate-08 BLOCK (B1-B3), candidate-09 BLOCK (B1-B3 remaining, new B4); candidate-10 answers them and its review is pending. The operator reopened the ticket on 2026-09-18, so candidate-10 is a fourth Codex round by his decision. Merge waits for the operator.

## What shipped

- `scripts/loam-control.sh`: the trusted operator setup and control entrypoint. POSIX `sh`, dependency free. It re-executes itself under `/usr/bin/env -i` with a fixed `PATH`, verifies the toolchain `bin/node` bytes against the trusted runtime manifest before running them, dispatches a finite verb table (`admit`, `status`, `doctor`) with `--no-global-search-paths`, and verifies the snapshot entrypoint set with the host digest tool, the startup import closure, the startup metadata and the selected Node's executability before any snapshot code runs.
- `src/installation/admit.ts`: admission from a trusted source into an operator-selected control root: trusted-source shape guard, release identity recorded from the trusted source, Node and npm identities, lock-origin and `allowScripts` checks, a scripts-disabled `npm ci` fetch phase with pinned configuration, a contained build phase through CORE-02 `containedCommand`, post-build release binding, an exact installed inventory, a computed startup-closure manifest, and a single fail-closed publication order with an exclusive-create lock and no reselection.
- `src/commands/doctor.ts`: read-only installed diagnostics run only through the controller, with complete admission-record shape and internal-consistency relationship validation, defensive inventory reads, checkout attestation, and `providerReadiness` kept separate.
- `src/contracts/installation.ts`: frozen record fields and the diagnostic list.
- Fixtures: `runtime-admission` (35 offline cases, in `bin/check`) and `admission-containment` (11 host-only cases under a real sandbox mechanism); fixture packages under `assets/admission-fixtures/`.
- `launcher.mjs` gains `qualify runtime-admission`, `qualify admission-containment`, `status` and `doctor`; no `admit` verb. `assets/runtime-manifest.json` gains an `admission` block. `SETUP.md` documents the trust root, commands, layout, states and residuals.

Repairs answering the candidate-05 review (R2-R5) and candidate-08 review (B1-B3, first form) are carried; see the candidate-07 through candidate-09 handoffs.

Repairs answering the candidate-09 Codex review (B1-B4): admission writes a startup-closure manifest listing the doctor entrypoint's six-module import closure, made a required checksum entry, and the controller cross-checks that every closure path is a record entry before dispatch, so a required startup module cannot disappear from the record before Node loads it (B1). Doctor validates the complete admission-record contract and the internal-consistency relationships among the recorded tool digests, the installed inventory and the payload release manifest, so an incomplete or inconsistent record no longer reports healthy (B2). The checksum grammar regressions are isolated with real recorded targets that pass the raw digest tool, so only the grammar can account for each refusal (B3). The controller refuses a symlinked, missing or non-executable selected Node before dispatch, and doctor converts an unreadable installed file into a structured `installed-file-altered` instead of a raw permission error (B4).

## Verified results (candidate-10)

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

Full `bin/check` from a `$TMPDIR` clone of candidate-10 on the Mac: `check: PASSED` (the full check runs on one host; the qualification above ran on both). Render gate 2/2. Fixture tarballs drift-free. `candidateUnchanged` and `digestMatches` true on both hosts.

Evidence on the Mac: `~/.local/state/loam/build-evidence/CORE-04/` (baseline, reconciled packet, reading records, both-host probes, advisors, builders, red and green logs, negative probes, `candidate-10/{candidate.json,render-gate.log,fixture-drift.json,independent-probe.mjs,independent-probe-results.json,departures.md,repairs.md,mac/,linux/}`; the host records seal under `candidate-10/mac/` and `candidate-10/linux/`); reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan verdicts, the candidate-05, candidate-08 and candidate-09 Codex verdicts, the candidate-07 pre-screen, and the candidate-10 Codex verdict once written). Linux keeps its own copy under the same path on jhaveris.

## Unmet and deferred

- "Both provider payloads ship" is unmet by operator decision (2026-09-16). Successor: https://github.com/SamyakJhaveri/loam/issues/140 (CORE-04b). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately.

## Departures from plan-03 and the review R-list

See `candidate-10/departures.md`, items 1-38. Items 1-8 carry from candidate-06; 9-20 from candidate-07; 21-27 from candidate-08; 28-32 from candidate-09; 33-38 record candidate-10. In one line each, the candidate-10 items:

- 33: B1 writes a startup-closure manifest (six paths), makes it a required checksum entry, and cross-checks every closure path against the record before the metadata scan.
- 34: the closure generator uses `String.raw`/`new RegExp` because the build's import-closure scanner does not parse regex literals, following `package.ts`.
- 35: B2 relationship checks are internal consistency against the inventory and the payload release manifest; the source/output/dependency digests and gitDescribe are shape-checked only, to stay off self-authenticating-receipt ground.
- 36: B4 also refuses a symlinked selected Node.
- 37: B3 grammar-only records are the full healthy record plus one extra real-target line (`doctor.js.map`) proven to pass the raw digest tool.
- 38: the operator reopened the ticket on 2026-09-18 after the earlier cap, so candidate-10 is a fourth Codex round by his decision; this supersedes item 32.

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

The candidate-10 Codex review (`reviews/CORE-04/candidate-10/codex-verdict.md`, GPT-6) is BLOCK on one remaining item: R1-R6, B1, B3 and B4 repaired; B2 partial. Remaining: compare the record's aggregate release digests (sourceDigest, outputDigest, dependencyDigest) with the installed release manifest; validate platform, arch, Node, SQLite and npm identity fields against the admitted binaries and installed metadata; check the deterministic snapshot ID relationship; classify a record-only per-file digest mismatch as install-interrupted; add single-field mismatch cases. Opening candidate-11 is the operator decision. On APPROVE, the merge still waits for the operator's explicit instruction. On BLOCK, the operator decides whether to run a further round. After merge: CORE-05 (typed authoritative transactions) per core-02-acceptance.md. NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md`; whichever merges second rebases, rebuilds and requalifies both hosts.
