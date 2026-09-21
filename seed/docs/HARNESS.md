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
| Ruleset call failed, or posted but did not read back as active (token scope, plan, or permissions) | None. Add it by hand in repo Settings, Rules. |
| No GitHub repo, or `gh` missing or unauthenticated | None. The branch is directly pushable. |

There is no `ask` rule on `git push`, on purpose: an unattended run must not stop
on a prompt.

## The hooks

None runs on a tool matcher; every hook fires on a lifecycle event
(SessionStart, SessionEnd, PreCompact, Stop, PostModelSwitch), so none adds
per-tool latency.

- `fable-session-brief.sh` (SessionStart, PostModelSwitch): prints the Fable
  judgment rules Claude Code does not inject, when the event names a Fable
  model; silent otherwise. It reads `model` on SessionStart and `to_model` on
  PostModelSwitch. Measured on Claude Code 2.1.263: a non-interactive
  `claude -p` startup payload carries no `model` field, so the brief does not
  fire there.
- `post-compact-reinject.sh` (SessionStart `compact`): re-injects the task after
  a compaction.
- `mem-capture.sh` (SessionEnd, PreCompact, Stop): copies the session transcript
  into `$LOAM_MEMSTORE/traces/<repo>/` and appends one `INDEX.md` line, reading
  the hook JSON with a single `python3` and no model call. It is idempotent on
  the transcript's sha256, so a repeat capture adds no file and no line. The
  `Stop` entry passes `--throttle 600`, so a burst of stops copies at most once
  per ten minutes.
- `mem-recall.sh` (SessionStart `startup|resume|clear`): prints the last five
  `INDEX.md` lines for this repo and the applicability rule to stdout, which
  Claude Code adds to the context; capped at 4000 bytes, silent when the store
  has no index for the repo.

Codex runs the same two scripts through `.codex/hooks.json`, which registers
`mem-capture.sh` on SessionEnd, PreCompact, and Stop (the Stop entry throttled)
and `mem-recall.sh` on SessionStart. The entries point at the `.claude/hooks/`
scripts; each reads `cwd` from the hook payload, so one copy serves both
harnesses and a session lands under the same repository key whichever one ran it.

`bin/memsearch` and `bin/mem-weekly.sh` are companion tools, not hooks.
`memsearch PATTERN` greps the trace store and the repo's `docs/` with ripgrep
(or `grep`) and cuts the output at 80 lines. `mem-weekly.sh` commits the store as
a git baseline and rewrites `reports/recurring-errors.md`; add its cron line by
hand, it is not installed:

    0 9 * * 0 <project>/bin/mem-weekly.sh

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
- Skill listing: the three seed skills weigh about 250 tokens (description
  bytes divided by four), so a fresh project pays about 400 + 250 tokens before
  any work starts.
- In the Loam template repo the `sam-cc-setup` plugin listing weighs 565 tokens.
  That is the `LISTING_BUDGET` ratchet `bin/check` asserts. Lower it when the
  listing shrinks; never raise it without saying why. Raised from 448 on
  2026-09-09 when `plan-review` became model-invocable, so its description
  now sits in the listing.
- Memory hooks: recall adds at most 4000 bytes at SessionStart, and the Stop
  capture runs one `python3` and one `cp` at most once per ten minutes.

## Accepted risks, stated rather than hidden

- Git recovers committed work only. A command that dodges the deny prefixes and
  destroys uncommitted or untracked files is unrecoverable.
- The `.env` deny rules do not stop a Python or Node subprocess opening the file.
  The sandbox filesystem deny is the real containment, where the host supports it.
- Secrets typed into an ordinary source file are not caught locally.
- A captured transcript holds everything typed in the session, pasted secrets
  included. The store under `LOAM_MEMSTORE` (default `~/memstore`) is per user,
  outside every repository, never rendered and never committed to the project;
  delete a trace file to forget it. The weekly baseline commit in the store covers
  reports and native-memory caches only; `traces/` is gitignored there, so a
  deleted transcript leaves no copy in git history.
- Codex runs a repository hook only after the user trusts the project's `.codex`
  layer and reviews the hook definition once (Codex keeps a hash of it in its
  hooks state, and an edit to `hooks.json` asks again), so a Codex session before
  that step captures nothing.
- Test tampering and mutation coverage have no gate. Pull-request review owns
  test integrity.
- Editing any file under `.claude/` needs bypassPermissions mode. An unattended
  `dontAsk` agent cannot change its own harness.

## Owner global config, outside this project

The owner's `~/.claude/` files are personal and are not shipped by the template.
A global hook in `~/.claude/hooks/` repeats the "prefer targeted edits" rule for
every project on that machine, so the owner sees it twice; nobody else does.

## Measured cost, v2.3.0 to v3.0.0

Rendered-project rows measured in a `copier copy` render of each version;
repo-side rows measured in the repo itself.

| Row | Before (v2.3.0) | After (v3.0.0) |
|---|---|---|
| Hooks shipped in `.claude/hooks/` | 15 | 2 |
| `PreToolUse` hook entries matching Bash | 7 | 0 |
| Hook runs per Edit or Write | 1 ruff run | 0 |
| Always-on prose bytes (`CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
| Check wall time, one script | 207 s (`bin/verify-template.sh`) | 5 s local, 7 s in CI |
| Seed hook and lib lines | 2309 | 71 |
| `bin/` plus `bin/tests/` lines | 11377 | 1525 |
| Marketplace skills shipped | 26 | 3 |

Token figures anywhere in this file are byte counts divided by four, not a
tokenizer result.

## Accepted risks measured in v3.0.0

- A deny entry matches a literal prefix, so a combined short flag is a different
  string and runs. Measured in a rendered project: `rm -rfv y` deleted `y/`, and
  `git clean -fdx -n` ran (dry run), while `rm -rf` and `rm -Rf` were denied. Codex
  agrees: `codex execpolicy check` returns no decision for either. Both deny
  lists cover the honest mistake, not a deliberate rewording.
- "Where the host supports it" is load-bearing. With `bwrap` and `socat` present
  the sandbox enforces: `python3 -c "open('.env').read()"` raises
  `PermissionError`, and a write to `/tmp` fails with `Read-only file system`.
  Drop `socat` and Claude Code prints `Sandbox disabled` at startup and runs
  unsandboxed, because `failIfUnavailable` is false, and both commands then
  succeed. Install the sandbox dependencies, or treat the deny list as the only
  file guard.
- Under the sandbox, git writes its credential lock outside the workspace, so
  `git ls-remote origin` prints `fatal: unable to get credential storage lock in
  1000 ms: Read-only file system` on stderr and still exits 0. The line is noise.
