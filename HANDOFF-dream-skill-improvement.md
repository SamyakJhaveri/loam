# HANDOFF: Dream Skill Improvement — Multi-Scope Targeting + Retrieval-Quality Indexing

> **For the next Claude Code session.** This document is self-contained — you don't
> need any prior conversation context. Read this top to bottom, then implement.
>
> Written at an accessible level so the reasoning is clear to anyone picking it up.

---

## Table of Contents

1. [Goal — What We're Doing and Why](#goal)
2. [Background — What You Need to Understand First](#background)
3. [Research Findings — What We Learned](#research-findings)
4. [What Worked During Design](#what-worked)
5. [What Didn't Work / Was Rejected](#what-didnt-work)
6. [Current State — What Exists Right Now](#current-state)
7. [The Implementation Plan](#the-implementation-plan)
8. [Deferred Work — What We're NOT Doing Yet](#deferred-work)
9. [Verification Checklist](#verification-checklist)

---

## Goal

**Improve the dream skill** (`/dream`) so it can:

1. **Consolidate memories across scopes** — not just the current project's memories, but also user-level memories (preferences and habits that span all projects).
2. **Produce better MEMORY.md index entries** — so future Claude Code sessions can actually *find* the right memories when they need them.

These are the only two improvements. Nothing else changes.

### Why This Matters

Think of Claude Code's memory like a filing cabinet:
- Each project has its own drawer (project memory)
- You also have a personal drawer (user-level memory) for preferences that apply everywhere
- The **MEMORY.md** file is the label on the outside of each drawer — it tells Claude which files are inside and what they contain

Right now, the dream skill can only clean up one drawer at a time (the current project's). And when it relabels the drawer, it doesn't check whether the labels are actually helpful for finding things later.

We're fixing both problems.

---

## Background — What You Need to Understand First

### What is the Dream Skill?

The dream skill (`/dream`) performs **memory consolidation** — like decluttering and reorganizing a messy desk. Over many sessions, Claude Code accumulates memory files (notes about user preferences, project decisions, etc.). These files get stale, duplicated, or contradictory over time.

The dream skill runs a 4-phase workflow:
1. **Orient** — scan all memory files, check their health
2. **Gather Signal** — score each file (how stale? how redundant? dates accurate? right size?)
3. **Consolidate** — propose changes (prune, merge, deduplicate, fix dates) and WAIT FOR USER APPROVAL
4. **Execute** — apply the approved changes

The approval gate at Phase 3 is critical — memory files live at `~/.claude/projects/` and are **NOT in git**. Deletions are permanent.

### What is this project?

`project-seed-framework` is a **template** that bootstraps new Claude Code projects. It's not a regular project — it's the factory that makes projects. It uses [Copier](https://copier.readthedocs.io/) to stamp out new project directories from templates.

**Why this matters for you:** The dream skill exists in TWO identical copies:

| Copy | Path | Purpose |
|------|------|---------|
| Dev copy | `.claude/skills/dream/SKILL.md` | Used when working on this template project itself |
| Template copy | `template/.claude/skills/dream/SKILL.md` | Gets distributed to every new project created from this template |

**Both copies must be edited identically.** If you only edit one, they'll drift apart.

### How Claude Code Retrieves Memories (Important!)

This is how memories actually get used in a session:

1. **At session start**: Claude Code loads the first 200 lines (or 25KB) of `MEMORY.md` into context. Always. Automatically.
2. **Memory Prefetch**: A lightweight Sonnet model reads your prompt and picks up to 5 topic files it thinks are relevant.
3. **During the session**: Claude can manually `Read` or `Grep` memory files if it needs something specific.

There is **no semantic search**. No embeddings. No vector database. No synonym matching. If your MEMORY.md entry says "project notes" and Claude is looking for "Copier distribution decision," it won't find it.

**This is why retrieval-quality indexing matters.** The MEMORY.md entry is the *only* signal that connects a memory file to the sessions that need it. Vague entries = invisible files.

### Key File Paths

| What | Path |
|------|------|
| Dev dream skill | `/Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md` |
| Template dream skill | `/Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md` |
| Project memory dir | `~/.claude/projects/-Users-samyakjhaveri-Desktop-project-seed-framework/memory/` |
| User-level dir | `~/.claude/projects/-Users-samyakjhaveri/` (exists, but has NO `memory/` subdirectory) |
| YAML colon gotcha | `.claude/rules/known-issues.md` (read this before editing YAML frontmatter) |

---

## Research Findings — What We Learned

We compared our dream skill against two alternatives. Here's what we found:

### Comparison 1: External Community Dream Skill

A simpler dream skill (128 lines vs. our 244) found at `temp/dream_SKILL-2.md`.

**What it does better:**
- **Multi-scope targeting** — `/dream user` and `/dream all` commands let you consolidate user-level memory, not just project memory. *We're adopting this.*
- **Conciseness** — half the size means fewer tokens consumed when the skill loads. Trusts the model more.
- **Daily-log awareness** — checks for `logs/YYYY/MM/` structured daily logs. *Deferred — no logs directory exists.*

**What we do better:**
- **Safety gate** — our Phase 3 stops and waits for approval before any writes. The external skill just writes directly. Since memory files aren't in git, this is a critical safety difference.
- **Structured analysis** — our 5-tier staleness scoring, redundancy checking, date auditing, and size analysis are far more thorough.
- **Verification checklist** — 7-point post-execution check. The external skill has none.
- **Audit subcommand** — `/dream audit` as a safe read-only mode. The external skill has no equivalent.

### Comparison 2: Anthropic's Official Autodream (API Feature)

Autodream is a server-side feature for the Claude Agent SDK (not Claude Code CLI). It's a fundamentally different tool.

**What it does better:**
- **Full transcript processing** — can read up to 100 complete session transcripts to find patterns the user never explicitly stated. We can't do this (JSONL lines are massive JSON objects that would blow our context window).
- **Non-destructive** — creates a new memory store instead of editing in place. Input is preserved.
- **Automatic** — runs during idle periods without user action.

**What we do better:**
- **Human-in-the-loop** — approval gate means a developer reviews every change before it touches files.
- **Convention awareness** — knows about our frontmatter format, type taxonomy, cross-reference linking, 200-line index budget.
- **Surgical control** — `audit` and `prune <file>` give precise control vs. Autodream's all-or-nothing approach.
- **Diagnostic visibility** — health reports and signal analysis teach the user about their memory state. Autodream is a black box.

### Memory Retrieval Research

Key findings about how Claude Code uses memories:
- MEMORY.md is the **sole entry point** — first 200 lines/25KB loaded at session start
- Memory Prefetch (Sonnet sideQuery) selects up to 5 files based on the user's prompt
- No semantic search, no embeddings — just grep and Sonnet's judgment from reading the index
- The `description` field in memory file frontmatter does **NOT** affect retrieval (that's only for skills)
- Retrieval quality depends entirely on how descriptive MEMORY.md entries are

---

## What Worked During Design

1. **Phased approach** — instead of trying to add everything at once, we scoped to just the two improvements that have immediate value. This came from the plan-reviewer's critique.
2. **Adversarial review** — running the plan-reviewer agent found 14 issues including one critical bug (JSONL sampling would blow context by 25x). Better to catch that before implementation than during.
3. **Grounding in actual filesystem state** — we explored what actually exists on disk before designing. This prevented us from building features for infrastructure that doesn't exist (no `logs/` directory, no user-level `memory/` subdirectory).
4. **Anchor text over line numbers** — since edits change file length, we use content anchors ("find the section that says X") instead of line numbers ("edit line 42"). This prevents cascading insertion errors.

## What Didn't Work / Was Rejected

| Idea | Why Rejected |
|------|-------------|
| **Daily-log awareness** | No `logs/` directory exists anywhere. Building a feature for nonexistent infrastructure = dead code. Deferred until daily logging is actually adopted. |
| **Transcript pattern sampling (`/dream deep`)** | Each JSONL transcript "line" is a massive JSON object (full hook output, skill listings, attachment payloads). Reading 100 lines = ~500k tokens, not the 20k budget we estimated. Needs a complete redesign with `jq`-based field extraction. Deferred. |
| **Adding a Phase 2E (Retrieval Quality Check)** | User chose the simpler approach: enhance the existing INDEX REBUILD step in Phase 3 instead of adding a whole new phase. Less structural change, same outcome. |
| **Editing only one skill copy** | Plan-reviewer caught that both dev and template copies must be identical. Editing just one creates drift. |
| **Using `basename` or `grep` to find user-level memory dir** | These approaches are fragile and wrong. The user-level directory has a deterministic path derivable with `echo $HOME | tr '/' '-'`. |
| **Line-number-based edit instructions** | The first edit changes the file length, shifting all subsequent line numbers. A fresh session would insert content at wrong locations. Anchor text is robust. |

---

## Current State — What Exists Right Now

### Memory Files (as of 2025-05-13)

```
~/.claude/projects/-Users-samyakjhaveri-Desktop-project-seed-framework/memory/
├── MEMORY.md                     (341 bytes) — Index file, 3 entries
├── user-profile.md               (986 bytes) — User profile and work habits
├── project-copier-distribution.md (1.1 KB)   — Decision log: Copier vs Docker
└── feedback-plan-quality.md      (1.1 KB)    — Plan quality expectations
```

- No `.last-dream` file (dream skill has never been run)
- No `logs/` subdirectory
- 5 JSONL session transcripts (~4.9 MB combined) alongside the memory directory
- User-level directory (`-Users-samyakjhaveri/`) exists but has NO `memory/` subdirectory — only 1 transcript file

### Dream Skill (as of 2025-05-13)

- 244 lines, well-structured 4-phase workflow
- Both copies (dev + template) are identical
- Supports: `/dream`, `/dream full`, `/dream audit`, `/dream prune <file>`
- Does NOT support: scope targeting, retrieval-quality indexing

---

## The Implementation Plan

> **Instructions for the implementing session**: Read each step fully before starting it.
> Use anchor text (content patterns) to find insertion points, not line numbers.
> Edit the dev copy first (`.claude/skills/dream/SKILL.md`), verify each step, then
> copy to the template copy at the end.
>
> **Skill to load**: Use `/karpathy-guidelines` before starting implementation to avoid
> common coding mistakes. Use `/validate` before committing.

### Step 0: Backup Both Copies

```bash
cp /Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md \
   /Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md.backup
cp /Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md \
   /Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md.backup
```

**Verify**: Both `.backup` files exist and match the originals.

---

### Step 1: Update Frontmatter Description

**File**: `.claude/skills/dream/SKILL.md`

**Find this** (the `description:` line in the YAML frontmatter, starts with `"Memory consolidation for`).

**Replace with** (uses folded scalar `>` because the text contains colons — see `.claude/rules/known-issues.md`):

```yaml
description: >
  Memory consolidation for ~/.claude/projects memory files. Use after major
  milestones, after 5+ sessions without consolidation, when memory feels stale,
  or before long breaks. Runs 4-phase audit, plan, approval, execute workflow.
  Subcommands: audit (read-only), prune <file> (targeted), user/all (scope).
```

**Why folded scalar?** In YAML, colons in unquoted strings break parsing. The `>` character tells YAML "treat the following indented block as one long string, folding newlines into spaces." This is a known gotcha in this project — documented in `.claude/rules/known-issues.md`.

**Verify**: `head -7 .claude/skills/dream/SKILL.md` — confirm `---` delimiters are intact and description uses `>`.

---

### Step 2: Update Arguments Section

**Find**: The `## Arguments` section (currently lists 3 subcommands: `full`, `audit`, `prune`).

**Replace the entire arguments list with**:

```markdown
## Arguments

- `$ARGUMENTS` — one of:
  - (empty) or `full` — Full 4-phase consolidation on current project memory
  - `user` — Full 4-phase consolidation on user-level memory only
  - `all` — Full consolidation on both project AND user memory (run phases on each separately, combined report)
  - `audit` — Phases 1-2 only: read-only health report on current project
  - `audit user` — Read-only health report on user-level memory
  - `audit all` — Read-only health report on both scopes
  - `prune <filename>` — Targeted prune of a single memory file
```

**Why these 7 and only these 7?** We explicitly defined the valid argument grammar to prevent ambiguity. There is no `/dream deep` (deferred), no `/dream audit deep` (deferred). If a user types something not in this list, ask them to clarify.

**Verify**: The list has exactly 7 entries.

---

### Step 3: Update Trigger Line

**Find**: `**Trigger:** \`/dream\`, \`/dream audit\`, or \`/dream prune <file>\``

**Replace with**:

```markdown
**Trigger:** `/dream`, `/dream audit`, `/dream user`, `/dream all`, `/dream audit user`, `/dream audit all`, or `/dream prune <file>`
```

**Verify**: Lists all 7 valid subcommands.

---

### Step 4: Add Scope Resolution Section (NEW)

This is the biggest addition — a new section that teaches the skill how to find memory directories for different scopes.

**Find**: The Configuration code block that ends with these two lines:
```
Session transcripts live alongside the memory directory as JSONL files.
Grep them narrowly — never read whole transcript files.
```

**Insert AFTER those lines and BEFORE the `---` separator that precedes `## Phase 1 — Orient`**:

```markdown

## Scope Resolution

Parse scope from `$ARGUMENTS`:

| Command | Scope | Memory Directory |
|---|---|---|
| `/dream` or `/dream full` | project | `~/.claude/projects/<project-path-slug>/memory/` (auto-detect from $PWD) |
| `/dream user` | user | `~/.claude/projects/-$(echo $HOME | tr '/' '-')/memory/` |
| `/dream all` | both | Run all phases on each scope independently, then combine reports |
| `/dream audit [scope]` | read-only variant of above | Same directory resolution |

### Guard Clause (run before Phase 1)

Before starting any phase, verify the resolved memory directory exists and contains `.md` files:

```bash
MEMORY_DIR="<resolved path>"
if [ ! -d "$MEMORY_DIR" ] || [ -z "$(ls "$MEMORY_DIR"/*.md 2>/dev/null)" ]; then
  echo "No memory files found at $MEMORY_DIR. Nothing to consolidate."
  # Exit cleanly for this scope
fi
```

If scope is `all` and one scope has no memory directory, report it and proceed with the other scope only.

### Cross-Scope Behavior

When scope is `user`:
- Phase 2A (Staleness): Works normally
- Phase 2B (Redundancy): Skip cross-checks against project-specific `CLAUDE.md` and `.claude/rules/` — only check for redundancy within user-level memory files themselves
- Phase 2C (Date Audit): Works normally
- Phase 2D (Size Check): Works normally

When scope is `all`:
- Run Phases 1-4 independently on each scope's directory
- Present a single combined plan at Phase 3, but clearly label each action with its scope: `[project]` or `[user]`
- The approval gate applies to the combined plan — user approves/rejects as a whole
```

**Why the guard clause?** Right now, the user-level memory directory (`-Users-samyakjhaveri/`) has NO `memory/` subdirectory. Without the guard, `/dream user` would crash with confusing bash errors. The guard makes it fail gracefully.

**Why `tr '/' '-'` for path derivation?** Claude Code encodes directory paths as slugs — replacing `/` with `-`. So `/Users/samyakjhaveri` becomes `-Users-samyakjhaveri`. The `tr` command does this deterministically. Earlier plan versions tried to use `basename` or `grep` to find the directory — those approaches were fragile and wrong.

**Why skip Phase 2B for user scope?** Phase 2B checks for redundancy against project-specific files (`CLAUDE.md`, `.claude/rules/`). But user-level memories are project-agnostic — there's no single project's CLAUDE.md to check against.

**Verify**: Read the inserted section. Confirm the guard clause bash script is syntactically valid. Confirm the user-level path uses `tr '/' '-'`.

---

### Step 5: Enhance INDEX REBUILD for Retrieval Quality

This is the retrieval-quality improvement. We're upgrading the existing INDEX REBUILD step so it produces better MEMORY.md entries.

**Find**: In `## Phase 3 — Consolidate`, the subsection `### INDEX REBUILD`. It currently contains:

```
Propose the new MEMORY.md with:
- Semantic grouping: **Permanent Knowledge** / **Active State** / **Completed Decisions**
- Each entry: one line, <150 chars: `- [Title](file.md) — one-line hook`
- Total must stay under 200 lines
```

**Replace that entire subsection with**:

```markdown
### INDEX REBUILD (Retrieval-Optimized)

Claude Code's Memory Prefetch uses a Sonnet sideQuery that reads MEMORY.md to select up to 5 topic files per session. The index entry is the **sole retrieval signal** — if it's vague, the file is invisible to future sessions.

Propose the new MEMORY.md with:
- Semantic grouping: **Permanent Knowledge** / **Active State** / **Completed Decisions**
- Each entry: one line, <150 chars: `- [Title](file.md) — one-line hook`
- Total must stay under 200 lines

**Retrieval quality rules for each index entry:**

1. **Include searchable keywords** — terms a user or Claude would naturally use when the topic is relevant. "Copier distribution decision — chose Copier over Docker for zero-install cross-platform template delivery" beats "project distribution notes."
2. **Name the domain** — "authentication," "deployment," "testing strategy," not "some notes" or "project info."
3. **State the conclusion, not just the topic** — "Chose Copier over Docker" beats "Distribution options." The entry should help Claude decide relevance without reading the file.
4. **Use grep-friendly language** — Claude's fallback retrieval is literal grep. Include the exact terms someone would search for (e.g., "port conflict," "Docker networking," "auth middleware").

For each entry in the proposed MEMORY.md, briefly note whether it improved vs. the original (e.g., `[improved: added keywords]` or `[unchanged: already descriptive]`). This helps the user evaluate the index quality during the Phase 3 approval gate.
```

**Why this matters**: A memory file can survive consolidation perfectly — pruned, deduped, dates fixed — but still be invisible to future sessions because its MEMORY.md entry says "project notes" instead of "Copier distribution decision." This step ensures consolidation improves *discoverability*, not just *content quality*.

**Verify**: Read the modified Phase 3 section. Confirm 4 retrieval quality rules are present. Confirm the annotation instruction is included.

---

### Step 6: Add Safety Rule for Missing Directories

**Find**: The `## Safety Rules` section at the end of the file (currently 6 bullets).

**Add one new bullet at the end**:

```markdown
- **Guard missing directories** — if a resolved memory directory doesn't exist or has no `.md` files, report cleanly and exit that scope. Never create directories or files unprompted.
```

**Verify**: Safety rules section now has 7 bullets.

---

### Step 7: Copy to Template

After ALL edits to the dev copy are complete and individually verified:

```bash
cp /Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md \
   /Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md
```

**Verify** with diff:

```bash
diff /Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md \
     /Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md
```

Expected output: no differences (empty output).

---

### Step 8: Cleanup Backups

After end-to-end verification passes:

```bash
rm /Users/samyakjhaveri/Desktop/project_seed_framework/.claude/skills/dream/SKILL.md.backup
rm /Users/samyakjhaveri/Desktop/project_seed_framework/template/.claude/skills/dream/SKILL.md.backup
```

---

## Deferred Work — What We're NOT Doing Yet

| Feature | Why Deferred | What Would Unblock It |
|---------|-------------|----------------------|
| **Daily-log awareness** (Phase 2.0 that mines `logs/YYYY/MM/` files) | No `logs/` directory exists in any memory directory. This would be dead code. | Establish a daily-logging mechanism first. Then add this feature. |
| **Transcript pattern sampling** (`/dream deep`) | JSONL transcript lines are massive JSON objects — 100 lines ≈ 500k+ tokens, 25x over budget. The sampling strategy needs a complete redesign using `jq`-based field extraction. | Prototype `jq` extraction on real JSONL files. Prove it works within ~20k tokens. Then add. |

**Do NOT build these.** They were part of an earlier plan version that was rejected by the plan-reviewer for building on infrastructure that doesn't exist.

---

## Verification Checklist

Run these checks after all implementation steps are complete:

- [ ] **YAML frontmatter valid**: `head -7 .claude/skills/dream/SKILL.md` shows `---` delimiters, `description: >` (folded scalar), `auto-activate: false`
- [ ] **No unquoted colons**: Description uses folded scalar `>`, not a single-line string
- [ ] **Dry run audit**: `/dream audit` produces the health report table without errors
- [ ] **Scope test**: `/dream audit user` either reports user-level memory health OR cleanly says "No memory files found at [path]"
- [ ] **Template sync**: `diff` of both copies shows zero differences
- [ ] **No regressions**: `/dream full`, `/dream audit`, `/dream prune <file>` all work identically to before
- [ ] **Safety rules count**: 7 bullets in the Safety Rules section
- [ ] **Arguments count**: 7 subcommands in the Arguments section
- [ ] Run `/validate` before committing

---

## What NOT to Change (Preserve These)

These are the skill's competitive advantages over alternatives. Do not modify:

- The 4-phase structure (Orient → Signal → Plan/Gate → Execute)
- The approval gate at Phase 3
- The staleness scoring (1-5 tiers)
- The redundancy checking against CLAUDE.md and rules files
- The verification checklist in Phase 4
- The existing safety rules (6 bullets — you're adding a 7th, not replacing)
- The action taxonomy (PRUNE, MERGE, DEDUP, DATE-FIX)
- The `.last-dream` timestamp
- The `ultrathink` directive on line 6

---

## Quick Reference: The Full Plan File

The detailed plan (with exact anchor text for each edit) is also available at:
```
~/.claude/plans/users-samyakjhaveri-desktop-project-see-curried-alpaca.md
```

Read it if you need more detail on any step. This handoff summarizes the same content with added context and reasoning.
