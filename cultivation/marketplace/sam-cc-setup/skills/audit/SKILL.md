---
name: audit
disable-model-invocation: true
description: Checkpoint on a plan or a piece of work - blind review, each finding reproduced before any fix, an independent second design, a short evidence-tagged report, then the updated work. Manual-only; an agent told to run it reads this file by path.
argument-hint: [what to audit; default is the work just produced]
---

# Audit

Audit `$ARGUMENTS`, or the work just produced in this session.
It works on a plan, a research claim or an experiment design before anything is built, as well as on finished work.
The owner runs this because work sometimes drifts from the goal, sounds more certain than the evidence allows, or stays with the first workable approach.

Start by stating the goal in one sentence and what judges success.
Everything below is measured against that sentence.

## Size the audit to the work

Each agent costs tokens and a handoff, so match the audit to what is at stake.

- A small output (an answer, a few lines of code): no agents. Write the report below from the sources.
- A change or a document: one blind reviewer, then the report.
- A ticket set, a design, a research claim or an experiment plan: the full audit.

## Full audit

Blind means the agent gets the artifact path, the goal, the sources and the list of settled decisions.
It does not get this conversation, your reasoning or your conclusion.

1. **Second design.** A fresh agent gets the goal, the constraints and the sources, and not the work, and designs its own approach.
   This is the fresh-start lens of the surprise-me skill (`${CLAUDE_SKILL_DIR}/../surprise-me/SKILL.md`; it is manual-only, so read the file).
2. **Review.** Read-only reviewers, blind: a Fable agent, and Codex (`${CLAUDE_SKILL_DIR}/../codex-review/SKILL.md` for a diff, a read-only `codex exec` for anything else).
   Ask for gaps that would change the outcome for the judge; leave out style and anything that existed before this work.
   Each finding carries a file:line or a quote, the failure it causes, and a check that reproduces it.
   Settled decisions are not reopened.
3. **Dry run, for anything another agent will carry out** (a ticket, a plan, an experiment protocol).
   Give each one alone to a fresh Opus agent that builds nothing.
   It restates the goal, lists every question and assumption it would have to make, and says how it would know it was done.
   Each question is a gap.
4. **Verify.** One Opus agent per finding tries to reproduce it against the source and cites file:line either way.
   A finding is not dismissed with a defense that nobody located and read.
   A finding that does not reproduce goes into the report as rejected, with the attempt.
5. **Fix.** Fix reproduced findings only, each with the smallest change that removes its cause.
   Then re-run only the reviewer whose finding was fixed, once; report anything still open instead of starting another round.

What a reviewer looks for depends on the work:

- A research claim: another explanation for the same evidence; whether the cited source says what is claimed, checked by reading it; prior work that already did this.
- An experiment: whether the measurement tests the claim; the control; whether the result would have looked the same if the hypothesis were false.
- A plan, a design or a ticket: a step that rests on something nobody verified; the questions from the dry run.
- Code: run it the way a user meets it and show the output.

Reviewer conditions apply to this audit and are not carried into later work.

## Report

About 400 words; the updated work is separate.

1. **Claims.** Each main claim with its evidence (file:line, a command and its output, or a quote) and a tag: ran / read in full / inferred / from memory.
   Re-read the source for anything inferred or from memory before reporting it.
2. **Weakest point** and the cheapest check that settles it. Run the check and give the result.
3. **Failure.** Assume this failed two weeks from now. Name the most likely cause.
4. **Missing.** What the owner has not asked about, including what the request itself gets wrong.
5. **Second design against ours.** What differs, what to adopt, what it improves (quality, time, risk) and what it costs. If ours is best, say so in one line.
6. **Rejected findings**, one line each with the reason.

Write "none that matters" for an empty part.
Then give the updated work.
