# Blind review: merged plan-reviewer, plan-review skill, tech-selection skill

> Reviewed 2026-08-29 against `research-context-rules.md` (P13, P19-P22 especially) and the technique shortlists at the end of `refagents-voltagent.md`, `refagents-zglass.md`, `refagents-vercel.md`, `refagents-sweep.md`.
> The reviewer was given the artifacts and the settled constraints only, not the author's reasoning.

Artifacts:

- `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md` (84 lines)
- `cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md` (32 lines)
- `cultivation/marketplace/sam-cc-setup/skills/tech-selection/SKILL.md` (37 lines)

## Steel-man

The agent is a single blind unit that runs a fixed sequence: read and steel-man, enumerate the surface, ground every factual claim against the repo, a seven-point correctness checklist, then a mandatory elegance gate that forces two competing designs.
Its output contract caps findings at 10, requires each to trace to an enumerated surface item, caps severity at MEDIUM for uncited claims, and publishes a coverage ledger so the cap cannot silently swallow the eleventh finding.
The `plan-review` skill deliberately carries almost no content: its only job is to build a blind prompt and route the result, which is the correct division under P7 (guidance lives with the thing).
`tech-selection` is a separate, small decision helper that inherits the same bounding instincts (at most 4 candidates, at most 5 assumptions, one recommendation) and hands off to a measured bake-off rather than pretending to be one.
This is a genuinely tighter design than the pair it replaces, and the shape is right.

## Ruled-in technique coverage

| Technique (source) | Present | Where |
|---|---|---|
| Bounded findings + published coverage ledger (sweep #3) | Yes | Finding contract 5; Output 3 |
| Groundedness as a severity cap (sweep #1) | Yes | Finding contract 2 |
| Enumerate-the-surface-first (zglass #2) | Yes | Sequence 2, plus the traceability requirement in Finding contract 1 |
| Tool-bounded honesty (voltagent #1) | Yes | Honesty bounds, bullet 1 |
| Absence-needs-grep + two-source rule (voltagent #3) | Yes | Honesty bounds, bullets 3 and 4 |
| Precision-follows-provenance (vercel #3) | Yes | Honesty bounds, bullet 2 |
| License to approve (voltagent runner-up) | Yes, but see finding 1 | Line 16; Output 4 |
| Evaluator-provable completion condition (zglass #1) | Yes | Output 5, final bullet |

The zglass NEEDS MANUAL REVIEW escape hatch also survived, in Finding contract 4.
No ruled-in technique is missing outright.

## Findings

### 1. HIGH - nothing in the file distinguishes APPROVE from APPROVE_WITH_CHANGES, and the wording that exists forbids the latter

`plan-reviewer.md:16`: "If nothing blocks, you must say so and approve - manufacturing findings to justify the invocation is a failure."
`plan-reviewer.md:78`: "Verdict, exactly one of APPROVE / APPROVE_WITH_CHANGES / REJECT ... APPROVE is a legitimate outcome; use it when nothing blocks."

Read literally, both sentences make "no BLOCK-severity finding" sufficient for APPROVE.
A review that produces four HIGH findings with named fixes has nothing that blocks, so the stated rule points at APPROVE, which is plainly not the intent of a three-value verdict.
An executing model can read this two ways: APPROVE whenever there is no BLOCK, or APPROVE only when the findings list is empty.
The verdict is this agent's primary output and the thing the calling skill branches on, so the ambiguity is load-bearing.

Fix: state the mapping once, at the verdict, and delete the duplicated licence clause at line 16 (keep the anti-manufacturing sentence there, drop "and approve").
Something like: REJECT if any BLOCK finding stands; APPROVE_WITH_CHANGES if the findings are HIGH or MEDIUM and the revised plan absorbs them; APPROVE if the remaining findings are LOW or none.
CONFIRMED.

### 2. HIGH - the elegance gate mandates work products the Output contract has no slot for

`plan-reviewer.md:58-63` requires, in order: two written competing designs (A restricted to existing machinery, B unconstrained), an inversion pass per major component, a one-line reuse justification for every new file, script, config, or abstraction, and a closing statement of why the alternatives are worse if the artifact survives.

`plan-reviewer.md:73-84` lists exactly five output sections: steel-man, findings, coverage ledger, verdict, revised plan.
None of them is the design comparison.
The coverage ledger entry (`:77`) asks only for "each elegance pass: its status (clean / findings above / deferred)", which is a status word, not the designs.

So a strong model has two defensible readings: emit the designs in an unlisted section (which breaks the "in this order" output contract and can be longer than the findings themselves), or do the work silently and report only a status (which makes the mandatory gate unauditable, the exact failure P20 warns about - an assertion in place of evidence).
The same gap applies to the surface enumeration (Sequence 2) and the accurate/stale/wrong grounding classification (Sequence 3): both are mandated, neither has an output home, and the ledger's one-line-per-item shape does not obviously hold them.

Fix: either add a sixth output section ("Alternatives considered: Design A, Design B, verdict on each, in at most N sentences each") or state explicitly that Sequences 2, 3 and 5 are internal working notes whose only externalised trace is the coverage ledger, and widen the ledger's stated contents to include the surface list and the grounding table.
CONFIRMED.

### 3. MEDIUM - `maxTurns: 30` is tight against the mandated workload, and truncation destroys the two most valuable outputs

`plan-reviewer.md:7` sets `maxTurns: 30`.
Per `research-cc-docs.md:275`, exceeding `maxTurns` yields partial output marked as such.

The mandated sequence for a non-trivial plan is: read the artifact in full, enumerate the surface, then verify *each* factual claim by opening the file or running the command (Sequence 3), then checklist item 2 alone requires reading `.claude/rules/`, CLAUDE.md, AGENTS.md, linter and CI configs, then the elegance gate requires searching the repo *and the web* before writing Design A.
For a plan touching a dozen files that is well over 30 tool turns.
Because the verdict and the revised handoff plan are output items 4 and 5, a truncated run loses precisely the parts the caller needs, while the expensive grounding work is already paid for.
Note the calibration: the plugin's narrower agents sit at 15-20 turns (`build-validator.md`, `consistency-checker.md`, `read-only.md`), so the largest job in the set gets only 1.5x the budget of the smallest.

Fix: raise the ceiling (60 is a defensible number for an `effort: max` opus agent), and add one line to the output contract: if the turn budget is running short, stop grounding and emit the verdict plus the revised plan with the unfinished checks marked deferred in the ledger.
PLAUSIBLE - I did not measure an actual run; what would settle it is one timed invocation on a representative multi-file plan with the turn count recorded.

### 4. MEDIUM - "do not proceed on an empty set" is readable as "abort the whole review"

`plan-reviewer.md:24`: "If an input you need is missing or a glob matches nothing, stop and report that. Do not proceed on an empty set."

The first clause is correctly bounded by "an input you need".
The second, "or a glob matches nothing", is not bounded at all, and the elegance gate actively instructs the reviewer to go searching (`:58` "search the repo and the web before writing it", `:60` "If you cannot name one, search, then answer").
Ordinary exploratory greps miss constantly.
One reading: halt the review and report.
The other: report the empty result for that specific search and carry on.
The source technique (voltagent shortlist item 3, `knowledge-synthesizer`) means the first only for a required input, not for any failed search.

Fix: scope it - "If an input the review depends on is missing, or a glob over a path the artifact names matches nothing, stop and report that rather than inferring what should have been there. An exploratory search returning nothing is a normal result; record it and continue."
CONFIRMED.

### 5. MEDIUM - `tech-selection` hands off to skills the plugin does not ship

`skills/tech-selection/SKILL.md:9` and `:35` both route to the `experiment-loop` skill; `:11` names `brainstorming`.
Neither ships in `cultivation/marketplace/sam-cc-setup/`: `ls skills/` returns 13 directories and neither name is among them.
`experiment-loop` resolves on this machine only because it exists at `~/.claude/skills/experiment-loop`, and `brainstorming` comes from the separate `sam-superpowers` plugin.
The README states the plugin's audience is "existing repos on any machine", so on a clean install both handoffs are dead ends, and step 4's escape route for a high-importance/weak-evidence assumption disappears with no stated fallback.

Fix: either mark them as optional dependencies in the README and in the skill body ("if the `experiment-loop` skill is installed; otherwise write the protocol into the plan before measuring"), or inline the two-sentence bake-off contract so the skill is self-contained.
CONFIRMED.

### 6. LOW - the `plan-review` skill has no branch for a REJECT verdict

`agents/plan-reviewer.md:79` emits the revised handoff plan "only when the verdict is not REJECT".
`skills/plan-review/SKILL.md:32` instructs unconditionally: "write the revised handoff plan to disk next to the original".
On a REJECT there is no plan to write, and the skill does not say what to do instead.

Fix: one clause - "on REJECT there is no revised plan; present the findings and the verdict and stop, so the author can rewrite rather than patch."
CONFIRMED.

### 7. LOW - "This review is read-only" is prose sitting on top of an unrestricted Bash grant

`plan-reviewer.md:25`: "This review is read-only. Do not edit, commit, push, or run paid tools."
`plan-reviewer.md:4` grants `tools: Read, Glob, Grep, Bash, WebSearch`.

The allowlist already excludes Write and Edit, which is most of the protection.
But Bash is unrestricted, so `git commit`, `git push`, and paid CLI invocations remain reachable, and P16 is explicit that a rule which must hold every time should be enforced rather than requested.
Plugin agents cannot carry `hooks` (`research-cc-docs.md:288`), so the only available lever is the tool declaration itself.

Fix: keep the prose (it is cheap) and add `disallowedTools` naming the paid CLI wrappers, or accept the residual risk explicitly.
Low because a blind reviewer has no motive to commit, and the honesty bound is likely sufficient in practice.
CONFIRMED as a gap, PLAUSIBLE as a real risk.

### 8. LOW - three plan-review entries now compete in the skill listing (P14)

`plan-review`, the `plan-review-fanout` workflow, and `codex-plan-review` all describe adversarial review of a plan file.
P14's test is that overlapping descriptions degrade selection for all of them.
This is materially mitigated: `plan-review`'s description points at `/plan-review-fanout` for the parallel case, the workflow's description calls itself the "upgrade of the single-agent /plan-review skill", and `codex-plan-review` is scoped by "via the Codex CLI".
Recorded rather than pressed - no change requested, but if a fourth ever appears, this is the ceiling.

## Coverage ledger

| Checked | Status |
|---|---|
| All eight ruled-in techniques present, coherent | Clean - see the coverage table above |
| Frontmatter parses (yaml.safe_load on all three) | Clean - agent keys `name, description, tools, model, effort, maxTurns`; both skills `name, description, argument-hint` |
| Fields are real Claude Code fields | Clean - all six agent fields are on the plugin-agent supported list (`research-cc-docs.md:288`); `argument-hint` is on the skill list (`:174-176`). The agent correctly omits `permissionMode`, which plugin agents do not support - the other five agents in this plugin all carry it and are therefore wrong, but they are outside this review's scope |
| Unquoted-colon YAML hazards | Clean - the agent description is double-quoted, both skill descriptions use folded scalars |
| Cross-references resolve | `agents/plan-reviewer.md` exists; `/plan-review-fanout` exists at `workflows/plan-review-fanout.js`; `/code-review` and `/security-review` are bundled. Only `experiment-loop` and `brainstorming` fail - finding 5 |
| References to deleted assets | Clean - grep for `elegance-reviewer`, `plan-review-invoke`, `verify-app`, `regression-checker`, `diff-reviewer`, `self-critic`, `security-scanner`, `code-simplifier` across the three artifacts returns nothing. The only hits repo-side are the README's removal note (intentional) and two incidental prose uses of "self-critic pass" in `skills/unknowns/` |
| Fan-out workflow still consistent with the merged checklist numbering | Clean - `plan-review-fanout.js` lenses cite "canonical checklist item 2/3/4/5/6" and those map exactly to Repository rules / Over-engineering / Missing decisions / Completeness / Ordering in the new file. Checklist item 7 (assumptions and risk) has no fan-out lens; noted, not reported, because the fan-out is not under review here |
| P13 size | Clean - 84 / 32 / 37 lines, far under the 500-line split threshold |
| P19 blindness | Clean - enforced in three places (agent line 14, skill lines 20-22, skill step 2's NEVER list) and structurally, since the skill builds the prompt rather than forwarding the conversation |
| P21 explicit rubric | Clean - the seven checks and the finding contract are the rubric |
| P22 bounded critic | Clean - cap of 10 plus the traceability rule plus the ledger. Not reported: 10 is looser than the voltagent shortlist's top 3-5, but the ledger makes the cap auditable, which was the stated objection to a hard cap, so the looser number is defensible |
| Examined and not reported: `tech-selection` step 6 "the project's decision location" is undefined | One line, and the same step offers "the plan" as the concrete alternative, so the executor has a working default |
| Examined and not reported: `tech-selection:2` asserts "Reuse-before-new is repo law" | Overclaims for a plugin installed into arbitrary repos, but it is a taste statement the skill is entitled to make |
| Examined and not reported: the agent both authors the revised plan and is the sole verifier of its own findings | The vercel mechanical-claim-verification pass would close this, but it was not on the ruled-in list, so its absence is a design choice rather than a defect |
| Not examined | The five other agents' bodies, the hooks, and `plan-review-fanout.js` beyond its checklist-numbering references |

## Verdict

Findings 1 and 2 are the ones worth fixing before this ships: the first leaves the agent's headline output underdetermined, and the second means the mandatory gate can be satisfied invisibly.
Both are small edits to text that is otherwise well constructed, and neither touches the merge decision, the frontmatter, or the asset placement.
Everything ruled in is present, coherent, and non-duplicated apart from the licence-to-approve clause called out in finding 1.
Nothing here justifies a rewrite.

APPROVE_WITH_CHANGES
