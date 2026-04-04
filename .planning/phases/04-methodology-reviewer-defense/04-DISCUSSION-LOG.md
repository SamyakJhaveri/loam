# Phase 4: Methodology & Reviewer Defense - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 04-methodology-reviewer-defense
**Areas discussed:** Kernel isolation defense, Statistical test justification, Conjunction verification defense

---

## Kernel Isolation Defense

### Consolidation approach

| Option | Description | Selected |
|--------|-------------|----------|
| Consolidate into one paragraph | Write ONE authoritative paragraph in Section 3.4 that makes the full argument | ✓ |
| Strengthen existing mentions in-place | Keep distributed across abstract/related work/results, make each more precise | |
| Dedicated subsection | New subsection 'Kernel Isolation Rationale' within Section 3 | |

**User's choice:** Consolidate into one paragraph
**Notes:** Prevents reviewer complaint of 'scattered argument'. New paragraph opens Section 3.4.

### Preemptive defense

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, preemptive defense | Address 'making it too easy' objection proactively | ✓ |
| No, let the numbers speak | Trust XSBench 0% vs 68.8% comparison to speak for itself | |
| Address in rebuttal only | Save defense for rebuttal letter | |

**User's choice:** Yes, preemptive defense

### Tone

| Option | Description | Selected |
|--------|-------------|----------|
| Analytical framing | 'Measurement design choice' language — data does the arguing | ✓ |
| Direct rebuttal style | Name the objection explicitly and counter it | |
| Complementary positioning | Frame kernel-level and repo-level as complementary | |

**User's choice:** Analytical framing

### Evidence scope

| Option | Description | Selected |
|--------|-------------|----------|
| XSBench only | Cleanest apples-to-apples, don't dilute | |
| XSBench + 31/35 SLoC stat | Lead with XSBench, add non-trivial program size evidence | ✓ |
| XSBench + BUILD_FAIL rate | Lead with XSBench, add 'still challenging' evidence | ✓ |

**User's choice:** Both options 2 and 3 — three-layer defense: XSBench comparison, SLoC threshold, BUILD_FAIL rate
**Notes:** User explicitly requested combining both options for maximum defense strength.

### Number format

| Option | Description | Selected |
|--------|-------------|----------|
| Published 68.8% figure | Consistent with abstract, verified | ✓ |
| Both percentage and raw counts | Show '11 of 16 L0 pairs (68.8%)' | |
| Direction-specific breakdown | Break down per direction | |

**User's choice:** Published 68.8% figure

### Cross-references

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as-is | Existing mentions in abstract/related work/results stay intact | ✓ |
| Trim to back-references | Replace with 'as established in Section 3.4' | |
| Strengthen all consistently | Update all mentions to match new paragraph | |

**User's choice:** Keep as-is

---

## Statistical Test Justification

### Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Expand inline in Metrics | Add 1-2 sentences per test after current line 644 | ✓ |
| Dedicated subsection | New 'Statistical Methods' subsection | |
| Footnotes on first use | Footnotes where each test first appears in Results | |

**User's choice:** Expand inline in Metrics subsection

### Depth

| Option | Description | Selected |
|--------|-------------|----------|
| 1-2 sentences each | Name test, state why it fits, enough for stats-literate reviewer | ✓ |
| Full assumptions + alternatives | Null hypothesis, assumptions, alternatives per test | |
| Test + citation only | Textbook citation carries the justification | |

**User's choice:** 1-2 sentences each

### Test coverage

| Option | Description | Selected |
|--------|-------------|----------|
| All three (Wilson, Cochran-Armitage, McNemar) | Complete coverage | ✓ |
| Only Wilson + Cochran-Armitage | McNemar is standard, needs no justification | |
| Add Fisher's exact too | Justify all four tests | |

**User's choice:** All three tests

### Alternatives

| Option | Description | Selected |
|--------|-------------|----------|
| Name alternatives briefly | One clause per test naming what was rejected | ✓ |
| No alternatives | Just positive justification | |
| Alternatives in footnotes | Inline positive, footnote alternatives | |

**User's choice:** Name alternatives briefly

---

## Conjunction Verification Defense

### Example type

| Option | Description | Selected |
|--------|-------------|----------|
| Compilation-only misclassification | Real VERIFY_FAIL: compiles and runs but wrong output | ✓ |
| BLEU score misclassification | High textual similarity but functionally wrong | |
| Both examples | Compilation-only + BLEU | |

**User's choice:** Compilation-only misclassification

### Specificity

| Option | Description | Selected |
|--------|-------------|----------|
| Real kernel name from results | Specific VERIFY_FAIL kernel from Qwen data | ✓ |
| Generic framing | '9.8% of tasks' without naming a kernel | |
| Anonymized category example | 'A stencil computation that...' | |

**User's choice:** Real kernel name from results

### Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Section 3.2 Harness Pipeline | After verify stage description | ✓ |
| Section 5 Metrics | Alongside statistical test justifications | |
| Section 3.4 Evaluation Pipeline | Alongside kernel isolation defense | |

**User's choice:** Section 3.2 Harness Pipeline

### Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Keep focused on exit_code + stdout | Don't repeat clBuildProgram scan | ✓ |
| Include clBuildProgram as second layer | Mention multi-layered verification | |

**User's choice:** Keep focused on exit_code + stdout

---

## Claude's Discretion

- Exact wording and sentence structure of each paragraph
- LaTeX source comment format for new numbers
- Transition between new and existing paragraphs in Section 3.4
- Specific VERIFY_FAIL kernel to use as example (from result JSONs)

## Deferred Ideas

- Reproducibility claims paragraph (METHOD-03) — not selected for discussion; hardware table already covers version pins
