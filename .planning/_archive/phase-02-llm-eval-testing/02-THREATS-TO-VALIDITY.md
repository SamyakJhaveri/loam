---
phase: 02-llm-eval-testing
doc_type: threats-to-validity
status: draft
authored: 2026-04-17
superseded_by: null
---

# ParBench NeurIPS 2026 — Threats to Validity

> **Purpose.** Adversarial simulation of a NeurIPS reviewer, grounded in the actual
> codebase and planning docs. This is the Phase 4 threats-to-validity source document;
> the paper subsection must be derived from (and not diverge from) this file.
>
> Counts (severity-bulleted entries in §§1–5): **24 🔴 high, 18 🟡 medium, 3 🟢 low**,
> plus §6 prose catalog (≈9 UNDISCUSSED + ≈5 ACKNOWLEDGED-not-fixed + ≈8 MITIGATED-existing;
> some overlap with §§1–5) and §6 "Additional threats" (4 items, 3 of which recur under
> UNDISCUSSED). Of the 24 🔴 in §§1–5: ~10 are UNDISCUSSED in any repo doc, ~11 are
> ACKNOWLEDGED in design docs but not mitigated, 3 are partially MITIGATED-NARROWLY.

## Executive punchline — 5 most likely rejection vectors

1. **Verification is a syntactic oracle, not a semantic one.** `harness/verifier.py:59–91`
   only implements `exit_code` + `stdout_pattern`; `numeric_comparison`, `file_diff`,
   `custom_script` all return `SKIP` (lines 63–68). "PASS" means "exit 0 AND a regex
   matched stdout" — not numerical equivalence to a reference run. A trivially-broken
   translation that prints the hard-coded success string will pass. The S-VERIFY
   2026-03-27 fix (`.claude/rules/evaluation.md:226–254`) only tightened this to a
   conjunction — it did not change the underlying weakness.

2. **n=3 canonical samples, zero CIs, and extrapolated pass rates.** ROADMAP success
   criteria (`.planning/ROADMAP.md:98–103`) list no confidence intervals, no bootstrap, no
   minimum-detectable-effect analysis. The 55% L0-pass assumption driving the $559
   budget is openly flagged as an extrapolation from a 31% first-sample datapoint
   (`.planning/PROJECT.md:4`, `docs/neurips2026-experiment-plan.md §2.4`). A reviewer will ask
   for CIs on Δpass@1(L_k); there is no commitment to produce them.

3. **L0-conditional ablation filter is a survivor bias.** `experiment-plan §2.4`
   conditions the ablation on pass@1-of-any at L0. By construction you cannot observe
   L0-failers that would-have-passed under perturbation, and the paper commits
   (Key Decision 2026-04-16, `.planning/PROJECT.md:79`) to not running an audit sample. This
   is acknowledged as a TODO threats subsection — but only a subsection, not a
   measurement. Reviewer attack: "Your robustness result is conditional on a success
   subset you did not define beforehand."

4. **Model asymmetry: different providers, deployments, machines, thinking stacks.**
   Qwen 3.5 397B runs via Together AI on Samyak's RTX 4070; Azure GPT-5.4 runs on
   Le's machine (D-34, `02-CONTEXT.md`) under a different Azure tenant with a
   not-yet-pinned deployment name (`llm_evaluate.py:861` uses prefix-strip).
   `reasoning_effort="medium"` on Azure vs `enable_thinking=True` via Jinja
   template kwarg on Together (`llm_evaluate.py:1000-1002`) are not equivalent
   operationalizations of "thinking on". Cross-model comparisons are confounded
   by vendor-side quantization, routing, and tool-chain variability that ParBench
   cannot control.

5. **169 pre-S-VERIFY PASS results cannot be re-verified, yet the pipeline audit
   (2026-04-09) declared "0 core pipeline bugs" using them.**
   `.claude/rules/evaluation.md:247–249` explicitly: "Cannot be retroactively
   re-verified — `translated_files` was truncated to 200 bytes and
   `run_stdout_snippet` was null for PASS results." Any numeric comparison to
   "prior Qwen 31% pass rate" is implicitly a comparison against data the authors
   themselves say is uncheckable.

---

## 1. Internal validity

How the pipeline could produce incorrect PASS/FAIL labels.

- 🔴 **Verification is oracle-weak.** `harness/verifier.py:23,59-68` — exit_code +
  stdout_pattern is the conjunction; all numeric/file_diff strategies are TODO stubs
  returning SKIP. PASS ≠ "correct output". **UNDISCUSSED.**
- 🔴 **Pre-S-VERIFY 169 PASS results are unverifiable.**
  `.claude/rules/evaluation.md:247–249`; fix dated 2026-03-27. Any comparison or
  baselining against those results is un-auditable. **ACKNOWLEDGED** in rules file;
  no mention in paper-facing docs.
- 🔴 **Stdout-pattern-only specs have no correctness signal.** `bfs-omp` and
  `lavamd-omp` are kept as exit_code-only (`evaluation.md:241`) — a successful exit
  with empty output passes. **ACKNOWLEDGED.**
- 🔴 **2026-04-09 regex bug affected 9 nn-opencl results.**
  `.claude/rules/known-issues.md:82–90` — `_wrap_pattern()` scoping fix; 3 would flip
  VERIFY_FAIL→PASS. nn-opencl is KNOWN_FAIL so excluded, but the audit class of
  "pattern-combiner regex bugs" is not proven absent elsewhere (the audit re-ran the
  exact bug signature, not a fuzz sweep). **MITIGATED-NARROWLY.**
- 🟡 **Iterative repair confound despite "self-repair=OFF".** `llm_evaluate.py:1343,
  1486-1750` implements `analyze_build_failure()` → linker-hint injection on retry.
  Canonical uses `max_retries=1`, but the code path exists; a single flag change
  flips the estimator's meaning. No assertion in the pipeline that `max_retries==1`
  when writing canonical result JSONs. **UNDISCUSSED.**
- 🟡 **Stale top-level `run_status` / `run_time_seconds` fields.**
  `known-issues-archive.md:337-346` — on multi-attempt regressions, top-level fields
  can retain attempt-1 values; `overall_status` is authoritative but any analysis
  scripts reading top-level fields would mis-classify. **ACKNOWLEDGED** but no
  test-asserts-this.
- 🟡 **Header staging side-effects.** `evaluation.md:270-282` —
  `_stage_support_headers()` copies `.h/.hpp/.cuh` from source to target; cleanup in
  `finally`. If a translation subprocess is SIGKILLed mid-run (OOM), staged headers
  leak and the next task sees "missing header" becoming "present header"
  non-deterministically. Verification command listed, nothing asserts it post-batch.
  **UNDISCUSSED.**
- 🟡 **Submodule-in-worktree silent empty directories.** `CLAUDE.md:86,93`,
  `known-issues.md:64-67`. Rule: "never run evaluations in worktrees." Nothing in
  the pipeline verifies it isn't a worktree. Accidental run yields BUILD_FAILs on
  empty source dirs that look like real model failures. **ACKNOWLEDGED,
  not prevented.**
- 🟡 **Backup/restore depends on kernel-only predicate heuristic.**
  `known-issues-archive.md:386-410`: `_is_kernel_only_translation()` returns True iff
  all `translation_targets` end in `.cl`. A mixed kernel+host OpenCL translation
  would silently be treated as full-program. No assertion that target API ↔
  kernel-only predicate are consistent. **UNDISCUSSED.**
- 🟢 **`dict.get("key", {})` vs `or {}` gotcha.** `evaluation.md:256-267`. Crashes on
  null JSON fields; one known occurrence pattern documented. Low risk post-fix.
  **MITIGATED.**

## 2. External validity / generalization

How far does ParBench generalize?

- 🔴 **3 API families only (CUDA/OMP/OpenCL) + 2 case-study APIs (omp_target,
  openacc).** `CLAUDE.md:3`, `.planning/PROJECT.md:42`. SYCL/HIP explicitly out of main
  results; MPI/Kokkos/RAJA/stdpar/Thrust absent. Paper claim of "parallel code
  translation" covers 3 APIs out of ~12 in active HPC use. **ACKNOWLEDGED ("Out
  of Scope").**
- 🔴 **Kernel-centric scope is the entire benchmark.** `evaluation.md:42-64` +
  `CLAUDE.md:336-341` — every spec has `translation_targets`; the LLM never sees
  host drivers, Makefiles, or multi-component programs. Translation skill ≠
  project-level porting, and ParBench measures only the former. Reviewer attack:
  "Does this predict real HPC migration effort?" Answer in current docs: no.
  **ACKNOWLEDGED** as design, not as a limitation.
- 🔴 **Single hardware platform.** `CLAUDE.md:158-165` — RTX 4070 sm_89, GCC 12.4,
  CUDA 12.3, HPC SDK 24.3. OpenMP target offload uses a single `nvc` 24.3 build.
  No AMD/Intel GPUs, no ARM CPUs, no multi-node. A translation passing here may
  not build on A100/H100 sm_80/sm_90. **UNDISCUSSED** as a limitation.
- 🔴 **No runtime-performance correctness.** `evaluation.md:305-312` +
  `known-issues-archive.md:303-313` — `speedup_ratio` uses wall-clock with
  sub-ms baselines and is labeled unreliable. A translation 1000× slower than the
  reference but exits 0 with the right string is PASS. **ACKNOWLEDGED** as "not
  reported", not tied to the claim shape.
- 🔴 **Benchmarks are deliberately small.** Tasks assumed ~5 min each. Production
  CUDA/HIP codebases are 100k+ LoC; ParBench kernels are single-file or small
  multi-file. No generalization claim from small kernels to production HPC code.
  **UNDISCUSSED.**
- 🟡 **No multi-GPU / distributed / MPI kernels.** No spec has `omp_mpi` or `mpi` in
  `parallel_api` or `translation_targets`. Displayed in `API_DISPLAY_NAMES` but
  unused. **UNDISCUSSED.**
- 🟡 **HeCBench is a curated 10-kernel subset of 1874.** `known-issues.md:21`,
  `CLAUDE.md:87`. Sampling strategy not documented in paper-facing docs; selection
  bias risk (easy kernels may have been picked). **UNDISCUSSED.**
- 🟡 **Phantom-spec + KNOWN_FAIL exclusions change the population.**
  `known-issues.md:25-36,54-61`; 8 KNOWN_FAIL + 5 deleted phantom specs. Denominator
  is 87 TRUE PASS but manifest has 96 entries. Reader may assume the benchmark
  covers all 96. **ACKNOWLEDGED** in design; paper must replicate.

## 3. Construct validity

Does the metric measure what we claim?

- 🔴 **PASS ≠ semantic equivalence** (construct framing of §1). The claim "Model X
  translates correctly P% of the time" is stronger than the measurement ("produces
  a binary that exits 0 and prints a known string"). **UNDISCUSSED** as a
  construct-validity issue.
- 🟡 **11 weak-oracle Rodinia specs explicitly tagged.** S4a + S4b (commits
  `e912c8d`, `5bcf7fe`) per `.planning/phases/03-oracle-framework/03-B1-AUDIT.md`
  bucket5 classification: srad-{cuda,omp}, backprop-{cuda,omp,opencl},
  bptree-{cuda,omp}, lavamd-{cuda,omp}, nn-omp, nw-opencl. These specs have no
  deterministic output file accessible without touching benchmark source, no
  correctness numeric in stdout, no self-check; current verification is
  `stdout_pattern` on a completion sentinel only (e.g., "Training done",
  "Computation completed successfully"). PASS for these 11 specs means "binary
  printed the success string" — same construct gap as the bullet above, but now
  explicitly labeled (`oracle_strength: "weak"`) so reviewers and downstream
  analysis can isolate them. Bucket5 candidates ineligible for `file_hash` upgrade
  per HANDOFF.md §3 Rules 1+9 (no benchmark-source mutation; weak + Threats note
  is the documented escape hatch). **MITIGATED-NARROWLY** (audit + tagging +
  Threats disclosure); paper Methodology must cite this list and exclude these
  cells from any "semantic-gating" claim. Bptree-cuda is a known
  audit-classification candidate for re-triage in S6 (source writes
  `output.txt`; pending determinism pre-flight).
- 🔴 **pass@1-of-any filter vs reader expectation.** `.planning/PROJECT.md:77`,
  `experiment-plan §2.4`. Reader hears "ablation on L0-passers" and may picture a
  stricter filter; pass@1-of-any is the most permissive pass@k reducer (any sample).
  Δpass@1(L_k) is computed on a set where the model already demonstrated variance
  — so the canonical baseline for Δ is itself noisy. **ACKNOWLEDGED** as
  estimator-denominator caveat but only in §2.4; not in paper-level framing.
- 🔴 **Thinking ON confounds raw vs reasoning-augmented capability.**
  `experiment-plan §2.1` row "Reasoning: Thinking ON (both models)". Qwen
  thinking-ON was explicitly not the historical default (`llm_evaluate.py:1001`
  currently `enable_thinking: False`; plan flips it). Prior 31% Qwen datapoint is
  thinking-OFF; headline 55%-assumption is thinking-ON. These are operationally
  different models. **ACKNOWLEDGED** as design choice, but the 31% → 55%
  extrapolation silently crosses the thinking boundary.
- 🔴 **temp=0.7 + num_samples=3 under-samples the distribution.** At T=0.7 per-sample
  variance is non-trivial; with n=3 the pass@3 estimator has wide CIs. Chen et al.
  2021 form is implemented, but reporting only point estimates obscures that the
  "55%" has a ±10pp-ish 95% CI at n=3. **UNDISCUSSED.**
- 🟡 **KNOWN_FAIL exclusion is asymmetric.** `known-issues.md:68-78` — source-KF and
  target-KF both excluded. Defensible, but changes the comparator: if GPT-5.4
  succeeds on a KF spec whose host-side infra was broken (not the LLM's fault),
  that PASS is still excluded. **ACKNOWLEDGED** in policy; not in comparison
  semantics.
- 🟡 **"Kernel-centric" is itself a construct choice.** Measuring translation
  quality only on curated kernel files answers "can the LLM rewrite the parallel
  region?" not "can the LLM port the program?" Paper claim must not drift between
  these. **ACKNOWLEDGED** (design); paper-narrative alignment is a Phase 4 risk.

## 4. Statistical / experimental design

- 🔴 **No confidence intervals in ROADMAP success criteria.** `.planning/ROADMAP.md:98-103`.
  Success = "streams complete", "non-zero passer counts". Nothing about
  "report Δ with CIs", "bootstrap over cells". Paper risks stating deltas without
  error bars. **UNDISCUSSED.**
- 🔴 **55% L0-pass assumption is load-bearing.** `.planning/PROJECT.md:4`, `experiment-plan
  §2.4`. Closest datapoint: 31% Qwen first-sample (thinking-OFF, different config).
  Entire L0-conditional ablation presumes enough passers for stable Δ estimates.
  If real rate is 20%, per-direction breakdowns (6 directions × ~17 cells) become
  uselessly noisy. **ACKNOWLEDGED**; no contingency beyond "fallback to pass@2-of-3"
  (stricter, not looser).
- 🔴 **n=3 is weak for pass@k variance.** Seed-variance reporting is committed
  (`experiment-plan §6`: "std of 3 pass@3 samples") but std with n=3 has ~±50%
  estimator variance. **UNDISCUSSED.**
- 🔴 **Unmatched compute across models.** Azure GPT-5.4 `max_completion_tokens=32768`
  (`llm_evaluate.py:880`) + reasoning_effort=medium vs Together Qwen `max_tokens=
  81920` (`:993`) + Jinja-template thinking toggle. Not matched compute budgets.
  Reviewer: "Your proprietary-vs-open-source comparison is confounded by 2.5×
  output token ceiling." **UNDISCUSSED.**
- 🔴 **No baseline-model comparison in canonical.** `experiment-plan §2.4` lineup:
  Qwen 3.5 397B + GPT-5.4 only. No GPT-4o, no Claude, no Gemini despite all in
  `MODEL_REGISTRY` (`llm_evaluate.py:62-114`). Paper cannot claim "GPT-5.4 is best"
  without a non-cherry-picked comparator set. **UNDISCUSSED.**
- 🟡 **No kernel-complexity stratification in denominators.**
  `translation_complexity.csv` exists with 4 classes (`evaluation.md:65-84`);
  analysis hooks exist, but ROADMAP success criteria don't require stratified
  reporting. **PARTIALLY MITIGATED** (infra exists, reporting commitment absent).
- 🟡 **No blinded human ground-truth check.** No evidence anyone manually
  code-reviewed even a 20-cell sample of "PASS" translations. Construct validity
  asserted but not audited. **UNDISCUSSED.**
- 🟡 **pass@1-of-any biases ablation.** L0-pass set is enriched for "got lucky once
  in 3 at T=0.7". Δpass@1(L_k) on this set systematically over-estimates robustness
  (regression-to-mean on the canonical baseline). **ACKNOWLEDGED** in §2.4 but not
  corrected.
- 🟢 **Per-cell paired bootstrap CI is planned.** `experiment-plan Appendix A`.
  Execution TBD. **MITIGATION ACKNOWLEDGED.**

## 5. Reproducibility

- 🔴 **`config/paths.json` hardcoded for Samyak's machine.** `.planning/PROJECT.md:70` explicit
  decision: "Portability deferred." `/home/samyak/Desktop/parbench_sam` strings leak
  across ROADMAP, REQUIREMENTS, CRITIQUE, CLAUDE.md, tests, analysis scripts
  (15 files). **ACKNOWLEDGED.**
- 🔴 **HeCBench-master is gitignored but required.** `CLAUDE.md:87`,
  `known-issues.md:9-13`. 1874 benchmark dirs cloned locally. A reviewer who clones
  the repo cannot reproduce any HeCBench result without a side-channel download.
  Manifest schema errors are "expected." **ACKNOWLEDGED**, not automated.
- 🔴 **Toolchain is not locked.** `requirements-lock.txt` locks Python deps
  (`CLAUDE.md:168`) but not `nvcc 12.3`, `nvc++ 24.3`, `GCC 12.4`, OpenCL version.
  Version-dependent: `rodinia-kmeans-cuda` is KNOWN_FAIL because CUDA 12 removed
  `texture<>` (`known-issues.md:28`). Downstream reproducers on CUDA 11 or 13 get
  a different KNOWN_FAIL set. **ACKNOWLEDGED** in-repo, not documented as a
  reproducibility limit.
- 🔴 **GPT-5.4 runs on Le's machine, handed back as a tarball.** D-34 in
  `02-CONTEXT.md`; `docs/neurips2026-gpt5-handoff.md`. Azure tenant, TPM quota,
  exact deployment SKU all private to Le. Not reproducible even by another
  collaborator with Azure access. **ACKNOWLEDGED** as throughput design; no
  mitigation.
- 🔴 **S-VERIFY rewrote PASS semantics retroactively.** `evaluation.md:247-254`.
  Pre-fix and post-fix PASSes are incommensurable; old results not re-verifiable
  (truncated `translated_files`). Any longitudinal comparison in the paper
  (e.g., "Qwen 2024 vs 2026") is unsound across this boundary. **ACKNOWLEDGED**
  technically; paper must avoid the comparison.
- 🔴 **`azure-gpt-5.4` is not yet a runnable identifier.** `.planning/PROJECT.md:3`,
  `experiment-plan §2.4`. MODEL_REGISTRY contains only `azure-gpt-4.1` at
  2026-04-16. Paper submitted with `azure-gpt-5.4` results requires the registered
  deployment to exist at review time, 12+ months later. Azure deprecates and
  renames deployments. **ACKNOWLEDGED** as pending task.
- 🟡 **`api_version="2025-01-01-preview"` pinned in code.**
  `llm_evaluate.py:871`. Preview API surfaces change; reproducer two years later
  may hit auth/schema errors. **UNDISCUSSED.**
- 🟡 **`max_completion_tokens` vs `max_tokens` differ across providers.**
  `llm_evaluate.py:880,915,949,993`. Cross-provider ceilings in code, not
  documented in the paper. **UNDISCUSSED.**
- 🟡 **GPT-4.1 results on disk but model deprecated.** `.planning/PROJECT.md:50-52` + archive.
  Paper drops those runs, but the repo ships with ~1200 non-reproducible JSONs in
  `results/evaluation/gpt-4.1-*/`. **ACKNOWLEDGED** via memory
  (`feedback_protect_cuda_omp_results`).
- 🟢 **Augmentation is deterministic seed=42.** `experiment-plan §5`. Reproducible
  module of upstream libclang 18.1.1 pinned. **MITIGATED.**
- 🟡 **Qwen-vs-GPT sampling-control asymmetry (provider seed + top_p).**
  Plan 02-10 Step 2 (C1-C4) added `seed` + `top_p=1.0` across all provider
  branches in `llm_evaluate.py`. Together AI accepts both kwargs (verified
  2026-04-18 smoke test). Azure `gpt-5.3-chat` could not be smoke-tested at
  handoff time — the configured `AZURE_OPENAI_ENDPOINT` points to a
  `gpt-4.1` deployment and returned `DeploymentNotFound` for the 5.3-chat
  deployment name. Azure reasoning-model paths use `max_completion_tokens`
  with `reasoning_effort="medium"` when thinking is on; OpenAI/Azure
  reasoning endpoints historically reject `top_p` and sometimes `seed`.
  **If the Phase 3 launch surfaces a 400-class rejection from Azure, the
  asymmetry is real and must be documented in the paper — Qwen samples
  will carry a seed the provider treats as a hint, GPT samples will not
  carry one at all.** `seed` is also best-effort even on Together AI
  (Qwen3.5-397B MoE was observed to produce different completions on
  identical seeds in the 2026-04-18 smoke test). **ACKNOWLEDGED**,
  validation deferred to Phase 3 launch.

## 6. Mitigations vs acknowledged gaps

### What exists in-repo

- Validation waves (`CLAUDE.md:104-105`) + pre-commit gate.
- Schema tests: `scripts/validate_schema.py`, `c_augmentation/test_transforms.py`
  (15 tests).
- Known-issues tracking: `.claude/rules/known-issues.md` +
  `known-issues-archive.md` (active guardrails + historical fixes).
- Pipeline audit 2026-04-09 (found 1 regex bug, 9 results affected — all KNOWN_FAIL;
  `known-issues.md:80-90`).
- Pass@k estimator uses the Chen et al. 2021 unbiased form (`experiment-plan
  Appendix A`).
- FALSE_PASS hunting (`known-issues-archive.md:240-255`) — 9 FALSE_PASS specs
  found + fixed via run-arg and runner.py changes.
- Immutable result JSONs + hook-based deletion protection
  (`known-issues-archive.md:283-293`).
- Per-model cost tracking protocol (experiment-plan §7).

### What is acknowledged but not fixed (paper Phase-4 TODO)

- L0-failer audit sample deferred (`.planning/PROJECT.md:79` — "COMMITMENT (not yet
  fulfilled): paper's threats-to-validity section must acknowledge ...").
- Budget overshoot: **Gal sign-off CONFIRMED 2026-04-17** (memory
  `project_budget_overshoot.md` updated this commit). Previously PENDING in
  `.planning/PROJECT.md:80`.
- GPT-5.4 MODEL_REGISTRY registration (pending, `.planning/PROJECT.md:81` — Phase 2 02-01).
- Portability of `config/paths.json` — deferred post-NeurIPS.
- Threats-to-validity subsection itself — this file is the source; Phase 4 must
  convert to paper prose.

### UNDISCUSSED (most dangerous new gaps surfaced by this report)

- **Training-data contamination (leakage).** All 5 suites are public on GitHub;
  Rodinia predates 2014, HeCBench is active, XSBench/RSBench widely mirrored.
  Both Qwen 3.5 and GPT-5.4 likely saw these kernels in training. "Translate" cannot
  be distinguished from "recall".
- **Provider non-determinism at T=0.7.** Provider-side speculative decoding /
  batching means repeated calls with identical seed can drift. No `seed` parameter
  is threaded into any `chat.completions.create(...)` call in
  `llm_evaluate.py:878,913,947,991`.
- **`finish_reason="length"` masquerades as BUILD_FAIL.** If the model hits
  `max_completion_tokens` mid-translation, extraction fails → BUILD_FAIL → counted
  as capability failure. No result-JSON field classifies truncation separately from
  "wrong code".
- **No inter-model agreement analysis.** Do Qwen and GPT-5 agree on which cells
  pass? Disagreement structure is informative and unreported.
- **No adversarial / prompt-robustness testing.** All prompts are a single
  deterministic template from `spec_loader.py:get_prompt_payload`; small prompt
  perturbations might shift pass rates materially.
- **No construct-validity audit.** No human-labeled "semantically correct" check on
  any sample.
- **No cross-machine replication.** Qwen runs only on RTX 4070; no even-small
  re-run on a second box.
- **No tokenization-level confound check.** Together's Qwen tokenizer vs Azure's
  GPT-5 tokenizer inflate non-English comments differently, shifting prompt-token
  budgets per cell non-uniformly.
- **Fairness-of-failure-labels across providers.** `finish_reason` values from
  Azure/Groq/Together are not classified "truncated due to ceiling" vs "natural
  stop" (`llm_evaluate.py:884-887,919-921,959-961,1004-1007`). If one provider
  truncates more often, its BUILD_FAIL rate inflates for a non-capability reason.

### Additional threats outside the 6 prompted sections

- **Training-data contamination** (leakage) — see UNDISCUSSED list above.
- **Provider-side non-determinism at T=0.7** — see UNDISCUSSED list.
- **`finish_reason="length"` silently masquerades as BUILD_FAIL** — see UNDISCUSSED
  list.
- **Protected CUDA↔OMP results hook creates replay asymmetry.**
  `known-issues-archive.md:286-293` — `protect-cuda-omp-results.sh` blocks rm on
  cuda↔omp JSONs and blocks `run_eval_batch.py` without `--resume` for those
  directions. Safety mechanism, but cuda↔omp is privileged vs other directions;
  if bug-fix reruns become necessary post-hoc for 1 direction, the hook makes
  that direction's results effectively frozen. **ACKNOWLEDGED** (memory).

---

## Section-by-section counts

Severity-bulleted entries in §§1–5 (verbatim bullet counts):

| Section                              | 🔴 high | 🟡 med | 🟢 low |
| ------------------------------------ | ------: | -----: | -----: |
| 1. Internal validity                 |       4 |      5 |      1 |
| 2. External validity                 |       5 |      3 |      0 |
| 3. Construct validity                |       4 |      2 |      0 |
| 4. Statistical / design              |       5 |      3 |      1 |
| 5. Reproducibility                   |       6 |      3 |      1 |
| **§§1–5 total (bullet-verified)**    |  **24** | **16** |  **3** |

§6 mitigations catalog (prose, not severity-bulleted; counts are approximate
and overlap partially with §§1–5 🔴 entries rather than adding to them):

| §6 bucket                                | Approx count | Overlaps §§1–5? |
| ---------------------------------------- | -----------: | --------------- |
| "What exists in-repo" (🟢-like)          |            8 | mostly new      |
| "Acknowledged but not fixed" (🟡-like)   |            5 | yes, §§1–5      |
| "UNDISCUSSED" (🔴-like)                  |            9 | yes, §§1–5      |
| "Additional threats outside 6 sections"  |            4 | 3 recur under UNDISCUSSED |

Of the 24 🔴 in §§1–5, roughly **10 are UNDISCUSSED** in any repo doc (most
dangerous for reviewer attack), **~11 are ACKNOWLEDGED** in design docs but not
mitigated, **3 are partially MITIGATED-NARROWLY** (regex bug, S-VERIFY fix,
seed-pinned augmentation). The 5 in the executive punchline are the most likely
single-threat rejection vectors; the next tier (training-data contamination,
construct-validity unaudited, cross-model compute asymmetry, finish-reason
masquerade, single hardware platform) are the ones that could turn a weak-accept
into a weak-reject.

---

*Authored by an Opus explorer agent with read-only access to the full repo
(2026-04-17). Intended as a source document for the Phase 4 paper subsection,
not as paper prose itself. Update this file whenever new threats are discovered
or existing ones are mitigated.*
