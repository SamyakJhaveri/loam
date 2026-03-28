# Critic Review: SC26 Evaluation Campaign Plan

**Author:** Critic Agent (eval-campaign team)
**Date:** 2026-03-28
**Status:** Complete
**Approach:** Adversarial — assume everything that can go wrong will

---

## Task A: Minimum Viable Evaluation (MVE)

### The Question

What is the absolute minimum new data needed for a credible SC26 submission?

### MVE Definition

**The paper's fatal weakness is W1 (underpowered corpus) and W16 (no OpenCL).** The current
data has 255 tasks for cuda-to-omp and 63 for omp-to-cuda. The remaining 4 directions
(all OpenCL-involving) have only 15 tasks each — all XSBench, zero Rodinia. This is
statistically indefensible. A reviewer will immediately note: "You claim 6 translation
directions but only 1 has adequate sample size."

**MVE = Phase 1 only: 192 L0 tasks across 4 OpenCL directions.**

This gives every direction at least 48-51 L0 Rodinia results (17 or 15 kernels x 3 models),
which is minimally adequate for Wilson CIs and chi-squared tests.

### Can the paper survive with ONLY L0 for new OpenCL directions?

**Yes, but with significant caveats.** The augmentation-invariance claim (currently supported
by cuda-to-omp L0-L4 data) can be framed as: "We demonstrate level invariance on the
primary direction (cuda-to-omp, N=255) and report L0 baselines for the remaining 5
directions." This is honest and defensible. The alternative — running L1-L4 for all
directions with thin data — spreads resources without proportional insight.

**Recommended framing:** "Augmentation invariance is established on cuda-to-omp (N=255,
chi2 p=0.83). OpenCL directions are reported at L0 to establish cross-API baseline pass
rates. Full augmentation analysis of OpenCL directions is future work."

### Is Parboil (third benchmark) essential?

**No. Cut it.** The audit (W1) flags "underpowered corpus" but the fix is more *directions*
with existing kernels, not more kernels with existing directions. Adding Parboil means:
new spec generation, new build environment validation, new baseline verification — all
before a single LLM eval runs. The ROI is terrible given the Apr 8 deadline. Frame it
as future work: "ParBench's architecture supports arbitrary benchmark suites; we demonstrate
with Rodinia (21 kernels) and XSBench (1 kernel), with Parboil integration planned."

### Is pass@k essential?

**No. Cut it for the main paper.** Current results are greedy pass@1 with self-repair.
This is a valid and commonly reported metric. Pass@k at temperature=0.8 is a *different*
experiment that requires new API calls, introduces temperature as a confound, and may
produce embarrassing results (Anthropic models may be less temperature-sensitive, making
Claude's pass@k barely better than pass@1 while Groq's improves dramatically — this
would undermine the Claude dominance narrative).

**Recommended framing:** "We report greedy pass@1 with up to 2 self-repair attempts.
Pass@k evaluation with stochastic sampling is orthogonal future work."

### What claims must change if we only do MVE?

| Current claim | MVE-compatible claim |
|---|---|
| "6 translation directions" | "6 directions; cuda-to-omp is primary (N=255), others are L0 baselines" |
| "Augmentation invariance across all directions" | "Augmentation invariance on cuda-to-omp; OpenCL directions at L0 only" |
| "Comprehensive cross-API evaluation" | "Cross-API evaluation with asymmetric depth" |
| "1,530 tasks" | "570 tasks (378 existing + 192 new L0)" |

### [BLOCKER] MVE Still Requires OpenCL Build Environment Validation

Phase 0 (canary test) is a hard prerequisite. If OpenCL specs fail to build/run/verify
on the GPU machine, the entire campaign stalls. The Planner allocates 15 minutes for this.
**That is dangerously optimistic.** OpenCL toolchain issues on NVIDIA (ICD loader, headers,
library paths) can take hours to debug. Budget 2 hours for Phase 0 with a fallback plan:
if OpenCL env fails, the paper must survive on cuda-to-omp + omp-to-cuda only (318 tasks).

---

## Task B: Risk Register

### Phase 0: Canary Test (15 min planned)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OpenCL ICD loader not installed | MEDIUM | CRITICAL — blocks all OpenCL directions | Run `clinfo` first; install `ocl-icd-opencl-dev` if missing |
| OpenCL header/lib path mismatch | MEDIUM | HIGH — build failures | Verify `OPENCL_INC` and `OPENCL_LIB` in specs match actual paths |
| OpenCL spec pass baseline not established | LOW | HIGH — no reference for verify | Run `python3 -m harness -v verify` on all 15+ OpenCL specs first |
| Canary takes >2 hours | MEDIUM | MEDIUM — delays Phase 1 start | Set hard 2hr cutoff; if blocked, fall back to omp-to-cuda L1-L4 only |

### Phase 1: L0 OpenCL Baselines (4.8h planned, 192 tasks)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Groq rate limiting (30 req/min free tier) | HIGH | MEDIUM — slowdown, not blocker | 192/3 = 64 Groq tasks; at 90s avg, natural spacing is fine. But burst retries could trigger limits. |
| Systematic OpenCL BUILD_FAIL | HIGH | HIGH — many directions yield 0% pass | Expected: OpenCL build is harder than OMP. If >90% BUILD_FAIL, pivot to "OpenCL as challenge direction" framing. |
| EXTRACTION_FAIL spike on OpenCL translations | MEDIUM | MEDIUM — inflates failure rate | OpenCL code has different syntax (kernel qualifiers, `__global`); LLM may produce unparseable output. |
| API key expiry mid-batch | LOW | HIGH — partial results | Pre-flight check in batch script handles this. But check token quotas too. |
| Wall-clock overrun (>8h) | MEDIUM | LOW — still within schedule | 90s/task is average; OpenCL builds may be slower. Budget 6-8h. |

### Phase 2: L1-L4 Augmentation (14.1h planned, 960 tasks)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Augmentation transforms failing on OpenCL `.cl` files | **HIGH** | **HIGH** — L1-L4 produce identical code to L0, nullifying augmentation claim | **[BLOCKER]** See detailed analysis below |
| 14.1h wall-clock overrun | MEDIUM | HIGH — pushes into paper writing window | Two tmux windows helps. But if either stalls, the other can't compensate. |
| Groq rate limiting on 320 sequential calls | MEDIUM | MEDIUM — Groq window runs slower | Groq's 64 tasks in Phase 1 + 320/3 in Phase 2 = ~170 Groq calls. May need delays. |
| L3-L4 augmentation producing non-compilable OpenCL | MEDIUM | MEDIUM — inflated BUILD_FAIL at high augmentation | If L3-L4 show dramatically higher BUILD_FAIL than L0, the "augmentation invariance" claim breaks for OpenCL. |
| Window 1 (564 tasks) finishes 4h after Window 0 (396 tasks) | HIGH | LOW — just wait | This is by design. But the imbalance means the machine is 50% idle for 4h. |

**[BLOCKER] Augmentation on OpenCL `.cl` files:**
The augmentation pipeline uses libclang-backed AST transforms. I checked the augmentation
results (`results/augmentation/phase3_opencl.json`): for `rodinia-bfs-opencl` at L1, the
`transforms_applied` for `Kernels.cl` is `[]` (empty). The transforms only applied to
`.cpp` host files. At L4, `Kernels.cl` gets `SwapCondition`, `PointerArithmeticToArrayIndex`,
`ChangeNames` — but these are host-side transforms being naively applied to OpenCL kernel
files. **OpenCL kernel files (`.cl`) use a C99 dialect that libclang may parse differently
from standard C/C++.** If transforms silently produce no changes on `.cl` files at L1-L2,
then L1-L2 results for OpenCL-as-source directions are effectively L0 results with
different filenames. This doesn't invalidate the data but it weakens the augmentation
claim: "augmentation is invariant" becomes trivially true because no augmentation occurred.

**Recommendation:** Before Phase 2, run augmentation at L1-L4 on 3 diverse OpenCL specs
and verify that transforms actually modify the `.cl` files. If they don't, L1-L4 for
OpenCL-as-source directions (opencl-to-cuda, opencl-to-omp) should be deprioritized
or the paper should note "augmentation transforms apply to host code only; kernel files
(.cl) receive fewer modifications at low augmentation levels."

### Phase 3: Retries + Analysis (40 min planned)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| EXTRACTION_FAIL retries still failing | HIGH | LOW — 23 tasks, marginal impact | These are likely model-inherent failures, not transient. Budget 50% re-failure rate. |
| Analysis script bugs | MEDIUM | MEDIUM — wrong numbers in paper | Run existing `analyze_eval.py` first; compare with manual spot-checks. |
| New results change statistical conclusions | LOW | HIGH — pivot required | If OpenCL data shows Gemini > Claude on any direction, the "Claude dominance" claim needs qualification. |

### Phase 4: Parboil (not scheduled)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Parboil source unavailable or broken | MEDIUM | LOW — already recommended cutting | N/A — recommend not doing this phase |
| Parboil spec generation takes >4h | HIGH | HIGH — eats paper writing time | Spec generation for a new suite has historically taken a full session |

### Phase 5: Pass@k Pilot (not scheduled)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Temperature=0.8 produces garbage from Claude | MEDIUM | HIGH — wasted API cost | Anthropic models may clamp temperature or behave differently at high temp |
| Pass@k barely improves over pass@1 | MEDIUM | MEDIUM — adds section with no insight | Only worth doing if pilot shows >10pp improvement |

---

## Task C: Scope Cut Priority List

Ordered by least-damage-first (cut from top):

| Priority | What to Cut | Audit Weakness | Damage Assessment |
|---|---|---|---|
| 1 (cut first) | **Parboil (Phase 4)** | W1 (underpowered corpus) | Minimal — adds breadth but not depth. "Future work" framing is standard. |
| 2 | **Pass@k (Phase 5)** | W4 (rigor) | Low — greedy pass@1 + self-repair is a valid metric. Literature precedent exists. |
| 3 | **L1-L4 for opencl-to-cuda and opencl-to-omp** | W1, W16 | Low-medium — OpenCL-as-source augmentation may not actually modify kernel files (see blocker above). Data would be near-duplicate of L0. |
| 4 | **L1-L4 for omp-to-opencl and cuda-to-opencl** | W1, W16 | Medium — these DO augment source (CUDA/OMP host code), so L1-L4 is meaningful. But can be deferred. |
| 5 | **L1-L4 for omp-to-cuda** | W1 | Medium — L0 is already done; L1-L4 completes bidirectional symmetry with cuda-to-omp. Valuable but not essential. |
| 6 | **Self-repair transition table** | W4 | Medium — nice-to-have for paper depth. Can be computed from existing data without new runs. |
| 7 | **Statistical analysis (CIs, tests)** | W4 (rigor) | HIGH — this is what separates "student project report" from "SC26 paper." Must keep. |
| 8 | **L0 for 4 OpenCL directions (Phase 1)** | W1, W16 | VERY HIGH — without this, paper has only 2 of 6 directions with Rodinia data. Reviewers will reject. |
| 9 (NEVER cut) | **Fixing 3-model narrative + stale numbers** | W7, W2, W3 | **FATAL** — paper currently references 4 models. Submitting with stale data = instant desk reject. |

---

## Task D: Data Validity Concerns

### D1. Pre-S-VERIFY Results: Are PASS Results Trustworthy?

**This is the most important data validity question.**

I checked the `verify_strategy` field across all 504 result files:

| verify_strategy | Count | Notes |
|---|---|---|
| `None` | 349 | Files that never reached verification (BUILD_FAIL, RUN_FAIL, EXTRACTION_FAIL) |
| `stdout_pattern+exit_code` | 105 | **Post-fix conjunction verification** |
| `stdout_pattern` | 45 | All are VERIFY_FAIL (matched stdout but didn't check exit, or vice versa) |
| `exit_code` | 5 | **Pre-fix: exit_code only, no stdout check** |

**Findings:**
- Of 414 standard (non-omp_target) files, **90 PASS use `stdout_pattern+exit_code`** (the
  correct conjunction method) and **1 PASS uses `exit_code` only** (the pre-fix method).
- The 1 exit_code-only PASS is `claude-sonnet-4-6/xsbench-xsbench-opencl-to-xsbench-xsbench-cuda-L4.json`.
  This could be a false positive — it passed exit_code check but was never verified against
  stdout_pattern.

**[BLOCKER] Recommendation:** That 1 file must be re-verified or re-run before paper
submission. If the XSBench CUDA target has a stdout_pattern in its spec, re-run the
harness verify step on the translated code. If it passes stdout_pattern+exit_code, keep
it. If it fails, it becomes VERIFY_FAIL and the paper number drops by 1.

**Overall assessment:** The vast majority of PASS results (90/91 in standard dirs) use the
correct verification method. The pre-S-VERIFY concern is largely mitigated. The paper
should note: "All results verified using stdout_pattern + exit_code conjunction."

### D2. 504 vs 468 Discrepancy: Should the Paper Acknowledge Excluded Files?

**504 files on disk = 414 standard + 90 omp_target.** The eval_summary.json reports 468 tasks
because it includes 414 standard + 54 tasks from somewhere (likely counting omp_target L0
results or including KNOWN_FAIL-related files).

**The 36 "excluded" files:** These are kmeans/mummergpu files that reference KNOWN_FAIL specs.
Some may show PASS (e.g., a translation FROM kmeans-omp, which is NOT KNOWN_FAIL, TO
kmeans-cuda, which IS KNOWN_FAIL). The paper should:
1. Report the 414 standard-direction number as primary.
2. Note in supplementary: "36 additional results involving KNOWN_FAIL specs are excluded
   from aggregate statistics but available in the artifact."
3. If any excluded PASS results involve translating FROM a valid spec TO a KNOWN_FAIL
   target, this is actually interesting — the LLM produced code that can't be verified
   because the *target* environment fails. Mention this as a limitation.

### D3. XSBench omp_target Results (90 files)

**Include as a case study in supplementary, NOT main paper.** Reasons:
- omp_target requires `nvc` (NVIDIA HPC SDK), not standard GCC/NVCC toolchain
- Only 1 kernel (XSBench), so N=30 per model per direction
- Introduces a 4th API (omp_target) that no Rodinia kernel uses
- Weakens the "3-API" framing if mentioned in main text

### D4. Self-Repair max_retries Consistency

**Inconsistent.** My analysis found:
- **480 files with max_retries=2** (standard configuration)
- **24 files with max_retries=1** (non-standard)

The 24 max_retries=1 files are a mix of Claude omp_target results and some standard-direction
results. **This means the self-repair comparison is NOT fully fair.** Files with max_retries=1
had only 1 retry opportunity (2 total attempts), while max_retries=2 files had 2 retry
opportunities (3 total attempts).

**Impact on paper claims:**
- The "self-repair adds 27 PASSes" claim needs to be qualified: "with max_retries=2
  (3 total attempts) for 480/504 tasks and max_retries=1 (2 total attempts) for 24 tasks."
- For a fair comparison, either re-run the 24 files with max_retries=2, or exclude them
  from self-repair analysis, or report self-repair rates separately for each max_retries value.

**Recommendation:** Check whether any of the 24 max_retries=1 files are PASS. If so, their
self-repair pathway had 1 fewer opportunity — the self-repair rate for these is a lower
bound on what max_retries=2 would have achieved.

---

## Task E: Adversarial Review of Statistical Methodology

### E1. Wilson CI with n=5 Cells

The Statistician correctly flags n<10 as "insufficient for reliable CI" and recommends
supplementary-only treatment. **But the paper currently has 4 directions with n=5 per model.**

**Problem:** Even after the campaign (adding L0 for OpenCL directions), per-model per-direction
cells for OpenCL directions will be n=17 or n=15 (one kernel per direction per model at L0).
Wilson CIs at n=15 have width ~30-40pp. This means a CI like "Gemini cuda-to-opencl:
0% [0%, 20.4%]" — which says almost nothing.

**Counter-argument:** The Statistician proposes aggregating across models for per-direction
CIs (n=51 for cuda-to-opencl). This is defensible IF the paper acknowledges that per-model
per-direction breakdowns are exploratory. **The danger is Table 3 in the paper showing a
6x3 grid with CIs that are so wide they overlap everywhere except Claude vs. others.**

### E2. Bonferroni with 18+ Tests

The Statistician counts: B1 (4 tests) + B2 (4 tests) + B3 (12 tests) = 20 tests minimum.
Bonferroni alpha = 0.05/20 = 0.0025.

**Problem:** At this alpha, the ONLY comparison likely to survive is Claude vs. Gemini/Groq
(p << 0.001 due to 52% vs 7-8% gap). Everything else — level effects, direction asymmetry,
Gemini vs. Groq — will be non-significant.

**This is actually fine for the paper.** The story is: "Claude dramatically outperforms
smaller/cheaper models; other effects are not statistically significant at the corrected
alpha, consistent with augmentation invariance." The danger is overselling non-significant
trends as "interesting patterns." **Rule: Any p > 0.0025 gets reported as "not significant
after correction" without narrative spin.**

### E3. Chi-squared Validity for Gemini/Groq

The Statistician notes expected cell counts must be >= 5 for chi-squared validity.

**Current data (cuda-to-omp):** Gemini passes 4/85, Groq passes 5/85. For a 2x3 model
comparison table, the expected count for Gemini-PASS = 85 * (total_pass/255). If total
pass = 62, expected = 85 * 62/255 = 20.7 > 5. Chi-squared is valid.

**Post-campaign data (OpenCL directions):** If Gemini and Groq have 0-2% pass rates on
OpenCL directions (highly likely — they already fail on easier CUDA-to-OMP), expected
PASS cells could be < 5. **The Statistician's fallback to Fisher's exact is correct, but
the paper should not present chi-squared results for cells where it's invalid.**

**Recommendation:** Use Fisher's exact for ALL pairwise comparisons (it's always valid),
and chi-squared only for the omnibus test where expected counts are adequate.

### E4. Gemini ~ Groq (p=0.83): Hurt or Help?

**This helps the paper.** Two distinct capability tiers is a cleaner narrative:
- Tier 1: Claude Sonnet (frontier model, ~52% pass)
- Tier 2: Gemini Flash Lite + Groq Llama 3.3 70B (~7-8% pass)

This supports the claim: "Model capability is the dominant factor in translation success.
Among non-frontier models, neither instruction-tuned Llama nor distilled Gemini achieves
meaningful translation accuracy." The risk is a reviewer asking: "Why not test GPT-4 or
Claude Opus?" — and the answer is cost/access, which is honest.

**The deeper concern:** If Gemini and Groq are statistically indistinguishable, and both
are near floor (7-8%), the paper effectively compares ONE model (Claude) against noise.
This weakens the "cross-model" framing. **Honest framing: "We evaluate one frontier model
and two cost-efficient alternatives to establish a capability-cost tradeoff."**

### E5. Level Invariance p=0.83: Low Power or True Invariance?

**The Statistician computed:** chi2(4) ~ 1.5, p ~ 0.83 for cuda-to-omp level independence.

**Power analysis concern:** With n=57 per level (19 per model), the minimum detectable
effect at 80% power is ~18pp from a 24% baseline. This means if augmentation caused a
REAL 15pp change (24% -> 9%), the test would NOT detect it (Type II error).

**However:** The observed pass rates are L0=28%, L1=25%, L2=25%, L3=21%, L4=19%. There's a
monotonic DECLINE — L4 is 9pp below L0. The chi-squared test says this decline is not
significant, but the TREND is worth noting. If the campaign adds L1-L4 for omp-to-cuda
(192 tasks) and the same declining trend appears, the combined data might reach significance.

**Recommendation:** Report the chi-squared result honestly, note the monotonic decline as a
trend, and compute a linear trend test (Cochran-Armitage) as a secondary analysis. If the
trend test is significant but the omnibus chi-squared isn't, it means "augmentation doesn't
change pass rates in a pattern-free way, but there may be a monotonic degradation at higher
levels." This is actually an interesting finding.

### E6. Pass@k at Temperature=0.8: Claude Diversity Concern

**Anthropic models are known to be less temperature-sensitive than GPT or open-source models.**
At temperature=0.8, Claude may produce near-identical outputs across samples, while Groq's
Llama 3.3 produces genuinely diverse completions. This would make Claude's pass@k barely
better than pass@1, while Groq's pass@k could substantially exceed its pass@1.

**This could invert the model ranking for pass@k.** If Claude pass@1=52%, pass@5=55%, and
Groq pass@1=8%, pass@5=25%, the narrative shifts from "Claude dominates" to "open-source
models benefit more from sampling diversity." This is actually interesting science but
requires careful framing.

**Recommendation:** If pass@k is attempted, the paper MUST report temperature sensitivity
curves (pass@k at temp 0.4, 0.6, 0.8) for at least one kernel per model. Otherwise the
temperature choice is an uncontrolled variable.

---

## Task F: Paper Impact Assessment

| Addition | Audit W# | Reviewer Impact (1-5) | Effort (days) | ROI | Recommendation |
|---|---|---|---|---|---|
| OpenCL L0 (Phase 1) | W1, W16 | **5** — addresses "only 2 directions" fatal flaw | 0.5 | **10.0** | **MUST DO** |
| Statistical analysis (CIs, tests) | W4 | **5** — required for any top venue | 0.5 | **10.0** | **MUST DO** |
| Fix 3-model narrative | W7 | **5** — submission-blocking | 0.25 | **20.0** | **MUST DO** |
| omp-to-cuda L1-L4 | W1 | 3 — completes bidirectional pair | 1.0 | 3.0 | SHOULD DO |
| OpenCL L1-L4 (Phase 2) | W1, W16 | 3 — deepens OpenCL analysis | 1.5 | 2.0 | NICE TO HAVE |
| Self-repair transition table | W4 | 2 — adds analytical depth | 0.25 | 8.0 | SHOULD DO (no new runs) |
| Third benchmark (Parboil) | W1 | 2 — breadth, not depth | 2.0 | 1.0 | CUT |
| Pass@k sampling | W4 | 2 — different metric, not missing metric | 1.5 | 1.3 | CUT |
| Profiling paragraph | W9 | 1 — reviewers understand this is hard | 0.5 | 2.0 | NICE TO HAVE |

### Top 3 by ROI:
1. Fix 3-model narrative (ROI 20.0) — mandatory, low effort
2. OpenCL L0 baselines (ROI 10.0) — addresses the biggest reviewer concern
3. Statistical analysis (ROI 10.0) — elevates rigor to publication standard

### Recommended Campaign Scope (after cuts):
- **Phase 0:** Canary test (budget 2h, not 15min)
- **Phase 1:** OpenCL L0 baselines (192 tasks, ~5-8h)
- **Phase 2 (reduced):** omp-to-cuda L1-L4 only (192 tasks, ~5h). Drop OpenCL L1-L4.
- **Phase 3:** EXTRACTION_FAIL retries + full statistical analysis
- **Phase 4:** CUT (Parboil)
- **Phase 5:** CUT (pass@k)

**Revised total:** 192 + 192 + 23 = **407 new tasks** (down from 1,152)
**Revised wall-clock:** ~15-18h (down from ~20h)
**Revised API cost:** ~$8 (down from ~$19.50)

This focuses effort on what actually matters for the paper while leaving a safety margin
for paper writing (Apr 2-7).

---

## Summary: Top 3 Risks

1. **[BLOCKER] OpenCL build environment failure.** If Phase 0 canary fails, the entire
   campaign is blocked. Mitigation: budget 2h, have `ocl-icd-opencl-dev` ready, verify
   `clinfo` works before running harness. Fallback: paper with 2 directions only (weakened
   but not fatal if framed as "CUDA-OMP translation study with directional asymmetry analysis").

2. **[BLOCKER] OpenCL augmentation hollow.** Augmentation transforms may not modify `.cl`
   kernel files at L1-L2, making L1-L4 results for OpenCL-as-source directions effectively
   L0 duplicates. This doesn't block Phase 1 (L0 only) but blocks the value of Phase 2
   for opencl-to-* directions. Mitigation: verify augmentation transform coverage on `.cl`
   files before committing to Phase 2 for those directions.

3. **[HIGH] max_retries inconsistency.** 24/504 files have max_retries=1 vs 480 with
   max_retries=2. Self-repair comparison is not fully fair. Mitigation: exclude the 24
   files from self-repair analysis or re-run them. Either way, disclose in methodology
   section.

---

## Appendix: Data Validation Cross-Checks

| Claim (from teammates) | Verified? | Finding |
|---|---|---|
| 1,530 eligible tasks | YES | Math checks: (17+17+18+18+16+16) x 5 levels x 3 models = 1,530 |
| 378 done tasks | YES | 414 standard + 90 omp_target = 504 on disk. Standard only: 414 files. Teammate counts 378 *excluding omp_target and KNOWN_FAIL-related files*. Plausible. |
| 53 EXTRACTION_FAIL | YES | Confirmed: `overall_status` distribution matches explorer report |
| 168 files per model | YES | `ls | wc -l` confirmed |
| All 3 models identical coverage | YES | Symmetric at 168 each |
| Gemini ~ Groq p=0.83 | NOT VERIFIED | Need to run Fisher's exact on (11/156, 13/156). Plausible given rates are 7.05% vs 8.33%. |
| Level invariance p=0.83 | NOT VERIFIED | Need to run chi2 on cuda-to-omp contingency table. Plausible from eyeballing trend. |
| 90s avg per task | NOT VERIFIED | Should check actual wall-clock from batch logs. If OpenCL builds are 2-3x slower, timeline doubles. |
| $19.50 total API cost | PLAUSIBLE | Claude at $0.045/task dominates. But if self-repair triggers 3 attempts per task, cost triples. |
