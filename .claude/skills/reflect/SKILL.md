---
name: reflect
auto-activate: false
description: Structured post-task reflection — surprises, pattern proposals, prompt improvements, gotchas to record. Use at the end of a significant session, after a debugging marathon, or when patterns emerged that should update CLAUDE.md or .claude/rules/.
---

# Structured Reflection

After completing a significant task, generate a structured reflection capturing
surprises, patterns, and gotchas for future sessions. Inspired by Addy Osmani's
REFLECTION.md pattern — turning tacit knowledge into durable project memory.

**Trigger:** When user types `/reflect` or `/reflect <topic>`

## Arguments

- `$ARGUMENTS` — optional topic string (e.g., `auth-refactor`, `test-flakiness`).
  If omitted, the topic is derived from the most recent git diff or conversation context.

## Prerequisites

- Work must be done in the current session (git diff or recent commits to reflect on)

## Workflow

### Phase 1: Gather Context

Read the current session's work to understand what was done:

```bash
cd "$(git rev-parse --show-toplevel)"

# What changed in this session?
echo "=== UNCOMMITTED CHANGES ==="
git diff --stat HEAD

echo "=== RECENT COMMITS (last 5) ==="
git log --oneline -5

echo "=== FILES CHANGED ==="
git diff --name-only HEAD
```

If there are uncommitted changes, use `git diff HEAD` to understand the substance.
If changes are already committed, use `git diff HEAD~3..HEAD` to see recent work.

**Also read the conversation context** — identify moments of surprise, course corrections,
failed approaches, or non-obvious decisions made during the session.

### Phase 2: Derive Topic

If `$ARGUMENTS` provides a topic, use it directly (slugified for the filename).

If no topic is provided, derive one from:
1. The most-changed directory or file pattern (e.g., `api-migration`, `config-cleanup`)
2. The nature of the work (e.g., `debugging`, `new-feature`, `dependency-update`)
3. The primary insight or surprise (e.g., `db-schema-discovery`)

The topic should be 2-4 words, hyphenated, descriptive.

### Phase 3: Generate Reflection

Write a structured reflection with exactly these four sections:

#### Section 1: What Surprised Me
- List 1-3 unexpected findings from the session
- Focus on things that contradicted assumptions or revealed hidden complexity
- Include specific file paths, line numbers, or error messages where relevant
- Ask: "What would I have done differently if I'd known this at the start?"

#### Section 2: Pattern Proposal
- Identify ONE concrete pattern or convention that should be codified
- Specify exactly where it should go: `CLAUDE.md`, a specific `.claude/rules/` file, or a new rule file
- Write the proposed text (ready to copy-paste into the target file)
- Explain WHY this pattern matters — what failure does it prevent?

#### Section 3: Prompt Improvement
- Identify ONE way the task prompt (or session setup) could have been better
- Was context missing? Were instructions ambiguous? Did exploration waste tokens?
- Write the improved prompt fragment (concrete, not abstract)

#### Section 4: Gotcha Discovered
- Document ONE non-obvious issue found during the session
- Include: the symptom, the root cause, and the fix (or workaround)
- If it's already in `known-issues.md`, note that and suggest any updates needed
- If it's NEW, flag it explicitly: "NEW GOTCHA — not yet documented"

### Phase 4: Write Output

Create the output directory if it doesn't exist, then write the reflection:

```bash
mkdir -p docs/reflections
```

Write the reflection to `docs/reflections/YYYY-MM-DD-<topic>.md` using today's date
and the derived or provided topic slug.

File format:

```markdown
# Reflection: <Topic>

**Date:** YYYY-MM-DD
**Session work:** <1-line summary of what was done>
**Files touched:** <count> files in <primary directories>

## What Surprised Me

- <surprise 1>
- <surprise 2>

## Pattern Proposal

**Target:** `<file path where this should be added>`

\```
<proposed text, ready to copy-paste>
\```

**Why:** <explanation of what failure this prevents>

## Prompt Improvement

**Original approach:** <what the prompt/setup was>
**Better approach:** <what it should have been>

\```
<improved prompt fragment>
\```

## Gotcha Discovered

**Symptom:** <what went wrong or was confusing>
**Root cause:** <why it happened>
**Fix:** <what resolved it>
**Status:** NEW GOTCHA / Already in known-issues.md (line N)
```

### Phase 5: Suggest Next Actions

After writing the reflection, present a brief summary to the user:

```
=== REFLECTION WRITTEN ===

File: docs/reflections/YYYY-MM-DD-<topic>.md

Suggested actions:
  [ ] Review pattern proposal for <target file>
  [ ] Add gotcha to known-issues.md (if NEW)
  [ ] Consider running /dream to consolidate learnings into memory

No auto-updates made. You decide what to codify.
```

**Important:** The reflection skill NEVER auto-updates CLAUDE.md or rules files.
It only suggests. The user is the decision maker on what becomes project policy.

## Context Management

This skill reads git state and conversation context. It should NOT launch subagents
or perform deep exploration. The reflection is generated from what's already in context.

Total output to main conversation: the reflection file path + the 6-line summary above.
The reflection content itself is written to disk, not pasted into the conversation.
