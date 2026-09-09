# Primary-source readings, 2026-09-08

Four reports written by Opus 4.8 readers from the live pages, repositories, and YouTube auto-captions, not from the earlier notes in `docs/research/`.
Fable 5.1 then read the page text itself for the Anthropic posts, cwc-long-running-agents, sssf, loop-engineering, unlazy, loopx, Roth, loiane, developersdigest, and two AI LABS transcripts, and a Fable fact-check ran against the reports.
The decision this reading fed is issue #38 and the subtraction ledger it produced.

| File | Covers |
|---|---|
| `anthropic-pages.md` | the loops post, the SDLC playbook, both harness posts, Building Effective Agents, the evals post, managed agents, the hooks doc |
| `loop-repos.md` | cwc-long-running-agents, sssf, unlazy, autoprompt, thoughtdag, loopy, loopx, LongHorizon, agent-apprenticeship, loop-engineering |
| `blogs-and-threads.md` | loiane, developersdigest, Roth's gate analysis, three playbook critiques; Reddit and X were unreachable |
| `videos.md` | five AI LABS and design videos with transcripts; one Claude video had no captions |

## Corrections the fact-check made to the first synthesis

- "Every source with a model verifier has exactly one" is false. autoprompt runs four checkers, agent-apprenticeship three roles, Roth four gates, LongHorizon an auditor beside the manager.
- Roth's 61 percent is the plan gate's own rejection rate, not the share of all rejections landing there. 31.5 percent of rejected work recovered. One operator, one system.
- unlazy's gates are written by the agent and approved command by command by the human. cwc's Stop hook commits work; unlazy's blocks exit without running checks. `/goal` is a prompt-based Stop hook.
- The harness post never had two evaluators. V2 kept one evaluator at the end and ran three QA rounds; the evaluator "continued to give real lift" at the edge of the model's ability.
- "Parallelism last" comes from Addy Osmani's guide (see `../anthropic-loop-engineering.md` lines 7 to 9), not from Anthropic.
- LongHorizon and unlazy ship replay suites; none of the sources runs its loop nested inside a round of itself.

## What held

The worker never grades its own work; a person decides the pass or fail lines before the run; deterministic checks first; simplest first and re-cut one component at a time on every model release; the plan gate is the cheapest place to catch errors.
The sources with field data kept several gates and report gains; the guidance posts say cut and measure.
The method both agree on: remove one component per run, read the run ledger, then keep or cut.
