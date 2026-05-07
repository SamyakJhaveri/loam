---
name: dream
description: Memory consolidation for ~/.claude/projects memory files. Use after major milestones, after 5+ sessions without consolidation, when memory feels stale, or before long breaks. Runs 4-phase audit→plan→approval→execute; subcommands `audit` (read-only) and `prune <file>` (targeted).
---

# Memory Consolidation (Dream)

Performs a reflective consolidation pass over auto-memory files — the manual
equivalent of Anthropic's unreleased Auto-Dream feature. Synthesizes recent
learnings into durable, well-organized memories so future sessions orient quickly.

Based on: Anthropic's `agent-prompt-dream-memory-consolidation.md` (v2.1.83)
Reference: github.com/grandamenium/dream-skill

**Trigger:** `/dream`, `/dream audit`, or `/dream prune <file>`

## Arguments

- `$ARGUMENTS` — one of:
  - (empty) or `full` — Full 4-phase consolidation (read-only until user approves)
  - `audit` — Phases 1-2 only: read-only health report
  - `prune <filename>` — Targeted prune of a single memory file

## Configuration

```
MEMORY_DIR=~/.claude/projects/<project-path-slug>/memory  # Auto-detect: encode project root path
INDEX_FILE=MEMORY.md
INDEX_MAX_LINES=200
INDEX_MAX_SIZE=25KB
```

Session transcripts live alongside the memory directory as JSONL files.
Grep them narrowly — never read whole transcript files.

---

## Phase 1 — Orient

Read the memory directory to understand current state. **All read-only.**

1. Run `ls -la $MEMORY_DIR/` to see all files with sizes and modification dates
2. Count total lines: `wc -l $MEMORY_DIR/*.md`
3. Read `$MEMORY_DIR/MEMORY.md` — note line count, structure, and all linked files
4. For each file listed in MEMORY.md, verify it exists on disk (**detect phantoms**)
5. For each `.md` file on disk in the memory dir, verify it appears in MEMORY.md (**detect orphans**)
6. Read each topic file's frontmatter (first 10 lines) to catalog: name, description, type

**Output a table:**

```
=== MEMORY HEALTH REPORT ===

| # | File | Lines | Type | Modified | In Index? | Notes |
|---|------|-------|------|----------|-----------|-------|
| 1 | MEMORY.md | 42 | index | Mar 25 | — | INDEX |
| 2 | user_working_style.md | 18 | user | Mar 19 | ✓ | |
| ... | ... | ... | ... | ... | ... | ... |

TOTALS: N files, N total lines
INDEX: N/200 lines (N% capacity)
ORPHANS: [list or "none"]
PHANTOMS: [list or "none"]
```

## Phase 2 — Gather Signal

For each memory file, evaluate along four dimensions. **All read-only.**

### 2A. Staleness Score (1–5)

Assign each file a staleness tier:

| Score | Tier | Meaning | Examples |
|-------|------|---------|----------|
| 1 | Permanent | Rarely changes — user prefs, hard rules, design decisions | `feedback_no_benchmark_edits.md`, `user_working_style.md` |
| 2 | Active | Current state that changes often — sprint progress, eval results | `project_paper_writing.md` |
| 3 | Completed | Done but worth keeping for context — resolved decisions | `project_m11_resolution.md` |
| 4 | Historical | Session logs, past sprint days, superseded comparison tables | Session-by-session logs in sprint files |
| 5 | Stale | Dates passed, contradicted by newer files, fully duplicated elsewhere | — |

### 2B. Redundancy Check

For each memory file, search for the **same information** in:
- `CLAUDE.md` (project root) — `grep` for key phrases
- `.claude/rules/*.md` — especially `known-issues.md`, `workflow.md`, `evaluation.md`
- Other memory files

Flag content appearing in 2+ locations. Identify the **canonical source** (usually a rules file
or CLAUDE.md, since those are loaded with higher priority).

### 2C. Date and Accuracy Audit

- Find relative date references ("last week", "yesterday", "recently") → flag for absolute conversion
- Find past dates describing future plans (e.g., "March 24: Week 1 end" when today is past March 24)
- Cross-check key factual claims against current state:
  - Spec counts: `ls specs/*.json | wc -l` vs. what memory claims
  - KNOWN_FAIL list: `.claude/rules/known-issues.md` vs. memory
  - Model selection: has the 4-model directive changed?

### 2D. Size Check

- Flag files > 80 lines as candidates for **pruning or splitting**
- Flag files < 10 lines as candidates for **merging** into a related file

### Output the Signal Report

```
=== SIGNAL ANALYSIS ===

| # | File | Staleness | Redundant With | Date Issues | Size Flag |
|---|------|-----------|---------------|-------------|-----------|
| 1 | project_sc26_sprint.md | 4-Historical | eval tables in paper_writing.md | 3 past-future dates | >80 lines |
| ... | ... | ... | ... | ... | ... |

RECOMMENDED ACTIONS: N prune, N merge, N dedup, N date-fix
```

**If `$ARGUMENTS` is `audit`, STOP HERE. Display both reports and exit.**

---

## Phase 3 — Consolidate (Present Plan, Do NOT Execute)

Based on Phase 2 analysis, build a concrete consolidation plan. Group actions by type:

### PRUNE actions (staleness >= 4)

For each file to prune:
- Show the specific sections to remove (line ranges + content preview)
- Show the proposed "after" content
- Justify: "This info is in git history at commit X" or "Superseded by file Y"

Historical session logs that exist in git history should be removed from memory —
they're recoverable via `git log`.

### MERGE actions (files < 10 lines on related topics)

- Propose which files to combine
- Show the target filename
- Show the proposed merged content

### DEDUP actions (redundant content)

Convert duplicated content to a cross-reference pointer. Template:
```
This feedback is now codified in [canonical source]. See `<path>` for current details.

**Why (original motivation):** <preserve the why — it may not be in the canonical source>

**How to apply:** <keep the application guidance if unique to this memory>
```

**Always preserve the WHY even when removing the WHAT.**

### DATE FIX actions

List each conversion: `"March 24: Week 1 end"` → `"2026-03-24: Week 1 end (completed)"`

### INDEX REBUILD

Propose the new MEMORY.md with:
- Semantic grouping: **Permanent Knowledge** / **Active State** / **Completed Decisions**
- Each entry: one line, <150 chars: `- [Title](file.md) — one-line hook`
- Total must stay under 200 lines

### Summary Table

```
=== CONSOLIDATION PLAN ===

| Action | File | Before | After | Change |
|--------|------|--------|-------|--------|
| PRUNE | project_sc26_sprint.md | 173 lines | ~50 lines | -123 lines |
| MERGE | project_azure_disabled.md → project_model_selection.md | 11 lines | DELETE | -11 lines |
| ... | ... | ... | ... | ... |

TOTAL: N files → M files, X lines → Y lines (Z% reduction)
```

### CRITICAL GATE

**STOP HERE. Display the full plan and WAIT FOR USER APPROVAL.**

Do NOT execute any changes without explicit go-ahead from the user.
Remind: "Memory files at `~/.claude/...` are NOT in git — deletions are permanent."

---

## Phase 4 — Execute and Index (After Approval Only)

Execute only the actions the user approved:

1. **Prune:** Use Edit tool for partial changes, Write for full rewrites
2. **Merge:** Write the merged file, then delete (or note) the absorbed file
3. **Dedup:** Edit to replace duplicated content with cross-reference pointers
4. **Date fixes:** Edit each relative date to absolute
5. **Rebuild MEMORY.md:** Write the new index
6. **Write timestamp:**
   ```bash
   echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > $MEMORY_DIR/.last-dream
   ```

### Post-Execution Report

```
=== DREAM COMPLETE ===

Files modified:  N
Files deleted:   N
Files merged:    N
Lines before:    X
Lines after:     Y (Z% reduction)
MEMORY.md:       N lines (of 200 max)
.last-dream:     <timestamp>

Next recommended dream: ~1 week or after next major milestone
```

### Verification Checklist

Run these checks and report pass/fail:

- [ ] `MEMORY.md` line count < 200
- [ ] Every file in `$MEMORY_DIR/*.md` is listed in MEMORY.md
- [ ] Every entry in MEMORY.md points to an existing file on disk
- [ ] No duplicate content between memory files and `.claude/rules/`
- [ ] All dates are absolute (no "yesterday", "last week", "recently")
- [ ] `.last-dream` file exists with current UTC timestamp
- [ ] Key information still accessible: spec counts, model selection, hard rules, user prefs

---

## Safety Rules

- **Never delete without showing** — always present what will be lost in Phase 3
- **Never touch CLAUDE.md or .claude/rules/** — those are managed separately
- **Preserve the WHY** — when converting to cross-references, keep the motivation
- **Memory files are NOT in git** — deletions at `~/.claude/` are permanent; warn user
- **`/dream audit` is always safe** — purely read-only, no side effects
- **If `prune <file>` mode:** Read the file, score it (Phase 2), propose changes (Phase 3),
  wait for approval, then execute (Phase 4). Same 4-phase flow, scoped to one file.
