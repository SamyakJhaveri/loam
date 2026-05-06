# Reflection: Pre-Submission Audit

**Date:** 2026-04-28
**Session work:** Audited architecture diagram, figures, appendix data, and NeurIPS 2026 compliance for the ParBench paper. Found 8 diagram errors, 1 data integrity bug, 3 NeurIPS compliance fixes. Updated HANDOFF for fresh-session handoff.
**Files touched:** 2 files — `HANDOFF.md`, `results/analysis/quantitative_findings_gpt54.json`

## What Surprised Me

- **The architecture diagram had 8 errors, not the 1-2 I expected.** The obvious ones (wrong temperature "T=0", wrong task count "1,420") were caught early, but the plan-reviewer agent found 4 more: "self-repair rate" listed in the Metrics box despite self-repair never being exercised, "Fisher" instead of "McNemar" as the statistical test, "6 Translation Directions" when the paper reports 10, and a second typo ("Heterogenous") in the same cell as the first typo I found. Lesson: diagrams that were correct at design time drift as the methodology evolves, and they accumulate errors silently because nobody re-reads the drawio XML.

- **The GPT-5.4 quantitative findings JSON had a wrong metadata model field** — it said "together-qwen-3.5-397b-a17b" (the Qwen model ID). The actual data (822 records) was correct for GPT-5.4, so no analysis was affected, but this would be a data integrity red flag for any reviewer inspecting supplementary material. The bug likely originated when the script was run with a copy-paste of the Qwen command and the metadata wasn't regenerated.

- **The NeurIPS "Datasets & Benchmarks" track was renamed to "Evaluations & Datasets" for 2026**, requiring a `[eandd]` package option. The `neurips_2026.sty` already supported it (lines 58-62), but in anonymous submission mode this option has zero visible effect on the PDF — only the internal `\@trackname` variable changes, which renders only in camera-ready `[final]` mode. A fresh session could waste time debugging "why nothing changed."

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (add to "Key Build/Run Rules" or create new section)

```
## Supplementary Material Data Integrity

Before submission, verify metadata fields in all analysis JSON files:
- `quantitative_findings_*.json` → check `metadata.model` matches filename suffix
- `paper_data_*.json` → check model-specific fields
- `cross_model_comparison.json` → check both model references

Command: `python3 -c "import json,glob; [print(f'{f}: {json.load(open(f))[\"metadata\"][\"model\"]}') for f in sorted(glob.glob('results/analysis/quantitative_findings_*.json'))]"`

This catches copy-paste bugs where a script is re-run for model B using model A's config.
```

**Why:** The metadata.model bug in `quantitative_findings_gpt54.json` would not have been caught by any existing validation (schema validation checks spec files, not analysis outputs). A reviewer or reproduction attempt inspecting the supplementary JSON could flag this as a data integrity issue.

## Prompt Improvement

**Original approach:** The user asked broadly about "figures, architecture diagram, appendix, NeurIPS guidelines" as a single question. This triggered the brainstorming skill, which launched 3 Explore agents, then a Plan agent, then a plan-reviewer agent — burning significant context on broad exploration before narrowing to actionable issues.

**Better approach:** For a pre-submission audit, the task should have been split into independent checks with specific verification criteria upfront.

```
Run a pre-submission audit of the ParBench NeurIPS paper. Check these 4 things independently and report exact fixes needed:

1. ARCHITECTURE DIAGRAM: Read docs/paper/NeurIPS_ready_version/figures/parbench_architecture.drawio XML. Cross-reference every text element against the paper text (framework.tex, experimental-setup.tex, results.tex). Report any factual mismatch.

2. FIGURES: Verify all figure PDFs in docs/paper/NeurIPS_ready_version/figures/ are dated after the latest data in results/analysis/. Confirm both model variants exist.

3. APPENDIX DATA: Spot-check 5 numerical claims in appendices_neurips.tex against quantitative_findings_{qwen,gpt54}.json.

4. NEURIPS COMPLIANCE: Fetch the NeurIPS 2026 E&D track CFP. Check: style package options, page limits, checklist completeness, code availability requirements.

I can only edit on Overleaf manually. Give exact find-replace text for every fix.
```

## Gotcha Discovered

**Symptom:** The architecture diagram listed "T=0, greedy decode" for the LLM Under Test, "1,420 tasks," and "self-repair rate" in the metrics — all of which were correct at the initial design stage but became wrong as the methodology evolved (temperature changed to 0.7, L0-conditional ablation reduced task count, self-repair was disabled).

**Root cause:** The draw.io diagram was created early in the project and never systematically re-audited against the final paper text. Each methodology change updated the LaTeX but not the diagram. The drawio XML is not machine-verifiable (unlike spec JSONs which have schema validation).

**Fix:** Performed manual cross-reference of every text element in the drawio XML against the paper. Found 8 errors. User will fix in draw.io; verification via grep on the XML.

**Status:** NEW GOTCHA — not yet documented. Suggest adding to workflow: "Before submission, cross-reference every text element in Figure 1 (architecture diagram) against the paper text. Diagrams created early in the project accumulate silent drift."
