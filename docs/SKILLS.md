# Skill paths

The map of which skill, agent or workflow serves each kind of work on Samyak's hosts.
Adopted by the owner on 2026-10-27 (streamline brief, step 1).
Design page: https://claude.ai/artifact/8Mmrxpy8AqULkQgvwDDAdJ.
Evidence and per-skill decisions: `~/.local/state/loam/evidence/2026-10-25-consolidation/runs/skill-index/`.

## Three layers

- **Claude picks**: the lead sees the skill in its skill list and may load it unprompted.
- **Workers read**: a worker or scout reads a pstack `SKILL.md` from the enabled plugin folder, using the index in its agent file (pstack's own Claude Code method). The lead names the skill in the brief and never runs it inline.
- **You type**: a user-only slash command; Claude never starts it.

A skill stays in the lead's list only if Claude should pick it unprompted and no other listed skill fires on the same words.

## The eight paths

| Path | Claude picks | Workers read | You type |
|------|--------------|--------------|----------|
| 1. Intake | `catchup` | | `/sam-cc-setup:brief`, `/pstack:sharpen`, `/pstack:in-your-own-words`, `/mattpocock-skills:grill-with-docs`; too big for one session: `/pstack:figure-it-out` or `/mattpocock-skills:wayfinder` |
| 2. Understand | none; send a scout or worker | `how`, `why` | `/pstack:teach`, `/pstack:how`, `/pstack:why` |
| 3. Plan and design | `mattpocock-skills:codebase-design`, `:domain-modeling`, `:prototype` | | `/mattpocock-skills:to-spec` (only for a full spec first), `/mattpocock-skills:to-tickets`, `/sam-cc-setup:plan-review`, `/mattpocock-skills:improve-codebase-architecture`; contested design, concurrency or cross-cutting: `/pstack:poteto-mode` |
| 4. Build | a few lines inline, else one `worker`; `resolving-merge-conflicts`, `run`, `loop` | `tdd` (cheap test path only), the principles, `show-me-your-work` on long unattended runs | `/sam-cc-setup:run-spec` (spec with tickets), `bin/factory` (queued tickets), `/pstack:poteto-mode` (pushes a branch, never merges) |
| 5. Review | `code-review` (bugs), `simplify` (quality) | `interrogate`, `blast-radius` | `/sam-cc-setup:codex-review` (Codex second opinion on a diff), `/pstack:no-comments`; after a loop: the `lean-critic` agent |
| 6. Debug and measure | `mattpocock-skills:diagnosing-bugs` | `principle-fix-root-causes`, `principle-attack-the-premise`, `benchmark-checklist`, `principle-explain-the-number` | `/hypothesis-tree`, `/experiment-loop` |
| 7. Research | `mattpocock-skills:research` | | the `deep-research` workflow, the academic-research workflow (step 5), `/new-model-workflow` |
| 8. Write | `mattpocock-skills:writing-for-agents`; `artifact-design`, `artifact-diagramming`, `dataviz` | | `/pstack:technical-writing`, `/pstack:unslop` |

Side lanes.
Session: `/pstack:ketchup`, `/pstack:bro`, `/mattpocock-skills:wait-what`, `/pstack:show-me-your-work`.
Improve the harness: `/pstack:reflect`, `/pstack:correct`, `update-config`.

## Descriptions

Every description Loam or Samyak owns reads "Use when <trigger>. Not for <near case>: use <other>."
Third-party descriptions (Matt Pocock, Codex, pstack, built-ins) are not edited; only visibility changes.

## How visibility is controlled

- `skillOverrides` in `~/.claude/settings.json` works for user, project and synced skills.
  In Claude Code 2.1.312 it has no effect on third-party plugin skills, and neither do `Skill(...)` deny rules (three fresh `claude -p` listings, 2026-10-27).
- To make one plugin skill user-only, add `disable-model-invocation: true` to its frontmatter in the plugin cache.
  A plugin update replaces the cache and undoes it; re-add the line in the new version folder.
  Applied 2026-10-27: `mattpocock-skills:tdd` and `mattpocock-skills:code-review`.
- To hide a whole plugin, turn it off in `enabledPlugins`.
- pstack ships every skill user-only, and its author flag cannot be overridden.

## Codex

One way, set in step 3 (2026-10-28): a bare `codex exec` with sandbox, model, effort and prompt chosen per task.
The rule lives in the Codex line of `~/.claude/CLAUDE.md`; Claude may call it itself, for example for the read-only Codex review in `docs/RULES.md`.
The sandbox flag matters because `~/.codex/config.toml` defaults to a write-capable profile (`default_permissions = "loam-auto"`): a call without `-s read-only` can edit the checkout it runs in (tested 2026-10-28).
For a diff review you type `/sam-cc-setup:codex-review`: the same command plus a scope check, a blind intent paragraph and triage buckets.

The Codex plugin (`codex@openai-codex`) is off (owner decision 2026-10-28).
Its rescue agent told Claude to use it proactively, ran on Sonnet and wrote by default; it also put four skills in the lead's list and three hooks in every session, and was used in three sessions.
To turn it back on, set `enabledPlugins["codex@openai-codex"]` to `true` in `~/.claude/settings.json`.

## Open steps

Steps 2 (pstack by path, `docs/PSTACK.md`), 3 (Codex, above) and 4 (`/sam-cc-setup:run-spec`, parallel workers in worktrees) are done.

| Step | Change |
|------|--------|
| 5 | Academic-research workflow. |
| 6 | Try `anthropic-skills:setup-writing-style` for DistBench's paper (the global "no writing or voice skill" rule was removed for this trial, 2026-10-27). |
