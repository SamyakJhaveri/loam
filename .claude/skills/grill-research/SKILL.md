---
name: grill-research
description: Adversarial research interrogation before launching an eval or making a published claim. Use before /overnight-eval, before adding a claim to the paper, or when a reviewer-style stress test is needed. 4 waves: basics, clarifications, deep probes, assessment. Stops you from running expensive batches on shaky premises.
---
ultrathink
# Research Interrogation

Use when designing experiments, preparing for paper review, defending methodology,
or before launching any eval campaign. Forces articulation of null hypothesis,
confounding variables, success criteria, failure modes, and alternative explanations.

**Trigger:** When user types `/grill-research` with optional arguments.

## Arguments

- `$ARGUMENTS` --- free-text description of the experiment, claim, or methodology
  to interrogate. If omitted, ask the user what they want to examine.

## Iron Law

```
NO EXPERIMENT WITHOUT A STATED NULL HYPOTHESIS.
No eval batch, no paper claim, no methodology decision proceeds until the user
has articulated what result would DISPROVE their expectation.
```

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I already know what I'll find" | Then stating the hypothesis costs 10 seconds. If you're wrong, you just saved a week. |
| "This is just exploratory" | Exploratory work still needs success criteria --- otherwise you can't tell when to stop. |
| "The hypothesis is obvious" | Obvious hypotheses are the ones most likely to be wrong. State it anyway. |
| "I'll figure out the analysis later" | Post-hoc analysis is p-hacking. Define metrics before running. |
| "It's a small experiment" | Small experiments with wrong methodology produce small, wrong results. |
| "The reviewers won't care about this detail" | Reviewers have rejected papers for exactly this. 30 seconds to verify. |

## Red Flags --- STOP

If any of these occur, restart the interrogation from Wave 1:

- User cannot state what result would falsify their claim
- Numbers cited without a file path to verify against
- "All models" or "most kernels" without specifying which ones
- Confounding variables dismissed as "probably fine"
- Success criteria defined after seeing preliminary results
- Comparison between runs with different prompt formats, retry counts, or augmentation levels

## Workflow

### Phase 1: Wave 1 --- Basics

Ask these questions. Do not proceed until ALL are answered:

1. **Null hypothesis:** "What specific result would prove your expectation WRONG?"
2. **Independent variable:** "What exactly are you changing between conditions?"
3. **Dependent variable:** "What metric are you measuring? How is it computed?"
4. **Success criteria:** "What numeric threshold separates success from failure?"
5. **Scope:** "Which specs, models, directions, and augmentation levels?"

**Verification gate:** All 5 questions answered with concrete, specific values.
No "most", "roughly", "probably" --- exact numbers or file paths.

### Phase 2: Wave 2 --- Clarifications

Apply all 4 analytical lenses. Probe any weak answers from Wave 1.

#### Methodological Lens
- Are you comparing apples to apples? Same specs, same prompt format, same retries?
- Is the measurement instrument (harness) calibrated? Are specs verified TRUE PASS?
- Does `overall_status` (not top-level `run_status`) determine the verdict?

#### Statistical Lens
- With N specs and M models, how many data points do you have?
- Is N large enough to distinguish signal from noise?
- Are you reporting mean, median, or mode? Why that choice?
- If claiming "model A outperforms model B", what is the effect size?

#### Adversarial Lens
- What is the strongest objection a reviewer could raise?
- Could the result be explained by a confounding variable instead?
- If you got the opposite result, what would that mean?

#### Reproducibility Lens
- Can someone re-run this from scratch with only what's in the repo?
- Are all environment variables documented (CUDA version, compiler, GPU)?
- Is the model version pinned (e.g., `claude-sonnet-4-20250514`, not `claude-sonnet`)?
- Are results stored with `--resume` in a unique output directory?

**Verification gate:** Each lens has at least one concrete answer. User has addressed
the strongest adversarial objection.

### Phase 3: Wave 3 --- Deep Probes

#### Codebase Verification (MANDATORY)

When the user cites a number (e.g., "pass rate is 34%", "54 specs pass"), verify it:

```bash
# Count actual result files and statuses
find {{PROJECT_ROOT}}/results/evaluation/ -name "*.json" | head -5
# Then read specific files to verify claimed numbers
```

Cross-check against:
- `results/evaluation/` --- actual result JSONs (authoritative)
- `results/augmentation/` --- augmentation results
- Spec files in `specs/` --- verify spec counts and KNOWN_FAIL exclusions

**Check `.claude/rules/known-issues.md` for any KNOWN_FAIL items to exclude.**

**Do NOT accept any claimed number without tracing it to data on disk.**

#### Alternative Explanations

For each finding/claim, generate at least 2 alternative explanations:
- "Could this result be caused by prompt differences rather than model capability?"
- "Could the KNOWN_FAIL exclusions bias the comparison?"
- "Is the augmentation level confounding the model comparison?"

#### Statistical Validity

- With the given sample size, what is the minimum detectable effect?
- Would a different grouping of kernels (by category, by complexity) change the story?
- Are per-kernel anomalies (like the backprop tier inversion) noise or signal?

**Verification gate:** All cited numbers verified against actual files. At least 2
alternative explanations generated and addressed.

### Phase 4: Assessment

Present a structured assessment:

```
=== RESEARCH INTERROGATION ASSESSMENT ===

Hypothesis:     <stated null hypothesis>
Variables:      IV: <...>  DV: <...>
Sample size:    <N specs x M models x K directions = total>
Success criteria: <threshold>

METHODOLOGICAL:    [STRONG / ADEQUATE / WEAK] --- <1-line reason>
STATISTICAL:       [STRONG / ADEQUATE / WEAK] --- <1-line reason>
ADVERSARIAL:       [STRONG / ADEQUATE / WEAK] --- <1-line reason>
REPRODUCIBILITY:   [STRONG / ADEQUATE / WEAK] --- <1-line reason>

Data verification: [N/N numbers verified against disk]

Top risks:
1. <risk + mitigation>
2. <risk + mitigation>
3. <risk + mitigation>

VERDICT: [READY TO PROCEED / NOT READY --- <blocking issue>]
```

If NOT READY, list the specific items that must be addressed before proceeding.
Do not allow the user to launch an eval batch or make a paper claim until READY.

## Project Context (Self-Contained)

- **Project root:** `{{PROJECT_ROOT}}`
- **Results directory:** `results/` (check CLAUDE.md for structure)
- Check CLAUDE.md and `.claude/rules/known-issues.md` for project-specific counts, models, and exclusions
- **Timing caveat:** Wall-clock times are often unreliable for performance claims. Use proper profiling tools for performance numbers.
- **Result truth:** Check CLAUDE.md for which fields/files are authoritative in your result format.
