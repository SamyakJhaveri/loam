# Prompt audit - 2026-09-06

Run of `/claude-api prompt-audit` (anthropics/skills at 41bbe19, 2026-09-03) over the Loam prompt surface.
Target model: Claude Fable 5.1, with Claude Opus 4.8 as the worker model.
Scope: the whole repository prompt surface, since the request named no file.
Grounding for every "why obsolete": `shared/prompt-audit.md` pattern rows and `shared/model-migration.md`, section "Migrating to Claude Fable 5.1".

## Assumptions

- Target model is Fable 5.1 because the seed ships a Fable 5.1 brief hook and a `fable-prompting` skill.
- Prompts to the Codex CLI (two `<=60 lines` caps in the codex skills) are out of scope for a Claude-targeted audit.
- Skill frontmatter `description` fields are trigger text and were not flagged for urgency.

## Inventory

| Partition | Files read | Judged clean |
|---|---|---|
| Seed harness (root and rendered prose, 15 hook emitters, 2 libraries, Codex policy, 2 skills) | 26 | 22 |
| sam-cc-setup skills A to H plus the six agents | 25 | 12 |
| sam-cc-setup skills P to Z, plugin hooks, README, marketplace.json, impeccable | 28 | 18 |

Group 4 check: no hook or library calls a model for a deterministic job. Zero model-call sites.

## Summary

Findings: 16 High, 27 Medium, 12 Low. 41 carry a hunk in the proposed patch. Low items are flag-only.

Three highest-impact findings:

1. **The shipped harness contradicts itself.** The post-compaction hook re-injects the autonomy and batching nudges into every rendered project, one day before the `fable-prompting` skill and the Fable brief hook told sessions never to paste those exact blocks. Four of its five reminders are duplicates (F01 to F04).
2. **The agent-team prompts run on a small-context budget.** A 30K raw-content ceiling, a 200-line read cap, a 500-token message cap and a 300-token reply cap sit in prompts pointed at a 1M-context model documented as strongest on long context-gathering runs (F12 to F15, F28).
3. **The brainstorming skill shouts its gate three times.** HARD-GATE tags, "You MUST", and "The ONLY skill" state one rule at lines 13, 66 and 136. One plain sentence is the fix (F16, F17, F31, F32).

Two Medium items are reported without a hunk because they are structural: removing the length-advisory hook (F07) touches six files and is already in the Lean v3 design, and merging build-validator with test-synthesizer (F38) rewrites two agent files.

## Findings

| ID | Location | Evidence | Pattern | Why obsolete | Confidence | Action | Replacement | In patch |
|---|---|---|---|---|---|---|---|---|
| F01 | `seed/.claude/hooks/post-compact-reinject.sh:15` | 1. Finish the whole task; do not stop early or ask permission for work already requested. | 1d re-insertion, 1a pressure | Restates the autonomy block Claude Code injects. The repo's own fable-prompting skill names that block as never-paste. A second copy is paid tokens for no behavior change. | High | remove |  | yes |
| F02 | `seed/.claude/hooks/post-compact-reinject.sh:15` | 4. Batch independent tool calls. | 1d re-insertion | Claude Code injects the batching nudge per request. The fable-prompting skill lists it as never-paste. | High | remove |  | yes |
| F12 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:43` | **Context ceiling:** stay under 30K tokens of raw file content. | 1b arithmetic rubric, 1d fossil | Fable 5.1 has a 1M-token window and is documented as strongest on context-gathering long runs. The clamp starves that work, and the model cannot measure the figure. | High | rewrite | **Context discipline:** read what the task needs and summarize findings as you go, so your working state survives a long run. | yes |
| F13 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:132` | Keep messages under 500 tokens. The advisor's context is a shared resource. | 1f numeric output ceiling | A stated operational reason does not convert a numeric clamp into a keeper. Re-express as audience framing. | High | rewrite | Send the advisor what it needs to answer and nothing else. Its context is a shared resource. | yes |
| F14 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/advisor-prompt.md:37` | Keep responses under 300 tokens; your context is a shared resource. | 1f numeric output ceiling | 300 tokens truncates a real architectural answer on the agent whose job is giving one. | High | rewrite | Answer at the length the question needs; your context is a shared resource, so do not pad. | yes |
| F15 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:24` | - No shortcuts. Read files before editing them and understand code before changing it. | 1a pressure language | The documented 'Be thorough. Do not be lazy.' row. Fable 5.1 reads before editing unprompted, and the harness refuses edits to unread files. | High | remove |  | yes |
| F16 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:12-14` | <HARD-GATE> Do NOT invoke any implementation skill... This applies to EVERY project</HARD-GATE> | 1a pressure language | Fable 5.1 follows a brief instruction as reliably as a shouted one. The XML wrapper and caps set an anxious register that produces hedging. The gate is real; state it plainly. | High | rewrite | Present a design and get the user's approval before writing code, scaffolding a project, or invoking an implementation skill. This holds for small projects too - the design can be two sentences. | yes |
| F17 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:22` | You MUST create a task for each of these items and complete them in order: | 1a pressure language | An emphasis marker on an instruction the model would follow anyway. Boosters now over-apply and make the checklist rigid. | High | rewrite | Create a task for each item and work them in order: | yes |
| F18 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:89` | up to 200-300 words if nuanced | 1f numeric output ceiling | Word caps tuned against an older model's verbosity starve reasoning. Replace the number with the outcome. | High | rewrite | Scale each section to its complexity: a sentence or two when it is straightforward, longer when the design decision is genuinely nuanced. | yes |
| F19 | `cultivation/marketplace/sam-cc-setup/skills/hypothesis-tree/SKILL.md:39-47` | ## Anti-rationalization table \| "I'll add the evidence later" \| ... | 1c prohibition list | Five rows arguing against excuses the model was not going to make. A prohibition against an unmade failure can anchor toward it. Every row is already enforced by the Phase 2a and 2b file checks. | High | remove |  | yes |
| F20 | `cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md:42-44` | a 2026-08-02 audit cut twelve anti-patterns to three, and all three survivors were incidents local to the source repo | 2 history narrative | A rule's authority is the behavior it prescribes, not the incident behind it. The date and counts rot. | High | rewrite | **No anti-pattern list is written.** Anti-patterns are local to the repo that earned them. A new repo starts with zero and earns its own. | yes |
| F21 | `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md:16` | You are scored on the quality of what you let the author fix or delete, not on the number of findings. | 1c grader vocabulary | Describing the scoring apparatus pushes effort toward being watched. State the requirement. | High | rewrite | Report the findings the author can act on. (rest of the paragraph unchanged) | yes |
| F22 | `cultivation/marketplace/sam-cc-setup/skills/session-critique/teammates.md:1-150` | Loaded by /session-critique when spawning workers in Phase 2. | 1d unenforced, 2 dangling refs, 2 pinned models | Nothing references this file. The phases and buckets it cites were removed from SKILL.md on 2026-09-05, and its three '(Opus)' pins contradict SKILL.md line 27, which says not to copy a model ID from prose. | High | remove | delete the file | yes |
| F23 | `cultivation/marketplace/sam-cc-setup/README.md:119` | The repository contract tests require both sam-cc-setup fields to be 0.5.0. | 2 volatile specific | Both manifests carry 0.7.0 and the routes test asserts 0.7.0. | High | rewrite | ...require both sam-cc-setup version fields to match each other and the value asserted in bin/tests/test_marketplace_skill_routes.py. | yes |
| F24 | `cultivation/marketplace/sam-cc-setup/skills/reflect/SKILL.md:163-164` | It should NOT launch subagents or perform deep exploration. | 1d update suppressor (delegation) | The migration guide calls delegation suppression a common prior-model guardrail and says to use sub-agents freely on Fable 5.1. The real requirement is that the reflection draw on session context. | High | rewrite | Generate the reflection from what is already in this session's context and git state. Fresh exploration would describe the repository, not the session. | yes |
| F25 | `cultivation/marketplace/sam-cc-setup/skills/reflect/SKILL.md:166` | Total output to main conversation: the reflection file path + the 6-line summary above. | 1f numeric output ceiling | Fable 5.1 under-narrates, so a six-line clamp strips wanted output. | High | rewrite | Keep the conversation output to the file path and a short summary. | yes |
| F03 | `seed/.claude/hooks/post-compact-reinject.sh:15` | 2. Keep changes to what the task asks... 3. Surgically edit files. | 1c repetition as reinforcement | Both rules already live in the rendered AGENTS.md Editing discipline, which is in the system prompt and survives compaction. Duplicates make the model reconcile wordings. | Medium | remove |  | yes |
| F04 | `seed/.claude/hooks/post-compact-reinject.sh:15` | 5. Re-read HANDOFF.md if present and run the verify command it names before claiming anything. | 1d re-insertion (keeper) | The one item the model cannot recover after compaction, since HANDOFF.md is local and gitignored. Keep the hook, reduce it to this line. F01 to F04 are one physical line, so they form one hunk plus its two test assertions. | Medium | rewrite | After compaction: re-read HANDOFF.md if it exists and run the verify command it names before claiming any result. | yes |
| F05 | `seed/.claude/hooks/fable-session-brief.sh:39-41` | On a rough request, restate goal, constraints, and done check in three lines before acting | 1c step choreography for a judgment task | Claude Code injects 'When you have enough information to act, act', the migration guide's own anti-overplanning nudge. A mandated preamble on every rough request pushes the other way. The guide says de-prescribe migrated prompts. | Medium | rewrite | Fable session. Ask one question before acting only if a reading of the request would change the architecture; otherwise act. | yes |
| F06 | `seed/.claude/hooks/fable-session-brief.sh:39` | Fable 5.1 session. | 2 pinned model name | The hook fires for any model name containing 'fable' but asserts 5.1. On the next Fable release it misnames the session. Folded into the F05 hunk. | Medium | rewrite | Fable session. | yes |
| F07 | `seed/.claude/hooks/bash-length-advisory.sh:36` | Long command (%d chars). Split it into steps so each result is readable. | 1f numeric clamp, 1d per-call re-insertion | A character count stands in for a readability judgment and fires on every Bash call. It fired eight times in this audit session, every time on a readable command, and works against the batching nudge Claude Code injects. Not in the patch: removal touches settings.json, CLAUDE.md.jinja, agent-parity.toml, the harness contract, and two test files, and the Lean v3 design already deletes this hook. Fold it into Lean v3. | Medium | remove | Delete the hook and its wiring. If a nudge is still wanted, trigger on the count of chained commands, not length. | no |
| F26 | `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md:71` | **Bounded.** Report at most 10 findings, ranked by severity then payoff. | 1f numeric ceiling | A hard cap drops real findings past ten defects, and contradicts code-architect.md line 14 in the same roster ('never drop one to fit a length target'). | Medium | rewrite | **Bounded.** Rank findings by severity then payoff and lead with the ones that change the plan. Everything you noticed but did not report goes in the coverage ledger. | yes |
| F27 | `cultivation/marketplace/sam-cc-setup/agents/code-architect.md:14` | Keep each finding to 1-3 lines. | 1f numeric ceiling | Sits one clause after 'never drop one to fit a length target', so the file both forbids and imposes a length target. | Medium | rewrite | Keep each finding tight enough to act on without re-reading the file. | yes |
| F28 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:37,40` | Never read more than 200 lines without a reason. / bulk reads (more than 5 files, or more than 500 total lines) must be delegated | 1b arithmetic rubric | Three counted thresholds computed before every read, written for a small-context generation. The guide says let Fable 5.1 decide when to delegate rather than script it. | Medium | rewrite | Read with offset and limit when you only need part of a file. / Delegate bulk reading to a mechanical Explore subagent and keep only its summary. | yes |
| F29 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:59` | - You estimate you are at roughly 80% of your context capacity. | 1d unenforceable, Group 4 budget countdown | The model cannot observe its remaining context, so this trigger never fires reliably. Surfacing a remaining-context figure is documented to cause premature wrap-up on Fable 5.1. The next two triggers are observable and sufficient. | Medium | remove |  | yes |
| F30 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:9, advisor-prompt.md:9` | ## MANDATORY DIRECTIVES | 1a pressure language | When the whole block is marked mandatory the marker carries no information, and the register bleeds into output. | Medium | rewrite | ## Operating directives | yes |
| F31 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:16-18` | ## Anti-Pattern: "This Is Too Simple To Need A Design" ... you MUST present it and get approval. | 1c repetition | Restates the gate two lines after the gate states it, and F16's replacement already carries the small-project point. | Medium | remove |  | yes |
| F32 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:66` | Do NOT invoke frontend-design, mcp-builder, or any other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans. | 2 volatile specifics, 1c repetition | Third statement of the rule (lines 13, 66, 136), naming two skills not in this plugin. | Medium | rewrite | **The terminal state is invoking writing-plans.** | yes |
| F33 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:138-145` | ## Key Principles - One question at a time... - Explore alternatives - Always propose 2-3 approaches | 1c scattered duplication | Six bullets, five restating rules already in 'The Process'. Beyond one deliberate recap this is scattered duplication. | Medium | remove |  | yes |
| F34 | `cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md:99` | you reason better about code you can hold in context at once, and your edits are more reliable when files are focused | 1a trait claim | A 'you tend to' claim addressed to the model. State the design principle without the self-diagnosis. | Medium | rewrite | Smaller, well-bounded units are also easier to change safely: a focused file makes the blast radius of an edit obvious. | yes |
| F35 | `cultivation/marketplace/sam-cc-setup/skills/hypothesis-tree/SKILL.md:49-57` | ## Red flags - stop and restart ... If any red flag triggers: STOP. | 1c prohibition list, duplicate | Five prohibitions restating the Phase 2a, 2b, 2c gates, which already enforce each one with a file check. | Medium | remove |  | yes |
| F36 | `cultivation/marketplace/sam-cc-setup/skills/hypothesis-tree/SKILL.md:23-27` | ## Iron law / NO HYPOTHESIS WITHOUT FALSIFIABLE CRITERIA AND A NEXT EXPERIMENT | 1a pressure language | An all-caps banner for a rule Phase 2a already enforces. Emphasis is a scoped fix, not a first-draft register. | Medium | rewrite | ## The rule / A hypothesis needs a falsifiable criterion and a named next experiment. Without both, do not add the node. | yes |
| F37 | `cultivation/marketplace/sam-cc-setup/skills/agent-team/brief-report-template.md:7` | Keep each artifact below 4 KiB. | 1f numeric ceiling | A byte cap on a written deliverable. The next two sentences already say what to leave out, which is the enforceable part. | Medium | rewrite | Keep each artifact short enough to read in one pass. | yes |
| F38 | `cultivation/marketplace/sam-cc-setup/agents/build-validator.md + test-synthesizer.md` | Same tools; build-validator forbids 'standalone test collection, import smoke, full pytest', which are test-synthesizer's Strategies 1-3. | Group 4 redundant specialist sub-agents | Two agents with identical tools both run commands over changed files and emit PASS/FAIL/SKIP. build-validator's scope rule exists only to stop it duplicating test-synthesizer. Not in the patch: a two-file structural rewrite you should decide on first. Proposed edit: keep build-validator with a mode input, configured-gate (current) and synthesized (test-synthesizer's four strategies), delete test-synthesizer.md, keep the tmp-dir plus trap cleanup script verbatim. | Medium | rewrite | Merge into one agent with a mode input. | no |
| F39 | `cultivation/marketplace/sam-cc-setup/skills/align-prompt/SKILL.md:192-193` | This skill is manual today. Wiring it into a workflow or a hook... is a pending task. | 2 history narrative / backlog note | Prescribes nothing for the reading session and costs tokens on every trigger. Belongs in an issue. | Medium | remove |  | yes |
| F40 | `cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md:15` | **Announce at start:** "I'm using the writing-plans skill to create the implementation plan." | 1c output choreography | A mandated verbatim announcement inherited from the superpowers original. It front-loads process narration instead of the outcome. | Medium | remove |  | yes |
| F41 | `cultivation/marketplace/sam-cc-setup/skills/tech-selection/SKILL.md:27` | bounded: at most 4 candidates, at most 5 assumptions to test, one recommendation | 1f numeric ceilings | Numeric ceilings on a judgment deliverable. Step 2 already says 2-4. | Medium | rewrite | The deliverable is bounded: compare only the candidates genuinely in play, test only the assumptions that would change the answer, and end with one recommendation. | yes |
| F42 | `cultivation/marketplace/sam-cc-setup/skills/surprise-me/SKILL.md:34,67` | Three to six ideas; kill the rest. / Scale is 3-6 ideas | 1f numeric ceiling, 1c repetition | The same clamp twice in a 71-line file. | Medium | rewrite | Present the survivors; cut anything that does not beat the ideas above it. / 6. One executed proof is mandatory. | yes |
| F43 | `cultivation/marketplace/sam-cc-setup/skills/surprise-me/SKILL.md:56` | ## Critical rules | 1a pressure language | A section labeled critical stops carrying information. | Medium | rewrite | ## Rules | yes |
| F44 | `cultivation/marketplace/sam-cc-setup/skills/sam_handoff/SKILL.md:3` | Renamed from handoff on 2026-08-02 to avoid a name clash... | 2 archaeology in trigger text | Rides in every request and does not help the model decide whether to fire. The disambiguation is the useful part. | Medium | rewrite | Not the mattpocock-skills handoff, which compacts the conversation into the OS temp dir instead. | yes |
| F45 | `cultivation/marketplace/.claude-plugin/marketplace.json:21` | UI polish workflow (vendored bundle; kept per 2026-08 rebuild ledger ruling) | 2 provenance in routing text | A description is routing text. The ruling belongs in UPGRADING.md. | Medium | rewrite | UI polish workflow: deterministic anti-pattern rules plus an LLM critique. Vendored from pbakaus/impeccable, Apache-2.0. | yes |
| F46 | `cultivation/marketplace/.claude-plugin/marketplace.json:104` | SkillSpector-vetted 2026-08-10... 16 flagged + 3 name-collided skills withheld | 2 volatile specifics | The counts and date drift as the pinned SHA moves and carry no verification path. | Medium | rewrite | Deer Flow public skills from bytedance/deer-flow, SHA-pinned via git-subdir. Only the vetted, collision-free skills are enabled. Installs DISABLED (defaultEnabled:false) - enable to trial. | yes |
| F47 | `cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md:100` | so no more hand-pasted summaries. | 1d migration-relative phrasing | A diff against a prior practice the model never saw. | Medium | rewrite | Every shipped work-stream leaves a machine-findable record. | yes |
| F08 | `seed/.claude/hooks/fable-session-brief.sh:43-45` | Do not paste the autonomy block... Claude Code already injects all four. | 2 volatile claim, no verification date | True today and the useful half of the brief, but it is a factual claim about another product's system prompt that nothing re-checks. | Low | flag |  | no |
| F09 | `seed/.claude/hooks/write-rewrite-guard.sh:52-53` | Prefer Edit; use Write only if most of the file is changing. | 1d re-insertion | Third statement of a rule the Write tool description and AGENTS.md already carry. The file-specific line count is real information, so this reads as working redundancy. | Low | flag |  | no |
| F10 | `AGENTS.md:15-17` | - Challenge assumptions and correct false premises. - Point out flaws... | 1c bullets for behavior, no reason | Idiom-dating only. The quality bar is legitimate author context the keep list protects. | Low | flag |  | no |
| F11 | `seed/.agents/lib/stop_verify.py:251, AGENTS.md:1, CLAUDE.md:1` | Turn-end verification gate FAILED — fix these | outside audit scope | Em dash in user-visible strings against the repo's own writing convention. Not a prompting pattern. | Low | flag |  | no |
| F48 | `cultivation/marketplace/sam-cc-setup/agents/*.md:5` | model: claude-opus-4-8[1m] | 2 pinned model names | Degrades silently after the next release. Against flagging: functional frontmatter that encodes your standing Opus-everywhere policy. | Low | flag |  | no |
| F49 | `cultivation/marketplace/sam-cc-setup/agents/build-validator.md:11-13` | Use the session's default model because this role is mechanical. | 2 (worker proposed rewrite; downgraded) | Omitting the model field is itself the enforceable mechanism, and the prose states the reason for the omission. Context, not cruft. | Low | flag |  | no |
| F50 | `cultivation/marketplace/sam-cc-setup/agents/consistency-checker.md:147-148,169-171` | This check exists because multiple documents once each called themselves controlling | 2 history narrative | Past-tense incident text, but it states the reason for a non-obvious scope decision, which the keep list protects. | Low | flag |  | no |
| F51 | `cultivation/marketplace/sam-cc-setup/skills/scaffold-context/SKILL.md:16,49,75,82` | 25-80 lines (four restatements) | 1c repetition (downgraded) | Each restatement sits in a different role (skip rule, target, numbered rule, anti-pattern) and they agree. Working redundancy under keep list item 8. | Low | flag |  | no |
| F52 | `cultivation/marketplace/sam-cc-setup/skills/techdebt/SKILL.md:4` | model: claude-opus-4-8[1m] | 2 pinned model name | Same as F48; functional config. | Low | flag |  | no |
| F53 | `cultivation/marketplace/sam-cc-setup/skills/reflect/SKILL.md:63` | Write a structured reflection with exactly these four sections | 1c (idiom only) | A real format contract for a filed artifact. No documented harm. | Low | flag |  | no |
| F54 | `cultivation/marketplace/sam-cc-setup/skills/unknowns/SKILL.md:55-56` | The phrasing is load-bearing; paraphrase and you lose the behaviour. | 2 volatile specific | Sourced from a July 2026 field guide with no verification against Fable 5.1. Idiom-dating only. | Low | flag |  | no |
| F55 | `cultivation/marketplace/.claude-plugin/marketplace.json:3,31,50,70,87` | Install on demand — not shipped... | outside audit scope | Em dashes against the repo's plain-dash convention. Not a prompting pattern. | Low | flag |  | no |

## Provenance

Every emphatic line dates from 2026-08-02 or later, so none was written for a retired model. They are first-draft register and small-context habits carried forward. The pattern matches still hold: the Fable 5.1 guide's de-prescription item says prompts written for prior models are too prescriptive for it and reduce output quality.

| ID | Commit and date |
|---|---|
| F01 | 5aee49a 2026-09-03; superseded by c38a02b and 7963147 on 2026-09-04 |
| F02 | 5aee49a 2026-09-03 |
| F12 | 992f0d60 2026-08-31 |
| F13 | 992f0d60 2026-08-31 |
| F14 | 992f0d60 2026-08-31 |
| F15 | 992f0d60 2026-08-31 |
| F16 | 368e4efe 2026-08-15 |
| F17 | 368e4efe 2026-08-15 |
| F18 | 368e4efe 2026-08-15 |
| F19 | 992f0d60 2026-08-31 |
| F20 | 2a3c7e8f 2026-08-02 |
| F22 | 8409d34e 2026-08-31; orphaned by cefcfdf 2026-09-05 |
| F23 | 676fafcc 2026-08-31 |
| F24 | 2a3c7e8f 2026-08-02 |
| F25 | 2a3c7e8f 2026-08-02 |
| F03 | 5aee49a 2026-09-03 |
| F04 | 5aee49a 2026-09-03 |
| F05 | 7963147 2026-09-04 |
| F06 | 7963147 2026-09-04 |
| F07 | 5aee49a 2026-09-03 |
| F27 | a9450f82 2026-09-03 |
| F28 | 992f0d60 2026-08-31; eaf1acad 2026-09-03 |
| F29 | 992f0d60 2026-08-31 |
| F30 | 992f0d60 2026-08-31 |
| F31 | 368e4efe 2026-08-15 |
| F32 | 368e4efe 2026-08-15 |
| F33 | 368e4efe 2026-08-15 |
| F34 | 368e4efe 2026-08-15 |
| F35 | 992f0d60 2026-08-31 |
| F36 | 992f0d60 2026-08-31 |
| F37 | cefcfdfa 2026-09-05 |
| F38 | cefcfdfa 2026-09-05 |
| F39 | 74b1d149 2026-08-29 |
| F40 | 2250e8cd 2026-08-31 |
| F41 | 8fd39fe4 2026-08-29 |
| F42 | 5d29cd7b 2026-08-25 |
| F43 | 5d29cd7b 2026-08-25 |
| F44 | 2a3c7e8f 2026-08-02 |
| F45 | c93485f6 2026-08-29 |
| F46 | d6a30513 2026-08-10 |
| F47 | 201167e2 2026-08-31 |
| F08 | 7963147 2026-09-04 |
| F09 | 5aee49a 2026-09-03 |
| F48 | a9450f82 2026-09-03 |
| F49 | cefcfdfa 2026-09-05 |
| F51 | 464f5992 2026-08-25 |
| F52 | a9450f82 2026-09-03 |

## Proposed diff

`docs/findings/prompt-audit-2026-09-06.patch`: 36 hunks over 20 files. It includes the two test assertions that the F04 and F05 hunks change.
The F22 hunk empties `teammates.md` rather than deleting it (a plain `diff -N` limitation); remove the file with `git rm` after applying.
Verified: `git apply --check` passes on `main` at 815bb7f, and in a throwaway worktree with the patch applied the affected hook tests and the marketplace routes tests pass (8 and 8).

```bash
git apply docs/findings/prompt-audit-2026-09-06.patch                     # everything
git apply --include='seed/*' --include='bin/*' docs/findings/prompt-audit-2026-09-06.patch   # seed only
```

To decline single hunks inside a file, use `git apply --reject` or edit the patch. The review page groups hunks by finding so the decision list can be copied out.

## Not applied

Nothing in the repository was changed by this audit. The patch is a proposal.
Removal is a hypothesis: after applying, re-run the affected skills once and re-add in minimal form anything that regresses.

## Audit tooling note

The commit gate in `seed/.agents/lib/validation.py:559` blocks any Bash call containing a backtick or dollar sign alongside a version-control commit verb, without parsing the command. It false-positived twice while a worker wrote Markdown through a heredoc. Shell logic, not prompt text, so it is a separate fix.
