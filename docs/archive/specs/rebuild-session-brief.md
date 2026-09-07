# Rebuild design session - brief

> Written 2026-08-29 for a fresh session. Self-contained: read this file and the files it names; nothing else is required.
> State as of commit 604e27a on main. Working tree clean. All prior verdicts are EXECUTED.

## Goal

Design the rebuilt Loam structure, get the plan reviewed, then execute it: a lean, unified seed (no flavors) that turns Loam back into a working software-factory template.
Done means: `reassess-bin/verify-template.sh` (rewritten) passes, CI is repointed and green on a PR, and a release tag ships.

## Read first, in this order

1. `CLAUDE.md` (root) - the epoch banner and current layout.
2. `docs/specs/rebuild-ledger.md` - rulings at top (EXECUTED), remaining rows below. This is the work queue's source of truth.
3. `docs/specs/rebuild-research/research-context-rules.md` - the design criteria (judgement not rules, progressive disclosure, one directive one home, verifier never the author).
4. `docs/specs/rebuild-research/research-cc-docs.md` and `research-codex-docs.md` - what the harnesses natively provide today; read before designing any custom asset.
5. `docs/specs/cliefnotes-wisdom.md` - 928 normalized source claims by theme; cite norm_ids in design decisions. Caveat: 64% are bare assertions.
6. For the plan-reviewer redesign only: `git show 317b961^:seed/plan-reviewer-design.md` (the old rationale, deleted in the teardown).

## Already ruled - do not relitigate

- Layering: seed/ = minimal always-on harness; sam-cc-setup plugin = agents + optional skills; marketplace = install-on-demand.
- Unified seed, NO flavors. Research assets wait in `cultivation/wip/research-assets/`.
- Sync: at most two canonical mechanisms - Copier forward (tag-driven), ONE unified reverse (absorbing template-sync + agent-sync + hub-ci). Engine parked in `reassess-bin/`.
- Models: session may be Fable 5; delegated workers use `claude-opus-4-8[1m]` at xhigh. Opus 5 is prohibited.
- Superpowers = brainstorming only. Ponytail is banned. `auto-activate` is not a real field; use `disable-model-invocation: true`.
- Commits authored by Samyak, no agent co-author trailer. Direct-to-main is the epoch norm; CI cannot pass on PRs until step 6.

## Work queue

1. STRUCTURE DESIGN. Use the brainstorming skill with Samyak, then write the target tree for seed/ (files, hooks, rules, settings) and sam-cc-setup (agents, skills). Apply the per-line removal test to everything that survives. Get the design plan adversarially reviewed before executing (fresh-context reviewer, plan + criteria only, no author reasoning).
2. PLAN-REVIEWER MERGE. One blind review unit replacing seed rewrite-plan-reviewer.md + sam-cc-setup plan-reviewer.md + elegance-reviewer.md. Lands in sam-cc-setup. FIRST ASK Samyak for the reference plan-review agents he found online; fold them in.
3. CORE REWRITES. CLAUDE.md.jinja (purpose + gotchas + routing table, under 200 lines), AGENTS.md.jinja (official contract: concatenated root-down, 32 KiB cap, all Codex-side prose lives here), known-issues rule (drop dead-machinery entries), context-md-anatomy rule (anatomy + skip-column only).
4. CODEX FIXES. Rename seed/.codex/reassess-hooks.json to hooks.json; delete the inert `agents.max_depth` key; fix the two dangling config refs (memory-server.sh, .agents/skills/agent-team); document the trust gate in bootstrap output; decide whether to ship .agents/skills/.
5. SYNC CONSOLIDATION. Design the one reverse mechanism; then rule each reassess-bin/ script: verify-template.sh (rewrite as thin wrapper; `claude plugin validate` refuses symlinked .claude), release.sh (keep), ip-sweep set (keep), spike-probes (already ruled remove), agent-sync engine (absorb or retire per the design).
6. FINISH. Drop remaining reassess-/rewrite- prefixes as each verdict executes; slim-audit meta-improvement/helpers/business-process bundles; rewrite test.yml; run the rewritten verify-template; tag a release via release.sh.

## Verification

- After step 1: design doc committed to docs/specs/, reviewed verdict recorded.
- After steps 3-5: `git grep -n reassess- -- seed/` shrinks to zero; `bash -n` on every shipped hook; settings.json validates; a scratch `copier copy` from the local repo renders without errors.
- After step 6: CI green on a real PR, tag pushed, smoke-test `uvx copier copy --trust gh:samyakjhaveri/loam` against the NEW tag.

## Standing reminders (raise with Samyak when relevant)

- Wire align-prompt (sam-cc-setup) into a workflow or hook for automatic use.
- Source external plugins, MCPs, and skills from other repos and online later.

## Known traps

- docs/plans/ is GITIGNORED; session deliverables go to docs/specs/.
- The stop-verify-gate Stop hook is live again; it blocks turn-end on diff --check / ruff / bash -n failures in changed files.
- Subagents sometimes drop their final chat message; have every worker write its deliverable to a file first, and re-prompt any worker that returns empty.
- Copier resolves TAGS, not HEAD; do not tag until verify passes.
