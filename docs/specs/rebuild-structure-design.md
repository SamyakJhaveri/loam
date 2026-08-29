# Loam rebuild - structure design (target tree)

> Written 2026-08-29 in the rebuild design session (work-queue step 1).
> Review verdict: PENDING blind review.
> Sources cited as: [CTX Pn] = docs/specs/rebuild-research/research-context-rules.md; [CC] = research-cc-docs.md; [CDX] = research-codex-docs.md; [N-xxxx] = docs/specs/cliefnotes-wisdom.md norm ids; [R-n] = ledger ruling n in docs/specs/rebuild-ledger.md; [D-n] = session decision n below.

## Scope

This document fixes the target tree for the rebuilt Loam template: `seed/`, `bin/`, CI, and the `cultivation/marketplace` layer.
It records a verdict for every asset that exists today and every asset that is added.
Execution happens in work-queue steps 2-6; this document is their contract.
Ledger rulings [R-1..R-7] are settled inputs, not open questions.

## Session decisions (Samyak, 2026-08-29)

- D-1. Reverse sync: retire the agent-sync engine entirely.
  The sam-cc-setup plugin marketplace is the ONE reverse/distribution channel.
  Grounds: the engine earns its place only if the hub sync loop is exercised; it is not.
  The official trigger "a second repository needs the same setup -> package it as a plugin" points the same way [CC §6].
- D-2. Marketplace: remove planning-with-files, ui-ux-pro-max, understand-anything (unused; ledger left them "decide by usage").
- D-3. Codex skills: ship `.agents/skills/` with one starter skill (the only shared-asset location between harnesses [CDX §2.6]).
- D-4. Plugin agents: aggressive slim; cut agents superseded by native /code-review, /simplify, /security-review [CC §8].
- D-5. Catchup: keep ONE copy total.
  Canonical file in `seed/.agents/skills/catchup/SKILL.md` (content: the slimmed plugin version, which targets current Claude models).
  Claude Code reads it through a symlink `seed/.claude/skills/catchup`.
  The plugin's catchup skill is removed.
- D-6. Prose layout ("Approach A - folded seed"): the known-issues gotchas fold INTO `CLAUDE.md.jinja`.
  Consequence: the Claude-side post-compact-recovery hook is deleted, because Claude Code natively re-reads and re-injects the project-root CLAUDE.md after compaction, and re-injecting rules was that hook's only job [CC §2, "Compaction behavior"].

## Design rules applied

1. Burden of proof is on keeping; default to delete [CTX P2].
2. One directive, one home [CTX P4, P7] [N-0058].
3. Must-hold-every-time -> hook; judgement -> prose, once [CTX P16].
4. Prefer a native feature over custom machinery that imitates it [CTX P18] [CC §10].
5. Always-loaded assets pay rent in EVERY subagent, so the always-on layer is priced highest [CC §4] [CTX P25].

---

## Target tree

```
seed/
  CLAUDE.md.jinja            REWRITE   purpose + gotchas + routing, <200 lines
  AGENTS.md.jinja            REWRITE   Codex-side prose home, <32 KiB
  README.md.jinja            KEEP
  pyproject.toml.jinja       KEEP
  .gitignore.jinja           KEEP
  .mcp.json.jinja            KEEP
  .copier-answers.yml.jinja  KEEP
  _gh_setup.sh               KEEP
  .claude/
    settings.json            EDIT      drop post-compact hook wiring
    settings.local.json.template KEEP
    hooks/bash-audit-log.sh          KEEP
    hooks/concurrent-checkout-guard.sh KEEP
    hooks/stop-verify-gate.sh        KEEP
    rules/architecture.md            KEEP  (path-scoped skeleton)
    skills/catchup -> ../../.agents/skills/catchup   (symlink, made by copier task)
  .agents/
    skills/catchup/SKILL.md  NEW       canonical catchup, both harnesses
  .codex/
    config.toml              FIX       4 defects (below)
    hooks.json               RENAME    from reassess-hooks.json
    hooks/post-compact-recovery.sh KEEP
    rules/default.rules      RENAME    from reassess-default.rules
bin/                          repopulated from reassess-bin/
  verify-template.sh         REWRITE   thin wrapper (below)
  release.sh                 KEEP
  ip-sweep.sh                KEEP
  check-own-synthesis.py     KEEP
.github/workflows/
  test.yml                   REWRITE   PR-only, runs bin/verify-template.sh
  release.yml                KEEP      re-verify path after rewrite
```

Deleted outright (with the criterion that fires):

| Asset | Criterion |
|---|---|
| seed/.claude/hooks/post-compact-recovery.sh | native supersession [CTX P18]; see D-6 |
| seed/.claude/rules/reassess-rewrite-known-issues.md | folded into CLAUDE.md.jinja [D-6]; one home [CTX P4] |
| seed/.claude/rules/reassess-context-md-anatomy.md | one home: the plugin scaffold-context skill inlines the anatomy [CTX P7]; a CONTEXT.md is authored rarely, so always-on loading fails the demotion test [CTX P6] |
| seed/.claude/skills/reassess-template-sync/ | follows engine retirement [D-1] |
| seed/.claude/agents/rewrite-plan-reviewer.md | merged review unit lands in sam-cc-setup [R-2]; one home [CTX P4] |
| reassess-bin/: agent-sync.sh, agent-sync-scan.sh, agent-sync-prune.sh, agent-sync-safe-io.py, agent-sync-tests/, template-sync.sh, hub-ci.sh | [D-1]; plugin path supersedes file-sync [CTX P18] |
| reassess-bin/spike-probes.sh | spike done 2026-07-19 [ledger] |
| reassess-bin/lint-skill-descriptions.sh | absorbed into the rewritten verify-template.sh [CTX P18] |
| reassess-bin/test-verify-template.sh | written against the old script; the thin wrapper gets a fresh smoke test only if it grows logic worth testing [CTX P23] |
| reassess-bin/lib.sh | delete unless a survivor still sources it (checked at execution) |
| cultivation/marketplace/planning-with-files, ui-ux-pro-max, understand-anything | unused [D-2] [CTX P24] |

## Asset detail

### CLAUDE.md.jinja (rewrite target)

Structure, in order, total under 200 lines [CC §1] [CTX P10]:

1. Purpose: what the project is, two or three sentences [N-0255].
2. Environment and commands: only what the model cannot guess [CC §1 include/exclude].
3. Gotchas: the surviving known-issues entries, rewritten.
   Dropped entries: everything about deleted machinery (validate sentinel, critique waves, old hook conventions) and the false `auto-activate` convention.
   The auto-activate lesson survives as one line naming the real field `disable-model-invocation: true` [CC §3].
   Kept lessons (rewritten to one short entry each): hooks receive JSON on stdin; YAML colons in skill descriptions; Copier resolves tags not HEAD (+ `--trust`); verification greps case-insensitive and repo-wide; count skills by SKILL.md; `paths:` fires on Read not Write.
4. Routing table (`File | Read when`) [N-0029, demo-grade] pointing at docs and skills on demand, including a row for the scaffold-context skill when authoring a CONTEXT.md.
5. NO restated general competence, NO file-by-file tree, at most one or two emphasis markers [CTX P10].

### AGENTS.md.jinja (rewrite target)

- Codex concatenates AGENTS.md root-down with a 32 KiB default cap; prose has no other Codex home [CDX §2.1, §2.5].
- Content: the project conventions and hard constraints that the Codex side needs, minus everything that only Claude Code enforces (hooks, plugin skills).
- Drop from the current file: the /validate sentinel machinery (retired), the Opus/Sonnet model-selection table (superseded by settings.json model pinning and rulings [R]), and any directive already living in CLAUDE.md.jinja for the Claude side when it would conflict rather than mirror [CTX P4].
  Where both harnesses need the same directive, AGENTS.md.jinja is the Codex home and CLAUDE.md.jinja the Claude home; the two must agree.
- Document the Codex trust gate in one line: the `.codex/` layer is inert until the project is trusted and hooks are reviewed via `/hooks` [CDX §2.2, defect 4].

### seed/.claude/settings.json (edit)

- Remove the `PostToolUse` matcher-`Compact` entry wiring post-compact-recovery.sh [D-6].
- Keep: model `claude-opus-4-8[1m]` [R], permissions lists, bash-audit-log (PreToolUse Bash), concurrent-checkout-guard (PreToolUse Bash|Edit|Write), inline ruff auto-fix (PostToolUse Edit|Write), stop-verify-gate (Stop) [R-6].
- No `skillOverrides`: the seed ships exactly one skill, so there is nothing to tier [CTX P23].

### seed/.claude/rules/architecture.md (keep)

Path-scoped to `src/**`, `lib/**`, `scripts/**`; costs nothing until source is touched [CC §2].
It is a fill-in skeleton for the seeded project's own architecture; that job cannot fold into CLAUDE.md without bloating it.

### seed/.agents/skills/catchup/ (new) + symlink

- Canonical `SKILL.md`: the plugin's slimmed catchup content, ported verbatim, then checked against the six-field portable frontmatter contract (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are the only fields legal outside Claude Code; anything else is a hard error in other consumers) [CC §3 portability].
- Claude Code reads it via symlink `seed/.claude/skills/catchup -> ../../.agents/skills/catchup` (skill dirs support symlinks [CC §3]).
- The symlink is NOT checked into the template; a guarded copier `_tasks` step creates it in the rendered project, avoiding Copier symlink-rendering differences.
- The plugin's `skills/catchup/` is removed [D-5]; one copy total.

### seed/.codex/ (fix + rename)

| Change | Grounds |
|---|---|
| Delete `[agents] max_depth = 1` | not a documented key; silently inert [CDX defect 2] |
| Rename `max_threads` to `max_concurrent_threads_per_session` | `max_threads` is a legacy alias [CDX §2.4] |
| Delete the `[mcp_servers.memory]` block | dangling: points at `.codex/mcp/memory-server.sh`, which does not ship [CDX defect 3] |
| Fix the `[features] multi_agent` comment | it references `.agents/skills/agent-team`, which does not ship [CDX defect 3]; the key itself stays (documented, harmless) |
| Rename `reassess-hooks.json` -> `hooks.json` | Codex discovers `hooks.json` only [CDX defect 1] |
| Rename `rules/reassess-default.rules` -> `rules/default.rules` | matches the documented example; filename auto-discovery is undocumented, so execution verifies with `codex execpolicy check --rules seed/.codex/rules/default.rules` [CDX §5] |
| Keep `hooks/post-compact-recovery.sh` | PostCompact is a documented Codex event and Codex documents no native re-injection [CDX §2.3] |

### copier.yml (edit)

1. Drop the dir-creation `_tasks` step (archive, meeting_notes, results, submission_docs, ...): it is research-flavored scaffolding and the research flavor is retired [R-4]; projects create their own directories [CTX P24].
2. Add a guarded symlink task, idempotent across `copier update`:
   `mkdir -p .claude/skills && [ -e .claude/skills/catchup ] || ln -s ../../.agents/skills/catchup .claude/skills/catchup`.
3. Keep the git-init and GitHub-setup tasks unchanged.

### bin/verify-template.sh (rewrite target)

Thin wrapper, three checks, evidence on failure [CTX P20]:

1. `claude plugin validate` on the REAL directories (`seed/.claude`, and each marketplace bundle) - the command refuses a symlinked `.claude`, which is exactly loam's root layout, so the wrapper must name `seed/.claude` directly [CC §6].
2. Scratch `copier copy --trust` from the local worktree into a temp dir; assert render succeeds and the `_tasks` symlink resolves.
3. The semantic skill-lint checks the native validator lacks (description quality, required `name`, colon quoting), absorbed from lint-skill-descriptions.sh [CC §10].

### CI

- `test.yml`: PR-only trigger stays; steps become checkout, install copier, run `bin/verify-template.sh`. The agent-sync test step is deleted [D-1]. Note: CI has no `claude` CLI; the wrapper must skip check 1 gracefully (with a visible SKIPPED line) when the CLI is absent, so CI still runs checks 2-3 honestly [CTX P20: no silent caps].
- `release.yml`: keep; it already runs `bin/verify-template.sh` on tag push; re-verify after the wrapper rewrite.

### cultivation/marketplace/sam-cc-setup (plugin layer)

Agents - survivors (7 now, 8 after step 2):

| Agent | Why it stays |
|---|---|
| build-validator | no native build-health check |
| code-architect | pre-change architecture review, no native equivalent |
| consistency-checker | docs-vs-code drift, explicitly not bundled [CC §10] |
| read-only | zero-blast-radius investigator pattern |
| regression-checker | baselines contract, no native equivalent |
| test-synthesizer | throwaway test scripts, no native equivalent |
| verify-app | evidence-based smoke run [CTX P20] |
| (step 2) merged plan-reviewer | adversarial PLAN review has no bundled equivalent [CC §8]; built in work-queue step 2 |

Agents - removed (6):

| Agent | Superseded by |
|---|---|
| diff-reviewer | native /code-review (background fork, effort-tunable, --fix) [CC §8] |
| code-simplifier | native /simplify [CC §8] |
| self-critic | native /code-review; also an unbounded critic [CTX P22] [R-ledger] |
| security-scanner | native /security-review |
| plan-reviewer | absorbed into the merged unit [R-2] |
| elegance-reviewer | absorbed into the merged unit [R-2] |

Skills:

- Remove `catchup/` [D-5].
- Rewire `validate/` waves to the surviving agents (references to removed agents must go).
- `plan-review-invoke/` and `elegance-review/` are redesigned WITH the merged reviewer in step 2 (expected outcome: one invoke skill).
- All other plugin skills are untouched this rebuild.

### cultivation/marketplace (bundles)

- Keep: sam-cc-setup, sam-superpowers (brainstorming-only [R]), impeccable [R].
- Slim-audit in step 6: meta-improvement, helpers, business-process (per-skill, listing-budget lens [CTX P14]).
- Delete now: planning-with-files, ui-ux-pro-max, understand-anything [D-2].

### docs/

- Rewrite the stale docs once, against the rebuilt tree, in step 6 (not incrementally) [ledger].
- Move the 8 pre-teardown specs from `docs/specs/` to `_archive/`.

## Open assumptions (for the blind review)

1. The plugin scaffold-context skill's inlined CONTEXT.md anatomy is current enough to be the anatomy's one home.
   If stale, the slimmed anatomy is folded into that skill during execution.
2. Claude Code's post-compact re-injection of root CLAUDE.md fully covers the gotchas' durability need (it does not cover always-on rules, which is why they fold in).
3. The copier `_tasks` symlink is safe across `copier update` with the `[ -e ]` guard.
4. Dropping the dir-creation task does not break any existing seeded project (tasks run only on copy/update; existing dirs are untouched).
5. Removing plugin agents/skills changes behavior in Samyak's other projects that use the global plugin; accepted under D-4/D-5 because native skills cover the cuts.

## Execution order (work-queue mapping)

1. This document reviewed and approved (step 1).
2. Step 2: merged plan-reviewer (after Samyak provides the reference agents).
3. Steps 3-4: core rewrites (CLAUDE.md.jinja, AGENTS.md.jinja, settings, catchup port) + Codex fixes.
4. Step 5: bin/ repopulation + verify-template rewrite.
5. Step 6: marketplace deletions and slim-audit, CI rewrite, prefix drops, docs, release.
