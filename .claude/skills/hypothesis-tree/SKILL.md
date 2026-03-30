# Hypothesis Tree Manager

Use when building, updating, or reviewing the persistent hypothesis tree for the SC26
paper. Maintains a structured markdown file at `docs/hypothesis_tree.md` where each
hypothesis has falsifiable criteria, linked evidence, and a next experiment.

**Trigger:** When user types `/hypothesis-tree` with a subcommand.

## Iron Law

```
NO HYPOTHESIS WITHOUT FALSIFIABLE CRITERIA AND A NEXT EXPERIMENT
```

## Arguments

- `$ARGUMENTS` — subcommand and parameters:
  - `add "H: <statement>"` — add a new hypothesis node
  - `update <ID> --evidence-for|--evidence-against "<description>" --file <path>` — attach evidence
  - `review` — display all hypotheses with staleness indicators
  - `prune` — archive hypotheses with no evidence updates in 14+ days

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll add evidence later" | Evidence without a timestamp rots; link it now or lose the thread |
| "The evidence is obvious" | Obvious to you today, opaque to a reviewer in 6 months — cite the file |
| "This hypothesis is too simple to formalize" | Simple claims break papers; the backprop tier inversion was "obvious" until it wasn't |
| "I just need a placeholder" | Placeholders become permanent — state the falsifiable criterion or don't add it |

## Red Flags — STOP and Restart

- Adding a hypothesis with no falsifiable criterion
- Linking evidence to a file path that does not exist on disk
- Claiming evidence supports a hypothesis without reading the actual file contents
- Updating confidence level without new evidence (confidence follows evidence, not intuition)
- Any hypothesis that cannot be tested with data already in `results/` or a concrete next experiment

If any red flag triggers: STOP. Re-read the hypothesis. Rewrite it with falsifiable criteria
before proceeding.

## Tree Node Schema

Each hypothesis in `docs/hypothesis_tree.md` follows this structure:

```markdown
### H<N>: <Statement>

- **Status:** ACTIVE | SUPPORTED | REFUTED | ARCHIVED
- **Confidence:** HIGH | MEDIUM | LOW
- **Falsifiable criterion:** <What specific observation would disprove this?>
- **Evidence FOR:**
  - [<description>](<relative path to file>) — <date added>
- **Evidence AGAINST:**
  - [<description>](<relative path to file>) — <date added>
- **Next experiment:** <Concrete action that would strengthen or weaken this hypothesis>
- **Last updated:** <YYYY-MM-DD>
```

## Project Context

- **Result directories:** `results/evaluation/{model}/` contains per-kernel JSON files
- **Models:** claude-sonnet, gemini-2.5-flash-lite, groq-llama-3.3-70b, together-qwen-3.5
- **Augmentation results:** `results/augmentation/` contains level-variant test data
- **Analysis outputs:** `analysis/data/` and `analysis/reports/`
- **Key known anomaly:** backprop tier inversion — Gemini (weakest overall) passes where
  Groq (stronger overall) fails. See `.claude/rules/known-issues.md` for details.
- **Spec counts:** 60 Rodinia (54 PASS, 6 KNOWN_FAIL), 4 XSBench (4 PASS)

## Workflow

### Phase 1: Parse Subcommand

Extract the subcommand from `$ARGUMENTS`:
- `add` — go to Phase 2a
- `update` — go to Phase 2b
- `review` — go to Phase 2c
- `prune` — go to Phase 2d
- No argument or `help` — display usage summary

### Phase 2a: Add Hypothesis

1. Parse the hypothesis statement from arguments
2. **Verification gate:** Confirm the statement includes:
   - A falsifiable criterion (what would disprove it?)
   - A next experiment (what concrete action tests it?)
   - If either is missing, prompt the user — do NOT add without them
3. Read `docs/hypothesis_tree.md` (create if it doesn't exist)
4. Assign the next sequential ID (H1, H2, H3...)
5. Write the new node using the Tree Node Schema above
6. Set Status=ACTIVE, Confidence=LOW (new hypotheses start at LOW)
7. Set Last updated to today's date

**Verification gate:** Read back the file and confirm the node was written correctly.

### Phase 2b: Update Hypothesis

1. Parse the hypothesis ID and evidence from arguments
2. Read `docs/hypothesis_tree.md` — confirm the ID exists
3. If `--file <path>` is provided:
   - **Verification gate:** Check the file exists on disk (`ls` or `Glob`)
   - **Verification gate:** Read the file and confirm it contains data supporting the claim
   - If the file doesn't exist or doesn't support the claim: STOP and report to user
4. Append the evidence entry with today's date
5. If `--confidence <level>` is provided, update confidence (only with evidence justification)
6. Update "Last updated" to today's date
7. If evidence now clearly supports or refutes the hypothesis, suggest changing Status

**Verification gate:** Read back the updated node and confirm evidence was appended correctly.

### Phase 2c: Review All Hypotheses

1. Read `docs/hypothesis_tree.md`
2. For each hypothesis, compute:
   - Days since last update
   - Staleness indicator: FRESH (<7 days), AGING (7-14 days), STALE (>14 days)
   - Evidence balance: count of FOR vs AGAINST entries
3. Display summary table:

```
=== HYPOTHESIS TREE REVIEW ===
ID    Status     Confidence  Evidence (F/A)  Staleness   Statement
H1    ACTIVE     HIGH        4/1             FRESH       Per-kernel difficulty is not...
H2    ACTIVE     LOW         1/0             STALE       Augmentation level affects...
H3    REFUTED    —           2/3             FRESH       Model size predicts pass rate...
```

4. Flag any ACTIVE hypothesis that is STALE — these need attention
5. Flag any hypothesis with 0 evidence entries — needs data or should be pruned

**Verification gate:** Cross-check that every file path referenced in evidence entries
still exists on disk. Report any broken links.

### Phase 2d: Prune Stale Hypotheses

1. Read `docs/hypothesis_tree.md`
2. Identify hypotheses with:
   - No evidence updates in 14+ days AND Status=ACTIVE
   - Zero evidence entries AND created 7+ days ago
3. Display candidates for archival — do NOT auto-archive
4. **Wait for user confirmation** before changing any Status to ARCHIVED
5. For confirmed archives, move to an `## Archived` section at the bottom of the file

**Verification gate:** Read back the file and confirm archived hypotheses were moved correctly.

### Phase 3: Report

After any subcommand, display:
- What was changed (added/updated/archived)
- Current tree statistics: total hypotheses, active, supported, refuted, archived
- Any recommended next actions (stale hypotheses, broken evidence links)
