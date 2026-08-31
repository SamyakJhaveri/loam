# Claude Code Plan Mode handoff: validate the Clief claims for Loam

Paste this prompt into a new Claude Code session after entering Plan Mode.

---

You are in Plan Mode in the Loam repository.

Your job is to build an evidence-backed plan for deciding which Clief claims
Loam should keep, test, change, or reject. Research first. Plan second. Stop for
Samyak's approval before any implementation.

## Hard boundary

Produce research and a proposed plan only.

Keep the working tree unchanged during this session. Do not edit Loam files,
`seed/`, hooks, settings, rules, skills, commands, agents, Copier configuration,
tests, or release tooling. Do not implement any Clief claim. Do not commit,
push, merge, publish, tag, or release.

End the session after presenting the plan and asking Samyak to approve it. An
approval must be an explicit later message. Do not treat this prompt as
implementation approval.

## Repository facts

Loam is both a Copier template and a Claude Code project.

- Only content under `seed/` renders into bootstrapped projects.
- Root-only files describe or operate the Loam repository itself.
- Generic behavior that every generated project needs belongs under `seed/`.
- Project-specific material must stay outside `seed/`.
- A change to `seed/` behavior, hooks, `copier.yml`, or release behavior uses a
  branch and pull request.
- One behavior change belongs in one implementation session.
- Source and observed command behavior override stale documentation.

Treat these facts as constraints on the plan. Verify their current expression
in the repository before mapping any recommendation.

## Required local reading

Read every file below in full before delegating research:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `.claude/rules/workflow.md`
4. `.claude/rules/known-issues.md`
5. `docs/specs/cliefnotes-wisdom.md`
6. `docs/specs/rebuild-research/research-cc-docs.md`
7. `docs/specs/rebuild-research/research-context-rules.md`
8. `docs/specs/rebuild-research/clief-claims-validation-method.md`

The three files under `docs/specs/rebuild-research/` are prior research. They
are leads, not authority. Recheck every product mechanic, source, date, and
inference. Record any conflict between fresh evidence and prior research.

Also inspect the current Loam implementation that corresponds to the claim
families. Include root instructions, `seed/`, `.claude/`, `cultivation/`,
`copier.yml`, `bin/verify-template.sh`, release callers, and current tests. Use
`rg` and source reads to find the exact active routes. Do not infer the current
state from the research notes.

## Exhaustive Clief evidence pass

Account for all Clief claims and their source evidence.

1. Read every normalized record in
   `soil/loam-rebuild-checkpoint/normalized-claims.jsonl` when it is available.
2. Reconcile every normalized ID and every raw ID with
   `docs/specs/cliefnotes-wisdom.md`.
3. Read every cited source and evidence field needed to judge each claim.
4. Inspect each unique cited Clief source page under
   `/Users/samyakjhaveri/Desktop/Skool AI Wisdom/skool-kb/out/cliefnotes` when
   that corpus is available.
5. Inspect external links that a Clief claim relies on. A link that was not
   opened is not evidence.

Use deterministic commands to compute coverage. Do not estimate counts by
eye. Sampling is allowed for exploration, but not for the final coverage claim.
If the ledger, corpus, or a cited source is unavailable, mark the affected
claims incomplete. State the one action that would unblock them. Do not call
the review exhaustive while any claim lacks a coverage disposition.

## Parallel read-only research team

Create a parallel, read-only research team. Use one lead editor. The lead
editor is the only agent that synthesizes the final plan. Research agents must
not edit files or write competing plans.

Give the agents disjoint work:

1. **Clief evidence auditor.** Reconcile normalized claims, raw claims, source
   pages, evidence grades, contradictions, and missing evidence.
2. **Claude Code product researcher.** Check current official Claude Code
   documentation. Verify instruction loading, skills, hooks, agents, teams,
   Plan Mode, memory, plugins, commands, validation, and worktrees.
3. **Anthropic practice researcher.** Check current Anthropic Engineering and
   official Anthropic or Claude blog sources. Separate documented product facts
   from first-party case reports and recommendations.
4. **Primary research reviewer.** Check reliable primary research on coding
   agents, repository context, planning, verification, evaluation, memory, and
   multi-agent work. Prefer peer-reviewed proceedings, author papers, and
   primary project artifacts.
5. **Loam mapper.** Inspect current Loam and rendered `seed/` behavior. Map each
   claim family to active files, current controls, tests, duplication, and
   missing wiring.

Each researcher returns a compact evidence table to the lead editor. Every row
must include a claim or family ID, finding, source URL or repository path,
access date, evidence type, limitation, and proposed verdict. Each researcher
must state what it could not verify.

Run these workstreams in parallel only where their inputs are independent. The
lead editor resolves overlaps and conflicts after all results return.

## Fresh external research rules

Check current sources during this session. Do not rely on model memory for
product mechanics or research results.

Use this source order:

1. Current official Claude Code documentation at `code.claude.com/docs`.
2. Current Anthropic Engineering and official Anthropic or Claude blog posts.
3. Reliable primary AI and coding-agent research.
4. Current source code or official release notes when documentation is silent.

Use secondary sources only to discover a primary source. Do not use a
secondary summary as the evidence for a verdict.

For each source, record:

- the direct URL or repository path;
- the access date;
- whether it proves a feature, a mechanism, or a measured outcome;
- the tested model, task, repository scale, baseline, and metric when relevant;
- limits on transfer to current Loam.

A vendor case report is first-party evidence. It is not an independent
replication. A successful demo without a comparator does not prove an outcome
improvement. Exact numeric heuristics need direct evidence or a Loam test.

## Verdict categories

Give every claim or clearly bounded claim family one of these verdicts:

| Verdict | Use when |
|---|---|
| `supported` | Current primary evidence supports the claim as stated and within its stated conditions. |
| `partially supported` | Evidence supports the mechanism or a narrower form, but not the full wording, scope, or universal rule. |
| `unsupported` | No adequate primary evidence supports the claim, or direct evidence refutes it. |
| `conflicting` | Credible sources or Clief records materially disagree and the conflict is not resolved by scope or conditions. |
| `time-sensitive` | The claim depends on current product, model, pricing, limits, flags, or service behavior and needs a dated recheck before adoption. |

Do not blend verdicts in one cell. Add separate columns for confidence,
evidence class, conditions, and recheck date where needed. A `time-sensitive`
verdict must include the current observed status and the exact source that
would be checked again.

Keep three evidence classes distinct:

- **Feature evidence:** the current product can do the stated thing.
- **Mechanism evidence:** there is a credible reason the thing may help.
- **Outcome evidence:** a comparison measured whether it helped.

Feature existence alone does not prove a quality improvement.

## Map findings to current Loam

For every verdict, inspect and record the corresponding Loam state.

The map must include:

- claim or family ID;
- current root-only Loam path;
- current shipped `seed/` path, if any;
- marketplace or cultivation path, if any;
- rendered-project effect;
- current verification or missing verification;
- duplication, conflict, missing route, or superseded mechanism;
- proposed action: keep, clarify, test, pilot, replace, retire, or no action;
- whether the action is generic enough to ship through `seed/`;
- branch and pull-request requirement;
- evidence and experiment that must pass before implementation.

Do not recommend copying a Loam-specific research artifact into `seed/`. Ship
through `seed/` only when the behavior is generic for bootstrapped projects.

## Evaluation designs

Propose controlled A/B evaluations for claims that have plausible mechanisms
but insufficient Loam outcome evidence. Propose the tests. Do not run them in
this Plan Mode session.

Each evaluation must define:

1. A falsifiable hypothesis and a decision threshold.
2. A control and one or more treatment arms with the same task inputs.
3. At least one negative control that can expose a false benefit or a bypass.
4. Fixed repository commit, model, effort, tools, permissions, prompt, and
   context budget where applicable.
5. Repeated trials and randomized condition order for nondeterministic agents.
6. End-state grading before transcript review.
7. Metrics for task success, hidden-test results, instruction adherence,
   false-green rate, scope drift, tokens, latency, cost, and human burden.
8. A stop, adopt, narrow, or reject rule tied to the results.

Cover at least these candidate comparisons when their claims survive the fresh
evidence pass:

- short root router versus monolithic instructions versus minimal instructions;
- Plan Mode and reviewed plan versus direct implementation;
- durable handoff versus no handoff versus a deliberately stale handoff;
- prose guidance versus deterministic gate versus hook-triggered gate;
- one agent versus producer plus reviewer versus a parallel read-only team;
- always-loaded procedure versus on-demand skill versus task-prompt procedure;
- correct memory versus no memory versus stale conflicting memory.

Negative controls must be able to fail. Include near-match hook events,
nonmatching paths, malformed hook output, known failing fixtures, stale facts,
irrelevant equal-token context, dependent same-file parallel work, and missing
or misleading handoffs where applicable.

## Required Plan Mode deliverables

The lead editor must return one coherent plan with these sections:

1. **Coverage statement.** Exact command-produced coverage of normalized IDs,
   raw IDs, source pages, external evidence, and unresolved gaps.
2. **Evidence matrix.** One row per claim or bounded family with the required
   verdict, evidence classes, sources, limits, confidence, and freshness.
3. **Conflict and freshness register.** Internal Clief contradictions, source
   conflicts, prior-research conflicts, time-sensitive mechanics, and recheck
   triggers.
4. **Current Loam map.** Exact root, `seed/`, marketplace, rendered, caller,
   hook, config, test, and release-gate connections.
5. **Evaluation portfolio.** Prioritized A/B and negative-control designs with
   costs, metrics, falsifiers, and decision rules.
6. **Proposed implementation sequence.** Small, independent behavior changes.
   Name exact files, interfaces, tests, render checks, risks, and branch policy
   for each change. This is a proposal only.
7. **Decision list for Samyak.** Choices that change scope, cost, or shipped
   behavior. Recommend one option and state why.
8. **Approval gate.** A final explicit statement that no implementation has
   started and a direct request for Samyak to approve or revise the plan.

If the full evidence matrix is too large for the final response, keep the plan
self-contained with a complete coverage index and bounded family summaries.
Propose the exact tracked artifact paths for the full matrix after approval.
Do not silently omit claims.

## Verification gates for this planning session

Before presenting the plan, run and report these checks:

1. Use a deterministic reconciliation command. Require every available
   normalized ID and raw ID to have one disposition. Report exact unmatched
   items rather than a rounded coverage percentage.
2. Check that every supported or partially supported verdict cites current
   primary evidence. Check that every unsupported verdict names the search
   scope or refuting evidence.
3. Check that every time-sensitive verdict has an access date and recheck
   trigger.
4. Check that every proposed Loam change maps to an inspected current path and
   a verification method.
5. Check that every proposed experiment has a negative control, a falsifier,
   and an end-state metric.
6. Run `git status --short`. Require an unchanged working tree.
7. Run `git diff --check`. Require exit `0` and no output.

Do not claim the plan is complete if any gate fails. Report the exact gap and
the single next action needed to close it.

## Future implementation gates to include in the plan

For any later approved implementation, require the smallest relevant test at
each step. Require a negative control for every new verifier or blocking hook.
Require a committed-`HEAD` Copier render for shipped behavior. Require
`bin/verify-template.sh` and `git diff --check` before any commit. Require a
fresh correctness review for changes over roughly one hundred lines or across
a trust boundary.

Generic shipped changes must originate in `seed/`. Root-only research and Loam
maintenance artifacts must remain outside `seed/`. Use a branch and pull
request for all `seed/` behavior, hook, Copier, and release changes.

## Completion criterion

You are done only when every available Clief claim has a disposition, every
load-bearing verdict has current primary evidence or a named evidence gap,
every recommendation maps to inspected Loam paths, every pilot has a falsifier,
the working tree remains unchanged, and Samyak has received one plan with a
clear approval choice.

Then stop and ask:

> Samyak, do you approve this plan for implementation, or do you want changes
> to the evidence thresholds, evaluation portfolio, or Loam scope?
