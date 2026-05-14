---
name: dream
description: "Memory consolidation — performs a reflective pass over Claude's memory files, synthesizing recent session learnings into organized, deduplicated memories with line-limit enforcement. Mirrors Anthropic's unreleased /dream command. Use when the user says 'dream', 'consolidate memory', 'clean up memory', 'organize memories', 'memory maintenance', or any request to tidy/consolidate/optimize Claude's memory files."
---

# Dream: Memory Consolidation

You are performing a dream — a reflective pass over your memory files. Synthesize what you've learned recently into durable, well-organized memories so that future sessions can orient quickly.

## Targeting

The user can specify a scope. Parse the argument after `/dream`:

| Command | Target |
|---|---|
| `/dream` (no args) | Current project memory only |
| `/dream user` | User-level memory only (`~/.claude/projects/C--Users-Chase/memory/`) |
| `/dream all` | Both user-level AND current project memory (run phases on each separately, report combined results) |

## Locating the Memory Directory

**User-level memory** is always at:
```
~/.claude/projects/C--Users-Chase/memory/
```

**Project-level memory** — find it by running:
```bash
ls ~/.claude/projects/
```

Match the current working directory to the project folder name (dashes replace path separators, e.g. `C:\Users\Chase\the vault` → `C--Users-Chase-The-Vault`). The memory directory is at:
```
~/.claude/projects/<matched-project>/memory/
```

Session transcripts (JSONL files) are in the parent directory of the memory folder.

If the user specifies a different project or path, use that instead.

**Index max lines:** 200

---

## Phase 1 — Orient

- `ls` the memory directory to see what already exists
- Read `MEMORY.md` to understand the current index
- Skim existing topic files so you improve them rather than creating duplicates
- If `logs/` or `sessions/` subdirectories exist, review recent entries there

## Phase 2 — Gather Recent Signal

Look for new information worth persisting. Sources in rough priority order:

1. **Daily logs** (`logs/YYYY/MM/YYYY-MM-DD.md`) if present — these are the append-only stream
2. **Existing memories that drifted** — facts that contradict something you see in the codebase now
3. **Transcript search** — if you need specific context (e.g., "what was the error message from yesterday's build failure?"), grep the JSONL transcripts for narrow terms:

```bash
grep -rn "<narrow term>" ~/.claude/projects/<project>/ --include="*.jsonl" | tail -50
```

Don't exhaustively read transcripts. Look only for things you already suspect matter.

## Phase 3 — Consolidate

For each thing worth remembering, write or update a memory file at the top level of the memory directory. Follow the memory file format:

```markdown
---
name: {{memory name}}
description: {{one-line description — used to decide relevance in future conversations, so be specific}}
type: {{user, feedback, project, reference}}
---

{{memory content}}
```

### Memory types
- **user** — role, goals, preferences, knowledge
- **feedback** — guidance on approach (what to avoid, what to keep doing). Structure: rule, then **Why:** and **How to apply:**
- **project** — ongoing work, goals, initiatives, bugs. Structure: fact/decision, then **Why:** and **How to apply:**
- **reference** — pointers to external resources

### What NOT to save
- Code patterns, architecture, file paths (derivable from code)
- Git history (use git log)
- Debugging solutions (fix is in the code)
- Anything in CLAUDE.md files
- Ephemeral task details

### Focus on
- Merging new signal into existing topic files rather than creating near-duplicates
- Converting relative dates ("yesterday", "last week") to absolute dates so they remain interpretable after time passes
- Deleting contradicted facts — if today's investigation disproves an old memory, fix it at the source

## Phase 4 — Prune and Index

Update `MEMORY.md` so it stays under 200 lines. It's an **index**, not a dump — link to memory files with one-line descriptions. Never write memory content directly into it.

- Remove pointers to memories that are now stale, wrong, or superseded
- Demote verbose entries: keep the gist in the index, move the detail into the topic file
- Add pointers to newly important memories
- Resolve contradictions — if two files disagree, fix the wrong one

---

## Output

Return a brief summary of what you consolidated, updated, or pruned. Format it as:

```
## Dream Complete — [scope: project / user / all]

### Consolidated
- [what was merged/created]

### Updated
- [what was modified]

### Pruned
- [what was removed or cleaned up]

### No Change
- [if memories are already tight, say so]
```
