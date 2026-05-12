# Session P Handoff: Compare & Transplant parbench_sam → project_template

> **What is this?** A complete briefing for a fresh Claude Code session to execute the
> transplant plan. Read this top-to-bottom before touching any files.

## The Big Picture

You're working with two repositories on the same machine:

| Repo | Path | What it is |
|------|------|-----------|
| **parbench_sam** | `/Users/samyakjhaveri/Desktop/parbench_sam/` | A mature research project (ParBench) that's been using Claude Code for months. Has lots of custom agents, skills, hooks, and rules. |
| **project_template** | `/Users/samyakjhaveri/Desktop/project_template/` | A **generic template** that bootstraps NEW projects. When you run `bin/init-project.sh`, it creates a fresh project with Claude Code setup already configured. |

**The relationship:** parbench_sam was the ORIGINAL project where Claude Code patterns were developed. Later, the best generic patterns were extracted into project_template. Now we're doing a thorough comparison to find anything we missed.

Think of it like a restaurant's original kitchen (parbench_sam) and a franchise template (project_template). We want to take the generic recipes (agents, skills, hooks) from the original kitchen and put them in the template, while leaving the restaurant-specific stuff (ParBench-specific eval pipeline, spec management, HPC tools) where it is.

---

## What's Already Done (Don't Redo This)

Previous sessions already transplanted a LOT of content. Specifically:

- **All research-flavor skills** are already in `flavors/research/skills/`: paper-write (with LaTeX templates), citation-audit, rebuttal, hypothesis-tree, interpret-results, etc.
- **Shared reference docs** (writing principles, venue checklists) are in `flavors/research/skills/aris-shared-references/`
- **protect-results.sh** hook exists in `flavors/research/hooks/`
- **All shared files** (hooks, agents, rules in the core `.claude/` directory) have already been generalized

**Important nuance:** The flavor system copies hooks as FILES but does NOT register them in `settings.json`. So `protect-results.sh` exists in the research flavor but will NOT run until someone wires it into the settings. This is a known design gap, not your problem to solve today.

---

## What This Session DOES Need to Do

### Summary (9 steps, ~16 file operations)

| Step | What | Why |
|------|------|-----|
| 0 | Create feature branch | Project rules: no direct commits to main |
| 1 | Copy 3 agents to template | diff-reviewer, security-scanner, explorer are useful in ANY project, not just ParBench |
| 2 | Copy 1 skill to template | reflect (structured post-task reflection) is useful anywhere |
| 3 | Add result-immutability hook | Protects experiment results from accidental overwriting |
| 4 | Set up 3-layer memory architecture | memsearch + graphify + built-in memory |
| 5 | Rename aris-shared-references | "aris" is a project-specific name; "shared-references" is generic |
| 6 | Backport fixes to parbench_sam | Fix hardcoded Linux paths, modernize hooks |
| 7 | Update documentation | CLAUDE.md, README, new MEMORY.md doc |
| 8 | Verify everything | Bootstrap test, backport test, grep for contamination |

---

## The Three-Layer Memory Architecture (Why and How)

This is the biggest conceptual addition. Here's why we're doing it:

### The Problem

Claude Code has built-in memory (CLAUDE.md files + auto-memory in `~/.claude/projects/`), but it has limitations:
- **200-line cap** on memory loaded per session (older entries get silently truncated)
- **No semantic search** (Claude reads files linearly, can't search by meaning)
- **No structural understanding** of the codebase (doesn't know how modules connect)

### The Solution: Three Complementary Layers

Think of it like how humans remember things:

| Layer | Tool | Analogy | What it stores |
|-------|------|---------|---------------|
| **1. Static knowledge** | Built-in (CLAUDE.md + rules) | Your textbook notes | Project conventions, coding standards, known issues |
| **2. Session memory** | Memsearch (by Zilliz) | Your journal/diary | What you worked on each day, decisions made, problems solved |
| **3. Codebase map** | Graphify | A building blueprint | How modules connect, which functions are "hubs," dependency chains |

**Why three layers?** They don't overlap:
- Layer 1 tells Claude "always use pytest, never mock the database"
- Layer 2 tells Claude "last Tuesday we decided to switch from REST to GraphQL"
- Layer 3 tells Claude "the auth module connects to 15 other modules, making it a god node"

### Technical Details

**Memsearch** (https://github.com/zilliztech/memsearch):
- Installs as a Claude Code plugin
- After each Claude response, a Haiku model summarizes the conversation turn and saves it to `.memsearch/memory/YYYY-MM-DD.md`
- At session start, recent memories are automatically injected
- Uses ONNX embeddings (runs 100% locally, no API key needed)
- Vector search via Milvus Lite (a local `.db` file — no server needed)
- **Cost: Free** (ONNX is local; Haiku summarization uses your Claude subscription)

**Graphify** (https://github.com/safishamsi/graphify):
- Parses your codebase using Tree-sitter (supports 29 languages)
- Builds a knowledge graph with NetworkX
- Identifies "god nodes" (modules everything depends on)
- Outputs `graphify-out/graph.json` + interactive `graph.html`
- Can run as an MCP server so Claude can query the graph directly
- **Cost: Free** for AST pass; optional API key for semantic analysis of docs/images

**CodeBurn** (https://github.com/getagentseal/codeburn):
- Tracks your AI token spending across 19 tools (Claude Code, Cursor, Copilot, etc.)
- Reads local session data — no proxy, no API keys
- Terminal dashboard showing cost per task, model, project
- **Cost: Free** (MIT license, `npx codeburn` to run)

### Why NOT claude-mem?

We evaluated claude-mem (65K stars) but rejected it because:
1. **Security issue:** Community audit found an unauthenticated HTTP API binding to `0.0.0.0` (exposed on network)
2. **Opaque storage:** SQLite + ChromaDB (you can't easily read/edit memories)
3. **Memsearch is better:** Markdown-first (human-readable), same auto-capture features, no security concerns

---

## Decision Table: What Was Transplanted vs. What Stays

This is the complete classification of every file in parbench_sam's `.claude/` directory.

### Files transplanted to template CORE (generic, useful in any project)

| File in parbench_sam | Destination in template | What it does | Why it's generic |
|---------------------|------------------------|-------------|-----------------|
| `.claude/agents/diff-reviewer.md` | `.claude/agents/diff-reviewer.md` | Reviews git diff for TODO/FIXME, partial implementations, accidental changes | Every project has git diffs to review |
| `.claude/agents/security-scanner.md` | `.claude/agents/security-scanner.md` | Scans for secrets, command injection, unsafe file operations | Security matters in every project |
| `.claude/agents/explorer.md` | `.claude/agents/explorer.md` | Maps files, traces call chains, checks test coverage | Codebase exploration is universal |
| `.claude/skills/reflect/SKILL.md` | `.claude/skills/reflect/SKILL.md` | Structured post-task reflection (surprises, patterns, gotchas) | Self-improvement pattern works anywhere |
| `.claude/hooks/result-immutability.sh` | `.claude/hooks/result-immutability.sh` | Blocks overwriting existing files in `results/` | Experiment result integrity matters everywhere |

### Files already in research flavor (done in prior sessions)

| File | Location in template | Status |
|------|---------------------|--------|
| paper-write (+ 8 LaTeX templates) | `flavors/research/skills/paper-write/` | Already there |
| citation-audit | `flavors/research/skills/citation-audit/` | Already there |
| cite-check | `flavors/research/skills/cite-check/` | Already there |
| paper-review-sim | `flavors/research/skills/paper-review-sim/` | Already there |
| paper-claim-audit | `flavors/research/skills/paper-claim-audit/` | Already there |
| auto-paper-improvement-loop | `flavors/research/skills/auto-paper-improvement-loop/` | Already there |
| rebuttal | `flavors/research/skills/rebuttal/` | Already there |
| interpret-results | `flavors/research/skills/interpret-results/` | Already there |
| hypothesis-tree | `flavors/research/skills/hypothesis-tree/` | Already there |
| shared references (6 files) | `flavors/research/skills/aris-shared-references/` | Already there (needs rename → `shared-references/`) |
| protect-results.sh | `flavors/research/hooks/protect-results.sh` | Already there (not wired in settings.json) |

### Files that STAY in parbench_sam (project-specific)

These are deeply tied to ParBench's domain (HPC benchmark evaluation) and have no generic use:

| Category | Files | Why they're project-specific |
|----------|-------|------------------------------|
| **Eval pipeline** | eval-run, eval-grader, post-eval, overnight-eval, interpret-results | These know about ParBench's LLM evaluation pipeline, result JSON schema, and model configs |
| **Spec management** | spec-check, spec-validator, gen-spec, spec-auditor agent | These work with ParBench's benchmark spec format (JSON files describing CUDA/OpenMP kernels) |
| **HPC tools** | cuda-omp-translator, hpc-code-reviewer | Domain-specific to HPC parallel programming |
| **Protection hooks** | protect-benchmark-sources.sh, protect-eval-results.sh | Guard ParBench-specific directories (Rodinia source, eval results) |
| **Validation agents** | verify-app, regression-checker, rodinia-verifier, test-synthesizer, consistency-checker, eval-batcher | All expect ParBench-specific baselines (135 known errors, 60 Rodinia specs, etc.) |
| **Research artifacts** | mentoring skill, workflow-ref, navigate taxonomy, agentic-coding-guide | Heavily personalized to ParBench/Samyak |
| **Other** | .local-paths, .venv-name, settings.json.bak, agents-archive/ | Local config and historical artifacts |

### StatusLine Config

**Neither repo has a `statusLine` configuration.** The progress bar the user remembers seeing was likely from a Claude Code version-specific UI feature or a plugin, not a settings.json config.

---

## Backport Fixes: What's Wrong in parbench_sam

parbench_sam has several bugs that the template already fixed:

| Bug | Impact | Fix |
|-----|--------|-----|
| **Hardcoded Linux paths** in settings.json | ALL hooks reference `/home/samyak/Desktop/parbench_sam/.claude/hooks/` — on macOS (`/Users/samyakjhaveri/`), NONE of the hooks run. Pre-commit gates, audit logging, result protection are ALL silently disabled. | Replace absolute paths with relative `.claude/hooks/` |
| **Missing Stop hook** | `dream-hook.sh` (memory consolidation reminder) is never triggered because it's not registered as a Stop hook | Add Stop hook section to settings.json |
| **Linux-only `date -d`** in should-dream.sh | `date -d` is a GNU extension. macOS `date` doesn't support it. The dream check silently fails. | Replace with Python datetime parsing (portable) |
| **`$CLAUDE_TOOL_INPUT` env var** in bash-audit-log.sh | Old approach; Claude Code now passes hook data as JSON on stdin | Replace with `PAYLOAD="$(cat)"` approach |
| **Inline hooks using `$CLAUDE_TOOL_INPUT`** in settings.json | The rm-rf blocker and ruff auto-fix hooks use the old env var approach | Replace with stdin reading |

---

## The Implementation Plan

The full step-by-step plan with verification at each step is in:
**`/Users/samyakjhaveri/.claude/plans/ultrathink-read-this-concurrent-grove.md`**

Read that file for exact instructions. Below is a condensed summary.

### Step 0: Create feature branch
```bash
cd /Users/samyakjhaveri/Desktop/project_template
git checkout -b session-p-transplant
```

### Step 1: Transplant 3 agents
- Read each source from parbench_sam, replace `{{PROJECT_ROOT}}` with `$(git rev-parse --show-toplevel)`, remove ParBench references
- Write to `.claude/agents/` in project_template
- Grep for "parbench", "manifest", "harness", "rodinia" to confirm no contamination

### Step 2: Transplant reflect skill
- Read from parbench_sam, add `auto-activate: false`, replace `{{PROJECT_ROOT}}`
- Write to `.claude/skills/reflect/SKILL.md`

### Step 3: Add result-immutability hook
- Create `.claude/hooks/result-immutability.sh` (full content in the plan file)
- Register in `settings.json` PreToolUse section under `Edit|Write` matcher
- The plan file has the complete expected JSON state for verification
- Functional test: create a file in `results/`, try to overwrite it → should block

### Step 4: Memory architecture
- Add `.memsearch.toml` to `seed-config/` (configuration for memsearch)
- Add `.memsearch/` and `graphify-out/` to `.gitignore.tmpl`
- Add tool installation section to `init-project.sh` (between git commit and GitHub remote sections)
- Update `.mcp.json.tmpl` to include graphify MCP server config
- Create `docs/MEMORY.md` documenting the 3-layer architecture
- Add plugin setup instructions to init-project.sh banner

### Step 5: Rename aris-shared-references → shared-references
```bash
git mv flavors/research/skills/aris-shared-references flavors/research/skills/shared-references
```
Then update any references in `flavors/research/README.md`.

### Step 6: Backport to parbench_sam
- Fix all hardcoded `/home/samyak/` paths → `.claude/hooks/`
- Add Stop hook for dream-hook.sh
- Fix `should-dream.sh` date parsing (Linux → portable Python)
- Copy template's `bash-audit-log.sh` over parbench_sam's old version
- Modernize inline hooks in settings.json (`$CLAUDE_TOOL_INPUT` → stdin)

### Step 7: Update docs
- Add memory architecture reference to `CLAUDE.md`
- Update research flavor README for the rename

### Step 8: Verify
- Run `bin/verify-template.sh` (expect ALL OK)
- Run `bin/init-project.sh /tmp/test-session-p --flavor research`
- Check all new files exist, are executable where needed, and contain no ParBench references
- Verify parbench_sam backports: no hardcoded paths, valid JSON, valid shell syntax

---

## Skills to Use During Implementation

| When | Skill | Why |
|------|-------|-----|
| Start of session | `/catchup` | Get current git status, recent commits, memory state |
| Steps 1-3 | Direct Read/Write/Edit | Simple file operations |
| Step 4 | Manual careful editing | init-project.sh is the bootstrap — don't break it |
| After all steps | `/validate` | Run the validation loop before committing |
| After validate passes | `/commit` | Create a conventional commit |
| If something breaks | `/fix-bug` | Structured reproduce→diagnose→fix workflow |

---

## Files to Touch (Complete List)

### NEW files to create in project_template:
1. `.claude/agents/diff-reviewer.md`
2. `.claude/agents/security-scanner.md`
3. `.claude/agents/explorer.md`
4. `.claude/skills/reflect/SKILL.md`
5. `.claude/hooks/result-immutability.sh`
6. `seed-config/.memsearch.toml`
7. `docs/MEMORY.md`

### Files to EDIT in project_template:
1. `.claude/settings.json` (add PreToolUse Edit|Write hook)
2. `bin/init-project.sh` (add tool install section + banner update)
3. `seed-config/.gitignore.tmpl` (add .memsearch/ and graphify-out/)
4. `seed-config/.mcp.json.tmpl` (add graphify MCP server)
5. `CLAUDE.md` (add memory doc reference)

### Files to RENAME in project_template:
1. `flavors/research/skills/aris-shared-references/` → `shared-references/`

### Files to EDIT in parbench_sam:
1. `.claude/settings.json` (fix paths + modernize inline hooks + add Stop hook)
2. `.claude/hooks/should-dream.sh` (portable date parsing)
3. `.claude/hooks/bash-audit-log.sh` (stdin-based approach)

---

## Red Flags to Watch For

- **ParBench contamination:** After every copy, grep for `parbench|ParBench|Rodinia|HeCBench|harness|manifest|spec`. If any hit, you copied too much.
- **Broken JSON:** After editing `settings.json`, always validate with `python3 -c "import json; json.load(open('...'))"`.
- **Non-executable hooks:** After creating `.sh` files, `chmod +x` them. The pre-commit gate will fail if hooks aren't executable.
- **Bootstrap regression:** Always test with `bin/init-project.sh /tmp/test --flavor research` after changes. If bootstrap breaks, STOP and fix before continuing.
