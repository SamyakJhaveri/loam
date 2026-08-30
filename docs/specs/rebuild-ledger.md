# Loam rebuild ledger - keep / remove / rewrite

## Rulings (Samyak, 2026-08-29) - EXECUTED in commits 74b1d14 + follow-up

1. Layering: ADOPTED. seed/ = minimal always-on; sam-cc-setup = agents + optional skills.
2. Plan-reviewer: REWRITE confirmed; waits for Samyak's reference agents + the rebuild design session.
3. Codex: tiered ship per recommendation (fixes pending in rebuild session).
4. Research flavor: RETIRED. Unified seed, no flavored separations. copier.yml simplified; overlay deleted; research assets parked in cultivation/wip/research-assets/ for later use as normal optional assets.
5. Ponytail: PURGED everywhere (shipped settings, jinja docs, the private benchmark repo, global plugin + marketplace).
6. Stop gate: REWIRED slimmed (stop-verify-gate.sh, deterministic core only).
7. Sync: CONSOLIDATE to at most two canonical mechanisms - Copier forward (loam -> seeded projects, tag-driven) and ONE unified reverse mechanism (seeded projects -> loam, absorbing template-sync/agent-sync/hub-ci). Consolidation design happens in the rebuild design session; engine kept parked until then.
Extra rulings: align-prompt REWRITTEN (not removed) for Fable 5 + Opus 4.8, new home sam-cc-setup, with citations; catchup slimmed, one home (sam-cc-setup), seed copy deleted; impeccable bundle KEPT; auto-activate bug fixed everywhere (real field: disable-model-invocation).

Standing reminders for Samyak (parked, raise when relevant):
- Wire align-prompt into a workflow/hook so rough handovers get aligned automatically.
- Source external plugins, MCPs, and skills from other repos + online later.

> Working document for the 2026-08 rebuild epoch. Judged row by row with Samyak; nothing is auto-applied.
> Markers: (kept) = survived the teardown unprefixed, (reassess)/(rewrite) = Samyak's teardown prefixes.
> Verdicts here are RECOMMENDATIONS awaiting Samyak's call. Sources:
> [CC] docs/specs/rebuild-research/research-cc-docs.md (official Claude Code docs, fetched 2026-08-28)
> [CTX] docs/specs/rebuild-research/research-context-rules.md (Claude 5 context-engineering rules, official Anthropic)
> [CDX] docs/specs/rebuild-research/research-codex-docs.md (official Codex docs, fetched 2026-08-28)
> [W:N-xxxx] docs/specs/cliefnotes-wisdom.md normalized claim ids (1,270 raw claims, 64% author-assertions - treat as hypotheses)
> [GD] gate-diagnosis report 2026-08-28

## Decision criteria (from the research pass)

1. Burden of proof is on KEEPING: Anthropic cut 80%+ of Claude Code's system prompt with no eval loss. [CTX]
2. "If Claude already does something correctly without the instruction, delete it or convert it to a hook." [CTX, official docs]
3. One directive, one home. Overlapping layers (rule + skill + prompt) measurably degrade behavior. [CTX] [W:N-0058]
4. Must-hold-every-time -> hook (deterministic). Judgement call -> prose, once. [CTX]
5. Skills are priced: descriptions compete for ~1% of context; unused skills starve the useful ones. Every subagent reloads the whole CLAUDE.md + rules hierarchy. [CC]
6. Verifier is never the author; unbounded adversarial critics over-report by construction. [CTX]
7. Prefer a native feature over custom machinery that imitates it. [CC]

## Cross-cutting bug found (fix regardless of verdicts)

- `auto-activate:` is NOT a real skill-frontmatter field - zero hits in all 34 doc pages. Loam's tiering convention (13 skills marked `auto-activate: false`) never worked; those skills stayed model-invocable and kept burning listing budget. The real field is `disable-model-invocation: true`. [CC] Applies to every surviving skill and the known-issues entry that codifies the convention.

## seed/.claude - shipped Claude Code harness

| Asset | Marker | Recommendation | Reason / citation |
|---|---|---|---|
| skills/auto-phase | kept | REMOVE | phase-plan executor duplicated by native workflows + /goal (both CONFIRMED) [CC crit.7]; also still references retired /validate + critique gates |
| skills/reassess-agent-team | reassess | REMOVE | native agent teams + dynamic workflows supersede [CC]; workflows are resumable and keep results out of context |
| skills/reassess-align-prompt | reassess | REMOVE | written for Opus 4.6/4.8 conventions; Claude 5 guidance is the opposite (judgement, minimal steering) [CTX]; taste-priced per crit.5 |
| skills/reassess-catchup | reassess | KEEP (slim) | genuinely useful session bootstrap; native recaps cover part but not git/env/memory staleness; deduplicate with sam-cc-setup:catchup - ONE home [crit.3] |
| skills/reassess-critique-swarm | reassess | REMOVE | fan-out critique is the native workflows adversarial-verify pattern [CC]; unbounded critics over-report [CTX crit.6] |
| skills/reassess-dream | reassess | REMOVE | native auto-dream + /dream exist [CC]; duplicate also in sam-cc-setup [crit.3] |
| skills/reassess-plan-review-invoke | reassess | REMOVE | folds into the merged plan-reviewer redesign (see agents row); invoke-wrapper skills are ceremony [CTX] |
| skills/reassess-researcher | reassess | REMOVE | bundled /deep-research workflow + research skills supersede [CC crit.7] |
| skills/reassess-template-sync | reassess | DEFER to reassess-bin verdict | thin wrapper over template-sync.sh; follows its script's fate |
| agents/rewrite-plan-reviewer.md | rewrite | REWRITE (decided) | merge with sam-cc-setup elegance-reviewer into ONE blind review unit: fresh context, sees only plan + criteria, never author reasoning [CTX crit.6]; judgement-based prompt, bounded findings; adversarial PLAN review has NO bundled equivalent [CC] so it earns its place; landing layer per cross-cutting decision 1 |
| agents/rewrite-self-critic.md | rewrite | REMOVE | diff critique is bundled /code-review's job (background fork, effort-tunable, --fix) [CC crit.7]; unbounded critic [crit.6] |
| hooks/bash-audit-log.sh | kept | KEEP | deterministic, cheap, useful forensics (proved itself in the gate diagnosis [GD]); log already gitignored |
| hooks/concurrent-checkout-guard.sh | kept | KEEP (verify) | guards a real race (index.lock); native worktrees reduce but do not remove it; re-verify need once worktree-first workflow lands |
| hooks/post-compact-recovery.sh | kept | KEEP | deterministic context re-injection after compaction; fixed for renamed rule in 7dce8ea |
| hooks/rewrite-stop-verify-gate.sh | rewrite | REWRITE -> smaller | keep the deterministic core (git diff --check, ruff, bash -n on changed files = crit.4 territory); drop prose-y verification theater; native /goal covers goal-completion, not lint gates [CC]; currently UNWIRED - decision needed on re-wiring |
| rules/architecture.md | kept | KEEP (audit content) | survives if each line passes "would removing this cause mistakes?" [CTX] |
| rules/reassess-context-md-anatomy.md | reassess | REWRITE (slim) | CONTEXT.md routing is the corpus's strongest theme [W:N-0029,N-0030 demo-grade]; but cut to the anatomy + skip-column principle, drop the sizing tables [CTX] |
| rules/reassess-rewrite-known-issues.md | reassess+rewrite | REWRITE | gotcha log is exactly what CLAUDE.md-layer docs are FOR ("purpose + gotchas") [CTX]; but entries about deleted machinery + the false auto-activate convention must go |
| settings.json | kept (pruned) | KEEP + 2 edits | pruned in 317b961; EDIT 1: drop ponytail enablement (lines 9, 11-18) - its SubagentStart hook injects "delete the explanation" into every spawned agent; dormant here, armed in any seeded project that installs it [GD]; EDIT 2 candidate: `skillOverrides` to tier skills correctly instead of the fake auto-activate field [CC] |

## seed/.codex - shipped Codex harness

Premise check: "Codex only reads AGENTS.md" is FALSE. Codex today consumes .codex/config.toml, .codex/hooks.json, .codex/agents/*.toml, .codex/rules/*.rules (Starlark), and .agents/skills/ - but ONLY in projects the user marks trusted. [CDX]

| Asset | Marker | Recommendation | Reason / citation |
|---|---|---|---|
| config.toml | kept | KEEP + fix 3 defects | layer is real [CDX]; fix: `agents.max_depth` is not a documented key (inert); dangling refs to `.codex/mcp/memory-server.sh` and `.agents/skills/agent-team` (neither ships); `max_threads` is a legacy alias |
| reassess-hooks.json | reassess | RENAME to hooks.json or REMOVE | Codex discovers `hooks.json` ONLY - current name never loads [CDX]; schema itself is valid and portable |
| hooks/post-compact-recovery.sh | kept | KEEP | PostCompact is a documented Codex event [CDX] |
| rules/reassess-default.rules | reassess | KEEP (verify filename discovery) | Starlark execpolicy is the real Codex rules concept [CDX]; filename auto-load undocumented - verify with `codex execpolicy check` |
| (missing) .agents/skills/ | - | ADD if Codex skills wanted | the ONLY shared-asset location between harnesses (same SKILL.md format) [CDX] |
| (missing) trust documentation | - | ADD | entire .codex/ layer is inert until the user trusts the project + reviews hooks via /hooks; bootstrap output must say so [CDX] |

## seed/ root + research overlay

| Asset | Marker | Recommendation | Reason / citation |
|---|---|---|---|
| CLAUDE.md.jinja | kept | REWRITE | target: purpose + gotchas + routing table, under 200 lines, per-line removal test [CTX] [W:N-0249,N-0252]; every subagent reloads it [CC] |
| AGENTS.md.jinja | kept | REWRITE | align with official contract: concatenated root-down, 32 KiB cap, prose has NO other Codex home so Claude-rules content the Codex side needs must fold in here [CDX] |
| README.md.jinja, pyproject.toml.jinja, _gh_setup.sh | kept | KEEP | mechanical |
| reassess-_apply_research_overlay.sh + reassess-_copier_merge_hooks.py | reassess | DEFER to flavor decision | follows cross-cutting decision 4 |
| _research/ overlay | reassess | SLIM or CUT | 32 research skills already deleted in teardown; remaining: 6 seed-docs templates + 1 hook + 2 rules; keep only if research flavor survives [decision 4] |
| copier.yml | kept | KEEP (simplify with flavor decision) | |

## reassess-bin/ - parked scripts

| Asset | Recommendation | Reason / citation |
|---|---|---|
| verify-template.sh (+test) | REWRITE (smaller) | its frontmatter/JSON checks are superseded by `claude plugin validate` [CC] - BUT that command refuses symlinked .claude dirs, which is loam's exact layout, so a thin wrapper remains needed; render-check via copier stays custom |
| release.sh | KEEP | tagging remains mandatory for Copier consumers (tags, not HEAD); no native equivalent |
| ip-sweep.sh + check-own-synthesis.py + .ip-terms.example | KEEP | policy guard, not tech; no native equivalent; cheap |
| template-sync.sh + agent-sync engine (scan/prune/safe-io + 100+ tests) | DECIDE by usage | heaviest asset in the repo; earns its place ONLY if the hub->projects sync loop is actually exercised across Samyak's projects; if the rebuild makes plugins (seed-skills marketplace) the distribution channel, the plugin path supersedes file-sync [CC crit.7] |
| hub-ci.sh | FOLLOWS agent-sync | |
| lint-skill-descriptions.sh | REWRITE (smaller) | superseded in part by `claude plugin validate` + the doc'd YAML rules [CC]; keep only the semantic checks the native tool lacks |
| spike-probes.sh | REMOVE | mechanism-spike leftover, spike done 2026-07-19 |
| lib.sh | FOLLOWS its dependents | |

## CI

| Asset | Recommendation | Reason / citation |
|---|---|---|
| test.yml | REWRITE (decided) | repoint at surviving verify tooling once ledger executes; fires on PR only |
| release.yml | KEEP (re-verify) | tag-gated release remains the Copier contract |

## cultivation/marketplace - 16 bundles

| Bundle | Recommendation | Reason / citation |
|---|---|---|
| sam-cc-setup | KEEP = becomes the agent/skill layer (recommend) | resolves the duplicate-layer problem [crit.3]: seed/ ships the minimal always-on harness; sam-cc-setup carries agents + optional skills as an installable plugin; its 13 agents then absorb the seed/ agent survivors (merged plan-reviewer lands here) |
| sam-superpowers | KEEP (decided) | brainstorming-only since 0d4efa9 |
| pocock-engineering | REMOVE | exact duplicate of the globally installed mattpocock-skills plugin [crit.3] |
| impeccable | DECIDE | seed vendored copy deleted in teardown; native /simplify + design skills cover part; keep bundle only if UI polish workflow is still used |
| team-deliberation | REMOVE | native agent teams + workflows [CC crit.7] |
| meta-improvement, helpers, business-process | SLIM | audit per-skill with the listing-budget lens [CC crit.5]; likely few survivors |
| academic-research, gpt-researcher, storm-research, nature-skills | REMOVE or ARCHIVE | native /deep-research workflow supersedes the research fan-outs [CC]; keep only venue-specific paper tooling if research flavor survives |
| code-review-graph | REMOVE | bundled /code-review [CC crit.7] |
| planning-with-files, ui-ux-pro-max, understand-anything | DECIDE by usage | no native supersession claim; judged on actual use |
| web-frontend-* + deer-flow | KEEP as-is | already defaultEnabled:false; zero context cost until enabled |

## docs/

| Asset | Recommendation | Reason / citation |
|---|---|---|
| ASSET-LAYERS, BOOTSTRAP, COPIER, FLAVORS, SYNC, MEMORY, VISUAL-OVERVIEW, MIGRATION-v3, FUTURE-WORK, known-failures | REWRITE after structure lands | several describe deleted assets; rewrite once, against the rebuilt tree, not incrementally |
| docs/specs/* (8 pre-teardown specs) | ARCHIVE | move to _archive/; superseded by the rebuild |
| CLAUDE.md (root) | done (interim) | rewritten in 7dce8ea for the epoch; final form after rebuild |

## Cross-cutting decisions for Samyak

1. LAYERING (recommend: adopt): seed/ = minimal always-on (CLAUDE.md.jinja + 3-4 hooks + 2-3 rules + settings); sam-cc-setup plugin = agents + optional skills; cultivation/marketplace = everything else, install-on-demand. Kills every seed-vs-plugin duplicate [crit.3, crit.5].
2. PLAN-REVIEWER (decided rewrite): one blind unit = plan-review judgement pass + elegance frame-breaking pass, fresh context, author reasoning withheld, bounded findings. Samyak's found agents fold in as references when shared.
3. CODEX: keep the .codex layer (it is real) with the 3 defect fixes + trust documentation, or cut to AGENTS.md-only tier 1? [CDX recommends: ship AGENTS.md + .agents/skills by default, .codex/ as documented opt-in]
4. RESEARCH FLAVOR: survive as Copier flavor, or retire (research bundles nearly all superseded)?
5. PONYTAIL: remove from shipped settings.json? (recommend yes - subagent-hostile injection [GD])
6. STOP GATE: re-wire rewrite-stop-verify-gate.sh (slimmed) or leave turn-end unverified?
7. AGENT-SYNC ENGINE: keep the file-sync hub machinery, or let the plugin marketplace BE the distribution channel?

## Rebuild executed (2026-08-29, session close-out)

All six work-queue steps of docs/specs/rebuild-session-brief.md are done.
Structure design + two blind reviews: docs/specs/rebuild-structure-design.md (verdict recorded inside).
Step 2 merge: one blind plan-reviewer agent (sam-cc-setup) + /plan-review + /tech-selection; blind-reviewed (refagents-merge-review.md).
Steps 3-5: one prose home via @AGENTS.md import; catchup shared via .agents/skills + symlink; codex layer fixed; MCPs cut; bin/ repopulated; verify-template rewritten and PASSING.
Step 6: bundles slimmed per slim-audit-bundles.md; CI repointed; docs rewritten; zero reassess-/rewrite- prefixes remain.
