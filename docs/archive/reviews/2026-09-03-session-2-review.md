# Session 2 review: prompts to Fable 5.1

Reviewer: Claude Fable 5.1, fresh context, 2026-09-03.
Scope reviewed: commit `eaf1aca` on `main` (plugin half) and commits `c05229f` and `d85a0da` on `fix/audit-s2-prompts` (seed half plus Codex fixes).
Full range checked: `git diff dfa9803..fix/audit-s2-prompts`, 13 files, +99/-64.
The branch is based on `eaf1aca` (`git merge-base main fix/audit-s2-prompts`), so it already contains the plugin half.

## Verdict: SHIP

All six handoff items are implemented.
Every block where the handoff gave exact text matches byte for byte.
The four checks pass on the branch (output below).
Two low-severity nits remain; neither blocks the merge.

## Checks run on `fix/audit-s2-prompts`

`uvx pytest -q bin/tests`:

```
153 passed, 367 subtests passed in 320.35s (0:05:20)
exit=0
```

`bin/verify-template.sh` (last line):

```
verify-template: PASSED
exit=0
```

`bin/harness-smoke.sh`:

```
== stage 1: render the working-tree seed ==
render: OK
== stage 2: rendered harness contract ==
contract: OK
== stage 3: skill-listing token weight (Score B) ==
score.B seed_listing_tokens=101 plugin_listing_tokens=2696

harness-smoke: PASS
```

Session 2 Verify line, `grep -rn "Fable 5[^.]" cultivation/marketplace/sam-cc-setup | grep -v "5\.1"`:

```
cultivation/marketplace/sam-cc-setup/skills/align-prompt/SKILL.md:97:  older models "are often too prescriptive for Claude Fable 5 and can degrade output quality"
```

That line is a direct quotation from the Fable 5 guide and keeps its Fable 5 citation. Historical, correct.
A tighter form, `grep -rn "Fable 5[^.0-9]"`, also surfaces line 93, which says "refusal on Fable 5; the 5.1 guide does not list it". Also historical, correct.

`grep -rn "^model:" cultivation/marketplace/sam-cc-setup/agents`:

```
agents/consistency-checker.md:5:model: claude-opus-4-8[1m]
agents/build-validator.md:5:model: claude-opus-4-8[1m]
agents/test-synthesizer.md:5:model: claude-opus-4-8[1m]
agents/read-only.md:5:model: claude-opus-4-8[1m]
agents/code-architect.md:5:model: claude-opus-4-8[1m]
agents/plan-reviewer.md:5:model: claude-opus-4-8[1m]
```

`grep -niE "sonnet|medium to high" cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md`: empty, exit 1.
`grep -rniE "model:\s*sonnet" cultivation/marketplace/sam-cc-setup/agents`: empty, exit 1.

## Exact-text conformance

Each block was extracted from the handoff and from the file and compared with `diff`. All five match:

| Handoff text | File | Result |
|---|---|---|
| Dispatch table | `skills/align-prompt/SKILL.md:37-42` | match |
| 5.1 deltas block plus the autonomy/batching paragraph | `skills/align-prompt/SKILL.md:103-123` | match |
| `reasoning_extraction` reword | `skills/align-prompt/SKILL.md:92-95` | match (bullet prefix only) |
| Teammate bullet | `skills/agent-team/teammate-prompt.md:14-18` | match |
| Model policy paragraph | `skills/agent-team/SKILL.md:32` | match |
| Editing discipline section | `seed/AGENTS.md.jinja:23-33` | match |
| writing-plans final line | `skills/writing-plans/SKILL.md:177` | match |
| Section 3 heading | `skills/align-prompt/SKILL.md:79` | match |

One deliberate drift from the handoff, and it is the right call.
Item 1 said the citation at line 176 "becomes the 5.1 guide URL".
The lead kept `[prompting-claude-fable-5]` on the four quoted phrases and added a new `[prompting-claude-fable-5-1]` key (`skills/align-prompt/SKILL.md:195`) for the API-parameter line.
I fetched the 5.1 guide: none of the four quotes appear in it. Retargeting would have produced false citations. Execution log decision (a) records this.

## Item-by-item

1. align-prompt: done. Frontmatter, dispatch table, refusal paragraph removed, heading, deltas block, `reasoning_extraction` reword, plan-mode renames, `-fable51.md`, sketch labels, citation. writing-plans line appended. Repo-wide grep for `fable5`, `f5`, `fable5-plan`, `-fable5.md`, `4.7` in the plugin, seed, and bin finds only the new `fable5.1` alias.
2. workflow-model-notes: done. Table rows are "Instruction detail" and "Subagents"; the Fable 5.1-only bullets are the four named in the handoff. Lines 15-21 ("Both models") and the "Harness-enforced" section are untouched. `bootstrap-cc-setup/SKILL.md:40-41` fixed.
3. agent-team: done. Teammate bullet replaced, both "Think hard" lines gone (`advisor-prompt.md`, `teammate-prompt.md`), Model policy paragraph replaced, Sonnet carve-out gone.
4. seed `AGENTS.md.jinja`: done on the branch. Gotcha lines for case-insensitive grep and marker-file counting removed; the tag and YAML gotchas kept; Editing discipline added after Gotchas. The contract (`bin/rendered_harness_contract.py`) never asserted those gotchas (grep for "case-insens", "marker file", "Editing discipline" in `bin/` is empty), so no test update was needed. The rendered seed passes the contract in the smoke run.
5. critique-swarm: "verbose preambles" dropped at `skills/critique-swarm/SKILL.md:51`.
6. build-validator and read-only re-pinned to `claude-opus-4-8[1m]` at `agents/build-validator.md:5` and `agents/read-only.md:5`. Effort stays `high` (decision d), which item 6 allowed.

## Claims checked against the guides

I fetched both prompting guides.

- Fable 5.1 guide: the targeted-edits sentence, the "mannered prose" line, the long-outputs-at-xhigh/max behavior, the fewer-progress-updates behavior, and the lead-keeps-working-while-subagents-run section are all present. `reasoning_extraction` does not appear; the safeguard section names compile-check phrasing, lesser-known languages, and base64 tool output. The reword at line 92-95 is accurate.
- Opus 4.8 guide: "does not silently generalize an instruction", "tends to spawn fewer subagents by default", "favor reasoning over tool calls", and the first-turn front-loading paragraph are all present. The new table row in `workflow-model-notes.md:13` is accurate.

## Scope extensions (log decision c) and the Codex round

- Removing the Sonnet carve-out from `teammate-prompt.md:39` and `scenarios.md:8`: justified. Leaving them would have contradicted the Model policy paragraph in the same skill.
- Tightening the test-synthesizer sample validator to `opus`, `claude-opus-*`, `claude-fable-*` (`agents/test-synthesizer.md:130-132`): justified. The old `claude-*` prefix accepted `claude-sonnet-*`, which is exactly the hole the never-Sonnet rule closes.
- Codex accepted: five scenario rows moved to xhigh (`scenarios.md:20,59,60,78,79`) match "Workers at xhigh everywhere"; the two "advisor runs at higher effort" lines (`advisor-prompt.md:17`, `teammate-prompt.md:117`) were false once the Fable advisor is capped at high. Correct to accept.
- Codex rejected: keeping `fable5`/`f5` aliases, a model pin on nested Explore subagents, gating the writing-plans line by target. All three rejections are consistent with the handoff and the binding rules. One round used; cap respected.

## Findings

Low severity, both optional follow-ups:

1. `cultivation/marketplace/sam-cc-setup/skills/agent-team/scenarios.md:7` still says "Every teammate below runs Opus" with the bare alias. `SKILL.md:32` was upgraded to "Opus 4.8 (`claude-opus-4-8[1m]`)". The handoff named the bare-alias fix for SKILL.md only, so this is not drift, but the two files now disagree in precision.
2. `cultivation/marketplace/sam-cc-setup/agents/test-synthesizer.md:130` accepts the short alias `opus` but not `fable`, while the policy sentence says "Use only Opus or Fable". No agent uses a short Fable alias today, so this has no effect.

Observations, no action needed:

- The "Scope of extras" quotation in `align-prompt/SKILL.md:107-113` and the Standing facts block is an abridged version of the guide's paragraph. The guide's version also has the ambiguity sentence and the "sized like the neighboring test files" clause. The handoff supplied the abridged text, so the session matched its spec. If the quotation marks are meant to signal verbatim, a later session could mark it abridged.
- Handoff item 1 says "Keep the five existing bullets"; the section has six. Pre-existing count, all six kept.
- The `Subagents` row for Fable 5.1 in `workflow-model-notes.md:14` ("Delegate freely; the lead keeps working while subagents run") describes a harness setting from the guide more than a model trait. Accurate enough for a rule that tells a session which column to apply.
- Teammate bullet "make the routine judgment call yourself" sits next to the pre-existing "Present options with tradeoffs, not unilateral choices" (`teammate-prompt.md:20`). The two read as a tension on first pass; the first is about routine calls, the second about significant decisions. Not touched by the handoff.
- Residuals the log named are confirmed as stated: `align-prompt/SKILL.md:145` "do not target Opus 5" is pre-existing and still true; the em dash in `seed/AGENTS.md.jinja:1` is pre-existing and untouched; `read-only.md:3` also carries a pre-existing em dash.

## Taste

Minimal diffs throughout. No file was rewritten. Every replaced paragraph reads like its neighbours.
The three commit messages describe the change and cite the checks. No agent co-author trailer on any of the three commits, per the user's rule.
Both Codex transcript and audit log live under gitignored paths (`.gitignore:35`, `.gitignore:83`).

## Thoroughness

The execution log records the four checks after every commit with their results, and my re-run on the branch reproduces them.
The log is honest about `/goal` not being set (decision e).
Test count is 153 where session 1 logged 151. Session 2 changed no file under `bin/tests`, and `git diff --stat c7952db dfa9803 -- bin/tests` is empty, so the origin of the two extra tests is not verified here. It does not affect this verdict.
