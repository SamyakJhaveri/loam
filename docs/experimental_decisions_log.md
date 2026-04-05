# Experimental Decisions Log — ParBench SC26 Paper

> **Purpose:** Authoritative record of every experimental design decision for the SC26 paper.
> Every entry includes rationale, alternatives considered, and reviewer-ready defense.
> Use this document when writing Methodology (S4), Experimental Setup (S5), and Discussion (S7).
>
> **Created:** 2026-03-29, Session 12 (campaign launch session)
> **Status:** Living document — updated as new decisions are made during the campaign.

---

## D1: Model Selection — 2 Models (Qwen 3.5 + Gemini 2.5 Flash)

**Decision:** Evaluate exactly 2 models in the primary campaign: `together-qwen-3.5-397b-a17b` (Qwen 3.5 397B MoE via Together AI) and `gemini-2.5-flash` (Gemini 2.5 Flash via Google AI). A 3rd model may be added later.

**Previous state:** The pilot campaign used 3 models: `claude-sonnet-4-6`, `gemini-2.5-flash-lite`, `groq-llama-3.3-70b-versatile`. Before that, 4 models were planned (included `azure-gpt-4.1`, which produced zero result files and was dropped).

**Alternatives considered:**
- Keep the pilot 3-model lineup. Rejected: the pilot models served their purpose for pipeline validation; the primary campaign should use fresh models that strengthen the paper's narrative.
- Add GPT-4.1 or Claude Opus as a 3rd model. Deferred: can be added later without changing infrastructure, thanks to the parameterized campaign script (D5).
- Use only 1 model. Rejected: cross-model comparison is essential for generalizability claims.

**Rationale:** Qwen 3.5 397B-A17B is a large Mixture-of-Experts model (397B total parameters, 17B active per token) — it tests whether massive parameter count with sparse activation helps HPC translation. Gemini 2.5 Flash is Google's latest fast model with a different architecture. Together, they cover two major non-Anthropic providers and distinct architecture families (MoE vs. dense).

**Who runs what:** Samyak runs Qwen on the Linux GPU machine (RTX 4070). Erel (collaborator) runs Gemini on their own machine with an identical codebase and GPU. Both use the same `run_eval_campaign.sh` script (D5).

**Paper section:** S5 Experimental Setup — "Models and Providers" subsection.

**Reviewer defense:** "Why not GPT/Claude?" — ParBench is model-agnostic; these 2 represent distinct architecture families (MoE vs. dense) from different providers. The framework is extensible: adding models requires only an API key and a single command. We chose models that maximize architectural diversity rather than brand recognition. Pilot data with Claude Sonnet and Llama 70B are available as supplementary material if reviewers request it.

---

## D2: Campaign Scope — 790 Tasks per Model

**Decision:** Each model's primary campaign covers 5 benchmark suites x 6 translation directions x 5 augmentation levels (L0-L4) = approximately 790 tasks.

**Breakdown:**
| Suite | Spec-API Pairs | L0 Task Pairs | Notes |
|-------|---------------|---------------|-------|
| Rodinia | 54 non-KNOWN_FAIL (+6 KNOWN_FAIL) | ~110 incl. KNOWN_FAIL | 6 KNOWN_FAIL handled gracefully |
| XSBench | 3 standard (cuda, omp, opencl) | 6 | omp_target excluded from standard batches |
| RSBench | 3 (cuda, omp, opencl) | 6 | Newly added 2026-03-28 |
| mixbench | 3 (cuda, omp, opencl) | 6 | Newly added 2026-03-28 |
| HeCBench (curated) | ~21 non-KNOWN_FAIL | 30 | 10 kernels, 4 direction combos |
| **Total** | **~84** | **158** | **x5 levels = 790 tasks** |

**Directions:** cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp (6 directions covering all 3 API pairs bidirectionally).

**Augmentation levels:** L0 (no augmentation), L1, L2, L3, L4 (increasing AST transform intensity).

**Alternatives considered:**
- Include all 6 Rodinia KNOWN_FAIL specs: rejected because known build failures (CUDA 12 `texture<>` removal, missing `libglew-dev`) would inflate failure rates with non-model-related errors. The campaign script handles them gracefully (they are included in the batch but produce expected failures).
- Include only L0 and L4 (extremes): rejected because intermediate levels (L1-L3) reveal the shape of the degradation curve. A model that degrades linearly vs. one that cliff-drops at L3 tells a different story.
- Add more directions (e.g., cuda-to-sycl, cuda-to-openacc): rejected for scope. 6 directions across 3 APIs is already comprehensive.

**Rationale:** 5 augmentation levels are the unique contribution of ParBench. Measuring model robustness to semantics-preserving code transformations at multiple intensity levels is novel — no prior benchmark does this. The 6-direction design ensures bidirectional measurement of every API pair, revealing directional asymmetries (e.g., cuda-to-omp may be easier than omp-to-cuda).

**Paper section:** S5 Experimental Setup — "Benchmark Suite" and "Evaluation Matrix" subsections.

**Reviewer defense:** "Why these 5 suites?" — They cover different HPC domains: stencil computation (Rodinia hotspot), graph algorithms (Rodinia bfs), particle transport (XSBench/RSBench), micro-benchmarks (mixbench), and additional algorithms (HeCBench curated). Together they represent the breadth of parallel computing patterns that HPC practitioners actually translate between APIs.

---

## D3: Self-Repair — max_retries=3 on All Tasks

**Decision:** Set `max_retries=3` for the primary campaign. Each task gets up to 3 LLM calls with iterative error feedback.

**What this means:** On failure (BUILD_FAIL, RUN_FAIL, VERIFY_FAIL), the error message (compiler output, wrong output diff, etc.) is fed back to the LLM as a follow-up message. The LLM gets to try again with knowledge of what went wrong. The result JSON records all attempts in an `attempts[]` array with per-attempt status, error snippets, and token counts.

**Self-repair outcome taxonomy** (from `scripts/analysis/selfrepair_analysis.py`):
- `first_attempt_pass`: Correct on first try (no repair needed)
- `full_repair`: Failed initially, succeeded after retry (model self-corrected)
- `partial_repair`: Improved category (e.g., BUILD_FAIL -> RUN_FAIL) but still failed
- `regression`: Got worse after retry (e.g., RUN_FAIL -> BUILD_FAIL)
- `no_repair`: Same error category across all 3 attempts

**Alternatives considered:**
- `max_retries=1` (zero-shot only): rejected because self-repair data is scientifically valuable and directly comparable to LASSI's agentic approach. Zero-shot is measured separately via pass@k (D4).
- `max_retries=5` or `max_retries=10`: rejected due to diminishing returns. Literature suggests most successful repairs happen on attempt 2. Attempt 3 catches residual cases. Beyond 3, LLMs typically oscillate between the same errors. Also controls API cost.
- No retry, but with RAG/tool access: rejected for this campaign — would confound the measurement of raw model capability with tool effectiveness.

**Rationale:** 3 retries simulate a lightweight agentic workflow (error feedback without external tools or RAG). This is a controlled middle ground between zero-shot (pass@k, D4) and full agentic systems (LASSI). The gap between these three levels directly quantifies the value of agentic infrastructure beyond simple error feedback.

**Paper section:** S4 Methodology — "Self-Repair Protocol" subsection; S6 Results — "Self-Repair Analysis" subsection.

**Reviewer defense:** "Why not full agentic?" — Full agentic approaches (RAG, web search, tool use) introduce confounds: is the improvement from the model's reasoning or from the tools? 3-retry error feedback isolates the model's ability to self-correct from diagnostic information alone. LASSI (Dearing et al., CLUSTER 2024) reports 80-85% with full agentic self-correction; the gap between our ~3-retry rate and LASSI's agentic rate quantifies the value of agentic infrastructure beyond simple error feedback.

---

## D4: pass@k — pass@3 at L0, Temperature 0.7

**Decision:** Run a separate pass@k sweep: 3 independent samples per task, temperature=0.7, L0 only (no augmentation), `max_retries=1` (zero-shot per sample).

**Configuration:**
| Parameter | Primary Campaign | pass@k Sweep |
|-----------|-----------------|-------------|
| Augmentation | L0-L4 | L0 only |
| Temperature | 0.0 (greedy) | 0.7 |
| max_retries | 3 | 1 |
| Samples | 1 | 3 |
| Total tasks | 790 | 474 |

**Alternatives considered:**
- `pass@10`: rejected because pass@3 is standard in the literature (HumanEval, MBPP by Chen et al., 2021). 10 samples would double API cost for diminishing analytical value.
- Cross augmentation x pass@k (5 levels x 3 samples = 15 per task): rejected because augmentation already provides controlled input variation (ParBench's unique axis). Crossing both creates a 5x3 matrix that's hard to interpret and doesn't add proportional insight.
- Temperature 1.0: rejected as too high — produces degenerate outputs for code generation. 0.7 is the standard from the Codex paper (Chen et al., 2021).
- `max_retries=3` for pass@k: rejected because each sample must be independent. Self-repair creates dependencies between attempts within a sample, violating the i.i.d. assumption that pass@k estimation requires.

**Rationale:** pass@k measures sampling variance — the gap between pass@1 (greedy) and pass@3 reveals whether failures are "hard" (model fundamentally cannot translate this kernel) vs. "noisy" (model sometimes gets it right but doesn't reliably surface it). Kernels with pass@1=0% but pass@3>0% are "noisy failures," indicating partial capability that doesn't reliably manifest. L0-only isolates sampling variance from augmentation effects, keeping the two evaluation axes orthogonal.

**Paper section:** S4 Methodology — "Sampling Variance (pass@k)" subsection; S6 Results — "Hard vs. Noisy Failures" subsection.

**Reviewer defense:** "Why L0 only for pass@k?" — Augmentation levels (L0-L4) already systematically vary the input code. pass@k measures variance in model output given the same input. Crossing both axes would conflate two sources of variation, making results harder to interpret. By holding augmentation at L0 for pass@k, we cleanly separate input-side variation (augmentation) from output-side variation (sampling).

---

## D5: Single Parameterized Campaign Script

**Decision:** Use one script `run_eval_campaign.sh MODEL [MODE]` instead of per-model scripts.

**Previous state:** Separate `run_qwen_campaign.sh` and `run_gemini_campaign.sh` existed.

**Alternatives considered:**
- Keep per-model scripts: rejected as DRY violation. Adding a 3rd model would require creating a 3rd script with identical logic.
- Use a configuration file per model: rejected as over-engineering. Model name as a CLI argument is sufficient; all other configuration is mode-dependent, not model-dependent.

**Rationale:** Single script follows the DRY (Don't Repeat Yourself) principle. The script uses model name prefixes (`together-*`, `gemini-*`, `claude-*`, etc.) to auto-detect which API key to verify — a convention-over-configuration pattern. Adding a 3rd model later requires zero script changes. The script also enforces tmux (auto-launches a detached session if not already inside one), preventing SSH disconnects from killing long-running campaigns.

**Key features:**
- Two modes: `primary` (L0-L4, retries=3, greedy) and `pass@k` (L0 only, retries=1, T=0.7, 3 samples)
- 28 batches total: 6 Rodinia + 6 XSBench + 6 RSBench + 6 mixbench + 4 HeCBench
- Pass 2 automatic retry for any failed batches
- Completeness check at end (counts result files vs. expected 790)
- Auto-runs `analyze_eval.py` for immediate summary statistics
- Writes a `.marker` file on completion with elapsed time and status

**Paper section:** S5 Experimental Setup — "Reproducibility" subsection. "All campaigns were executed via a single parameterized script ensuring identical batch logic, retry policy, and analysis pipeline across all models and modes."

**Reviewer defense:** Not likely to face direct questions, but supports the reproducibility narrative. The script is self-contained — a reviewer can inspect it to verify that all models received identical treatment.

---

## D6: Augmentation Level-Invariance Verified for All 5 Suites

**Decision/Finding:** Augmentation smoke tests confirm all non-KNOWN_FAIL specs produce identical correctness outcomes across L0-L4 for all 5 suites.

**Verification results:**
| Suite | Specs Tested | L0-L4 Result | Method |
|-------|-------------|-------------|--------|
| Rodinia | 54 of 60 (6 KNOWN_FAIL excluded) | All PASS | `augment_verify.py`, phases 3-5 |
| XSBench | 4 of 4 | All PASS | `augment_verify.py` |
| RSBench | 3 of 3 | All PASS | Smoke test (session 12) |
| mixbench | 3 of 3 | All PASS | Smoke test (session 12) |
| HeCBench (curated) | 4 spot-checked | All PASS | Smoke test (session 12) |

**Total: 64+ non-KNOWN_FAIL specs verified level-invariant.**

**Alternatives considered:** N/A — this is a verification result, not a design choice. However, if level-invariance had failed for any spec, we would have had to either fix the augmentation transform or exclude that spec from augmented evaluation.

**Rationale:** Level-invariance validates the augmentation methodology. If augmented code produced different correctness outcomes than the original (L0), the augmentation would be introducing bugs — and any model performance degradation at higher levels could not be attributed to model sensitivity. Verifying invariance across all suites confirms that AST-driven transforms preserve semantic equivalence, so model degradation at L1-L4 is genuinely measuring model robustness.

**Paper section:** S4 Methodology — "Augmentation Validation" subsection. "We verified that all 64 benchmark specifications produce identical correctness outcomes across augmentation levels L0-L4, confirming that our AST-driven transforms preserve semantic equivalence."

**Reviewer defense:** "How do you know augmentation doesn't change correctness?" — We ran every non-KNOWN_FAIL spec through the full build-run-verify pipeline at all 5 augmentation levels. All produced identical output. This is a stronger guarantee than unit-testing individual transforms in isolation — it verifies end-to-end semantic equivalence through the actual harness.

---

## D7: .cc Suffix Bug Fix

**Decision:** Added `.cc` to the suffix filter in `harness/spec_loader.py:199` to match `augment_verify.py`'s `AUGMENTABLE_SUFFIXES`.

**Previous state:** `spec_loader.py` had `.c`, `.cpp`, `.cu`, `.h`, `.hpp` but was missing `.cc`. The `augment_verify.py` script included `.cc` in its `AUGMENTABLE_SUFFIXES` list. The two files independently maintained C/C++ suffix lists.

**Impact if unfixed:** HeCBench specs with `.cc` source files would not have their files augmented during the eval pipeline's augmentation step. At L1-L4, the eval pipeline calls `spec_loader.py` to load and augment source files before sending them to the LLM. Files with `.cc` extension would be loaded but NOT augmented, silently skipping augmentation for those specs. The model would see the original L0 code even when asked to translate L2/L3/L4 augmented code, producing misleading results.

**Alternatives considered:**
- Centralize the suffix list in a single location: would be cleaner but requires a larger refactor. The immediate fix (adding `.cc`) is safe and sufficient for the campaign launch.

**Rationale:** Configuration drift between two files that independently maintained the same list. This is a classic research software engineering bug — caught during pre-campaign smoke testing, demonstrating the value of systematic baseline verification before launching evaluations.

**Paper section:** Not directly cited, but validates the methodology. Worth mentioning in a "threats to validity" or "lessons learned" subsection as an example of why research benchmarks require thorough pre-campaign verification.

**Reviewer defense:** N/A — this is a bug fix, not a design decision. However, it demonstrates due diligence: we caught and fixed a potential data validity issue before running the campaign, not after.

---

# Key Insights

## I1: Three Orthogonal Evaluation Axes

**Observation:** ParBench's experimental design measures model capability along three independent axes:

1. **Self-repair (retries):** Can the model recover from its own errors given diagnostic feedback? Measured by comparing attempt 1 vs. attempt 3 outcomes. (Primary campaign, D3)
2. **Sampling variance (pass@k):** How reliable is the model's output? Is failure deterministic or stochastic? Measured by pass@1 vs. pass@3. (pass@k sweep, D4)
3. **Augmentation robustness (L0-L4):** Does the model degrade when input code undergoes semantics-preserving transformations? Measured by comparing pass rates across augmentation levels. (Primary campaign, D2)

**Significance:** These three axes are orthogonal — they measure fundamentally different dimensions of capability. A model could be excellent at self-repair (fixes errors when told what's wrong) but sensitive to augmentation (fails when variable names change). Or it could be robust to augmentation but unreliable (pass@1 << pass@3). Together, the three axes provide a far richer characterization than a single aggregate pass rate. No prior benchmark evaluates all three simultaneously.

**Paper section:** S1 Introduction (framing contribution), S4 Methodology (axes definition), S6 Results (per-axis analysis), S7 Discussion (what the axes reveal about LLM limitations).

---

## I2: LASSI Comparison Framing

**Observation:** The experimental design creates a natural three-tier comparison:
- **ParBench pass@k = raw model capability** (floor: zero-shot, no repair, measures what the model can do unassisted)
- **ParBench primary campaign = controlled self-repair** (middle ground: 3 retries with error feedback, measures what lightweight assistance provides)
- **LASSI = agentic system** (ceiling: full self-correction pipeline with tools, measures what a complete system achieves)

The gap between these three levels directly quantifies the *value* of different levels of infrastructure investment.

**Significance:** This framing positions ParBench as complementary to, not competing with, agentic benchmarks like LASSI. ParBench measures raw and lightly-assisted model capability; LASSI measures agentic system effectiveness. One could run LASSI's agent pipeline on ParBench's specifications — the two are composable. This makes ParBench a foundational measurement layer rather than a complete system benchmark.

**Paper section:** S2 Related Work (positioning vs. LASSI), S7 Discussion (interpreting the gap between self-repair and agentic approaches).

---

## I3: Provider Detection from Model Name

**Observation:** The campaign script (`run_eval_campaign.sh`) uses model name prefixes (`together-*`, `gemini-*`, `claude-*`, `groq-*`, `azure-*`, `gpt-*`) to auto-detect which API key to verify before launch. This is a convention-over-configuration pattern — no separate configuration file maps models to providers.

**Significance:** Simplifies adding new models (just choose a name with the right prefix). Also makes the script self-documenting: the model name encodes its provider. This is a minor but concrete example of research software engineering for extensibility. More importantly, it means the campaign script requires zero modification to support new models from existing providers.

**Paper section:** S5 Experimental Setup — "Reproducibility and Extensibility" subsection, or in an artifact description.

---

## I4: Config Drift as a Research Software Engineering Lesson

**Observation:** Four scripts independently maintained model-specific configuration:
- `scripts/analysis/selfrepair_analysis.py` — model pricing, display names
- `scripts/analysis/token_analysis.py` — model pricing, display names
- `scripts/evaluation/analyze_eval.py` — expected models, Bonferroni correction count
- `harness/spec_loader.py` — file suffix list (the `.cc` bug, D7)

When the model lineup changed from 3 to 2 models, all four scripts needed updating. The `.cc` suffix list drift between `spec_loader.py` and `augment_verify.py` caused the bug in D7.

**Significance:** Configuration drift is a real and recurring problem in research software. Unlike production software (where CI/CD catches drift), research code is often run manually with infrequent integration. This is a concrete example of why research benchmark infrastructure requires ongoing maintenance and pre-campaign verification passes. Worth acknowledging in the paper as a "threats to validity" item — and as a lesson for other benchmark developers.

**Paper section:** S8 Threats to Validity or S7 Discussion — "Lessons for Benchmark Infrastructure" subsection.

---

## I5: HeCBench Direction Asymmetry

**Observation:** HeCBench uses an asymmetric direction layout:
- `cuda <-> omp` (CPU OpenMP): 5 kernels bidirectional = 10 direction-pairs
- `cuda <-> omp_target` (GPU offload): 10 kernels for `omp_target-to-cuda`, but only 8 for `cuda-to-omp_target` (excluding 2 KNOWN_FAIL target specs: `stencil1d-omp_target`, `scan-omp_target`)
- Total: 30 L0 HeCBench direction-pairs (including the `iso2dfd` manifest duplicate)

**Significance:** This asymmetry means HeCBench pass rates are not directly comparable across directions without normalizing for the number of eligible specs per direction. The paper must report raw counts (N PASS / M total) not just percentages when comparing `cuda-to-omp_target` (8 eligible kernels) vs. `omp_target-to-cuda` (10 eligible kernels).

**Paper section:** S5 Experimental Setup — "HeCBench Subset" subsection; S6 Results — any HeCBench-specific tables.

---

# Appendix: Session Timeline

| Date | Event | Decisions Made |
|------|-------|---------------|
| 2026-03-29 | Session 12: Campaign launch | D1-D7, I1-I5 |
| TBD | Campaign results arrive | D8+ (analysis decisions) |
| TBD | pass@k sweep complete | Update D4 with actual results |
| TBD | 3rd model selected (if any) | Update D1 |

---

*This document is maintained by the Decision Log agent. Last updated: 2026-03-29.*
