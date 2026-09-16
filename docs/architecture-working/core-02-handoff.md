# Historical CORE-02 handoff: candidate-03 before the repair review

Superseded by [CORE-02 acceptance](core-02-acceptance.md). PR #139 is merged; the final reviewed and qualified candidate is `031795f`, not the candidate described below. Preserve this record as history, not current instructions.

Status on 2026-09-16: the CORE-02 candidate is implemented, qualified on both hosts including the Mac plain-terminal containment run, checked with `bin/check`, and reviewed. It is not merged. Merge waits for one thing: a fresh Codex/Astra review on or after 2026-09-19.

Ticket: [#104](https://github.com/SamyakJhaveri/loam/issues/104). Campaign: [#102](https://github.com/SamyakJhaveri/loam/issues/102). Predecessor: [core-01-handoff.md](core-01-handoff.md).

## The candidate

Branch `core-02-storage-containment`, PR https://github.com/SamyakJhaveri/loam/pull/139, base main `2f0a845`. Candidate commit eacd020ec342969385d1d5600c1f3b7c01f02308 (tree d90a48d2), candidate-03. Worktree on this Mac: `/private/tmp/loam-core-02`. Worktree on jhaveris: `~/Desktop/loam-core-02`.

What shipped under `seed/.loam/factory/`:

- `src/platform/runtime.ts`: runtime identity (version, arch, bundled SQLite, executable digest) checked against `assets/runtime-manifest.json`; children are always spawned from `process.execPath`, never from PATH; a mismatch reports a precise unavailable status.
- `src/platform/ownership.ts`: stores open only through an internally built, percent-encoded `file:` URI with `mode=rw`, so a missing file is refused and nothing is ever created; empty, foreign and corrupt files are refused by an application-id check; effective settings are read back. The lifetime lock is the SQLite exclusive file lock held by a `node:sqlite` connection on `owner.lock`. There is no unlink, rotate, heartbeat or timeout-steal. Replaced paths are detected by comparing the stored device and inode numbers against a fresh `stat`. The module never opens a second descriptor on the lock, because closing any descriptor drops every POSIX record lock the process holds on that file.
- `src/platform/store-worker.ts`: the store connection on a worker thread, so a busy SQLite wait never blocks the main event loop.
- `src/platform/native-boundary.ts`: the containment boundary. Linux uses bubblewrap (`bwrap`) with a private mount namespace in which protected paths do not exist. macOS uses `sandbox-exec` with a generated profile that denies the protected control paths last, so the denial wins. Both rebuild the child environment from an allow list. `sanitizedEnvironment` strips preload, loader, package-manager and Git redirection variables before a trusted child starts, and `launcher.mjs` applies the same strip to its own environment before any child starts.
- Two fixed-case populations in `src/testing/verify.ts`: `platform-qualification` (23 cases, fixture `dist/tests/platform/qualification.test.js`) and `native-boundary` (13 cases, fixture `dist/tests/platform/native-boundary.test.js`). A skipped, missing or renamed case fails the gate; the renamed-case probe is saved as evidence.
- `launcher.mjs qualify platform` and `qualify native-boundary`. `bin/check` runs `qualify platform` after the render gate. `qualify native-boundary` is a per-host gate, not a `bin/check` or CI gate.
- `assets/runtime-manifest.json` records the bundled SQLite version and the two task-toolchain node digests. `supportedRuntime` stays false. No runtime is declared supported.

## Departures from the ticket and the design, with reasons

- Claude Code implemented, Codex reviews before merge. The runbook says Codex leads core tickets. Codex credits were exhausted until 2026-09-19, so Samyak chose this variant on 2026-09-15 (recorded in [NEXT-SESSION-PROMPT-CORE-02.md](NEXT-SESSION-PROMPT-CORE-02.md)). The opposite-model gate is kept by delaying the merge until Codex reviews the exact frozen candidate. Plan reviews were four fresh Claude Fable 5.1 contexts (BLOCK, BLOCK, BLOCK, APPROVE); this is a same-provider plan review, which the runbook's rule for Claude-led tickets does not cover. The Codex review on 2026-09-19 should read the plan as well as the diff.
- Lifetime lock through `node:sqlite` instead of the proposed `fs-ext` `flock` binding. Same operating-system primitive, no native build dependency, payload stays dependency-free. Measured on both hosts by the six `lock.*` cases.
- Four source files instead of the ticket's two. `runtime.ts` and `store-worker.ts` were added; only `runtime.ts` and `native-boundary.ts` read `process.platform`.
- Two populations instead of filling the single `platform-qualification` placeholder. `native-boundary` is registered available because its fixture exists; it passes on Linux, with Mac containment pending (open item 1). OPS-10 obligation: `native-boundary` is proved only by the two-host `qualify native-boundary` run, driven per host by `qualify-host.py` (open item 2); OPS-10 closure must add a CI host with bwrap or formally accept the per-candidate host evidence as the gate. Reverse with `available: false` if the campaign prefers a missing-fixture entry.
- The ticket names `node --test <both fixtures>` as the future command. Bare `node --test` exits 0 when every case is skipped, so the gates use `runFixedFixture`. `qualify-host.py` still runs the literal command as its first recipient check.
- The macOS profile allows reads outside the protected control root (global `file-read*`, then last-wins denies of the six protected paths). The narrower system-path allow list in the plan was not used because the profile cannot be exercised inside an agent sandbox and a too-narrow list would fail Node startup on the owner's manual run. Tightening the profile is an open item.
- Seatbelt lesson, measured on candidate-02: a deny written as `file*` loses to an earlier `allow file-read*` whatever its position, because Seatbelt gives the more specific operation name precedence. Samyak's first plain-terminal run leaked every read denial. Candidate-03 denies `file-read* file-write*` on the same operations, decided by order with the last rule winning, and the rerun observed all 13 denials.

## Evidence

Under `~/.local/state/loam/build-evidence/` on this Mac:

- `CORE-02/baseline.json`: `bin/check` on main `2f0a845`, `check: PASSED`.
- `CORE-02/reconciled-packet.json`: the 13 packet sources match the frozen approved packet; only the live `START-NEXT-SESSION.md` drifted (re-pointed after CORE-01), recorded as a successor.
- `CORE-02/reading/`: process rules, design decisions, package map, both-host probe.
- `reviews/CORE-02/plan-01..04/`: plan, ticket, verdict, input hashes per round; `plan-review-manifest.json`.
- `CORE-02/red/`: the three red logs (stubs throwing `not implemented`, old registry assertion).
- `CORE-02/candidate-01/`: the first frozen candidate `364dd73` (diff, manifest, `full-check.log` with `check: PASSED`, `jhaveris-02/` and `mac-sandboxed-02/` qualification records) and its fresh Fable review (APPROVE). A prose critic then required three comment fixes in shipped seed source.
- `CORE-02/candidate-02/`: candidate `9b6aea0` (candidate-01 plus the comment fixes). Reviewed APPROVE. Its `mac-terminal/` run by Samyak from a plain Terminal exposed the Seatbelt precedence defect: eight `boundary.*` read-denial cases leaked.
- `CORE-02/candidate-03/`: the final candidate `eacd020` (candidate-02 plus the one-line profile fix). `candidate.diff`, `interdiff-from-candidate-02.diff`, `manifest.json`, `full-check.log` (`check: PASSED`), `jhaveris/qualification.json` (status passed, five commands exit 0, candidate unchanged, node digest matches), `mac-terminal/qualification.json` (status passed, 36 of 36 recipient cases, 13 observed denials in `observed-4.jsonl`, run by Samyak outside any agent sandbox).
- `CORE-02/negative/renamed-case.log`: one renamed case fails `qualify platform`.
- `reviews/CORE-02/candidate-01/verdict.md`, `candidate-02/verdict.md` and `candidate-03/verdict.md`: the fresh Fable finished-work reviews. `candidate-01/lean-critic-docs.md` and `candidate-02/lean-critic-records.md`: the prose passes.
- `CORE-02/qualify-host.py`: the per-host qualification script.

## Open items

1. Mac plain-terminal containment run: done on candidate-03 by Samyak on 2026-09-16, status passed. If the candidate changes again, rerun from a normal Terminal window, not inside any agent session:

   ```
   cd /private/tmp/loam-core-02 && git checkout <candidate-sha> && \
   python3 ~/.local/state/loam/build-evidence/CORE-02/qualify-host.py \
     /private/tmp/loam-core-02 \
     ~/.local/state/loam/toolchains/node-v24.21.0-darwin-arm64 \
     ~/.local/state/loam/build-evidence/CORE-02/candidate-NN/mac-terminal
   ```

   Pass condition: `mac-terminal/qualification.json` shows `status: passed` and `candidateUnchanged: true`.
2. CI does not run `qualify native-boundary`. The GitHub runner has no bwrap and no unsandboxed Mac. Recorded for OPS-10.
3. The macOS profile could be tightened to deny the home directory outside the workspace and runtime once the plain-terminal run passes.
4. No runtime is declared supported. The pin stays a qualification candidate.

## Codex review on or after 2026-09-19

Run from `/Users/samyakjhaveri/Desktop/loam` in a new Codex session with Astra at the usual effort. Paste:

```text
Review, do not implement. Loam ticket CORE-02 (https://github.com/SamyakJhaveri/loam/issues/104)
was implemented by a Claude Code session; you are the opposite-model reviewer that gates the merge.

Read AGENTS.md, docs/architecture-working/core-02-handoff.md, the ticket, and the approved plan at
~/.local/state/loam/build-evidence/reviews/CORE-02/plan-04/plan.md. Then review the exact frozen
candidate: PR https://github.com/SamyakJhaveri/loam/pull/139, commit eacd020ec342969385d1d5600c1f3b7c01f02308, in the worktree /private/tmp/loam-core-02
(run: git -C /private/tmp/loam-core-02 rev-parse HEAD, and stop if it differs).

Judge against every acceptance bullet of the ticket. Check the evidence under
~/.local/state/loam/build-evidence/CORE-02/candidate-03/ and reviews/CORE-02/, including
mac-terminal/qualification.json (status passed, run by the owner from a plain Terminal) and
candidate-02/mac-terminal/check-1.log (the leak that the candidate-03 fix closed).

Hunt for vacuous cases, denials that could come from test setup rather than the mechanism, lock
semantics errors, URI encoding gaps, macOS profile or bwrap argument mistakes, environment
sanitisation gaps, and any weakening of fixed case accounting. Judge the recorded departures in the
handoff. Return findings with severity and file:line, and a verdict of APPROVE or BLOCK with required
fixes. Write the verdict to ~/.local/state/loam/build-evidence/reviews/CORE-02/candidate-03/codex-verdict.md.
Do not merge. Do not modify the candidate.
```

If Codex returns APPROVE, merge by squash so the merged tree equals the reviewed tree, verify remote main, tick CORE-02 in #102, and close #104. If Codex returns BLOCK, fix in a new session, refreeze as candidate-04, rerun both hosts (Mac from a plain Terminal) and `bin/check`, and repeat both reviews.
