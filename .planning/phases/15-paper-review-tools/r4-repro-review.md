# R4-REPRO: Reproducibility Review — ParBench SC26 Paper

**Reviewer:** R4-REPRO (Reproducibility & Open-Science Specialist)
**Date:** 2026-04-06
**Paper:** ParBench: A Build-Run-Verify Benchmark for LLM-Based Parallel Code Translation

---

## 1. Summary

ParBench demonstrates strong reproducibility intent: version-pinned benchmark sources, a requirements-lock.txt for exact Python environment reproduction, deterministic evaluation (temperature=0), and a machine-readable spec format that encodes the full build-run-verify recipe per kernel. However, several gaps remain that would prevent an independent researcher from fully replicating the results without contacting the authors: HeCBench lacks a true commit pin (the spec records "archive-download" instead of a git hash), API costs and evaluation wall-clock time are not reported in the paper text, and the GPT-4.1 mini evaluation environment is entirely unspecified. The repository URL is withheld for double-blind review, which blocks artifact evaluation until de-anonymization.

## 2. Verdict

**Minor Revision** — The framework design is strongly reproducibility-oriented, but the paper text under-reports several items that reviewers and replicators would need. Most gaps are addressable with text additions and one metadata fix (HeCBench commit).

---

## 3. Findings Table

| # | Item | Verdict | Details |
|---|------|---------|---------|
| 1 | **Hardware Specification** | PASS | GPU (RTX 4070 12GB), CPU (Ryzen 9 7900X), OS (Ubuntu 24.04, kernel 6.8.0-40-generic) all specified in S5.5 and Appendix Table 5. Source comments confirm verification against `nvidia-smi`, `lscpu`, `lsb_release`. NVIDIA driver version is not explicitly stated (only HPC SDK 24.3 / CUDA 12.3) -- a minor omission but the toolkit version is sufficient for compiler reproducibility. |
| 2 | **Software Environment** | MINOR | Python 3.12.3, GCC 12.4, nvcc (CUDA 12.3 via HPC SDK 24.3) are stated. `requirements-lock.txt` pins 30+ packages with exact versions (dated 2026-03-27), which is excellent. However, the paper text does not mention `requirements-lock.txt` or `libclang==18.1.1` -- a reader must discover these in the repo. The `together-ai` SDK is not listed in requirements (the `openai` SDK is used for Together AI access), which could confuse a replicator expecting a dedicated client. **Recommendation:** Add one sentence in S5.5 or a footnote pointing to `requirements-lock.txt` for exact dependency reproduction. |
| 3 | **Model Access** | MINOR | Qwen 3.5 397B-A17B: accessed via Together AI API, model weights stated as "publicly available" (line 657). The paper does not specify the Together AI model ID string (e.g., `together-qwen-3.5-397b-a17b`), the API endpoint URL, or whether the model version could change over time. GPT-4.1 mini: accessed via Azure OpenAI, but no Azure deployment details or model version snapshot. **Key concern:** API-served models can be silently updated. Without a model version hash or API snapshot date range, exact replication may be impossible if the provider updates the model. The paper mentions "March--April 2026" as the access window (line 657), which is helpful but not precise. |
| 4 | **Benchmark Source Pinning** | MAJOR | **Rodinia:** Properly commit-pinned at `9c10d3ea` as a git submodule -- excellent. **XSBench:** Commit `ba08e522` recorded in spec provenance -- good. **RSBench:** Commit `34b64478` recorded in spec provenance -- good. **mixbench:** Commit `32edeca9` recorded in spec provenance -- good. **HeCBench: PROBLEMATIC.** The paper states commit `22785cd` (line 657), but the spec JSON files record `"commit": "archive-download"` instead of an actual git hash. This means the spec metadata does not match the paper claim, and a replicator using only the specs cannot verify which HeCBench version to use. Furthermore, HeCBench is gitignored (not a submodule), so `git clone` of the ParBench repo will not include it. The paper does not document how to obtain the correct HeCBench snapshot. **Recommendation:** (a) Update all 25 HeCBench spec JSONs to record the actual commit hash `22785cd`. (b) Add a setup instruction for cloning HeCBench at the pinned commit. (c) Consider making HeCBench a git submodule or providing a download script. |
| 5 | **Spec Completeness** | PASS | Inspected 5 specs (rodinia-bfs-cuda, rodinia-hotspot-omp, rodinia-srad-omp, xsbench-xsbench-cuda, hecbench-nn-cuda). All contain: `build.commands.build`, `run.executable`, `run.default_arguments`, `verification.strategies` (stdout_pattern + exit_code conjunction), `baseline_results` with recorded stdout, `files.translation_targets`, `provenance` with repo URL and commit. The schema is thorough and self-documenting. The `input_configurations.correctness` block provides exact run arguments and input file paths. This is among the most complete benchmark spec formats I have reviewed. |
| 6 | **Harness Usability** | PASS | The paper shows the exact command: `python3 -m harness verify specs/rodinia-bfs-cuda.json` (implied from README and S5). The CLI (`harness/cli.py`) supports `build`, `run`, `verify`, `prompt`, `info`, `pairs` subcommands. The README provides a quick-start section with 4 numbered steps. A researcher could plausibly run the harness from the paper's description + README alone. One caveat: `--project-root` is required for some commands but not documented consistently in the paper text. |
| 7 | **Eval Pipeline Docs** | MINOR | The paper shows the campaign invocation command (lines 634-639) with `--suite`, `--direction`, `--models`, `--project-root`, `--resume` flags. This is a good start. However, the full pipeline (prompt construction -> API call -> code extraction -> file backup -> build -> run -> verify -> restore) is described architecturally in S3 but not as a step-by-step reproduction recipe. Missing from paper text: (a) How to set up API keys (environment variables? config file?). (b) The `--max-retries 3` flag for the self-repair protocol (mentioned as "up to 3 self-repair attempts" but not shown in the command). (c) How to run the pass@k experiment (temperature=0.7, num_samples=3, max_retries=1). The README and `run_eval_batch.py --help` likely fill these gaps, but the paper should be self-sufficient for an SC reviewer. |
| 8 | **Data Availability** | PASS | Line 657: "All 1,248 per-task result JSONs, analysis scripts, and spec files are included in the repository." Verified on disk: result JSONs exist in `results/evaluation/`, analysis scripts in `results/analysis/` and `scripts/analysis/`, spec files in `specs/`. The `results/analysis/paper_data.json` file serves as the single source of truth for all paper claims, with source comments in the LaTeX cross-referencing it. The data verification table in the handoff document confirms all 17 key claims match the data files. |
| 9 | **Open-Source Claims** | MINOR | The paper withholds the repository URL for double-blind review (line 657: "Repository URL withheld for double-blind review"). The actual repo is at `github.com/SamyakJhaveri/parbench_sam` and appears to be public. **However:** (a) No LICENSE file exists at the project root -- only `rodinia/LICENSE` (NCSA/Illinois, which covers Rodinia sources, not ParBench itself). The README mentions "Citation guidance will be added" but says nothing about the project license. (b) The paper does not state under what license ParBench is released. For ACM artifact evaluation, an explicit open-source license (MIT, Apache-2.0, etc.) at the project root is expected. (c) mixbench uses GPL-2.0 (per spec provenance), which may have implications for the combined distribution. **Recommendation:** Add a LICENSE file for the ParBench framework code and clarify license compatibility in the paper. |
| 10 | **KNOWN_FAIL Transparency** | PASS | The 8 KNOWN_FAIL specs are documented in S4 (lines 462-471) with specific technical reasons for each failure (CUDA 12 texture<> removal, missing OpenGL, runtime crashes). Line 501 states "8 are KNOWN_FAIL." Line 676 confirms they are excluded from evaluation. The per-kernel results table (Section 6) explicitly names the 4 excluded kernels (line 793). The internal `known-issues.md` provides even more granular documentation. This is exemplary transparency for a benchmark paper. |
| 11 | **Augmentation Reproducibility** | PASS | The augmentation engine uses `random.seed(args.seed)` with a fixed seed of 42 (stated in S5.3, line 596). The code in `c_augmentation/augment_dataset.py` confirms: the `AugmentationConfig.seed` field is passed through, and `random.seed(args.seed)` is called at line 1881. The `augment_verify.py` script accepts `--seed` and `--augment_level` flags. The augmentation baseline verification (54/60 Rodinia PASS at all L1-L4 levels, level-invariant) is documented. Transforms are deterministic given the seed. Unit tests exist (`test_transforms.py`, 15 tests). **One concern:** The augmentation depends on `libclang==18.1.1` for AST parsing. Different libclang versions could produce different parse trees, potentially altering transform candidate selection. The `requirements-lock.txt` pins this, but the paper does not mention the dependency. |
| 12 | **Cost and Time** | MAJOR | **API cost:** The `token_analysis.json` file records $145.37 total billing for the Qwen campaign (Together AI, 4,600 requests, 120M total tokens). This is valuable data that does NOT appear anywhere in the paper text. A researcher planning to replicate needs cost estimates before committing API budget. **Evaluation time:** No wall-clock time for the full campaign is reported in the paper. The `token_analysis.json` notes the billing period is "Mar 27 -- Apr 2, 2026" (~6 days), but this conflates campaign duration with calendar time. **Recommendation:** Add a paragraph or appendix table reporting: (a) total API cost per model, (b) approximate campaign wall-clock time, (c) cost per task (the data shows ~$0.13/task average). This is standard practice for LLM evaluation papers and critical for reproducibility budgeting. |

---

## 4. Artifact Assessment

**Would this pass ACM Artifact Evaluation?**

| Badge | Assessment |
|-------|-----------|
| **Artifacts Available** | Likely PASS after de-anonymization, IF a LICENSE file is added and HeCBench acquisition is documented. Currently blocked by double-blind URL suppression. |
| **Artifacts Evaluated — Functional** | Likely PASS. The harness, specs, and evaluation pipeline are well-structured. The `requirements-lock.txt` enables exact environment reproduction. Result JSONs are on disk. |
| **Results Reproduced** | AT RISK. HeCBench "archive-download" commit mismatch, missing cost/time reporting, and API model versioning concerns mean a reviewer might not be able to exactly reproduce the numbers. The deterministic T=0 design helps, but API-served model updates could break exact reproduction. |

**Overall AE recommendation:** Would likely earn "Artifacts Available" and "Artifacts Evaluated -- Functional" but may struggle with "Results Reproduced" without the fixes recommended above.

---

## 5. Strengths

- **Spec format is a reproducibility gold standard.** Each JSON spec encodes the complete build-run-verify recipe: exact build commands, run arguments, verification strategies, baseline stdout, input files, provenance with commit hash. This is more thorough than most benchmark papers provide.
- **requirements-lock.txt with exact pinned versions** (30+ packages, dated, with generation metadata) enables exact Python environment reproduction.
- **Temperature=0 deterministic evaluation** eliminates sampling variance for the primary campaign, making results reproducible given the same model version.
- **Append-only manifest and immutable result JSONs** prevent accidental data corruption.
- **Source comments in LaTeX** cross-reference every claim to its data file and field, enabling mechanical verification (e.g., `% src: paper_data.json > overall: 272/710=38.3%`).
- **Augmentation seed=42 with deterministic transforms** and a verified level-invariant baseline.
- **KNOWN_FAIL documentation** is among the most transparent I have seen -- each failure has a specific technical root cause, not just "excluded."
- **1,248 per-task result JSONs included in the repository** with full attempt history.

---

## 6. Weaknesses

- **[MAJOR] HeCBench version pinning is broken in specs.** The 25 HeCBench spec JSONs record `"commit": "archive-download"` instead of the actual commit hash `22785cd` stated in the paper. A replicator using spec metadata alone cannot determine which HeCBench version to use. HeCBench is also gitignored (not a submodule), with no documented acquisition procedure.
- **[MAJOR] API costs and evaluation time are unreported in paper text.** The data exists ($145.37 for Qwen, ~$0.13/task) but is buried in `token_analysis.json`. SC reviewers and replicators need this information to budget a reproduction attempt.
- **[MINOR] GPT-4.1 mini environment is entirely unspecified.** Table 5 shows `\pending{}` for all GPT-4.1 mini hardware/software fields. While the data is marked as pending, the paper should not be submitted with blank environment columns -- either complete the data or remove the GPT-4.1 mini column and present it as future work.
- **[MINOR] No project-level LICENSE file.** Only `rodinia/LICENSE` exists. For artifact evaluation, the ParBench framework code needs its own license.
- **[MINOR] Model version durability.** API-served models (Together AI, Azure OpenAI) can be silently updated. The paper notes the access window ("March--April 2026") but does not discuss model versioning risks or mitigation.
- **[MINOR] Paper text does not reference `requirements-lock.txt`.** The excellent dependency pinning is invisible to a reader who only has the paper.
- **[MINOR] pass@k experiment invocation is not documented.** The paper describes the design (T=0.7, k=3, no self-repair) but does not show how to invoke it.

---

## 7. Questions for Authors

1. **HeCBench commit:** The paper states commit `22785cd` but spec JSONs record `"archive-download"`. Which is correct? Can you update the spec metadata to record the actual commit hash?

2. **HeCBench acquisition:** How should a replicator obtain the correct HeCBench snapshot? Is there a download script, or should they clone and checkout the specific commit?

3. **API costs:** The token_analysis.json records $145.37 for the Qwen campaign. Why is this not reported in the paper? Can you add a cost table (per-model, per-direction, per-task average)?

4. **Evaluation wall-clock time:** How long did the Qwen campaign take end-to-end? This helps replicators plan compute time and API rate limits.

5. **Model versioning:** If Together AI updates Qwen 3.5 397B weights after April 2026, results may not reproduce. Have you considered downloading a snapshot of the model weights (which you note are publicly available) and reporting a model hash?

6. **License:** Under what license will ParBench be released? The rodinia/ submodule has NCSA/Illinois, XSBench and RSBench are MIT, mixbench is GPL-2.0, HeCBench is MIT. What license covers the ParBench framework code itself?

7. **libclang dependency:** The augmentation engine depends on `libclang==18.1.1`. Different libclang versions may produce different AST parse trees. Is this version sensitivity documented or tested?

8. **pass@k command:** What is the exact command to reproduce the pass@k experiment? The `--num-samples` and `--temperature` flags are not shown in the paper.

---

## 8. Recommendations

### Must-fix before submission (MAJOR)

1. **Fix HeCBench spec metadata.** Update all 25 `hecbench-*.json` spec files to record `"commit": "22785cdd7"` (or the full hash) instead of `"archive-download"`. Add a setup instruction in the README for cloning HeCBench at the pinned commit.

2. **Add cost and time reporting.** Add a paragraph in S5 or an appendix table with: (a) total API cost ($145.37 for Qwen via Together AI), (b) campaign duration (~6 days, March 27 -- April 2), (c) average cost per task (~$0.13), (d) total tokens consumed (120M). This data already exists in `token_analysis.json` -- it just needs to be surfaced in the paper.

### Should-fix (MINOR)

3. **Add a LICENSE file** at the project root for the ParBench framework code (MIT or Apache-2.0 recommended given the mixed upstream licenses).

4. **Reference `requirements-lock.txt`** in S5.5: "Exact dependency versions are provided in `requirements-lock.txt` for reproducible environment setup."

5. **Complete or remove GPT-4.1 mini environment columns** in Table 5 before submission.

6. **Add a one-paragraph "Reproduction Guide"** in S5 or an appendix: (a) clone repo, (b) install dependencies from lock file, (c) clone/checkout benchmark suites at pinned commits, (d) set API keys, (e) run campaign command. The README covers most of this but the paper should be self-sufficient.

7. **Document pass@k invocation.** Show the exact `run_eval_batch.py` command for the pass@k experiment (temperature, num_samples, max_retries flags).

8. **Acknowledge model versioning risk** in the threats to validity: API-served models may be updated, and exact reproduction requires the same model version.

### Nice-to-have

9. **Provide a `Makefile` or `reproduce.sh` script** that chains the full pipeline: environment setup -> benchmark acquisition -> augmentation baseline verification -> campaign execution. This is increasingly expected for "Results Reproduced" artifact badges.

10. **Consider archiving a HeCBench snapshot** (e.g., as a release asset or Zenodo archive) since it is gitignored and not a submodule.
