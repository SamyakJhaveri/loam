# S7b Adversarial Review

**Date:** 2026-04-19
**Reviewers:** plan-reviewer (Opus, advisor) + self-critic (Opus, worker) + code-simplifier (Sonnet, worker)
**Scope:** S7b artifacts prepared in the same session — `04-S7b-PLAN-REVIEW.md`, `04-S7b-ORACLE-AUDIT.md`, `04-S7-LAUNCH-MANIFEST.md`, `tests/test_oracle_divergence.py`, 8 spec downgrades, `known-issues.md` tally update.
**Dispatch pattern:** 3 parallel Agent invocations (read-only), outputs synthesized here. Cross-talk deferred because reviewer lenses are orthogonal (planning hazard / rationalization / simplification); the REVIEW doc consolidates findings.
**Fix-loop closure:** all BLOCKERs resolved before commit. FLAGs triaged inline. Advisory-only suggestions selectively adopted where cheap.

---

## Methodology

Each reviewer was given the three planning artifacts plus tools for read-only source cross-checks (`run_eval_batch.py` argparse, `llm_evaluate.py` MODEL_REGISTRY + Azure temp-gate, `derive_l0_passers.py`, `protect-cuda-omp-results.sh`). Explicit instructions: no edits, no builds. Output format per reviewer lens.

- **plan-reviewer** — ordering hazards, unverified claims, budget/scope drift, paste-readiness.
- **self-critic** — rationalization patterns, incomplete work framed as complete, unverified claims, quality-bar violations.
- **code-simplifier** — over-engineering, duplication, verbose prose, behavior-preserving suggestions only.

---

## Findings synthesis

### BLOCKERs (plan-reviewer — 2 found; both resolved before commit)

#### BLOCKER-1 — `derive_l0_passers.py` has no `--direction` filter; §6.1 ran it twice per model for identical output

**Evidence:** `derive_l0_passers.py` zero references to `direction`/`source_api`/`target_api`; groups purely by `(source_spec, target_spec)` at `augment_level == 0`. Two invocations in original §6.1 (per-model-per-direction) would produce byte-identical content. Downstream `_build_tasks_from_task_list` at `run_eval_batch.py:190-197` filters mismatched entries but emits per-entry warnings — misleading for operator.

**Fix adopted (ADV-1):** Collapse §6.1 to one invocation per model producing one passer file; both directions consume the same file. Noted the downstream filter behavior so operator expects the skip warnings. `04-S7-LAUNCH-MANIFEST.md` §6.1 + §6.2 rewritten. Added per-direction count sanity check via `jq` one-liner for visibility.

#### BLOCKER-2 — Audit text framed myocyte as `(cuda, opencl)` without reconciling the S7 CUDA↔OMP precedent narrative

**Evidence:** The Precedent section at `04-S7b-ORACLE-AUDIT.md:87-89` invoked the bfs CUDA↔OMP pattern but the myocyte downgrade is `(cuda, opencl)`. `rodinia-myocyte-omp` was already weak from S5 Batch 4 (commit `255bf0d`) — the audit scope included only the two still-strong myocyte variants. Silent mis-framing would mislead camera-ready reader.

**Fix adopted:** Added a "Scope note (myocyte pair)" paragraph after the Precedent section clarifying (a) `rodinia-myocyte-omp` was already weak prior to S7b, (b) the audit examined only the two still-strong myocyte variants, (c) CUDA↔OpenCL divergence is now the first non-CUDA↔OMP finding in the sprint, (d) paper-time narrative must distinguish FP-reduction divergence (any cross-runtime pair) from source-asymmetry divergence (bfs, nw, nn).

---

### FLAGs (plan-reviewer — 6 raised; triaged inline)

- **FLAG-1** (5-suite coverage not enumerated) — **accepted as-is**. Per-suite invocations are an operator-level trivial substitution (`--suite` swap); enumerating 40 near-identical tmux sessions is unnecessary bloat. Added a clarifying sentence noting operator responsibility.
- **FLAG-2** (budget math supersession phrasing) — **accepted as-is**. The existing §9 table reads "was $559, superseded by $784, now at $848" direction is paperwork-confusing but the memory trail (`project_budget_math_2026_04_17` and `project_gpt5_3_chat_resolution`) already documents both recomputations. Fresh sign-off requirement is clearly stated. Not worth prose churn now.
- **FLAG-3** (Azure temp field misleading in downstream analysis) — **accepted as followup**. Result JSONs record `temperature: 0.7` but Azure strips it. Downstream `analyze_eval.py` tolerates the field. The distinction between `temperature` and `effective_sampling = "reasoning_effort"` is a paper Threats-to-Validity section (`.planning/_archive/phase-02-llm-eval-testing/02-THREATS-TO-VALIDITY.md`), not a launch-blocker.
- **FLAG-4** (verifier uncommitted) — **fix adopted**. Moved `/tmp/s7b-manifest-verify.py` → `.planning/phases/03-oracle-framework/tools/verify_launch_manifest.py`. Launch manifest §8 updated to reference the committed path.
- **FLAG-5** (smoke-artifact fallback dependency) — **accepted as-is**. The v3 log is captured on disk (`04-S7-LIVE-v3.log`) and contains the smoke summary; `/tmp/` artifacts are supplementary. No new dependency.
- **FLAG-6** (sentinel TTL + edit churn) — **accepted as-is**. Hook behavior is documented in `validation-loop.md`. Operator awareness.

### Self-critic findings (1 precision refinement adopted)

- **Audit claim "nn_openmp.c emits no per-record distance output" was technically true but sanitized.** `nn_openmp.c:149` emits `fprintf(stderr, "%s --> %f\n", ...)` — distances ARE printed but to stderr without the `Distance=` prefix. The downgrade rationale is still correct (the `Distance=` regex on stdout cannot match), but the stream + format distinction is the precise reason, not an absence of distance output.
- **Fix adopted:** Updated `specs/rodinia-nn-cuda.json` strategy description to document the stdout-vs-stderr + `Distance=` vs bare-float difference. Audit doc narrative remains accurate enough (it says "no per-record `Distance=`" in that exact phrasing, not "no distance output").

### Code-simplifier findings (MINOR_CLEANUP)

- **High-value simplifications suggested** (spec description trimming, Karpathy-section deletion in plan-review, D-BUDGET §2↔§9 duplication): **declined**. Spec descriptions are consumed by `harness info` and LLM prompts; the longer form aids both human reviewers and downstream analysis. Planning-doc boilerplate deletion would save lines but the Karpathy recap records cross-cutting constraints per stage. D-BUDGET §2 is the decision block; §9 is the detailed table. Different reader contexts — duplication is intentional pointer architecture, not an error.
- **Lower-value suggestions** (remove `_DIVERGENT_HASHES` dict from tests, inline CTL hashes): **declined**. The dict is 10 lines; it encodes a historical audit constant that future reviewers (including paper camera-ready reviewers) may want to verify without re-reading the audit prose. Behavior-preserving, yes, but information-destructive.

---

## Verified claims (cross-checked by plan-reviewer against HEAD `9b1a1f5`)

1. All 12 manifest CLI flags match argparse at `run_eval_batch.py:465-606`.
2. `azure-gpt-5.4` (`:105-112`) and `together-qwen-3.5-397b-a17b` (`:128-133`) in `MODEL_REGISTRY`, both `supports_thinking: True`.
3. Azure temp-gate at `llm_evaluate.py:940-942` matches manifest claim. `reasoning_effort="medium"` injected at `:949-950` when `thinking_enabled AND supports_thinking`.
4. Gemini `reasoning_effort="none"` line (`:1030`) unrelated to `--thinking` flag — consistent with line-discipline note in evaluation.md.
5. CUDA↔OMP hook (`protect-cuda-omp-results.sh:67-75`) blocks batch runs without `--resume`. All §4–§6 commands carry `--resume`.
6. `_derive_llm_seed` at `llm_evaluate.py:312-323` is SHA-256-based, 31-bit, direction-sensitive; no `--seeds` CLI flag.
7. All 8 downgraded specs: `oracle_strength: "weak"`, no `file_hash`/`numeric_comparison`, `reference_files: []`.
8. `known-issues.md:25-28` tally updated (7 strong / 0 medium / 46 weak / 153 unknown).
9. `tests/test_oracle_divergence.py`: 6 tests all PASS.
10. Sweep 88/88 PASS post-downgrade.

---

## Assumptions carried forward

- Gal budget re-approval for `azure-gpt-5.4` at ~$848 is still open (PHASE-3-BLOCKER).
- Le's `azure-gpt-5.4` deployment provisioning on Le's node (PHASE-3-BLOCKER).
- TPM quota sufficient for ~1566 canonical + ~1148 ablation samples across both resources (PHASE-3-BLOCKER).
- Smoke artifacts at `/tmp/s7-artifacts-v3/` are optional for launch (entry gate marks as such).

---

## Final verdict

**PASS** (after fix loop).

- 2 BLOCKERs resolved in `04-S7-LAUNCH-MANIFEST.md` + `04-S7b-ORACLE-AUDIT.md` + `specs/rodinia-nn-cuda.json` + new committed `tools/verify_launch_manifest.py`.
- Verifier re-run: PASS — 5 command blocks, 21 argparse flags, 12 MODEL_REGISTRY entries.
- Divergence tests re-run: 6/6 PASS.
- Sweep status unchanged (88/88 from entry gate, no spec oracle logic altered by BLOCKER fixes).

Ready for Stage 7+8 (validate + commit + handoff).
