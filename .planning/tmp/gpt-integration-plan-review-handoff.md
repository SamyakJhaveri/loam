# GPT-4.1 Mini Paper Integration — Multi-Agent Plan Review Handoff

## Quick Start

```
/clear
```

Then paste:

```
Review the plans in /home/samyak/.claude/plans/hashed-sauteeing-kite.md using multi-agent adversarial review. Context and instructions are in .planning/tmp/gpt-integration-plan-review-handoff.md — read that file first, then spawn the review panel as described.
```

---

## What This Is

Three phases (16-18) have been planned for integrating GPT-4.1 mini evaluation results into the SC26 paper. The plans need adversarial review before execution because:

1. **Deadline pressure** (April 8, 2 days away) — no room for rework
2. **Data integrity** — every number in the paper must be verifiable
3. **Argumentation quality** — new LASSI/augmentation arguments must withstand SC-level review
4. **Page budget** — adding ~1-1.5 pages of new content to a ~10 page paper

## Plan Location

**Primary plan:** `/home/samyak/.claude/plans/hashed-sauteeing-kite.md`

## Review Panel Design

Spawn **4 parallel review agents** (use `plan-reviewer` subagent type or general-purpose agents), each with a different adversarial lens:

### Agent 1: Data Integrity Reviewer
**Focus:** Are the numbers correct? Will the analysis pipeline produce accurate results?
- Cross-check the GPT data summary in the plan against actual files at `results/evaluation/azure-gpt-4.1-mini/`
- Verify that `analyze_eval.py` and `generate_paper_data.py` can handle the GPT data without code changes
- Check if KNOWN_FAIL exclusions apply correctly to GPT data (especially HeCBench specs)
- Verify the 5 augmentation degradation examples by reading actual result JSONs
- Check: are the Qwen baseline numbers in the plan still accurate? (compare against `results/analysis/paper_data.json`)

### Agent 2: Paper Structure & Argumentation Reviewer
**Focus:** Will the paper hold up under SC peer review with these additions?
- Read `docs/paper/latex/paper.tex` (especially Sections 3, 5, 6, 7, 8)
- Are all 11 `\pending{}` markers accounted for in the plan?
- Does the proposed Section 6.9 fit the paper's flow, or should comparison be woven into existing subsections?
- Is the LASSI argument based on augmentation degradation strong enough? Are there counterarguments?
- Is the prompt anonymization emphasis placed in the right section (3 vs 5)?
- Does the "benchmark paper, not LLM evaluation paper" framing survive with a 2-model comparison section?
- Page budget: will all additions fit in ~10 pages IEEE double-column?

### Agent 3: Technical Completeness Reviewer
**Focus:** Are there missing steps, ordering hazards, or unstated assumptions?
- Does the figure pipeline (`generate_paper_figures.py`) actually auto-discover multiple models, or does it need code changes beyond F7?
- The plan mentions GPT color `#E0E0E0` → `#56B4E9` — is this the only code change needed?
- Coverage gap: GPT missing `omp_target-to-cuda` — is this properly handled in all tables/figures/prose?
- Are there scripts that need `--project-root` that the plan doesn't mention?
- Does `generate_paper_data.py` handle pass@k data correctly for GPT (temp=0.7, sample files with `-s` suffix)?
- Check: `scripts/generate_paper_figures.py` MODEL_COLORS, MODEL_DISPLAY, MODEL_LINESTYLE — are these complete for GPT?

### Agent 4: Risk & Simplification Reviewer
**Focus:** What could go wrong? What can be cut to save time?
- Given 2 days to deadline, is the scope realistic?
- Which tasks are P0 (submission-blocking) vs P1 (nice-to-have)?
- Can Phase 18 (verification) be parallelized with Phase 17 (integration)?
- Is writing `cross_model_comparison.py` necessary, or can comparison stats be computed inline?
- Should the augmentation degradation examples go in a table rather than prose (more space-efficient)?
- What's the fallback if figure regeneration breaks or produces bad output?
- Are there simpler alternatives that achieve 80% of the impact?

## Key Files for Reviewers

| File | Purpose |
|------|---------|
| `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` | THE PLAN being reviewed |
| `docs/paper/latex/paper.tex` | The paper (read Sections 3, 5.1, 6, 7, 8) |
| `results/evaluation/azure-gpt-4.1-mini/` | GPT result files (897 total) |
| `results/analysis/paper_data.json` | Existing Qwen analysis baseline |
| `scripts/generate_paper_figures.py` | Figure generation (check MODEL_COLORS ~line 84) |
| `scripts/evaluation/analyze_eval.py` | Multi-model aggregation |
| `scripts/analysis/generate_paper_data.py` | Paper statistics generator |
| `scripts/evaluation/llm_evaluate.py` | Anonymization code (~line 570) |
| `.claude/rules/known-issues.md` | KNOWN_FAIL specs to exclude |

## Expected Output

Each agent should produce a structured review with:

```
## [Agent Name] Review

### PASS — Things that look correct
- ...

### FLAG — Concerns that need addressing before execution
- [SEVERITY: HIGH/MEDIUM/LOW] Description + suggested fix

### BLOCK — Issues that would prevent successful execution
- Description + what must change
```

After all 4 agents complete, synthesize into a single verdict:
- **APPROVED** — proceed to Phase 16 execution
- **APPROVED WITH CONDITIONS** — list the conditions that must be addressed
- **BLOCKED** — list blockers that require replanning

## GPT-4.1 Mini Data Quick Reference

```
Location: results/evaluation/azure-gpt-4.1-mini/
Files: 897 total (606 primary temp=0.0, 291 pass@k temp>0)
Model ID: azure-gpt-4.1-mini
Primary pass rate: 26.6% (161/606)
Directions: 7 (missing omp_target-to-cuda)
Suites: rodinia (693), hecbench (108), mixbench (32), xsbench (32), rsbench (32)
Augment levels: L0 (416), L1-L4 (120-121 each)
```

## Qwen Baseline Quick Reference

```
Location: results/evaluation/together-qwen-3.5-397b-a17b/
Files: ~1136 total (710 primary, 426 pass@k)
Model ID: together-qwen-3.5-397b-a17b
Primary pass rate: ~38.3% (272/710)
Directions: 8 (includes omp_target-to-cuda)
Paper data: results/analysis/paper_data.json
```
