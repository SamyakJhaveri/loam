# CI performance diagnosis

Verified: the main CI bottleneck is an oversized recursion-limit test. The unchanged test took 262.133 seconds locally. A smaller input that still crosses the same limit took 1.230 seconds. The complete suite then reported `Ran 253 tests in 98.116s`, followed by `OK` (exit 0).

Scope: diagnose Loam's time to passing checks using GitHub logs, Loam-related Claude transcripts, source history, and isolated experiments. Separate hosted execution from repeated local verification. Recommend improvements without changing production behavior or publishing changes. The requested [prompting guide](https://promptessor.com/blog/gpt-6-astra-prompting-guide) informed the explicit scope, evidence requirements, and completion criteria.

## What was measured

Verified: the experiment checkout is based on `c38a02be75b2735fde8bebf26e9dc4e4b15ad48c`. During the investigation, the primary checkout moved to `4b2ea9e2e53358a1acd743b6b56458bfa3303f8a` on `main`. A direct diff confirmed that the test file, policy parser, CI workflow, and verification script were unchanged between those revisions. This investigation did not make that branch change.

Verified: these completed GitHub jobs all show their largest log gap at `test_policy_process_fails_closed_past_recursion_limit`. Times below are seconds. The hotspot column is the timestamp gap between the previous completed test line and this test's completed line. It is an approximation of that test's duration, not a separate profiler measurement. Local timing independently confirms the hotspot.

| Job | Dependency installation | Full verification | Hotspot log gap | Hotspot share |
| --- | ---: | ---: | ---: | ---: |
| [100120769551](https://github.com/SamyakJhaveri/loam/actions/runs/33589618909/job/100120769551) | 11.749 | 399.363 | 373.981 | 93.6% |
| [100575547424](https://github.com/SamyakJhaveri/loam/actions/runs/33732537307/job/100575547424) | 13.324 | 384.213 | 355.082 | 92.4% |
| [101202904847](https://github.com/SamyakJhaveri/loam/actions/runs/33928777105/job/101202904847) | 11.215 | 439.467 | 340.996 | 77.6% |
| [101248567600](https://github.com/SamyakJhaveri/loam/actions/runs/33944696002/job/101248567600) | 19.265 | 382.545 | 289.811 | 75.8% |
| [101249512586](https://github.com/SamyakJhaveri/loam/actions/runs/33945052007/job/101249512586) | 14.542 | 761.744 | 678.732 | 89.1% |

Verified: installation is measured from the pip step start to the Git identity step start. Verification is measured from stage 1 to `verify-template: PASSED`. These are not queue times or whole workflow durations. The newest job succeeded and its unit-test summary was `Ran 253 tests in 756.830s`.

## Root cause and isolated experiment

Verified: `bin/tests/test_rendered_harness_contract.py:2007` creates nested shell text by applying `shlex.quote()` inside a loop. Repeated quoting expands existing quote marks. At nesting depths 10, 11, 12, and 14, the command lengths are respectively 118145, 354345, 1062937, and 9566001 bytes. The production recursion limit is 10, and `seed/.codex/hooks/pre-tool-policy.py:674` denies when depth exceeds that limit.

Verified: commit `eec2ff064684741a6c0d71bec3d3665f28fb5d00` introduced this test with 14 wrappers. The same Claude transcript records quick verification before this work and repeated multi-minute verification afterward. The commit diff and the CI timing identify the test as the principal regression.

Verified: the temporary checkout changes only `range(14)` to `range(11)` in that test. The denial assertions stay intact. Local Python is `3.14.7`; the CI workflow requests `3.12`.

| Local check | Result |
| --- | --- |
| Original test | `Ran 1 test in 262.133s`; `OK`; exit 0 |
| Smaller-input test | `Ran 1 test in 1.230s`; `OK`; exit 0 |
| Separate process boundary probes | Safe command allowed at depth 10; denied at depths 11 and 12; each exit 0 |
| In-memory mutation control | Relaxing the recursion limit removes depth-11 denial; assertion passed |
| Complete suite with smaller input | `Ran 253 tests in 98.116s`; `OK`; exit 0 |

Verified: the single-test speedup was 213.116 times in this local comparison. This is not a measured full-CI speedup. The mutation control calls the imported helper directly; it does not mutate the separate process used by the original test. An independent source review confirmed that 11 wrappers preserve the current fail-closed boundary. A permanent change should include both the allowed and denied neighboring depths.

Verified: the production parser also repeats work. `main()` calls `_literal_tokens()` at `seed/.codex/hooks/pre-tool-policy.py:847`. `_command_denied()` tokenizes the outer command again at line 680. In a depth-12 profiling probe, total time was 4.526 seconds. The two outer tokenization calls took 1.829 and 1.766 seconds, together 79.4% of the run. This amplifies the cost of the oversized input.

## Additional causes of slow feedback

Verified: `run_policy()` at `bin/tests/test_rendered_harness_contract.py:1811` has no subprocess timeout. `.github/workflows/test.yml` also has no explicit job or step timeout. The shipped hook has a 10-second timeout in `seed/.codex/hooks.json:10`. Its internal `bash -n` timeout covers syntax checking only. It does not bound subsequent Python parsing. Tests therefore permit a long-running parser invocation that exceeds the shipped hook's time budget.

Verified: the handoff duplicates full verification. `docs/HANDOFF-2026-09-03-audit-sessions.md:350` requires both `uvx pytest -q bin/tests` and `bin/verify-template.sh` before every commit. Its review prompt at line 544 asks a reviewer to run both again. Stage 1 of `bin/verify-template.sh:13` already discovers the same `bin/tests` suite. Different Python environments can provide useful coverage, but the current instruction does not define that as a separate compatibility check.

Verified: Claude session `12ad6ece-5a01-4a34-8db5-cc5761ece5cc.jsonl:33` launches pytest at `2026-09-03T22:45:21.111Z`. Line 38 launches the full gate at `22:45:27.898Z`. Both run in the background. Line 194 records `153 passed, 367 subtests passed in 320.35s (0:05:20)` and `verify-template: PASSED`. This is repeated execution, not merely repeated wording. All transcript paths here are relative to `/Users/samyakjhaveri/.claude/projects/-Users-samyakjhaveri-Desktop-loam/`.

Verified: session `bd1e8aeb-3303-441e-ae29-db10ae7f2dc0.jsonl` invokes the full gate at lines 353, 506, 620, 694, 796, and 897. Matching completion records are at lines 393, 531, 634, 735, 839, and 905. Most checkpoints concern handoff or ticket prose. These runs follow the broad before-every-commit instruction. Polling adds conversation overhead, but it is not the cause of the GitHub test's long compute time.

Verified: session `fb540faa-256c-4fad-8f87-b12e511403a0.jsonl:667` runs `bin/verify-template.sh 2>&1 | tail -8; echo "EXIT: $?"`. Line 668 contains both `verify-template: FAILED` and `EXIT: 0`. The pipeline masks the failing gate status with the successful `tail` status. Later commands rerun verification to investigate. This is an exit-status bug in the invocation, not in CI's direct invocation of the script.

## Recommended order

1. Replace the oversized boundary fixture. Keep the shell-wrapper coverage and add depth-10 allow plus depth-11 deny cases. Keep oversized-input stress testing as a separately bounded check if desired. Verify with the affected test and the full suite. The isolated experiment already demonstrates this opportunity without changing the policy.
2. Add bounded test execution and timing output. Set a timeout on `run_policy()` and a deliberate CI time budget. Add unittest `--durations 10` and stage timings. Timeouts should fail visibly. Never treat a killed policy process as an allow decision. Python's [unittest documentation](https://docs.python.org/3.12/library/unittest.html#command-line-options) documents duration reporting.
3. Consolidate local verification ownership. Run the full gate once for the exact state being approved. Use focused checks during edits. Update the handoff and standing rules together if adopting this change. Keep intentional interpreter or integration coverage explicit. Preserve pipeline exit codes with `pipefail` or captured status. Do not skip checks based only on a file extension: some Loam prose is part of the rendered contract.
4. Harden the policy parser separately. Avoid duplicate outer tokenization. Define a bounded input size or parse-work budget with an explicit denial response. A compact `eval` chain can test the shared depth guard without quote expansion, but cannot replace shell-route coverage by itself. These are production behavior changes and need their own focused correctness review.
5. Improve CI scheduling after the main fix. Cancel obsolete runs for the same pull request using [GitHub concurrency controls](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency). Pin dependencies and cache downloads for repeatability. Installation caching has limited value against the measured hotspot. Test sharding can be reconsidered after removing the dominant serial test. Cancellation reduces obsolete work; it does not make the current parser call faster.

## Artifacts and limits

Verified: temporary artifacts are in `/private/tmp/loam-ci-diagnosis.FOJsl8/`. `checkout/` contains the isolated one-line experiment. `probe.py` contains boundary, profile, and mutation probes. `ci-evidence-complete.json` contains selected timestamped CI evidence. No code, workflow, permission setting, or standing instruction was changed in the primary checkout. This report is the only intended primary-checkout addition. Nothing was pushed, published, or deleted.

Reproduce the optimized test in that checkout with `python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -k fails_closed_past_recursion_limit -v --durations 1`. Reproduce the full suite with `python3 -m unittest discover -s bin/tests -p 'test_*.py' --durations 10`.

Risks: the optimized test has not run on GitHub. Local and CI Python versions differ. The completed CI logs explain where time went, but not why runner speed varied between runs. Queue time and billing were not measured. Removing the oversized routine fixture does not fix production handling of very large commands. The response of the live Codex host to a whole-hook timeout was not exercised. Temporary experiment files may be removed by the operating system; the diagnosis remains in this report.
