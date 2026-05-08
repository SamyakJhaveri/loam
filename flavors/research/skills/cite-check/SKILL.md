---
name: cite-check
description: Paper citation and claims verifier. Use before submitting a paper, after major eval runs that change numbers, or when reviewing a paper draft. Traces every numeric claim in the paper to a result JSON on disk; flags UNTRACED, MISMATCH, STALE_REF, MISSING_CITE, PHANTOM categories.
---

# Paper Citation and Claims Verifier

Use when auditing a paper draft for numerical accuracy, stale references, and
unsubstantiated claims. Traces every number and assertion back to actual result files
on disk.

**Trigger:** When user types `/cite-check` with an optional file path.

## Iron Law

```
NO NUMBER IN THE PAPER WITHOUT A TRACEABLE DATA SOURCE
```

## Arguments

- `$ARGUMENTS` — optional: path to paper draft file. Defaults to `docs/paper_draft.md`.

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "The numbers are approximately right" | Reviewers check exact numbers. "Approximately" gets your paper rejected |
| "I'll update the numbers before submission" | Stale numbers propagate — every draft review builds intuition on wrong data |
| "Only the final version matters" | SC papers are reviewed once. There is no "fix it later" after submission |
| "The trend is correct even if the number is off" | A wrong number undermines trust in every other number in the paper |

## Red Flags — STOP and Escalate

- A percentage or count in the paper that does not match any result file on disk
- A reference to a model that has been dropped from the campaign (e.g., azure-gpt-4.1)
- A table or figure referenced in text that does not exist in the draft
- A claim about "all models" or "all kernels" that actually excludes some
- A speedup ratio cited from wall-clock timing (known to be unreliable — see known-issues.md)

If any red flag triggers: mark the claim as FAIL in the report and include the exact
discrepancy (paper says X, data shows Y).

## Flag Categories

Claims are checked against 5 categories:

| Category | What it catches |
|----------|----------------|
| **UNTRACED** | Claims with numbers but no backing data file on disk |
| **MISMATCH** | Numbers that conflict with current result files (paper says 34%, data shows 22%) |
| **STALE_REF** | References to dropped models, old spec counts, or superseded results |
| **MISSING_CITE** | Related work claims without citations, or methodology claims without spec references |
| **PHANTOM** | Figures, tables, or sections referenced in text but not present in the draft |

## Project Context

- **Paper draft:** `docs/paper_draft.md` (default) or user-specified path
- **Result directories:**
  - `results/evaluation/claude-sonnet/` — Claude Sonnet eval results
  - `results/evaluation/gemini-2.5-flash-lite/` — Gemini Flash Lite results
  - `results/evaluation/groq-llama-3.3-70b/` — Groq Llama results
  - `results/evaluation/together-qwen-3.5-397b-a17b/` — Qwen results (newest)
- **Analysis outputs:** `analysis/data/`, `analysis/reports/`
- **Results:** `results/` directory (check CLAUDE.md for structure)
- Check CLAUDE.md for canonical counts, baselines, and known caveats
- Check `.claude/rules/known-issues.md` for exclusions and known failures

## Workflow

### Phase 1: Load Draft

1. Read the paper draft file from `$ARGUMENTS` or default path
2. If the file does not exist, report error and stop
3. Parse the draft into sections (by `##` headers)

**Verification gate:** File must be readable and non-empty. If empty, STOP.

### Phase 2: Extract Claims

Scan the entire draft for checkable claims. A "claim" is any of:
- A sentence containing a number (percentage, count, ratio)
- A sentence referencing a table or figure ("Table 1", "Figure 3")
- A sentence making a comparative assertion ("X outperforms Y", "all models fail on Z")
- A sentence citing a specific model name, kernel name, or API
- A sentence citing related work without a bibliographic reference

Build a claims list with: claim text, section, line number (approximate), category.

**Verification gate:** At least 1 claim must be extracted. If the draft has zero
checkable claims, something is wrong — report and stop.

### Phase 3: Verify Each Claim

For each claim, perform category-specific verification:

**Numerical claims (counts, percentages, pass rates):**
1. Identify which result files should contain the backing data
2. READ the actual result files — count PASS/FAIL/BUILD_FAIL/etc.
3. Compare the computed number to the paper's number
4. Verdict: PASS (matches), FAIL (mismatch — report both values), WARN (close but not exact)

**Model references:**
1. Check the model name against known active models
2. If the paper references azure-gpt-4.1 or any dropped model: STALE_REF
3. Check that claims about specific models match their actual result files

**Table/figure references:**
1. Search the draft for the referenced table or figure
2. If not found: PHANTOM
3. If found: verify the data in the table matches result files (same as numerical claims)

**Related work citations:**
1. Check if the claim cites a specific paper or system
2. If the claim makes a comparison ("unlike X, we...") without citing X: MISSING_CITE

**Kernel/spec claims:**
1. Verify kernel names exist in `specs/` directory
2. Verify API claims match actual spec files (e.g., "backprop has CUDA and OMP variants")
3. Cross-check any per-kernel results against actual result JSONs

**Verification gate:** Every claim must receive a verdict. No claim is skipped.

### Phase 4: Generate Report

Present findings in structured format:

```
=== CITE-CHECK REPORT ===
File: <path to draft>
Claims checked: <N>
  PASS:       <N> — backed by data, numbers match
  WARN:       <N> — minor discrepancies or approximate matches
  FAIL:       <N> — data mismatch or missing source
  STALE_REF:  <N> — references to dropped/outdated data
  MISSING_CITE: <N> — assertions without citations
  PHANTOM:    <N> — referenced figures/tables not found

--- FAILURES (must fix before submission) ---

[F1] Section: <section>, Line ~<N>
  Claim: "<exact text>"
  Issue: MISMATCH — paper says 34%, results/evaluation/ shows 22.44%
  Data source: <file path> or "NO FILE FOUND"
  Fix: <suggested correction>

[F2] ...

--- WARNINGS (review before submission) ---

[W1] Section: <section>, Line ~<N>
  Claim: "<exact text>"
  Issue: <description>

--- STALE REFERENCES ---

[S1] ...

=== END REPORT ===
```

Sort by severity: FAIL first, then STALE_REF, then WARN, then MISSING_CITE, then PHANTOM.

**Verification gate:** The report must list every extracted claim with a verdict. If any
claim lacks a verdict, the check is incomplete — report it as such.
