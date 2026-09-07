# Harness Smoke Rig - design

> Approved by Samyak on 2026-09-01 after a 7-agent audit
> (session history, harness inventory, Desktop fleet survey, surprise-me panel, 20-source research sweep).
> Interactive version of this design: the "Harness Smoke Rig" artifact report from the planning session.
> Evidence base: the planning session's plan file and `docs/specs/rebuild-research/clief-claims-verdicts.md`.

## Goal

One repeatable gate that proves the rendered harness works and measures how well it guides the model.
"Works" is the floor.
The bar is: token efficiency, correct skill/agent/hook routing, and long goal-directed loops that finish headless.

## Section 1: architecture

One script, `bin/harness-smoke.sh`, four stages, PASS/FAIL verdict.

1. **Render.**
   Copier renders the seed from the local working tree into a scratch directory.
   It must test what is about to ship, not the last tag and not the last commit.
2. **Contract.**
   Run the existing `bin/rendered_harness_contract.py` against the rendered tree.
   Reuse, not rebuild.
3. **Live loop.**
   Drive headless Claude sessions (`claude -p`) inside the rendered project through a scripted
   research-engineering task: plan, execute, validate, critique, handoff.
   Every hook appends one line to a hook log when it fires.
   The rig asserts fired hooks equal registered hooks.
4. **Scores.**
   Three numbers, printed and appended to a tracked run log:
   - **A. Routing accuracy**: share of probe prompts where the model invoked the expected skill or agent.
   - **B. Always-loaded token weight**: rendered prose chain plus skill-listing weight, against a budget.
   - **C. Loop health**: goal reached headless, turn count, spend per unit progress,
     and defensiveness creep per iteration (added guards and try/except blocks).

## Section 2: what feeds the rig

- **Routing probes use the first-party skill-creator eval format**:
  a committed `evals/evals.json` per skill, subagent-isolated token-counted runs,
  `benchmark.json` comparing with-skill vs without, and should/should-not-trigger tuning probes.
  The corpus is seeded from the salvaged E5 pilot data
  (staged at `soil/e5-pilots-salvage-2026-09-01/`, 31 rendered fixtures plus graders; ip-sweep before tracking).
- **The token check is deterministic**: verify-template stage 8 sums model-invocable description
  lengths against the 1% listing budget from `docs/specs/seed-skill-promotion.md`.
  Measured 2026-09-01: ~2,875 tokens, ~1.4%; the budget has already tripped.
- **The loop stage uses `/goal`**:
  `claude -p "/goal <condition> or stop after 20 turns" --output-format stream-json`,
  parsed for turns, spend, and hook-log coverage.
- Eleven Wave F fixes land before the baseline run so the scores measure a sound harness
  (force-push bypass class, `Bash(sed:*)` allowlist hole, fake `auto-activate` field,
  silent ruff no-op in the stop gate, side-effect skills made manual-only, hygiene batch).

## Section 3: execution order

1. Wave F fixes. Seed-behavior items ride one branch and PR; docs and memory fixes go direct to main.
2. Build the rig: `bin/harness-smoke.sh`, per-skill `evals/`, stage-8 token gate.
3. Baseline run; commit the run log. Every later harness change shows its effect as a number moving.
4. Opportunity wave, owner-gated per item:
   /goal adoption note and a SessionStart compact-matcher hook;
   review-cluster consolidation if the baseline probe confirms the ambiguity;
   the research-lane marketplace bundle behind the vet-skill gate;
   fleet promotions (completion contract, bash-guard, codex-review convention, skills-lock).
5. Tag v2.1.0. Copier resolves tags, so nothing ships until this happens.
6. Handoff for deferred work: seed-to-project sync repair, align-prompt auto-wiring,
   unfunded hypotheses and recheck scheduling.

## Non-goals

- No seed-to-project sync changes in this effort (deferred by owner ruling, 2026-09-01).
- No new always-loaded prose. Every activation lands as an on-demand skill, a hook, or a gate.
