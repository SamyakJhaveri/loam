# The "Anthropic" loop-engineering guide and the levels video

Conclusion: the supervisor owns everything mechanical, and the models own only two things, writing the change and judging it with fresh eyes against evidence the supervisor gathered.
Every failure both sources describe comes from letting a model own something mechanical: the stop decision, the check execution, or the judge's own prompt.

## Sources

Source A is the PDF "Loop Engineering: The Anthropic Playbook for Designing Systems That Prompt Your Agents", 11 pages, at `/Users/samyakjhaveri/Desktop/Hardware, Software and AI Agent Harness Setup/Guides/loop engineering form anthropoic.pdf`.
It is not an Anthropic document: the p1 footer and p11 acknowledgment say it is a HuaShu reformatting of Addy Osmani's open "Orange Book" guide, citing Prithvi Rajasekaran (Anthropic) for the generator/evaluator findings and Steve Kaliski (Stripe) for the enterprise case, so nothing in it should be cited to Anthropic.

Source B is <https://www.youtube.com/watch?v=PLyRe6Zk--8>, "Every Level Of Claude Code Loop Engineering Explained", AI LABS, 23:04, read transcript-only via the `watch` skill with caption rollup stripped.
It is a different video from the one in `video-loop-engineering.md`.

Page numbers refer to Source A and timestamps to Source B.
My own reasoning is labelled **Inference**.

## Recommendations for the Lean v3 bash supervisor

The target is a bash supervisor running `claude -p` per round for one GitHub ticket, running the ticket's done checks as real commands, then a fresh-context judge, on a headless Ubuntu box.

### Adopt

1. **Keep the generator and the judge as separate `claude -p` invocations with no shared context.** Source A p4 gives the mechanism, the reason, and the failure mode if you merge them. Source B states it as a rule at [14:05]-[14:16]. This is the single most-supported claim across both sources.

2. **Give the judge an adversarial default stance, in a fixed file the worker cannot author.** Source A's p4/p5 agent file is directly reusable: assume broken until proven otherwise, do not praise, execute rather than read, paste real output, PASS only if every check holds, otherwise REJECT with each reason listed. Source B's adversarial reviewer [14:16]-[14:30] is the same instruction.

3. **Use a different model for the judge than for the worker.** Source A p4: swapping the underlying model "keeps its blind spots" if you do not. This directly supports the planned Opus 5 worker and Fable 5.1 judge split.

4. **Run the ticket's done checks as real commands and feed their exit codes and real output to the judge.** Source A p4 is emphatic that a reading judge answers "does this look right", not "does it run right", and its checklist item 2 is "run them, paste real output". Source B's blinking-mascot failure at [08:27] is the empirical case for not trusting a judge's own observation channel alone. Running the checks in the supervisor rather than inside the judge also removes the judge's ability to claim a check passed.

5. **Set three caps before the first unattended run: a per-round or per-run budget, a daily budget, and a maximum retry count.** Source A p8 names exactly these three and calls them circuit breakers rather than savings. Neither source supplies numeric values, so Lean v3 must pick its own. Source B ran three hours with no cap and did not notice.

6. **Write every round's outcome to a state file on disk, not to the transcript.** Source A p4 and p9. This is what makes a fresh-context judge possible at all, and what makes a killed run resumable on a headless box. The per-ticket JSONL run directory already in the repos-fit recommendation satisfies this.

7. **Keep exactly one human checkpoint and treat it as permanent.** Source A p8 and p11: the pause exists so the human stays able to intervene, not because they always will. Source B's checkpoint is the pull-request merge [14:48]-[15:21]. For Lean v3 the natural checkpoint is the same: the supervisor opens the pull request and never merges.

8. **Keep everything deterministic out of the model's hands.** Source A's Stripe case, p6: the orchestrator assembles context deterministically, the linter is hard-coded and unskippable, and the commit is a hard-coded step. For a bash supervisor this means the supervisor, not the agent, decides which ticket, runs the checks, counts rounds, enforces caps, and opens the pull request.

9. **Isolate each ticket in its own worktree or branch.** Source A p3 and p10 on the tangled loop, Source B [13:56]-[14:02]. Only matters once tickets run in parallel.

10. **Add parallelism last.** Source A p10: "the safe order of growth is to add parallelism last, after the checks are proven ... prove the evaluator catches real mistakes before trusting it to judge many agents at once." Source A p11 repeats it: "the loop that survives is the small one that earned trust, not the ambitious one that demanded it."

### Reject or diverge

11. **Do not make `/goal` the completion authority.** Both sources describe `/goal` as a small model reading the conversation and deciding whether the condition holds (Source A p5, Source B [05:49]-[06:00]). Lean v3's completion condition is the ticket's done checks run as real commands with real exit codes, which is strictly stronger than a model reading a transcript. Use `/goal`-style phrasing in the worker prompt if useful, but the supervisor's exit code, not `/goal`, decides done.

12. **Do not rely on the version numbers or feature descriptions in Source A.** The `/loop` after v2.1.72 and `/goal` after v2.1.139 claims (p9), the "small fast model" implementation detail (p5), and the Codex equivalences in Table V (p7) are a secondary synthesist's claims. Verify against `claude` before encoding.

13. **Do not adopt Source A's local-versus-cloud scheduling decision as written.** Table IV on p6 frames the choice as local `/loop` (needs the machine on, 1-minute interval, sees local files) versus cloud (machine off, 1-hour minimum). A headless Ubuntu box that stays on collapses this distinction: it has the local option's file access and interval with the cloud option's independence from a laptop lid. The document's own warning at p6 applies here, that "local rerun means run a few extra rounds while I am here" is a weaker capability than it sounds, but a permanently-on box is not a laptop.

14. **Do not treat discovery as required.** Source A's blind-loop anti-pattern (p5) says a loop whose work the human chooses is a failure. Lean v3's unit is one GitHub ticket a human picked. That is deliberate scope, and Source B's entire demonstration works the same way. Note it and move on.

## Against the two earlier research files

`video-loop-engineering.md`: agree.
Source A p8 fills the cost-cap gap that file records, and its static `.claude/agents/reviewer.md` confirms that file's fixed-judge-prompt recommendation.
Neither source mentions "ultra code", so it stays out of Lean v3.
On design law 2, Source A's Stripe case gives the stronger justification: move everything deterministic out of the judge entirely, which the done-checks-as-commands design already does.

`loop-repos-fit.md`: agree on the core recommendation, one conflict on `/goal`.
Source A p6 and p8 argue for exactly the shape that file proposes, deterministic gates plus the three caps it borrows.
That file marks loopx down for rejecting `/goal`; both sources treat `/goal` as the loop primitive, but loopx is right on the merits for this design, since a transcript-reading judge is weaker than an exit code (recommendation 11).
Neither source mentions hooks or `bypassPermissions`, so both are compatible with law 3 and that file's rejection of LongHorizon-Harness.
Do not cite Source A's Stripe figure of 1,300 pull requests a week as a target; Source A itself calls such numbers secondhand.

## Risks

Source A is a third-party synthesis with an "Anthropic Playbook" title it does not earn, so its authority is one practitioner's blog plus two second-hand cases, and I did not read Osmani's original Orange Book guide to check the reformatting is faithful.

I did not verify any Claude Code mechanical claim in either source against Claude Code itself, including the `/loop` v2.1.72 and `/goal` v2.1.139 version numbers, the "small fast model" stop-check implementation, the Codex equivalences in Table V, and the claim that remote-control Claude has broken skill support.

Source B is auto-generated captions with rollup duplication that I stripped programmatically, so quoted wording is reconstructed and a stripped overlap could have dropped a word.

Source B was read transcript-only with no frames, so every on-screen file, prompt, spec, `Q` table, and skill body was known only from narration.

Source B's run figures, 38 minutes for the landing page and roughly 3 hours for the two-feature batch, are the channel's own unaudited numbers for one project, and the video runs a paid-community pitch and a sponsor segment.

Neither source gives a numeric value for any cap, so Lean v3's budget, daily, and retry ceilings have no external anchor and must be chosen from local measurement.

I did not read the middle sections of `loop-repos-fit.md`, only its fit table, recommendation, and risks, so a per-repo detail there could contradict something above.
