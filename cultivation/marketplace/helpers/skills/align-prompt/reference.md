# align-prompt — Reference

The distilled prompting facts and the six-move rewrite spine that `SKILL.md` consumes on every invocation. Re-curate this file when a new Opus model drops; the three source URLs are listed at the bottom.

## § 1 — Opus 4.6 prompting facts (the execution target)

These characterize what 4.6 does that 4.8 does NOT, and what the rewrite must account for when target=4.6. Sourced from the Anthropic migration guide's §"Migrating to Claude Opus 4.7" section, read in reverse — every behavior 4.7 changed FROM is a 4.6 behavior.

- **Manual extended-thinking API is supported but caller-controlled.** `thinking: {type: "enabled", budget_tokens: N}` works on 4.6 (it returns 400 on 4.7+). Adaptive thinking is a 4.7+ feature that 4.6 does NOT have. Rewrite implication: the prompt body **cannot** elicit reasoning depth on 4.6 — thinking is set at the API layer by the caller. Move 5 (adaptive-thinking cues) is therefore skipped for target=4.6 not because "execution doesn't need it" but because 4.6 cannot act on it.
- **Sampling parameters supported.** `temperature`, `top_p`, `top_k` work on 4.6 (they return 400 on 4.7+). NEVER mention them in the rewrite body — they are caller-controlled.
- **Older tokenizer (less bloat).** 4.6's tokenizer emits roughly 0.74×–1.0× the tokens that 4.7+ does for the same input (the 0.74× lower bound is the reciprocal of the sourced ~35% / 1.35× figure, not a directly-quoted number; equivalently, 4.7+ emits ~1.0×–1.35× as many tokens as 4.6). This is the structural reason 4.6 is the execution target: lower token volume per turn, amortized over many execution turns. Per-token rate-card pricing is flat across the Opus tier — the savings come from emission count, not unit price.
- **Will silently generalize an instruction from one item to others.** Unlike 4.7+ (literal), 4.6 may infer requests not made and apply instructions to siblings of the named target. Rewrite implication: **explicit scope statements are MORE valuable on 4.6 than on 4.8** ("Apply to file X ONLY, do not touch siblings"; "Modify ONLY the regex at line N, do not generalize the fix"). State the exact items; do not rely on inference.
- **Fixed-ish verbosity baseline.** 4.6 does not calibrate response length to task complexity the way 4.7+ does. If the draft implies a short answer, state "Be concise." explicitly.
- **Warmer, more validation-forward tone with more emoji.** If the draft wants direct technical prose, state it (e.g., "Direct technical prose. No emoji.").
- **Loose effort calibration.** 4.6 tends to go above-and-beyond what was asked, especially at low/medium effort. For execution scoping, explicit Must-NOTs help bound drift — more valuable on 4.6 execution than they would have been on 4.7 execution.
- **More tool calls and more subagents spawned by default.** Useful for execution tasks; less need to explicitly say "use the X tool" or "spawn N subagents" unless you want to bound them.
- **High-resolution image support absent.** 4.6 max image resolution is 1568px on the long edge (vs 4.7+'s 2576px). Irrelevant to the rewrite unless the draft involves images.

## § 2 — Opus 4.8 prompting facts (the planning target)

These characterize what 4.8 does well that the rewrite should lean into when target=4.8. Sourced from `whats-new-claude-4-8` and the migration guide's §"Migrating from Claude Opus 4.7 to <NextOpus>" section.

- **Adaptive thinking decides per turn.** With `thinking: {type: "adaptive"}` enabled by the caller, 4.8 decides on each turn whether to think. Steerable via prompt-body cues: "Consider alternatives before answering.", "Weigh trade-offs between X and Y.", "Decompose into N parts." Do NOT mention `effort`, `thinking.budget_tokens`, or any API parameter in the rewrite body — those are caller-controlled. Adaptive thinking is OFF until the caller opts in; the rewrite assumes the caller has done so for planning sessions.
- **More literal instruction following.** 4.8 (inherits from 4.7) does not silently generalize from one item to others; does not infer un-asked requests. Rewrite implication: state scope explicitly ("Apply to every section, not just the first") rather than relying on inference. NB: 4.8 needs the same explicit-scope move as 4.6 but for the OPPOSITE reason — 4.6 over-generalizes; 4.8 under-generalizes. Both lead to the same fix (state scope explicitly).
- **Calibrated response length.** 4.8 picks length by judged complexity — shorter on simple lookups, longer on open-ended analysis. If you want a fixed shape, state it.
- **Effort default is `high`** across all surfaces (Claude API, Claude Code). For coding and high-autonomy work, set `xhigh` explicitly. API-level only; NEVER mention in the rewrite body.
- **Better long-context handling, fewer derailments after compaction.** Long planning prompts are safer on 4.8.
- **Better tool triggering.** Less likely to skip a required tool call (this was a 4.7 weakness; 4.8 fixes it).
- **Direct, opinionated prose; sparing on validation phrasing and emoji.** If you want a warmer voice, state it.
- **New tokenizer (more bloat).** 4.8 inherits 4.7's tokenizer — up to ~35% more tokens than 4.6 for the same input. The structural reason 4.8 is the planning target (not execution): planning sessions have lower turn volume; the per-turn cost is amortized over fewer turns. Execution loops run many turns; that's where 4.6's tokenizer wins.
- **Infra-level features (not promptable, skip in rewrites).** Mid-conversation system messages, refusal stop details, fast mode (`speed: "fast"`), 1024-token cache minimum, 1M context window default.

## § 3 — Universal Anthropic prompting principles (the rewrite checklist)

From the prompt-engineering best-practices doc, ordered by rewrite-time impact:

1. **Be clear and direct.** Specific about output format and constraints; sequential steps as numbered lists when order matters. *Golden rule:* if a colleague with minimal context would be confused, Claude will be too.
2. **Add context (the why).** Explaining *why* an instruction matters lets the model generalize correctly. ("Your response will be read aloud — never use ellipses" beats "Never use ellipses.")
3. **Use examples.** Few-shot beats zero-shot. Wrap examples in `<example>` tags inside `<examples>`. 3–5 examples optimal.
4. **Structure prompts with XML tags** when content is mixed (`<instructions>`, `<context>`, `<input>`).
5. **Give Claude a role** in the system prompt frame for domain-specific tasks. One sentence is enough.
6. **Tell what TO do, not what NOT to do.** Positive instructions beat negative ones for STYLE/FORMAT. *Tension with Loam:* `stage-contract.md` mandates Must-NOT lists for SCOPE-BOUNDING. Rule of thumb in this skill: positive framing for body/style; Must-NOT list only when (a) target=4.8 AND task is planning, or (b) the draft has explicit exclusion hints — see Move 3.
7. **Long-context layout:** longform data near the TOP, query at the BOTTOM. Up to ~30% quality lift on multi-doc inputs.
8. **Tool use:** be explicit ("Make these edits" beats "Can you suggest changes") — latest Opus models read intent literally; 4.6 reads intent more loosely but explicit phrasing still helps.

## § 4 — The Six Rewrite Moves (operational core)

The transformations every rewrite applies. These are deterministic; the only LLM creativity is in *how* each move's content is phrased for the user's specific draft.

1. **Lead with intent.** Convert leading "I want…" / "help me…" / "can you…" into a one-sentence statement of the task + the success criterion. The first line of the rewrite is what Done looks like.
2. **Name the role *if domain-specific*.** Prepend a one-sentence role frame ONLY when the task is in a specific domain (Copier templates, ML eval, HPC benchmarking, etc.). Skip for generic or single-shot tasks — unconditional role-prepending adds bloat.
3. **Surface scope (constraints + must-NOTs + explicit anti-generalization on 4.6).** Pull implicit constraints into a `## Constraints` section. Add a `## Must NOT include` list when:
   - target=4.8 AND task is planning/brainstorming (drift risk is highest in open-ended planning), OR
   - the draft explicitly hints at exclusions ("don't refactor X", "keep Y untouched").
   For target=4.6 specifically, **always** add an explicit anti-generalization scope statement in the body or Constraints section ("Apply to file X ONLY, do not touch siblings"; "Modify ONLY the regex at line N, do not generalize the fix to other validators") because 4.6 silently generalizes. Otherwise omit the Must-NOT list (Anthropic positive-instruction principle wins by default for style/format).
4. **Specify Done (artifact + verification).** State what the response should *be* (plan file path, code diff, code block, checklist, ADR) AND a verification step ("the new test passes", "the lint suite reports 0 errors", "the rewritten function reduces line count by ≥30%"). One section, two pieces.
5. **Add adaptive-thinking-eliciting language when target=4.8.** Phrase the prompt body to invite multi-step reasoning: "Consider alternatives before committing.", "Weigh the trade-offs between X and Y.", "Decompose the problem into N parts before answering." DO NOT mention `effort`, `thinking.budget_tokens`, or any API parameter — those are caller-controlled. **Skip this move entirely for target=4.6** — 4.6 does NOT have adaptive thinking; thinking depth is set at the API layer at call time, not in the prompt body. Eliciting it via prose is inert on 4.6.
6. **Compress + tone-anchor.** Strip filler, hedges, second-person scaffolding ("if you could please"). Match Claude's own direct prose style. The rewrite should be shorter and denser than the draft, not longer. For target=4.6 specifically, also add "Direct technical prose. No emoji." if the draft implies a technical voice — 4.6's default tone is warmer and includes more validation-forward phrasing and emoji than 4.8's baseline. For target=4.8, the model already defaults to direct prose; the tone-anchor is unnecessary.

## Source URLs

Re-curate this file from these three URLs when a new Opus model drops:

1. https://platform.claude.com/docs/en/about-claude/models/migration-guide — read both §"Migrating from Claude Opus 4.7 to <NextOpus>" (forward: what 4.8 adds over 4.7) and §"Migrating to Claude Opus 4.7" (reverse: what 4.6 does that 4.7+ doesn't). One page covers both targets.
2. https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8 — 4.8 feature summary.
3. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices — universal prompting principles, model-agnostic.

## Re-curation checklist (when a new Opus model drops)

Models rotate ~quarterly. A transition (the planning target ages into the execution slot; a newer model becomes the planning target) touches the sites below. After editing, grep the old model numbers to confirm nothing was missed.

- **reference.md** — § 1 (execution-target facts), § 2 (planning-target facts), Source URLs (migration-guide section names).
- **SKILL.md** — `description` + `argument-hint` (model tokens); Phase 1 dispatch tokens + Phase 1A question + Phase 1B refusal; Critical Rule 8 + Out-of-scope (the chucked model).
- **examples.md** — the three `target=` labels and the "Notes on the moves applied" table.

Sanity grep: `grep -rn '4\.6\|4\.7\|4\.8' <skill-dir>` — every remaining hit should be intentional after re-curation.
