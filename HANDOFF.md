# HANDOFF: Build Anonymous Executable Artifact for NeurIPS 2026

**Date:** 2026-05-01
**Status:** Ready for execution — all research and design complete, no code changes made yet
**Previous handoff (COMPLETED):** GPT-5.3-codex paper integration (Steps 1-9)

---

## What This Task Is About (Plain English)

ParBench is a benchmark that tests whether AI models can translate parallel code between different GPU/CPU programming languages (CUDA, OpenMP, OpenCL). We have a research paper being submitted to NeurIPS 2026 that reports results from 3 AI models on 2,262 translation tasks.

**Your job:** Build an anonymous, self-contained package (a "tarball") that a paper reviewer can download, run one Docker command, and get all the paper's tables and figures regenerated from the raw data. The reviewer needs no GPU, no API keys, and no special hardware — just Docker on any machine.

**Why this matters:** NeurIPS requires a reproducibility artifact. If a reviewer can't reproduce the numbers, the paper gets rejected.

**The end product:** A file called `parbench-artifact-v1.tar.gz` (~40-60 MB compressed) that gets uploaded to Zenodo (a scientific data hosting service) and linked in the paper via a DOI.

**Scope of "reproduce":** The artifact programmatically regenerates 5 key tables (T1: overall pass, T2: direction rates, T3: pass@k, T4: augmentation rates, T5: statistical tests) and all 11 figures (F2-F7, C.1-C.4) from raw evaluation data. The paper LaTeX source is also bundled so reviewers can trace every number in every table (including hand-written appendix tables) back to its `% src:` JSON annotation.

---

## What's Already Done

1. **Design spec written and reviewed:** `docs/superpowers/specs/2026-05-01-artifact-packaging-design.md`
2. **Detailed plan with adversarial review:** `/home/samyak/.claude/plans/lets-work-on-this-sleepy-platypus.md`
3. **All evaluation data exists:** 2,262 result JSONs across 3 model directories in `results/evaluation/`
4. **Analysis pipeline exists and works:** All scripts in `scripts/analysis/` and `scripts/generate_paper_figures.py`
5. **Existing CPU-only Dockerfile:** At repo root `/home/samyak/Desktop/parbench_sam/Dockerfile`
6. **3 critical blockers + 4 flags identified** via adversarial Claude + Codex cross-model review (see below)

**Nothing has been created yet. All artifact files are new.**

---

## What You Must NOT Do

1. **Never delete or modify result JSONs** in `results/evaluation/` — they are immutable research data
2. **Never modify the existing `Dockerfile`** at repo root — create a new one in `artifact/`
3. **Never skip anonymization checks** — a single leaked path like `/home/samyak/...` could de-anonymize the paper
4. **Never claim binary PNG diffs as a verification** — cross-platform font rendering makes PNGs non-deterministic; verify LaTeX tables (text) and check figure existence + non-zero size
5. **Never bypass validation** — run `/validate` before any commit
6. **Do NOT use GSD commands** (per project convention)

---

## Skills to Invoke (in order)

Before you begin ANY work, invoke these skills using the Skill tool:

| When | Skill Name | How to Invoke | Why |
|------|-----------|---------------|-----|
| Before writing any code | `andrej-karpathy-skills:karpathy-guidelines` | `Skill(skill: "andrej-karpathy-skills:karpathy-guidelines")` | Prevents over-engineering; ensures surgical, minimal changes |
| Before writing `reproduce.sh` and `build_artifact.sh` | `superpowers:test-driven-development` | `Skill(skill: "superpowers:test-driven-development")` | Write tests first; verify each script works before moving on |
| Before claiming any step done | `superpowers:verification-before-completion` | `Skill(skill: "superpowers:verification-before-completion")` | Run the verification commands listed in each step; confirm output matches expectation |
| Before any git commit | `validate` | `Skill(skill: "validate")` | 4-wave validation loop (waves 1-3 required for commit gate) |
| End of session | Run `/codex:rescue review the uncommitted changes` | Type it as a command | Cross-model second opinion (mandatory per project rules) |

---

## Environment Setup (MUST DO FIRST)

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
# Always use python3, never bare python
```

---

## Critical Blockers Found During Plan Review

These are bugs/gaps that the adversarial plan review discovered. They are **already remediated in the step-by-step plan below**, but you need to know WHY certain choices were made.

### BLOCK-1: Missing Python Dependencies

**Problem:** `scienceplots==2.2.1` and `scipy==1.17.1` are installed in the project's virtual environment but are **missing from `requirements-lock.txt`** (the file that Docker uses to install dependencies). Without them, the Docker container will build fine but crash when `reproduce.sh` tries to import `scienceplots` (needed by `scripts/generate_paper_figures.py` line 36) or `scipy.stats` (needed by 4 analysis scripts).

**Fix:** Step 1 adds them to `requirements-lock.txt`.

### BLOCK-2: `generate_paper_data.py` Processes ONE Model at a Time

**Problem:** `scripts/analysis/generate_paper_data.py` takes `--results-dir` pointing to a single model's directory and `--output` for a single JSON. The artifact has 3 models. If `reproduce.sh` only calls it once, it only processes one model and the remaining analysis steps fail.

**Fix:** Step 2b's `reproduce.sh` loops over all 3 model directories.

### BLOCK-3: Hidden Cross-Module Import

**Problem:** `scripts/analysis/statistical_analysis.py` (line 46) does:
```python
from scripts.evaluation.analyze_eval import (_kernel_from_spec, load_results)
```
This means the artifact needs `scripts/evaluation/analyze_eval.py` and `scripts/evaluation/__init__.py`, not just `scripts/analysis/`. If you only copy the analysis directory, `statistical_analysis.py` will crash with `ModuleNotFoundError`.

**Fix:** The Dockerfile and `build_artifact.sh` include `scripts/evaluation/` in the copy list.

### FLAG-1: Path Leaks in Analysis JSONs

**Problem:** Files in `results/analysis/*.json` contain metadata like `"results_dir": "/home/samyak/Desktop/parbench_sam/results/evaluation/azure-gpt-5.3-codex"`. The file `error_taxonomy.json` has **1,024** such path references. If these ship in the artifact, a reviewer could identify the author.

**Fix:** Step 4 runs `sed` to replace all `/home/samyak/Desktop/parbench_sam` with `/app` in the staged copies. A final `grep` check catches any remaining leaks.

### FLAG-2: Binary Figure Diff Won't Work Cross-Platform

**Problem:** The plan originally said "bit-for-bit match" for expected_outputs/. But PNG files rendered by matplotlib differ across platforms (different fonts, library versions, x86 vs ARM). A reviewer on macOS or ARM Linux will get different PNG bytes even with identical data.

**Fix:** Verification diffs LaTeX tables (text, deterministic) and checks figure file existence + non-zero size, not binary PNG comparison.

### BLOCK-4: Only T2 is Programmatically Generated (Codex review B1)

**Problem:** The original task says "reproduce Tables 2-5" but `generate_paper_figures.py` only generates T2 (model comparison table). The paper has 2 main-body tables and ~20 appendix tables, all hand-written LaTeX. An implementer can complete the plan without generating or validating any table beyond T2.

**Fix:** Step 2d adds 4 new table generators to `generate_paper_figures.py`: T1 (overall pass rates), T3 (pass@k), T4 (augmentation rates), T5 (statistical tests summary). All data for these exists in the analysis JSONs.

### BLOCK-5: Verification is Artifact-Against-Itself (Codex review B2)

**Problem:** `expected_outputs/` is generated by running the same `reproduce.sh` that the reviewer runs. There's no check that generated outputs match the tables/figures in the actual submitted paper. A systematic bug could pass artifact validation unchanged.

**Fix:** Bundle the paper LaTeX source (anonymized) in the artifact. Reviewers can trace every `% src:` comment to its JSON. Step 5 verification includes diffing generated T1-T5 LaTeX against the paper's actual table content.

### FLAG-3: Spec Count is 206, Not 207 (Codex review F2)

The repo has 206 spec JSONs in `specs/` (run `ls specs/*.json | wc -l` to confirm). Both earlier docs said 207. Use 206 in README and sanity checks.

### FLAG-4: LICENSE File Missing from Copy List (Codex review F3)

`build_artifact.sh` must copy a LICENSE file. Check if one exists at repo root; if not, create a minimal one (MIT or Apache 2.0 — ask user).

### FLAG-5: ARM/macOS Docker Portability (Codex review F4)

The Quick Start in README must include `--platform linux/amd64` for ARM Mac users. The base image `python:3.12-slim` is multi-arch but matplotlib's font rendering differs per arch.

---

## Step-by-Step Execution Plan

### STEP 1: Fix `requirements-lock.txt` (addresses BLOCK-1)

**File to edit:** `/home/samyak/Desktop/parbench_sam/requirements-lock.txt`

**What to do:** Add these two lines in alphabetical order within the file:
```
scienceplots==2.2.1
scipy==1.17.1
```

**Why these exact versions:** They match what's installed in the working venv (verified via `pip show`). Using different versions could produce different floating-point results in the analysis.

**Verification:**
```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
python3 -c "import scienceplots; print('scienceplots OK')"
python3 -c "from scipy import stats; print('scipy OK')"
grep -E "scienceplots|scipy" /home/samyak/Desktop/parbench_sam/requirements-lock.txt
# Expected: both lines appear
```

---

### STEP 2: Create `artifact/` Directory with 3 Files

**What:** Create a new directory `artifact/` at the project root with 3 files: a Dockerfile, a reproduce script, and a README.

#### 2a: Create `artifact/Dockerfile`

**File:** `/home/samyak/Desktop/parbench_sam/artifact/Dockerfile`

**Based on:** The existing `/home/samyak/Desktop/parbench_sam/Dockerfile` (read it first — 44 lines)

**Key differences from the existing Dockerfile:**
- Add `COPY results/ results/` after line 36 (bundles evaluation data + analysis summaries)
- Add `COPY reproduce.sh .` and `RUN chmod +x reproduce.sh`
- Keep the `pip install -e .` line (it registers the `harness` and `c_augmentation` packages, which analysis scripts import from)
- Keep the `paths.json` generation line (line 38 of existing)
- Change `CMD` to print usage instructions instead of running schema validation

**Why `pip install -e .` matters:** Three analysis scripts import `harness.constants.EXCLUDED_SPECS`:
- `scripts/analysis/quantitative_findings.py` (line 39)
- `scripts/analysis/generate_paper_data.py` (line 30)
- `scripts/analysis/token_analysis.py` (line 32)

Without the editable install, these imports fail with `ModuleNotFoundError`.

#### 2b: Create `artifact/reproduce.sh`

**File:** `/home/samyak/Desktop/parbench_sam/artifact/reproduce.sh`

This is the single command a reviewer runs. It calls 5 scripts in order:

1. `generate_paper_data.py` — called **3 times** (once per model: `together-qwen-3.5-397b-a17b`, `azure-gpt-5.4`, `azure-gpt-5.3-codex`). Each call reads raw result JSONs from one model directory and produces one `paper_data_*.json` summary.

2. `quantitative_findings.py` — called **3 times** (once per model). Each call reads raw results and produces `quantitative_findings_*.json`.

3. `statistical_analysis.py` — called **once**. Reads ALL model results from `results/evaluation/`, runs McNemar tests, Cohen's h, chi-squared. Imports from `scripts.evaluation.analyze_eval` (BLOCK-3).

4. `cross_model_comparison.py` — called **3 times** (one per model pair). Reads `paper_data_*.json` files from step 1.

5. `generate_paper_figures.py` — called **once** with `--figure all`. Reads raw results directly from `results/evaluation/` via `load_eval_results()`. Produces all figures (F2-F7, C.1-C.4) and all 5 tables (T1-T5). T1/T3/T4/T5 are new generators added in Step 2d.

**CRITICAL filename matching issue:** `generate_paper_data.py` step 1 output filenames must match what `cross_model_comparison.py` step 4 expects as `--model-a`/`--model-b` defaults. The defaults in `cross_model_comparison.py` (lines 258-268) are:
- `results/analysis/paper_data_together-qwen-3.5-397b-a17b.json`
- `results/analysis/paper_data_azure_gpt54.json`

The slug transform `tr '.-' '_'` will convert:
- `together-qwen-3.5-397b-a17b` → `together_qwen_3_5_397b_a17b` (WRONG — default expects `together-qwen-3.5-397b-a17b`)
- `azure-gpt-5.4` → `azure_gpt_5_4` (different from default `azure_gpt54`)

**Solution:** Don't use slug transforms. Hard-code the output filenames to match what already exists in `results/analysis/`:
```bash
# Model 1: Qwen
python3 scripts/analysis/generate_paper_data.py \
    --results-dir results/evaluation/together-qwen-3.5-397b-a17b \
    --output results/analysis/paper_data_together-qwen-3.5-397b-a17b.json -v

# Model 2: GPT-5.4
python3 scripts/analysis/generate_paper_data.py \
    --results-dir results/evaluation/azure-gpt-5.4 \
    --output results/analysis/paper_data_azure_gpt54.json -v

# Model 3: Codex
python3 scripts/analysis/generate_paper_data.py \
    --results-dir results/evaluation/azure-gpt-5.3-codex \
    --output results/analysis/paper_data_azure-gpt-5.3-codex.json -v
```

**Verify these filenames match** by running:
```bash
ls results/analysis/paper_data_*.json
# Should show: paper_data_together-qwen-3.5-397b-a17b.json, paper_data_azure_gpt54.json, paper_data_azure-gpt-5.3-codex.json
```

#### 2d: Add Table Generators to `generate_paper_figures.py` (addresses BLOCK-4)

**File to edit:** `/home/samyak/Desktop/parbench_sam/scripts/generate_paper_figures.py`

**What:** Add 4 new table-generation functions (T1, T3, T4, T5) alongside the existing T2 generator (`generate_t2_model_table` at line 1626). Each writes a `.tex` file to the output directory.

**T1: Overall Pass Rates** (`generate_t1_overall_pass`)
- Data source: `quantitative_findings_*.json > canonical > failure_taxonomy > status_counts` for each model
- Output: LaTeX tabular with columns: Model | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | Total | Rate [95% Wilson CI]
- The data loading is already done by `load_eval_results()` — group by model, count statuses, compute Wilson CIs
- Wilson CI formula: already used in `quantitative_findings.py` line ~200 — you can import `scipy.stats.binom` or compute inline

**T3: Pass@k Rates** (`generate_t3_passk`)
- Data source: `paper_data_*.json > passk_campaign > aggregate_passk` for each model
- Output: LaTeX tabular with columns: Model | n tasks | pass@1 | pass@3 | Always-fail | Noisy | Always-pass
- Task classification from: `quantitative_findings_*.json > canonical > pass_at_k > task_classification`

**T4: Augmentation Rates** (`generate_t4_augmentation`)
- Data source: `statistical_analysis.json > augmentation_curves > {model}` for each model
- Output: LaTeX tabular with columns: Model | L0 | L1 | L2 | L3 | L4 | Chi2 p (Bonf)
- Chi-squared p from: `statistical_analysis.json > chi2_augmentation_by_model > {model} > p_corrected_bonferroni`

**T5: Statistical Tests Summary** (`generate_t5_stats`)
- Data source: `statistical_analysis.json > model_comparison > pairwise` for each pair
- Output: LaTeX tabular with columns: Pair | OR [95% CI] | p (Bonferroni) | Cohen's h | Interpretation
- Omnibus row from: `statistical_analysis.json > model_comparison > omnibus`

**Implementation approach:**
1. Read the existing `generate_t2_model_table` function (line 1626-1670) as the pattern to follow
2. Each new function: loads data from analysis JSONs (not raw results), formats as LaTeX `\begin{tabular}...\end{tabular}`, writes to `output_dir / "t{N}_{name}.tex"`
3. Register each in `FIGURE_REGISTRY` dict (line 1679): `"T1": "t1_overall_pass"`, etc.
4. Add T1, T3, T4, T5 to the `EVAL_FIGURES` set (line 1694) since they need eval data loaded
5. Add generation calls in `main()` after the existing T2 block (line 1841)

**How T1-T5 load their data:** T2 loads from raw `records` (the `load_eval_results()` output). For T3-T5, the analysis JSONs are simpler to use. The function should load the JSON files directly from `project_root / "results" / "analysis"` rather than recomputing from raw records. Pattern:
```python
import json
findings_dir = project_root / "results" / "analysis"
# For each model, load quantitative_findings_{model}.json
```

**Verification:**
```bash
source env_parbench/bin/activate
python3 scripts/generate_paper_figures.py \
    --project-root /home/samyak/Desktop/parbench_sam \
    --figure T1 --output-dir /tmp/test-tables -v
# Repeat for T3, T4, T5
ls /tmp/test-tables/t*.tex
# Expected: 4 new .tex files
# Diff against paper content:
grep -A 10 'label{tab:overall-pass}' docs/paper/NeurIPS_ready_version/sections/results.tex
cat /tmp/test-tables/t1_overall_pass.tex
# Numbers should match
```

#### 2c: Create `artifact/README.md`

**File:** `/home/samyak/Desktop/parbench_sam/artifact/README.md`

Structure:
1. **Quick Start** — 4 commands: `tar xf`, `cd`, `docker build -t parbench .`, `docker run --rm -v $(pwd)/output:/app/output parbench ./reproduce.sh`. Include note: **ARM Mac users:** add `--platform linux/amd64` to `docker build` (FLAG-5).
2. **What This Reproduces** — table: Figure/Table ID → Script → Data Source. Include all 5 tables (T1-T5) and 11 figures (F2-F7, C.1-C.4).
3. **Directory Structure** — annotated file tree including `paper/` for traceability
4. **What's Included** — raw eval results (97 MB), analysis scripts, spec JSONs, Docker env, paper LaTeX (for `% src:` traceability)
5. **What's NOT Included** — GPU, API keys, benchmark source trees
6. **Hardware Requirements** — any x86_64 machine with Docker (~4 GB RAM, ~15 min). ARM (Apple Silicon) works with `--platform linux/amd64` but figures may differ slightly due to font rendering.
7. **Verifying Outputs** — diff `.tex` tables (text, deterministic), check `.pdf`/`.png` existence + non-zero size. Also: trace `% src:` comments in `paper/sections/*.tex` to their JSON files in `results/analysis/`.
8. **Table/Figure Registry**:
   - T1 (overall pass rates), T2 (direction rates), T3 (pass@k), T4 (augmentation), T5 (statistical tests)
   - F2 (repo vs kernel), F3 (heatmap), F4 (failure taxonomy), F5 (pass@k), F6 (cross-suite), F7 (augmentation)
   - C.1-C.4 (appendix figures)

**Verification:**
```bash
ls -la /home/samyak/Desktop/parbench_sam/artifact/
# Expected: 3 files (Dockerfile, reproduce.sh, README.md)
```

---

### STEP 3: Create `scripts/build_artifact.sh`

**File:** `/home/samyak/Desktop/parbench_sam/scripts/build_artifact.sh`

**What this script does:** Automates the entire artifact packaging process — copies files, anonymizes paths, builds Docker, generates expected outputs, creates tarball.

**Pseudocode:**
```
1. Parse args (--dry-run flag skips Docker steps)
2. Set STAGING=/tmp/parbench-artifact-staging/parbench-artifact
3. rm -rf $STAGING && mkdir -p $STAGING
4. Copy files (see file list below)
5. Run anonymization (sed + grep check)
6. If not --dry-run:
   a. docker build -t parbench-artifact $STAGING
   b. docker run --rm -v $STAGING/expected_outputs:/app/output parbench-artifact ./reproduce.sh
7. tar czf parbench-artifact-v1.tar.gz -C /tmp/parbench-artifact-staging parbench-artifact
8. Print size and file count
```

**Exact file copy list** (all paths relative to `/home/samyak/Desktop/parbench_sam/`):

| Source | Destination in staging | Notes |
|--------|----------------------|-------|
| `specs/` | `specs/` | All 206 JSONs (2.2 MB) — verify: `ls specs/*.json \| wc -l` |
| `manifest.jsonl` | `manifest.jsonl` | Kernel registry |
| `schema/` | `schema/` | JSON schemas |
| `results/evaluation/together-qwen-3.5-397b-a17b/*.json` | `results/evaluation/together-qwen-3.5-397b-a17b/` | Raw results ONLY (exclude `*.log`, `*.marker`) |
| `results/evaluation/azure-gpt-5.4/*.json` | `results/evaluation/azure-gpt-5.4/` | Same |
| `results/evaluation/azure-gpt-5.3-codex/*.json` | `results/evaluation/azure-gpt-5.3-codex/` | Same |
| `results/analysis/*.json` | `results/analysis/` | Pre-computed summaries (will be regenerated) |
| `scripts/analysis/*.py` | `scripts/analysis/` | Exclude `__pycache__/` |
| `scripts/evaluation/analyze_eval.py` | `scripts/evaluation/analyze_eval.py` | BLOCK-3 dependency |
| `scripts/evaluation/__init__.py` | `scripts/evaluation/__init__.py` | Package init for import |
| `scripts/generate_paper_figures.py` | `scripts/generate_paper_figures.py` | Primary figure/table generator |
| `scripts/validate_schema.py` | `scripts/validate_schema.py` | Optional validation |
| `scripts/__init__.py` | `scripts/__init__.py` | If it exists (check first) |
| `harness/*.py` | `harness/` | All `.py` files (needed for `pip install -e .`) |
| `c_augmentation/*.py` | `c_augmentation/` | All `.py` files (same reason) |
| `config/` | `config/` | Template will be regenerated by Dockerfile |
| `pyproject.toml` | `pyproject.toml` | Package definition |
| `requirements-lock.txt` | `requirements-lock.txt` | Exact pins (with scienceplots + scipy added in Step 1) |
| `artifact/Dockerfile` | `Dockerfile` | Root of staging (not in artifact/ subdir) |
| `artifact/reproduce.sh` | `reproduce.sh` | Root of staging |
| `artifact/README.md` | `README.md` | Root of staging |
| `LICENSE` | `LICENSE` | Check if exists at repo root; if not, create MIT (FLAG-4) |
| `docs/paper/NeurIPS_ready_version/sections/*.tex` | `paper/sections/` | Anonymized paper LaTeX for traceability (BLOCK-5) |
| `docs/paper/NeurIPS_ready_version/appendices_neurips.tex` | `paper/` | Appendix tables with `% src:` annotations |

**Files explicitly EXCLUDED:**
- `.git/` — no commit history (de-anonymization risk)
- `.claude/`, `.planning/` — development artifacts
- `docs/` (EXCEPT `sections/*.tex` and `appendices_neurips.tex` which ARE included for traceability)
- `graphify-out/` — knowledge graph (development tool)
- `env_parbench/` — virtual environment
- `*.log`, `*.marker` — eval campaign logs (may contain timestamps/paths)
- `__pycache__/`, `*.pyc` — Python cache
- `HeCBench-master/`, `rodinia/` — benchmark source trees (licensed separately, ~10 GB)
- `results/augmentation/` — not needed for table reproduction

**Verification:**
```bash
chmod +x /home/samyak/Desktop/parbench_sam/scripts/build_artifact.sh
bash /home/samyak/Desktop/parbench_sam/scripts/build_artifact.sh --dry-run
# Expected: staging directory created, anonymization check passes, no Docker steps
echo "Exit code: $?"  # Must be 0
```

---

### STEP 4: Anonymization Pass (addresses FLAG-1)

**What:** Ensure no author-identifying information leaks into the artifact.

**Known leaks (verified by grep during this session):**

| File(s) | Leak | Count |
|---------|------|-------|
| `results/analysis/paper_data_*.json` (3 files) | `"results_dir": "/home/samyak/..."` | 1 per file |
| `results/analysis/quantitative_findings_*.json` (5 files) | Same | 1 per file |
| `results/analysis/error_taxonomy.json` | Path references in error snippets | 1,024 |
| `results/analysis/benchmark_characterization.json` | Path reference | 1 |
| `scripts/analysis/statistical_analysis.py` line 1087 | `/home/samyak` in argparse epilog example | 1 |
| `pyproject.toml` | Clean — no author fields | 0 |
| `results/evaluation/**/*.json` | Clean — no path leaks | 0 |

**The fix in `build_artifact.sh`:**
```bash
# Replace all absolute paths in analysis JSONs
find "$STAGING/results/analysis/" -name "*.json" -exec \
    sed -i 's|/home/samyak/Desktop/parbench_sam|/app|g' {} +

# Replace path in statistical_analysis.py epilog
sed -i 's|/home/samyak/Desktop/parbench_sam|/app|g' "$STAGING/scripts/analysis/statistical_analysis.py"

# Final check — MUST return zero hits or ABORT
if grep -ri "samyak\|jhaveri\|/home/samyak\|/Users/samyak\|@.*\.edu" "$STAGING/"; then
    echo "FAIL: De-anonymization leak detected. Fix before proceeding."
    exit 1
fi
```

**Verification:**
```bash
# After build_artifact.sh runs, this must return exit code 1 (no matches):
grep -ri "samyak\|jhaveri\|/home/samyak\|/Users/" /tmp/parbench-artifact-staging/
echo "Exit code: $?"  # MUST be 1
```

---

### STEP 5: Build and Test the Full Artifact

**What:** Build the Docker image from the staged artifact, run reproduce.sh, verify all outputs exist.

```bash
cd /tmp/parbench-artifact-staging/parbench-artifact

# Build Docker image
docker build -t parbench-artifact .

# Run reproduce.sh, mount output to host
mkdir -p /tmp/artifact-test-output
docker run --rm -v /tmp/artifact-test-output:/app/output parbench-artifact ./reproduce.sh
```

**What success looks like:**
- Docker build completes without errors (~3-5 min for pip install)
- `reproduce.sh` prints 5 steps with no Python tracebacks
- Output directory contains:
  - T1-T5 table files (`.tex`) — 5 LaTeX tables
  - F2-F7 main body figures (`.pdf` and/or `.png`)
  - C.1-C.4 appendix figures
  - At least 20 output files total

**Verification:**
```bash
# Count output files
echo "Total outputs: $(find /tmp/artifact-test-output -type f | wc -l)"
# Expected: >= 20

# Check all 5 tables exist
for t in t1_overall_pass t2_model_table t3_passk t4_augmentation t5_stats; do
    [ -s "/tmp/artifact-test-output/${t}.tex" ] && echo "OK: ${t}.tex" || echo "FAIL: ${t}.tex missing"
done

# Check key figures exist and are non-empty
for f in /tmp/artifact-test-output/*.pdf /tmp/artifact-test-output/*.png; do
    [ -s "$f" ] && echo "OK: $(basename $f)" || echo "FAIL: $f"
done

# PAPER-ANCHORED VALIDATION (addresses BLOCK-5):
# Diff generated T1 numbers against paper's actual Table 1
echo "--- Paper-anchored check: T1 numbers ---"
# Extract PASS counts from generated T1
grep -o '[0-9]\+ &' /tmp/artifact-test-output/t1_overall_pass.tex | head -6
# Compare against paper's Table 1
grep -A 3 'label{tab:overall-pass}' docs/paper/NeurIPS_ready_version/sections/results.tex | grep '&'
# These MUST show the same numbers (230, 621, 604 for PASS column)
```

---

### STEP 6: Package as Tarball

**What:** Copy verified outputs into `expected_outputs/`, create the final tarball.

```bash
# Copy verified outputs as reference
cp -r /tmp/artifact-test-output /tmp/parbench-artifact-staging/parbench-artifact/expected_outputs

# Create compressed tarball
cd /tmp/parbench-artifact-staging
tar czf /home/samyak/Desktop/parbench_sam/parbench-artifact-v1.tar.gz parbench-artifact

# Report
du -sh /home/samyak/Desktop/parbench_sam/parbench-artifact-v1.tar.gz
tar tzf /home/samyak/Desktop/parbench_sam/parbench-artifact-v1.tar.gz | wc -l
```

**Expected:** ~40-60 MB compressed, ~2500-3000 files.

**Final verification — fresh unpack test:**
```bash
mkdir -p /tmp/artifact-final-test && cd /tmp/artifact-final-test
tar xf /home/samyak/Desktop/parbench_sam/parbench-artifact-v1.tar.gz
cd parbench-artifact
docker build -t parbench-final-test .
docker run --rm -v $(pwd)/test-output:/app/output parbench-final-test ./reproduce.sh

# Diff LaTeX tables (text-based, deterministic)
diff <(find test-output -name "*.tex" -exec cat {} +) \
     <(find expected_outputs -name "*.tex" -exec cat {} +)
echo "Table diff exit code: $?"  # MUST be 0

# Check figure existence (NOT binary diff — see FLAG-2)
for f in expected_outputs/*.pdf expected_outputs/*.png; do
    base=$(basename "$f")
    [ -s "test-output/$base" ] && echo "OK: $base" || echo "FAIL: $base missing"
done
```

---

### STEP 7: Add Zenodo DOI Placeholder to Paper

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex`

**What:** Add a footnote with placeholder Zenodo DOI. The actual DOI gets filled in after upload.

Find a suitable location (Introduction section, near the end of the first paragraph, or a dedicated Reproducibility statement) and add:

```latex
\footnote{Artifact available at \url{https://doi.org/10.5281/zenodo.XXXXXXX}. Includes evaluation data, analysis scripts, and Docker environment to reproduce all tables and figures.}
```

**Overleaf sync:** Per project convention, apply the edit locally AND give the user exact copy-paste text for Overleaf. The user syncs manually.

**Verification:**
```bash
grep -n "zenodo" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex
# Expected: one line with the footnote
```

---

## Import Chain Diagram

This is why certain files must be included. If you see `ModuleNotFoundError`, trace it here:

```
generate_paper_figures.py (the primary output generator)
  └── matplotlib, numpy, scienceplots ← BLOCK-1 fix (add to requirements-lock.txt)
  └── NO project imports (self-contained for figure generation)
  └── load_eval_results() reads results/evaluation/{model}/*.json directly

quantitative_findings.py
  └── harness.constants.EXCLUDED_SPECS ← needs pip install -e . (harness package)
  └── scipy.stats ← BLOCK-1 fix

statistical_analysis.py
  └── scripts.evaluation.analyze_eval._kernel_from_spec ← BLOCK-3 (need analyze_eval.py)
  └── scripts.evaluation.analyze_eval.load_results ← BLOCK-3
  └── harness.constants.EXCLUDED_SPECS ← needs pip install -e .
  └── scipy.stats ← BLOCK-1 fix

generate_paper_data.py
  └── harness.constants.EXCLUDED_SPECS ← needs pip install -e .
  └── scipy.stats ← BLOCK-1 fix

cross_model_comparison.py
  └── scipy.stats ← BLOCK-1 fix
  └── reads paper_data_*.json (output of generate_paper_data.py)
```

---

## File Sizes (for sanity checks)

| Component | Size | In artifact? |
|-----------|------|-------------|
| `results/evaluation/` (3 model dirs, JSON only) | ~97 MB | YES |
| `results/analysis/` | ~1.9 MB | YES |
| `specs/` | ~2.2 MB | YES |
| `scripts/` (relevant subset) | ~3 MB | YES |
| `harness/` + `c_augmentation/` | ~1 MB | YES |
| `expected_outputs/` | ~2 MB | YES (generated in Step 6) |
| **Total uncompressed** | **~107 MB** | |
| **Compressed (.tar.gz)** | **~40-60 MB** | (JSON compresses well) |

Zenodo limit is 50 GB. We're well within it.

---

## What Could Go Wrong

| Risk | Symptom | Fix |
|------|---------|-----|
| Missing `scienceplots` | `ModuleNotFoundError: No module named 'scienceplots'` | Step 1 not applied — check requirements-lock.txt |
| Missing `scipy` | `ModuleNotFoundError: No module named 'scipy'` | Same as above |
| Missing `analyze_eval.py` | `ModuleNotFoundError: No module named 'scripts.evaluation'` | BLOCK-3 — Dockerfile must COPY `scripts/evaluation/` |
| Filename mismatch in `cross_model_comparison.py` | `FileNotFoundError: paper_data_azure_gpt54.json` | Output filenames in reproduce.sh don't match defaults — hard-code them |
| Docker build fails on ARM Mac | `platform mismatch` | Add `--platform linux/amd64` to docker build |
| Path leak in final tarball | `grep samyak` returns hits | Step 4 sed patterns incomplete — add more patterns |
| `reproduce.sh` permission denied | `bash: ./reproduce.sh: Permission denied` | Dockerfile must `RUN chmod +x reproduce.sh` |

---

## Dependencies Between Steps

```
Step 1 (fix requirements-lock.txt) ← Must be first (Docker build depends on it)
    │
Step 2 (create artifact/ files) ← Must be after Step 1 (Dockerfile copies requirements-lock.txt)
    │
Step 3 (create build_artifact.sh) ← Can be parallel with Step 2
    │
Step 4 (anonymization) ← Runs inside build_artifact.sh
    │
Step 5 (build + test) ← After Steps 1-4
    │
Step 6 (tarball) ← After Step 5 succeeds
    │
Step 7 (paper DOI) ← Independent; can be done anytime
```

---

## Summary Checklist

| Step | What It Creates | How to Verify It Worked |
|------|----------------|------------------------|
| 1 | Updated `requirements-lock.txt` | `grep scienceplots requirements-lock.txt` returns a line |
| 2a | `artifact/Dockerfile` | File exists, references `COPY results/` |
| 2b | `artifact/reproduce.sh` | File exists, calls all 5 scripts with correct filenames |
| 2c | `artifact/README.md` | File exists, includes ARM guidance, table registry T1-T5 |
| 2d | T1/T3/T4/T5 generators in `generate_paper_figures.py` | `python3 scripts/generate_paper_figures.py --figure T1 ...` produces `.tex` |
| 3 | `scripts/build_artifact.sh` | `bash scripts/build_artifact.sh --dry-run` exits 0 |
| 4 | Anonymized staging directory | `grep -ri samyak staging/` returns empty (exit 1) |
| 5 | Docker image + reproduced outputs | `reproduce.sh` exits 0; ≥20 output files; T1 numbers match paper |
| 6 | `parbench-artifact-v1.tar.gz` | Fresh unpack + rebuild + run matches expected |
| 7 | Zenodo DOI footnote in paper | `grep zenodo main_neurips.tex` returns a line |

---

## To Start the Fresh Session

```
Open a new Claude Code session, then:
1. Read this file: /home/samyak/Desktop/parbench_sam/HANDOFF.md
2. Invoke skill: andrej-karpathy-skills:karpathy-guidelines
3. Invoke skill: superpowers:test-driven-development
4. Start with Step 1
```
