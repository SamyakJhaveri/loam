# HANDOFF: Replace Graphify with CodeGraphContext + Semble, Add Lean Research Integrity Layer

> **For:** Fresh Claude Code session. **Project:** Loam (`/Users/samyakjhaveri/Desktop/loam`). **Date:** 2026-05-21.
> **Branch:** main (commit directly, no feature branches).

---

## Goal

Replace Graphify (the code knowledge graph MCP server) with two complementary tools in the Loam Copier template, and add a lean research integrity layer to the `_research/` flavor.

**Two new tools:**
- **CodeGraphContext** — structural code graph (call chains, class hierarchies, symbol resolution). Embedded KuzuDB, 20 languages. GitHub: `CodeGraphContext/CodeGraphContext`. Pure MCP server, zero scaffolding.
- **Semble** — semantic code search (embedding-based similarity). Tree-sitter chunking, 19+ languages, MIT. GitHub: `MinishLab/semble`. Pure MCP server, zero scaffolding.

**Lean integrity layer (research flavor only):**
- A behavioral rules file (`research-consistency.md`) with 4 rules preventing research consistency failures
- A starter research changelog (`CHANGELOG.research.md.jinja`)

---

## Current Progress

**Done (this session):**
- Explored the `better_use_of_graphify/` directory (5 files documenting ParBench project failures with Graphify)
- Assessed all proposals: identified 9 highly effective, 6 moderate, and 6 questionable
- Verified GitNexus behavior from source code — confirmed `--index-only` flag exists but it's still a footgun for template users
- Compared 4 candidate tools: GitNexus, CodeGraphContext, Semble, AgentMemory
- Ran adversarial plan review (plan-reviewer agent) — caught 2 critical, 4 high issues in the first draft
- Cleaned ParBench-specific content from cite-check skill (in plan, not yet executed)
- Final plan written and approved

**Not done (for implementing session):**
- All file edits (10 files across 2 commits)
- Template render verification (`bin/verify-template.sh`)
- Validation (`/validate`) and critique (`/session-critique`)

---

## What Worked (Approaches That Succeeded)

1. **Tool verification from source repos** — The initial plan assumed GitNexus was safe. Deep-diving the actual repo revealed it overwrites CLAUDE.md and AGENTS.md by default. This changed the tool choice.
2. **Adversarial plan review** — The plan-reviewer caught that shipping `pipeline_version.py` and `validate-claims.sh` in a template is over-engineering (application code, not template infrastructure). Cut the plan from 15 files to 10.
3. **Category separation** — Recognizing that the 4 candidate tools solve 3 different problems (code graph vs. semantic search vs. session memory) avoided comparing apples to oranges.

## What Didn't Work (Don't Repeat These)

1. **Trusting LLM-generated research docs as ground truth** — The `better_use_of_graphify/graphify_alternative_setup.md` was itself LLM-generated and contained unverified claims about npm package names and CLI flags. Always verify tool behavior from the actual repo.
2. **First draft was over-engineered** — 15 files, including Python modules, bash hooks with underdefined append-only logic, and Jinja expressions that would break (`{{ now() }}` is not a default Jinja2 function). The lean version (10 files, 2 creates) is both safer and sufficient.
3. **Shipping application code in a template** — `pipeline_version.py` (80-line Python module with hash computation) is project-specific implementation, not a template concern. Templates ship conventions (rules, changelogs), not implementations.

---

## Why These Tools Were Chosen (Decision Context)

### Why NOT GitNexus (despite 28K stars)

GitNexus `npx gitnexus analyze` auto-generates CLAUDE.md, AGENTS.md, skills, and hooks by default. The `--index-only` flag prevents this, but Loam is a Copier template that generates these files — if a user runs `analyze` without the flag, Loam's rendered artifacts are destroyed. This is a template-destroying footgun. CodeGraphContext and Semble never write project files, period.

### Why NOT AgentMemory

AgentMemory is a session memory system (records tool calls, file accesses, decisions across sessions). It does NOT parse ASTs, build call graphs, or provide code structural intelligence. It's a different tool category entirely — useful but not a Graphify replacement.

### Why CodeGraphContext + Semble (two tools, not one)

They solve complementary problems:
- CodeGraphContext: "What calls this function? What's the blast radius of this change?" (structural graph queries)
- Semble: "Find code that does something like X" (natural-language semantic search)

Neither alone covers both needs. Together they replace Graphify's structural role and add semantic search that Graphify never had.

### Why lean integrity layer (2 files, not 5)

The plan-reviewer's critique: a Copier template should ship conventions, not implementations.
- **Ships in template:** behavioral rules (research-consistency.md) + changelog format (CHANGELOG.research.md.jinja) — these are conventions that cost nothing and prevent the highest-impact failures
- **Does NOT ship:** pipeline_version.py, claims.jsonl, validate-claims.sh — these are application code that belongs in specific projects, not a generic template. They may move to `cultivation/marketplace/` later as an optional skill pack.

---

## Implementation Plan

**Two commits, each independently verifiable.** Use `/commit` for conventional commits.

### Commit 1: Graphify → CodeGraphContext + Semble (6 files)

#### Step 1.1 — Edit `seed/.mcp.json.jinja`

Replace the entire file. Current file has a `graphify` MCP server block. New content:

```json
{
  "_comment": "{{ project_name }} MCP servers. CodeGraphContext (code graph) and Semble (semantic search) provide code intelligence. Memory MCP stores structured facts. See docs/MEMORY.md.",
  "mcpServers": {
    "codegraphcontext": {
      "type": "stdio",
      "command": "cgc",
      "args": ["mcp-server"],
      "env": {
        "CGC_DB_TYPE": "kuzu",
        "CGC_DB_PATH": ".codegraphcontext/db"
      }
    },
    "semble": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "semble[mcp]", "semble"]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "${PWD}/.claude-memory/knowledge-graph.json"
      }
    }
  }
}
```

**Verify:** `python3 -c "import json; json.load(open('seed/.mcp.json.jinja'))"` parses cleanly.

#### Step 1.2 — Edit `seed/.gitignore.jinja` (lines 50-51)

Replace:
```
# Graphify (codebase knowledge graph — rebuild from source)
graphify-out/
```
With:
```
# CodeGraphContext (code graph — rebuild with cgc setup)
.codegraphcontext/
```

**Verify:** `grep -n "graphify" seed/.gitignore.jinja` returns nothing.

#### Step 1.3 — Edit `.gitignore` (line 56)

Remove: `graphify-out/cache/`
Add: `.codegraphcontext/`

**Verify:** `grep "graphify" .gitignore` returns nothing.

#### Step 1.4 — Edit `docs/MEMORY.md`

Four changes in this file:

1. **Line 11** — L3 layer table row. Replace Graphify entry with:
```
| L3 — Codebase map | [CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext) + [Semble](https://github.com/MinishLab/semble) | Structural code graph (call chains, hierarchies) + semantic code search (embedding similarity) | How is the code organized; what depends on what? What code is related to X? |
```

2. **Lines 52-69** — Replace the entire "## Layer 3 — Graphify" section with:
```markdown
## Layer 3 — CodeGraphContext + Semble (code intelligence)

Two complementary MCP servers providing structural and semantic code intelligence.

**CodeGraphContext** — AST-derived code graph stored in embedded KuzuDB. Provides call-chain traversal, class hierarchies, symbol resolution, and relationship analysis across 20 languages. Runs as a pure MCP server; never writes project files beyond `.codegraphcontext/`.

**Semble** — Semantic code search using embeddings (model2vec) with tree-sitter code-aware chunking. Finds code similar to natural-language queries. In-memory indexes, session-scoped. Runs as a pure MCP server; writes no project files.

### Setup

CodeGraphContext:

    pip install codegraphcontext   # or: uv tool install codegraphcontext
    cgc setup                      # index the codebase; produces .codegraphcontext/

Semble:

    pip install semble             # or: uv tool install semble
    # No setup needed — indexes on first MCP query. Optional pre-index:
    semble /path/to/project

Both are wired in `.mcp.json` by default. Storage:
- `.codegraphcontext/` — graph database (gitignored, rebuild with `cgc setup`)
- Semble indexes are in-memory (no persistent files)
```

3. **Lines 96-100** — In the `.gitignore` reference section, replace `graphify-out/` with `.codegraphcontext/`.

4. **Line 45** — Replace "registers Graphify" with "registers CodeGraphContext, Semble,".

**Verify:** `grep -i "graphify" docs/MEMORY.md` returns nothing.

#### Step 1.5 — Edit `docs/BOOTSTRAP.md`

1. **Line 45:** Replace `registers Graphify and the Knowledge-Graph Memory MCP` with `registers CodeGraphContext, Semble, and the Knowledge-Graph Memory MCP`.

2. **Line 85:** Replace:
```
3. If using Graphify, run `graphify .` after the first non-trivial commit to seed the codebase map.
```
With:
```
3. Run `cgc setup` after the first non-trivial commit to build the code graph index.
```

**Verify:** `grep -i "graphify" docs/BOOTSTRAP.md` returns nothing.

#### Step 1.6 — Clean up `.claude/settings.local.json` (housekeeping only)

This file is excluded from Copier renders (listed in `copier.yml` `_exclude`). In the `disabledMcpjsonServers` array, replace `"graphify"` with `"codegraphcontext"` and `"semble"` (or remove if you want them enabled locally).

#### Post-Commit-1 Verification

```bash
grep -ri "graphify" seed/          # Expected: zero results
bin/verify-template.sh             # Expected: ALL OK
```

Then: `/commit` with message like `refactor: replace Graphify with CodeGraphContext + Semble MCP servers`

---

### Commit 2: Lean Research Integrity Layer (4 files)

#### Step 2.1 — Create `seed/_research/rules/research-consistency.md`

**New file.** Ships only when `is_research=true`.

```markdown
# Research consistency rules

> Always loaded in research projects. Prevents the four highest-impact consistency failures.

## 1. Never cite numbers from memory

Do NOT use any number from memory, previous messages, or knowledge graph nodes.
For any statistic: compute from raw data files or ask the user for the source.
Say "Let me check the result files for this number" — never "Based on the results, the rate is approximately X%."

## 2. Claim-first paper writing

When writing any paper section:
1. Identify what claims the section needs
2. Find or compute evidence for each claim from raw data
3. Write prose referencing the evidence

Never write prose first and backfill numbers — that path leads to confirmation bias.

## 3. Code graph is structural, not authoritative

CodeGraphContext answers: "What connects X to Y in code structure?"
It does NOT answer: "Is X correct?" or "What value does X produce?" or "Is X the current approach?"
Never use graph node descriptions as paper text. Never navigate the graph to find statistics.

## 4. Explicit uncertainty over silent assumptions

When you cannot find a number or verify a claim, say so:
- "I can't find a result file for this statistic. Should I compute it, or can you point me to the source?"
- "The changelog doesn't mention when this metric was added. Can you confirm?"

Never fill gaps with plausible-sounding guesses. Asking takes seconds; guessing wrong costs hours of rework.
```

**Verify:** `wc -w seed/_research/rules/research-consistency.md` — should be ~180-220 words.

#### Step 2.2 — Create `seed/_research/seed-docs/CHANGELOG.research.md.jinja`

**New file.** Starter template rendered to project root when `is_research=true`.

```markdown
# Research Changelog — {{ project_name }}

> Append-only. Tracks **scientific** changes — methodology, metrics, validation logic.
> Git tracks code changes; this file tracks what those changes **mean for results**.
> Read this file before any paper-writing task.

<!-- Add entries in reverse chronological order (newest first). -->
<!-- Each entry documents a change that affects result validity. -->

## YYYY-MM-DD — Pipeline v1 (initial)

- **Changed:** Initial evaluation framework established
- **Why:** Project bootstrap
- **Impact:** Baseline — no prior results affected
- **Status:** Initial setup complete
```

**Verify:** The only Jinja variable is `{{ project_name }}` — consistent with existing seed-docs patterns.

#### Step 2.3 — Edit `seed/_research/skills/cite-check/SKILL.md` (lines 57-68)

Replace the ParBench-specific "Project Context" section with generic placeholders:

```markdown
## Project Context

- **Paper draft:** `docs/paper_draft.md` (default) or user-specified path
- **Result directories:** `results/evaluation/*/` — organized by model/configuration
- **Analysis outputs:** `analysis/` — computed tables, figures, reports
- Check CLAUDE.md for canonical directory structure and known caveats
- Check `.claude/rules/known-issues.md` for exclusions and known failures
- If `CHANGELOG.research.md` exists, read it before verifying — it documents which results are current
```

**Verify:** `grep -c "claude-sonnet\|gemini-2.5-flash\|groq-llama\|together-qwen" seed/_research/skills/cite-check/SKILL.md` returns 0.

#### Step 2.4 — Edit `seed/_research/rules/research-memory.md`

Add one line to the existing `[LEARN:tag]` list:
```
- `[LEARN:pipeline]` — pipeline/methodology changes that invalidate prior results (also record in `CHANGELOG.research.md`)
```

**Verify:** `grep "LEARN:pipeline" seed/_research/rules/research-memory.md` returns the new line.

#### Post-Commit-2 Verification

```bash
bin/verify-template.sh             # Expected: ALL OK (both default and is_research=true)
```

Then: `/session-critique` → `/validate` → `/commit` with message like `feat(research): add consistency rules and research changelog starter`

---

## Must NOT

- Must NOT modify existing hook scripts (`protect-results.sh`, `validate-experiment-config.sh`)
- Must NOT change default (non-research) render output beyond the Graphify→CGC+Semble swap
- Must NOT add always-loaded rules exceeding 200 tokens to research-consistency.md
- Must NOT ship `pipeline_version.py`, `claims.jsonl`, or `validate-claims.sh` in the template
- Must NOT modify `copier.yml` `_tasks` (new seed-docs copy via existing `cp _research/seed-docs/* .` task)
- Must NOT add ParBench-specific paths, model names, or project details to any template file

## Skills to Use

- **`/validate`** after each commit (Pipeline Gate)
- **`/session-critique`** before final commit
- **`bin/verify-template.sh`** as primary verification (tests both Copier flavors)
- **`/commit`** for conventional commits (one per part)

## File Summary

| Action | File | Commit |
|--------|------|--------|
| **Edit** | `seed/.mcp.json.jinja` | 1 |
| **Edit** | `seed/.gitignore.jinja` (lines 50-51) | 1 |
| **Edit** | `.gitignore` (line 56) | 1 |
| **Edit** | `docs/MEMORY.md` (L3 section, ~20 lines) | 1 |
| **Edit** | `docs/BOOTSTRAP.md` (2 lines) | 1 |
| **Edit** | `.claude/settings.local.json` (housekeeping) | 1 |
| **Create** | `seed/_research/rules/research-consistency.md` | 2 |
| **Create** | `seed/_research/seed-docs/CHANGELOG.research.md.jinja` | 2 |
| **Edit** | `seed/_research/skills/cite-check/SKILL.md` (lines 57-68) | 2 |
| **Edit** | `seed/_research/rules/research-memory.md` (1 line) | 2 |

**Total: 10 files (6 edits, 2 creates, 2 minor edits). Two commits.**

---

## Reference: The `better_use_of_graphify/` Directory

This untracked directory contains the research that motivated this work. It is NOT part of the implementation — it's context for understanding the decisions above. The user may choose to delete it after implementation.

| File | What it contains |
|------|------------------|
| `graphify_alternative_setup.md` | 8-line executive summary recommending GitNexus (superseded by our CodeGraphContext + Semble decision) |
| `CLAUDE-CODE-BEHAVIORAL-RULES.md` | 10 behavioral rules — we adopted the 4 highest-value ones in `research-consistency.md` |
| `RESEARCH-WORKFLOW-MASTERGUIDE.md` | ~1300-line comprehensive research workflow guide from ParBench. Reference material, not implemented. |
| `IMPLEMENTATION-TEMPLATES.md` | ~1200 lines of drop-in code templates (pipeline_version.py, claims.jsonl, etc.). Not shipped — application code, not template infrastructure. |
| `Claude-Code-Research-Workflow-ToolStack.xlsx` | 7-sheet tool comparison matrix. Used during evaluation, now superseded by our decisions. |
