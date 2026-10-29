# How we use pstack

pstack is poteto's skill pack (the `pstack@cursor-plugins` Claude Code plugin).
This page says how Samyak's hosts use it.
The full map of skills is `docs/SKILLS.md`; the rulings are in `docs/RULES.md`.
`<pstack>` below is the enabled plugin folder: `jq -r '.plugins["pstack@cursor-plugins"][0].installPath' ~/.claude/plugins/installed_plugins.json`.

Installed: pstack 0.15.36 (updated 2026-10-27).
The five short principle cards (laziness, context window, encode lessons, design space, migrate callers) stay as the author wrote them: she cut them on purpose and tested the cuts (owner ruling 2026-10-27).

## The one fact that shapes everything

pstack ships every skill with `disable-model-invocation: true` (only `setup-pstack` is model-invocable).
So Claude never sees a pstack skill in its skill list, and the Skill tool refuses it.
pstack's own Claude Code adapter (`<pstack>/docs/harness/claude-code.md`) gives the way around it: an agent reads `<pstack>/skills/<name>/SKILL.md` by path and follows it.
We use exactly that (owner choice C, 2026-10-27).
There are no copies in `~/.claude/skills/`, so a pstack update reaches every agent with nothing to re-run.

## Who runs what

| Who | How | Which skills |
|-----|-----|--------------|
| `worker` agent | reads by path, from the index in `~/.claude/agents/worker.md`, grouped by stage (understand, shape, build, debug, measure, review, finish), when the brief names a skill or the work reaches its row | `how`, `why`, `tdd`, `blast-radius`, `interrogate`, `benchmark-checklist`, `show-me-your-work`, `maintain-formal-verification-skill`, 15 principles |
| `scout` agent | reads by path, index in `~/.claude/agents/scout.md`; never edits | `how`, `why`, `blast-radius`, `principle-explain-the-number` |
| Lead session | never runs pstack inline; names the skill in a worker's brief | none |
| Samyak | types `/pstack:<name>` | everything else, below |

A worker has the Agent tool (proof run 2026-10-27), so it runs the fan-out skills in full.
A scout has none, so it runs `how` or `why` as their single explainer or investigator itself.

## What Samyak types, and when

- `/pstack:poteto-mode`: only for a contested design, concurrency, or a cross-cutting change (ruling 2026-10-19; pilot cost 1.9x with no quality gain on small work, #236).
  The author says the same: "Save `/poteto-mode` for work that needs rigor. A small, obvious edit doesn't" (`<pstack>/docs/guide/01-setup.md:52`).
  Give it a goal and a pass/fail check; it picks a playbook and keeps skipped steps visible as `skip: <reason>`.
  Our limit (ruling 2026-10-27): it may push a branch and open a PR, never merge.
  Its own playbooks open PRs ready for review and merge only under "land the stack" or Autopilot-full, so never ask it for those.
- `/pstack:figure-it-out`: a large or step-away job with no fitting playbook; it designs one and logs decisions.
- `/pstack:architect` and `/pstack:arena`: a design worth competing sketches; arena runs N candidates and grafts the best parts into one.
- `/pstack:swarm`: coverage or a race across parallel workers, not design. In Claude Code its cloud workers become local worktrees on the session model.
- `/pstack:sharpen`, `/pstack:in-your-own-words`: deepen or restate a request before work starts.
- `/pstack:teach`, `/pstack:how`, `/pstack:why`: an explanation for Samyak, with the full subagent fan-out.
- `/pstack:interrogate`: a multi-model review of a diff you do not trust; use it on a diff, not an abstract plan.
- `/pstack:unslop`, `/pstack:technical-writing`, `/pstack:no-comments`: clean prose or comments.
- `/pstack:reflect`, `/pstack:correct`: after a session, turn repeated mistakes into structure (architecture, then types or lint, then tests, docs last).
- `/pstack:ketchup`, `/pstack:ketchup-video`, `/pstack:bro`: catch up (the video version adds subtitled slides), or say the last message plainly.
- `/pstack:statechart`: check a TLA+ model of a flow and draw it as a statechart, or show a bug as a path through states.
- `/pstack:create-verification-skill`, `/pstack:create-formal-verification-skill`, `/pstack:maintain-verification-skill`: a project's proof skills.

## Not used

- `recall`: parked by the owner (2026-10-27); `catchup` and `ketchup` cover it.
- `automate-me`: its authoring step is Cursor's built-in `create-skill`, which the adapter does not map.
- `make-bot-ui`: built on Cursor Automations and Grok bot webhooks, which Claude Code lacks.
They stay in the plugin, user-only, out of every agent index, so Claude never starts them.
Deleting them from the plugin cache would come back with the next pstack update.

## Settings

- Models per role: `~/.claude/rules/pstack-models.md`, every role on Opus 5.5 at high or xhigh.
  Edit it by hand; a `/pstack:setup-pstack` re-run reverts effort-only changes, and its `unlimited` budget puts Opus at max, which our never-max ruling forbids.
- Non-Claude models in pstack's default panels (Grok, GPT) map to the session model in Claude Code, so a panel loses model-family diversity; Codex is our second family (step 3).

## Pitfalls the author lists

From `<pstack>/docs/guide/10-recipes-and-pitfalls.md:163-176`:
do not list skills in the prompt; give a finish condition that can pass or fail (a duration is not one); do not lead with your theory of the cause; do not take the first design; review a diff, not a plan; give each parallel agent its own worktree; do not loop before you trust the loop; vet a number before you trust it; do not accept every review comment; a green build is not proof.

## When pstack updates

Nothing to re-run: `installPath` moves to the new version.
Check after an update that the adapter still says to read skills by path, and that the agent indexes still name skills that exist:
`P=$(jq -r '.plugins["pstack@cursor-plugins"][0].installPath' ~/.claude/plugins/installed_plugins.json); for s in $(grep -oE '`[a-z-]+` \|$' ~/.claude/agents/worker.md | cut -d'`' -f2); do test -f "$P/skills/$s/SKILL.md" || echo "missing $s"; done`
