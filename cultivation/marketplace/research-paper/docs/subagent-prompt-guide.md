# Writing subagent prompts for paper review and paper writing

Rules for writing a Claude Code subagent prompt (an agent file or a task message) for the work this plugin does: review seats, critics, the adjudicator, gates and writers.
Written for subagents on `claude-opus-5-5`; recheck the sources when the model changes.
The agents in `../agents/` follow these rules.

Tags: [A] = Anthropic, [U] = users or third-party tests, [H] = a house rule of this plugin.
Source keys:
G55 = https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 ;
G5 = https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 ;
BP = https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices ;
SA = https://code.claude.com/docs/en/sub-agents ;
MC = https://code.claude.com/docs/en/model-config ;
PB = https://claude.dev/blog/getting-the-most-out-of-opus-5-5/ ;
CO = https://claude.dev/blog/what-a-task-costs-on-opus-5-5/ ;
CR = https://www.coderabbit.ai/blog/opus-5-5-model-review (vendor test).

## 1. What the harness already supplies

A custom subagent gets its own body plus "basic environment details like the working directory, not the Claude Code system prompt" [A, SA].
[H] In local transcripts of custom agents on Opus 5.5, none carried the main prompt's autonomy block, its section on delivering work, its progress-update line, its tool-batching line or its note on pasted content.
Those live in the main session's prompt only, so an agent file states its own stop rule, and the advice "never paste these" applies to the main prompt, not to an agent file.

Never paste what a custom agent already gets [A, SA#what-loads-at-startup]: every CLAUDE.md and AGENTS.md level unless `omitClaudeMd: true` (this carries a project's writing rules), a git status snapshot, and the skills listed in `skills:`.

Set outside the prompt [A]:
- Effort: frontmatter `effort` "Overrides the session effort level"; "There is no per-subagent thinking setting" (SA).
- Early stops: the lead resumes a subagent that stopped with items open, and stops "after two or three automatic continuations" (G55#unattended-agentic-runs).

## 2. Rules for every prompt [A]

1. Name the stops: the model "is responsive to instructions that name the specific kinds of early stop you want it to avoid", and "It also helps to name the stops you do want" (G55#unattended-agentic-runs).
2. "state the completion condition up front" (G55#unattended-agentic-runs).
3. For long passes: "Keep the task's parts in a checklist the model updates" (G55#unattended-agentic-runs).
4. Delete "think carefully" lines: "The model decides for itself how much to think, and effort is the main control" (G55#thinking-instructions-in-chat-system-prompts).
5. Never ask for its reasoning in the reply: "If your prompts ask the model to write out its reasoning in the response, remove those instructions" (G55#safeguard-refusals).
   A short reason is fine: "Explain why you chose this approach in three sentences" (PB).
6. Name concrete patterns, since a general instruction "mostly swaps one default for another" (G55#frontend-design-defaults; extended here beyond frontend work).
7. Point it at sources: "it helps to tell the model to look through the relevant sources before acting" (G55#explore-context-in-multi-app-workflows).
8. Wrap third-party text the lead pastes into the task in `<pasted_content id="...">` tags plus the guide's note (G55#mark-pasted-text-in-user-messages).
9. Give the whole specification at once: "it performs best when given the complete task specification up front" (G5#capability-improvements).

## 3. Reviewer rules

Evidence:
- [A] "ask Claude to quote relevant parts of the documents first" (BP#long-context-prompting); "Mark anything you couldn't confirm, and say where you looked" (PB).
- [H] Every number comes from a command run or a file read in the same session, labelled Verified, Likely or Assumption.
- [H] Each reviewer lists the sections it read; the system card reports "describing a partial check as a full read" [A, via https://thezvi.substack.com/p/claude-opus-55-the-system-card].

Severity:
- [A] "only report high-severity issues" or "be conservative" makes the model "report less; ask it to report everything and filter in a separate pass instead" (G5#capability-improvements).
- [H] PB's "List only problems you'd block the merge for" belongs in the adjudicator, not in the seats.

False positives:
- [A] Per finding: "why it's wrong, and how to show it fails" (PB).
- [A] The adjudicator applies "check its evidence before you accept it" (PB).
- [H] For every gate or check reported, one sentence names what it does not establish (the `not_established` field of a finding).

Coverage and precision:
- [U] "Turning up effort did not consistently produce a better review"; two settings each caught 10 of 13 hard bugs "but they missed different ones" (CR).
  So the seats differ in lens, and the adjudicator gets their union.
- [A, system card] It "has checked a plan against requirements it wrote itself", so give reviewers outside criteria, not the author's rationale.
- [U] "Never use the same context/session for both writing the code and reviewing the code" (https://www.reddit.com/r/ClaudeCode/comments/1wqnjkp/, 57 points, 67 comments; comment score 8).

When to stop:
- [H, from rule 2] Done means every input section has findings or "no finding".
- [A] No time budget: "under time pressure the model might search and verify a little less" (G55#time-signals-for-multi-agent-harnesses).
- [A] No "treat that answer as done" line: it "may also make the model less likely to point out a mistake in an earlier answer" (G55#thinking-instructions-in-chat-system-prompts).

## 4. Model and effort per role

| Role | Model, effort | Evidence |
|---|---|---|
| Reviewer seat | Opus 5.5, `high` | [A] `high` is for "Work where verification matters or edge cases are likely"; `max` "is prone to overthinking" (MC#adjust-effort-level). [U] CR's higher-effort setup had 35.7% precision against 38.6%. |
| Critic | Opus 5.5, `high` (`lean-critic-forensic`); Fable 5.1 only through the user-level `escalate` agent type | [U] "each time Fable catches gaps" (1wqnjkp, comment score 11). [H] `escalate` is the blind second opinion on another model. |
| Adjudicator | Opus 5.5, `high` | Its job is verification (MC, as above). |
| Gate | Opus 5.5, `low` or `medium`, plus a script | [A] "before you raise effort, check whether the model has a way to check its work"; "Use low for mechanical work" (CO). |
| Writer | Opus 5.5 `high` drafts; Fable 5.1 or a person edits | [U] "As an editor, it ranked behind even Opus 5" (https://every.to/vibe-check/vibe-check-opus-5-5-is-pulling-our-codex-converts-back-to-claude). [A] Fable 5.1 for "analysis carried through to a finished document" (https://platform.claude.com/docs/en/about-claude/models/choosing-a-model). |

Escalate [A]: "If Opus 5.5 on xhigh hits the same problem twice, switch" to Fable 5.1 (CO).
Some setups default reviewers to effort `max`, but no source here measures a gain from it.

## 5. Skeleton

```
---
name: paper-review-<lens>
description: <one line>
tools: Read, Grep, Glob, Bash
model: claude-opus-5-5
effort: high
---
Role: You review <section> of a <VENUE> submission through the <lens> lens. You do not edit files.
Inputs: read all before judging: paper/tools/contract.md under ROOT; <paper paths>; criteria <call for papers path>, <prior reviews path>; numbers <results file path>.
Lens: <3 to 6 named patterns>, because <one-sentence reason>.
Procedure: read every input; quote, check and record each suspect passage.
Evidence rule: quote the sentence with page and line; check each number against <path>; mark what you could not confirm and where you looked.
Output schema: one row per finding: id, location, quote, problem, how to show it fails, severity (report all), Verified/Likely/Assumption. Then: sections read.
What it does not establish: one sentence per check.
Stop condition: done when every input section has findings or "no finding". Stop early only if an input path is missing. Do not end on a plan or an offer.
```

## 6. Stop doing [A]

- "think carefully" lines and requests for written-out reasoning (rules 4 and 5).
- Prompt text meant to cut thinking; lowering effort does it "more reliably than prompt instructions do" (G55#calibrate-effort).
- Old or blanket effort levels: "rather than carrying over the setting you used on Claude Opus 5"; "Reserve `xhigh` and `max` for work where you've measured a quality gain" (G55#calibrate-effort).
- "double-check your answer" and "re-verify before responding" (G5#self-correction).
- In reviewers: "only report high-severity issues", time budgets, and "treat that answer as done" (section 3).
