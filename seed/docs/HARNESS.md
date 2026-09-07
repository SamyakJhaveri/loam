# The harness: what it guards, and what it does not

## Safety, native only

Nothing parses your command text to decide safety, and no hook runs on a tool
matcher. Two native deny lists do the blocking.

- Claude Code, `.claude/settings.json` `permissions.deny`: `rm -rf` and its
  spellings (`-fr`, `-Rf`, `-r -f`, `-f -r`), `git push --force` / `-f` /
  `--force-with-lease` / `--force-if-includes`, `git reset --hard`,
  `git clean -f|-d|-x`, `git checkout -- .` / `git checkout .` /
  `git restore .`, `git stash clear|drop`, and read or edit of `.env*`.
  Deny applies in every permission mode, including bypassPermissions. Each
  entry is a literal prefix, so only the listed spellings block; see the
  accepted risks below.
- Codex, `.codex/rules/loam.rules`: the same families, one `prefix_rule` per
  spelling, `decision = "forbidden"`. Codex splits command chains itself.
- The Claude sandbox is on (`sandbox.enabled`), with `.env*` denied for read and
  write. `failIfUnavailable` is false, so a host without sandbox support runs
  unsandboxed; see the accepted risks below.
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

- `fable-session-brief.sh` (SessionStart, PostModelSwitch): prints the Fable
  judgment rules Claude Code does not inject, when the event names a Fable
  model; silent otherwise. It reads `model` on SessionStart and `to_model` on
  PostModelSwitch. Measured on Claude Code 2.1.263: a non-interactive
  `claude -p` startup payload carries no `model` field, so the brief does not
  fire there.
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

- Prose (`CLAUDE.md` plus `AGENTS.md`): 400 tokens. The skill listing and the
  session brief are separate always-on costs and are not inside that number.
- Skill listing: the two seed skills weigh 131 tokens, so a fresh project pays
  about 400 + 131 tokens before any work starts.
- In the Loam template repo the `sam-cc-setup` plugin listing weighs 448 tokens.
  That is the `LISTING_BUDGET` ratchet `bin/check` asserts. Lower it when the
  listing shrinks; never raise it without saying why.

## Accepted risks, stated rather than hidden

- Git recovers committed work only. A command that dodges the deny prefixes and
  destroys uncommitted or untracked files is unrecoverable.
- A deny entry matches a literal prefix, so a combined short flag is a different
  string and runs. Measured in a rendered project: `rm -rfv y` deleted `y/`, and
  `git clean -fdx` was allowed, while `rm -rf` and `rm -Rf` were denied. Codex
  behaves the same way: `codex execpolicy check` returns no decision for
  `rm -rfv` and `git clean -fdx`. Both deny lists cover the honest mistake, not
  a deliberate rewording.
- The `.env` deny rules do not stop a Python or Node subprocess opening the file.
  The sandbox filesystem deny is the real containment. It needs host support:
  on a Linux host without `socat`, Claude Code prints `Sandbox disabled` at
  startup, and `python3 -c "open('.env').read()"` then prints the file. Install
  the sandbox dependencies, or treat the deny list as the only file guard.
- Secrets typed into an ordinary source file are not caught locally.
- Test tampering and mutation coverage have no gate. Pull-request review owns
  test integrity.
- Editing any file under `.claude/` needs bypassPermissions mode. An unattended
  `dontAsk` agent cannot change its own harness.

## Owner global config, outside this project

The owner's `~/.claude/` files are personal and are not shipped by the template.
A global hook in `~/.claude/hooks/` repeats the "prefer targeted edits" rule for
every project on that machine, so the owner sees it twice; nobody else does.

## Measured cost, v2.3.0 to v3.0.0

Rendered-project rows, measured in a `copier copy` render of each version. The
repo-side rows (`bin/` size, parked plugin skills) are in the v3.0.0 pull
request, not here.

| Row | Before (v2.3.0) | After (v3.0.0) |
|---|---|---|
| Hooks shipped in `.claude/hooks/` | 15 | 2 |
| Hooks on a tool matcher | 11 | 0 |
| Hook events per Bash call | 7 (about 414 ms) | 0 (about 0 ms) |
| Hook runs per Edit or Write | 1 ruff run | 0 |
| Always-on prose bytes (`CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
| Check wall time, one script | 207 s (`bin/verify-template.sh`) | 5 s local, 7 s in CI |

Token figures anywhere in this file are byte counts divided by four, not a
tokenizer result.
