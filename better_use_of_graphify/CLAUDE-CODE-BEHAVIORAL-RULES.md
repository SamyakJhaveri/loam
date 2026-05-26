# Claude Code Behavioral Rules for Research Projects

> **File location:** `.claude/rules/research-consistency.md`
> **Trigger:** Always loaded (no file-path condition). This is a global rule.
> **Purpose:** Encode behavioral patterns that prevent the specific consistency
> failures observed in the ParBench project. These rules change how Claude Code
> approaches tasks, not just what it knows.

---

## Rule 1: Never Cite Numbers From Memory or Graph Traversal

**The failure this prevents:** Claude Code navigating a knowledge graph or recalling
a number from earlier in the conversation, then writing it into a paper section
without verification. This produced incorrect statistics in ParBench paper drafts.

**The rule:**

When asked to write a paper section, create a table, or reference a specific
statistic:

1. DO NOT use any number from memory, from a previous message, or from a
   knowledge graph node.
2. DO check `claims.jsonl` for an existing claim entry with `status: "current"`.
3. If a matching claim exists, verify its `pipeline_version` matches the current
   pipeline fingerprint before using the value.
4. If NO matching claim exists, compute the value from raw data by running the
   appropriate analysis script. Then create a new `claims.jsonl` entry.
5. If you cannot compute the value (missing script, missing data), tell the user:
   "I need to compute this value but [specific blocker]. Can you run [specific
   script] or point me to the right data?"

**Never say:** "Based on the results, the pass rate is approximately 34%."
**Always say:** "Let me check claims.jsonl for this statistic" or "Let me compute
this from the raw result files."

---

## Rule 2: Read the Research Changelog Before Paper Tasks

**The failure this prevents:** Claude Code writing paper text that describes an
obsolete version of the framework (e.g., describing string-based verification
after it was replaced with numerical verification).

**The rule:**

Before performing ANY of these tasks:
- Writing or editing a paper section
- Creating or updating a figure or table
- Interpreting results
- Answering questions about what the results show
- Drafting responses to reviewer comments

FIRST read `CHANGELOG.research.md` (the entire file, not just the first entry).
The most recent entry describes the current state. If any entry says prior results
are invalid, treat them as invalid regardless of what the file system shows.

After reading, explicitly state to the user:
"Current pipeline version is {version} from {date}. The most recent change was:
{one-sentence summary}."

This confirmation prevents silent use of stale context.

---

## Rule 3: Distinguish Engineering Context From Research Context

**The failure this prevents:** Claude Code using knowledge of how the pipeline
*works* (engineering context) when it should be using knowledge of what the
pipeline *found* (research context). These are different questions requiring
different sources.

**The rule:**

| Task type | Correct source | Wrong source |
|---|---|---|
| "How does the verifier work?" | Engineering graph, code files | Results, claims.jsonl |
| "What was the pass rate for Qwen?" | claims.jsonl, raw results | Engineering graph, code files |
| "Why did we use numerical comparison?" | CHANGELOG.research.md | Knowledge graph (may have stale edges) |
| "What's the pipeline architecture?" | Engineering graph, CLAUDE.md | Meeting notes, presentations |
| "What did the reviewers say?" | The specific reviewer comment file | Knowledge graph, inferred context |

When you catch yourself about to answer a research question using engineering
context (or vice versa), stop and redirect to the correct source.

---

## Rule 4: Treat the Knowledge Graph as Structural, Not Authoritative

**The failure this prevents:** Claude Code treating Graphify graph edges —
especially INFERRED edges (23% of the ParBench graph) — as ground truth for
paper claims.

**The rule:**

The Graphify knowledge graph answers: "What connects X to Y in the code structure?"
It does NOT answer:
- "Is X correct?"
- "Is X still the current approach?"
- "What value does X produce?"
- "When was X last updated?"

Specifically:
- NEVER use a graph node's description as a source for paper text
- NEVER assume a graph edge represents the current state (it may reflect code
  from weeks ago)
- NEVER navigate the graph to find statistics (use claims.jsonl)
- ALWAYS treat INFERRED edges (confidence < 1.0) as hypotheses, not facts
- The graph is useful for: understanding module dependencies, finding related
  code, navigating unfamiliar parts of the codebase

---

## Rule 5: Pipeline Version Awareness

**The failure this prevents:** Analysis or paper writing that unknowingly mixes
results from different pipeline versions (e.g., some results from the
string-comparison era, some from numerical-comparison era).

**The rule:**

Before ANY task involving result files:

1. Check the current pipeline fingerprint:
   ```bash
   python3 -c "from harness.pipeline_version import compute_pipeline_fingerprint; print(compute_pipeline_fingerprint('.'))"
   ```

2. If loading result files, check their `pipeline_version` field. If ANY result
   has a version that doesn't match the current fingerprint, STOP and alert:
   "Found results from pipeline version {old} but current version is {current}.
   These results may be stale. Run `python3 scripts/audit_result_versions.py`
   for details."

3. Never silently filter out stale results. The user must make the decision
   about whether to re-run experiments or archive old results.

---

## Rule 6: Meeting Notes and Planning Docs Are Not Authoritative

**The failure this prevents:** Claude Code incorporating content from meeting notes,
TODO lists, or planning documents into paper text or code decisions. These are
ephemeral artifacts that reflect a point-in-time discussion, not the current state.

**The rule:**

Files in these directories are INFORMATIONAL ONLY:
- `meeting_notes/`
- `presentations/`
- `planning/`
- Any file named `TODO.md`, `HANDOFF.md`, `TASKS.md`, or similar

NEVER:
- Quote or paraphrase meeting notes in paper text
- Use a design decision from meeting notes without verifying it against the
  actual code
- Assume a TODO item represents the current state of the project
- Reference meeting note content when answering questions about how the system works

ALWAYS:
- Verify against source code if a meeting note describes a design decision
- Check CHANGELOG.research.md if a meeting note describes a methodology change
- Ask the user if you're unsure whether a meeting note reflects current thinking

---

## Rule 7: Explicit Uncertainty Over Silent Assumptions

**The failure this prevents:** Claude Code filling gaps in its knowledge with
plausible-sounding but incorrect assumptions, producing paper text that reads
confidently but is factually wrong.

**The rule:**

When you encounter a gap — a statistic you can't verify, a design decision you
can't trace, a result file you can't find — say so explicitly:

**Acceptable:**
- "I can't find a claims.jsonl entry for this statistic. Let me compute it
  from raw data, or would you like to point me to the right source?"
- "The CHANGELOG.research.md doesn't mention when this metric was added. Can
  you confirm when the failure taxonomy was introduced?"
- "I found result files from two different pipeline versions. I'm not sure which
  set to use for this analysis."

**Unacceptable:**
- Silently assuming a round number ("approximately 35%") when the exact value
  should be computed
- Writing "the verifier compares numerical outputs" without checking whether
  that's still true
- Using a graph edge description as paper text without verifying the underlying code

The cost of asking is a few seconds of the user's time. The cost of guessing
wrong is hours of paper rework.

---

## Rule 8: Claim-First Paper Writing

**The failure this prevents:** Writing paper prose first and then trying to find
supporting evidence, which biases toward confirmation and makes it easy to cite
numbers that don't exist in the raw data.

**The rule:**

When writing a results section or creating a table/figure:

1. **First:** Identify what claims the section needs to make.
2. **Second:** Check claims.jsonl for each needed claim.
3. **Third:** For missing claims, compute the values from raw data.
4. **Fourth:** Add claims.jsonl entries for all new values.
5. **Fifth:** Write the prose, referencing specific claim IDs.

In the LaTeX source, annotate every statistical claim:
```latex
% claim:C001 — verified 2026-05-21 against pipeline v3 (a3f8b2c1e9d4)
Qwen achieves an overall pass rate of 34.2\% on CUDA-to-OpenMP translation.
```

This creates an auditable chain from paper text to raw data.

---

## Rule 9: Graph Rebuild Discipline

**The failure this prevents:** An outdated knowledge graph providing stale
structural information that misleads code navigation and architecture descriptions.

**The rule:**

The engineering Graphify graph (`graphify-out-engineering/`) should be rebuilt
ONLY when:
- A new module or pipeline stage is added
- A module is significantly restructured (split, merged, renamed)
- Major dependencies change

The engineering graph should NOT be rebuilt for:
- Bug fixes within existing modules
- Parameter changes
- Verification logic changes (these are tracked by CHANGELOG.research.md)
- New result files or spec files

If you need to answer a structural question and the graph might be stale, verify
by reading the actual source code. The graph is a navigation aid, not a source
of truth.

---

## Rule 10: Result Immutability Is Non-Negotiable

**The failure this prevents:** Modification of result files, which destroys the
reproducibility guarantee and breaks the pipeline version audit trail.

**The rule:**

Files in `results/` are NEVER modified after creation. No exceptions.

- If a result is wrong: produce a new result file (re-run the experiment).
- If results need to be superseded: archive the old results directory, then
  produce new results under the current pipeline version.
- If a single field needs correction: this indicates a pipeline bug. Fix the
  pipeline, bump the pipeline version, re-run.

This rule is enforced by a pre-tool-use hook in `.claude/settings.json` that
blocks Edit and Write operations targeting `results/`. Do not circumvent this hook.

---

## Rule Summary (Quick Reference)

| # | Rule | One-liner |
|---|------|-----------|
| 1 | No numbers from memory | Compute from raw data or read from claims.jsonl |
| 2 | Read changelog first | CHANGELOG.research.md before any paper task |
| 3 | Separate engineering from research | Different questions need different sources |
| 4 | Graph is structural, not authoritative | Never use graph for paper claims |
| 5 | Check pipeline versions | Verify results match current pipeline fingerprint |
| 6 | Meeting notes aren't ground truth | Verify against code and changelog |
| 7 | Explicit uncertainty | Say "I don't know" rather than guess |
| 8 | Claim-first writing | Compute claims before writing prose |
| 9 | Rebuild graph sparingly | Only on major structural changes |
| 10 | Results are immutable | Never modify result files |
