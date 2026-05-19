---
name: grill-research
description: >
  Adversarial research interrogation before launching an eval or making a published
  claim. Use before /overnight-eval, before adding a claim to a paper, or when a
  reviewer-style stress test is needed. 4 waves: basics, clarifications, deep probes,
  assessment. Stops you from running expensive batches on shaky premises.
---

# Research Interrogation

Use when designing experiments, preparing for paper review, defending methodology,
or before launching any eval campaign. Forces articulation of null hypothesis,
confounding variables, success criteria, failure modes, and alternative explanations.

**Trigger:** When user types `/grill-research` with optional arguments.

## Arguments

- `$ARGUMENTS` — free-text description of the experiment, claim, or methodology
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
| "I already know what I'll find" | Then stating the hypothesis costs 10 seconds. If you're wrong, you saved a week. |
| "This is just exploratory" | Exploratory work still needs success criteria — otherwise you can't tell when to stop. |
| "The hypothesis is obvious" | Obvious hypotheses are the ones most likely to be wrong. State it anyway. |
| "I'll figure out the analysis later" | Post-hoc analysis is p-hacking. Define metrics before running. |
| "It's a small experiment" | Small experiments with wrong methodology produce small, wrong results. |
| "The reviewers won't care about this" | Reviewers have rejected papers for exactly this. 30 seconds to verify. |

## Red Flags — STOP

If any of these occur, restart the interrogation from Wave 1:

- User cannot state what result would falsify their claim
- Numbers cited without a file path to verify against
- Vague quantifiers ("all models", "most tasks") without specifics
- Confounding variables dismissed as "probably fine"
- Success criteria defined after seeing preliminary results
- Comparison between runs with different configurations

## Workflow

### Wave 1: Basics

Ask these questions. Do not proceed until ALL are answered:

1. **Null hypothesis:** "What specific result would prove your expectation WRONG?"
2. **Independent variable:** "What exactly are you changing between conditions?"
3. **Dependent variable:** "What metric are you measuring? How is it computed?"
4. **Success criteria:** "What numeric threshold separates success from failure?"
5. **Scope:** "Which tasks, models, and configurations?"

**Gate:** All 5 answered with concrete, specific values. No "most", "roughly", "probably".

### Wave 2: Clarifications

Apply all 4 analytical lenses. Probe any weak answers from Wave 1.

#### Methodological Lens
- Are you comparing apples to apples? Same tasks, same configuration, same retries?
- Is the measurement instrument calibrated? Are baseline results verified?
- Which field in the result data determines the authoritative verdict?

#### Statistical Lens
- With N tasks and M models, how many data points do you have?
- Is N large enough to distinguish signal from noise?
- Are you reporting mean, median, or mode? Why?
- If claiming "A outperforms B", what is the effect size?

#### Adversarial Lens
- What is the strongest objection a reviewer could raise?
- Could the result be explained by a confounding variable?
- If you got the opposite result, what would that mean?

#### Reproducibility Lens
- Can someone re-run this from scratch with only what's in the repo?
- Are all environment variables and versions documented?
- Are model versions pinned (not floating aliases)?
- Are results stored in unique, non-colliding output directories?

**Gate:** Each lens has at least one concrete answer. User has addressed
the strongest adversarial objection.

### Wave 3: Deep Probes

#### Data Verification (MANDATORY)

When the user cites a number, verify it against actual data on disk:
```bash
# Find relevant result files
find results/ -name "*.json" -type f | head -10
# Cross-check claimed numbers against actual data
```

**Do NOT accept any claimed number without tracing it to data on disk.**

#### Alternative Explanations

For each finding/claim, generate at least 2 alternative explanations:
- "Could this result be caused by configuration differences rather than the IV?"
- "Could exclusions bias the comparison?"
- "Is there a confounding variable in the experimental setup?"

#### Statistical Validity

- With the given sample size, what is the minimum detectable effect?
- Would a different grouping of tasks change the story?
- Are anomalies noise or signal?

**Gate:** All cited numbers verified. At least 2 alternative explanations addressed.

### Wave 4: Assessment

```
=== RESEARCH INTERROGATION ASSESSMENT ===

Hypothesis:      <stated null hypothesis>
Variables:       IV: <...>  DV: <...>
Sample size:     <N tasks x M models = total>
Success criteria: <threshold>

METHODOLOGICAL:    [STRONG / ADEQUATE / WEAK] — <1-line reason>
STATISTICAL:       [STRONG / ADEQUATE / WEAK] — <1-line reason>
ADVERSARIAL:       [STRONG / ADEQUATE / WEAK] — <1-line reason>
REPRODUCIBILITY:   [STRONG / ADEQUATE / WEAK] — <1-line reason>

Data verification: [N/N numbers verified against disk]

Top risks:
1. <risk + mitigation>
2. <risk + mitigation>
3. <risk + mitigation>

VERDICT: [READY TO PROCEED / NOT READY — <blocking issue>]
```

If NOT READY, list specific items that must be addressed first.
