# S7c Adversarial Review

**Date:** 2026-04-19 / 2026-04-20 (post-smoke)
**Reviewers:** plan-reviewer (Opus, read-only) + self-critic (Opus, read-only) + code-simplifier (Opus, read-only)
**Scope:** S7c artifacts prepared in the same session — smoke-v4 log, `scripts/evaluation/derive_l0_passers.py` (Stage 2 code+tests), 5 bucket2 spec upgrades (Stage 3 code+tests), `04-S7-LAUNCH-MANIFEST.md` §6 refresh (Stage 4), 2 stale memory files (Stage 5), `.claude/rules/known-issues.md` tally.
**Dispatch pattern:** 3 parallel `Agent` invocations, team `s7c-review`, `--all-opus` (per memory `feedback_plan_review_team` "all ultrathink"). Read-only — reviewers had tools for `git status`, `git diff`, `python3 -m pytest`, targeted `harness verify`, but no editing. Synthesis here.
**Fix-loop closure:** 0 BLOCKERs. 4 FLAGs actionable; fixes landed pre-commit. 3 advisory FLAGs accepted as-is with rationale.

---

## Methodology

- **plan-reviewer** — plan-vs-execution trace; stage-by-stage claim verification; end-to-end semantic trace from Stage 2 `derive_l0_passers.py` through Stage 4 manifest §6.1/6.2 → `run_eval_batch.py:190-197` direction-filter; CLAUDE.md invariant checks; source-code cross-read (`rodinia/rodinia-src/cuda/hotspot3D/3D.cu:122-132` for accuracy semantics).
- **self-critic** — rationalization patterns, incomplete-work scans, unverified-claim audit. Independently re-ran 15 `harness verify` invocations (5 specs × 3 runs) + 43 unit tests + `validate_schema --all` + `verify_launch_manifest.py` to corroborate the executor's pass claims.
- **code-simplifier** — behavior-preserving simplification audit of Stage 2 + Stage 3 diffs. Explicit "never alter interfaces or behavior" directive.

---

## Findings synthesis

### BLOCKERs — none.

### FLAGs actionable (4 raised by plan-reviewer; all resolved inline)

#### FLAG 3-A (MEDIUM-HIGH) — hotspot3d tolerance semantics

**Evidence.** `rodinia/rodinia-src/cuda/hotspot3D/3D.cu:122-132` defines `accuracy()` as `sqrt(sum((a-b)²)/len)` — an RMS residual where 0 = perfect, lower = better. Initial S7c Stage 3 Policy-B tolerance `1e-7 abs` around baseline `4.096975e-05` would spuriously reject strictly-better translations (LLM output `Accuracy: 0` → delta `4.097e-05` ≫ `1e-7` → FAIL). Same class of bug surfaced and fixed earlier in the session for `hecbench-md-cuda` (baseline `1.86265e-09`, tolerance widened to `1e-8` abs); missed for hotspot3d because executor assumed Accuracy was "score-to-match" without reading the kernel source.

**Fix adopted** (option i from four enumerated to Samyak; chosen by user):
- `rodinia-hotspot3d-{cuda,omp,opencl}.json`: tolerance `1e-7` → `1e-4 abs` (~2.4× baseline). Widened window `[0, baseline + 1e-4]` accepts strictly-better translations (`Accuracy: 0`) and cross-compiler FP-reordering drift; still rejects gross errors (`Accuracy >= 1e-3`).
- Descriptions rewritten to document the RMS-residual semantics + the widening rationale.
- `tests/test_bucket2_numeric_comparison.py` lock-table + docstring updated to reflect the new tolerances.
- Post-fix: 30/30 bucket2 tests PASS, 88/88 sweep PASS, 219 unit tests PASS.

#### FLAG 3-B (MEDIUM) — stale `hecbench-md-cuda` `baseline_results.stdout_snippet`

**Evidence.** `specs/hecbench-md-cuda.json` `baseline_results.configurations.correctness.stdout_snippet` read `"Max error between host and device: 0"` while S7c Stage 3 numeric_comparison uses `expected: 1.86265e-09`. Asymmetric with `md-omp_target` which captured 0 — suggested either stale snippet or erroneous Stage 3 capture. Stage 3 pre-flight captured `1.86265e-09` 3/3 runs deterministic; self-critic corroborated same value across 3 additional runs.

**Fix adopted.** `baseline_results.stdout_snippet` refreshed to `"Max error between host and device: 1.86265e-09\nAverage kernel execution time 0.00445281 (s)"`. No schema extension added; only the existing `stdout_snippet` field updated. This reconciles spec-internal consistency and documents cross-API asymmetry (CUDA=1.86e-9, omp_target=0) as expected (own-API baselines, not cross-API lock).

#### FLAG 3-D (LOW) — missed follow-up marker in S7b-AUDIT §"Follow-up work (NOT in S7b)"

**Evidence.** Stage 3 edit updated the `## Scope` follow-up paragraph (around line 28) but missed the bulleted `## Follow-up work (NOT in S7b)` section at line 95-97 which still read "True strength is `weak`" — the same claim the upgrade obsoleted.

**Fix adopted.** Bullet #1 struck through and replaced with "UPGRADED 2026-04-19 (S7c, commit pending)" paragraph documenting the final Policy B-per-spec tolerances (post-FLAG-3-A widening), the RMS-residual rationale for hotspot3d, and pointer to `tests/test_bucket2_numeric_comparison.py`. Section now contains exactly one UPGRADED marker per prior follow-up item.

#### FLAG 3-C (MEDIUM) — `hecbench-md-omp_target` tolerance 1e-9 is tight

**Evidence.** `expected: 0.0, tolerance: 1e-9 abs` — rejects any LLM output > 1 ppb. Plan-reviewer questioned whether FP reduction-order drift on the OMP-target runtime could silently convert the oracle into a reduction-order sensitivity test.

**Fix decision: accepted as-is.** Self-critic ran the omp_target binary 3× — bit-identical `Max error between host and device: 0` output each time. Stage 3 pre-flight was also 3/3 deterministic. The 1e-9 tolerance is in-band for observed determinism. If a future session surfaces non-determinism on this target, re-open this flag. Rationale preserved in spec description.

### FLAGs advisory (accepted as-is with rationale)

- **Stage 1 result-JSON count 22 vs plan RED-gate 24.** Plan estimate was speculative; 22 is internally consistent with the pytest fixture shape (canonical produces 7 samples × 2 models + direction-independence 1 × 2 models + batch_summary trailers). Exit criterion #1 (4/4 pytest PASS, 0 nulls) met. Plan's RED-gate `24` was wrong; not a session gap.
- **Self-critic FLAG 1: no post-Stage-3 full sweep log.** False positive — executor ran `scripts/spec_tools/run_verify_sweep.py` at Stage 3 end with output `PASS 88/88 FAIL 0`. Subsequent re-runs after each fix in Stage 6 also PASS 88/88.
- **Self-critic FLAG 2: team-lead brief said "4 memory files" vs plan §Stage 5 "3".** Typo in brief, not a Stage 5 gap — executor edited the 3 files the plan enumerated.
- **Self-critic FLAG 3: "3/3 deterministic" claim is schema-only in tests.** True; bit-identical determinism was verified out-of-band by executor pre-flight and self-critic independently. Optional integration-marker test deferred to follow-up; 15/15 `harness verify` runs in this session constitute adequate in-session evidence.
- **Self-critic noted `~~strikethrough~~` retraction in S7b-AUDIT.** Called out as correct anti-rationalization posture (doc contradicts prior text openly).

### Code-simplifier findings (MINOR)

- **1 optional cosmetic nit.** `scripts/evaluation/derive_l0_passers.py:84-86` — filter condition could be expressed as tuple compare `(src.rsplit(…), tgt.rsplit(…)) != (src_api, tgt_api)`. **Declined** — current two-clause form is readable and the simplifier tagged it low-risk/optional.
- **6 rejections (all load-bearing duplication / intentional verbosity).** Most notable: `BUCKET2_UPGRADES` lock-table in `test_bucket2_numeric_comparison.py` IS redundant with spec JSON content, but that duplication is the point — tests exist to fail if specs drift from paper-cited values. Extracting from JSON would make tests tautological (spec == spec). Spec `numeric_comparison.description` fields are long but encode non-obvious context (captured baseline, tolerance rationale, audit trail) that won't be in the commit message six months from now.

---

## Verified claims (cross-checked against HEAD post-Stage-6 fixes)

- **Smoke v4:** 4/4 pytest PASS, 14m 54s wall, 0 telemetry nulls across 22 result JSONs. Log committed to `.planning/phases/03-oracle-framework/04-S7-LIVE-v4.log` with outcome summary appended.
- **Stage 2 derive --direction:** 3 new RED→GREEN tests (`test_direction_filter_keeps_matching_entries`, `…_drops_non_matching_entries`, `…_none_preserves_legacy_behavior`). End-to-end trace: derive → direction-scoped passer JSON → `run_eval_batch.py:148` `--direction` split → `_build_tasks_from_task_list:190-197` direction-suffix safety net (no-op with direction-scoped files). Edge case verified: `omp_target` correctly distinguished from `omp` by `rsplit("-", 1)[-1]`.
- **Stage 3 bucket2 upgrade:** 5 specs (`rodinia-hotspot3d-{cuda,omp,opencl}`, `hecbench-md-{cuda,omp_target}`) carry `oracle_strength: "medium"` with `stdout_pattern + numeric_comparison + exit_code` conjunctive strategy. Post-FLAG-3-A fix: hotspot3d tolerance `1e-4 abs`; hecbench-md-cuda `1e-8 abs`; hecbench-md-omp_target `1e-9 abs`. Determinism: 15/15 `harness verify` bit-identical (executor pre-flight + self-critic corroboration).
- **Stage 4 manifest §6:** 4 derive commands (model × direction), 1 ablation skeleton + mirror instruction. `verify_launch_manifest.py` PASS (5 command blocks, 21 argparse flags, 12 MODEL_REGISTRY entries).
- **Stage 5 memory:** `reference_threats_to_validity.md` tally corrected to `24 🔴 / 18 🟡 / 3 🟢` (matches `02-THREATS-TO-VALIDITY.md:15` verbatim; plan target `16 🟡` was itself stale — executor trusted the live doc over the plan, which is the correct Karpathy-compliant behavior). 2 of 3 plan-flagged memory files were already fresh (previous session repaired them); MEMORY.md index entry updated to match new tally.
- **Oracle strength distribution (post-S7c):** `{strong: 2, medium: 5, weak: 46, untagged/None: 153}`. Self-critic ran a `Counter` over all 206 specs — distribution matches `known-issues.md:25-29` exactly.
- **CLAUDE.md invariants.** Invariant 1 (manifest append-only) — `git diff manifest.jsonl` = 0 lines. Invariant 2 (result JSONs immutable) — `git status results/` clean. Invariant 4 (spec run args unchanged) — 0 matches for `+/- .*(args|command_args)` across the 5 edited specs. Invariant 5 (~15 phantom schema errors) — `validate_schema --all` emits exactly 15 bullet errors of the known pattern; 0 new errors from the 5 spec edits. Invariant 7 (no push) — branch up-to-date with origin; no push attempted.

---

## Overall verdict

**PASS — ready for `/validate` + commit.**

All 3 workers converged on 0 BLOCKERs. The one semantically-important FLAG (3-A, hotspot3d RMS-residual tolerance) was surfaced by plan-reviewer's source-code cross-read, presented to Samyak with 4 enumerated options and per-option analysis, and fixed via option (i) — widen tolerance to `1e-4 abs` (~2.4× baseline), which accepts strictly-better translations while still rejecting gross errors. Supporting FLAGs (3-B stale snippet, 3-D missed audit line) resolved inline. FLAG 3-C and the Stage-1 JSON-count divergence kept as informational — not blocking.

The session's session-batched commits can now proceed in Stage 7 under CLAUDE.md Rule 10 (`/validate` waves 1-3 required). No further adversarial review needed.

---

## Artifacts referenced (all absolute, post-fix state)

- `.planning/phases/03-oracle-framework/04-S7-LIVE-v4.log` — Stage 1 smoke log + outcome summary.
- `scripts/evaluation/derive_l0_passers.py:43-86,97-121` — Stage 2 `--direction` flag.
- `tests/test_derive_l0_passers.py:130-164` — Stage 2 3 new tests (13/13 total PASS).
- `specs/rodinia-hotspot3d-{cuda,omp,opencl}.json` `.verification` — Stage 3 + Stage 6 FLAG-3-A fix.
- `specs/hecbench-md-{cuda,omp_target}.json` `.verification` — Stage 3 bucket2 upgrade.
- `specs/hecbench-md-cuda.json` `.baseline_results.configurations.correctness.stdout_snippet` — Stage 6 FLAG-3-B fix.
- `tests/test_bucket2_numeric_comparison.py` — Stage 3 + Stage 6 lock-table update (30/30 PASS).
- `.claude/rules/known-issues.md:25-29` — Stage 3 oracle tally refresh.
- `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md:28,97` — Stage 3 + Stage 6 FLAG-3-D follow-up markers.
- `.planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md:168-234` — Stage 4 §6.1 + §6.2 refresh.
- `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/{reference_threats_to_validity.md,MEMORY.md}` — Stage 5 memory sweep.

## Dispatch telemetry

- Team name: `s7c-review`
- Workers: 3 (plan-reviewer, self-critic, code-simplifier) — all Opus, all read-only.
- Worker runtime: plan-reviewer ≈ 2 min; self-critic ≈ 2 min; simplifier ≈ 1 min (independent, parallel).
- Cost: bounded by read-only scope; estimate ~$0.50 Opus tokens across 3 workers.
- Fix-loop iterations: 1 (Stage-6 fixes landed in a single pass; post-fix regression green).
