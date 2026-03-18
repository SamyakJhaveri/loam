 Presentation prep as a research skill: Having structured talking points mapped to a live dashboard (rather than static slides) is a powerful technique for research meetings. It lets you:                                                           
  1. Adapt in real-time — skip sections if the audience drills into one area, or show backup data without "going back to slide 14"                                                                                                                     
  2. Show working artifacts — the kanban, charts, and filters are live proof of project management rigor, which builds PI confidence                                                                                                                   
  3. Drive decisions — ending with explicit "Decision Points" (which suite? augmentation timeline? Overleaf?) forces the meeting to produce actionable outcomes rather than vague direction                                                            
                                                                                                                                                                                                                                                       
  This is a pattern from agile sprint reviews that translates well to academic research: demo the working system, then ask for decisions.                                                                                                              
  ─────────────────────────────────────────────────                                                                                                                                                                                                    
                                                                                                                                                                                                                                                       
  Here's a quick prep checklist for tomorrow:                                                                                                                                                                                                          
                                                                                                                                                                                                                                                       
  1. Before the meeting — open the website and verify all pages load (especially sprint_dashboard.html with its new features)                                                                                                                          
  2. Practice the flow — overview (2 min) → LLM eval (5 min) → sprint dashboard (8 min, most time) → augmentation (3 min) → decisions (5 min)                                                                                                        
  3. Key interactive demos — filter the kanban by Week 1, toggle between team members, click a task card to show the modal, show the burndown chart                                                                                                    
  4. Three decisions to get — (1) additional benchmark suite, (2) Erel's L3/L4 fix timeline, (3) Overleaf project/template                                                                                                                             
  5. Have docs/sprint_to_SC26.md open as backup for detailed task breakdowns if asked                                          
  
# SC26 Sprint Presentation — Talking Points

**For:** Research team meeting
**Presenter:** Samyak Jhaveri
**Date:** March 19, 2026 (Sprint Day 2)
**Format:** Live walkthrough of https://samyakjhaveri.github.io/parbench_sam/
**Objective:** Align team on sprint progress, surface blockers, get decisions on open questions

---

## Opening (2 min)

> We're on Day 2 of our 21-day sprint to SC26 paper submission (April 8).
> I'm going to walk through the live dashboard to show where everything stands.
> At the end I have 3 decisions I need from the team.

**Open the website:** https://samyakjhaveri.github.io/parbench_sam/
(Password-protected — enter the shared password)

---

## Page 1: Overview (`overview.html`) — 3 min

**What to show:** The project landing page with high-level architecture.

**Talking points:**

- "ParBench is a meta-benchmark — we don't create new benchmarks, we wrap existing ones (Rodinia, HeCBench) with machine-readable specs that drive automated LLM evaluation."
- "Since February, we've gone from 5 pilot kernels to 185 specs across 2 suites."
- Point out the pipeline: **Specs → Harness → LLM Translation → Build → Run → Verify**
- "The key architectural decision is the two-level metadata system: a lightweight manifest for discovery, and detailed JSON spec files for execution. This means scaling from 5 kernels to 500 requires zero code changes — just new spec files."

**Transition:** "Let me show you the actual evaluation results."

---

## Page 2: LLM Evaluation (`llm_evaluation.html`) — 5 min

**What to show:** The pilot results (cuda→omp, 5 kernels × 2 models).

**Talking points:**

- "This is our pilot: 5 Rodinia kernels translated from CUDA to OpenMP by two LLMs."
- **Pass rate: 50% (5/10)**
  - "Both models pass bfs and nw — these are relatively straightforward translations."
  - "Azure GPT-4.1 also passes hotspot; Claude fails with a missing `#include <cstring>` — a trivial error that iterative repair should fix."
  - "Both models fail srad — the LLM doesn't realize OMP needs an extra `nthreads` argument. This is a genuine translation quality issue."
  - "Both fail backprop — multi-file coordination problems (duplicate function definitions, missing macros)."
- "All remaining failures are LLM quality issues, not infrastructure. We fixed all infrastructure bugs in Phase 1."

**Key insight to emphasize:**
> "The interesting finding is that failure modes cluster into patterns: missing includes (BUILD_FAIL), dropped arguments (RUN_FAIL), multi-file coordination (BUILD_FAIL). These are the patterns we'll categorize in the paper's failure taxonomy."

**Transition:** "Now let me show the sprint plan for scaling this up."

---

## Page 3: Sprint Dashboard (`sprint_dashboard.html`) — 8 min

**This is the main page for the meeting.** Spend the most time here.

### 3a. Stats Row + Countdown (top of page)

- "21-day sprint, we're on Day 2. 22 tasks total, currently [N] done."
- "The countdown shows [X] days to SC26 submission."
- Point out: 185 specs ready, 50% pilot pass rate, 7 open bugs.

### 3b. Progress Bars

- "Week 1 is scale-up: smoke test all OMP specs, full Rodinia evaluation."
- "Week 2 is expansion: HeCBench clone, new APIs (OpenACC, maybe OMP target)."
- "Week 3 is the paper: final evaluation sweep, publication figures, paper draft."

### 3c. Timeline

- Walk through the milestones: "Bug fixes done by tomorrow, OMP smoke tests by Friday, full Rodinia eval by Monday..."
- Highlight: "Paper draft is due April 5, giving us 2 days for review and Overleaf transfer."

### 3d. Kanban Board (click the tab)

**This is interactive — use it live:**

- Filter by **Week 1** to show what's happening now
- "Tasks 2A through 2G are Week 1. Bug fixes and iterative repair are in progress today."
- Filter by **Samyak** vs **Claude Code** to show the division of labor
  - "Claude Code handles the mechanical work: bug fixes, batch runs, code gen. I handle the judgment-heavy work: smoke testing, analysis, paper writing."
- Click on a task card to show the detail modal
  - "Each task has effort estimates, dependencies, and notes."

**Key task to highlight:**
> "Task 2C (Smoke Test All OMP Specs) is the critical path — everything downstream depends on it. If specs are broken, the full eval will produce misleading results."

### 3e. Results & Charts (click the tab)

- Show the **pilot heatmap** — green/red grid of pass/fail
- Show the **pass rate donut** — "50% overall, but Claude and Azure differ on hotspot"
- Show the **failure taxonomy** — stacked bars of BUILD_FAIL vs RUN_FAIL
- Show the **token usage** — "backprop is 3x more tokens than bfs — larger codebases are harder"
- Show the **speedup chart** — "bfs omp→cuda shows 546x speedup — that's the GPU doing its job"
  - Note: "We use log scale now to handle outliers like this"

### 3f. Team Tab

- "Four team members: Samyak (lead), Erel (augmentation), Gal (advisor), Claude Code (AI agent)."
- Show task distribution — "Claude Code has 10 tasks, I have 9 — the split is intentional."

### 3g. Risks & Questions Tab

- Walk through the **top 3 risks:**
  1. "HeCBench build failures — we're budgeting 2 days for Makefile debugging"
  2. "Paper writing may take longer than planned — mitigated by starting framework sections early"
  3. "LLM rate limits — mitigated by --resume flag and spreading runs across days"

**Transition:** "Before we discuss, let me quickly show the augmentation work."

---

## Page 4: Augmentation Deep Dive (`augmentation_deep_dive.html`) — 3 min

**Talking points:**

- "Augmentation is our code obfuscation pipeline — AST-driven transforms that make source code harder for LLMs."
- "L1/L2 pass rates are 75% (stable). L3/L4 are 48% and 37% — there are known bugs."
- "Erel may have fixes for L3/L4. If those land this week, we retest in Week 3 and potentially add L3/L4 to the evaluation matrix."
- "For the paper, even L0/L1/L2 gives us interesting data: does augmentation affect LLM translation quality?"

---

## Page 5: Architecture (`architecture.html`) — 2 min (optional)

Only show this if the team wants to understand the system design.

- "This is the full architecture: spec loading → build → run → verify → report."
- "The harness is 1,366 lines of Python. Everything is spec-driven."
- "Key design property: scaling to 500+ kernels requires zero code changes."

---

## Decision Points (5 min)

**These are the 3 things I need from the team:**

### Decision 1: Which additional benchmark suite?

> "We need at least 2 suites for the paper (Rodinia + HeCBench is the plan). Should we attempt a third?"
>
> Options: PolyBench/GPU (~30 kernels, popular in literature), Parboil (12 kernels, well-studied), or NAS (8 kernels, impressive name recognition).
>
> My recommendation: PolyBench/GPU if we have time, but it's a stretch goal.

### Decision 2: Erel's augmentation fixes — timeline?

> "The augmentation L3/L4 bugs (overlapping candidates, struct member precedence, assignment-in-condition) — when will the fixes be merged? We need to know whether to include L3/L4 in the evaluation matrix."
>
> If fixes land by March 30 → we include L3/L4.
> If not → paper focuses on L0/L1/L2, mentions L3/L4 as future work.

### Decision 3: Paper structure and Overleaf

> "Has the Overleaf project been created? What template are we using (SC26 proceedings format)?"
> "I'll start writing Sections 3 (corpus) and 4 (framework) this week — those don't depend on final results."

---

## Closing (1 min)

> "Summary: We're on Day 2 of 21. Infrastructure is solid, pilot shows 50% pass rate, sprint plan is tracked on the dashboard. The critical path is: smoke tests (this week) → full Rodinia eval (next Monday) → HeCBench (next Tuesday) → paper (April 4–5)."
>
> "I'll send a daily status update each evening with what got done and what's next."
>
> "The dashboard is live at the URL — you can check kanban status anytime."

---

## Backup: If Asked About...

### "How do we compare to related work?"

> No existing benchmark specifically targets LLM-based parallel code translation. HumanEval and MBPP test sequential code generation. BabelTower (Microsoft, 2024) does multilingual translation but not parallel APIs. Our contribution is the first infrastructure for systematically evaluating CUDA↔OMP↔OpenCL↔SYCL translation by LLMs.

### "What if the pass rate stays at 50%?"

> A 50% pass rate is actually a strong finding — it means LLMs can handle roughly half of translation tasks without human intervention. The interesting paper contribution is the *failure analysis*: what patterns cause LLMs to fail, and does iterative repair help? We expect the pass rate to vary significantly by kernel complexity, translation direction, and model.

### "How does augmentation affect translation?"

> We don't know yet — that's a Week 1 deliverable (Task 2D). The hypothesis is that augmentation (making source code harder to read) will decrease pass rates, but by how much? If L1/L2 augmentation has minimal impact, it suggests LLMs are reasoning about code structure, not pattern-matching. If it tanks the pass rate, it suggests surface-level understanding. Either result is publishable.

### "What's the minimum viable paper?"

> 2 suites (Rodinia + HeCBench), 2 models, 3 directions (cuda→omp, omp→cuda, cuda→opencl), L0/L1/L2 augmentation. That gives us a 6-dimensional results matrix with ~300 translation pairs. The failure taxonomy and self-repair analysis are the novel analytical contributions beyond the infrastructure.

---

## Quick Reference: Website Page → Content Map

| Website Page | What It Shows | When to Reference |
|---|---|---|
| `overview.html` | Project intro, architecture overview | Opening, to frame the project |
| `llm_evaluation.html` | Pilot results, pass/fail heatmap | When discussing LLM translation quality |
| `sprint_dashboard.html` | Kanban, timeline, charts, risks | Main meeting page — most time here |
| `augmentation_deep_dive.html` | Augmentation pass rates, transforms | When discussing code obfuscation |
| `results.html` | Full augmentation results matrix | If team wants detailed per-spec results |
| `architecture.html` | System architecture diagram | If team wants to understand internals |
| `pipeline.html` | Build/run/verify pipeline flow | If team asks about the harness |
| `build_results.html` | Build success/failure matrix | If team asks about infrastructure reliability |

---

## Presentation Flow Diagram

```
overview.html (2 min)
    ↓
llm_evaluation.html (5 min)
    ↓
sprint_dashboard.html (8 min)  ← MOST TIME HERE
  ├─ Stats + Timeline
  ├─ Kanban Board (interactive demo)
  ├─ Results Charts
  └─ Risks & Questions
    ↓
augmentation_deep_dive.html (3 min)
    ↓
Decision Points (5 min)
    ↓
Close (1 min)
```

**Total: ~25 minutes + discussion**
