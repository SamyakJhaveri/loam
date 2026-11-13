---
name: audit
disable-model-invocation: true
effort: xhigh
description: "The owner's end-of-work audit, in his own words: audit what you just proposed or did with blind Fable and Codex reviewers, Opus verifiers and fixers, and a surprise-me agent; report confidence, weakest point, what he is missing, blind spots, claims made without reading the source, and a simpler approach; then hand back the fixed work. Manual-only; an agent told to run it reads this file by path."
argument-hint: [what to audit; default is what you just proposed or did]
---

# Audit

The owner typed the instruction below by hand at the end of many sessions, and it worked.
This file keeps it as he wrote it, with spelling and numbering fixed, and adds only how to carry it out on each host.
It is his instruction to you, the agent that did the work. Everything after it serves it and never narrows it.

Target: `$ARGUMENTS` if that names one; otherwise what you just proposed or did in this session, including claims you made in chat.

## The owner's instruction

> Audit using a blind agent, or set of agents, what you just proposed or did.
> I use this checkpoint because you sometimes drift from the goal or sound more certain than the evidence allows.
> Answer in these six parts, 400 words or less in total:
>
> 1. **Confidence:** for each claim, idea or engineering work you did, rate your confidence in its correctness out of 10, including the evidence or reasoning it rests on (file:line, command output, or a quote from a source you read in full). What would change your mind about it, to improve that confidence?
> 2. **Weakest point:** the part you are least sure of, and the cheapest check that would settle it. If you can run that check now, run it, then report the result.
> 3. **What I am missing:** an important thing about this I have not asked about. Include what my request itself gets wrong, if anything.
> 4. **Blind spots:** what are our blind spots in what we have done so far, or in my requests, that we are not yet looking into but should?
> 5. **From memory:** anything you stated from memory, a repo doc, or an abstract rather than from reading the actual file, output, or paper. Make sure you actually read the source material, navigating to the part that holds the content you are looking for.
> 6. **Simpler or more elegant:** knowing what you know after your proper reading of the files or URLs, and our discussions, set aside what you proposed. Knowing what you know now, is there a simpler or more elegant approach? Think of more elegant research and/or engineering solutions and their consequential impact on quality and efficiency. Name it, say what it improves (quality, time, risk) and what it costs. If the current approach is already the best, say so in one line.
>
> If a part has nothing that matters, write "none that matters" instead of filling it.
>
> Use the Fable and Codex review agents, tools and slash commands we have available to review the work we did here.
> The Fable and Codex agents are read-only; the issues they point out should be verified by Opus agents, and confirmed or rejected.
> Then the Opus workers make the fixes.
> Make sure to look into reliable sources; some of them are also saved in files in the repo for easy access.
> Also launch a surprise-me agent to come up with better solutions.
>
> Finally, give me the updated version of the work based on the findings you get from this audit.

## Why the steps below are not optional

Your host's default guidance tells you to start few agents and to weigh their cost.
Here the owner has asked for each agent by name, so every role below runs on every audit.
Small work makes each agent quick; it does not make one optional.

These ways of ending early defeat the audit:
- shrinking it because the work looks small or agents cost tokens;
- ending your turn with a summary that announces the next step, or an offer to fix, instead of fixing;
- writing the report while an agent or command you started is still running;
- dropping a finding as out of scope, pre-existing or settled without opening the file or ruling that shows it.

Copy this checklist into your task list and tick each item; the audit is not done while one is open:
1. Target, owner's words, sources and constraints gathered.
2. Fable and Codex reviewers launched.
3. Your own pass done: scores, sources re-read, weakest-point check run.
4. Surprise-me launched with the corrected evidence.
5. Every finding verified.
6. Confirmed findings fixed and re-reviewed.
7. Report and updated work delivered.

## 1. Gather

- **Target:** the files, diffs, plans and chat claims under audit, plus what they depend on.
- **The owner's words:** his requests and later corrections that led to this work, quoted verbatim. These, not your summary of them, are the goal every agent measures against.
- **Sources:** the files, data, papers and docs the work rests on, including the copies the project keeps in the repo (search it before the web).
- **Constraints:** the project's recorded rulings and permission rules that bear on the work, by title and path.

Ask the owner one question only when the target could mean materially different things; otherwise name it in one line and go on.

## 2. Launch the reviewers, in the background, at once

A blind brief holds the target paths, the owner's words, the sources, the constraints, what the reviewer may and may not do, and the output asked for.
It leaves out your reasoning, your conclusions and your confidence.
Start each reviewer with fresh context, never a fork of this conversation.
Write the brief to a file when a command-line reviewer needs one.

The brief asks the reviewer to:
- find where the work drifts from the owner's words, and what his request itself gets wrong;
- find claims stated more certainly than their evidence allows, reading the primary source at the part that holds the fact, not an abstract or a summary;
- name blind spots: lines of inquiry neither the work nor the owner has opened, and the most likely reason this fails two weeks from now;
- check by kind of work:
  - a research claim: a rival explanation for the same evidence; whether the cited source says what is claimed; prior work that already did this, searched by name;
  - an experiment: whether the measurement tests the claim; the control; whether the result would look the same if the hypothesis were false;
  - a plan, design or ticket: each step that rests on something nobody verified, and, for work another agent will carry out, every question that agent would have to guess;
  - code: run it the way a user meets it and show the output;
- report every finding, however small, since filtering happens later, each with its evidence (file:line, a quote, or a command and its output), the failure it causes, and a check that reproduces it;
- criticize a recorded ruling when new evidence bears on it; the ruling stands until the owner changes it;
- edit nothing; scratch files go only in a temporary directory.

| Role | Claude Code | Codex |
|---|---|---|
| Fable reviewer | an `escalate` agent (Fable 5.2, high); brief it by the project's `fable-prompting` skill where there is one | `claude -p --model claude-fable-5-2 --permission-mode plan "Read <brief file> and follow it."` if the `claude` CLI runs; otherwise a fresh native agent, and the report says Fable did not review |
| Codex reviewer | one bare `codex exec -s read-only -c model_reasoning_effort=xhigh -o <report file> "Read <brief file> and follow it."` in the background; for a diff, `${CLAUDE_SKILL_DIR}/../codex-review/SKILL.md` without its "do not question the intent" line | a fresh native agent (`fork_turns="none"` where the spawn tool offers it) |
| Surprise-me, verifiers, fixers | Opus agents | fresh native agents |

`${CLAUDE_SKILL_DIR}` is this file's folder in Claude Code; on another host use the folder you read this file from, and give every agent the resolved path.

## 3. Your own pass, while the reviewers run

Do this before you read any review, so the reviews can contradict you.
- **Part 1:** list every claim, idea and piece of engineering in the work, each with a score out of 10, the evidence it rests on, and what would change your mind. Earlier evidence counts once you check it still applies.
- **Part 5:** for each claim you made from memory, a repo doc or an abstract, open the source, go to the part that holds the fact, read it, and correct the claim and its score. A claim you cannot find support for is withdrawn.
- **Part 2:** run the cheapest check that settles the weakest point, within what you are already allowed to do; local tests and temporary files are fine. If it cannot run, name what blocks it.

A score is your judgment, not a probability. Give the evidence behind it, not a log of your reasoning.

## 4. Surprise-me, knowing what you know now

After your own pass, start one agent that reads `${CLAUDE_SKILL_DIR}/../surprise-me/SKILL.md` and runs its solo process.
Its goal is the owner's words, its default to beat is the work as you have now corrected it, and it gets the corrected evidence and the constraints.
It files nothing into plans; its step 7 stays a proposal in its answer.
Its factual claims go to the verifiers like any finding.

## Verify findings

Every reviewer finding and every factual claim from surprise-me goes to a fresh Opus verifier at xhigh, read-only; one verifier may take several findings.
The verifier tries to reproduce each finding against the source and cites file:line either way, then gives one verdict:
- **confirmed:** it reproduces as stated;
- **partly:** part of it reproduces; say which part and what fix that part needs;
- **rejected:** the attempt shows it does not hold, with the command and its output, or the passage read;
- **unresolved:** the access, data or hardware to settle it is missing; say what is missing. A host without this verdict counts it as confirmed and says what could not be checked.

A finding is never rejected on a defense nobody located and read.
A confirmed finding that does not bear on the owner's goal is listed under other findings, not fixed.

## 5. Fix, then review again

Opus workers fix every confirmed or partly confirmed finding that bears on the goal, each with the smallest change that removes its cause.
Give edits to the same file to one worker.
Adopt a surprise-me idea when verification shows it beats the current work on the owner's goal; otherwise say in one line why not.
Follow the project's permission rules: where they reserve a merge, a change to a recorded ruling or frozen file, spending, or publishing for the owner, prepare it as a ready diff or pull request and go on with the rest.

Then send the changed parts back to the reviewers whose findings were fixed, verify what they return, and re-score the claims the fixes touched.
Repeat while a confirmed finding is open.
After three rounds, stop and mark the report INCOMPLETE, naming what is still open and why.

## 6. Report and hand back

Wait for every agent and command you started.
Answer the six parts in order, 400 words or less, with "none that matters" for an empty part.
Put the full claim list (each claim, score, evidence, what would change your mind) and every verdict with its evidence in a file beside the work, or an artifact page where the host has one; part 1 links it and names only the claims scored below 8 or whose score moved.
Then give the updated work in the form it already has: the file, the diff, the pull request or the page.
