# Verified agent efficiency implementation plan

> For agentic workers: use subagent-driven-development for bounded tasks and independent review. The user explicitly requests parallel workers. Each writer uses a separate checkout or disjoint owned files.

**Goal:** Reduce CI execution and repeated agent work without weakening checks or security decisions.

**Architecture:** Keep one deterministic validation owner. Bind reusable local evidence to file contents, Git state, command definitions, and runtime identity. Keep CI independent. Preserve the existing Claude hooks as thin adapters where shared code replaces their logic. Use focused tests during edits and one integrated full gate on the final state.

**Tech Stack:** Python standard library, Bash, Copier, GitHub Actions, Claude Code and Codex adapters.

## Global Constraints

- Preserve the existing primary checkout and audit work. The integration branch now starts at upstream main `e6c41ba`, whose tree matches audit commit `594d51c`. Work happens in an independent task-runtime clone; earlier worktrees remain intact. Do not publish or merge into original checkouts.
- A stale, failed, partial, malformed, or missing validation result must not authorize a commit. Required checks that cannot run are failures, not passes. Local evidence is not a permission or security boundary against a malicious local writer.
- Bind evidence to contents, not file times. Detect changes to staged, unstaged, untracked, deleted, renamed, executable, and symlink inputs. Detect changes during validation. Never read secret environment files.
- Keep security checks synchronous. Deny excessive policy input explicitly. Do not replace shell-wrapper boundary coverage with a different parser path.
- Reports must distinguish measured results from projections. Model token savings require actual usage evidence. Unit fixtures do not prove live host dispatch.

## Task 1: Bound policy work and preserve boundary coverage

Owned files: `seed/.codex/hooks/pre-tool-policy.py`, policy tests in `bin/tests/test_rendered_harness_contract.py`, and a focused new `bin/tests/test_policy_performance.py` if needed.

1. Inspect policy helpers and their callers. Add neighboring recursion boundary cases and a timeout to policy subprocess fixtures. Prove the oversized-input and duplicate-parse regressions with focused tests before changing production.
2. Replace the expanding depth-14 fixture with the smallest denied shell-wrapper boundary. Keep adjacent allowed coverage and a mutation negative control that proves the depth guard matters.
3. Reuse outer tokenization and reject excessive input before expensive work. Use an explicit JSON denial. Choose a budget that preserves the normal boundary probe and fits the configured hook timeout. Test malformed input and existing denial routes.
4. Verify: `python3 -m unittest discover -s bin/tests -p 'test_policy_performance.py' -v` and the policy test class in `test_rendered_harness_contract.py` pass. Report exact commands, elapsed time, and red/green evidence.

## Task 2: Content-bound shared validation evidence

Owned files: `seed/.agents/lib/validation.py`, `seed/.claude/hooks/run-validate-waves.sh`, `seed/.claude/hooks/pre-commit-gate.sh`, `seed/.claude/hooks/sentinel-cleanup.sh`, and a new `bin/tests/test_validation_evidence.py`.

1. Replace timestamp-only marker trust with a versioned JSON receipt in the existing `.validation_passed` location. Keep the existing runner as the canonical entry point. Implement shared Python logic under `.agents/lib/`. Read all existing marker callers first.
2. Provide CLI `run`, `check`, and `fingerprint`. Use atomic receipt replacement. Include exact commands, check status, exit code, elapsed time, source fingerprint and runtime identity. Remove stale success before running. Reject concurrent source changes. A test command override must never mint production evidence.
3. For Loam, select `bin/verify-template.sh` as the full check instead of also running its unit suite. For generated Python projects require available Ruff and pytest. Use explicit configured commands for other project types; do not turn absent tests into PASS. Allow an explicit justified not-applicable declaration where the project truly has no executable tests.
4. Share `check` with the commit hook and retain robust hook payload parsing. Reject marker forgery by omission or altered command definitions, but do not claim cryptographic protection against a malicious repository owner. Content validity, not marker age, controls reuse.
5. Verify: `python3 -m unittest discover -s bin/tests -p 'test_validation_evidence.py' -v` passes. Cover content change with preserved mtime, deletion, rename, staging difference, untracked input, stale HEAD, failed/missing checks, override seams, source mutation during execution, and atomic success.

## Task 3: Correct snapshots and CI observability

Owned files: `bin/verify-template.sh`, `bin/harness-smoke.sh`, new root snapshot/measurement helpers and tests, `.github/workflows/test.yml`, `.github/workflows/release.yml`, dependency pins where supported by observed versions.

1. Make the full gate validate one frozen intended source state across tests and rendering. Copier 9.16.0 includes dirty local files with `--vcs-ref=HEAD`; the snapshot prevents changes between gate stages. Preserve original Git state. Include source identity and stage timing in output. Exclude only explicit local outputs; do not use broad prose-only skip rules.
2. Add unittest duration output, deliberate job time limits, and PR-scoped obsolete-run cancellation. Keep releases independent. Pin and cache dependencies only using verified versions and supported cache paths.
3. Make smoke checks use the same snapshot contract. Add deterministic negative controls that catch a broken dirty seed rather than testing the old commit.
4. Verify: new snapshot tests pass, `bash -n bin/verify-template.sh bin/harness-smoke.sh` passes, and the full gate ends with `verify-template: PASSED` for the integrated final state.

## Task 4: Reduce duplicate agent work and repair parity claims

Owned files: root and seed agent prose, plugin validation/build-validator/team/ship/auto-phase/critique/review workflow assets, parity inventory and its checker/tests. Do not edit policy, marker hooks, or full verification shell scripts owned by other tasks.

1. Inspect the named session audit and relevant assets. Use one integration and validation owner. Focused workers return bounded report artifacts. Reviewers use a fixed diff and do not rerun unchanged suites without a concrete unresolved risk.
2. Reuse valid content-bound evidence across turns, while requiring new checks for changed inputs. Record failing regression output before the fix; do not require a deliberately failing shared commit. Keep independent final review for risky changes.
3. Use cheaper models for mechanical work and stronger review for security or cross-cutting changes. Avoid duplicated end-of-phase and ship reviews of the same diff. Keep review findings durable. Remove blind polling instructions where completion events exist.
4. Correct parity classifications: distinguish unimplemented adapters from unsupported host features. Document the shared validation command for both agents. Do not claim host support or live execution without evidence.
5. Verify: parity tests, listing-budget checks, and relevant contract tests pass. Search the edited active guidance for redundant full-suite/same-turn requirements and cite each remaining intentional occurrence.

## Task 5: Host checks, benchmarks, and independent attack review

Owned by the integration lead after the task outputs stabilize.

1. Run focused host dispatch probes for allowed, denied, malformed, and over-budget decisions in isolated generated projects. Use installed CLI help and official documentation. Do not make dangerous network or file operations. Report unavailable host tests as COULD_NOT_RUN, never PASS.
2. Measure the same policy fixture and representative validation flows before and after. Include unchanged-state reuse and invalidated-state rerun. Plant safe defects to prove checks still catch failures. Extract actual transcript token usage where present; do not invent saved token counts.
3. Review each task diff, integrate only intended files, then obtain a fresh-context whole-change correctness review. Fix confirmed gaps and rerun covering tests.
4. Run `bin/verify-template.sh` once on the final integrated state. Quote its explicit result and exit code. Recheck original checkout status to prove existing work was preserved.
5. Update the durable findings with measured outcomes, residual limits, and exact reproduction commands. Check each user objective against the completed artifacts before marking the goal complete.

## Progress ledger

- Baseline: completed in prior diagnosis; see the saved task reports. No repeated oversized baseline run is needed.
- Task 1: integrated; focused policy review and tests passed before handoff.
- Task 2: integrated with source/runtime receipts, explicit shell runtime declarations,
  commit parsing, and negative controls for the independent review findings.
- Task 3: integrated with caller and scratch invariants, bounded cleanup, CI budgets,
  dependency pins, and focused mutation/timeout controls.
- Task 4: integrated; parity/listing and bounded workflow pressure checks pass.
- Task 5: the fixed-diff review, repair reports, live-host observations, receipt
  measurements, and final gate record live in `/private/tmp/loam-efficiency-runtime`.
  Consult their actual verdicts and exits for readiness; this plan does not certify
  the final branch independently of that evidence.
