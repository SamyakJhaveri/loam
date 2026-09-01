---
name: hypothesis-tree
description: >
  Structured hypothesis tree manager for multi-step investigations. Use when a
  "why does X fail" question branches into sub-hypotheses, when an investigation
  spans several sessions and the reasoning must survive between them, or when
  falsifiable claims need tracking with linked evidence and dates. Maintains one
  markdown file with add, update, review, and prune subcommands, each gated on
  verifying that the cited evidence file actually exists and actually says what
  the claim says. NOT for a single-session bug hunt, a question answerable by
  one command, or as a general note-taking file.
argument-hint: "add \"H: <statement>\" | update <ID> --evidence-for|--evidence-against \"<desc>\" --file <path> | review | prune"
---

# hypothesis-tree

Builds, updates, and reviews a persistent hypothesis tree for an investigation.
The tree lives in a single markdown file at `docs/hypothesis_tree.md` (or the project's equivalent docs location).
Each hypothesis carries falsifiable criteria, linked evidence, and a next experiment.

**Trigger:** `/hypothesis-tree <subcommand>`.

## Iron law

```
NO HYPOTHESIS WITHOUT FALSIFIABLE CRITERIA AND A NEXT EXPERIMENT
```

## Arguments

`$ARGUMENTS` is a subcommand plus parameters:

- `add "H: <statement>"` - add a new hypothesis node.
- `update <ID> --evidence-for|--evidence-against "<description>" --file <path>` - attach evidence to an existing node.
- `update <ID> --confidence <level>` - change confidence, permitted only alongside evidence.
- `review` - display every hypothesis with staleness indicators.
- `prune` - propose archiving hypotheses with no evidence updates in 14 or more days.

## Anti-rationalization table

| Excuse | Reality |
|--------|---------|
| "I'll add the evidence later" | Evidence without a timestamp rots. Link it now or lose the thread. |
| "The evidence is obvious" | Obvious to you today, opaque to a reviewer in six months. Cite the file. |
| "This hypothesis is too simple to formalize" | Simple claims are exactly the ones that break a conclusion, because nobody checked them. State the criterion. |
| "I just need a placeholder" | Placeholders become permanent. State the falsifiable criterion or do not add the node. |
| "The confidence feels higher now" | Confidence follows evidence, not intuition. No new evidence, no confidence change. |

## Red flags - stop and restart

- Adding a hypothesis with no falsifiable criterion.
- Linking evidence to a file path that does not exist on disk.
- Claiming evidence supports a hypothesis without having read that file's contents.
- Updating a confidence level without new evidence.
- Any hypothesis that cannot be tested against data you already have, or by a concrete next experiment you can name.

If any red flag triggers: STOP. Re-read the hypothesis and rewrite it with falsifiable criteria before doing anything else.

## Tree node schema

Every hypothesis in the tree file follows this structure:

```markdown
### H<N>: <Statement>

- **Status:** ACTIVE | SUPPORTED | REFUTED | ARCHIVED
- **Confidence:** HIGH | MEDIUM | LOW
- **Falsifiable criterion:** <What specific observation would disprove this?>
- **Evidence FOR:**
  - [<description>](<relative path to file>) - <date added>
- **Evidence AGAINST:**
  - [<description>](<relative path to file>) - <date added>
- **Next experiment:** <Concrete action that would strengthen or weaken this hypothesis>
- **Last updated:** <YYYY-MM-DD>
```

## Workflow

### Phase 1: Parse the subcommand

Read the subcommand from `$ARGUMENTS` and route: `add` to Phase 2a, `update` to Phase 2b, `review` to Phase 2c, `prune` to Phase 2d.
With no argument, or `help`, display the usage summary and stop.

### Phase 2a: Add a hypothesis

1. Parse the hypothesis statement from the arguments.
2. **Verification gate:** confirm the statement carries both a falsifiable criterion (what would disprove it) and a next experiment (what concrete action tests it). If either is missing, prompt the user. Do not add the node without them.
3. Read the tree file, creating it if it does not exist.
4. Assign the next sequential ID (H1, H2, H3, ...).
5. Write the node using the schema above.
6. Set Status to ACTIVE and Confidence to LOW. New hypotheses always start at LOW.
7. Set Last updated to today's date.

**Verification gate:** read the file back and confirm the node was written correctly.

### Phase 2b: Update a hypothesis

1. Parse the hypothesis ID and the evidence from the arguments.
2. Read the tree file and confirm the ID exists.
3. If `--file <path>` was given:
   - **Verification gate:** confirm the file exists on disk.
   - **Verification gate:** read the file and confirm it actually contains something supporting the stated claim.
   - If the file does not exist, or does not support the claim, STOP and report it to the user. Do not write the entry.
4. Append the evidence entry with today's date.
5. If `--confidence <level>` was given, update it, but only when the new evidence justifies the change.
6. Update Last updated to today's date.
7. If the evidence now clearly supports or refutes the hypothesis, suggest a Status change to the user.

**Verification gate:** read the updated node back and confirm the evidence was appended correctly.

### Phase 2c: Review all hypotheses

1. Read the tree file.
2. For each hypothesis compute: days since last update, a staleness indicator (FRESH under 7 days, AGING 7 to 14 days, STALE over 14 days), and the evidence balance as a count of FOR versus AGAINST.
3. Display the summary table:

```
=== HYPOTHESIS TREE REVIEW ===
ID    Status     Confidence  Evidence (F/A)  Staleness   Statement
H1    ACTIVE     HIGH        4/1             FRESH       <truncated statement>
H2    ACTIVE     LOW         1/0             STALE       <truncated statement>
H3    REFUTED    -           2/3             FRESH       <truncated statement>
```

4. Flag every ACTIVE hypothesis that is STALE. Those need attention.
5. Flag every hypothesis with zero evidence entries. Those need data or should be pruned.

**Verification gate:** cross-check that every file path referenced by an evidence entry still exists on disk, and report the broken links.

### Phase 2d: Prune stale hypotheses

1. Read the tree file.
2. Identify hypotheses that are either ACTIVE with no evidence update in 14 or more days, or have zero evidence entries and were created 7 or more days ago.
3. Display the archival candidates. Never auto-archive.
4. **Wait for user confirmation** before changing any Status to ARCHIVED.
5. For confirmed archives, move the node into an `## Archived` section at the bottom of the file. Nothing is deleted.

**Verification gate:** read the file back and confirm the archived hypotheses moved correctly.

### Phase 3: Report

After any subcommand, display:

- What changed: added, updated, or archived.
- Current tree statistics: total hypotheses, and counts of active, supported, refuted, and archived.
- Any recommended next actions: stale hypotheses, broken evidence links, nodes with no evidence.
