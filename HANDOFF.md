# HANDOFF: Create RESULTS.md for Anonymous Branch

**Date:** 2026-05-06
**Priority:** HIGH — reviewers currently have no top-level results summary
**Project root:** `/home/samyak/Desktop/parbench_sam`

---

## Goal

Create `RESULTS.md` at the project root so NeurIPS reviewers landing on the anonymous GitHub can immediately see evaluation results. Link it at the top of `README.md`. Cherry-pick to the `anonymous` branch.

Every number must be read from existing data files (listed below). Do not copy numbers from memory or documentation.

---

## What's Done (DO NOT REDO)

- Brainstorming, plan-reviewer critique (18 concerns fixed), CLI flag verification, branch comparison — all done
- Data is current (verified 2026-05-06 — `expected_outputs/` matches `eval_summary.json`)
- No data regeneration needed

---

## Skills to Load

1. `andrej-karpathy-skills:karpathy-guidelines` — before code changes
2. `/validate` — before commit

---

## Data Sources (all paths relative to project root)

| Source | Path | What it has |
|--------|------|-------------|
| T1 | `expected_outputs/t1_overall_pass.tex` | Per-model pass rates with Wilson 95% CIs |
| T2 | `expected_outputs/t2_model_comparison.tex` | Per-model per-direction (L0, s0, 6 standard dirs) |
| T3 | `expected_outputs/t3_passk.tex` | pass@k, always-pass/noisy/hard-fail |
| T4 | `expected_outputs/t4_augmentation.tex` | L0-L4 augmentation robustness |
| T5 | `expected_outputs/t5_stats.tex` | McNemar, Cohen's h, odds ratios |
| JSON | `results/evaluation/eval_summary.json` | Failure taxonomy, by_direction (aggregate), by_complexity, total_tasks |
| MD | `results/evaluation/eval_summary.md` | Per-kernel heatmap (cuda→omp, L0) |

**Denominator warning:** T1 = full corpus (Qwen 626, GPT 822, Codex 814). T2 = L0 + sample_id=0 + 6 dirs only (Qwen 138, GPT 120, Codex 120). Always footnote which slice a table uses.

---

## 4 Steps

### Step 1: Create RESULTS.md

**File:** `/home/samyak/Desktop/parbench_sam/RESULTS.md`

Read each source file above and convert LaTeX tables to markdown.

**Core sections (always visible):**

1. **Title + Intro** — "ParBench — Evaluation Results". State: 5 suites, 206 specs, 4 APIs, 3 models. Read `total_tasks` from `eval_summary.json`.
2. **Overall Pass Rates** — Convert `t1_overall_pass.tex` to markdown. Include Wilson CIs.
3. **Per-Direction Pass Rates** — Convert `t2_model_comparison.tex` to markdown. Footnote: "L0 canonical (first sample, 6 standard directions). Totals differ from Table 1."
4. **Failure Taxonomy** — From `eval_summary.json > failure_taxonomy`. Compute each as % of total failures.
5. **Key Findings** — 5 bullets, each number extracted from data:
   - BUILD_FAIL dominance → `eval_summary.json > failure_taxonomy`
   - Direction asymmetry → `eval_summary.json > by_direction` (cuda-to-omp vs opencl-to-cuda)
   - GPT-5.4 ≈ Codex → `t5_stats.tex`
   - Augmentation robust → `t4_augmentation.tex`
   - Systematic failures → `t3_passk.tex` hard-fail counts
6. **Reproduction** — Docker one-liner + link to `artifact/README.md`

**Deep-dive (single collapsible `<details>` block):**

7. **Detailed Analysis** containing:
   - pass@k table (from `t3_passk.tex`)
   - Augmentation robustness table (from `t4_augmentation.tex`)
   - Statistical tests table (from `t5_stats.tex`)
   - Translation complexity (from `eval_summary.json > by_complexity`)
   - Per-kernel heatmap (from `eval_summary.md` kernel matrix)

**Verification:**
```bash
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    data = json.load(f)
print('Total tasks:', data['total_tasks'])
for m, s in data['by_model'].items():
    print(f'{m}: {s[\"pass\"]}/{s[\"total\"]} = {s[\"rate\"]:.1%}')
print('BUILD_FAIL:', data['failure_taxonomy']['BUILD_FAIL'])
"
# Grep RESULTS.md for these numbers — they must match
```

### Step 2: Edit README.md

**File:** `/home/samyak/Desktop/parbench_sam/README.md`

Insert after line 1 (H1 title), before line 3 (description):

```markdown

> **[Evaluation Results](RESULTS.md)** — Full results for three LLMs across 2,262 parallel code translation tasks, including pass rates, direction analysis, failure taxonomy, and per-kernel breakdowns.

```

Verify: `head -5 README.md` — title, blank, blockquote, blank, description.

### Step 3: Identity Leak Check + Commit

All must return empty:
```bash
grep -iE '(samyak|jhaveri|gal|erel|niranjan|erkap|university|institution)' RESULTS.md
grep -E '@' RESULTS.md
grep -E '/home/samyak|/Users/samyakjhaveri|parbench_sam' RESULTS.md
grep -E 'github\.com/' RESULTS.md
```

Run `/validate`, then commit:
```bash
git add RESULTS.md README.md
git commit -m "docs: add RESULTS.md with full evaluation summary for reviewer access"
```

### Step 4: Cherry-Pick to Anonymous

```bash
git checkout anonymous
git cherry-pick <hash>
# If conflicts: abort, create both files manually on anonymous, commit directly
grep -iE '(samyak|jhaveri|gal|erel|niranjan|erkap)' RESULTS.md  # must be empty
git checkout main
```

Ask user to push: `! git push origin main` and `! git push origin anonymous`

---

## Traps to Avoid

- **`analyze_eval.py --output-dir`** does NOT exist — use `--out-json`/`--out-md` if needed
- **Don't mix denominators** — T1 (full corpus) vs T2 (L0-s0-6dir) have different totals
- **`eval_summary.json > by_direction`** is aggregate across ALL models — per-model breakdown is ONLY in `t2_model_comparison.tex`
- **Wilson CIs** are ONLY in `t1_overall_pass.tex`, not in the JSON
- **Don't `git push origin main`** — blocked. User runs `! git push origin main`

---

## Detailed Plan

Full section-by-section instructions at:
**`.claude/plans/lets-think-about-the-magical-popcorn.md`**

---

## Other Tasks (SEPARATE)

Citation audit details in `docs/paper/NeurIPS_ready_version/CITATION_AUDIT.md`. Do NOT combine with this task.
