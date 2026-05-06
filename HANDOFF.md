# HANDOFF: Anonymize ParBench Artifact for NeurIPS 2026 Submission

**Date:** 2026-05-05
**Deadline:** May 6, 2026 AoE (Anywhere on Earth) — TOMORROW
**Priority:** CRITICAL — this is the only remaining task before submission
**Project root:** `/home/samyak/Desktop/parbench_sam`

---

## What Is This Project?

ParBench is a benchmark for evaluating how well Large Language Models (LLMs) translate parallel code between CUDA, OpenMP, and OpenCL. Think of it as a test suite: you give an LLM some CUDA code and ask it to produce the equivalent OpenMP code, then you compile and run both to check if the translation is correct.

The project is being submitted to the **NeurIPS 2026 Evaluations & Datasets Track** — a peer-reviewed venue for datasets and benchmarks. The paper PDF is already done and submitted. What remains is preparing the **code/data artifact** (the actual repo with specs, code, and results) for anonymous review.

---

## Goal

Make the source repository fully anonymous so it can be mirrored on `anonymous.4open.science` (a platform that creates read-only anonymous mirrors of GitHub repos for double-blind peer review). Reviewers must not be able to identify who wrote this.

**The three deliverables:**
1. A clean anonymous repo URL (no author names, emails, or personal paths anywhere in any file)
2. An updated `croissant.json` with the correct anonymous URL
3. A rebuilt ZIP file (`parbench-artifact-neurips2026.zip`) for OpenReview upload

---

## Skills to Load at Session Start

Before doing ANY work, load these two skills:

```
Invoke Skill: andrej-karpathy-skills:karpathy-guidelines
Invoke Skill: superpowers:test-driven-development
```

**Why these skills:**
- `karpathy-guidelines` — Prevents over-engineering. This task is surgical: find identity leaks, fix them, verify. No refactoring, no new abstractions.
- `test-driven-development` — Each step has a verification command. Run the verification FIRST (it will fail showing the problem), fix it, then verify again (it should pass). This prevents "I think I fixed it" without proof.

---

## What's Already Done (DO NOT REDO)

| Item | Status |
|------|--------|
| Paper PDF (anonymous, no author names) | ✅ Complete |
| README.md content (NeurIPS format, reproduction recipe) | ✅ Complete |
| `croissant.json` created with RAI metadata, validated 4/4 | ✅ Complete |
| `config/paths.json` anonymized to `"."` | ✅ Complete |
| `expected_outputs/` 37 reference files | ✅ Complete |
| `scripts/build_artifact_zip.sh` ZIP builder | ✅ Complete |
| ZIP built at 42MB (under OpenReview 100MB limit) | ✅ Complete |

---

## What's NOT Done — Your Task

### The Problem: 100+ Files Contain Identity Leaks

The repo has the author's name (`samyak`, `jhaveri`) and personal path (`/home/samyak/Desktop/parbench_sam`) scattered across:

- **Python scripts** — docstrings show example commands with absolute paths
- **Result JSONs** — compiler error output captured verbatim includes paths
- **README.md** — references `parbench_sam/` as directory name
- **`.gitignore`** — contains `parbench_sam/downloads/`
- **1 spec JSON** — baseline stdout capture includes machine path
- **Tracked binary files** — screenshots and presentations committed to git

The `anonymous.4open.science` platform only does FILE-LEVEL exclusion (hide entire files/folders). It does NOT edit file contents. So we must fix the source files before mirroring.

### The Second Problem: Old Anonymous URL

`croissant.json` line 44 references a DELETED anonymous repo (`parbench-artifact-EE29`). Must be updated to the new URL after the user creates the new anonymous repo.

---

## Execution Plan — Step by Step

### STEP 1: Verify the Problem (TDD Red Phase)

Run this command to see ALL identity leaks in files that will be visible to reviewers:

```bash
cd /home/samyak/Desktop/parbench_sam
grep -rn "samyak\|jhaveri\|samyaknj\|parbench_sam" \
  --include="*.py" --include="*.json" --include="*.md" \
  --include="*.sh" --include="*.txt" --include="*.jsonl" \
  --exclude-dir=env_parbench --exclude-dir=HeCBench-master \
  --exclude-dir=rodinia --exclude-dir=.git --exclude-dir=.claude \
  --exclude-dir=.planning --exclude-dir=graphify-out \
  --exclude-dir=docs --exclude-dir=meeting_notes \
  --exclude-dir=presentations --exclude-dir=analysis \
  --exclude-dir=scripts/batch --exclude-dir=scripts/archive \
  --exclude-dir=scripts/survey --exclude-dir=scripts/generators \
  --exclude-dir=scripts/baselines --exclude-dir=node_modules \
  --exclude-dir=.vscode --exclude-dir=.ruff_cache \
  --exclude-dir=.pytest_cache --exclude-dir=parbench.egg-info \
  . 2>/dev/null | wc -l
```

**Expected:** A large number (100+). This is your "red" state — proof the problem exists.

---

### STEP 2: Fix All Path-Based Identity Leaks (The Big Sed)

This single command fixes `/home/samyak/...` paths across ALL relevant directories:

```bash
cd /home/samyak/Desktop/parbench_sam

# Fix absolute paths in ALL code/data files that reviewers will see
find specs/ harness/ scripts/evaluation/ scripts/analysis/ scripts/augmentation/ \
     scripts/spec_tools/ c_augmentation/ results/ config/ artifact/ \
     expected_outputs/ tests/ patches/ templates/ schema/ \
     -type f \( -name "*.py" -o -name "*.json" -o -name "*.md" -o -name "*.sh" -o -name "*.txt" \) \
     -exec sed -i \
       's|/home/samyak/Desktop/parbench_sam|.|g;
        s|/home/samyak/Desktop/downloads/HeCBench-master|./HeCBench-master|g;
        s|/home/samyak/Desktop|.|g;
        s|/home/samyak[^"]*|.|g;
        s|samyaknj@uci\.edu|anonymous@example.com|g' {} +

# Fix the two top-level scripts not inside a subdirectory
sed -i 's|/home/samyak/Desktop/parbench_sam|.|g; s|samyaknj@uci\.edu|anonymous@example.com|g' \
  scripts/generate_paper_figures.py scripts/validate_schema.py
```

**What this does:** Replaces every occurrence of the personal absolute path with `.` (current directory — the standard way to reference project root). Also anonymizes the email address.

---

### STEP 3: Fix Name-Based Identity Leaks (parbench_sam → parbench)

The project directory is called `parbench_sam` (contains author's name). References to this name must become `parbench`:

```bash
cd /home/samyak/Desktop/parbench_sam

# README.md — 6 occurrences of parbench_sam
sed -i 's|parbench_sam/|parbench/|g; s|cd parbench_sam|cd parbench|g; s|parbench_sam|parbench|g' README.md

# .gitignore — 1 occurrence
sed -i 's|parbench_sam/downloads/|downloads/|g' .gitignore

# harness/cli.py — help string mentions parbench_sam/
sed -i 's|parbench_sam/|parbench/|g' harness/cli.py

# scripts/validate_schema.py — comment mentions parbench_sam/
sed -i 's|parbench_sam/|parbench/|g' scripts/validate_schema.py
```

---

### STEP 4: Verify the Fix (TDD Green Phase)

Re-run the same grep from Step 1:

```bash
cd /home/samyak/Desktop/parbench_sam
grep -rn "samyak\|jhaveri\|samyaknj\|parbench_sam" \
  --include="*.py" --include="*.json" --include="*.md" \
  --include="*.sh" --include="*.txt" --include="*.jsonl" \
  --exclude-dir=env_parbench --exclude-dir=HeCBench-master \
  --exclude-dir=rodinia --exclude-dir=.git --exclude-dir=.claude \
  --exclude-dir=.planning --exclude-dir=graphify-out \
  --exclude-dir=docs --exclude-dir=meeting_notes \
  --exclude-dir=presentations --exclude-dir=analysis \
  --exclude-dir=scripts/batch --exclude-dir=scripts/archive \
  --exclude-dir=scripts/survey --exclude-dir=scripts/generators \
  --exclude-dir=scripts/baselines --exclude-dir=node_modules \
  --exclude-dir=.vscode --exclude-dir=.ruff_cache \
  --exclude-dir=.pytest_cache --exclude-dir=parbench.egg-info \
  . 2>/dev/null
```

**Expected:** 0 results. If any remain, fix them manually with `sed -i` on the specific file.

**Also verify JSON syntax wasn't broken:**
```bash
find results/ specs/ -name "*.json" -exec python3 -m json.tool {} > /dev/null \; 2>&1 | head -20
```
**Expected:** No output (all valid JSON). If any fail, the sed broke a JSON string — fix manually.

---

### STEP 5: Delete Operational Noise from results/evaluation/

The top level of `results/evaluation/` has 199 batch summary files, 199 markdown reports, 10 logs, and 9 marker files. These are operational artifacts (like build logs), not research data. They also contain identity-leaking paths. Delete them:

```bash
cd /home/samyak/Desktop/parbench_sam
rm -f results/evaluation/batch_*.json results/evaluation/batch_*.md
rm -f results/evaluation/*.log results/evaluation/*.marker
```

**Verification:**
```bash
ls results/evaluation/
```
**Expected output:**
```
azure-gpt-5.3-codex/  azure-gpt-5.4/  together-qwen-3.5-397b-a17b/
```
Only the 3 model subdirectories should remain. These contain the actual per-task evaluation results (2,344 JSONs across 3 models).

---

### STEP 6: Remove Git-Tracked Binary Files

Screenshots and a PowerPoint file are committed to git. They must be untracked:

```bash
cd /home/samyak/Desktop/parbench_sam

# Untrack screenshots (they stay on disk but won't be in the repo)
git rm --cached "Screenshot 2026-05-05 at 2.26.17 PM.png" \
                "Screenshot 2026-05-05 at 3.03.01 PM.png" \
                "Screenshot 2026-05-05 at 8.14.05 PM.png" \
                "Screenshot 2026-05-05 at 8.47.13 PM.png" \
                "Screenshot_2026-05-05_at_2.56.56_PM.png" 2>/dev/null || true

# Untrack the PowerPoint
git rm --cached "presentations/ParaCodex Results.pptx" 2>/dev/null || true

# Untrack any .docx files
git ls-files "*.docx" | xargs -r git rm --cached

# Untrack analysis visualization PNGs (entire analysis/ dir is excluded anyway)
git rm --cached -r analysis/ 2>/dev/null || true
```

**Verification:**
```bash
git ls-files "*.png" "*.pptx" "*.docx" | grep -v "expected_outputs\|docs/paper"
```
**Expected:** Empty output (no tracked binary files outside expected_outputs and docs/paper).

---

### STEP 7: ASK THE USER — Create Anonymous Repo

**STOP HERE.** You cannot proceed without the user creating the anonymous repo and providing the URL.

Tell the user:

> "All identity leaks are fixed. You now need to:
> 1. Delete the existing anonymous repo at anonymous.4open.science/r/parbench_sam-533B/
> 2. Create a new one with these exclusions (copy-paste the block below)
> 3. Tell me the new URL so I can update croissant.json"

**Exclusion list for the user to copy-paste into the anonymous.4open.science UI:**

```
.claude/
.planning/
.git/
.gitmodules
.github/
graphify-out/
meeting_notes/
env_parbench/
HeCBench-master/
rodinia/
xsbench/xsbench-src/
rsbench/rsbench-src/
mixbench/mixbench-src/
docs/
analysis/
raw/
output/
presentations/
node_modules/
.vscode/
.ruff_cache/
.pytest_cache/
parbench.egg-info/
scripts/batch/
scripts/archive/
scripts/survey/
scripts/generators/
scripts/baselines/
scripts/build_artifact_zip.sh
scripts/build_artifact.sh
HANDOFF.md
CLAUDE.md
AGENTS.md
ARTIFACT_REPRODUCE_CHANGES.md
.mcp.json
.claudeignore
.graphifyignore
bp_install.sh
neurips_submission_form.pdf
report_croissant-validation_ParBench Kernel Specifications.md
parbench-artifact-neurips2026.zip
parbench-artifact-v1.tar.gz
parbench-artifact-v2.tar.gz
.codex_review_done
.validation_passed
```

Tell the user to **check "Anonymize repository name"** so the URL doesn't contain `parbench_sam`.

---

### STEP 8: Update croissant.json URL (after user provides new URL)

Once the user gives you the new URL (it will look like `https://anonymous.4open.science/r/parbench-artifact-XXXX/`):

**File: `croissant.json` — line 44:**
```bash
# Replace OLD_URL with the actual new URL (no trailing /README.md)
sed -i 's|https://anonymous.4open.science/r/parbench-artifact-EE29/|https://anonymous.4open.science/r/NEW-URL-HERE/|' croissant.json
```

**File: `scripts/build_artifact_zip.sh` — line 70:**
```bash
sed -i 's|https://anonymous.4open.science/r/parbench-artifact-EE29/|https://anonymous.4open.science/r/NEW-URL-HERE/|' scripts/build_artifact_zip.sh
```

**Verification:**
```bash
grep "anonymous.4open" croissant.json scripts/build_artifact_zip.sh
```
**Expected:** Both lines show the new URL.

---

### STEP 9: Validate Croissant and Rebuild ZIP

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# Validate Croissant metadata
python3 -c "from mlcroissant import Dataset; d = Dataset('croissant.json'); print('VALID')"

# Delete old ZIP and rebuild
rm -f parbench-artifact-neurips2026.zip
bash scripts/build_artifact_zip.sh

# Check ZIP size (must be under 100MB)
ls -lh parbench-artifact-neurips2026.zip
```

**Expected:**
- Croissant prints `VALID`
- ZIP is ~42MB
- ZIP builder passes its internal identity check (it greps for "samyak" and aborts if found)

---

### STEP 10: Commit and Push

```bash
cd /home/samyak/Desktop/parbench_sam
git add -A
git status  # Review — should show many modified files + deleted batch logs + untracked binaries removed
git commit -m "fix(artifact): anonymize all identity leaks for NeurIPS double-blind submission"
```

**For the push:** `git push origin main` is blocked by Bash tool permissions. Tell the user:

> "Please run this in your terminal: `! git push origin main`"

---

### STEP 11: Final Verification Checklist

After the push, the user should verify the anonymous repo in an **incognito browser**:

- [ ] Search all files for "samyak" → 0 results
- [ ] Search all files for "jhaveri" → 0 results
- [ ] Search all files for "parbench_sam" → 0 results
- [ ] `README.md` renders correctly
- [ ] `croissant.json` is present with correct URL
- [ ] `specs/` directory has JSON files
- [ ] `results/evaluation/` shows only 3 model subdirectories
- [ ] No `.pptx`, `.docx`, `.png` screenshots visible
- [ ] No `.claude/`, `docs/`, `meeting_notes/` visible
- [ ] No `HeCBench-master/`, `rodinia/` visible

---

### STEP 12: Complete OpenReview Form (user does manually)

| Field | Value |
|-------|-------|
| Dataset Submission | ✅ Check the box |
| Croissant File | Upload `croissant.json` |
| Dataset URL | `https://anonymous.4open.science/r/<NEW-URL>/` |
| Code URL | Same URL (no `/README.md` suffix) |
| Supplementary Material | Upload `parbench-artifact-neurips2026.zip` |
| Other LLM Usage | "Artifact preparation and compliance verification" |

---

## What Worked (from previous sessions)

- `mlcroissant` Python library validates identically to the HuggingFace online checker
- The `scripts/build_artifact_zip.sh` has its own sed-based identity scrubber — it's a safety net for the ZIP even if source files have minor leaks
- `artifact/reproduce.sh` generates all 37 expected output files correctly
- anonymous.4open.science strips git commit authorship metadata (no author name/email leak from commits)

## What Didn't Work / Traps to Avoid

- **anonymous.4open.science blocks WebFetch (403)** — you CANNOT verify the anonymous repo programmatically. Must use a real browser.
- **`zip -r` updates existing archives** — always `rm -f` the old ZIP before rebuilding, or stale files persist inside.
- **Result JSONs are "immutable" per project rules** — but we ARE modifying path strings in error snippets. This is a justified exception: we're not changing evaluation outcomes, just anonymizing paths in compiler error output. Do not feel guilty about this.
- **The sed regex `/home/samyak[^"]*` stops at a quote** — this is intentional to avoid breaking JSON string boundaries. Don't change it to a greedy match.
- **Platform glob support is uncertain** — the exclusion list may not support `*.pptx` patterns. That's why Step 6 untracks binaries from git directly (belt AND suspenders).
- **Don't commit the URL until you have the actual URL** — Steps 7-8 are ordered this way on purpose. Committing a speculative URL wastes a commit cycle.

## Key Files Reference

| File | What It Is | What You Do With It |
|------|-----------|-------------------|
| `croissant.json` | NeurIPS-required dataset metadata | Update URL (line 44) |
| `scripts/build_artifact_zip.sh` | Builds the supplementary ZIP | Update URL (line 70), then run it |
| `README.md` | What reviewers see first | Fix `parbench_sam` → `parbench` |
| `.gitignore` | Git ignore rules | Fix `parbench_sam/downloads/` → `downloads/` |
| `harness/cli.py` | CLI entry point | Fix help string (line 228) |
| `scripts/validate_schema.py` | Schema checker | Fix comment (line 33) |
| `results/evaluation/batch_*.json` | Batch operational logs | DELETE these |
| `results/evaluation/batch_*.md` | Batch markdown reports | DELETE these |
| `results/evaluation/*.log` | Run logs | DELETE these |
| `results/evaluation/*.marker` | Done markers | DELETE these |
| `parbench-artifact-neurips2026.zip` | OpenReview upload (42MB) | Rebuild after URL fix |

## What Reviewers Will See (Final Anonymous Repo Structure)

```
parbench/                        ← anonymized repo name
├── README.md                    ← NeurIPS-formatted, reproduction recipe
├── LICENSE                      ← MIT
├── croissant.json               ← NeurIPS-required metadata
├── manifest.jsonl               ← 206-kernel registry
├── pyproject.toml               ← Python package metadata
├── requirements.txt             ← Dependencies
├── requirements-lock.txt        ← Pinned dependencies
├── Dockerfile                   ← Container reproduction
├── .gitignore
├── config/paths.json            ← Anonymized machine config (".")
├── specs/                       ← THE DATASET: 206 JSON kernel specs
├── schema/                      ← JSON schema for validating specs
├── harness/                     ← Build → Run → Verify pipeline
├── scripts/
│   ├── evaluation/              ← LLM evaluation pipeline (4 scripts)
│   ├── analysis/                ← Analysis + figure generation (12 scripts)
│   ├── augmentation/            ← Code augmentation pipeline
│   ├── spec_tools/              ← Spec utilities
│   ├── generate_paper_figures.py
│   └── validate_schema.py
├── c_augmentation/              ← AST transform engine (libclang)
├── results/
│   ├── evaluation/
│   │   ├── azure-gpt-5.4/      ← 822 per-task result JSONs
│   │   ├── azure-gpt-5.3-codex/← 814 per-task result JSONs
│   │   └── together-qwen-3.5-397b-a17b/  ← 708 per-task result JSONs
│   ├── analysis/                ← Pre-computed analysis outputs
│   └── augmentation/            ← Augmentation verification results
├── artifact/                    ← reproduce.sh + Dockerfile + README
├── expected_outputs/            ← 37 reference files for reproduction
├── tests/                       ← Test suite
├── patches/                     ← Rodinia build patches
├── templates/                   ← Spec template
├── xsbench/INDEX.md
├── rsbench/INDEX.md
└── mixbench/INDEX.md
```

---

## Fallback Plan (if anonymous.4open.science is down)

1. Submit the ZIP to OpenReview as supplementary material (this always works)
2. Add a note in the "Code URL" field: "Anonymous repository URL to be provided within 24 hours"
3. Create a Zenodo deposit as alternative hosting
4. Once platform is back, create the anonymous repo and email the URL to the program chairs
