# SC26 Paper Writing Roadmap — ParBench

**Generated:** 2026-03-29
**Deadline:** April 8, 2026 (10 days remaining)
**Format:** IEEE IEEEtran double-column, 10 pages + references
**Current draft:** `docs/paper/paper_draft.md` (669 lines, STALE 3-model pilot data)
**New campaign:** 2-model (Qwen 3.5 397B + Gemini 2.5 Flash), results pending
**Paper strategy:** ALL numbers become [PLACEHOLDER] until new campaign data arrives

---

## A. IEEE 10-Page Column Budget

IEEE double-column = ~20 columns of content across 10 pages. Each column is ~55 lines of text or equivalent in figures/tables. Budget below includes figures, tables, and equations.

| Section | Columns | Pages | Rationale |
|---------|:-------:|:-----:|-----------|
| **S1 Introduction** | 2.0 | 1.0 | Motivation, gap, contributions, findings preview. Tight — must not exceed 1 page. |
| **S2 Related Work** | 2.5 | 1.25 | Table 1 comparison matrix (~0.5 col) + 5 subsections. Expanded from draft to address W2/W3/W10. |
| **S3 Framework** | 3.0 | 1.5 | Fig 1 architecture (~0.5 col) + spec schema + harness + augmentation + eval pipeline. Core contribution — needs space. |
| **S4 Benchmark Curation** | 1.5 | 0.75 | Survey results + Table 3 (kernel counts) + selection criteria. Compressed from draft. |
| **S5 Experimental Setup** | 2.0 | 1.0 | NEW 2-model lineup + directions + augmentation protocol + metrics + hardware. Table 5 (models). |
| **S6 Results** | 4.5 | 2.25 | Heaviest section: Tables 7-11 + Figures 3-5 + statistical analysis. Expanded for W4 (CIs) and pass@k. |
| **S7 Discussion** | 2.5 | 1.25 | Kernel-centric advantage + BUILD_FAIL analysis + augmentation robustness + threats to validity. |
| **S8 Conclusion** | 1.0 | 0.5 | Summary + future work. Keep tight. |
| **References** | 1.0 | 0.5 | ~25-30 references in IEEE format. |
| **TOTAL** | **20.0** | **10.0** | |

**Budget notes:**
- S6 gets the most space (4.5 columns) because it carries the empirical contribution with multiple tables and figures.
- S3 gets 3.0 columns because the framework (spec schema, harness, augmentation, eval pipeline) is the primary contribution.
- S2 expanded from original 1.0-page target to 1.25 pages to properly address LASSI/CodeRosetta/missing papers (W2/W3/W10).
- S4 compressed from 1.0 to 0.75 pages — survey data is important but can be presented concisely with a good table.
- If space is tight, S7.5 (Threats to Validity) can be compressed to ~0.5 columns by removing the most defensive items.

---

## B. Per-Section Status: EXISTS vs NEEDS WRITING vs NEEDS DELETING

### S1 Introduction (2.0 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 1.1 Motivation | EXISTS (good quality) | KEEP — minor edits only. Remove any 3-model pilot numbers. |
| 1.2 Gap in Existing Evaluation | EXISTS (good quality) | KEEP — the four-gap framing (sequential benchmarks, parallel generation, repo-level, training data contamination) is strong. Update ParEval-Repo citation with DOI. |
| 1.3 Contributions | EXISTS but STALE | REWRITE — change "184 specs across three suites" to "N specs across five suites" (5 suites now: Rodinia, XSBench, RSBench, mixbench, HeCBench). Change "three LLMs" to "two LLMs" (Qwen + Gemini). All numbers become [PLACEHOLDER]. Add pass@k as a contribution dimension. |
| 1.4 Key Findings Preview | EXISTS but STALE | REWRITE COMPLETELY — every number is from the pilot. Replace with [PLACEHOLDER] markers for: overall pass rate, per-model rates, BUILD_FAIL %, VERIFY_FAIL %, augmentation robustness finding, direction asymmetry. Structure around the three orthogonal evaluation axes (I1 from decisions log): self-repair, pass@k, augmentation robustness. |

**DELETE:** All references to Claude Sonnet, Gemini Flash-Lite, Llama 3.3 70B, "562 tasks", "468 tasks", "54.26%", "8.56%", "10.16%", "two-tier capability gap", specific Fisher's p values, specific chi-squared values. These are pilot data.

### S2 Related Work (2.5 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 2.1 Three-Granularity Landscape | EXISTS (strong) | KEEP — Table 1 positioning is the right framing. Update ParBench row for 5-suite, 2-model, 8-direction scope. |
| 2.2 Code Synthesis & Translation | EXISTS (adequate) | EXPAND — Add CodeRosetta [W3] with proper comparison (encoder-decoder vs general-purpose LLM, BLEU-only vs build+run+verify). Add TransCoder-ST, BabelTower if space permits. |
| 2.3 Parallel Code Evaluation | EXISTS (adequate) | EXPAND — Add LASSI [W2] as a dedicated paragraph. Frame as complementary: LASSI = agentic ceiling, ParBench = raw capability floor (I2 from decisions log). Add HPC-Coder-V2 [W10]. Add OMPify with more detail. |
| 2.4 Repository-Level Translation | EXISTS (adequate) | KEEP — AlphaTrans, RepoTransBench positioning is fine. |
| 2.5 LLM-for-HPC | EXISTS (thin) | EXPAND — Add TRACY [W10] (execution efficiency), SWE-bench Illusion [W10] (memorization critique — directly motivates augmentation), VibeCodeHPC [W10] (agentic HPC), QiMeng-MuPa [W10] (seq-to-parallel). |
| 2.6 ParaCodex | EXISTS | KEEP as-is. |

**NEW:** Add Table 1 row for LASSI, CodeRosetta, HPC-Coder-V2. Update ParBench row.

**DELETE:** Nothing — S2 only grows.

### S3 Framework (3.0 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 3.A Spec Schema | EXISTS (good) | KEEP — update "184 specs" to actual count with 5 suites. The BFS JSON example is good. |
| 3.B Harness Pipeline | EXISTS (good) | KEEP as-is. Minor: clarify that EXTRACTION_FAIL is added by the eval pipeline, not the harness. |
| 3.C Augmentation Engine | EXISTS (good) | KEEP — 6 transforms, Table 2, level definitions are well-written. Update augmentation baseline to "64+ non-KNOWN_FAIL specs verified level-invariant across 5 suites" (was "54/60 Rodinia"). |
| 3.D Evaluation Pipeline | EXISTS (good) | MINOR UPDATE — add mention of pass@k mode (temperature=0.7, 3 samples, max_retries=1). Add parameterized campaign script as reproducibility feature (D5). Update "three LLM providers" to reflect new providers (Together AI, Google AI). |
| Figure 1 | EXISTS | KEEP — system architecture diagram. |

**DELETE:** Any specific pilot model names in 3.D.

### S4 Benchmark Curation (1.5 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 4.A Suite Selection | EXISTS (good) | UPDATE — now 5 suites, not 3. Add RSBench (particle transport), mixbench (micro-benchmark). Table 3 (kernel-level counts) stays. |
| 4.B Kernel Selection | EXISTS (good) | UPDATE — expand Rodinia paragraph. Add RSBench, mixbench, HeCBench curated (10 kernels) paragraphs. Update "57 verified-PASS specs" to actual count across 5 suites (~88 PASS). |
| 4.C API Coverage | EXISTS (adequate) | MINOR UPDATE — mention omp_target more prominently (HeCBench uses it). |
| 4.D Representative Subset | EXISTS | UPDATE — reflect 5-suite scope and ~142 translation pairs at L0 per model. |
| Table 4 | EXISTS but STALE | UPDATE — add RSBench, mixbench, HeCBench rows to Kernel x API matrix. |

**DELETE:** Any references to "3 suites" — now 5.

### S5 Experimental Setup (2.0 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 5.A Models | EXISTS but COMPLETELY STALE | REWRITE COMPLETELY — replace Claude/Gemini-Lite/Llama with Qwen 3.5 397B-A17B + Gemini 2.5 Flash. Discuss MoE vs dense architecture distinction (D1). Remove all reasoning-disabled discussion (both new models are standard). Add reviewer defense for "Why not GPT/Claude?" |
| 5.B Translation Directions | EXISTS but STALE | REWRITE — now 8 core directions (6 for CUDA/OMP/OpenCL + 2 for HeCBench CUDA/omp_target). Update direction matrix to reflect 5-suite scope. Primary direction remains cuda-to-omp. |
| 5.C Augmentation Protocol | EXISTS (good) | KEEP — L0-L4 description is accurate. Update seed mention. |
| 5.D Metrics | EXISTS but NEEDS EXPANSION | EXPAND — add pass@k metric (D4). Redefine primary metric as "greedy-decode pass@1" (addresses W5). Add confidence interval methodology (Wilson CIs). Mention three orthogonal evaluation axes (I1). |
| 5.E Hardware & Software | EXISTS (good) | KEEP — RTX 4070, Ryzen 9, Ubuntu 24.04. Add note about Erel's machine if Gemini runs there. |
| Table 5 | STALE | REWRITE — new model configurations (Qwen via Together AI, Gemini via Google AI). |
| Table 6 | EXISTS | KEEP. |

**DELETE:** All references to Claude Sonnet, Gemini Flash-Lite, Llama 3.3, Groq, azure-gpt-4.1, "three models", "468 tasks", "562 tasks".

### S6 Results (4.5 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 6.1 Overall Pass Rates | EXISTS but COMPLETELY STALE | REWRITE with [PLACEHOLDER] — all numbers from new campaign. Structure: Table 7 (model x pass rate), comparison with ParEval-Repo 0%. |
| 6.2 Failure Taxonomy | EXISTS but STALE | REWRITE with [PLACEHOLDER] — Figure 5 stacked bar. Keep the qualitative analysis structure (BUILD_FAIL = syntax, VERIFY_FAIL = logic, etc.) but all numbers are placeholders. |
| 6.3 Per-Kernel Analysis | EXISTS but STALE | REWRITE with [PLACEHOLDER] — Table 8 kernel-by-model matrix. Keep tier structure but tiers will change with new models. Add 5-suite kernel coverage. |
| 6.4 Self-Repair Effectiveness | EXISTS but STALE | REWRITE with [PLACEHOLDER] — Table 9. Keep structure: first-attempt vs repaired vs persistent. Add self-repair transition analysis (W12): which failure modes are recoverable? |
| 6.5 Augmentation Robustness | EXISTS but STALE | REWRITE with [PLACEHOLDER] — Table 10, Figure 7. CRITICAL: report per-model curves (not just aggregate). Frame as "augmentation robustness discriminates model capability" not "level-invariance" (Simpson's Paradox insight from audit). Add Cochran-Armitage trend test per model. |
| 6.6 Cross-Direction & Extended Suite | EXISTS but STALE | REWRITE with [PLACEHOLDER] — now covers 5 suites, 8 directions. Keep direction asymmetry analysis structure. Add HeCBench-specific results. |
| NEW: 6.7 pass@k Analysis | DOES NOT EXIST | WRITE NEW — pass@3 at L0, temperature=0.7 results (D4). Hard vs noisy failures. Compare pass@1 (greedy) vs pass3. |
| NEW: 6.8 Statistical Summary | DOES NOT EXIST | WRITE NEW — Wilson CIs for all major rates, chi-squared for model comparison, Cochran-Armitage for augmentation trends, McNemar for direction asymmetry. Addresses W4 directly. |

**DELETE:** All specific numbers from pilot (54.26%, 8.56%, 10.16%, chi2=136.93, OR=12.68, etc.). All references to Claude/Gemini-Lite/Llama per-kernel results.

### S7 Discussion (2.5 columns)

| Subsection | Status | Action |
|------------|--------|--------|
| 7.1 Kernel-Centric Advantage | EXISTS (strong) | KEEP structure — update comparison numbers with [PLACEHOLDER]. The argument (0% repo-level vs N% kernel-level) is model-independent. |
| 7.2 BUILD_FAIL as Bottleneck | EXISTS (strong) | KEEP structure — update % with [PLACEHOLDER]. The qualitative analysis (retained cudaMalloc, missing pragmas) likely holds for new models too. |
| 7.3 Model Capability Spread | EXISTS but STALE | REWRITE with [PLACEHOLDER] — new 2-model comparison. Discuss MoE (Qwen) vs dense (Gemini) architecture implications. |
| 7.4 Direction Asymmetry | EXISTS (strong) | KEEP structure — update numbers with [PLACEHOLDER]. The structural argument (removal vs introduction) is model-independent. |
| 7.5 Threats to Validity | EXISTS (comprehensive) | UPDATE — change "Three-model evaluation" to "Two-model evaluation" (stronger defense needed). Add W11 (Rodinia generalizability — mitigated by 5-suite expansion). Add W5 (temperature=0 → mitigated by pass@k sweep). Add W9 (no performance data → cite TRACY). Remove the "GPT-4.1 was removed" paragraph. |
| 7.6 Augmentation Robustness | EXISTS but STALE | REWRITE with [PLACEHOLDER] — per-model interpretation. Keep Simpson's Paradox framing if it applies to new data. |
| 7.7 Implications | EXISTS (adequate) | KEEP structure — update for 2-model context. Add LASSI comparison framing (I2): raw capability (ParBench pass@k) < controlled self-repair (ParBench primary) < agentic (LASSI). |

**DELETE:** All specific pilot numbers and model names.

### S8 Conclusion (1.0 column)

| Subsection | Status | Action |
|------------|--------|--------|
| 8.1 Summary | EXISTS but STALE | REWRITE — 4 contributions with [PLACEHOLDER] numbers. Update "three suites" to "five suites", "three LLMs" to "two LLMs". Add pass@k as contribution dimension. |
| 8.2 Future Work | EXISTS (adequate) | UPDATE — remove "HeCBench evaluation" (now done). Remove "add GPT-4.1" (no longer relevant). Add: more models, performance timing, agentic evaluation (ParaCodex), deeper augmentation analysis, community extension. |

**DELETE:** All pilot-specific numbers and model names.

### Abstract (~200 words)

| Status | Action |
|--------|--------|
| EXISTS but COMPLETELY STALE | REWRITE LAST — after all sections are complete. Every number is [PLACEHOLDER] until campaign results arrive. Structure: problem (1 sentence) → contribution (2 sentences) → key findings (3-4 sentences) → availability (1 sentence). |

---

## C. Audit Weakness Assignments

Each audit weakness (W1-W17) is assigned to the section(s) that must address it. Weaknesses are re-evaluated for the new 2-model campaign context.

| Weakness | Severity | Section(s) | How to Address | Status in New Campaign |
|----------|----------|------------|----------------|----------------------|
| **W1** Small-N evaluation | CRITICAL | S6, S7.5 | 5-suite expansion (142 pairs/model at L0) dramatically improves this. Primary direction cuda-to-omp now has ~24 kernels. Still caveat non-primary directions. | LARGELY MITIGATED by 5-suite scope |
| **W2** Missing LASSI comparison | CRITICAL | S2.3, S7.7 | Add dedicated LASSI paragraph. Frame three-tier comparison: pass@k (floor) < primary campaign (middle) < LASSI agentic (ceiling). Quantify the gap. | MUST ADDRESS — model-independent |
| **W3** Missing CodeRosetta | CRITICAL | S2.2, S7.7 | Add CodeRosetta paragraph. Note: encoder-decoder vs general-purpose, BLEU vs build+run+verify, single direction vs 8 directions. | MUST ADDRESS — model-independent |
| **W4** No statistical rigor | MAJOR | S6.8 (NEW), all tables | Wilson CIs on all pass rates, chi-squared for model comparison, Cochran-Armitage for augmentation trends. Already in analysis pipeline (`statistical_analysis.py`). | MUST ADDRESS — run after campaign |
| **W5** Temperature=0 methodology | MAJOR | S5.D, S6.7 (NEW) | Addressed by pass@k sweep (D4): 3 samples at T=0.7, L0 only. Redefine primary metric as "greedy-decode pass@1". | FULLY ADDRESSED by campaign design |
| **W6** Format (ACM vs IEEE) | MAJOR | LaTeX transfer | Use IEEE IEEEtran template. | ADDRESSED — decision made |
| **W7** 4-model vs 3-model | MAJOR | All sections | SUPERSEDED — new campaign is 2-model. Clean slate: no legacy model references. | SUPERSEDED — fresh start |
| **W8** Augmentation confound | MAJOR | S6.5, S7.6 | New campaign runs L0-L4 for ALL directions (not just cuda-to-omp). Eliminates the direction-composition confound. Report per-model curves. | FULLY ADDRESSED by campaign design (D2) |
| **W9** No performance data | MODERATE | S7.5 | Cite TRACY. Frame as correctness-only by design. Performance is future work. | ACKNOWLEDGED — not fixable in scope |
| **W10** 5 missing papers | MODERATE | S2 | Add LASSI, CodeRosetta, HPC-Coder-V2, TRACY, SWE-bench Illusion + newly found UniPar, OMPar, OMPGPT, TransCoder-ST, BabelTower. | MUST ADDRESS — model-independent |
| **W11** Rodinia generalizability | MODERATE | S4, S7.5 | 5-suite expansion directly addresses this. RSBench + mixbench + HeCBench curated provide kernels from different domains and eras. Mention algorithmic memorization as irreducible threat. | LARGELY MITIGATED by 5-suite scope |
| **W12** Self-repair incomplete | MINOR | S6.4 | Add repair transition table: which failure modes are recoverable (BUILD_FAIL->PASS, etc.). Add attempt-number distribution. Script exists (`selfrepair_analysis.py`). | MUST ADDRESS — run after campaign |
| **W13** XSBench asymmetric reporting | MINOR | S6.6 | With 5 suites, XSBench is no longer the only non-Rodinia data. Normalize per-kernel task counts in tables. | LARGELY MITIGATED |
| **W14** Wrong numbers in draft | CRITICAL | All | SUPERSEDED — all pilot numbers are being replaced with [PLACEHOLDER]. No stale numbers will survive. | SUPERSEDED — clean slate |
| **W15** No LaTeX draft | CRITICAL | LaTeX transfer | Separate workstream. Not a writing-roadmap item. | MUST ADDRESS — parallel track |
| **W16** Non-primary directions missing | MAJOR | S6.6 | New campaign runs ALL 6 core directions for Rodinia + all directions for other suites. Eliminates the "only 2 directions have Rodinia data" problem. | FULLY ADDRESSED by campaign design (D2) |
| **W17** No anonymous repo | MODERATE | Submission prep | Separate workstream. Not a writing-roadmap item. | MUST ADDRESS — after writing |

**Summary:** Of the 17 original weaknesses:
- 6 are FULLY ADDRESSED by the new campaign design (W5, W6, W7, W8, W14, W16)
- 3 are LARGELY MITIGATED by 5-suite expansion (W1, W11, W13)
- 6 MUST BE ADDRESSED in writing (W2, W3, W4, W10, W12, W17)
- 2 are ACKNOWLEDGED but out of scope (W9, W15)

---

## D. [PLACEHOLDER] Catalog

Every number/table/figure that depends on new campaign data. These MUST remain as `[PLACEHOLDER]` until results arrive.

### Numbers (inline text)

| Location | Placeholder | What It Needs |
|----------|-------------|---------------|
| Abstract | `[OVERALL_PASS_RATE]` | X/Y = Z% across 2 models, all directions, all levels |
| Abstract | `[MODEL_A_PASS_RATE]` | Qwen pass rate with 95% Wilson CI |
| Abstract | `[MODEL_B_PASS_RATE]` | Gemini pass rate with 95% Wilson CI |
| Abstract | `[TOTAL_TASKS]` | Total evaluated tasks (790 x 2 models = ~1580) |
| Abstract | `[BUILD_FAIL_PCT]` | BUILD_FAIL % of all failures |
| Abstract | `[VERIFY_FAIL_PCT]` | VERIFY_FAIL % of all failures |
| Abstract | `[AUGMENTATION_TREND]` | Cochran-Armitage result (overall and per-model) |
| S1.3 | `[SPEC_COUNT]` | Total specs across 5 suites (~96 non-KNOWN_FAIL) |
| S1.3 | `[DIRECTION_COUNT]` | Number of translation directions (8 core) |
| S1.4 | `[PRIMARY_DIR_PASS]` | Best model cuda-to-omp L0 pass rate |
| S1.4 | `[PASSK_FINDING]` | pass@1 vs pass@3 gap summary |
| S5.B | `[PAIRS_PER_MODEL]` | ~142 at L0, ~710 at L0-L4 |
| S6 all | Every number in S6 | All results from new campaign |
| S7 all | Every comparison number | Derived from S6 data |
| S8.1 | `[SUMMARY_NUMBERS]` | Repeat of key findings |

### Tables

| Table | Content | Data Source |
|-------|---------|-------------|
| Table 1 | Related work comparison | Literature (AVAILABLE) + ParBench row needs [PLACEHOLDER] |
| Table 3 | Survey kernel counts | AVAILABLE (model-independent) |
| Table 4 | Kernel x API matrix | AVAILABLE (model-independent) — update for 5 suites |
| Table 5 | Model configurations | NEW — Qwen 3.5 + Gemini 2.5 Flash details |
| Table 7 | Overall pass rates by model | [PLACEHOLDER] — from campaign results |
| Table 8 | Per-kernel result matrix | [PLACEHOLDER] — from campaign results |
| Table 9 | Self-repair statistics | [PLACEHOLDER] — from campaign results |
| Table 10 | Augmentation L0-L4 by model | [PLACEHOLDER] — from campaign results |
| Table 11 | Direction comparison | [PLACEHOLDER] — from campaign results |
| NEW Table | pass@k results | [PLACEHOLDER] — from pass@k sweep |
| NEW Table | Statistical summary (CIs) | [PLACEHOLDER] — from statistical_analysis.py |

### Figures

| Figure | Content | Data Source |
|--------|---------|-------------|
| Figure 1 | System architecture | AVAILABLE (model-independent) |
| Figure 2 | API co-occurrence heatmap (survey) | AVAILABLE (model-independent) |
| Figure 3 | Repo vs kernel comparison (survey) | AVAILABLE (model-independent) |
| Figure 4 | HeCBench selection funnel (survey) | AVAILABLE (model-independent) |
| Figure 5 | Failure taxonomy stacked bar | [PLACEHOLDER] — from campaign results |
| Figure 6 | Kernel-by-model heatmap | [PLACEHOLDER] — from campaign results |
| Figure 7 | Augmentation robustness lines | [PLACEHOLDER] — from campaign results |
| Figure 8 | Cross-direction bar chart | [PLACEHOLDER] — from campaign results |
| NEW Figure | pass@k comparison | [PLACEHOLDER] — from pass@k sweep |

---

## E. Section-Specific Writing Instructions

### For S1 (Intro Writer)

**KEEP:** The four-gap framing (S1.2) is the paper's strongest argumentative structure. The training-data contamination paragraph is excellent and directly motivates augmentation. The ParEval-Repo comparison (0% repo-level vs N% kernel-level) is the headline finding.

**REWRITE:** S1.3 contributions and S1.4 key findings. Structure contributions around the three orthogonal evaluation axes (self-repair, pass@k, augmentation robustness) — this is the novel framing from the decisions log (I1). The old "two-tier capability gap" narrative may or may not apply to new models — use [PLACEHOLDER].

**ADD:** Mention 5-suite scope (Rodinia + XSBench + RSBench + mixbench + HeCBench curated). Mention pass@k as an evaluation dimension.

**DELETE:** All pilot model names and numbers. All specific statistical values from pilot.

**TONE:** Confident but precise. Every claim must be traceable to data. No superlatives.

**LENGTH TARGET:** 2.0 columns (strict — S1 tends to bloat).

### For S2 (Related Work Writer) — CRITICAL

**CRITICAL ADDITIONS (W2, W3, W10):**

1. **LASSI** (Dearing et al., CLUSTER Workshops 2024): Dedicated paragraph in S2.3. Key points:
   - Reports 80% OMP-to-CUDA, 85% CUDA-to-OMP on HeCBench benchmarks
   - Uses agentic self-correction: multi-round with compilation + execution feedback + profiling
   - Uses different models (likely GPT-4)
   - ParBench deliberately measures raw translation competence, not agentic system effectiveness
   - Frame as complementary: LASSI = ceiling (what's possible with tooling), ParBench = floor (what models actually understand)
   - The gap between ParBench's self-repair rate and LASSI's agentic rate quantifies the value of agentic infrastructure

2. **CodeRosetta** (TehraniJamsaz et al., NeurIPS 2024): Paragraph in S2.2. Key points:
   - Encoder-decoder model for C++ <-> CUDA translation
   - AST-aware pretraining
   - Reports BLEU/CodeBLEU scores, NOT build+run+verify correctness
   - Single direction (C++/CUDA), not multi-API
   - Domain-specific model vs ParBench's general-purpose LLM evaluation
   - ParBench's specs could evaluate CodeRosetta-style models (future work)

3. **HPC-Coder-V2** (Chaturvedi et al., arXiv 2024): Brief mention in S2.5.
   - Fine-tuned HPC-specific LLM
   - Demonstrates that HPC-targeted training improves parallel code generation
   - ParBench could serve as evaluation backend for such models

4. **TRACY** (Gong et al., arXiv 2025): Brief mention in S2.2 or S7.5.
   - Execution efficiency benchmarking for LLM code translation
   - Finding: "correctness is not a reliable proxy for efficiency"
   - Motivates future performance evaluation on ParBench

5. **SWE-bench Illusion** (arXiv 2506.12286): Mention in S1.2 or S2.1.
   - Memorization critique of benchmarks with known test data
   - Directly motivates ParBench's augmentation engine
   - ParBench's augmentation is the HPC-specific answer to this concern

6. **Additional papers** from related work research: UniPar, OMPar, OMPGPT, TransCoder-ST, BabelTower — brief mentions where relevant.

**UPDATE Table 1:** Add rows for LASSI, CodeRosetta, HPC-Coder-V2. Update ParBench row for 5-suite, 2-model scope.

**KEEP:** Three-granularity landscape framing (ParEval -> ParEval-Repo -> ParBench). ParaCodex paragraph.

**DELETE:** Nothing — S2 only grows.

**LENGTH TARGET:** 2.5 columns. If over, compress the less-critical papers (UniPar, OMPar, etc.) into a single "Other work" paragraph.

### For S3+S4 (Framework Writer)

**S3 is the most stable section.** The framework description is model-independent and well-written.

**KEEP:** All four subsections (3.A-3.D). The BFS JSON example. Table 2 augmentation levels. The six-transform descriptions. Figure 1 architecture diagram.

**UPDATE in S3:**
- S3.A: "184 specs" -> actual count with 5 suites
- S3.C: "54/60 Rodinia" -> "64+ non-KNOWN_FAIL specs across 5 suites"
- S3.D: Add pass@k mode description. Update provider list (Together AI, Google AI). Remove old model names.

**UPDATE in S4:**
- Add RSBench, mixbench, HeCBench curated to 4.A and 4.B
- Update Table 4 (Kernel x API matrix) for 5 suites
- Update "57 verified-PASS specs" to ~88

**TONE:** Technical and precise. This is the engineering contribution — show the design decisions.

**LENGTH TARGET:** S3 = 3.0 columns, S4 = 1.5 columns.

### For S5 (Setup Writer)

**REWRITE ALMOST ENTIRELY.** S5 is the most affected by the campaign change.

**S5.A Models:** New content needed:
- Qwen 3.5 397B-A17B (Together AI): MoE architecture, 397B total / 17B active per token. Large sparse model.
- Gemini 2.5 Flash (Google AI): Dense architecture. Google's latest fast model.
- Rationale: Two non-Anthropic providers, distinct architecture families (MoE vs dense).
- Reviewer defense: "Why not GPT/Claude?" — ParBench is model-agnostic; framework extensibility demonstrated by supporting 5+ providers. Chosen for architectural diversity, not brand recognition.

**S5.B Translation Directions:** Now 8 core directions:
- 6 across CUDA/OMP/OpenCL (all 4 non-HeCBench suites)
- 2 across CUDA/omp_target (HeCBench curated)
- Total L0 pairs: 142 per model

**S5.C Augmentation Protocol:** Largely unchanged. Emphasize L0-L4 across ALL directions (eliminates W8 confound).

**S5.D Metrics:** Add:
- Greedy-decode pass@1 (primary metric, T=0)
- pass@3 (sampling metric, T=0.7, L0 only — addresses W5)
- Self-repair rate (with transition analysis)
- Augmentation robustness (per-model Cochran-Armitage)
- Wilson 95% CIs on all rates

**S5.E Hardware:** Mostly unchanged. Add Erel's machine if applicable.

**LENGTH TARGET:** 2.0 columns.

### For S6+S7 (Results Writer)

**ALL NUMBERS ARE [PLACEHOLDER].** Write the prose structure with analysis templates.

**S6 Structure (keep this order):**
1. Overall pass rates (Table 7) — headline numbers
2. Failure taxonomy (Figure 5) — BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL
3. Per-kernel analysis (Table 8, Figure 6) — difficulty tiers
4. Self-repair effectiveness (Table 9) — with transition analysis
5. Augmentation robustness (Table 10, Figure 7) — PER-MODEL curves (critical)
6. Cross-direction & extended suite (Table 11, Figure 8)
7. pass@k analysis (NEW — Table, Figure)
8. Statistical summary (NEW — CIs, tests)

**S6.5 Augmentation — REFRAME:** The finding is NOT "level-invariance" (which was an artifact of Simpson's Paradox in the pilot). The finding is "augmentation robustness discriminates model capability." Per-model curves are mandatory. If one model is stable and the other degrades, that's the headline. If both degrade, that's a different (but still interesting) finding.

**S6.7 pass@k — WRITE NEW:** Compare pass@1 (greedy, T=0) vs pass@3 (T=0.7). Identify hard failures (pass@3=0) vs noisy failures (pass@3>0 but pass@1=0). The gap quantifies sampling variance.

**S7 Structure:**
1. Kernel-centric advantage (keep — model-independent argument)
2. BUILD_FAIL as bottleneck (keep — qualitative argument likely holds)
3. Model capability analysis (rewrite — MoE vs dense discussion)
4. Direction asymmetry (keep structure — update numbers)
5. Threats to validity (update — 2-model defense, cite TRACY for W9, mention algorithmic memorization for W11)
6. Augmentation robustness interpretation (rewrite — per-model)
7. Implications (update — LASSI comparison framing I2, agentic gap quantification)

**LENGTH TARGET:** S6 = 4.5 columns, S7 = 2.5 columns.

### For S8 (Conclusion — part of Intro Writer task)

**REWRITE with [PLACEHOLDER].** Four contributions, each with one headline number. Future work: more models, performance timing, agentic evaluation (ParaCodex), deeper augmentation, community extension.

**DELETE:** "HeCBench evaluation" from future work (now done). "Add GPT-4.1" (no longer relevant).

**LENGTH TARGET:** 1.0 column (strict).

---

## F. Writing Sequence and Dependencies

### Phase 1: Model-Independent Sections (can start NOW)

These sections do not depend on campaign results:

| Section | Writer | Priority | Depends On |
|---------|--------|----------|------------|
| S2 Related Work | Related Work Writer | P0 | Research notes (AVAILABLE) |
| S3 Framework | Framework Writer | P1 | Draft (AVAILABLE) |
| S4 Benchmark Curation | Framework Writer | P1 | Draft + 5-suite specs (AVAILABLE) |

### Phase 2: Setup + Structure (can start NOW with [PLACEHOLDER])

| Section | Writer | Priority | Depends On |
|---------|--------|----------|------------|
| S5 Experimental Setup | Setup Writer | P0 | Decisions log D1-D7 (AVAILABLE) |
| S6 Results (structure only) | Results Writer | P1 | Section structure (this roadmap) |
| S7 Discussion (structure only) | Results Writer | P1 | Section structure (this roadmap) |

### Phase 3: Data-Dependent Sections (after campaign results)

| Section | Writer | Priority | Depends On |
|---------|--------|----------|------------|
| S6 Results (fill numbers) | Results Writer | P0 | Campaign results + analyze_eval.py + statistical_analysis.py |
| S7 Discussion (fill numbers) | Results Writer | P1 | S6 complete |
| S1 Introduction | Intro Writer | P1 | S6 key numbers known |
| S8 Conclusion | Intro Writer | P2 | S6 + S7 complete |
| Abstract | Intro Writer | P2 (LAST) | All sections complete |

### Phase 4: Review + Polish

| Task | Priority | Depends On |
|------|----------|------------|
| Paper Critic (adversarial review) | P0 | All sections complete |
| LaTeX transfer | P0 (parallel track) | Markdown complete |
| Anonymous repo | P1 | LaTeX draft ready |

---

## G. Critical Decision Gates

These items require user input before proceeding:

1. **IEEE vs ACM template:** The audit report (W6) flags that SC26 uses IEEE IEEEtran, not ACM sigconf. The paper draft header says "ACM sigconf" but the decisions log says "IEEE IEEEtran format." **Assumed IEEE based on latest decisions.** Confirm with SC26 CFP.

2. **3rd model addition:** D1 says "A 3rd model may be added later." If a 3rd model is added, S5, S6, S7, and Abstract all need updates. **Recommendation:** Write for 2 models now; adding a 3rd is additive, not restructuring.

3. **pass@k scope:** D4 specifies pass@3 at L0 only with T=0.7. If pass@k results are not ready by paper writing time, S6.7 can be marked as "future work" and the column budget redistributed. **Recommendation:** Include pass@k if results arrive; omit section if not.

4. **HeCBench results:** The curated 10 kernels are now in the campaign scope (D2). If HeCBench results arrive, S6 gets richer data. If not, the 4 non-HeCBench suites still provide ~114 pairs/model at L0. **Recommendation:** Include whatever arrives; don't block on HeCBench.

---

*This roadmap is the authoritative writing plan for the SC26 paper. All section writers should follow it. Updated as campaign results arrive.*
