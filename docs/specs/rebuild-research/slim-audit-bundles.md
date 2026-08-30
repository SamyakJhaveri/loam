# Slim audit - marketplace bundles (meta-improvement, helpers, business-process)

> Audited 2026-08-29 against the condensed ledger criteria in
> `docs/specs/rebuild-research/research-context-rules.md` (Part 6).
> Criteria are applied in order; the first one that fires decides the verdict.
> All three bundles are install-on-demand marketplace bundles, so they carry zero context cost
> until a user enables them - the bar is lower than for always-on assets.
> Criteria 1, 3 and 5 (natively superseded, duplicate-of-another-home, wraps an existing capability)
> still kill regardless of loading tier, because an installed duplicate competes with its own original.

## Verdict summary

| Bundle | Skills | KEEP | REMOVE |
|--------|--------|------|--------|
| meta-improvement | 1 | 0 | 1 |
| helpers | 7 | 1 | 6 |
| business-process | 4 | 0 | 4 |

**Two bundles end with zero survivors: `meta-improvement` and `business-process`.**
Both should be deleted whole, including their `.claude-plugin/` directories and any marketplace
entry that lists them.
`helpers` survives with exactly one skill (`surprise-me`); a one-skill bundle is not worth a
plugin manifest, so `surprise-me` should be rehomed rather than shipped as a bundle of its own.

## meta-improvement

| Skill | Verdict | Reason |
|-------|---------|--------|
| self-healing | REMOVE | Criterion 3 - it duplicates directives that already live in other layers: memory consolidation is `sam-cc-setup:dream`, pattern/gotcha capture is `sam-cc-setup:reflect`, and skill authoring is the `skill-creator` plugin plus the `writing-for-agents` skill. Its own rules also conflict with those homes (it asserts a 300-line SKILL.md ceiling against the documented 500-line tip, and tells the author to write descriptions "for auto-activation", a mechanism that does not exist). |

Zero survivors. Delete `cultivation/marketplace/meta-improvement/` entirely.

## helpers

| Skill | Verdict | Reason |
|-------|---------|--------|
| align-prompt | REMOVE | Criterion 3 - straight duplicate of `sam-cc-setup:align-prompt`, which is the current, already-rewritten home (targets Claude Fable 5 and Opus 4.8). This copy is the stale generation: it targets Opus 4.6/4.8 and hard-refuses 4.7 by name. Two installed skills answering to "align prompt" is exactly the conflict criterion 3 kills. |
| decision-matrix | REMOVE | Criterion 1 - building a weighted criteria-by-option scoring table with a recommendation is stock model behaviour; the file is generic prompting with no repo-specific or hard-won content. Secondarily criterion 3: the software-choice case is already owned by `sam-cc-setup:tech-selection`. |
| grill-research | REMOVE | Criterion 4 - it hard-codes another project's surroundings rather than reading them: `{{PROJECT_ROOT}}`, `results/evaluation/`, `results/augmentation/`, `specs/`, `overall_status` vs `run_status`, KNOWN_FAIL exclusions, and two commands that do not exist (`/overnight-eval`, `/researcher`). The generic residue after that rewrite - adversarial interrogation and "trace every number to disk" - is already covered by the shipped `grilling` skill and the `/rigor` skill, so DELETE rather than REWRITE. |
| model-route | REMOVE | Criterion 3 - it conflicts with a settled ruling in another layer. The whole skill routes work across an Opus/Sonnet/Haiku tier matrix, while the recorded model policy is Opus everywhere with effort as the dial, and Haiku is ruled out for any task. An advisor whose core output contradicts the standing policy is worse than none. |
| navigate | REMOVE | Criterion 1 - selecting the right skill/agent from the available descriptions is what the model does natively on every turn; the skill re-implements the harness's own dispatch as a prompt. Criterion 5 applies equally (it wraps functionality the agent already invokes). It also recommends `/model-route`, which this audit removes. |
| prompt-improver | REMOVE | Criterion 1 - asking a small number of grounded clarifying questions on a vague request is native behaviour, and the harness already ships `AskUserQuestion` for it. Compounding defect: the skill declares itself invokable only by `.claude/hooks/improve-prompt.py`, and no such hook exists in the seed, so as shipped it is inert. |
| surprise-me | KEEP | Criterion 14 - survives every prior criterion. It is not native behaviour (unprompted, ranked, goal-scored ideation with a mandatory executed proof in the same turn), it is not a duplicate (`adhd` is planning-only divergent ideation, `brainstorming` is pre-implementation requirements elicitation, neither produces an executed proof), and it hard-codes no environment. Its anti-tuning rules and "every claimed fact traces to a command run this session" clause are the outcome it protects: creative suggestions that a reader can verify rather than must trust. |

## business-process

All four skills target organizational process work rather than code, and all four are generic
consulting prompts with no repo-derived or hard-won content.

| Skill | Verdict | Reason |
|-------|---------|--------|
| process-optimizer | REMOVE | Criterion 1 - "look at these steps and find redundant, mis-ordered, serialisable, and error-prone ones" is stock reasoning the model performs without an asset. It also depends on `workflow-mapper` output, which this audit removes. |
| sop-writer | REMOVE | Criterion 1 - drafting a numbered procedure with prerequisites, decision points and a troubleshooting table is native. This is the closest call in the bundle, because the fixed 7-section document skeleton is the one part not derivable on demand; it is not enough on its own to clear criterion 1, and if the skeleton is wanted later it belongs in a docs template, not a skill. |
| weekly-review | REMOVE | Criterion 1 - personal-productivity coaching (recall the week, score it, pick three priorities) needs no asset. Criterion 9 also fires: nobody can name an engineering outcome it demonstrably improved, and it is unrelated to what this template ships. |
| workflow-mapper | REMOVE | Criterion 1 - extracting trigger/steps/decisions/handoffs from a description is native. Its GREEN/YELLOW/RED classification adds a label vocabulary, not a capability, and the mandated "hours saved per week / equivalent salary value" output invites fabricated numbers, which contradicts the evidence discipline the rest of the harness enforces. |

Zero survivors. Delete `cultivation/marketplace/business-process/` entirely.

## Mechanical defects found

Checked: does each bundle have a `.claude-plugin/plugin.json` that parses, and do the SKILL.md
frontmatters carry real fields.

1. All three `plugin.json` files exist and parse as valid JSON
   (`meta-improvement`, `helpers`, `business-process`, each `version: 0.1.0`, MIT, same author block).
   No structural defect in any manifest.
2. **Fake `auto-activate: false` field in 9 of the 12 SKILL.md files.**
   That field does not exist in Claude Code; the skills stayed fully model-invocable the whole time.
   Affected: `self-healing`, `align-prompt`, `decision-matrix`, `grill-research`, `prompt-improver`,
   `process-optimizer`, `sop-writer`, `weekly-review`, `workflow-mapper`.
   The real field is `disable-model-invocation: true`, and **no skill in any of the three bundles uses it.**
   Three files carry no such field at all and are clean on this point: `model-route`, `navigate`, `surprise-me`.
3. **Fake `user-invocable: false` field** in `helpers/skills/prompt-improver/SKILL.md`.
   Also not a real frontmatter field. The intended behaviour (hook-only, never user-invoked) has no
   frontmatter expression; the nearest real control is `disable-model-invocation`, which does the opposite.
4. **`helpers` manifest description is out of date.** It enumerates six skills
   (decision-matrix, navigate, model-route, prompt-improver, grill-research, align-prompt)
   while the bundle ships seven - `surprise-me` is missing from the description.
   Moot if the bundle is dissolved down to `surprise-me`, but it is a live inconsistency today.
5. **`grill-research` ships unrendered placeholders and dead references.**
   `{{PROJECT_ROOT}}` appears as a literal (nothing under `cultivation/` is Jinja-rendered),
   and it points at `/overnight-eval`, `/researcher`, and `.claude/rules/known-issues.md`
   (the seed file is now `reassess-rewrite-known-issues.md`).
6. **`prompt-improver` has a missing dependency.** It names `.claude/hooks/improve-prompt.py`
   as its sole trigger; that hook is not present in the seed, so the skill cannot fire as documented.
7. No file trips criterion 11 (size). The largest is `grill-research` at 173 lines,
   well under the ~500-line SKILL.md guideline.
