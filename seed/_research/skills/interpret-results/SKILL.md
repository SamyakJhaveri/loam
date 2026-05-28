---
name: interpret-results
description: Hypothesis-first interpretation of eval results. Use after an eval batch completes, after /post-eval populates analyses, or when preparing paper narrative from result JSONs. Phase 1 requires a prior hypothesis (prevents post-hoc rationalization); Phase 2 compares to actual data.
auto-activate: false
model: opus
---
# Hypothesis-First Result Interpreter

Use when analyzing evaluation or augmentation results. Prevents post-hoc rationalization
by requiring the user to state their expectations BEFORE seeing any data. Every
interpretation must be grounded in actual result files, not approximations.

**Trigger:** When user types `/interpret-results` with an optional result scope.

## Iron Law

```
NO INTERPRETATION WITHOUT A PRIOR HYPOTHESIS
```

## Arguments

- `$ARGUMENTS` — optional scope for which results to analyze:
  - `<model>` — e.g., `claude-sonnet`, `gemini-2.5-flash-lite`
  - `<direction>` — e.g., `cuda-to-omp`, `omp-to-cuda`
  - `<kernel>` — e.g., `backprop`, `hotspot`
  - `<model> <direction>` — combined filter
  - `all` — full cross-model comparison
  - Omit to be prompted interactively

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I just want to see the numbers" | Numbers without hypotheses lead to p-hacking and cherry-picked narratives |
| "My hypothesis is obvious" | State it anyway — obvious hypotheses are often wrong (backprop tier inversion was "obvious") |
| "This is exploratory" | Exploratory still needs a framework — define what would surprise you |
| "I'll form a hypothesis after I see the data" | That is called post-hoc rationalization. It is the #1 threat to scientific credibility |
| "The pattern is clear" | Clear patterns in small samples are often noise. State the null hypothesis and test it |

## Red Flags — STOP and Restart Process

- Presenting an interpretation before the user has stated their hypothesis
- Cherry-picking results that confirm expectations while ignoring contradictions
- Citing a number without a file path reference to the actual result JSON
- Using `speedup_ratio` from wall-clock timing as evidence (known unreliable)
- Claiming statistical significance without a test (we have small N — be honest about it)
- Generalizing from a single kernel or model to "LLMs" broadly

If any red flag triggers: STOP. Return to Phase 1. Do not proceed until the user has
stated their prior hypothesis.

## Project Context

- **Result directories:**
  - `results/evaluation/together-qwen-3.5-397b-a17b/` — Qwen 3.5 397B (Phase 3 canonical + ablation)
  - Pre-Phase-3 data (claude-sonnet, gemini, groq-llama) was purged 2026-04-20
- **Result JSON structure:** Each file contains `overall_status` (authoritative verdict),
  `attempts[]` array, `build_error_snippet`, `run_stderr_snippet`, `timing_method`,
  `thinking_enabled`, `num_samples`, `seed`, `top_p`, `augment_level`, `sample_id`
- **Failure taxonomy:** PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL, TIMEOUT
- **Known timing limitation:** All results use `wall_time`. `translated_cpu_time_seconds`
  and `translated_kernel_time_seconds` are null. Do NOT use `speedup_ratio` for claims.
- **Qwen canonical (Phase 3, 2026-04-24):**
  - 708 total results: 504 canonical (168 pairs × 3 samples) + 204 ablation (51 pairs × L1-L4)
  - Overall: 243 PASS (34.3%), 290 BUILD_FAIL (41.0%), 131 RUN_FAIL (18.5%), 43 VERIFY_FAIL (6.1%)
  - Zero-shot (max_retries=1, no self-repair). Temperature=0.7. Thinking=on.
  - 146 clean pairs + 22 KNOWN_FAIL-involved (excluded by analyze_eval.py)
- **Pipeline audit findings (2026-04-24):** See `docs/eval-findings/2026-04-24-qwen-pipeline-audit.md`
  - 18 BUILD_FAILs are "header confusion" (prompt shows headers, model #includes instead of inlining)
  - 8 PASS results from KNOWN_FAIL pairs (LLM "fixed" broken source during translation)
  - Ablation pass rate declines monotonically: L1=74.5% → L4=54.9%

## Known Confounding Variables (from pipeline audit)

When interpreting results, always consider these confounds:
1. **Header confusion BUILD_FAILs (~18/290):** Prompt shows source headers and says "inline."
   Some models #include instead → BUILD_FAIL. This is partially prompt design, not purely model quality.
2. **Zero-shot only:** No self-repair means BUILD_FAILs that a retry could fix are counted as failures.
3. **KNOWN_FAIL pollution:** 22 pairs involving KNOWN_FAIL specs ran. Excluded by analysis, but
   8 PASS results suggest LLMs can recover from broken source code — interesting signal.
4. **nvc++ strictness:** OpenMP target translations compiled with nvc++ (NVIDIA HPC SDK 24.3) which
   is stricter about pragma syntax than GCC. Some OMP BUILD_FAILs may pass on GCC.
5. **Verification mode asymmetry:** 527 results use cross_api_combined_pattern, 181 use
   kernel_only_target_pattern. Pass rates differ by verification mode — compare within mode.

## Workflow

### Phase 1: Collect Prior Hypothesis (MANDATORY — cannot be skipped)

Before reading ANY result files, ask the user to state:

```
Before I show you results, I need three things:

1. EXPECTATION: What do you expect to see?
   (e.g., "Claude should outperform Gemini on CUDA-to-OMP because...")

2. NULL HYPOTHESIS: What is the default/boring explanation?
   (e.g., "All models perform equally — differences are noise")

3. FALSIFICATION: What specific observation would make you abandon your expectation?
   (e.g., "If Gemini outperforms Claude on >50% of kernels, my expectation is wrong")
```

**Verification gate:** User must provide all three answers. If they try to skip with
"just show me the numbers" or similar, redirect them to the Anti-Rationalization Table
above and ask again. Do NOT proceed without a stated hypothesis.

Record the user's responses — they will be referenced in the analysis output.

### Phase 2: Read Actual Results

Only after Phase 1 is complete, read the result files matching the scope:

```bash
# Example: list all result files for a model
ls results/evaluation/<model>/*.json | head -50

# Example: read a specific result
# Use Read tool on each JSON, extract overall_status
```

For each result file, extract:
- `overall_status` (the ONLY authoritative verdict — not top-level `run_status`)
- `attempts[]` length (number of retries)
- `build_error_snippet` (for BUILD_FAIL)
- `run_stderr_snippet` (for RUN_FAIL)
- Kernel name and direction (from filename)

Build a structured data table from actual file contents.

**Verification gate:** Every number reported must have a source file path. If a result
file is missing or unreadable, note it explicitly — do not estimate or skip.

### Phase 3: Compare to Stated Expectations

Structure the analysis in this exact order — do NOT rearrange:

#### 3a. Observed Results (raw data)

Present the raw data table. No interpretation yet.

```
=== OBSERVED RESULTS: <scope> ===
Kernel          Direction       Model           Status          Attempts
backprop        cuda-to-omp     claude-sonnet   PASS            1
backprop        cuda-to-omp     gemini-flash    PASS            2
backprop        cuda-to-omp     groq-llama      BUILD_FAIL      3
...

Summary: <N> PASS, <N> BUILD_FAIL, <N> RUN_FAIL, <N> VERIFY_FAIL
Source: results/evaluation/<model>/<files>
```

#### 3b. Comparison to User's Expectation

Directly reference what the user said in Phase 1:

```
Your expectation was: "<quoted expectation>"
Observation: <does the data match or contradict?>
```

Be specific about which results match and which contradict. Do not soften contradictions.

#### 3c. Null Hypothesis Assessment

```
Your null hypothesis was: "<quoted null>"
Assessment: Can we reject it?
```

With small sample sizes (typical for per-kernel analysis), be honest about statistical
power. "We cannot reject the null with N=3 models" is a valid and important conclusion.

#### 3d. Alternative Explanations (minimum 2)

Generate at least 2 alternative explanations for the observed pattern that the user
did NOT suggest. These must be plausible and grounded in the data:

- Training data distribution differences between models
- Kernel-specific code patterns (reductions, stencils, control flow) matching model strengths
- Prompt sensitivity (same code, different tokenization)
- Compiler/build environment effects (not model effects)
- Sample size limitations masking true performance

#### 3e. Confounding Variables

List variables that could explain the results but are not controlled:

- Model temperature and sampling strategy
- Tokenizer differences across models
- Prompt format differences (if any)
- Time-of-day API performance variance
- Retry logic recovering from transient failures vs. systematic failures

#### 3f. Recommended Follow-Up Experiments

Propose 2-3 concrete next experiments that would strengthen or weaken the hypothesis:

```
Recommended experiments:
1. [Experiment]: <description>
   [Tests]: <which hypothesis element this addresses>
   [Command]: <actual command to run, if applicable>

2. [Experiment]: <description>
   ...
```

**Verification gate:** Every recommended experiment must be actionable with the current
project infrastructure. Do not suggest experiments that require new tools or data sources
not already in the project.

### Phase 4: Summary Verdict

```
=== INTERPRETATION SUMMARY ===
Hypothesis:     <SUPPORTED | WEAKENED | REFUTED | INCONCLUSIVE>
Confidence:     <HIGH | MEDIUM | LOW>
Key finding:    <one sentence>
Biggest surprise: <one sentence — what deviated most from expectations>
Paper-ready:    <YES — safe to cite | NO — needs more data | CAUTION — cite with caveats>
Next action:    <single most important follow-up>
```

**Verification gate:** The verdict must be consistent with the data presented in Phase 3.
If the data is INCONCLUSIVE, say so — do not force a conclusion.
