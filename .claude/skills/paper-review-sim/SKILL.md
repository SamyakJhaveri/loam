---
name: paper-review-sim
description: Simulate a NeurIPS/SC/ICSE-style peer review with 5 reviewer personas (HPC, ML, Stats, Reproducibility, Devil's Advocate). Use before paper submission, after major methodology changes, or when stress-testing a draft against expected objections. Each reviewer verifies claims against actual result data.
---

# Paper Review Simulation

Use when preparing a paper draft for submission, stress-testing claims before
writing, or wanting structured feedback on methodology, presentation, or rigor.
Simulates a 5-reviewer SC26 panel.

**Trigger:** When user types `/paper-review-sim` with optional arguments.

## Arguments

- `$ARGUMENTS` --- path to paper draft file(s) or specific section to review.
  If omitted, searches for `docs/paper_draft.md` or asks the user.

## Iron Law

```
NO REVIEWER MAY ACCEPT A CLAIM WITHOUT TRACING IT TO DATA.
Every number, percentage, comparison, or performance claim in the paper must be
verified against actual files in results/evaluation/ or results/augmentation/.
"The paper says X" is not evidence. The data file says X is evidence.
```

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "The numbers are from a previous session" | Previous sessions can have bugs. Verify against current disk state. |
| "This is just a rough draft" | Rough drafts with wrong numbers become final drafts with wrong numbers. |
| "I'll verify during camera-ready" | Camera-ready is too late. SC26 reviewers see the submitted version. |
| "The reviewer personas are too harsh" | SC26 acceptance rate is ~25%. Real reviewers ARE this harsh. |
| "One reviewer disagreeing is fine" | One dissenting reviewer can sink a paper. Address all concerns. |

## Red Flags --- STOP

If any of these occur, halt the review and flag immediately:

- A number in the paper cannot be traced to any file on disk
- A claim about model A vs model B contradicts the actual result JSONs
- "All models" or "consistently" used without checking every model's data
- Performance claims based on wall-clock time (unreliable --- see Timing Caveat below)
- Missing error bars, confidence intervals, or sample sizes for quantitative claims
- Related work section missing key papers (LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus)

## Workflow

### Phase 1: Locate and Read the Draft

1. Find the paper draft at the path in `$ARGUMENTS` or `docs/paper_draft.md`.
2. Read the full draft to understand structure, claims, and data references.
3. Identify every quantitative claim (pass rates, failure counts, comparisons).

**Verification gate:** Draft located and read. All quantitative claims catalogued.

### Phase 2: Data Verification Sweep

Before spawning reviewers, verify every number in the paper against actual data:

```bash
# Count result files per model
for model_dir in {{PROJECT_ROOT}}/results/evaluation/*/; do
  echo "$(basename $model_dir): $(find "$model_dir" -name '*.json' | wc -l) files"
done
```

Read specific result JSONs to verify claimed pass rates. Use `overall_status` field
(not top-level `run_status`) as the authoritative verdict.

Build a verification table:

```
=== DATA VERIFICATION ===
| Claim in paper | Source file(s) | Verified value | Match? |
|----------------|---------------|----------------|--------|
| "34% overall pass rate" | eval_summary.json | <actual> | YES/NO |
| "BUILD_FAIL is 36%" | <files> | <actual> | YES/NO |
```

**Verification gate:** Every number traced to a file. Any mismatches flagged BEFORE
the review proceeds.

### Phase 3: Spawn Review Panel

Launch 5 subagents in parallel. Each reviewer gets:
- The full paper draft (or relevant section)
- The data verification table from Phase 2
- Their specific review focus (below)
- Access to read files in `results/evaluation/` and `results/augmentation/`

#### Reviewer R1: HPC Domain Expert

**Focus:** GPU architecture correctness, performance claims, parallelism semantics.

Review checklist:
- Are CUDA/OpenMP/OpenCL semantics described accurately?
- Do performance claims use kernel time (not wall-clock)?
- Is the CUDA-to-OpenMP thread mapping discussion correct (SPMD vs fork-join)?
- Are warp divergence, memory coalescing, and occupancy discussed where relevant?
- Is the hardware (RTX 4070, CUDA 12, nvcc from HPC SDK 24.3) correctly documented?
- Are data movement patterns (cudaMemcpy elimination in OMP translations) addressed?

Score: 0-100. Must cite specific paper sections and result files.

#### Reviewer R2: ML/AI Researcher

**Focus:** LLM evaluation methodology, model comparison fairness, prompt engineering.

Review checklist:
- Is the comparison between models fair? Same prompt, same retries, same specs?
- Are model versions pinned (exact model IDs, not just "Claude" or "Gemini")?
- Is the thinking/reasoning confound addressed (Gemini Flash Lite thinking OFF by default)?
- Are temperature and sampling parameters documented?
- Is the prompt format (system prompt, code context, augmentation) fully specified?
- Are self-repair attempts (retry mechanism) documented and controlled across models?
- Is BUILD_FAIL analysis distinguishing model capability from prompt issues?

Score: 0-100. Must cite specific paper sections and result files.

#### Reviewer R3: Benchmarking Methodologist

**Focus:** Statistical rigor, reproducibility, baseline validity.

Review checklist:
- Is sample size (N specs x M models x K directions) sufficient for claims?
- Are results reported with appropriate statistical measures (not just percentages)?
- Is the baseline clearly defined (Rodinia reference implementations)?
- Are KNOWN_FAIL specs excluded consistently across all analyses?
- Is augmentation level-invariance claim (54/60 at L1-L4) verified?
- Are per-kernel anomalies (backprop tier inversion) addressed as noise vs signal?
- Is the failure taxonomy (BUILD_FAIL/RUN_FAIL/VERIFY_FAIL) consistently applied?

Score: 0-100. Must cite specific paper sections and result files.

#### Reviewer R4: Reproducibility Reviewer

**Focus:** Environment capture, result versioning, open-source readiness.

Review checklist:
- Can the full pipeline be re-run from a fresh clone?
- Are all dependencies documented (Python version, CUDA SDK, compiler flags)?
- Is the Rodinia submodule version (commit `9c10d3ea`) recorded?
- Are API keys the only external dependency? Are they documented?
- Is `--project-root` documented as required (auto-detection broken)?
- Are result JSONs committed and version-controlled?
- Is the spec schema (v1.0.0) documented?
- Could a reviewer reconstruct any table or figure from the raw data?

Score: 0-100. Must cite specific paper sections and result files.

#### Reviewer R5: Devil's Advocate

**Focus:** Strongest objections, alternative explanations, novelty assessment.

Review checklist:
- What is the strongest argument that this work is NOT novel?
  (Compare to SWE-bench, HumanEval, TransCoder, LASSI, CodeRosetta, HPC-Coder-v2, OMPify)
- Could the results be explained by prompt engineering rather than model capability?
- Is "22% pass rate" actually useful? What would a practitioner do with this?
- Are the benchmark kernels representative of real HPC workloads?
- Could a simpler approach (regex-based translation, template matching) achieve similar results?
- What is the paper's contribution beyond "we ran LLMs on code and measured pass rates"?
- Is the threat to validity section honest about limitations?

Score: 0-100. Must cite specific paper sections and result files.

**Verification gate:** All 5 reviewers have returned scores and written reviews.

### Phase 4: Aggregate and Synthesize

Collect all reviews and produce a unified panel report:

```
=== SC26 SIMULATED REVIEW PANEL ===

PAPER: <title>
DATE:  <date>

┌─────────┬───────┬──────────────────────────────────────────┐
│ Reviewer │ Score │ One-line verdict                         │
├─────────┼───────┼──────────────────────────────────────────┤
│ R1 (HPC)│  XX   │ <verdict>                                │
│ R2 (ML) │  XX   │ <verdict>                                │
│ R3 (Stats)│ XX  │ <verdict>                                │
│ R4 (Repro)│ XX  │ <verdict>                                │
│ R5 (Adv) │  XX  │ <verdict>                                │
├─────────┼───────┼──────────────────────────────────────────┤
│ AVERAGE  │  XX   │                                          │
└─────────┴───────┴──────────────────────────────────────────┘

SC26 CRITERIA:
  Novelty:          [1-5] <justification>
  Reproducibility:  [1-5] <justification>
  Significance:     [1-5] <justification>
  Presentation:     [1-5] <justification>

DECISION: [STRONG ACCEPT / WEAK ACCEPT / BORDERLINE / WEAK REJECT / STRONG REJECT]

=== PRIORITY-RANKED ACTION ITEMS ===

P0 (must fix before submission):
1. <action> --- raised by R<N>
2. <action> --- raised by R<N>

P1 (strongly recommended):
1. <action> --- raised by R<N>

P2 (nice to have):
1. <action> --- raised by R<N>

=== QUESTIONS FOR AUTHORS ===
(Questions reviewers would ask in the rebuttal phase)
1. <question> --- R<N>
2. <question> --- R<N>

=== SUGGESTED EXPERIMENTS ===
(Additional experiments that would strengthen the paper)
1. <experiment> --- R<N>
```

**Verification gate:** All action items are concrete and actionable. Every data
mismatch from Phase 2 appears as a P0 item.

### Phase 5: Author Response Coaching

If requested, help the user draft responses to each reviewer's concerns:
- For each P0 item: propose a concrete fix with file paths and commands
- For each question: draft a factual response with data citations
- For each suggested experiment: estimate effort and prioritize

## Timing Caveat (Self-Contained)

All existing eval results use `timing_method: "wall_time"`. Sub-millisecond baseline
wall times produce unreliable speedup ratios. Do NOT let the paper claim speedup
numbers from `speedup_ratio` in result JSONs. Valid performance measurement requires
`nvprof`/`ncu` for CUDA kernel time and `omp_get_wtime()` for OMP.

## Project Context (Self-Contained)

- **Project root:** `{{PROJECT_ROOT}}`
- **Paper draft:** `docs/paper_draft.md` (or as specified in arguments)
- **Eval results:** `results/evaluation/{model}/` directories
- **Augmentation results:** `results/augmentation/`
- **Models:** claude-sonnet, gemini-2.5-flash-lite, groq-llama-3.3-70b, together-qwen-3.5
- **Suites:** rodinia (54 TRUE PASS, 6 KNOWN_FAIL), xsbench (4 PASS)
- **SC26 target:** Supercomputing 2026 conference
- **Key related work gaps:** LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus, TransCoder
- **Result JSON truth:** Use `overall_status` field as authoritative verdict
