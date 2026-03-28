# Plan: SC26 Paper Audit Agent Team

## Context

ParBench is targeting an SC26 main track submission. The paper draft exists but needs updating
with latest data. Key concern: "only 17 kernels" when evals were run for both Rodinia (60 specs)
and XSBench (4 specs). Need to reconcile what data exists, what's missing, what claims are
supportable, and what tasks remain to strengthen the paper.

## Approach: Create a 4-Teammate Agent Team

Use the experimental Agent Teams feature (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) to spawn
a coordinated team. All teammates use Opus with ultrathink/extended thinking on high.

---

### Teammate 1: "search-planner" (Coordinator)

**Role:** Plan and coordinate the search strategy. Reads high-level project docs first,
then directs the other teammates toward specific files and areas.

**Prompt:**
You are the search coordinator for a comprehensive SC26 paper audit. Use ultrathink.

Your job:
1. Read these files FIRST to build the big picture:
   - docs/ — paper outline, sprint plan, any planning docs
   - docs/session_plans/ — all session plan files
   - .claude/rules/known-issues.md
   - CLAUDE.md (project overview)
   - config/paths.json
   - manifest.jsonl (count entries per suite)

2. From these, build a map of:
   - What sessions were planned vs completed
   - What evals/augmentations were planned but not yet run
   - The full intended scope of the paper vs what's been executed
   - Any session plans that reference future eval runs or augmentation experiments

3. Share your findings with teammates so they know where to look.

4. Synthesize all teammate findings into a single structured report:
   - DONE: tasks/data completed
   - NOT DONE: planned but unexecuted tasks
   - GAPS: things needed for the paper that were never planned
   - NEXT STEPS: prioritized list of tasks to strengthen the paper

Key question to answer: Why does the paper reference only 17 kernels when Rodinia has
60 specs and XSBench has 4? Where is the disconnect?

Do NOT make conclusions without data. Read files. Count entries. Verify claims.

---

### Teammate 2: "data-explorer" (Eval & Augmentation Data Auditor)

**Role:** Exhaustively inventory all result data on disk. Count everything.

**Prompt:**
You are the data auditor for a ParBench SC26 paper audit. Use ultrathink.

Exhaustively inventory ALL evaluation and augmentation data on disk:

1. results/evaluation/ — for EACH subdirectory:
   - Count total JSON files
   - List unique kernels (extract from filenames)
   - List unique directions (cuda-to-omp, omp-to-cuda, etc.)
   - List augmentation levels present (L0, L1, L2, L3, L4)
   - Count PASS vs BUILD_FAIL vs RUN_FAIL vs VERIFY_FAIL (read overall_status from JSONs)
   - Note which models have data

2. results/augmentation/ — for EACH file:
   - What levels were tested?
   - How many specs passed/failed per level?
   - Is augmentation data available for XSBench or only Rodinia?

3. results/phase3/, results/phase5/ — baseline data
   - What exists here?

4. scripts/analysis/ and analysis/ — any generated summaries
   - Read eval_summary.json, any CSV files, reports

5. Build a COMPLETE data inventory table:
   | Suite | Kernel | API | Directions Evaluated | Aug Levels | Models |

6. Answer precisely:
   - How many UNIQUE kernels have L0 eval data?
   - How many have augmented (L1-L4) eval data?
   - Which Rodinia kernels have NO eval data at all?
   - Does XSBench have eval data beyond baseline verification?
   - What is the total result file count per model?

Share your inventory with all teammates. Be precise — count files, don't estimate.

---

### Teammate 3: "git-explorer" (Commit History & Task Auditor)

**Role:** Trace the project's execution history through git commits and task artifacts.

**Prompt:**
You are the git/task auditor for a ParBench SC26 paper audit. Use ultrathink.

Trace what has actually been done vs what was planned:

1. Run `git log --oneline -100` to see recent commit history
   - Categorize commits by type: eval runs, spec fixes, paper work, infrastructure
   - Identify the last eval batch run (date, scope)
   - Identify any data-generating commits

2. Read ALL session plan files in docs/session_plans/:
   - For each: what was the objective? Was it completed? How do you know?
   - Which sessions planned eval runs? Which directions/models/levels?
   - Which sessions planned augmentation experiments?
   - Are there sessions planned but not yet executed?

3. Read the sprint plan (look in docs/ for sprint_plan.md or similar):
   - What milestones exist?
   - Which are marked complete vs blocked vs todo?
   - What's the critical path to paper submission?

4. Check for any TODO files, tracking docs, or incomplete work markers:
   - grep for TODO, FIXME, INCOMPLETE across docs/
   - Check visualizations/sprint_dashboard.html for task statuses

5. Build a timeline:
   - When were eval batches run?
   - When was the paper draft last updated?
   - What's the gap between latest data and latest draft?

Share your timeline and completion audit with all teammates.

---

### Teammate 4: "sc26-reviewer" (Adversarial Paper Reviewer)

**Role:** Act as a rigorous SC26 main track reviewer. Critique the current paper state.

**Prompt:**
You are an adversarial SC26 main track paper reviewer. Use ultrathink.

Your job is to honestly critique the ParBench paper and identify what's needed for acceptance.

1. Read the paper outline/draft (check docs/ for paper outline, any .tex or .md drafts)
2. Read the actual data summaries from your teammates' findings
3. Search the web for:
   - SC26 main track submission requirements and evaluation criteria
   - Related work: SWE-bench, HumanEval, TransCoder, OMPify, HPCorpus, VibeCodeHPC,
     CodeBERT, PLBART, any LLM-for-HPC papers from SC24/SC25
   - Best practices for benchmark papers in HPC venues
   - Statistical methodology for evaluating LLM code generation

4. Write a structured review:

   **Summary:**
   What the paper claims to contribute.

   **Strengths:**
   What's solid and publishable.

   **Weaknesses (be brutal but constructive):**
   - Missing baselines or comparisons
   - Statistical rigor issues (no confidence intervals? no effect sizes?)
   - Kernel count concerns (17 vs potential 57+)
   - Missing augmentation-level eval data
   - Related work gaps
   - Reproducibility concerns
   - Threat to validity gaps

   **Required Revisions for Accept:**
   Prioritized list of what MUST change for SC26 main track acceptance.

   **Suggested Improvements:**
   Nice-to-haves that would strengthen the paper.

   **Missing Claims / Unsupported Claims:**
   What the paper says vs what the data actually supports.

5. For each weakness, provide a SPECIFIC, ACTIONABLE fix — not vague advice.

Share your review with all teammates, especially the search-planner for synthesis.

---

## Team Creation Command

After exiting plan mode, execute:

Create a team called "sc26-audit" with 4 teammates. All teammates MUST use Opus with
ultrathink and extended thinking on high. Require plan approval before implementation.

**Teammates:**
1. "search-planner" — Coordinator who reads project docs, session plans, and synthesizes
2. "data-explorer" — Exhaustive inventory of all eval/augmentation result data on disk
3. "git-explorer" — Git history and task completion audit
4. "sc26-reviewer" — Adversarial SC26 main track paper reviewer with web search

[Insert full prompts from plan above]

**Coordination flow:**
- search-planner reads high-level docs first, shares map with others
- data-explorer and git-explorer work in parallel on their respective areas
- sc26-reviewer waits for findings from others before writing the review
- search-planner synthesizes all findings into a final prioritized action plan

**Key questions to answer:**
1. Why only 17 kernels in the paper when 60+ specs exist?
2. What eval data is missing (augmentation levels, directions, models)?
3. What claims can we make vs cannot make with current data?
4. What are the top 5 tasks to strengthen the paper for SC26 main track?
5. What related work is missing?
6. What statistical tests are needed?

Report all findings to me (Samyak) for decision-making. Do NOT make implementation
decisions — present options with tradeoffs.

## Fallback: If Agent Teams Unavailable

If the experimental Agent Teams feature is not enabled or fails to spawn, fall back to
4 parallel subagents (general-purpose, Opus, with the same prompts). The tradeoff:
subagents can't communicate with each other, so the synthesis step would need to happen
in the main context after all 4 return.

Check CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 in settings.json first. If not set,
ask the user whether to:
(a) Enable it and proceed with agent teams
(b) Fall back to parallel subagents with main-context synthesis

## Verification

The team's output should be a structured report containing:
- Complete data inventory (file counts, kernels, models, directions, levels)
- Session completion audit (planned vs executed)
- Gap analysis (what's missing for the paper)
- SC26 reviewer critique with specific actionable fixes
- Prioritized task list for next steps
- Claims matrix (supportable vs unsupportable)

I (Samyak) review all findings before any implementation decisions are made.

## Context Management

- Each teammate reads only their assigned area — no overlap
- Teammates share summaries, not raw file contents
- search-planner synthesizes — avoids context duplication in main window
- Kill teammates as soon as they finish their section
- Total expected cost: ~4x single Opus session (4 teammates)

---

> **Insight: Agent Teams vs. Subagents**
>
> This is an ideal use case for Agent Teams rather than simple subagents. The key difference: teammates maintain persistent context windows and can communicate bidirectionally via SendMessage. The sc26-reviewer needs findings from data-explorer and git-explorer before writing its review — that cross-agent dependency is exactly what teams enable. With subagents, we'd lose that coordination and have to synthesize everything in the main context window.

## Execution Status

| Teammate | Task | Status |
|---|---|---|
| search-planner | #1: Read project docs, build big picture map | Running |
| data-explorer | #2: Inventory all eval/augmentation data | Running |
| git-explorer | #3: Audit git history & session completion | Running |
| sc26-reviewer | #4: Adversarial paper review (blocked until #2, #3 done) | Running (reading paper draft + web search while waiting) |

Task #5 (final synthesis) is blocked until all 4 complete — search-planner will claim it.

> **Insight: Coordination Pattern — Pipeline with Parallel Fan-Out**
>
> The team structure mirrors a classic dataflow graph. Tasks 1, 2, 3 execute in parallel (fan-out), task 4 joins on 2+3 (partial barrier), and task 5 joins on all (full barrier). This is the same pattern as MapReduce or MPI collective operations — maximize parallelism in the independent exploration phase, then synchronize only when cross-cutting analysis requires combined data. The sc26-reviewer starts its web search work immediately (no data dependency for related work lookup) while waiting for the data-dependent parts.
>
> Why Agent Teams here, not subagents: Subagents would each return a summary to me, consuming ~4x the main context window. With Agent Teams, teammates share findings with each other via SendMessage, and only the final synthesized report comes back — keeping the main context lean for decision-making.

The teammates will message each other as they complete their tasks. I'll relay findings to you as they come in. This typically takes 5-15 minutes for a team of this size working through the full codebase.

## Teammate Reports

- **@search-planner:** Big picture map from project docs, session plans, and data inventory
- **@search-planner:** CRITICAL: Paper draft has stale 4-model data, contradicts actual 3-model results
- **@git-explorer:** Git history and session completion audit (Task #3)
- **@data-explorer:** Complete eval and augmentation data inventory
- **@search-planner:** VERIFY_FAIL zero claim is confirmed false — 45 actual VERIFY_FAIL

---

## Interim Findings Summary

### The "17 Kernels" Question — Answered

- 22 unique Rodinia kernels exist in specs
- 18 have both CUDA + OMP variants (needed for cuda-to-omp)
- 2 of those are KNOWN_FAIL (kmeans, mummergpu) → excluded
- 16 Rodinia + 1 XSBench = 17 kernels in eval_summary
- 4 Rodinia kernels (dwt2d, gaussian, huffman, hybridsort) have no OMP spec → never evaluated
- 120 HeCBench specs exist but were never evaluated (not cloned locally)

### CRITICAL: Paper Has Stale/False Data

Three categories of data integrity issues:

| Issue | Paper Claims | Actual Data |
|---|---|---|
| Models | "Four LLMs" including GPT-4.1 | 3 models, GPT-4.1 has zero files on disk |
| Task count | "500 evaluated tasks" | 468 (eval_summary) or 504 (raw) |
| VERIFY_FAIL | "Zero across all tasks" (called "most important result") | 45 VERIFY_FAIL (9.62%) |
| Claude pass rate | 70.6% | 51.92% |
| GPT-4.1 pass rate | 52.9% | N/A — deleted |
| BUILD_FAIL share | "68.4% of failures (26/38)" | 38.46% of all tasks |

The "zero VERIFY_FAIL" claim is the most dangerous — the entire Discussion section and Conclusion are built on it.

### Data Inventory (504 files)

- 168 per model × 3 models
- Rodinia: 2 directions (cuda-to-omp at L0-L4, omp-to-cuda at L0 only)
- XSBench: all 12 directions × 5 levels
- 10 of 12 directions have only 1 kernel (XSBench)
- Augmentation level-invariance confirmed at 54/60 for Rodinia

### 11 Days to Deadline (April 8)

Critical path blockers: no LaTeX paper, no anonymous repo, sections 1-2 unfinished, stale numbers throughout draft.

---

Waiting for sc26-reviewer to complete the adversarial review (Task #4), then search-planner will synthesize everything into the final action plan (Task #5).

Data-explorer and git-explorer are idle waiting for shutdown confirmation. Let me re-send the shutdown requests more explicitly.

Shutdown messages sent. Still waiting on sc26-reviewer (Task #4) to complete the adversarial paper review. Once that's done, search-planner will claim Task #5 and produce the final synthesis.

The sc26-reviewer is doing the most complex work — reading the paper draft, searching the web for SC26 requirements and related work, and incorporating all the data findings into a structured review. This typically takes longer than the data-gathering tasks.

## Additional Teammate Reports

- **@data-explorer:** Ground truth L0 cuda-to-omp numbers for paper rewrite
- **@sc26-reviewer:** Complete adversarial SC26 paper review

Excellent — the sc26-reviewer has delivered a thorough adversarial review. Data-explorer has shut down. Let me update tasks and get the synthesis going.

Task #4 complete, sc26-reviewer shutting down. search-planner is now working on Task #5 — the final synthesis.

> **Insight: The "Zero VERIFY_FAIL" Collapse — A Cautionary Tale in Research Data Integrity**
>
> This audit revealed that the paper's marquee finding ("zero VERIFY_FAIL") was true for an early 68-task pilot but false for the full 468-task dataset. This is a classic scope creep of claims — a finding from a restricted dataset gets propagated into sections written about the expanded dataset without re-verification. In research methodology, this is called a compositional validity threat: a result valid at one scope being incorrectly generalized. The fix isn't to panic — BUILD_FAIL is still dominant (49.6% of failures) and VERIFY_FAIL is still relatively low (9.62%) — but the narrative must be reframed from "zero" to "low but non-zero," which is still an interesting and publishable finding. The lesson: every time a dataset expands, re-derive all claims from scratch.
>
> **The 4-Model → 3-Model Stale Data Problem:** This is the same class of error — GPT-4.1 was dropped on Day 7 of the sprint, but the paper draft was only partially updated. Every quantitative claim in the draft needs to be traced back to eval_summary.json or raw result files. This is why the facts_sheet_s_verify.md document exists as a single source of truth — but the paper draft diverged from it.

Waiting for search-planner's final synthesis (Task #5). Current team status:

| Teammate | Status |
|---|---|
| search-planner | Working on Task #5 (synthesis) |
| data-explorer | Shut down |
| git-explorer | Shutting down |
| sc26-reviewer | Shutting down |

## Late Teammate Reports

- **@git-explorer:** Verified: paper_draft.md has pervasive 4-model stale data
- **@sc26-reviewer:** Acknowledge data, note sharpened findings

Good — sc26-reviewer, git-explorer, and data-explorer are all shut down. Only search-planner remains, working on the final synthesis (Task #5).

The additional findings sharpen the picture:

- 40-60 lines in paper_draft.md need rewriting (7-9% of the paper) — all quantitative claims in S1, S6, abstract
- Direction coverage is thinner than it appears: only 2 of 12 directions have multi-kernel data
- Three competing task counts (504/468/500) need resolution to ONE authoritative number
- No LaTeX — converting from Markdown to IEEE format is itself 2-3 days of work

The team is converging nicely. search-planner will now synthesize all of this into the final prioritized action plan with options and tradeoffs for your decision-making.

- **@search-planner:** TASK #5 COMPLETE: Final synthesized audit report with prioritized action plan

search-planner has delivered the final synthesis. Let me close out the team.

All teammates have reported and are shutting down. Here is the complete audit delivered to you.

---

## SC26 Paper Audit — Complete Report

### Team Results

All 5 tasks completed across 4 teammates (~12 minutes total):

| Teammate | Task | Key Finding |
|---|---|---|
| search-planner | Docs + synthesis | 17-kernel question answered; 10 sessions not started; critical path mapped |
| data-explorer | Data inventory | 504 files, 3 models, 19 kernels; ground truth numbers extracted |
| git-explorer | Git audit | Session timeline; stale data scope (40-60 lines); root cause traced |
| sc26-reviewer | Adversarial review | MAJOR REVISION (borderline reject as-is); 3 blocking, 3 high, 3 medium issues |

---

### The Three Fatal Findings

#### 1. Every Quantitative Claim in the Paper Is Wrong

The paper draft uses 4-model pilot data (GPT-4.1 + 3 others, 68 tasks). Actual data: 3 models, 468 tasks. 82+ instances of stale numbers across abstract, S1, S6-S8.

| Claim | Paper Says | Actual |
|---|---|---|
| Models | 4 (incl. GPT-4.1) | 3 (GPT-4.1 has zero files on disk) |
| Tasks | 500 | 468 |
| Claude PASS | 70.6% | 51.92% (all) / 56.2% (L0 cuda-to-omp) |
| Aggregate | 44.1% | 22.44% |
| VERIFY_FAIL | Zero ("most important result") | 45 (9.62%) |

#### 2. Direction Coverage Is Thinner Than Claimed

"12 translation directions" — but 10 of those have only 1 kernel (XSBench). Only cuda-to-omp and omp-to-cuda have multi-kernel Rodinia data.

#### 3. 120 HeCBench Specs Exist but Were Never Evaluated

Paper says "184 specs across 3 suites" but only 64 are evaluated. HeCBench isn't even cloned locally.

---

### What You CAN Claim (Supportable)

- Build-run-verify kernel-centric framework with 64 evaluated specs (Rodinia + XSBench)
- 468 evaluated tasks across 3 models, 12 directions, 5 augmentation levels
- BUILD_FAIL is the dominant failure mode (~38% of all tasks, ~50% of failures)
- VERIFY_FAIL is the least common failure mode (9.62%) — not zero, but still low
- Claude Sonnet dramatically outperforms Gemini Flash-Lite and Groq Llama (51.92% vs 7-8%)
- Augmentation is level-invariant for the Rodinia harness baseline (54/60 PASS at all L1-L4)
- Cross-direction asymmetry: CUDA-to-OMP is easier than OMP-to-CUDA (+18.8pp)
- AST-driven augmentation engine with 6 transforms is methodologically novel

### What You CANNOT Claim (Unsupported)

- "Zero VERIFY_FAIL" — false
- "4 LLMs" / "500 tasks" — stale
- "184 specs evaluated" — only 64 evaluated
- "Level-invariant augmentation for LLM eval" — no statistical test (range 19-25% could be noise)
- Performance/speedup claims — no timing data
- Generalization across 12 directions — 10 directions have N=1 kernel

---

### Prioritized Action Plan (11 days to April 8)

#### IMMEDIATE (Days 11-12: Today-Tomorrow)

| # | Task | Effort | Blocks |
|---|---|---|---|
| 1 | Numerical audit of paper_draft.md — fix all stale 4-model data, kill "zero VERIFY_FAIL" | 4-6h | Everything |
| 2 | S-DEPS — requirements.txt, pyproject.toml | 30min | Artifact eval |
| 3 | W-S16 — Anonymous GitHub repo | 4h | Submission |

#### SHORT-TERM (Days 13-15)

| # | Task | Effort | Blocks |
|---|---|---|---|
| 4 | S12 — Write Intro + Related Work (read Paraval first) | 1 day | LaTeX |
| 5 | S-TAXONOMY — Error taxonomy for BUILD_FAIL subcategories | 3h | Paper quality |
| 6 | Reframe claims — honest scoping of directions + HeCBench | 2h | Paper integrity |
| 7 | Merge draft files — single coherent Markdown | 1h | LaTeX |

#### MEDIUM-TERM (Days 15-17)

| # | Task | Effort | Blocks |
|---|---|---|---|
| 8 | W-S17 — LaTeX conversion (CRITICAL PATH BOTTLENECK) | 2-3 days | Submission |
| 9 | S-BIB — Expand bibliography (15→30+ refs) | 2h | Paper quality |

#### FINAL (Days 19-21)

| # | Task | Effort |
|---|---|---|
| 10 | W-S15 — Full paper review | 4h |
| 11 | S18 — Co-author review + submit | 2-3 days |

#### Explicitly Deferred

- S10/S10b (OpenCL direction evals) — nice-to-have, not achievable
- S-TIMING (kernel performance) — framed as future work
- HeCBench evaluation — future work
- 4th model addition — sc26-reviewer recommends it but timeline is tight

---

### Critical Path

```
Mar 28-29:  Numerical audit + S-DEPS + W-S16 (anonymous repo)
     ↓
Mar 30-31:  S12 (Intro + Related Work) + S-TAXONOMY + claim reframing
     ↓
Apr 1:      Merge drafts → finalized Markdown
     ↓
Apr 1-3:    W-S17 (LaTeX conversion) ← BOTTLENECK
     ↓
Apr 4-5:    W-S15 (paper review) + S-BIB
     ↓
Apr 5-8:    S18 (co-author review + submit)
```

Single biggest risk: If the paper draft isn't finalized by April 1, LaTeX conversion starts late, compresses the review cycle, and risks a rushed submission.

---

> **Insight: Research Data Pipeline Integrity — The "Stale Propagation" Anti-Pattern**
>
> This audit uncovered a systemic problem that affects many research projects: when a dataset expands (68→468 tasks) or a variable changes (4→3 models), claims derived from the old data propagate into new sections because authors copy-paste or write from memory rather than re-deriving from the data source. The fix is to establish a single source of truth (here, eval_summary.json and facts_sheet_s_verify.md) and enforce that every quantitative claim in the paper can be traced back to a specific query on that source. This is the same principle as database normalization — don't store derived values, compute them from the canonical source. For the SC26 paper, this means the numerical audit (Task #1) should produce a "claims verification table" mapping every number in the paper to its source query, so future edits can be mechanically re-verified.
>
> **Agent Teams for Research Audits:** This 4-teammate audit completed in ~12 minutes what would have taken 2-3 hours of sequential work in a single context window. The key was the fan-out/join pattern: 3 independent data-gathering tasks in parallel, followed by a synthesis task. The sc26-reviewer's web search for related work (UniPar, HPC-Coder) happened concurrently with the data inventory — no sequential bottleneck. This pattern is directly applicable to any pre-submission paper review.

---

## SC26 Paper Audit Complete

- **@search-planner:** FINAL SYNTHESIS: Complete audit findings with prioritized action plan and tradeoffs

The 4-agent team has finished. Here's your decision-ready summary:

### Verdict: MAJOR REVISION (Borderline Reject As-Is)

The paper has a strong core (kernel-centric design, augmentation engine, failure taxonomy) but the draft is unpublishable in its current state due to stale data.

### Three Things That Must Happen First

1. **Numerical Audit (4-6h)** — 82+ stale references to 4 models/GPT-4.1/zero-VERIFY_FAIL. Every number in the abstract, S1, S6-S8 is wrong. This unblocks everything.
2. **Scope Reframing (2-3h)** — Honestly present "17 kernels evaluated, 64 specs curated, 184 in framework." Distinguish 2 multi-kernel directions from 10 single-kernel XSBench case studies.
3. **LaTeX Conversion (2-3 days)** — No .tex file exists. This is the critical path bottleneck. Must start by April 1 at latest.

### Your Decisions Needed

1. **Start the numerical audit now?** This is the single highest-leverage task — nothing else matters until the draft matches reality.
2. **Add a 4th model?** sc26-reviewer says the 3-model set (1 strong + 2 weak) looks like "a Claude press release." Adding GPT-4o or DeepSeek-V3 would strengthen the paper but costs ~1 day GPU time. Worth it?
3. **Run S10 (cuda-to-opencl)?** Adds a 3rd multi-kernel Rodinia direction. Nice-to-have but 1 day GPU time. Defer?
4. **Statistical tests?** Bootstrap CIs + Fisher's exact test = ~4h implementation. The reviewer says "won't reject for this alone at SC venue" but it's standard practice. Include?
5. **HeCBench — drop from claims or evaluate?** The honest path is to drop it from scope claims. Evaluating 120 specs in 11 days isn't realistic.

> **Insight: The "Stale Propagation" Anti-Pattern in Research**
>
> This audit caught a systematic failure mode that plagues research projects: when a dataset expands (68→468 tasks) or a variable changes (4→3 models), claims from the old scope propagate forward into new sections because authors write from memory rather than re-querying the data source. The "zero VERIFY_FAIL" claim was true for the original 68-task L0 pilot, but became false when the dataset grew to 468 tasks — yet the claim was copied into S13's Discussion section verbatim. The preventive fix: establish eval_summary.json as the single source of truth and build a "claims verification table" mapping every paper number to a specific query on that source. This is database normalization applied to scientific writing.
>
> **Agent Teams ROI:** 4 teammates completed in ~15 minutes what would have taken 3-4 hours of sequential analysis. The fan-out (3 parallel data-gatherers) + join (1 synthesizer) pattern maximized throughput. Total cost: ~4x a single Opus session, but the cross-agent communication (sc26-reviewer incorporating data-explorer's ground truth numbers) produced findings that sequential subagents would have missed.

---

## Team Shutdown

All teammates confirmed shut down. Team "sc26-audit" is fully closed.

| Teammate | Status |
|---|---|
| search-planner | Shut down |
| data-explorer | Shut down |
| git-explorer | Shut down |
| sc26-reviewer | Shut down |

The full audit report and prioritized action plan are delivered above. Waiting on your decisions on the 5 questions before proceeding with any implementation work.
=====








● Good. Now let me check if search-planner is still alive and shut it down.

✻ Cooked for 12m 9s

● All teammates shut down. Here's the final consolidated report incorporating the supplemental findings:

  ---
  SC26 Paper Audit — Complete Report

  ★ Insight ─────────────────────────────────────
  Benchmark Paper Credibility: The sc26-reviewer's W14 is perhaps the most important finding: wrong numbers in a benchmark paper destroy credibility. Unlike a systems paper where performance varies with setup, a benchmark paper's entire value
  proposition is rigorous measurement. If a reviewer downloads ParBench, runs eval_summary.json, and finds that the paper says "zero VERIFY_FAIL" when the data shows 45 — that's not a minor discrepancy, it's a falsification flag. The fact-checking
   table (mapping each claim → source file → computation) is a technique from journalism and auditing that should be standard practice for any empirical paper. In ParBench's pipeline architecture, this means treating the paper draft like another
  stage in the pipeline — its inputs (eval_summary.json, result JSONs) must be traceable, just like harness outputs.
  ─────────────────────────────────────────────────

  17 Weaknesses Found (W1-W17), Prioritized into 3 Tiers

  Tier 1: CRITICAL (submission-blocking, do first)

  ┌─────┬─────────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────┬──────────┐
  │  #  │                                  Weakness                                   │                     Fix                      │  Effort  │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W14 │ Factually incorrect numbers (zero VERIFY_FAIL, 68.4% BUILD_FAIL, 500 tasks) │ Audit every number against eval_summary.json │ 4 hrs    │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W7  │ Paper says "4 models" — actual: 3                                           │ Search-replace throughout draft              │ 2 hrs    │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W15 │ No LaTeX paper (only 692-line Markdown)                                     │ Convert to IEEE IEEEtran                     │ 2-3 days │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W2  │ Missing LASSI comparison (80-85% pass rate, direct competitor)              │ Add to §2 + §7 with methodology defense      │ 3 hrs    │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W3  │ Missing CodeRosetta comparison (NeurIPS'24)                                 │ Add to §2 Related Work                       │ 1 hr     │
  ├─────┼─────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────┤
  │ W17 │ No anonymous artifact repo                                                  │ Create via anonymous.4open.science or Zenodo │ 2-4 hrs  │
  └─────┴─────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────┴──────────┘

  Tier 2: MAJOR (strengthen for acceptance)

  ┌─────┬────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┬────────────────┐
  │  #  │                            Weakness                            │                                  Fix                                  │     Effort     │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W4  │ No statistical tests or CIs                                    │ Python script: Wilson CIs, chi-squared, Fisher's exact                │ 3 hrs          │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W8  │ Augmentation confound (L0 has different directions than L1-L4) │ Restrict comparison or add caveat                                     │ 1 hr           │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W1  │ 10/12 directions have N=15 (noise)                             │ Restructure §6.6: primary vs exploratory                              │ 2 hrs          │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W16 │ No Rodinia data for 10/12 directions                           │ Run S10 or restructure claims                                         │ 6 hrs or 2 hrs │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W6  │ IEEE vs ACM template                                           │ Verify SC26 CFP; addressed by LaTeX transfer                          │ 30 min         │
  ├─────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────┼────────────────┤
  │ W10 │ 5 missing related work papers                                  │ Add HPC-Coder-v2, TRACY, QiMeng-MuPa, VibeCodeHPC, SWE-bench Illusion │ 2 hrs          │
  └─────┴────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────┴────────────────┘

  Tier 3: MODERATE (nice-to-have)

  ┌─────┬────────────────────────────────────────────┬──────────────────────────────────────┬───────────────────────────────────┐
  │  #  │                  Weakness                  │                 Fix                  │              Effort               │
  ├─────┼────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
  │ W5  │ Temperature=0 single-seed (no pass@k)      │ Add caveat or run pass@k sampling    │ caveat: 30min, sampling: 1-2 days │
  ├─────┼────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
  │ W9  │ No performance/efficiency data             │ Wall-clock ratios for ~10 PASS cases │ 4 hrs                             │
  ├─────┼────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
  │ W11 │ Rodinia training-data familiarity confound │ Discuss in §7.2 Threats to Validity  │ 30 min                            │
  ├─────┼────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
  │ W12 │ Self-repair breakdown incomplete           │ Add failure-mode transition table    │ 1 hr                              │
  ├─────┼────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────┤
  │ W13 │ XSBench asymmetric reporting               │ Clarify task-count differences       │ 30 min                            │
  └─────┴────────────────────────────────────────────┴──────────────────────────────────────┴───────────────────────────────────┘

  Recommended Schedule (11 days to Apr 8)

  ┌─────┬────────┬────────────────────────────────────────────────────────────────────────┬───────┐
  │ Day │  Date  │                                 Tasks                                  │ Hours │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 1   │ Mar 29 │ W14 (numerical audit) + W7 (3-model fix)                               │ 6 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 2   │ Mar 30 │ W2+W3 (LASSI/CodeRosetta) + W10 (5 papers)                             │ 6 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 3   │ Mar 31 │ W4 (stats script) + W8 (augmentation fix) + W1 (direction restructure) │ 6 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 4   │ Apr 1  │ W15 begins: LaTeX transfer (§3-§5 first)                               │ 8 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 5   │ Apr 2  │ W15 continues: LaTeX (§6-§7, tables, figures)                          │ 8 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 6   │ Apr 3  │ W15 finishes: LaTeX (§1-§2, bibliography, appendix)                    │ 8 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 7   │ Apr 4  │ W17 (anonymous repo) + W16 caveat or S10 eval                          │ 6 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 8   │ Apr 5  │ W-S15: Full paper review + polish                                      │ 8 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤
  │ 9   │ Apr 6  │ Tier 3 fixes (W5, W9, W11, W12, W13) if time                           │ 6 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤                                                                                                                                                    
  │ 10  │ Apr 7  │ Co-author review                                                       │ 4 hrs │
  ├─────┼────────┼────────────────────────────────────────────────────────────────────────┼───────┤                                                                                                                                                    
  │ 11  │ Apr 8  │ S18: Final submit                                                      │ 2 hrs │                                                                                                                                                  
  └─────┴────────┴────────────────────────────────────────────────────────────────────────┴───────┘                                                                                                                                                    
  
  Total estimated: ~68 hours across 11 days. Tight but feasible if LaTeX transfer stays on track.                                                                                                                                                      
                                                                                                                                                                                                                                                     
  Decision Points for You, Samyak                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                     
  1. S10 (Rodinia cuda-to-opencl eval): Run it (~6 hrs) to strengthen "12 directions" claim, or restructure the paper to honestly present 2 primary + 10 exploratory directions? I recommend the restructure — it's faster and more honest.            
  2. IEEE vs ACM: The reviewer flagged that SC26 may use IEEE, not ACM sigconf. Need to verify against the actual CFP before starting LaTeX transfer.                                                                                                
  3. pass@k sampling: Running temperature>0 evaluations would address W5 but costs 1-2 days. Given the timeline, I'd caveat it as future work instead.                                                                                                 
  4. Performance sanity check (W9): Wall-clock ratios for ~10 PASS cases would cost ~4 hours. Worth doing if Day 9 has slack.                                                                                                                          
                                                                                                                                                                                                                                                       
  What would you like to tackle first?                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                       
✻ Worked for 1m 19s                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                       
@search-planner❯ Task #5 complete: Full synthesis report with prioritized action plan
                                                                                                                                                                                                                                                       
● All teammates are shut down. search-planner delivered an outstanding synthesis with a key additional finding I should highlight:                                                                                                                   
                                                                                                                                                                                                                                                     
  ★ Insight ─────────────────────────────────────                                                                                                                                                                                                      
  Per-Model Augmentation Curves — The Hidden Story: The aggregate "level-invariance" claim (19-25% across L0-L4) masks a dramatic per-model divergence:
  - Claude: 52.9% → 47.1% → 47.1% → 41.2% → 52.9% (genuinely flat — robust to augmentation)                                                                                                                                                            
  - Gemini: 17.6% → 17.6% → 17.6% → 11.8% → 0.0% (catastrophic L4 collapse)                                                                                                                                                                            
  - Groq: 17.6% → 11.8% → 11.8% → 11.8% → 5.9% (gradual decline)                                                                                                                                                                                       
                                                                                                                                                                                                                                                       
  This is Simpson's Paradox in action — the aggregate is flat because Claude's stability masks Gemini/Groq's collapse. The disaggregated finding is scientifically more interesting: augmentation robustness discriminates model capability. Claude    
  reasons about parallel structure; Gemini/Groq rely more on surface patterns that augmentation disrupts. This should be the paper's augmentation contribution, not "level-invariance."                                                                
  ─────────────────────────────────────────────────                                                                                                                                                                                                    
                                                                                                                                                                                                                                                       
  ---                                                                                                                                                                                                                                                
  Team "sc26-audit" — COMPLETE                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                       
  All 4 teammates finished, all 5 tasks complete, all teammates shut down.
                                                                                                                                                                                                                                                       
  ┌────────────────┬────────────────────┬─────────────────────────────────────────────────────────┐                                                                                                                                                    
  │    Teammate    │        Task        │                       Key Finding                       │                                                                                                                                                    
  ├────────────────┼────────────────────┼─────────────────────────────────────────────────────────┤                                                                                                                                                    
  │ search-planner │ Big-picture map    │ Stale 4-model data everywhere; "17 kernels" explained   │                                                                                                                                                  
  ├────────────────┼────────────────────┼─────────────────────────────────────────────────────────┤                                                                                                                                                  
  │ data-explorer  │ Data inventory     │ 504 files, 110 PASS, eval_summary excludes 36 files     │                                                                                                                                                    
  ├────────────────┼────────────────────┼─────────────────────────────────────────────────────────┤                                                                                                                                                    
  │ git-explorer   │ Git/session audit  │ 5 sessions not started; 11 days to deadline             │                                                                                                                                                    
  ├────────────────┼────────────────────┼─────────────────────────────────────────────────────────┤                                                                                                                                                    
  │ sc26-reviewer  │ Adversarial review │ 17 weaknesses; MAJOR REVISION verdict; LASSI is #1 risk │                                                                                                                                                  
  └────────────────┴────────────────────┴─────────────────────────────────────────────────────────┘                                                                                                                                                    
                                                                                                                                                                                                                                                     
  The Three Strategic Options                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                     
  Option A (Minimum Viable): Fix stale data → add LASSI/CodeRosetta → stats → LaTeX → submit. No new evals. Lowest risk.                                                                                                                               
    
  Option B (Recommended): Option A + run S10 (cuda-to-opencl) on GPU in background while doing paper work. Adds a 3rd Rodinia direction with minimal distraction.                                                                                      
                                                                                                                                                                                                                                                     
  Option C (Not recommended): Option B + S10b + timing + HeCBench. Too many moving parts for 11 days.                                                                                                                                                  
                                                                                                                                                                                                                                                     
  Your Immediate Decision Points                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                       
  1. IEEE or ACM? Check the SC26 2026 CFP — this determines the entire LaTeX transfer.                                                                                                                                                                 
  2. Option A or B? Run S10 in parallel, or focus purely on paper?                                                                                                                                                                                     
  3. Start the numerical audit today? The 3 false claims (zero VERIFY_FAIL, 4 models, 500 tasks) are the lowest-effort, highest-impact fix.                                                                                                            
                                                                                                                                                                                                                                                       
  The full report with all details, corrections tables, claims matrices, and schedules is captured in the teammate messages above and saved to memory for future sessions. What would you like to tackle first?      