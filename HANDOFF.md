# HANDOFF: NeurIPS 2026 E&D Track — Artifact Compliance Fixes

**Date:** 2026-05-05
**Status:** Fully planned, Codex-reviewed, ready for implementation.
**Deadline:** May 6, 2026 AoE (Abstract due May 4 — already past; full paper + artifact due May 6)
**Priority:** CRITICAL — submission deadline is tomorrow.

**Previous handoff (Architecture Diagram Fixes):** The prior HANDOFF.md content about Figure 1 drawio edits is in git history. Check `git show HEAD:HANDOFF.md` if you need it. That task is independent of this one.

---

## What This Is About (Plain English)

You're submitting a paper + code artifact to NeurIPS 2026's "Evaluations & Datasets" track. Think of it like submitting a homework assignment that has strict formatting rules — if you break them, the teacher won't even read your paper (that's called "desk rejection").

We audited the artifact against NeurIPS's rules and found **6 problems in the README**, **1 missing file**, **1 paper sentence to update**, and **several anonymization leaks**. None are hard to fix, but ALL must be fixed before upload.

**The big picture:** NeurIPS uses "double-blind" review — reviewers don't know who wrote the paper. If your GitHub username (`samyakjhaveri`) appears anywhere in the artifact, you've blown your cover. That's an instant desk rejection.

---

## What Was Found (The Audit)

We compared the artifact (hosted at `anonymous.4open.science/r/parbench-artifact-EE29/`) against the official NeurIPS 2026 E&D track requirements. Here's what's wrong:

### CRITICAL (desk rejection risk)

| # | Problem | Where | Fix |
|---|---------|-------|-----|
| 1 | **GitHub Pages links expose your identity** | README.md `## Visualizations` section | Remove entire section |
| 2 | **config/paths.json has `/home/samyak/...`** | `config/paths.json` lines 2-4 | Replace with relative `"."` |

### HIGH (reviewer will notice, may downgrade)

| # | Problem | Where | Fix |
|---|---------|-------|-----|
| 3 | **Citation says "SC26" (wrong venue)** | README.md bottom | Change to "NeurIPS 2026 (Evaluations & Datasets Track)" |
| 4 | **No reproduction instructions in README** | README.md | Add tiered recipe pointing to `artifact/reproduce.sh` |
| 5 | **Result data not described** | README.md | Add paragraph explaining `results/evaluation/` |
| 6 | **No hardware requirements stated** | README.md | Add what GPU you need (and don't need for Tier 2) |
| 7 | **No Croissant metadata file** | Project root | Create minimal `croissant.json` (conditional — see below) |

### MEDIUM (good practice)

| # | Problem | Where | Fix |
|---|---------|-------|-----|
| 8 | **Paper says "Croissant not applicable"** | `appendices_neurips.tex` line ~2232 | Update to reference new Croissant file (or strengthen opt-out) |
| 9 | **No artifact ZIP for OpenReview upload** | — | Build sanitized ZIP ≤100MB |
| 10 | **Numbers may be inconsistent** | README vs paper vs artifact/README | Verify 206/96/87/9/2344/2262 match everywhere |

---

## What You Need to Know Before Starting

### The Artifact Structure

```
parbench_sam/
├── README.md                  ← THE FILE WITH MOST PROBLEMS (public-facing on anonymous site)
├── artifact/
│   ├── README.md              ← This one is GOOD (detailed reproduction docs)
│   ├── reproduce.sh           ← Already works (5-step pipeline, tested)
│   └── Dockerfile             ← Already works (containerized reproduction)
├── config/paths.json          ← LEAKS YOUR IDENTITY (has /home/samyak/...)
├── results/evaluation/        ← 97MB of result JSONs (2,344 files)
├── specs/                     ← 206 kernel spec JSONs
├── docs/paper/NeurIPS_ready_version/
│   └── appendices_neurips.tex ← Paper appendix (Croissant claim on line ~2232)
└── croissant.json             ← DOESN'T EXIST YET (you'll create it)
```

### Key NeurIPS Rules You Must Not Violate

1. **Double-blind:** No author names, usernames, emails, or personal URLs anywhere reviewers can see
2. **Code release required:** ParBench is a benchmark tool, so code MUST be provided
3. **Supplementary ZIP ≤ 100MB:** If uploading to OpenReview directly (the anonymous URL is also fine)
4. **Croissant metadata:** Required for datasets, BUT the FAQ says "If your submission does not introduce new data, data-hosting guidelines do not apply." ParBench is an eval tool using existing public benchmarks — so it's arguably exempt. We're providing a Croissant anyway as belt-and-suspenders.

---

## The Plan (12 Tasks, Ordered by Dependencies)

### Phase A: README Content Fixes (Tasks 1-5, independent, do in any order)

---

#### Task 1: Remove Visualizations Section

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

**What to do:** Find the `## Visualizations` section (it has ~10 lines with `samyakjhaveri.github.io` links) and delete the entire section including the heading.

**Why:** Those URLs contain your GitHub username → breaks double-blind → desk rejection.

**Verify:**
```bash
grep -n "samyakjhaveri\|github.io" README.md
# Expected: NO output (zero matches)
```

---

#### Task 2: Fix Citation Section

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

**What to do:** Find the `## Citation` section at the very bottom. Replace:
```
ParBench is being prepared for submission to SC26 (International Conference for High
Performance Computing, Networking, Storage, and Analysis). Citation guidance will be
added once the paper is published. <!-- VERIFY: SC26 submission status and citation details -->
```

With:
```
ParBench is under review at NeurIPS 2026 (Evaluations & Datasets Track). Citation
guidance will be added upon publication.
```

**Why:** Wrong venue name + leftover comment.

**Verify:**
```bash
grep -n "SC26\|VERIFY" README.md
# Expected: NO output
```

---

#### Task 3: Add Reproduction Recipe

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

**What to do:** Add a new section `## Reproducing Paper Results` AFTER the existing `## Quick start` section. Insert this content:

```markdown
## Reproducing Paper Results

Results reproduction is tiered by what you want to verify:

### Tier 1: Pipeline Verification (free, ~5 min, no GPU needed)

Confirm the harness and analysis pipeline work on your machine:

\```bash
source env_parbench/bin/activate
python3 scripts/validate_schema.py --all             # Schema validation (expect ~15 known errors from phantom specs)
python3 -m harness info specs/rodinia-bfs-cuda.json  # Inspect a spec
\```

### Tier 2: Reproduce Tables & Figures from Bundled Results (free, ~15 min, no GPU needed)

All 2,344 per-task result JSONs are included in `results/evaluation/`. Regenerate every
table and figure in the paper from these raw results:

\```bash
# Docker (recommended — exact environment):
cd artifact && docker build -t parbench . && docker run --rm -v $(pwd)/../output:/app/output parbench ./reproduce.sh

# Or without Docker:
bash artifact/reproduce.sh
\```

Output lands in `output/` — 5 LaTeX tables (T1–T5) and 15 figures (F2–F7, C.1–C.4).
Deterministic table values can be diffed against `expected_outputs/` for bit-exact verification.
See `artifact/README.md` for full details.

### Tier 3: Full Re-Evaluation (paid, ~8 hours, requires API keys + NVIDIA GPU)

Re-run all 2,262 LLM evaluations from scratch. Requires:
- NVIDIA GPU (CUDA 12.x) for build-run-verify of CUDA/OpenCL specs
- API keys: Together AI (Qwen), Azure OpenAI (GPT-5.4, GPT-5.3-Codex)
- Estimated cost: ~$150–200 in API credits (as of May 2026)

\```bash
# Example: re-run Qwen on CUDA-to-OpenMP direction
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-omp \
  --models together-qwen-3.5-397b-a17b \
  --project-root . --resume -v
\```

See `scripts/evaluation/README.md` and the paper's Appendix J for full campaign details.
```

**Why:** NeurIPS checklist asks "Does the paper provide instructions for reproducing the main experimental results?" Your checklist says Yes, but the README didn't deliver on that promise until now.

**Verify:**
```bash
grep -c "Tier 1\|Tier 2\|Tier 3" README.md
# Expected: 3
```

---

#### Task 4: Add Evaluation Results Section

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

**What to do:** Add a new section `## Evaluation Results` AFTER the reproduction section:

```markdown
## Evaluation Results

Pre-computed evaluation results for all three models are in `results/evaluation/`:

\```
results/evaluation/
├── together-qwen-3.5-397b-a17b/   # 780 result JSONs
├── azure-gpt-5.4/                  # 782 result JSONs
└── azure-gpt-5.3-codex/            # 782 result JSONs
\```

Each JSON file represents one translation task and contains:
- `overall_status`: PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, or EXTRACTION_FAIL
- `translation_code`: The LLM-generated translated source code
- `build_result`, `run_result`, `verification_result`: Per-stage outcomes with stdout/stderr
- `model`, `direction`, `source_spec`, `target_spec`: Task metadata
- `augmentation_level`, `sample_id`: Experiment design coordinates

After KNOWN_FAIL exclusion, 2,262 records are eval-eligible (the denominator for all paper statistics).
```

**Why:** Reviewers who look at `results/` need to know what those JSON files mean.

**Verify:**
```bash
grep -c "overall_status" README.md
# Expected: 1
```

---

#### Task 5: Add Hardware Requirements

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

**What to do:** Find the `## Requirements` section. After the existing bullet about `jsonschema`, add:

```markdown
### Hardware

- **For reproducing paper tables/figures (Tier 2):** Any x86_64 machine, no GPU needed (~4 GB RAM)
- **For running CUDA/OpenCL specs (Tier 3):** NVIDIA GPU (compute capability ≥ 7.0, e.g., RTX 3060+)
- **For OpenMP-only specs:** Any multi-core x86_64 CPU (no GPU required)
- **Tested platform:** NVIDIA RTX 4070, AMD Ryzen 9 7900X, Ubuntu 24.04, NVIDIA HPC SDK 24.3
```

**Why:** Reviewer without GPU needs to know they can still reproduce your tables.

**Verify:**
```bash
grep "RTX 4070" README.md
# Expected: 1 match
```

---

### Phase B: Croissant File (Task 6, has validation gate)

---

#### Task 6: Create Croissant Metadata

**File to create:** `/home/samyak/Desktop/parbench_sam/croissant.json`

**What to do:** Create a minimal Croissant JSON-LD file. Here's a template:

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "cr": "http://mlcommons.org/croissant/",
    "rai": "http://mlcommons.org/croissant/RAI/"
  },
  "@type": "Dataset",
  "name": "ParBench Kernel Specifications",
  "description": "206 JSON specification files defining parallel code translation tasks across CUDA, OpenMP, OpenCL, and OpenMP target offload APIs, sourced from 5 HPC benchmark suites.",
  "license": "https://opensource.org/licenses/MIT",
  "url": "https://anonymous.4open.science/r/parbench-artifact-EE29/",
  "version": "1.0.0",
  "keywords": ["parallel computing", "code translation", "CUDA", "OpenMP", "OpenCL", "benchmark", "LLM evaluation"],
  "datePublished": "2026-05-06",
  "cr:conformsTo": "http://mlcommons.org/croissant/1.0",
  "distribution": [
    {
      "@type": "cr:FileObject",
      "name": "kernel-specs",
      "description": "JSON specification files, one per kernel variant",
      "contentUrl": "specs/",
      "encodingFormat": "application/json"
    },
    {
      "@type": "cr:FileObject",
      "name": "spec-schema",
      "description": "JSON Schema (draft-07) defining the spec file structure",
      "contentUrl": "schema/spec_schema.json",
      "encodingFormat": "application/schema+json"
    }
  ],
  "rai:dataCollection": "Specifications curated from existing open-source HPC benchmark suites (Rodinia, HeCBench, XSBench, RSBench, mixbench). No personal or sensitive data.",
  "rai:dataCollectionType": "Curated from existing sources"
}
```

**CRITICAL VALIDATION GATE:** After creating the file, run:
```bash
pip install mlcroissant
python3 -c "from mlcroissant import Dataset; d = Dataset('croissant.json'); print('VALID')"
```

**Decision point:**
- If it prints `VALID` → keep the file, proceed to Task 7 (success path)
- If it errors → try to fix the error (usually a missing field or wrong structure)
- If you can't fix it in ~15 minutes → DELETE `croissant.json` and use the FALLBACK path in Task 7

**Why this is conditional:** A malformed Croissant file draws MORE reviewer scrutiny than having no file at all. The NeurIPS FAQ explicitly exempts evaluation tools from Croissant requirements. We're only providing one as extra credit — it must not hurt us.

---

### Phase C: Paper Update (Task 7, depends on Task 6 outcome)

---

#### Task 7: Update Paper Appendix I

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex`

**What to do:** Find the line (around line 2232) that says:
```latex
Because \parbench{} is an executable evaluation benchmark rather than a model-training dataset, Croissant metadata is not applicable here.
```

**If Task 6 SUCCEEDED (Croissant validates),** replace with:
```latex
A minimal Croissant metadata file (\texttt{croissant.json}) is provided at the repository root, describing the spec corpus structure for machine-readable discovery. Because \parbench{} is an executable evaluation benchmark rather than a model-training dataset, the full Croissant data-hosting requirements do not apply per the track FAQ; the JSON Schema (draft-07) documentation in \texttt{schema/spec\_schema.json} serves as the primary machine-readable contract.
```

**If Task 6 FAILED (couldn't validate Croissant),** replace with:
```latex
Because \parbench{} is an executable evaluation benchmark rather than a model-training dataset, Croissant data-hosting requirements do not apply per the track FAQ. Machine-readable structure is provided through the JSON Schema (draft-07) definitions in \texttt{schema/spec\_schema.json} and the per-spec provenance fields (repository URL, pinned commit, license), which serve an equivalent discovery and documentation purpose for tool artifacts.
```

**Why:** Either way you're strengthening the justification from a bare assertion to one that cites the FAQ and explains what DOES provide machine-readability.

**Verify:** Compile the paper (`pdflatex` + `bibtex` cycle) and check Appendix I renders.

---

### Phase D: Anonymization & Packaging (Tasks 8-9, depend on Phase A-C being complete)

---

#### Task 8: Full Anonymization Sweep

**What to do:** Run this grep across the entire project:

```bash
cd /home/samyak/Desktop/parbench_sam
grep -rn "samyak\|jhaveri\|samyakjhaveri\|2799@gmail" \
  --include="*.py" --include="*.json" --include="*.md" --include="*.tex" \
  --include="*.toml" --include="*.cfg" --include="*.sh" --include="*.txt" \
  . | grep -v ".git/" | grep -v "env_parbench/" | grep -v "node_modules/" | grep -v ".claude/"
```

**Known hit that MUST be fixed:**
- `config/paths.json` — replace all `/home/samyak/Desktop/parbench_sam` with `"."`

**Fix `config/paths.json`:** Replace its entire content with:
```json
{
    "project_root": ".",
    "downloads_root": ".",
    "hecbench_root": "."
}
```

**Any other hits:** Fix them case-by-case (delete personal info, replace with generic text).

**Also check PDF metadata:**
```bash
cd docs/paper/NeurIPS_ready_version
pdflatex main_neurips && bibtex main_neurips && pdflatex main_neurips && pdflatex main_neurips
pdfinfo main_neurips.pdf | grep -i "author\|creator"
# Author field should be empty or "Anonymous"
```

**Verify:** The grep command returns ZERO lines.

---

#### Task 9: Build Sanitized Artifact ZIP

**What to do:** Create a script `scripts/build_artifact_zip.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
# Build anonymized artifact ZIP for NeurIPS supplementary upload

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR=$(mktemp -d)

echo "Building sanitized artifact in $ARTIFACT_DIR..."

# Copy only artifact-relevant files (no .git, no dev tools, no benchmark sources)
rsync -a \
  --exclude='.git' --exclude='.git*' --exclude='.gitmodules' \
  --exclude='env_parbench/' --exclude='.claude/' --exclude='docs/' \
  --exclude='node_modules/' --exclude='HeCBench-master/' \
  --exclude='rodinia/' --exclude='xsbench-src/' --exclude='rsbench-src/' \
  --exclude='mixbench-src/' --exclude='graphify-out/' --exclude='.planning/' \
  --exclude='*.pyc' --exclude='__pycache__/' \
  --exclude='Screenshot*' --exclude='*.png' \
  --exclude='HANDOFF.md' --exclude='CLAUDE.md' --exclude='AGENTS.md' \
  "$PROJECT_ROOT/" "$ARTIFACT_DIR/parbench-artifact/"

# Sanitize config/paths.json
cat > "$ARTIFACT_DIR/parbench-artifact/config/paths.json" << 'EOF'
{
    "project_root": ".",
    "downloads_root": ".",
    "hecbench_root": "."
}
EOF

# Identity check (MUST pass)
if grep -rn "samyak\|jhaveri" "$ARTIFACT_DIR/parbench-artifact/" \
   --include="*.py" --include="*.json" --include="*.md" \
   --include="*.toml" --include="*.sh" --include="*.txt" \
   --include="*.tex" 2>/dev/null; then
    echo "ERROR: Identity leak found! Aborting."
    rm -rf "$ARTIFACT_DIR"
    exit 1
fi

# Build ZIP
cd "$ARTIFACT_DIR"
zip -r "$PROJECT_ROOT/parbench-artifact-neurips2026.zip" parbench-artifact/
SIZE=$(du -sh "$PROJECT_ROOT/parbench-artifact-neurips2026.zip" | cut -f1)
echo ""
echo "=== Artifact ZIP built: parbench-artifact-neurips2026.zip ($SIZE) ==="

# Size check (OpenReview limit: 100MB)
BYTES=$(stat -c%s "$PROJECT_ROOT/parbench-artifact-neurips2026.zip" 2>/dev/null || stat -f%z "$PROJECT_ROOT/parbench-artifact-neurips2026.zip")
if [ "$BYTES" -gt 104857600 ]; then
    echo "WARNING: ZIP exceeds 100MB!"
    echo "Options:"
    echo "  a) Exclude results/evaluation/ from ZIP, rely on anonymous URL for full data"
    echo "  b) Compress results/ more aggressively (gzip individual JSONs)"
    echo "  c) Upload ZIP with just code + specs, link to anonymous URL for results"
fi

rm -rf "$ARTIFACT_DIR"
```

**If ZIP exceeds 100MB:** The most likely culprit is `results/evaluation/` (97MB). Best option: exclude it from the ZIP and add a note in the ZIP's README saying "Full evaluation results available at the anonymous repository URL." The anonymous.4open.science link provides the complete artifact; the ZIP is just for OpenReview's supplementary upload requirement.

**Verify:**
```bash
bash scripts/build_artifact_zip.sh
# Should complete without "ERROR" and report size < 100MB
```

---

### Phase E: Consistency & Final Checks (Tasks 10-12, run after everything else)

---

#### Task 10: Number Consistency Sweep

**What to do:** Verify these numbers match across all documents:

```bash
cd /home/samyak/Desktop/parbench_sam

# Ground truth (file system counts)
echo "Spec files on disk: $(ls specs/*.json | wc -l)"
echo "Result JSONs on disk: $(find results/evaluation -name '*.json' | wc -l)"
echo "Model dirs: $(ls results/evaluation/)"

# Check each document mentions correct numbers
echo "--- README.md ---"
grep -on "206\|2,344\|2,262\|87\|96" README.md | head -20

echo "--- artifact/README.md ---"
grep -on "206\|2,344\|2,262\|87\|96" artifact/README.md | head -20
```

| Number | What it means | Ground truth |
|--------|---------------|--------------|
| 206 | Total spec JSON files | `ls specs/*.json \| wc -l` |
| 96 | Curated specs (used in paper) | 87 eval-eligible + 9 KNOWN_FAIL |
| 87 | Eval-eligible (non-KNOWN_FAIL) | Paper denominator |
| 9 | KNOWN_FAIL specs | Listed in `known-issues.md` |
| 2,344 | Total result files on disk | `find results/evaluation -name "*.json" \| wc -l` |
| 2,262 | Eval-eligible records (after exclusion) | Paper statistics denominator |

**If any number doesn't match between README, artifact/README, and the paper — fix it.** The file system count is always the ground truth.

---

#### Task 11: Re-push to anonymous.4open.science

**MUST BE THE VERY LAST THING YOU DO.** Only after Tasks 1-10 all pass.

**Steps:**
1. Commit all changes locally
2. Push to anonymous.4open.science:
   - If using git: `git push anonymous main` (or whatever the remote is named)
   - If manual upload: use the platform's update mechanism
3. **Cold-start test in incognito browser:**
   - Open `https://anonymous.4open.science/r/parbench-artifact-EE29/`
   - Verify README renders correctly (no GitHub Pages links, correct venue)
   - Click into `config/paths.json` — should show `"."` not `/home/samyak/...`
   - Click into `artifact/README.md` — should render normally
   - Verify NO login is required to browse
   - Check that `.git` internals aren't exposed (the platform should handle this)

---

#### Task 12: Final PDF Metadata Check

**What to do:**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
pdflatex main_neurips && bibtex main_neurips && pdflatex main_neurips && pdflatex main_neurips
pdfinfo main_neurips.pdf | grep -i "author\|creator\|producer\|title"
```

**Check:**
- Author field: should be empty, "Anonymous", or absent
- No acknowledgments section visible in the PDF
- Main content (before References) ≤ 9 pages
- Appendix I (Artifact Availability) reflects your Task 7 changes

---

## Execution Order Diagram

```
Phase A (Tasks 1-5)  ←── Independent, do in any order
       ↓
Phase B (Task 6)     ←── Croissant creation + validation gate
       ↓
Phase C (Task 7)     ←── Depends on Task 6 outcome (two paths)
       ↓
Phase D (Tasks 8-9)  ←��─ Anonymization sweep + ZIP build
       ↓
Phase E (Tasks 10-12) ←── Final checks, push LAST
```

**Total estimated time:** 1-2 hours for a focused session.

---

## What Worked in This Research Session

- Fetched and compared both the artifact README and the full NeurIPS 2026 E&D CFP + FAQ
- Identified that `artifact/` subdirectory already has excellent reproduction infrastructure (`reproduce.sh`, Dockerfile, detailed README) — the top-level README just needs to POINT to it
- Codex adversarial review caught 4 issues the initial audit missed: config/paths.json leak, ZIP size risk, Tier 2 inaccuracy, and the need for a cold-start reviewer simulation
- Confirmed `pyproject.toml` and `LICENSE` are already anonymous ("ParBench Authors", no author field)
- Verified the paper already has `\usepackage[eandd]{neurips_2026}` and the mandatory checklist

## What Didn't Work / Traps to Avoid

- **anonymous.4open.science blocks automated access (403)** — WebFetch can't retrieve content from the anonymous URL. You must verify it manually in a browser.
- **Don't assume `analyze_eval.py` reproduces paper figures** — it's a helper script. The real pipeline is `artifact/reproduce.sh` (5 steps: `generate_paper_data.py` → `quantitative_findings.py` → `statistical_analysis.py` → `cross_model_comparison.py` → `generate_paper_figures.py`)
- **Don't create Croissant without validating** — a malformed file is WORSE than no file. The `mlcroissant` Python package is the official validator. If it fails, use the fallback opt-out path.
- **Don't push to anonymous site before ALL fixes are done** — partial pushes could briefly expose identifying content to anyone monitoring the URL
- **config/paths.json uses absolute paths** — this is gitignored in normal development but WILL be in the artifact if you don't sanitize it. The `config/paths.json.template` with `{{PROJECT_ROOT}}` exists but isn't the file that ships.
- **ZIP may exceed 100MB** — `results/evaluation/` alone is 97MB. If so, exclude results from ZIP and note that full data is at the anonymous URL. OpenReview supplement is for code; the data can live externally.

---

## Skills to Load

No special Claude Code skills needed for this task — it's all file editing + shell commands.

If using Claude Code: just Read/Edit/Write/Bash tools are sufficient.

---

## Quick Decision Reference

| If you encounter... | Do this... |
|---|---|
| Croissant validation fails | Delete `croissant.json`, use fallback text in Task 7 |
| ZIP > 100MB | Exclude `results/evaluation/` from ZIP, add note linking to anonymous URL |
| New identity leak found by grep | Fix it (replace with generic text or delete) |
| PDF shows author in metadata | Add `\pdfinfo{/Author {}}` to LaTeX preamble |
| Number mismatch between documents | Trust the file system count, update the document |
| anonymous.4open.science won't let you push | Try the platform's web upload interface; if blocked, document the issue and submit via OpenReview ZIP only |

---

## Detailed Plan File

The full 12-task plan with exact file paths, text anchors, and verification commands is at:
**`/home/samyak/.claude/plans/check-out-the-https-anonymous-4open-scie-groovy-moler.md`**

That file has the same content as above but in a more structured format suitable for step-by-step execution.
