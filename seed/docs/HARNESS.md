# The harness: what it guards, and what it does not

## Safety, native only

Nothing parses your command text to decide safety, and no hook runs on a tool
matcher. Two native deny lists do the blocking.

- Claude Code, `.claude/settings.json` `permissions.deny`: `rm -rf` and its
  spellings (`-fr`, `-Rf`, `-r -f`, `-f -r`), `git push --force` / `-f` /
  `--force-with-lease` / `--force-if-includes`, `git reset --hard`,
  `git clean -f|-d|-x`, `git checkout -- .` / `git checkout .` /
  `git restore .`, `git stash clear|drop`, and read or edit of `.env*`.
  Deny applies in every permission mode, including bypassPermissions.
- Codex, `.codex/rules/loam.rules`: the same families, one `prefix_rule` per
  spelling, `decision = "forbidden"`. Codex splits command chains itself.
- The Claude sandbox is on (`sandbox.enabled`), with `.env*` denied for read and
  write. `failIfUnavailable` is false, so a host without sandbox support still
  runs; the deny list is then the only file guard.
- `.codex/config.toml` denies `.env*` in the workspace and leaves network on.
  All of `.codex/` is inert until you mark this project trusted in Codex.

## Push guard, by case

When `github_repo` was answered, `_gh_setup.sh` posts a repository ruleset on the
default branch requiring a pull request and the `check` status, with no bypass
actors. Three cases, and the setup output says which one you got:

| Case | Guard on the default branch |
|---|---|
| Ruleset created | Direct push rejected; PR plus a green `check` required. |
| Ruleset call failed (token scope, plan, or permissions) | None. Add it by hand in repo Settings, Rules. |
| No GitHub repo, or `gh` missing or unauthenticated | None. The branch is directly pushable. |

There is no `ask` rule on `git push`, on purpose: an unattended run must not stop
on a prompt.

## The two hooks

Both are SessionStart-class, so they add no per-tool latency.

- `fable-session-brief.sh` (SessionStart, PostModelSwitch): prints five
  judgment rules Claude Code does not inject, plus a Fable-only paragraph when
  the event names a Fable model. The rules block is unconditional because no
  SessionStart payload names the model (measured on Claude Code 2.1.263); only
  PostModelSwitch carries `to_model`, so a session that starts on Fable and
  never switches sees the rules but not the Fable paragraph.
- `post-compact-reinject.sh` (SessionStart `compact`): re-injects the task after
  a compaction.

## The one check

`bin/check` runs ruff, shell syntax, whitespace, and pytest. The agent runs it by
choice; `.github/workflows/check.yml` runs the same script on every push and pull
request. Nothing else lints or tests.

## Always-on budget

`AGENTS.md` is the one prose home for agent guidance; Claude Code imports it
via `CLAUDE.md`, Codex reads it directly. Add a line to either file only if
removing it would cause a mistake.

- Prose (`CLAUDE.md` plus `AGENTS.md`) plus the unconditional part of
  `fable-session-brief.sh`: 400 tokens together. The skill listing is a separate
  always-on cost and is not inside that number.
- Skill listing: the two seed skills weigh 131 tokens, so a fresh project pays
  about 400 + 131 tokens before any work starts.
- In the Loam template repo the `sam-cc-setup` plugin listing weighs 448 tokens.
  That is the `LISTING_BUDGET` ratchet `bin/check` asserts. Lower it when the
  listing shrinks; never raise it without saying why.

## Accepted risks, stated rather than hidden

- Git recovers committed work only. A command that dodges the deny prefixes and
  destroys uncommitted or untracked files is unrecoverable.
- The `.env` deny rules do not stop a Python or Node subprocess opening the file.
  The sandbox filesystem deny is the real containment, where the host supports it.
- Secrets typed into an ordinary source file are not caught locally.
- Test tampering and mutation coverage have no gate. Pull-request review owns
  test integrity.
- Editing any file under `.claude/` needs bypassPermissions mode. An unattended
  `dontAsk` agent cannot change its own harness.

## Owner global config, outside this project

The owner's `~/.claude/` files are personal and are not shipped by the template;
the Fable "prefer targeted edits" rule is enforced there by a global hook in
`~/.claude/hooks/`, which is why this project ships no seed hook for it.
