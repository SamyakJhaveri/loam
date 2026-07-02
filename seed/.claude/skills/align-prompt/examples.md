# align-prompt — Worked Examples

Three before/after pairs covering the common rewrite shapes. SKILL.md references this file for few-shot anchoring on every invocation.

## Example 1 — Planning prompt, target 4.8

### Before (user's draft)

```text
help me figure out how to add a CHANGELOG generator to this template. i want it to read git commits and group them by type or something. should run on release.
```

### After (rewrite, target=4.8 → planning shape)

```text
You are a release-engineering contributor to the Loam Copier template (this repo).

Goal: design a CHANGELOG generator that groups commits by Conventional Commit type
and runs on `bin/release.sh`. Done = a written plan file at `docs/plans/<date>-changelog-generator.md`
that another session can execute without rediscovery.

## Constraints
- Must integrate with the existing `bin/release.sh` flow (do not replace it).
- Must work with the existing commit history (Conventional Commits are used but not strictly enforced).
- Output format: a new file `CHANGELOG.md` at repo root, updated in place per release.

## Must NOT include
- A rewrite of `bin/release.sh` beyond a single hook-point call.
- A new dependency on a third-party CHANGELOG library (prefer git + awk/python stdlib).
- Backfilling history older than the most recent tag.

Consider at least two alternative groupings (by type vs by scope vs by author) and
weigh trade-offs before committing to one. Decompose the design into: commit parser,
grouping logic, formatter, integration point.
```

## Example 2 — Execution prompt, target 4.6

### Before (user's draft)

```text
the lint hook is failing for kebab-case skill names with numbers in them like skill-4-2. fix the hook so it allows numbers in skill names.
```

### After (rewrite, target=4.6 → execution shape, no thinking cues, explicit anti-generalization scope, tone-anchor added)

```text
Fix `bin/lint-skill-descriptions.sh` so that skill names with digits (e.g., `skill-4-2`)
pass the kebab-case check. Done = the lint suite reports 0 errors against a test fixture
with a digit-bearing skill name.

## Constraints
- Modify ONLY the regex that validates `name:` in skill frontmatter. Do not generalize the fix to other validators in the file (description-length check, YAML safety check, etc.).
- Do not touch any helper function not directly invoked by the `name:` validator.
- Preserve the existing exit-code behaviour (0 on success, 1 on any failure).

Apply the regex fix, then run `bin/lint-skill-descriptions.sh all` and
confirm zero errors. Direct technical prose in the response — no emoji, no validation-forward phrasing.
```

## Example 3 — Mixed / ambiguous prompt, target 4.8

### Before (user's draft)

```text
i want to understand if there's a way to make the workflow rules less repetitive across the rules files. seems like the 60/30/10 framework comes up in multiple places. think about it and tell me what to do.
```

### After (rewrite, target=4.8 → planning shape, role omitted because task is meta)

```text
Goal: identify duplication of the 60/30/10 framework across `seed/.claude/rules/*.md`
and recommend a consolidation strategy. Done = a written analysis document at
`docs/plans/<date>-60-30-10-consolidation.md` that lists every file containing the
framework (with line ranges), names the duplicated phrasings, and proposes ONE
canonical home for the framework with one-line cross-references from the other files.

## Constraints
- Must preserve every concrete rule currently in any rule file (no deletion of guidance).
- Must keep CLAUDE.md under 200 lines (per `docs/MEMORY.md` cap).
- Must not break any path-scoped loading that depends on a rule file's current contents.

## Must NOT include
- Edits to the actual rule files (this is analysis + plan, not implementation).
- A rewrite of `layer-triage.md` beyond identifying it as the canonical home (or not).
- Proposals to remove the framework — it is load-bearing.

Weigh at least two consolidation approaches (single canonical home with cross-refs
vs distributed with a shared excerpt at the top of each file) and recommend one with
its trade-offs explicit.
```

## Notes on the moves applied

| Example | Move 1 | Move 2 (role) | Move 3 (Must-NOTs + anti-generalization) | Move 4 (Done) | Move 5 (thinking) | Move 6 (compress + tone-anchor) |
|---------|--------|---------------|-------------------------------------------|---------------|-------------------|----------------------------------|
| 1       | ✓      | ✓ (eng role)  | ✓ Must-NOTs (4.8 planning)               | ✓             | ✓ (4.8)           | ✓ (no tone-anchor; 4.8 default direct) |
| 2       | ✓      | ✗ (mechanical)| ✗ Must-NOTs, ✓ anti-generalization (4.6) | ✓             | ✗ (4.6 lacks adaptive thinking) | ✓ + tone-anchor (4.6 baseline warmer) |
| 3       | ✓      | ✗ (meta task) | ✓ Must-NOTs (4.8 planning)               | ✓             | ✓ (4.8)           | ✓ (no tone-anchor; 4.8 default direct) |
