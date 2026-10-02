---
name: section-from-exemplars
description: Blind-reader loop for a research paper section. Use when asked to write, rewrite, improve or tighten a section, abstract or introduction of a paper, or to bring it to the standard of published papers.
---

# Rewrite a paper section from exemplars, tested on a blind reader

Use on one section of a paper at a time: one section, one file, one commit.
The acceptance test is a **restatement**: a reader with no context reads the section once and says what it claims and on what evidence.
The section is done when the restatement is complete and correct, never when the author is satisfied.
The full loop, the reader briefs per section type and the skim-reader test are in `${CLAUDE_PLUGIN_ROOT}/docs/section-loop.md`.

## Steps

1. **Read first.** Strip comments from the section as it stands and give it to a fresh reader: the `research-paper:blind-reader` agent (brief below).
   Done when you hold the restatement, the scores, and the list of terms and numbers the reader could not trace.
   This control read is the diagnosis and the baseline.
2. **Exemplars.** Look for a move table for this section type in the project (saved by an earlier run of this step).
   If there is none, read the papers in full, one read-only agent per paper, in three rings: papers this paper cites, strong papers of the same kind outside the field, two recent accepted papers at the target venue.
   Ask each reader for verbatim quotes on how the section opens, how a number is anchored, how tables carry the argument, where caveats and limitations sit, and what to copy and avoid.
   Write the shared moves as a table with the paper and quote behind each, and save it in the project.
   Done when every paper is reported read in full with the URL fetched, or named as unreachable.
3. **Edit to the findings.** Start from the text on disk.
   Change what the reader could not restate and apply the moves.
   Keep every fact, number, citation and caveat of the previous version, and check any number you add against its source file.
   Done when each control finding is fixed or listed as the owner's decision.
4. **Gate.** Run the project's mechanical checks in one command (`paper-tool section_gate <file>`, or `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/section_gate.py <file>`): no number, citation or cross-reference lost against the base commit, no banned term, style lint, a clean build, page limit, page slack.
   Done at exit 0 with no less page slack than the base commit had.
5. **Blind read again.** A new fresh reader on the new extract; fix what it could not restate; rerun the gate; read once more.
   Done when the restatement is complete and correct and no score is below the control's.
   One reader per version is noisy: a one-point move means nothing, a change in what the reader restates does.
6. **Show the owner.** Before and after lines for each change, the page range, the restatements side by side, and every finding left for the owner.
   Commit on the owner's go.

## The reader brief

The `research-paper:blind-reader` agent carries this brief; give it the extract path, the venue and field, the macro-to-text map (`paper.macros` in `paper/tools/paper-tools.toml`) and the add-on for the section type from `${CLAUDE_PLUGIN_ROOT}/docs/section-loop.md`.
Without it, spawn a fresh agent on the strongest model, with read access to the one extract and nothing else: no project rules, no history, no other file.

> You are a program committee member for VENUE, competent in FIELD, who has never seen this paper. Read exactly one file, once: PATH. Report, with a verbatim quote and line number for every point, in one message under 3,800 characters, in this order: (1) RESTATE in at most 150 words what the text claims and on what evidence, marking every guess; (2) VERDICT, three scores out of 10: could you explain this to a colleague, SECOND SCORE, how engaging is it against a specification manual; (3) every term, mechanism or number you could not follow, with the line where you needed it and the line that explains it or "never"; (4) the hardest sentences with a one-line rewrite that keeps every fact; (5) contradictions between two sentences, numbers that do not add up, order that fights the reader. Be harsh and specific. Do not suggest adding material you cannot know is true. End with Risks: what you could not judge from one file.

SECOND SCORE by section type: method, "could you re-implement it from this text"; results, "could you state which number supports each claim"; discussion, "could you state what each limitation leaves unmeasured and what would fix it"; abstract or introduction, "could you list the contributions and the evidence for each".

Re-read every quoted line before acting on it: a term the reader calls undefined may be defined in a section it did not see, and a reported mismatch between two numbers is worth checking against the data.

## Limits that shape the work

- A read-only agent's report reaches you cut at about 4,000 characters, and at 16,000 for all reports arriving together. Ask paper readers for two parts of under 3,300 characters each, and collect part 2 by message from three or four agents per turn.
- When the paper is at its page limit, every added sentence is paid for in the same file; check the slack after each edit.
- Open owner decisions stay as they are in the text and go to the owner as decisions with a recommendation.
