---
name: audit
disable-model-invocation: true
description: Checkpoint on a plan or a piece of work - blind review, each finding reproduced before any fix, an independent second design, a short evidence-tagged report, then the updated work. Manual-only; an agent told to run it reads this file by path.
argument-hint: [what to audit; default is the work just produced]
---

# Audit

`${CLAUDE_SKILL_DIR}` is this file's folder; give a subagent the resolved path.

Audit `$ARGUMENTS`, or the work just produced in this session.
It works on a plan, a research claim or an experiment design before anything is built, as well as on finished work.
The owner runs this because work sometimes drifts from the goal, sounds more certain than the evidence allows, or stays with the first workable approach.

First settle what is being audited: one current artifact (a file, a section, a diff).
If the target is stale or could mean several things, ask one question that names the candidates.
Then state in one sentence the goal that work serves and what judges success.
Everything below is measured against that sentence.

## Size the audit to the work

Each agent costs tokens and a handoff, so match the audit to what is at stake.
When two sizes fit, use the larger.

- A small output (an answer, a few lines of code): no agents. Write the report below from the sources.
- A change or a document that no agent will carry out: one blind reviewer (step 2), then steps 4 and 5, then the report.
- Anything another agent will carry out (a ticket, a plan, a protocol), a design, a research claim or an experiment plan: the full audit.

## Full audit

Blind means the agent's brief holds the artifact path, the goal sentence, the paths of the sources the work rests on, and the titles of the settled decisions the artifact itself cites.
It holds nothing from this conversation: not your reasoning, not your conclusion.
Every agent here is read-only; say so in its brief.

1. **Second design.** A fresh Opus agent gets the goal, the constraints and the sources, and not the work, and designs its own approach.
   It runs nothing and files nothing; its design goes to part 5 of the report.
2. **Review.** Blind reviewers: a Fable agent (`escalate` where the host has it; brief it by the project's `fable-prompting` skill where there is one) and Codex (`${CLAUDE_SKILL_DIR}/../codex-review/SKILL.md` for a diff; for anything else a read-only `codex exec` given the same blind brief).
   The middle size uses one of the two.
   Ask for gaps that would change the outcome for the judge; leave out style and anything that existed before this work.
   Each finding carries a file:line or a quote, the failure it causes, and a check that reproduces it.
   Settled decisions are not reopened.
3. **Dry run, for anything another agent will carry out** (a ticket, a plan, an experiment protocol).
   Give each one alone to a fresh Opus agent that builds nothing.
   It restates the goal, lists every question and assumption it would have to make, and says how it would know it was done.
   Each question is a gap; close it in the work directly, without step 4.
4. **Verify.** Each review finding goes to an Opus agent that tries to reproduce it against the source and cites file:line either way; one agent may take several findings when there are many.
   A finding is not dismissed with a defense that nobody located and read.
   A finding that does not reproduce goes into the report as rejected, with the attempt.
5. **Fix.** Fix reproduced findings only, each with the smallest change that removes its cause.
   Work that is this session's own and not yet merged is fixed in place; a change to a shared plan, a ruling or a frozen file is proposed as a diff and waits for the owner.
   Then re-run only the reviewer whose finding was fixed, once; report anything still open instead of starting another round.

What a reviewer looks for depends on the work:

- A research claim: another explanation for the same evidence; whether the cited source says what is claimed, checked by reading it; prior work that already did this.
- An experiment: whether the measurement tests the claim; the control; whether the result would have looked the same if the hypothesis were false.
- A plan, a design or a ticket: a step that rests on something nobody verified.
- Code: run it the way a user meets it and show the output.

A condition a reviewer sets (for example "stop at the first error") holds for this audit only; do not carry it into later work or notes.

## Report

About 400 words; the updated work is separate.

1. **Claims.** Each main claim with its evidence (file:line, a command and its output, or a quote) and a tag: ran / read in full / inferred / from memory.
   Re-read the source for anything you would tag from memory, and tag it by what you did.
2. **Weakest point** and the cheapest check that settles it. Run the check if it is read-only and free, and give the result; otherwise name it and its cost.
3. **Failure.** Assume this failed two weeks from now. Name the most likely cause.
4. **Missing.** What the owner has not asked about, including what the request itself gets wrong.
5. **Second design against ours.** What differs, what to adopt, what it improves (quality, time, risk) and what it costs. If ours is best, say so in one line.
6. **Rejected findings**, one line each with the reason.

Write "none that matters" for an empty part.
Then give the updated work, in the form it already has (the file, the diff, the page).
