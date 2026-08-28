# Loam rebuild ledger - keep / remove / rewrite

> Working document for the 2026-08 rebuild epoch.
> One row per surviving asset. Judged row by row with Samyak; nothing is auto-applied.
> Markers from the teardown: (kept) = survived unprefixed, (reassess) = user marked for reassessment, (rewrite) = user marked for rewrite.
> Verdict values: KEEP / REMOVE / REWRITE / PENDING.
> Every non-pending verdict must carry a citation: an official doc URL or a cliefnotes-wisdom norm_id.

## Decision criteria (filled from research pass)

- To be filled from research-context-rules and research-cc-docs findings.

## seed/.claude - shipped Claude Code harness

| Asset | Marker | Verdict | Reason / citation |
|---|---|---|---|
| skills/auto-phase | kept | PENDING | |
| skills/reassess-agent-team | reassess | PENDING | native agent teams + workflows may supersede |
| skills/reassess-align-prompt | reassess | PENDING | |
| skills/reassess-catchup | reassess | PENDING | overlaps native recaps + /catchup in sam-cc-setup |
| skills/reassess-critique-swarm | reassess | PENDING | workflows adversarial-verify may supersede |
| skills/reassess-dream | reassess | PENDING | native auto-dream exists; duplicate in sam-cc-setup |
| skills/reassess-plan-review-invoke | reassess | PENDING | folds into merged plan-reviewer redesign |
| skills/reassess-researcher | reassess | PENDING | native /research + deep-research skills exist |
| skills/reassess-template-sync | reassess | PENDING | pairs with reassess-bin/template-sync.sh |
| agents/rewrite-plan-reviewer.md | rewrite | REWRITE (decided) | merge with elegance-reviewer into ONE blind review unit; judgement-based prompt; layer TBD (seed vs sam-cc-setup) |
| agents/rewrite-self-critic.md | rewrite | PENDING | overlaps native /code-review; duplicate in sam-cc-setup |
| hooks/bash-audit-log.sh | kept | PENDING | writes .claude/audit.log; unbounded growth noted |
| hooks/concurrent-checkout-guard.sh | kept | PENDING | native worktree support may supersede |
| hooks/post-compact-recovery.sh | kept | PENDING | native PostCompact behavior improved in Claude 5 era |
| hooks/rewrite-stop-verify-gate.sh | rewrite | PENDING | currently UNWIRED (pruned in 317b961) - the turn-end gate (git diff --check + ruff + bash -n, blocking) no longer runs ANYWHERE; decide: re-wire under current name, rewrite, or rely on native /goal + plugin evals (gate-diagnosis report 2026-08-28) |
| settings.json ponytail enablement (lines 9, 11-18) | kept | PENDING (recommend REMOVE) | landmine found by gate-diagnosis: ponytail ships a SubagentStart hook injecting "if the explanation is longer than the code, delete the explanation" into EVERY spawned agent - adversarial to review/report agents; dormant in loam (plugin not installed here) but ships to every seeded project and arms on any /plugin install |
| rules/architecture.md | kept | PENDING | |
| rules/reassess-context-md-anatomy.md | reassess | PENDING | |
| rules/reassess-rewrite-known-issues.md | reassess+rewrite | PENDING | gotcha entries partly stale after teardown |
| settings.json | kept (pruned) | KEEP | pruned to 3 existing hooks in teardown commit 317b961 |

## seed/.codex - shipped Codex harness

| Asset | Marker | Verdict | Reason / citation |
|---|---|---|---|
| config.toml | kept | PENDING | verify against current Codex docs (research-codex-docs) |
| reassess-hooks.json | reassess | PENDING | Codex hook support unverified |
| hooks/post-compact-recovery.sh | kept | PENDING | |
| rules/reassess-default.rules | reassess | PENDING | |

## seed/ root + research overlay

| Asset | Marker | Verdict | Reason / citation |
|---|---|---|---|
| CLAUDE.md.jinja | kept | PENDING | rewrite against L0 lean guidance (purpose + gotchas only) |
| AGENTS.md.jinja | kept | PENDING | align with official AGENTS.md contract |
| README.md.jinja, pyproject.toml.jinja | kept | PENDING | |
| _gh_setup.sh | kept | PENDING | |
| reassess-_apply_research_overlay.sh | reassess | PENDING | research-flavor machinery |
| reassess-_copier_merge_hooks.py | reassess | PENDING | |
| _research/ overlay (seed-docs, 1 hook, 2 rules, settings-hooks.json now empty) | reassess | PENDING | does the research flavor still earn its complexity? |
| copier.yml + flavor machinery | kept | PENDING | |

## reassess-bin/ - parked scripts

| Asset | Marker | Verdict | Reason / citation |
|---|---|---|---|
| agent-sync engine (scan/prune/safe-io + 100+ tests) | reassess | PENDING | hub sync machinery; heavy; judged against actual multi-project use |
| template-sync.sh | reassess | PENDING | |
| verify-template.sh + test-verify-template.sh | reassess | PENDING | currently broken against gutted seed; CI depends on it |
| hub-ci.sh | reassess | PENDING | |
| release.sh | reassess | PENDING | tagging still required for Copier consumers |
| ip-sweep.sh + check-own-synthesis.py + .ip-terms.example | reassess | PENDING | IP guards; policy decision, not tech |
| lint-skill-descriptions.sh | reassess | PENDING | |
| spike-probes.sh | reassess | PENDING | mechanism-spike leftover |
| lib.sh | reassess | PENDING | follows its dependents |

## CI

| Asset | Marker | Verdict | Reason / citation |
|---|---|---|---|
| .github/workflows/test.yml | kept (broken) | REWRITE (decided) | points at deleted bin/ paths; fires on PR only; repair when rebuild shape known |
| .github/workflows/release.yml | kept | PENDING | fires on tags; re-verify against rebuilt verify tooling |

## cultivation/marketplace - 16 bundles

| Bundle | Verdict | Reason / citation |
|---|---|---|
| sam-cc-setup | PENDING | candidate REAL agent layer: 13 agents (incl. plan-reviewer + elegance-reviewer to merge), 12 skills, hook set, plan-review-fanout workflow; overlaps seed/ heavily |
| sam-superpowers | KEEP (decided) | brainstorming-only as of commit 0d4efa9 |
| pocock-engineering | PENDING | upstream also installed globally as mattpocock-skills plugin - duplicate? |
| impeccable | PENDING | was vendored into seed (v4.0.0), seed copy deleted in teardown |
| team-deliberation | PENDING | native agent teams may supersede |
| meta-improvement | PENDING | |
| helpers | PENDING | |
| business-process | PENDING | |
| academic-research / gpt-researcher / storm-research / nature-skills | PENDING | research bundles; overlap deep-research skill |
| code-review-graph | PENDING | native /code-review may supersede |
| planning-with-files | PENDING | |
| ui-ux-pro-max / understand-anything | PENDING | |
| web-frontend-* + deer-flow (git-subdir, disabled) | PENDING | already defaultEnabled:false |

## docs/

| Asset | Verdict | Reason / citation |
|---|---|---|
| ASSET-LAYERS.md, BOOTSTRAP.md, COPIER.md, FLAVORS.md, SYNC.md, MEMORY.md, VISUAL-OVERVIEW.md, MIGRATION-v3.md, FUTURE-WORK.md, known-failures.md | PENDING | rewrite to match rebuilt structure; several now describe deleted assets |
| docs/specs/* (8 existing spec docs) | PENDING | archive candidates |
| CLAUDE.md (root) | REWRITE (decided) | references deleted rules/skills throughout; rewrite after ledger is judged |

## Cross-cutting decisions (judged with Samyak)

1. Which layer is the real agent/skill layer: seed/ (shipped to every project) vs sam-cc-setup (installable plugin)? Duplicates exist in both.
2. Plan-reviewer redesign: single merged blind review unit (plan-review checklist judgement + elegance frame-breaking pass, separate contexts, author reasoning withheld). Landing layer per decision 1.
3. Does the Codex harness survive at all beyond AGENTS.md (pending research-codex-docs)?
4. Does the research flavor survive as a Copier flavor?
5. Native replacements to adopt: /code-review, plugin evals, auto-memory/auto-dream, workflows, /goal (each pending CONFIRMED status from research-cc-docs).
