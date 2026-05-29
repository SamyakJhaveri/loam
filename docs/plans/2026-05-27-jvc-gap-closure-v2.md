You are a contributor to the Loam Copier template (this repo). Codify the remaining JVC
constraint learnings into Loam's rule files, reference docs, and one skill. Done = the 11
file changes below are applied exactly, `bin/verify-template.sh` prints `ALL OK`, both Copier
smoke tests pass every check, and one conventional commit lands on `main`.

All paths are repo-relative. New-file bodies and insert snippets are given verbatim — write
them as-is. This prompt is self-contained; no external plan is required.

## Files to create (write the fenced body verbatim)

### 1. `seed/.claude/rules/PROJECT-BACKGROUND.md`
```markdown
# Project Background

> Read when you need the "why" of the project — problem framing, stakeholders, glossary.
> This file is a template. Replace each section's placeholder text with project-specific content.

## Problem Statement

(What problem does this project solve? Who experiences it? What happens if it's not solved?
Frame as a concrete user/business need, not a technical description.)

## Stakeholders

| Role | Who | Cares About |
|------|-----|-------------|
| (e.g., Project Lead) | (name or team) | (what they need from this project) |

## Glossary

| Term | Definition |
|------|-----------|
| (domain term) | (what it means in THIS project's context — not the textbook definition) |

## Prior Art & Key Decisions

(What approaches were considered and why was this one chosen?
Link to ADRs in `docs/adr/` if available. Keep to 3-5 bullet points.)

## Current Phase

(One sentence: what stage is the project in right now? What's the immediate next milestone?)
```

### 2. `seed/.claude/rules/scaling-vs-automating.md` (on-demand rule — NO `paths:` frontmatter)
```markdown
# Scaling vs. Automating

> Read when: creating new skills, deciding whether to automate a process, or evaluating
> whether a workflow step should become a hook/skill/agent.

## The distinction

Automation means a task runs without human involvement. Scaling means your capacity
increases without proportional increase in effort. These overlap but are not identical.
You can automate something that doesn't scale (an automated response that annoys people
faster). You can scale something without automating it (a well-documented process a new
team member can follow on day one).

The fix is different for each:
- **Automation problems** → deterministic tools, hooks, skills (Layer 1-2 of 60/30/10)
- **Scaling problems** → documentation, context files, stage contracts (make judgment transferable)

## The four-question diagnostic

For each step in your workflow, ask:

1. **Does this step require my specific judgment?**
   If yes → scales by documentation (make judgment criteria explicit), not automation.

2. **Would this step produce the same output regardless of who does it?**
   If yes → automate or delegate with minimal documentation.

3. **Does the quality of this step affect everything downstream?**
   If yes → this is a leverage point. Invest in quality, not speed.

4. **Am I the bottleneck on this step?**
   If yes → document well enough to delegate, or restructure the workflow.

**Rule of thumb**: If #1 and #3 are "yes," this is scaling work — document it,
don't automate it. If #2 is "yes" and #4 is "yes," this is automation work —
make it a skill or hook.

## Anti-pattern: premature skill creation

Before creating a new skill, run the diagnostic above. Common mistakes:
- Automating a task you don't yet understand well enough (Paul Graham: "do things that
  don't scale" until you understand the work deeply)
- Creating a skill for a one-off task (a skill's value comes from reuse frequency)
- Automating the judgment part instead of the throughput part

## Source

JVC `constraints/07-scaling-vs-automating.md` (Brooks's *Mythical Man-Month*, Toyota
Production System, Paul Graham's "Do Things That Don't Scale").
```

### 3. `seed/.claude/rules/naming-conventions.md` (on-demand rule — NO `paths:` frontmatter)
```markdown
# Naming Conventions

> Read when: creating files or directories, authoring CONTEXT.md files, or reviewing
> project structure.

## Load-bearing names

Naming conventions are load-bearing documentation (JVC Constraint 08). A folder called
`01_research` tells you two things: this is the first stage, and it contains research.
A folder called `stuff` tells you nothing. Consistent, descriptive naming reduces the
need for external documentation because the structure self-documents.

## Patterns

| Pattern | When to use | Example |
|---------|-------------|---------|
| Numbered prefix (`01_`, `02_`) | Encode execution order in sequential workflows | `01_research/`, `02_analysis/` |
| Underscore prefix (`_config`) | Mark support files (not workflow stages) | `_prompts/`, `_reference/` |
| Date prefix (`YYYY-MM-DD`) | Chronological files (logs, plans, handoffs) | `2026-05-27-gap-closure.md` |
| Status suffix (`_draft`, `_final`) | Track lifecycle state | `proposal_draft.md` |
| Kebab-case | Multi-word file and directory names | `scaling-vs-automating.md` |

## Anti-patterns

- Generic names: `stuff/`, `misc/`, `temp/`, `new_file.md`, `test.py`
- Acronyms without context: `pba/` (what does PBA stand for?)
- Mixed conventions in the same directory level
- CamelCase for non-code files (use kebab-case for markdown, configs, docs)

## Source

JVC `constraints/08-handoff-readiness.md` (naming as self-documenting structure).
```

## Edits to apply (insert the snippet at the named anchor)

### 4. `seed/_research/rules/research-consistency.md` — append after §4 ("Explicit uncertainty over silent assumptions")
```markdown

## 5. Scaffold routing for research directories

After bootstrapping a research project, run `/scaffold-context` on high-traffic
research directories (`results/`, `scripts/`, `submission_docs/`) to create
per-directory CONTEXT.md routing files. These directories ship without routing —
each project's content is different enough that pre-built CONTEXT.md files would
be too generic to meet the 25-line minimum in `context-md-anatomy.md`.
```

### 5. `seed/.claude/rules/spec-conventions.md` — insert after "Acceptance Criteria Rules", before "## Spec Lifecycle"
```markdown

## The Stranger Test

Before finalizing any spec or task description, apply this gate: could a stranger
(or a fresh Claude Code session with zero context) start working on this without
asking follow-up questions? If not, the spec is incomplete. Check:

- Can you describe the expected output in one sentence?
- Are acceptance criteria verifiable by reading the output alone?
- Would removing any section cause ambiguity about what "done" means?

Source: JVC Constraint 02 ("If you cannot describe your expected output in one
sentence, the model cannot hit it") and Foundation Course 1.3 (the stranger test).
```

### 6. `seed/.claude/rules/session-guardrails.md` — append after §5 ("Skill Placement")
```markdown

## 6. Context Freshness

At session end, check these files for staleness before committing:
- `CLAUDE.md` — does the reference table match the actual rules that exist?
- Active `CONTEXT.md` files — do they reflect current directory contents?
- `known-issues.md` — any new gotchas discovered this session?
- Relevant rule files — if a convention changed, update the rule, not just the code.

Anti-pattern: "I'll update the docs later" — you won't. Update in the same session.
```

### 7. `seed/.claude/rules/context-md-anatomy.md` — insert before the final "## Source"
```markdown

## Routing tables vs. reference tables

Task routing tables (`Task | Go to | Read | Skills`) are an L1 pattern.
They belong in CONTEXT.md files, not in the root CLAUDE.md.

CLAUDE.md uses a *reference* routing table (`File | Read when`) that points
to on-demand docs. This is navigation (L0), not task routing (L1).

If you find yourself adding task-specific routing to CLAUDE.md, move it to the
relevant subdirectory's CONTEXT.md instead.
```

### 8. `seed/.claude/rules/layer-triage.md` — insert before the final "## Source"
```markdown

## Self-audit

Periodically audit your project's `.claude/` setup against the 60/30/10 framework.
Run this diagnostic:

1. **Inventory**: List every rule, skill, agent, and hook in `.claude/`.
2. **Classify**: For each, assign to deterministic (60%), rule-based (30%),
   or probabilistic (10%) based on what the asset actually does.
3. **Flag**: Identify items where an LLM is used but a deterministic tool could
   do the job (the "LLM where a regex would do" anti-pattern above).
4. **Report**: Show the current ratio and specific recommendations.

If the probabilistic portion exceeds ~15%, look for items to move to Layer 1 or 2.

Source: JVC Vault Course 4.2 ("The Build — VigilOre"), Exercise 2 — "Find the AI that shouldn't be AI."
```

### 9. `seed/.claude/skills/scaffold-context/SKILL.md` — two edits
- In "## Process", insert a new step between step 3 ("Classify the dominant tasks") and
  step 4 ("Identify which skills…"), then renumber subsequent steps (old 4→5 … old 9→10):
  > 4. Ask the user: "What does successful work in this area look like? (One verifiable sentence.)"
  >    Include their answer as a `Done looks like:` line at the end of "The Process" section in
  >    the generated CONTEXT.md.
- In the "## Done looks like" section, add this criterion between "Every Skill row has a
  non-trivial When trigger." and "The user has acknowledged the draft.":
  > - "The Process" section ends with a `Done looks like:` line from the user.

### 10. `seed/CLAUDE.md.jinja` — insert after the `layer-triage.md` row, before the `validation-loop.md` row
```
| `scaling-vs-automating.md` | Creating new skills or deciding whether to automate a process |
| `naming-conventions.md`    | Creating files/directories or authoring CONTEXT.md |
```

### 11. root `CLAUDE.md` — under "Reference Docs … Operational:", add
```
- `.claude/rules/scaling-vs-automating.md` — when creating new skills or deciding whether to automate
- `.claude/rules/naming-conventions.md` — when creating files/directories or authoring CONTEXT.md
```

## Constraints
- Apply each edit to ONLY the file named, at the position named. Do not generalize an insert
  to sibling rule files, and do not edit sections not referenced here.
- `scaling-vs-automating.md` and `naming-conventions.md` are on-demand rules — NO `paths:`
  frontmatter; the first line is the `#` heading.
- Keep `seed/CLAUDE.md.jinja` ≤ 65 lines / ~800 tokens. Keep root `CLAUDE.md` under 200 lines.
- Commit directly to `main`; no branches.

## Must NOT include
- Any new rule file beyond the three created above.
- Recreating `seed/_research/rules/research-memory.md` (it already exists), or adding
  CONTEXT.md files to research directories (the overlay script cannot deploy them).
- A new `context-update-discipline.md`, `five-part-prompt-framework.md`, or `system-audit`
  skill — these were deliberately folded into existing files above.
- "While-we're-here" cleanups of any file not named above.

## Done + verification
1. `bin/verify-template.sh` → expect `ALL OK`.
2. Copier smoke test (default flavor):
   ```bash
   TMP=$(mktemp -d)
   uvx copier copy --trust --defaults --vcs-ref HEAD --data "project_name=gap-test" . "$TMP/default"
   test -f "$TMP/default/.claude/rules/PROJECT-BACKGROUND.md" && echo PASS
   test -f "$TMP/default/.claude/rules/scaling-vs-automating.md" && echo PASS
   test -f "$TMP/default/.claude/rules/naming-conventions.md" && echo PASS
   grep -q "Stranger Test" "$TMP/default/.claude/rules/spec-conventions.md" && echo PASS
   grep -q "Context Freshness" "$TMP/default/.claude/rules/session-guardrails.md" && echo PASS
   grep -q "Routing tables vs" "$TMP/default/.claude/rules/context-md-anatomy.md" && echo PASS
   grep -q "Self-audit" "$TMP/default/.claude/rules/layer-triage.md" && echo PASS
   grep -q "scaling-vs-automating" "$TMP/default/CLAUDE.md" && echo PASS
   rm -rf "$TMP"
   ```
   Expect 8 PASS lines.
3. Copier smoke test (research flavor):
   ```bash
   TMP=$(mktemp -d)
   uvx copier copy --trust --defaults --vcs-ref HEAD --data "project_name=gap-research" --data "is_research=true" . "$TMP/research"
   test -f "$TMP/research/.claude/rules/research-memory.md" && echo PASS
   grep -q "scaffold-context" "$TMP/research/.claude/rules/research-consistency.md" && echo PASS
   rm -rf "$TMP"
   ```
   Expect 2 PASS lines.
4. Run the Pipeline Gate in order: `/session-critique` → `/validate` → `/commit`, with commit message:
   ```
   feat: codify remaining JVC constraint learnings into Loam rules

   - Create PROJECT-BACKGROUND.md template (fixes CLAUDE.md.jinja:44 stub)
   - Create scaling-vs-automating.md from JVC Constraint 07
   - Create naming-conventions.md from JVC Constraint 08
   - Add Stranger Test to spec-conventions.md (JVC Constraint 02)
   - Add Context Freshness §6 to session-guardrails.md (JVC Constraint 04)
   - Add routing table clarification to context-md-anatomy.md
   - Add self-audit section to layer-triage.md (JVC Vault 4.2)
   - Enhance scaffold-context with "Done looks like" generation
   - Add scaffold-context guidance to research-consistency.md
   - Update CLAUDE.md.jinja and root CLAUDE.md reference tables
   ```

Direct technical prose. No emoji.
