# Sprint-Crunch Memory Consolidation Implementation Plan

> **For agentic workers:** This plan is executed via `/agent-team` using TeamCreate.
> Do NOT use standalone subagents. Use ultrathink for all teammates. Model: Opus everywhere.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure Claude Code memory (13 → 9 files) for SC26 sprint crunch — purge stale 3-model data, merge overlapping feedback files, add sprint orientation and Qwen safety rule.

**Architecture:** Sequential agent team pipeline. Auditor reads and validates the action plan against current disk state. Executor-Critic writes/deletes files one at a time with incremental validation after each operation. Lead coordinates and gates on user approval between phases.

**Tech Stack:** Claude Code agent teams (TeamCreate), Write/Edit tools for memory files, Bash for verification commands.

**Spec:** `docs/superpowers/specs/2026-03-31-dream-consolidation-design.md`

---

## Copy-Pasteable Session Prompt

**Use this prompt in a fresh `/clear` Claude Code session to execute this plan:**

```
Use /agent-team to create a team called "dream-consolidation" with Lead + 2 teammates.

Read the design spec at docs/superpowers/specs/2026-03-31-dream-consolidation-design.md first.
Then read the implementation plan at docs/superpowers/plans/2026-03-31-dream-consolidation.md.

Execute the plan task by task. All teammates use ultrathink and model: opus.

MEMORY_DIR = ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory

SAFETY RULES (INVIOLABLE):
- NEVER touch anything in results/evaluation/
- NEVER touch Qwen data/code/results
- Memory files are NOT in git — deletions are permanent
- All new file contents are pre-written in the spec — Executor copies them exactly, does not improvise

Context Management:
- 200K token soft limit per teammate (soft, not hard)
- If approaching limit: create handoff doc with summary + remaining tasks → spawn replacement teammate
- Read ONLY what you need — conditional, non-repetitive reads
- If unsure which files to read, ask Samyak

Execute Tasks 1-5 from the plan in order. Present Auditor's report (Task 1) to me for approval before proceeding to Task 2+.
```

---

## Files Reference

### Memory Directory
```
~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/
```

### Current Files on Disk (13 memory + 1 index)
| File | Action | Task |
|------|--------|------|
| `MEMORY.md` | REBUILD | Task 4 |
| `feedback_opus_only.md` | KEEP | — |
| `feedback_context_hygiene.md` | KEEP | — |
| `feedback_use_tmux.md` | KEEP | — |
| `feedback_f1_claude_desktop.md` | KEEP | — |
| `feedback_protect_cuda_omp_results.md` | KEEP | — |
| `reference_sc26_related_work.md` | KEEP | — |
| `feedback_agent_team_practices.md` | DELETE | Task 3 |
| `feedback_agent_team_creation.md` | DELETE | Task 3 |
| `feedback_use_agent_teams.md` | DELETE | Task 3 |
| `feedback_agent_team_not_local.md` | DELETE | Task 3 |
| `project_eval_baseline.md` | DELETE | Task 3 |
| `project_sc26_audit_findings.md` | DELETE | Task 3 |
| `project_3model_decision.md` | DELETE | Task 3 |

### Files to Create
| File | Content Source | Task |
|------|---------------|------|
| `feedback_agent_teams.md` | Spec § "feedback_agent_teams.md" | Task 2 |
| `feedback_protect_qwen_results.md` | Spec § "feedback_protect_qwen_results.md" | Task 2 |
| `project_sprint_crunch.md` | Spec § "project_sprint_crunch.md" | Task 2 |

---

## Task 1: Audit Current State (Auditor Teammate)

**Owner:** `auditor` teammate
**Files:** All 14 files in `MEMORY_DIR` (read-only)

- [ ] **Step 1: List all files on disk**

```bash
ls -la ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/
```

Expected: 14 .md files (13 memory + MEMORY.md). May also have `.last-dream` timestamp file.

- [ ] **Step 2: Read MEMORY.md index and verify all entries point to existing files**

Read `MEMORY.md`. For each entry, confirm the linked file exists on disk. Report any phantoms (entries pointing to missing files) or orphans (files on disk not in index).

- [ ] **Step 3: Read the 7 files marked for DELETE — confirm they contain stale data**

Read each file's frontmatter and first 5 lines of content. Confirm:
- `project_eval_baseline.md` references old 3-model data (105/468, claude-sonnet, etc.)
- `project_sc26_audit_findings.md` references old 3-model audit (504 files, 3 models)
- `project_3model_decision.md` references old model set decisions
- 4 agent-team feedback files contain rules that are captured in the spec's merged version

- [ ] **Step 4: Read the 6 files marked for KEEP — confirm they are NOT stale**

Read each file's frontmatter. Confirm none reference the old 3-model set or contain data that would be invalidated by the consolidation.

- [ ] **Step 5: Produce structured action report**

Format:
```
AUDIT REPORT — Dream Consolidation
===================================
Files on disk: [count]
Phantoms: [list or "none"]
Orphans: [list or "none"]

ACTIONS CONFIRMED:
  DELETE (7): [list files, each with 1-line reason]
  CREATE (3): [list files]
  REBUILD: MEMORY.md

KEEP (6): [list files, each confirmed not stale]

ANOMALIES: [anything unexpected, or "none"]
```

Return this report to Lead. **STOP HERE — Lead presents to Samyak for approval.**

---

## Task 2: Create New Files (Executor-Critic Teammate)

**Owner:** `executor-critic` teammate
**Prerequisite:** Task 1 approved by Samyak
**Files:**
- Create: `MEMORY_DIR/feedback_agent_teams.md`
- Create: `MEMORY_DIR/feedback_protect_qwen_results.md`
- Create: `MEMORY_DIR/project_sprint_crunch.md`

**IMPORTANT:** Copy file contents EXACTLY from the spec at `docs/superpowers/specs/2026-03-31-dream-consolidation-design.md`. The spec wraps each file's content in triple-backtick markdown fences — extract the content BETWEEN the fences (not including the `` ```markdown `` and `` ``` `` delimiters). Do not improvise or modify content.

- [ ] **Step 1: Read the spec to get exact file contents**

Read `docs/superpowers/specs/2026-03-31-dream-consolidation-design.md`, sections:
- "### `feedback_agent_teams.md`" (lines 67-116)
- "### `feedback_protect_qwen_results.md`" (lines 120-138)
- "### `project_sprint_crunch.md`" (lines 142-208)

Extract the content between the triple-backtick markdown fences for each file.

- [ ] **Step 2: Write `feedback_agent_teams.md`**

Use Write tool to create `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_agent_teams.md` with the exact content from spec lines 68-115.

- [ ] **Step 3: Validate `feedback_agent_teams.md`**

Read the file back. Confirm:
- Frontmatter has `name`, `description`, `type: feedback`
- Contains "TeamCreate Is Mandatory" section
- Contains "200K Soft Limit + Handoff Protocol" section
- Contains "Incremental critic" in Team Creation Standards
- No placeholder text

- [ ] **Step 4: Write `feedback_protect_qwen_results.md`**

Use Write tool to create `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_protect_qwen_results.md` with the exact content from spec lines 121-137.

- [ ] **Step 5: Validate `feedback_protect_qwen_results.md`**

Read the file back. Confirm:
- Frontmatter has `type: feedback`
- Contains "together-qwen-3.5-397b-a17b" path
- Contains "NEVER delete, modify, or overwrite"

- [ ] **Step 6: Write `project_sprint_crunch.md`**

Use Write tool to create `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/project_sprint_crunch.md` with the exact content from spec lines 143-207.

- [ ] **Step 7: Validate `project_sprint_crunch.md`**

Read the file back. Confirm:
- Frontmatter has `type: project`
- Deadline says "2026-04-08"
- Model set says "Qwen 3.5 397B" and "GPT-4.1 mini"
- Contains P0/P1/P2 action items with checkboxes
- Does NOT reference claude-sonnet, gemini-flash-lite, or groq-llama as current models (only as "DROPPED")

---

## Task 3: Delete Stale Files (Executor-Critic Teammate)

**Owner:** `executor-critic` teammate
**Prerequisite:** Task 2 complete (create before delete — safer ordering)
**Files to delete (7):**
- `MEMORY_DIR/project_eval_baseline.md`
- `MEMORY_DIR/project_sc26_audit_findings.md`
- `MEMORY_DIR/project_3model_decision.md`
- `MEMORY_DIR/feedback_agent_team_practices.md`
- `MEMORY_DIR/feedback_agent_team_creation.md`
- `MEMORY_DIR/feedback_use_agent_teams.md`
- `MEMORY_DIR/feedback_agent_team_not_local.md`

**WARNING:** Memory files are NOT in git. Deletions are permanent. The spec's new files already capture all non-stale content from these files.

- [ ] **Step 1: Delete the 3 project files**

```bash
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/project_eval_baseline.md
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/project_sc26_audit_findings.md
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/project_3model_decision.md
```

- [ ] **Step 2: Validate project files are gone**

```bash
ls ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/project_*.md
```

Expected: only `project_sprint_crunch.md` remains.

- [ ] **Step 3: Delete the 4 agent-team feedback files**

```bash
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_agent_team_practices.md
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_agent_team_creation.md
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_use_agent_teams.md
rm ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_agent_team_not_local.md
```

- [ ] **Step 4: Validate agent-team feedback files are gone**

```bash
ls ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/feedback_agent_team*.md
```

Expected: only `feedback_agent_teams.md` remains (the merged file from Task 2).

---

## Task 4: Rebuild MEMORY.md Index (Executor-Critic Teammate)

**Owner:** `executor-critic` teammate
**Prerequisite:** Tasks 2 and 3 complete
**Files:**
- Rewrite: `MEMORY_DIR/MEMORY.md`

- [ ] **Step 1: Write the new MEMORY.md**

Use Write tool to overwrite `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/MEMORY.md` with this exact content:

```
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

- [ ] **Step 2: Validate MEMORY.md**

Read the file back. Confirm:
- Exactly 9 entries
- Every linked file exists on disk (no phantoms)
- No references to deleted files
- Under 200 lines

---

## Task 5: Final Verification (Executor-Critic Teammate)

**Owner:** `executor-critic` teammate
**Prerequisite:** Task 4 complete

- [ ] **Step 1: Count files on disk**

```bash
ls ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/*.md | wc -l
```

Expected: **10** (9 memory files + MEMORY.md)

- [ ] **Step 2: List all files and confirm the exact set**

```bash
ls -1 ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/*.md
```

Expected files (alphabetical):
```
feedback_agent_teams.md
feedback_context_hygiene.md
feedback_f1_claude_desktop.md
feedback_opus_only.md
feedback_protect_cuda_omp_results.md
feedback_protect_qwen_results.md
feedback_use_tmux.md
MEMORY.md
project_sprint_crunch.md
reference_sc26_related_work.md
```

- [ ] **Step 3: Cross-check MEMORY.md against disk**

For each entry in MEMORY.md, verify the linked file exists. For each .md file on disk (excluding MEMORY.md), verify it appears in MEMORY.md. Report:
- Orphans (on disk but not in index): should be 0
- Phantoms (in index but not on disk): should be 0

- [ ] **Step 4: Verify frontmatter of all 9 memory files**

Read the first 5 lines of each file. Confirm each has:
- `name:` field (non-empty)
- `description:` field (non-empty)
- `type:` field (one of: user, feedback, project, reference)

- [ ] **Step 5: Spot-check sprint_crunch.md critical fields**

Read `project_sprint_crunch.md`. Confirm:
- Deadline: "2026-04-08"
- Models: "Qwen 3.5 397B" and "GPT-4.1 mini"
- Contains "ALL previous models DROPPED"
- P0 action items present with checkboxes
- Does NOT say "Gemini 2.5 Flash" as current model

- [ ] **Step 6: Spot-check feedback_agent_teams.md critical rules**

Read `feedback_agent_teams.md`. Confirm:
- "ALWAYS use TeamCreate" present
- "200K" soft limit present
- "Incremental critic" present
- "Handoff Protocol" present

- [ ] **Step 7: Update .last-dream timestamp**

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/.last-dream
```

- [ ] **Step 8: Produce final report**

```
DREAM CONSOLIDATION COMPLETE
=============================
Files before: 14 (13 memory + MEMORY.md)
Files after:  10 (9 memory + MEMORY.md)
Deleted: 7 (project_eval_baseline, project_sc26_audit_findings, project_3model_decision,
         feedback_agent_team_practices, feedback_agent_team_creation,
         feedback_use_agent_teams, feedback_agent_team_not_local)
Created: 3 (feedback_agent_teams, feedback_protect_qwen_results, project_sprint_crunch)
Kept:    6 (unchanged)
Rebuilt: MEMORY.md (9 entries)

VERIFICATION:
  Orphans: 0
  Phantoms: 0
  Frontmatter valid: 9/9
  Sprint crunch fields: PASS
  Agent team rules: PASS
  .last-dream updated: YES

STATUS: PASS ✓
```

Return this report to Lead. Lead presents to Samyak for final confirmation.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| File count ≠ 10 | Missed a delete or create | Re-check Tasks 2-3 steps |
| Phantom in MEMORY.md | Typo in filename link | Edit MEMORY.md to fix link |
| Orphan on disk | File not in index | Either add to MEMORY.md or delete if it's stale |
| `.last-dream` not writable | Permissions | `chmod 644` on the file |
| Frontmatter missing `type` | Copy error from spec | Re-copy from spec verbatim |
| sprint_crunch says "Gemini" | Wrong spec version read | Re-read spec, copy exactly |
