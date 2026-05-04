# HANDOFF: Replace "ablation" → "augmentation" Terminology

**Date:** 2026-05-04
**Status:** Research complete. Ready for execution.
**Supersedes:** Previous figure-unification handoff (that task may or may not be complete — check git log).

---

## What This Task Is About (Plain English)

ParBench is a benchmark for testing whether AI models can translate parallel code (CUDA ↔ OpenMP ↔ OpenCL). We wrote a NeurIPS 2026 paper about it.

**The terminology problem:** The paper and scripts use the word "ablation" to label the L1-L4 augmentation experiments. In ML, "ablation" means "removing components to test their contribution." In our paper, it's being used as shorthand for "the experiment phase where augmented source code (L1-L4) is tested." This confuses readers — Niranjan (co-author) flagged it: *"can we just call it augmentations? 426 L0 + 200 augmentations makes more sense than calling it ablation."*

**What needs to happen:** Replace every occurrence of "ablation" with either "augmentation" (for the experiment/data) or "L0-conditional filter" (for the filtering mechanism). The word "ablation" should not appear anywhere in the published paper or analysis scripts.

**Important:** Nobody has done this yet. Erel's recent changes to the paper were content rewrites for clarity — NOT ablation→augmentation replacements. No broken find-replace to fix.

---

## Skills to Load First

Before doing ANY work, invoke these skills:

1. **`andrej-karpathy-skills:karpathy-guidelines`** — Think before coding. Simplicity first. Surgical changes. Goal-driven execution.
2. **`superpowers:test-driven-development`** — For each file change: write a grep "test" showing current state → apply change → verify new state. Gated checkpoints.

---

## Critical Context

### Project Root
```
/home/samyak/Desktop/parbench_sam
```

### Paper Directory (NRV/)
```
/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/
```

### How to Compile the Paper
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
pdflatex -interaction=nonstopmode main_neurips.tex
```

### How to Activate Python Env
```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
```

### How to Undo Everything
```bash
cd /home/samyak/Desktop/parbench_sam && git checkout -- docs/paper/ scripts/ results/analysis/
```

---

## The Replacement Rules

There are exactly TWO patterns to replace:

| Current text | Replacement | Reason |
|---|---|---|
| "ablation" meaning the L1-L4 experiment phase or records | "augmentation" or "augmentation campaign" | The experiment applies augmentations, so call it that |
| "ablation filter" or "L0-conditional ablation filter" | "L0-conditional filter" | The filter is self-explanatory without "ablation" |

**DO NOT** blindly find-replace. Some occurrences need "augmentation", others need "augmentation campaign", and the filter references just drop "ablation." Each file section below specifies the exact replacement.

---

## STEP 1: Paper — `sections/experimental-setup.tex`

**File:** `docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex`

### 1A: Comments (3 changes)

| Line | Current text | New text |
|------|---|---|
| 22 | `% §4.4 Canonical Evaluation and Augmentation Ablation` | `% §4.4 Canonical Evaluation and Augmentation Campaign` |
| 24 | `%   - Then: augmentation ablation design — L0-conditional filter` | `%   - Then: augmentation campaign design — L0-conditional filter` |
| 39 | `%   Ablation filter:   pass@1-of-any (memory: project_neurips_experiment_design.md)` | `%   L0-conditional filter:   pass@1-of-any (memory: project_neurips_experiment_design.md)` |

### 1B: Body text (1 change)

| Line | Current text | New text |
|------|---|---|
| 83 | `The augmentation applies an L0-conditional filter, retaining` | `The augmentation campaign applies an L0-conditional filter, retaining` |

### Verification after Step 1:
```bash
grep -ni "ablation" docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex
# Expected: zero results
```

---

## STEP 2: Paper — `appendices_neurips.tex`

**File:** `docs/paper/NeurIPS_ready_version/appendices_neurips.tex`

### 2A: Table caption (line 1364)

**Current:**
```
These 12 kernels were selected by the L0-conditional ablation filter ($\geq$1 of 3 L0 samples passes)
```
**New:**
```
These 12 kernels were selected by the L0-conditional filter ($\geq$1 of 3 L0 samples passes)
```

### 2B: Running text (line 1380) — THREE replacements in one paragraph

**Replacement 1:** `because the ablation filter selects kernels` → `because the L0-conditional filter selects kernels`

**Replacement 2:** `the survivorship selection inherent in L0-conditional ablation` → `the survivorship selection inherent in L0-conditional filtering`

(Note: There are exactly 2 occurrences of "ablation" on this line. Both change.)

### 2C: Evaluation card text (line 1879)

**Current:** `in the ablation only if $\geq$1 of its L0 samples passes`
**New:** `in the augmentation campaign only if $\geq$1 of its L0 samples passes`

### 2D: Source comments (lines 2220, 2269, 2318)

| Line | Current | New |
|------|---|---|
| 2220 | `(426 L0 + 200 ablation, KNOWN_FAIL excluded)` | `(426 L0 + 200 augmentation, KNOWN_FAIL excluded)` |
| 2269 | `(426 L0 + 396 ablation, KNOWN_FAIL pre-excluded)` | `(426 L0 + 396 augmentation, KNOWN_FAIL pre-excluded)` |
| 2318 | `(426 L0 + 388 ablation, KNOWN_FAIL pre-excluded)` | `(426 L0 + 388 augmentation, KNOWN_FAIL pre-excluded)` |

### 2E: Evaluation card checklist item (line 2401)

**Current:** `and the L0-conditional ablation design`
**New:** `and the L0-conditional augmentation design`

### Verification after Step 2:
```bash
grep -ni "ablation" docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Expected: zero results

# Also verify paper still compiles:
cd docs/paper/NeurIPS_ready_version && pdflatex -interaction=nonstopmode main_neurips.tex
# Expected: no errors (warnings are OK)
```

---

## STEP 3: Scripts — `scripts/analysis/build_error_taxonomy.py`

**File:** `scripts/analysis/build_error_taxonomy.py`

This is the biggest script change. There are **18 occurrences** across lines 996-1100.

### Exact replacements (use find-replace carefully):

| Old | New | Type |
|---|---|---|
| `ablation_results` | `augmentation_results` | variable name (4 occurrences) |
| `ablation_taxonomy` | `augmentation_taxonomy` | variable name (3 occurrences) |
| `ablation_by_level` | `augmentation_by_level` | variable name AND dict key (4 occurrences) |
| `abl_pass_rate` | `aug_pass_rate` | variable name (2 occurrences) |
| `"ablation_pass_rate"` | `"augmentation_pass_rate"` | JSON output key (1 occurrence) |
| `"ablation"` (as JSON key, line 1099) | `"augmentation"` | JSON output key (2 occurrences: line 996 check + line 1099 assignment) |
| `Ablation (L1-L4)` | `Augmentation (L1-L4)` | print string (1 occurrence) |
| `Classifying ablation failures` | `Classifying augmentation failures` | print string (1 occurrence) |
| `Ablation runs only on tasks` | `Augmentation runs only on tasks` | print string (1 occurrence) |
| `# Partition into canonical (L0) and ablation (L1-L4)` | `# Partition into canonical (L0) and augmentation (L1-L4)` | comment (1 occurrence) |
| `# Per-level ablation breakdowns` | `# Per-level augmentation breakdowns` | comment (1 occurrence) |
| `- Ablation pass rate:` | `- Augmentation pass rate:` | f-string (1 occurrence, line 1037) |

**IMPORTANT:** Line 996 has a conditional: `if "canonical" in taxonomy and "ablation" in taxonomy:` — this reads from the JSON file it previously wrote. Since we're changing the output key from "ablation" to "augmentation", this line must become: `if "canonical" in taxonomy and "augmentation" in taxonomy:`

Similarly line 1016: `abl = taxonomy["ablation"]` → `abl = taxonomy["augmentation"]` (or better: rename the local var to `aug = taxonomy["augmentation"]`)

And line 1022: `if "ablation_by_level" in taxonomy:` → `if "augmentation_by_level" in taxonomy:`
Line 1026: `taxonomy["ablation_by_level"].get(lvl, {})` → `taxonomy["augmentation_by_level"].get(lvl, {})`

### Verification after Step 3:
```bash
grep -n "ablation" scripts/analysis/build_error_taxonomy.py
# Expected: zero results
```

---

## STEP 4: Scripts — `scripts/audit_eval_consistency.py`

**File:** `scripts/audit_eval_consistency.py`

**13 occurrences.** This file has BOTH comments AND variable names AND dict keys.

| Line | Old | New |
|------|---|---|
| 9 | `check ablation)` | `check augmentation)` |
| 13 | `1 for ablation)` | `1 for augmentation)` |
| 30 | `ablation_count = 0` | `augmentation_count = 0` |
| 62 | `ablation_count += 1` | `augmentation_count += 1` |
| 127 | `issues["max_retries_ablation"]` | `issues["max_retries_augmentation"]` |
| 128 | `for ablation (expected 1)` | `for augmentation (expected 1)` |
| 173 | `issues["num_samples_ablation"]` | `issues["num_samples_augmentation"]` |
| 174 | `for ablation, got` | `for augmentation, got` |
| 220 | `Ablation (L1-L4): {ablation_count}` | `Augmentation (L1-L4): {augmentation_count}` |
| 236 | `"max_retries_ablation"` (both key + value string) | `"max_retries_augmentation"` + `"augmentation"` in value |
| 243 | `"num_samples_ablation"` (both key + value string) | `"num_samples_augmentation"` + `"augmentation"` in value |
| 252 | `"max_retries_ablation"` | `"max_retries_augmentation"` |
| 256 | `"num_samples_ablation"` | `"num_samples_augmentation"` |

### Verification:
```bash
grep -n "ablation" scripts/audit_eval_consistency.py
# Expected: zero results
```

---

## STEP 5: Scripts — `scripts/analysis/augmentation_analysis.py`

**File:** `scripts/analysis/augmentation_analysis.py`

**5 occurrences** (docstrings and comments):

| Line | Old | New |
|------|---|---|
| 7 | `canonical+ablation corpus` | `canonical+augmentation corpus` |
| 168 | `matching ablation filter` | `matching L0-conditional filter` |
| 204 | `ablation files are not seeded` | `augmentation files are not seeded` |
| 813 | `canonical+ablation corpus` | `canonical+augmentation corpus` |
| 885 | `all ablation directions` | `all augmentation directions` |

### Verification:
```bash
grep -n "ablation" scripts/analysis/augmentation_analysis.py
# Expected: zero results
```

---

## STEP 6: Scripts — Remaining files (comments/docstrings only)

### `scripts/analysis/generate_paper_data.py` (1 occurrence)
- **Line 868:** `ablation L1-L4 are different augmentation` → `L1-L4 records use augmented source variants`

### `scripts/analysis/quantitative_findings.py` (3 occurrences)
- **Line 4:** `canonical+ablation corpus` → `canonical+augmentation corpus`
- **Line 984:** `# ablation L1-L4 are different augmentation levels` → `# L1-L4 are different augmentation levels`
- **Line 3349:** `canonical+ablation corpus` → `canonical+augmentation corpus`

### `scripts/analysis/cross_model_comparison.py` (2 occurrences)
- **Line 4:** `canonical+ablation corpus` → `canonical+augmentation corpus`
- **Line 256:** `canonical+ablation corpus` → `canonical+augmentation corpus`

### `scripts/evaluation/analyze_eval.py` (1 occurrence)
- **Line 350:** `conditional ablation — \`derive_l0_passers.py\`` → `L0-conditional filter — \`derive_l0_passers.py\``

### Verification:
```bash
grep -rn "ablation" scripts/ --include="*.py" | grep -v "test_"
# Expected: zero results (test files handled in Step 7)
```

---

## STEP 7: Test Files (CRITICAL — these assert on the old JSON keys)

**If you change production code without updating these tests, they will FAIL.**

### `scripts/analysis/test_build_error_taxonomy.py` (6 occurrences)

| Line | Old | New |
|------|---|---|
| 265 | `canonical/ablation split` | `canonical/augmentation split` |
| 286 | `def test_taxonomy_canonical_ablation_split():` | `def test_taxonomy_canonical_augmentation_split():` |
| 287 | `canonical and ablation sections` | `canonical and augmentation sections` |
| 295 | `assert "ablation" in data, "Missing ablation section"` | `assert "augmentation" in data, "Missing augmentation section"` |
| 297 | `data["ablation"]["total_results"]` | `data["augmentation"]["total_results"]` |
| 304 | `Canonical should have more results than ablation` | `Canonical should have more results than augmentation` |

### `scripts/analysis/test_augmentation_analysis.py` (6 occurrences)

| Line | Old | New |
|------|---|---|
| 140 | `L2 (ablation) against raw data` | `L2 (augmentation) against raw data` |
| 152 | `# L2 ablation check (only kernels with ablation data)` | `# L2 augmentation check (only kernels with augmentation data)` |
| 268 | `L1-L4 for ablation kernels` | `L1-L4 for augmentation kernels` |
| 275 | `# Kernels with ablation data must have L1-L4` | `# Kernels with augmentation data must have L1-L4` |
| 280 | `(ablation data expected)` | `(augmentation data expected)` |

### `scripts/analysis/test_quantitative_findings.py` (5 occurrences)

| Line | Old | New |
|------|---|---|
| 462 | `def test_pass_at_k_excludes_ablation_levels():` | `def test_pass_at_k_excludes_augmentation_levels():` |
| 463 | `augment_level>0 records (ablation, not seeds)` | `augment_level>0 records (augmentation, not seeds)` |
| 472 | `# Task 1: 4 ablation records` | `# Task 1: 4 augmentation records` |
| 491 | `# Only 2 tasks (ablation records excluded` | `# Only 2 tasks (augmentation records excluded` |
| 494 | `# Chen formula (ablation excluded` | `# Chen formula (augmentation excluded` |

### Verification:
```bash
grep -rn "ablation" scripts/ --include="*.py"
# Expected: zero results TOTAL

# Run tests to confirm nothing broke:
cd /home/samyak/Desktop/parbench_sam
python3 -m pytest scripts/analysis/test_build_error_taxonomy.py -v
python3 -m pytest scripts/analysis/test_augmentation_analysis.py -v
python3 -m pytest scripts/analysis/test_quantitative_findings.py -v
```

---

## STEP 8: Regenerate Analysis JSON

The file `results/analysis/error_taxonomy.json` contains keys `"ablation"`, `"ablation_by_level"`, and `"ablation_pass_rate"` from a previous run of `build_error_taxonomy.py`. After Step 3's changes, regenerate:

```bash
source env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
python3 scripts/analysis/build_error_taxonomy.py --project-root .
```

### Verification:
```bash
grep "ablation" results/analysis/error_taxonomy.json
# Expected: zero results

# Confirm the new keys exist:
grep "augmentation" results/analysis/error_taxonomy.json | head -5
# Expected: "augmentation": {, "augmentation_by_level": {, "augmentation_pass_rate":
```

---

## STEP 9: Final Sweep

```bash
# Paper sweep:
grep -rni "ablation" docs/paper/NeurIPS_ready_version/ --include="*.tex"
# Expected: zero

# Scripts sweep:
grep -rni "ablation" scripts/ --include="*.py"
# Expected: zero

# Analysis output sweep:
grep -rni "ablation" results/analysis/
# Expected: zero

# Paper compiles cleanly:
cd docs/paper/NeurIPS_ready_version && pdflatex -interaction=nonstopmode main_neurips.tex
# Expected: no errors

# All tests pass:
cd /home/samyak/Desktop/parbench_sam
python3 -m pytest scripts/analysis/test_build_error_taxonomy.py scripts/analysis/test_augmentation_analysis.py scripts/analysis/test_quantitative_findings.py -v
# Expected: all PASS
```

---

## Execution Order (Strict)

1. Steps 1-2: Paper .tex files (independent of each other)
2. Steps 3-6: Production Python scripts (3 depends on nothing; 4-6 independent of each other)
3. Step 7: Test files (MUST be done after or simultaneously with Steps 3-6)
4. Step 8: Regenerate JSON (MUST be after Step 3)
5. Step 9: Final verification (MUST be last)

**Parallelization opportunity:** Steps 1+2 can run in parallel with Steps 3-7. Step 8 depends on Step 3 only.

---

## What NOT to Change (Explicitly Out of Scope)

| Location | Why |
|---|---|
| `.planning/` directory (145 occurrences) | Internal planning docs, not published |
| `CLAUDE.md`, `.claude/rules/known-issues.md` | Internal project docs |
| `results/evaluation/**/*.json` | These use `augment_level` (already correct) |
| `harness/` code | Doesn't use "ablation" anywhere |
| `c_augmentation/` code | Doesn't use "ablation" anywhere |
| `visualizations/` | Zero occurrences (verified) |

---

## What Worked in This Research Session

- **Full grep sweep found 10 Python files** (not the 4 originally planned) — the critical catch was 3 test files that assert on `"ablation"` JSON keys
- **Verified Erel's changes are NOT relevant** — diffs show content rewrites, not terminology fixes
- **Confirmed `results.tex:71` table caption is already correct** — says "426 L0 + 200 augmentation"
- **Confirmed zero occurrences in visualizations/** — no JS/HTML/CSS changes needed

## What Didn't Work / Traps to Avoid

- **Don't just `sed -i 's/ablation/augmentation/g'`** — some places need "augmentation campaign", some need "L0-conditional filter", some need "augmentation" alone. Each replacement is specified above.
- **Don't change production scripts without updating test assertions** — `test_build_error_taxonomy.py:295` literally asserts `"ablation" in data`. If you change the script but not the test, pytest will fail.
- **Don't regenerate JSON before changing the script** — Step 8 depends on Step 3.
- **Line numbers may drift slightly** — if the previous HANDOFF's figure changes were applied, line numbers in `appendices_neurips.tex` may have shifted. Use the TEXT ANCHORS (quoted strings) to locate each change, not just line numbers.

---

## Summary Statistics

| Category | Count | Effort |
|---|---|---|
| Paper .tex changes | 12 replacements across 2 files | ~15 min |
| Production script changes | ~45 replacements across 7 files | ~30 min |
| Test file changes | ~17 replacements across 3 files | ~15 min |
| JSON regeneration | 1 script run | ~2 min |
| Verification | grep + compile + pytest | ~5 min |
| **Total** | **~74 replacements** | **~60-90 min** |
