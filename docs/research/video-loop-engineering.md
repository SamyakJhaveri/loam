# What the loop-engineering video teaches

Lean v3 takes three things from this video: a written pass-or-fail answer key as the completion condition per ticket, a fixed judge prompt the planner cannot author, and explicit iteration, time, and spend caps, which the video lacks.
It also takes the fog rule: an unsettled decision becomes an explicit question, never an assumption.
It does not take letting the main agent invent the checking criteria, or any reading in which the critic's free-text verdict gates safety rather than quality.

Source: <https://www.youtube.com/watch?v=D_uojDHkbw4>, "This Claude Skill Just Fixed Loop Engineering", channel AI LABS, 14:31.
Method: `watch` skill, `--detail transcript --no-whisper`, transcript-only with no frames.
Timestamps are caption times.
My own reasoning is labelled **Inference**.

## The loop it teaches

A loop is when the human leaves the prompt, inspect, correct cycle: you give the agent the goal and the standard, and it checks its own work until it gets there [01:03]-[01:22].
The specific method is the "gauntlet loop", named by Matt Schumer after a one-prompt first-person-shooter demo [01:40]-[02:03], a three-line prompt [02:45]-[02:51]:

1. What you are building and the quality bar, for Schumer the most recent Call of Duty games [02:56]-[03:16].
2. How to build: the main agent breaks the goal into parts and hands each to its own sub-agent, each in its own memory [03:17]-[03:37].
3. The quality level the final output must match, which is what tells the critic when it may stop [04:16]-[04:22].

Each builder gets its own loop with a separate review sub-agent, the critic [03:48]-[03:56].
The shape is a diamond graph: one task fanning out to parallel sub-agents, then narrowing back to one agent [04:57]-[05:30].
The prompt ends with the keyword "ultra code", which the video says turns the run into a "dynamic workflow" running a fleet of sub-agents at once [04:46]-[04:52]; I did not verify that this keyword exists.

**Inference.** For Lean v3's six tickets the transferable shape is one planning pass that produces the standard, per-ticket workers, a fresh critic per worker, and a final narrowing agent. The tickets are already the split.

## The completion condition

The video's central claim: "good is something it decides for itself, and an agent that decides its own standard passes its own work", so Schumer gave it a real game to measure against [02:03]-[02:12].
The critic's stopping test is a blind comparison of the built thing and the reference, without being told which one Claude made [04:26]-[04:45].

The critic [03:56]-[04:15]: it only checks and never builds, starts with no memory, does not know who made the work or how many times it has been sent back, is told to be "brutal and critically honest", and returns work until it passes.

For projects with nothing to copy, the fix is a written spec as the bar [10:20]-[10:40], produced by a modified version of Matt Pocock's Wayfinder planning skill [08:34]-[08:56], [11:02]-[12:00].
The modified skill emits two files into a `.wayfinder` folder [12:26]-[12:47]: the **map**, every decision, its reason, and what the finished thing should look like, and the **answer key**, "nothing but checks, where every line comes back as either a pass or a fail".
The gauntlet prompt then points at `.wayfinder` instead of a game [12:56]-[13:15].
Wayfinder reaches those decisions by interview, 34 questions in the session shown, and is a manual skill [12:06]-[12:33].

**Inference.** The pass-or-fail answer key is the single most portable idea. A binary per-line checklist is a completion condition a worker cannot argue with, and it is the same artifact regardless of who reads it. Keep it under Loam's gitignored `.superpowers/` rather than adding a `.wayfinder` folder.

## Cost and time

The video gives no cost mechanism, only measured outcomes.

| Measure | Value | Timestamp |
|---|---|---|
| Intro example build time | over 1 hour | [00:12] |
| HR system build time | 1 hour 33 minutes | [13:38] |
| Session limit consumed (Max plan) | about 40 percent | [13:40] |
| Equivalent API cost | about $116 | [13:44] |

It calls $116 "a lot" [13:49] but proposes no budget cap, no iteration cap, no wall-clock limit, and no early-abort rule; the only exit is the critic passing the work.
Its bounding argument is upstream: a drifting critic wastes "a lot of time and tokens", so fix the standard before the loop starts [07:44]-[08:00].

**Inference.** A loop whose only exit is "the critic is satisfied" has no upper bound. Lean v3 must add an iteration cap per ticket and a wall-clock or spend cap.

## Roles and the fixed judge prompt

Three roles: main agent (planner) splits the work and in the HR run planned, installed tools, laid the foundation, then launched many agents [13:22]-[13:38]; sub-agent (worker) in its own memory [03:30]-[03:37]; critic (judge) attached to each builder, memoryless, checks only [03:50]-[04:14].

The video's first named problem is that this separation is not enforced [06:36]-[07:13].
The main agent is "completely responsible for checking", spins up the critics and writes their instructions, and "you don't have control on the agents nor how the judgment prompt is being passed to the critics".
Past the reference game, the prompt only says be a really harsh critic and check it visually [06:59]-[07:03].

**Inference.** The judge's independence is only as strong as the judge's prompt, and here the planner writes it. For Lean v3 the judge prompt and its pass criteria are a fixed file the planner cannot rewrite.

## Drift

The second named problem [07:13]-[08:20]: when there is no existing product to copy, "the critic makes up a standard and starts passing work by it", and you come back to "a pile of features that all got built in one go against a standard the agent made up itself".
"Having nothing to compare the work to is the normal case, not the exception" [08:05]-[08:08], so "the gauntlet loop works when there's something close enough to copy, and it breaks the moment there isn't" [08:14]-[08:20].

The related planning failure is Pocock's "fog" [08:56]-[09:20]: the agent never says it is in the fog, fills the gap with an assumption, and returns a plan that looks finished with invented parts.
Wayfinder's answer [09:26]-[09:58]: every remaining decision becomes a question on the map, split into answerable now and blocked; fog is cleared by research, a rough build, or a real-world action, and each answer unblocks what was waiting.

The fixed loop still was not clean: every feature worked "though it did have some issues" [13:51]-[14:00], after being told "no close enough and no shortcuts" [13:26]-[13:29].
The video says nothing about drift within a single long run; its whole analysis is about the standard being wrong from the start.

## Loam design laws 2 and 3

Law 2, nothing parses free text to decide safety: the critic decides pass or fail by judging free text and rendered output, so it conflicts if treated as a safety control.
The answer key reduces this, since a pass-or-fail line is closer to an assertion than a verdict [12:44]-[12:47].
**Inference.** The critic is a quality gate, not a safety gate. It may judge whether work is good, never whether an action is safe; safety stays with deny rules, the sandbox, git, and CI. Any answer-key line that gated a destructive or outward-facing action belongs in `bin/check` or CI instead.

Law 4 tension: an answer key is a second place where checks live.
Lean v3 should make the answer key call `bin/check` for anything mechanically checkable and reserve answer-key lines for judgements `bin/check` cannot express.

Law 3, no hook on any tool matcher: no conflict.
The video's entire control mechanism is prompt content and sub-agent structure; the critic is a spawned sub-agent, not a harness interception.

## Risks

Single source, transcript-only, auto-captioned, from a channel that sells a paid community and ran a sponsor segment [05:38]-[06:32]; on-screen prompt and answer-key text were never seen, and "ultra code" is unverified against Claude Code documentation.
The $116 and 40-percent figures are the video's own unaudited numbers for one build.

## Transcripts, read in full 2026-09-09

The full transcripts of the three AI LABS videos were fetched on the runner with `youtube-transcript-api` (YouTube rate-limits the Mac) and copied to `.superpowers/transcripts/<video id>.txt`, gitignored because the full text is not ours to publish.
Line numbers below are lines of those files.
Everything above this section for the D_uojDHkbw4 video was written from a caption-only read on 2026-09-06 and stands.

### PLyRe6Zk--8, "Every Level Of Claude Code Loop Engineering Explained" (736 lines)

- Three levels (lines 8-11): level one is the basic unit, level two the factory, level three "finally frees" the human.
- Level two (lines 408-490): the main agent picks a queue row, hands it to a build subagent on a branch, then to an adversarial review subagent with a fresh context, and loops until the row is ticked; a pull request with screenshots is opened and a human merges.
- The rule (lines 452-455), verbatim: "The agent that does the work should never verify it. The verification should always go to another agent with a fresh context window."
- The reviewer's stance (lines 457-460): the review agent "always needs to believe that there is some error in the work done".
- Merge stays human (lines 477-486): "When a feature is done, a pull request is made", and "If it's correct, you can merge the pull request."
- The screenshot tool (lines 236-240 and 276-279) exists because a screenshot "only ever catches" what is on the page; the blinking mascot was the error no screenshot caught.

What the factory already has: this exact shape, with the judge and reviewer as the fresh-context review agents and human merge as the only merge (`../factory/ARCHITECTURE.md`, stage table).

### D_uojDHkbw4, "This Claude Skill Just Fixed Loop Engineering" (461 lines)

- The diamond graph (one planner, parallel subagents each with a critic, one integrator) has two failures the video names: the orchestrator writes the critic prompts itself, so "you don't have control on the agents nor how the judgment prompt is being passed to the critics" (lines 220-222); and the bar must be a concrete reference, an answer key "where every line comes back as either a pass or a fail" (lines 408-410).
- The run "took 1 hour and 33 minutes" (line 437) and "would have cost around $116" (line 441) at API rates.

### c47uqR7XB_c, the Unlazy walkthrough (403 lines)

- Gates carry a command, the expected output, and an evidence line; "A tick box with pending still under it" means the agent ticked it itself, "so, it counts as unmet" (lines 254-257).
- In orchestrated mode the main agent "doesn't take its word for it and runs that task's checks against itself" (lines 268-270).
- The plan file names which task works with "which file so that if two agents are working at the same time, they don't overwrite each other's work" (lines 369-372).
- Serial hand-out was the slowness: a three-to-four-hour run produced only a login page because the skill "hands out one task, waits for it to complete, and only then hands out the next one" (lines 331-343); parallel hand-out fixed it. A router sends "the simple mechanical work" to "a cheaper model" (lines 386-387).

What the factory takes from the two: the fixed grader prompts the planner cannot write (already `LOOP.md`, Grader change protocol), the owned-files rule and the integrator that reruns every check (F12), and the answer key as the done-checks block (already `CONTRACT.md`).
