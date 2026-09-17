# CORE-04 handoff: admit an isolated installed runtime from an independent trust source

Status: candidate-08 (`edf0ccd1568e7ebd84bc27c92cd2c542e5c16f3a`, factory tree `112598bf9407b372fd9f9f1b30c1e4ce485a678d`) on branch `core-04-runtime-admission` from main `e4c6f47`, on top of candidate-07 `90aafd9`. Both hosts qualified the same frozen candidate (Mac arm64 under sandbox-exec, jhaveris Linux x64 under bwrap); full check passed. Pull request: https://github.com/SamyakJhaveri/loam/pull/141 (open, head candidate-08, not merged). The Codex finished-work review has NOT run: the operator paused Codex usage on 2026-09-17; it is the one open gate. A fresh-context Claude pre-screen of candidate-07 found no blocking or major finding; its minors are closed in candidate-08. Merge waits for the operator and for the Codex review.

## What shipped

- `scripts/loam-control.sh`: the trusted operator setup and control entrypoint. POSIX `sh`, dependency free. It re-executes itself under `/usr/bin/env -i` with a fixed `PATH`, verifies the toolchain `bin/node` bytes against the trusted runtime manifest before running them, dispatches a finite verb table (`admit`, `status`, `doctor`) with `--no-global-search-paths`, and verifies the snapshot entrypoint set with the host digest tool before any snapshot code runs.
- `src/installation/admit.ts`: admission from a trusted source into an operator-selected control root: trusted-source shape guard, release identity recorded from the trusted source, Node and npm identities, lock-origin and `allowScripts` checks, a scripts-disabled `npm ci` fetch phase with pinned configuration (`--no-bin-links`, empty user and global config, registry pinned, proxy variables only here), a contained build phase through CORE-02 `containedCommand` for allowlisted packages (empty in production), post-build release binding, an exact installed inventory, and a single fail-closed publication order with an exclusive-create lock and no reselection.
- `src/commands/doctor.ts`: read-only installed diagnostics run only through the controller: state table, exact inventory, release binding, own-executable identity, environment check, checkout attestation (`matches-admitted-release` or `unadmitted-fork`), `providerReadiness` kept separate.
- `src/contracts/installation.ts`: frozen record fields (admission record, snapshot record, installed files, runtime record, selection) and the diagnostic list.
- Fixtures: `runtime-admission` (35 offline cases, in `bin/check`) and `admission-containment` (11 host-only cases under a real sandbox mechanism), both registered in `verify.ts`; fixture packages under `assets/admission-fixtures/` built by `scripts/admission-fixtures.mjs`.
- `launcher.mjs` gains `qualify runtime-admission`, `qualify admission-containment`, `status` and `doctor` (forwarded to `<control-root>/loam-control`); no `admit` verb. `assets/runtime-manifest.json` gains an `admission` block. `SETUP.md` documents the trust root, commands, layout, states and residuals.

Repairs answering the candidate-05 review (R2-R5):

- R2: the pre-dispatch digest set covers `payload/package.json` (the file Node reads at bootstrap), so a malformed or type-changed metadata file is refused as `installed-file-altered` before dispatch, not a Node crash; doctor validates the registry records and returns a structured `install-interrupted`.
- R3: the controller validates the checksum-record grammar, requires the selection's trailing newline for shell and Node parity, and rejects control characters in operator-supplied paths; a failed fetch leaves no proxy-bearing log.
- R4: the contained child writes a start marker as its first act, so a wrapper that refuses before the child starts is classified `containment-unavailable`, and the declared `cc` shim is exercised inside containment.
- R5: a fixture-only late-contender pause seam proves a contender refuses under a live admission's lock and the detached snapshot runs after the checkout and a disposable toolchain are removed.

Candidate-08 also closes four minor findings of a fresh-context Claude pre-screen of candidate-07: the two generic usage-error echoes reject control characters with a constant detail, checksum rule 4 is anchored to the path column, the admit argument rotator uses a counter instead of a sentinel word, and doctor reads the sealed inventory defensively when invoked directly.

## Verified results (candidate-08)

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

Full `bin/check` from a `$TMPDIR` clone of candidate-08 on the Mac: `check: PASSED` (the full check runs on one host; the qualification above ran on both). Render gate 2/2. Fixture tarballs drift-free. `candidateUnchanged` and `digestMatches` true on both hosts.

Evidence on the Mac: `~/.local/state/loam/build-evidence/CORE-04/` (baseline, reconciled packet, reading records, both-host probes, advisors, builders, red and green logs, negative probes, `candidate-08/{candidate.json,render-gate.log,fixture-drift.json,departures.md,repairs.md,mac/,linux/}`; `candidate-08/mac/` and `candidate-08/linux/` hold the qualification records and walkthrough logs once the runs seal); reviews under `~/.local/state/loam/build-evidence/reviews/CORE-04/` (plan-01 to plan-03 with Codex verdicts, the candidate-05 Codex verdict, the candidate-07 fresh-context pre-screen, and the Codex finished-work verdict once written). Linux keeps its own copy under the same path on jhaveris.

## Unmet and deferred

- "Both provider payloads ship" is unmet by operator decision (2026-09-16). Successor: https://github.com/SamyakJhaveri/loam/issues/140 (CORE-04b). The admission record carries `providers.payloads: []` and the successor link; doctor reports `providerReadiness: not-evaluated` separately from installation availability.

## Departures from plan-03 and the review R-list

See `candidate-08/departures.md`, items 1-27. Items 1-8 carry from candidate-06; items 9-20 record candidate-07; items 21-27 record candidate-08. In one line each, the candidate-08 items:

- 21: the candidate-07 pre-screen ran as fresh-context Claude agents through a dynamic workflow because Codex is paused; it is a pre-screen, not the reviewer of record, and the Codex review is still required.
- 22: candidate-06, -07 and -08 all answer the single candidate-05 BLOCK and none has been reviewed, so the lead counts them as one repair round; Samyak may overrule.
- 23: the two usage-error echoes refuse control characters with a constant detail instead of escaping; the staging-glob echo residual stays within the accepted same-user boundary.
- 24: checksum rule 4 is anchored to the extracted path column.
- 25: the admit argument rotator uses a counter, not a sentinel word.
- 26: doctor reads the sealed inventory defensively when invoked directly; the controller path was already gated by the pre-dispatch digest.
- 27: the pre-screen's remaining minor (two spaces before `..`) is closed by item 24; the SETUP.md TMPDIR wording is the only other change.

## Limits that stay

- `supportedRuntime` remains false. This is mechanical foundation work, not managed-execution acceptance.
- Between runs any same-user process can rewrite the snapshot, both inventories, the registry records and the controller copy together, undetectably. The trust boundary is the operator's review at admission plus CORE-02 containment during a contained build.
- The controller cannot protect its own first startup (native loader variables and the shell's startup) and trusts `/bin/sh`, `/usr/bin/env`, `/usr/bin/mktemp`, `/usr/bin/uname`, the digest tool, `grep`, `sed`, `cut` and `sort` as operating-system components.
- One admission per control root; a complete but unselected snapshot is reported as interrupted; recovery is manual removal.
- The Mac containment profile protects only registered paths. CORE-02's limits (non-atomic prelaunch admission, truthful link counts, hard-link refusal, no discovery of removed-original aliases) are unchanged.

## Follow-ups (not in this ticket)

- The landed sanitizers disagree: `native-boundary.ts` `shouldStrip` does not strip `npm_config_*`; `toolchain.mjs` `cleanEnvironment` and `verify.ts` `cleanTestEnvironment` do not strip `LD_PRELOAD`, `DYLD_*`, `NODE_TLS_REJECT_UNAUTHORIZED`, `NODE_EXTRA_CA_CERTS` or `OPENSSL_CONF`. CORE-04 uses its own allowlists and did not edit those modules.
- The controller leaves its `mktemp` scratch home behind after each run; SETUP.md documents the lifetime.
- `json_escape` in the controller still escapes only backslash and double quote. Every caller-reachable value is refused before formatting when it carries a control character; the one remaining raw interpolation is a staging directory name inside the control root, which is the accepted same-user residual.
- Garbage collection of superseded snapshots (about 120 MB each with the copied Node and npm).
- `admission.snapshot-collision` was dropped as unreachable under the one-admission rule.

## Next

CORE-05 (typed authoritative transactions) per core-02-acceptance.md, after the CORE-04 PR merges. NATIVE-05 (#117) shares `launcher.mjs`, `verify.ts`, `package.test.ts`, `release-manifest.json`, `bin/check` and `SETUP.md`; whichever merges second rebases, rebuilds and requalifies both hosts.
