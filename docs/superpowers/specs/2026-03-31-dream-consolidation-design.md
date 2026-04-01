# Design: Sprint-Crunch Memory Consolidation via Agent Team

**Date:** 2026-03-31
**Goal:** Restructure Claude Code memory for the SC26 sprint home stretch (deadline April 8).
Every new session should orient instantly to paper-writing + eval-campaign mode.

---

## Context

The memory system has 13 files, all 2-3 days old, with one critical contradiction:
the model set changed from 3 (claude-sonnet, gemini-flash-lite, groq-llama) to 2
(Qwen 3.5 397B + GPT-4.1 mini via Azure) but two project files still reference old
3-model data. Additionally, 4 feedback files about agent teams overlap significantly.

**Key decisions (locked):**
- Purge ALL old 3-model data entirely — those models are dropped
- NEVER touch Qwen data/code/results (new inviolable safety rule)
- Second model: GPT-4.1 mini via Azure (NOT Gemini 2.5 Flash)
- Paper models: Qwen 3.5 397B (Together) + GPT-4.1 mini (Azure)
- Merge 4 agent-team feedback files into 1
- Include remaining audit action items in sprint crunch memory

---

## Target State (After Consolidation)

**From 13 files → 9 files** (+ MEMORY.md index = 10 on disk)

### Files to KEEP (unchanged)
| File | Type | Why |
|------|------|-----|
| `feedback_opus_only.md` | feedback | Timeless preference |
| `feedback_context_hygiene.md` | feedback | Timeless principle |
| `feedback_use_tmux.md` | feedback | Still relevant for eval runs |
| `feedback_f1_claude_desktop.md` | feedback | Timeless |
| `feedback_protect_cuda_omp_results.md` | feedback | Critical safety rule |
| `reference_sc26_related_work.md` | reference | Still relevant for paper |

### Files to DELETE (7 files)
| File | Reason |
|------|--------|
| `project_eval_baseline.md` | Old 3-model numbers (105/468), purged |
| `project_sc26_audit_findings.md` | Old 3-model audit, superseded by sprint_crunch.md |
| `project_3model_decision.md` | Superseded by project_sprint_crunch.md |
| `feedback_agent_team_practices.md` | Absorbed into feedback_agent_teams.md |
| `feedback_agent_team_creation.md` | Absorbed into feedback_agent_teams.md |
| `feedback_use_agent_teams.md` | Absorbed into feedback_agent_teams.md |
| `feedback_agent_team_not_local.md` | Absorbed into feedback_agent_teams.md |

**(4 feedback + 3 project = 7 deleted. 6 kept + 3 created = 9 files. Net: 13 → 9.)**

### Files to CREATE (3 files)
1. **`feedback_agent_teams.md`** — merged from 4 agent-team feedback files
2. **`feedback_protect_qwen_results.md`** — new safety rule
3. **`project_sprint_crunch.md`** — full orientation for sprint crunch

### File to REBUILD
- **`MEMORY.md`** — rebuilt index with 9 entries, semantic grouping

---

## New File Contents

### `feedback_agent_teams.md`

```markdown
---
name: Agent team rules (consolidated)
description: All agent team preferences — TeamCreate mandatory, ultrathink, plan-first, incremental-critic, context-conservative, Opus only
type: feedback
---

## TeamCreate Is Mandatory
When /agent-team is invoked, ALWAYS use TeamCreate. NEVER use standalone subagents
(Agent tool without team_name). This is a recurring correction — no exceptions.

## Team Creation Standards
1. **Samyak is PRIMARY DECISION MAKER** — pause and ask when intent is unclear
2. **Ultrathink** for ALL teammates — include "Use ultrathink" in every teammate prompt
3. **Model: Opus** everywhere — specify `model: "opus"` explicitly
4. **Plan-first** — planner teammate goes first, plan presented to lead before edits
5. **Incremental critic** — critic reviews changes AS they happen, not only at
   the end. After each major action (file write, merge, delete), critic validates
   that specific change before the next action proceeds. Don't batch all review
   to the end where issues compound.

## Context Management (200K Soft Limit + Handoff Protocol)
- **Soft limit: 200K tokens per teammate.** Not a hard wall — a signal.
- **When approaching 200K:** teammate creates a structured handoff document:
  1. Summary of work completed so far
  2. "Guide" with remaining tasks, file paths, and key decisions made
  3. Any partial state that needs to be carried forward
- **Spawn a fresh teammate** in the same agent team with the handoff document.
  New teammate picks up seamlessly — other teammates interact with it as if
  it were the original.
- **Conditional reading:** Read ONLY what you need. Don't bulk-read directories.
  If unsure which files matter, pause and ask another teammate or Samyak to
  direct you to the precise folder(s).
- **Non-repetitive reads:** If a file was already read by another teammate and
  summarized, use the summary — don't re-read the file.

## Execution Style
- Use agent teams, superpowers skills, and ultrathink proactively
- For 2+ independent subtasks, dispatch parallel teammates immediately
- Reuse existing agents: explorer, eval-batcher, spec-auditor, plan-reviewer,
  self-critic, consistency-checker, rodinia-verifier, paper-drafter

## Anti-Patterns
- No teammate overlap on same files
- No eval batches in worktrees (submodules won't initialize)
- Kill idle teammates early

**Why:** Consolidated from 4 correction sessions (2026-03-28 to 2026-03-30).
**How to apply:** Check before any /agent-team invocation.
```

### `feedback_protect_qwen_results.md`

```markdown
---
name: NEVER touch Qwen data or results
description: Inviolable rule — never delete, modify, or overwrite Qwen 3.5 397B eval results, code, or data
type: feedback
---

NEVER delete, modify, or overwrite any Qwen 3.5 397B evaluation results, translated
code, or data files.

**Why:** Qwen results represent days of GPU compute time. Accidental overwrites (like
the BFS omp-to-cuda incident with CUDA/OMP results) are catastrophic and unrecoverable.

**How to apply:**
- Treat `results/evaluation/together-qwen-3.5-397b-a17b/` as read-only
- Always use `--resume` when running eval batches that include Qwen
- Never run `rm` on any path matching `*qwen*` in results/evaluation/
- This rule applies to ALL operations: eval reruns, cleanup scripts, batch operations
```

### `project_sprint_crunch.md`

```markdown
---
name: SC26 Sprint Crunch
description: Deadline April 8 2026, 2-model campaign (Qwen 3.5 397B + GPT-4.1 mini Azure), remaining actions, key findings, paper priorities
type: project
---

## Deadline
SC26 paper submission: 2026-04-08 (8 days from 2026-03-31).

## Model Set (Final)
- **Qwen 3.5 397B** via Together AI — ~333 result files complete as of 2026-03-30
- **GPT-4.1 mini** via Azure endpoint — eval not yet started

ALL previous models DROPPED: claude-sonnet-4-6, gemini-2.5-flash-lite,
groq-llama-3.3-70b-versatile, azure-gpt-4.1 (full). Old 3-model data (504 files)
is historical — do not reference in paper.

## Campaign Parameters
- Self-repair protocol: max_retries=3, temperature=0.0
- pass@k sweep: separate eval, T=0.7, num_samples=3
- Always use `--resume` and `--suite` flags

## Remaining Actions (from SC26 audit, updated for 2-model)

### P0 — Submission-Blocking
- [ ] **LaTeX transfer** — only 692-line Markdown exists. SC26 may use IEEE template
  (verify). Biggest bottleneck (2-3 days).
- [ ] **Anonymous GitHub repo** — double-blind requirement. Not started.
- [ ] **Run GPT-4.1 mini eval** — second model has zero results
- [ ] **Update all model references** — paper draft references old 3-4 model set.
  Now 2 models.
- [ ] **Add LASSI + CodeRosetta** to Related Work — highest-risk omissions
  - LASSI (arxiv:2407.01638): 80-85% pass with agentic self-correction
  - CodeRosetta (arxiv:2410.20527): NeurIPS'24, domain-specific C++↔CUDA

### P1 — Required for Acceptance
- [ ] **Statistical analysis**: 95% CIs, chi-squared for augmentation, significance tests
- [ ] **Fix augmentation confound**: L0 has different directions than L1-L4
- [ ] **Add 5 more related work**: HPC-Coder-v2, TRACY, SWE-bench Illusion,
  VibeCodeHPC, QiMeng-MuPa
- [ ] **Performance sanity check** for subset of PASS results
- [ ] **Address small-N** for exploratory directions — caveat appropriately

### P2 — Strengthen Paper
- [ ] Failure taxonomy with error snippets per model
- [ ] Per-kernel difficulty analysis (backprop tier anomaly as case study)
- [ ] Verify IEEE vs ACM template for SC26

## Key Technical Findings
1. **OpenCL kernel-only fix** (S-OCLFIX, 2026-03-30): X-to-OpenCL only translates .cl
   kernel files, host code untouched. Fixed run/verify to use target args/patterns.
2. **pass@k preliminary**: self-repair 2.3x over stochastic sampling
3. **Failure taxonomy**: BUILD_FAIL dominant (~41%), VERIFY_FAIL least (~9%)
   — numbers from OLD 3-model data, will change with Qwen+GPT-4.1-mini
4. **Backprop tier anomaly**: per-kernel difficulty not monotonic with model strength

## Claims That Need Re-Evaluation (with new 2-model data)
- All pass rate percentages (were based on old 3-model data)
- "Claude dramatically outperforms" — Claude is dropped
- Failure breakdown distribution — recompute from Qwen + GPT-4.1 mini
- Self-repair statistics — verify still holds

**Why:** Sprint-mode orientation. Every session checks this first.
**How to apply:** Update checkboxes as work completes. Recompute numbers once
GPT-4.1 mini eval finishes.
```

### Rebuilt `MEMORY.md`

```markdown
- [Opus only, no Sonnet](feedback_opus_only.md) — Always Opus everywhere; fast mode only for implementation
- [Agent team rules](feedback_agent_teams.md) — TeamCreate mandatory, ultrathink, plan-first, incremental-critic, 200K soft limit + handoff
- [Context hygiene](feedback_context_hygiene.md) — Delegate reads to agents; avoid context rot; conditional reads only
- [Use tmux for long runs](feedback_use_tmux.md) — Always tmux for eval batches and commands >5 min
- [F1 is Claude Desktop only](feedback_f1_claude_desktop.md) — Never include F1 architecture in Claude Code work
- [NEVER touch CUDA/OMP results](feedback_protect_cuda_omp_results.md) — Inviolable: never delete/modify CUDA↔OMP eval results
- [NEVER touch Qwen results](feedback_protect_qwen_results.md) — Inviolable: never delete/modify Qwen 3.5 397B eval data
- [SC26 sprint crunch](project_sprint_crunch.md) — Deadline April 8, Qwen+GPT-4.1-mini, remaining actions, key findings, paper priorities
- [SC26 related work gaps](reference_sc26_related_work.md) — 7 missing papers (LASSI, CodeRosetta, HPC-Coder-v2, etc.)
```

---

## Agent Team Design

**Team name:** `dream-consolidation`
**Structure:** Lead + 2 teammates, sequential pipeline with incremental critic.

| Role | Name | Responsibility |
|------|------|---------------|
| Lead | (main session) | Coordinates. Presents Auditor's plan to Samyak. Greenlights Executor. |
| Teammate 1 | `auditor` | Reads all 13 memory files (conditional, non-repetitive). Produces structured action list: DELETE/MERGE/CREATE/REBUILD with exact file contents. |
| Teammate 2 | `executor-critic` | Executes ONE action at a time. After each action, validates that specific change (incremental critic). Reports issues before proceeding. |

### Context Protocol
- **200K token soft limit** per teammate
- If approaching limit: create handoff doc → spawn replacement → seamless continuation
- Conditional reads only — ask Samyak/Lead if unsure which files to read
- Non-repetitive: use summaries from other teammates, don't re-read

### Execution Flow
1. Lead spawns `auditor` → reads all memory files → returns structured action plan
2. Lead presents plan to Samyak → waits for explicit approval
3. Lead spawns `executor-critic` with approved plan
4. Executor-critic executes actions ONE AT A TIME:
   - For each action: execute → validate → report → proceed to next
   - If any validation fails: STOP and report to Lead
5. Lead confirms final state with Samyak

### Safety Rules
- Memory files are NOT in git — deletions are permanent
- NEVER touch anything in `results/evaluation/`
- NEVER touch Qwen data/code/results
- All file contents for new/merged files are pre-written in this spec — Executor copies them exactly, does not improvise
- `.last-dream` timestamp updated after completion

---

## Verification

After execution, the Executor-Critic validates:
1. **No orphan files** — every .md file in memory/ is listed in MEMORY.md
2. **No phantom entries** — every MEMORY.md entry points to an existing file
3. **Correct frontmatter** — every file has name, description, type fields
4. **No deleted files still exist** — the 7 deleted files are actually gone
5. **File count** — exactly 10 files on disk (9 memory + MEMORY.md)
6. **Index length** — MEMORY.md is 9 entries, well under 200 lines
7. **Content accuracy** — spot-check that sprint_crunch.md has correct deadline, model names, and action items
