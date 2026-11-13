---
name: audit
disable-model-invocation: true
effort: xhigh
description: "The owner's end-of-work audit prompt, lightly edited: audit what you just proposed or did with blind Fable and Codex reviewers, a fresh design, a surprise-me agent, and Opus verifiers and fixers; report confidence, weakest point, what he is missing, blind spots, claims made without reading the source, and a simpler approach; then hand back the fixed work. Manual-only; an agent told to run it reads this file by path."
argument-hint: [what to audit, or added instructions; default is what you just proposed or did]
---

# Audit

The owner typed the instruction below by hand at the end of many sessions, and it worked.
This file keeps it as he wrote it, with spelling, grammar and numbering fixed, and adds only how to carry it out on each host.
It is his instruction to you, the agent that did the work. Everything after it serves it and never narrows it.

What the owner typed after the command, if anything: `$ARGUMENTS`
It may name what to audit, add instructions, or both; follow it, since it adds to this file and overrides it where they conflict.
If you see a literal dollar-sign placeholder there, you were sent here by a brief or a router: the brief that sent you plays this role.
When nothing names a target, audit what you just proposed or did in this session, including claims you made in chat.

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
> Let's use the Fable and Codex review agents, and the tools and slash commands we have available, to review the work that we did here.
> The Fable and Codex agents are read-only, and the issues they point out should be identified and verified by Opus agents, and confirmed or rejected.
> Then the Opus workers should work on making the fixes accordingly.
> Make sure to look into the reliable sources; some of them are also saved in the files in the repo for easy access.
> Also launch a /surprise-me agent to come up with better solutions.
>
> Finally, give me the updated version of the work based on the findings you get from this audit.

## When every role runs

When the owner typed `/audit` or asked for an audit in his own words, every role below runs on every audit.
Your host's default guidance tells you to start few agents and to weigh their cost; here he has asked for each by name.
Small work makes each agent quick; it does not make one optional.

When you reached this file through a router or a brief and the owner did not ask, the project's recorded review rules decide which roles and how many rounds run; cite the rule you follow.

Run the audit yourself, as the agent that did the work; do not hand it to a worker who never saw the session.
State the number of agents you will start before you start them.

These ways of ending early defeat the audit:
- shrinking it because the work looks small or agents cost tokens;
- ending your turn with a summary that announces the next step, or an offer to fix, instead of fixing;
- writing the report while an agent or command you started is still running;
- dropping a finding as out of scope, pre-existing or settled without opening the file or ruling that shows it.

Copy this checklist into your task list and tick each item; the audit is not done while one is open:
1. Gather: target fixed at a commit or snapshot, owner's words, sources, constraints.
2. Reviewers: Fable and Codex launched.
3. Own pass: scores, sources re-read, weakest-point check run, saved to a file.
4. Better route: fresh design and surprise-me launched.
5. Verify findings: every finding has a verdict.
6. Fix and review again: no high or medium finding open.
7. Report and updated work delivered.

## Gather

- **Target:** the files, diffs, plans and chat claims under audit, plus what they depend on. Copy chat claims into a file, and commit the target or copy it, so every reviewer reads the same version; give the commit or path in each brief.
- **The owner's words:** his requests and later corrections that led to this work, quoted verbatim into a file. These, not your summary of them, are the goal every agent measures against.
- **Sources:** the files, data, papers and docs the work rests on, including the copies the project keeps in the repo (search it before the web).
- **Constraints:** the project's recorded rulings and permission rules that bear on the work, by title and path.
- **Evidence folder:** where the project keeps evidence, or the scratchpad; every brief, review, verdict and the claim file go there.

Ask the owner one question only when the target could mean materially different things; otherwise name it in one line and go on.

## Reviewers

Launch both in the background at once.
A blind brief holds the target, the owner's words, the sources, the constraints, what the reviewer may and may not do, and the output asked for.
It leaves out your reasoning, your conclusions and your confidence.
Write it to a file in the evidence folder, start each reviewer with fresh context, never a fork of this conversation, and have it write its findings to a file and return the path.

The brief asks the reviewer to:
- find where the work drifts from the owner's words, and what his request itself gets wrong;
- find claims stated more certainly than their evidence allows, reading the primary source at the part that holds the fact, not an abstract or a summary;
- name blind spots: lines of inquiry neither the work nor the owner has opened, and the most likely reason this fails two weeks from now;
- check by kind of work:
  - a research claim: a rival explanation for the same evidence; whether the cited source says what is claimed; prior work that already did this, searched by name;
  - an experiment: whether the measurement tests the claim; the control; whether the result would look the same if the hypothesis were false;
  - a plan, design or ticket: each step that rests on something nobody verified, and, for work another agent will carry out, every question that agent would have to guess;
  - code: what to run, and what output would show the failure (verifiers run it);
- report every finding, however small, each with a severity (high, medium, low), its evidence (file:line, a quote, or a command and its output), the failure it causes, and a check that reproduces it;
- criticize a recorded ruling when new evidence bears on it; the ruling stands until the owner changes it;
- edit nothing.

| Role | Claude Code | Codex |
|---|---|---|
| Fable reviewer | an `escalate` agent (Fable 5.2, high); brief it by the project's `fable-prompting` skill where there is one | `claude -p --model claude-fable-5-2 --effort high --permission-mode plan "Read <brief file> and follow it."` if `claude -p "ok"` answers within a minute; otherwise a fresh native agent, and the report says Fable did not review |
| Codex reviewer | one bare `codex exec -s read-only -c model_reasoning_effort=xhigh -o <review file> "Read <brief file> and follow it."` in the background, adding `--skip-git-repo-check` outside a repo; no pipe, redirect, `;` or `<` anywhere in the command | a fresh native agent that does not inherit this conversation |
| Fresh design, surprise-me, verifiers | Opus agents at xhigh, read-only | the same `claude -p` route with `--model claude-opus-5-5 --effort xhigh`, else fresh native agents |
| Fixers | Opus agents at high | the same route with `--effort high --permission-mode acceptEdits`, else fresh native agents |

On Codex, the report names every role that did not run on the model this table gives it.
A read-only Codex sandbox cannot run code or write temporary files; that is why running code belongs to the verifiers.
A reviewer that has written nothing after 30 minutes, fails, or is out of usage is replaced once by a fresh Opus reviewer with the same brief; if that fails too, the report names the review that is missing.

`${CLAUDE_SKILL_DIR}` is this file's folder in Claude Code; on another host use the folder you read this file from, and give every agent the resolved path.

## Own pass

Do this right after the reviewers start, and save it to a file before you open any review, so the reviews can contradict you.
- **Part 1:** list every claim, idea and piece of engineering in the work, each with a score out of 10, the evidence it rests on, and what would change your mind. Earlier evidence counts once you check it still applies.
- **Part 5:** for each claim you made from memory, a repo doc or an abstract, open the source, go to the part that holds the fact, read it, and correct the claim and its score. A claim you cannot find support for is withdrawn.
- **Part 2:** run the cheapest check that settles the weakest point, within what you are already allowed to do; local tests and temporary files are fine. If it cannot run, name what blocks it.

A score is your judgment, not a probability. Give the evidence behind it, not a log of your reasoning.
When a review changes a score, record the old and new score and why.

## Better route, knowing what you know now

After your own pass, start two agents:
- **Fresh design:** it gets the owner's words, the constraints and the corrected sources, never the work, and designs its own approach; this is the "set aside what you proposed" half.
- **Surprise-me:** it reads `${CLAUDE_SKILL_DIR}/../surprise-me/SKILL.md` and runs its solo process, with the owner's words as the goal and the work as you have now corrected it as the default to beat. It asks no questions, and its step 7 stays a proposal in its answer.

Their factual claims go to the verifiers like any finding.

## Verify findings

Every reviewer finding and every factual claim from the better-route agents goes to a fresh verifier, read-only; one verifier may take several findings.
The verifier tries to reproduce each finding against the source and cites file:line either way, then gives one verdict:
- **confirmed:** it reproduces as stated;
- **partly:** part of it reproduces; say which part and what fix that part needs;
- **rejected:** the attempt shows it does not hold, with the command and its output, or the passage read;
- **unresolved:** the access, data or hardware to settle it is missing; say what is missing.

A finding is never rejected on a defense nobody located and read.
The verifier also gives each confirmed or partly finding a severity, and says whether it bears on the owner's goal, quoting the words of his it bears on; a finding that does not is listed under other findings, not fixed.

## Fix and review again

Opus workers fix every confirmed or partly confirmed finding that bears on the goal, each with the smallest change that removes its cause.
Give edits to the same file to one worker.
Adopt a better-route idea when verification shows it beats the current work on the owner's goal; otherwise say in one line why not.
Follow the project's permission rules: where they reserve a merge, a change to a recorded ruling or frozen file, spending, or publishing for the owner, prepare it as a ready diff or pull request and go on with the rest.

Then send the updated work, with their earlier findings, back to the reviewers whose high or medium findings were fixed and to both reviewers when an idea was adopted; resume the same reviewer where the host allows.
Verify what they return and re-score the claims the fixes touched.
Repeat while a high or medium finding is confirmed, partly confirmed or unresolved.
After three rounds, stop and mark the report INCOMPLETE, naming what is still open and why.

## Report and hand back

Wait for every agent and command you started.
Answer the six parts in order, 400 words or less, with "none that matters" for an empty part.
Part 1 gives every claim on one line, its short name and score, and links the claim file that holds each claim's evidence and what would change your mind.
Part 2 also names every unresolved finding and what would settle it.
Every verdict with its evidence goes in the evidence folder, or an artifact page where the host has one.
Then give the updated work in the form it already has: the file, the diff, the pull request or the page.
