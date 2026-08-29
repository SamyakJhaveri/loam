# Loam rebuild - structure design (target tree)

> Written 2026-08-29 in the rebuild design session (work-queue step 1).
> Review verdict: APPROVE_WITH_CHANGES from BOTH blind reviewers (plan-reviewer: 11 findings; elegance-reviewer: 12 findings), all accepted findings folded in below.
> Review records: rebuild-structure-design-review.md (correctness, cited [P-n]) and rebuild-structure-design-review-elegance.md (elegance, cited [E-n]).
> All three FLAG items (MCP cut, baseline-agent cut, clangd cut) were CONFIRMED by Samyak on 2026-08-29; the design below is final.
> Sources cited as: [CTX Pn] = docs/specs/rebuild-research/research-context-rules.md; [CC] = research-cc-docs.md; [CDX] = research-codex-docs.md; [N-xxxx] = docs/specs/cliefnotes-wisdom.md norm ids; [R-n] = ledger ruling n; [D-n] = session decision n.

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
- D-2. Marketplace: remove planning-with-files, ui-ux-pro-max, understand-anything (unused).
- D-3. Codex skills: ship `.agents/skills/` with one starter skill (the only shared-asset location between harnesses [CDX §2.6]).
- D-4. Plugin agents: aggressive slim; cut agents superseded by native /code-review, /simplify, /security-review [CC §8].
- D-5. Catchup: keep ONE copy total.
  Canonical file in `seed/.agents/skills/catchup/SKILL.md` (content: the slimmed plugin version, which targets current Claude models).
  Claude Code reads it through a symlink `seed/.claude/skills/catchup`.
  The plugin's catchup skill is removed.
- D-6. Prose layout ("Approach A - folded seed"): the gotchas fold INTO the always-loaded prose layer.
  Consequence: the Claude-side post-compact-recovery hook is deleted.
  Claude Code natively re-reads and re-injects the project-root CLAUDE.md (with its imports) after compaction, and re-injecting rules was that hook's only job [CC §2].
  Review addendum [P-sound] [E10]: the hook never fired anyway - it was wired as `PostToolUse` matcher `Compact`, which is not a real event/matcher pair - so deletion has provably zero behavioral delta, and open assumption 2 is CLOSED, not carried.

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
  AGENTS.md.jinja            REWRITE   the ONE prose home; gutted to <40 lines [E1][E2]
  CLAUDE.md.jinja            REWRITE   opens with @AGENTS.md import + Claude-only content [E1]
  README.md.jinja            KEEP
  pyproject.toml.jinja       KEEP
  .gitignore.jinja           KEEP
  .copier-answers.yml.jinja  KEEP
  _gh_setup.sh               KEEP
  .claude/
    settings.json            EDIT      see settings verdicts below
    settings.local.json.template KEEP
    hooks/bash-audit-log.sh          KEEP
    hooks/concurrent-checkout-guard.sh KEEP
    hooks/stop-verify-gate.sh        KEEP
    skills/catchup             CHECKED-IN symlink -> ../../.agents/skills/catchup [E7]
  .agents/
    skills/catchup/SKILL.md  NEW       canonical catchup, both harnesses
  .codex/
    config.toml              FIX       defects below
    rules/default.rules      RENAME    from reassess-default.rules
bin/                          repopulated from reassess-bin/
  verify-template.sh         REWRITE   two checks [E6]
  release.sh                 EDIT      remove the hub-ci.sh call at line 86 [P2]
  lib.sh                     KEEP      release.sh:20 sources it [P2]
  ip-sweep.sh                EDIT      missing terms file becomes FATAL under IP_SWEEP_STRICT=1 [P8]
  check-own-synthesis.py     KEEP
  .ip-terms.example          KEEP      moves with ip-sweep.sh [P8][E11]
.github/workflows/
  test.yml                   REWRITE   PR-only, runs bin/verify-template.sh
  release.yml                KEEP      re-verify path after rewrite
```

Deleted outright (with the criterion that fires):

| Asset | Criterion |
|---|---|
| seed/.claude/hooks/post-compact-recovery.sh | native supersession [CTX P18]; never fired anyway [E10]; see D-6 |
| seed/.claude/rules/reassess-rewrite-known-issues.md | folded into the prose layer [D-6]; one home [CTX P4] |
| seed/.claude/rules/reassess-context-md-anatomy.md | one home: the plugin scaffold-context skill inlines the anatomy [CTX P7]; rare need fails the demotion test [CTX P6] |
| seed/.claude/rules/architecture.md | 51 lines of headings and TBD placeholders; removing an empty form cannot cause mistakes [CTX P10]; names no repeated failure [CTX P24]; injects TBD noise at the highest-attention moment [CTX P25] [E3]. `rules/` goes to ZERO files and the directory is removed. |
| seed/.claude/skills/reassess-template-sync/ | follows engine retirement [D-1] |
| seed/.claude/agents/rewrite-plan-reviewer.md | merged review unit lands in sam-cc-setup [R-2] |
| seed/.claude/audit.log, seed/.DS_Store | stray artifacts in the tree [E11] |
| seed/.codex/reassess-hooks.json + seed/.codex/hooks/ | DELETE, do NOT rename. Renaming would activate 4 dangling handlers (pre-tool-policy.py, post-tool-policy.py, session-start.sh, stop-verify-gate.sh - none ship) [P1][E4]. The one real hook (post-compact-recovery.sh) would print only git root + branch after this rebuild (its known-issues and results/ branches go dead), which is context rent, not recovery [E4][P7]. Codex hooks return when a real hook is written [CTX P24]. |
| seed/.codex/agents/, seed/.codex/mcp/ | empty dirs; mcp/ is the dangling target of the deleted memory server block [E11] |
| seed/_research/ (empty skeleton dirs) | flavor retired [R-4] [E11] |
| seed/.mcp.json.jinja | see MCP verdicts below [E5] |
| reassess-bin/: agent-sync.sh, agent-sync-scan.sh, agent-sync-prune.sh, agent-sync-safe-io.py, agent-sync-tests/, template-sync.sh, hub-ci.sh | [D-1]; plugin path supersedes file-sync [CTX P18] |
| reassess-bin/spike-probes.sh | spike done 2026-07-19 [ledger] |
| reassess-bin/lint-skill-descriptions.sh | NOT absorbed after all: a 4 KB semantic linter guarding one shipped skill fails [CTX P23]; the real semantic gap (frontmatter parses but lacks `name`) is a one-line grep inside verify-template.sh [E6] |
| reassess-bin/test-verify-template.sh | written against the old script [CTX P23] |
| reassess-bin/__pycache__/ | build artifact [E11] |
| cultivation/marketplace/planning-with-files, ui-ux-pro-max, understand-anything | unused [D-2] [CTX P24] |

Unchanged, verdict recorded [E11]: `cultivation/wip/research-assets/` stays parked per [R-4]; it is re-judged asset-by-asset when something in it is actually wanted [CTX P24].

## Asset detail

### One prose home: AGENTS.md.jinja + @AGENTS.md import [E1][E2][P9]

The reviewed draft kept two hand-maintained prose homes with a "the two must agree" clause.
Both reviewers flagged this as the exact drift failure [CTX P4] names.
Adopted shape:

- `AGENTS.md.jinja` is the ONE home for shared prose.
  Codex reads it unconditionally (no trust gate) [CDX §4].
  Gutted per [E2]: the Karpathy behavioral sections, the security block, the scalability block, and the model-selection table are DELETED as restated general competence [CTX P3, P11]; roughly an 80% cut, matching the measured-neutral precedent [CTX P2].
  What remains, target under 40 lines: project purpose, the harness-agnostic gotchas (Copier resolves tags not HEAD + `--trust`; case-insensitive repo-wide verification greps; count skills by SKILL.md; YAML colons in descriptions), the project-conventions fill-in section, and one line documenting the Codex trust gate for the `.codex/` layer [CDX §2.2].
- `CLAUDE.md.jinja` opens with a literal `@AGENTS.md` import line [CC §1: documented bridge; imports are expanded at load and on the post-compact re-read, so D-6 durability holds].
  Below the import: Claude-only content, under 100 lines total - the environment/commands section, the Claude-specific gotchas (hooks receive JSON on stdin; `paths:` fires on Read not Write; `disable-model-invocation: true` is the real tiering field; hook event/matcher names are exact strings and a wrong name fails silently [E10]), and the routing table (`File | Read when`) [N-0029] including a row for the scaffold-context skill.
  No directive may appear in both files.

### seed/.claude/settings.json verdicts [E9]

| Item | Verdict |
|---|---|
| PostToolUse `Compact` -> post-compact-recovery.sh | DELETE (never fired [E10]) |
| PostToolUse Edit/Write ruff auto-fix | KEEP |
| PreToolUse bash-audit-log, concurrent-checkout-guard | KEEP [R] |
| Stop -> stop-verify-gate.sh | KEEP [R-6] |
| model `claude-opus-4-8[1m]` | KEEP [R] |
| `enabledPlugins.pyright-lsp` | KEEP (seed ships pyproject.toml; Python-first) |
| `enabledPlugins.clangd-lsp` | DELETE (confirmed) + delete the CLAUDE.md paragraph explaining its false positives [CTX P24] [E9] |
| `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | DELETE (speculative experimental flag in a template default [CTX P24]) |
| permissions allow/deny/ask lists | KEEP, minus `mcp__sequential-thinking` (allow) and `mcp__drawio` (ask) which follow the MCP verdicts below; the read-only Bash allowlist is deliberate policy |
| skillOverrides | NOT ADDED (one shipped skill, nothing to tier) |

### seed/.agents/skills/catchup/ + checked-in symlink [E7][P3][P4][P5]

- Canonical `SKILL.md`: the plugin's slimmed catchup content, ported, then checked against the six-field portable frontmatter contract [CC §3 portability].
- The symlink `seed/.claude/skills/catchup -> ../../.agents/skills/catchup` IS checked into the template, and `_preserve_symlinks: true` is added to copier.yml so Copier renders it as a symlink.
  This deletes the previously-planned `_tasks` step, its idempotency guard, and open assumption 3 [E7].
  Committing the symlink is safe for validation because `claude plugin validate` simply does not follow it; the canonical directory is validated directly (see verify-template) [P3][P11].
  Execution step 0 verifies `_preserve_symlinks` against the installed Copier version; fallback if unsupported: a `_tasks` step `[ -e X ] || [ -L X ] || ln -s ...` ordered BEFORE the git-init task [P4][P5].
- The plugin's `skills/catchup/` is removed [D-5].

### seed/.codex/ [P1][E4]

| Change | Grounds |
|---|---|
| Delete `[agents] max_depth = 1` | not a documented key [CDX defect 2] |
| Rename `max_threads` -> `max_concurrent_threads_per_session` | legacy alias [CDX §2.4] |
| Delete the `[mcp_servers.memory]` block | dangling script ref [CDX defect 3]; also superseded by native auto memory [CTX P8] |
| Mirror the surviving MCP verdicts below in config.toml | one policy, both harnesses |
| Fix the `[features] multi_agent` comment | references `.agents/skills/agent-team`, which does not ship [CDX defect 3] |
| DELETE `reassess-hooks.json` and `hooks/` entirely | see deletion table [P1][E4] |
| Rename `rules/reassess-default.rules` -> `rules/default.rules` | matches the documented example; verify discovery with `codex execpolicy check --rules seed/.codex/rules/default.rules` [CDX §5] |

Resulting `.codex/` layer: `config.toml` + `rules/default.rules`. Every file real.

### MCP servers (was .mcp.json.jinja) [E5]

| Server | Verdict |
|---|---|
| memory | DELETE (native auto memory [CC §1] [CTX P8]) |
| sequential-thinking | DELETE (reasoning scratchpad wrapped around a Claude 5 harness [CTX P18]) |
| codegraphcontext, semble, drawio | DELETE from the seed default (confirmed). Nothing names the repeated failure that makes a generic day-one project need a code graph, semantic search, and a diagram editor [CTX P24]; they are Samyak's personal stack and belong in his user-level config, not the template. |

With all five gone, `.mcp.json.jinja` is deleted and the two MCP permission entries in settings.json go with it.

### copier.yml (edit)

1. Drop the dir-creation `_tasks` step (archive, meeting_notes, results, submission_docs, ...): research-flavored scaffolding, flavor retired [R-4] [CTX P24].
2. Add `_preserve_symlinks: true` (verified in execution step 0) [E7].
3. Keep the git-init, GitHub-setup, and `rm -f _gh_setup.sh` tasks unchanged [P5].

### bin/verify-template.sh (rewrite target) [E6][P3]

Two checks, evidence on failure, no silent caps [CTX P20]:

1. Scratch `copier copy --trust` from the local worktree into a temp dir; assert the render succeeds AND `.claude/skills/catchup` in the render is a symlink resolving to the canonical skill.
2. `claude plugin validate` over `seed/.claude`, `seed/.agents/skills`, and each marketplace bundle (real directories only - the tool refuses a symlinked `.claude` and does not follow symlinks [CC §6]), plus a one-line grep asserting every SKILL.md frontmatter carries `name:` (the one semantic gap the native tool has).
   When the `claude` CLI is absent (CI), this check prints a visible SKIPPED line; CI therefore honestly verifies check 1 only.

### bin/release.sh (edit) [P2][P8]

- Remove the `hub-ci.sh` invocation (line 86); hub-ci is deleted under D-1.
- `lib.sh` stays (sourced at line 20), surviving solely for release.sh.
- `ip-sweep.sh`: change the missing-terms-file branch from WARN+skip to FATAL when `IP_SWEEP_STRICT=1`, so a release cannot pass its IP gate having swept nothing [CTX P20]. `.ip-terms.example` and the gitignored `.ip-terms` move to `bin/` with the script (its hardcoded `bin/` paths become correct again).

### CI

- `test.yml`: PR-only trigger stays; steps become checkout, install copier, run `bin/verify-template.sh`. The agent-sync test step is deleted [D-1].
- `release.yml`: keep; re-verify after the wrapper rewrite.

### cultivation/marketplace/sam-cc-setup (plugin layer)

Agents - survivors (5 now, 6 after step 2):

| Agent | Why it stays |
|---|---|
| build-validator | no native build-health check |
| code-architect | pre-change architecture review, no native equivalent |
| consistency-checker | docs-vs-code drift, explicitly not bundled [CC §10]; gets the [CTX P22] bounded-findings treatment during the step 2 rewrite pass |
| read-only | zero-blast-radius investigator pattern |
| test-synthesizer | throwaway test scripts, no native equivalent |
| (step 2) merged plan-reviewer | adversarial PLAN review has no bundled equivalent [CC §8] |

Agents - removed (8):

| Agent | Superseded by / criterion |
|---|---|
| diff-reviewer | native /code-review [CC §8] |
| code-simplifier | native /simplify [CC §8] |
| self-critic | native /code-review; unbounded critic [CTX P22] |
| security-scanner | native /security-review |
| plan-reviewer, elegance-reviewer | absorbed into the merged unit [R-2] |
| verify-app, regression-checker | both key off `.claude/baselines.json`, which the seed never ships; overlapping descriptions [CTX P14]; in every fresh project they can only report NO-BASELINE [CTX P24] [E8]. Cut confirmed. |

Plugin cleanup (the REAL dangling references [P6]):

- Remove `skills/catchup/` [D-5].
- `workflows/plan-review-fanout.js`: rebuilt in step 2 against the merged reviewer (it is built on the old plan-reviewer checklist and agent roster).
- `skills/elegance-review/SKILL.md` and `skills/plan-review-invoke/SKILL.md`: redesigned WITH the merged reviewer in step 2 (expected outcome: one invoke skill).
- `README.md`: agent roster updated to the survivor list.
- The `validate/` skill needs NO rewire (it names no agents); it is left untouched.

### cultivation/marketplace (bundles)

- Keep: sam-cc-setup, sam-superpowers (brainstorming-only [R]), impeccable [R].
- Slim-audit in step 6: meta-improvement, helpers, business-process [CTX P14].
- Delete now: planning-with-files, ui-ux-pro-max, understand-anything [D-2].

### docs/

- Rewrite the stale docs once, against the rebuilt tree, in step 6 [ledger].
- Move the pre-teardown specs (NINE files, not eight) from `docs/specs/` to `_archive/`, EXCEPT `cliefnotes-wisdom.md`, which stays in docs/specs/ because it is the resolution target of the `[N-xxxx]` citations in the rebuild documents [P10].

## Considered and deferred

- Shipping `seed/.claude/` itself as a plugin instead of Copier-rendered files [E12].
  It would give in-place updates and dissolve the symlink workarounds, but settings.json (model, permissions, env) is not plugin-shippable, so Copier remains necessary; a hybrid is a scope change beyond this rebuild.
  Recorded so the next rebuild does not re-derive it.

## Open assumptions

1. The plugin scaffold-context skill's inlined CONTEXT.md anatomy is current enough to be the anatomy's one home. Checked during execution; if stale, the slimmed anatomy is folded into that skill.
2. CLOSED [E10]: the deleted compact hook never fired, so deleting it changes nothing.
3. CLOSED [E7]: replaced by `_preserve_symlinks: true`, verified in execution step 0 with the documented fallback.
4. Dropping the dir-creation task does not break existing seeded projects (tasks do not remove existing dirs; confirmed sound by review [E-sound]).
5. Removing plugin agents/skills changes behavior in Samyak's other projects using the global plugin; accepted under D-4/D-5.

## Execution order (work-queue mapping)

0. Verify `_preserve_symlinks` support in the installed Copier; verify `codex execpolicy check` accepts `default.rules`.
1. This document reviewed and folded (DONE) and confirmed by Samyak (FLAG items).
2. Step 2: merged plan-reviewer + fanout workflow + invoke skill (after Samyak provides the reference agents).
3. Steps 3-4: prose rewrites (AGENTS.md.jinja gut + @AGENTS.md import in CLAUDE.md.jinja), settings edits, catchup port + symlink, Codex fixes, MCP deletions.
4. Step 5: bin/ repopulation (verify-template rewrite, release.sh + ip-sweep edits).
5. Step 6: marketplace deletions and slim-audit, CI rewrite, prefix drops, docs, release.
