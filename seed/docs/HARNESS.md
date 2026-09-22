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
- `mem-capture.sh` (SessionEnd, PreCompact, Stop): scrubs known secret shapes
  from the session transcript, stores it gzipped at
  `$LOAM_MEMSTORE/traces/<repo>/<date>-<sid8>.jsonl.gz`, and appends one
  `INDEX.md` line, with no model call. It is idempotent on the scrubbed content's
  sha256 (kept beside the trace as `<date>-<sid8>.sha`), so a repeat capture adds
  no file and no line. After a capture it links `<repo>/.loam/memory` to the
  store when that path is free. The `Stop` entry passes `--throttle 600`, so a
  burst of stops captures at most once per ten minutes. It then commits the store
  and, when an `origin` remote is set, pushes it in the background, so a second
  machine sees the trace; the hook never waits on the network.
- `mem-recall.sh` (SessionStart `startup|resume|clear`): prints a manifest to
  stdout, which Claude Code adds to the context. When an `origin` remote is set it
  first pulls the store (bounded to five seconds) so a line another machine
  committed shows up here. A `Loaded:` line names how many recent sessions, hint
  bullets, and handoffs it injected; a claimed handoff, the last five `INDEX.md`
  lines, and the newest hint bullets follow; a `Not loaded:` line names the notes
  and traces it did not open and points at `memsearch <pattern>` or
  `mem-inspect <session>` to reach them, and at the handoff path; a trust rule
  closes it, labelling every recalled item supported, contradicts, near-match, or
  insufficient. Capped at 4000 bytes, silent when the store has no index and no
  handoff for the repo.

Codex runs the same two scripts through `.codex/hooks.json`, which registers
`mem-capture.sh` on SessionEnd, PreCompact, and Stop (the Stop entry throttled)
and `mem-recall.sh` on SessionStart. The entries point at the `.claude/hooks/`
scripts; each reads `cwd` from the hook payload, so one copy serves both
harnesses and a session lands under the same repository key whichever one ran it.

`bin/memsearch`, `bin/mem-inspect`, and `bin/mem-weekly.sh` are companion tools,
not hooks. `memsearch PATTERN` greps the trace store (gzipped and plain traces
alike) and the repo's `docs/` with ripgrep (or `grep`/`zgrep`) and cuts the
output at 80 lines. `mem-inspect <session>` reads one captured trace by turn
instead of grepping the raw file: `--summary` lists the turns, `--span A:B`
prints a range, `--match RE` prints the turns whose text matches. `mem-weekly.sh`
deletes traces older than a year, rewrites `reports/recurring-errors.md` (error
lines normalized to a signature so runs differing only in a number collapse) and
`reports/counts.md` (capture, retrieval, and application counts), commits the
store as a git baseline with those reports included, then pulls and pushes the
store's remote when one is set; add its cron line by hand, it is not installed:

    0 9 * * 0 <project>/bin/mem-weekly.sh

## Sharing the store between machines

The store is a git repository, so a second machine can see what the first
learned by giving the store a remote. Use a machine you own; no third-party host
is involved.

1. On the machine that will hold the remote, create a bare repository:

        git init --bare -b main ~/memstore.git

2. On every machine, point the local store at it over an ssh alias (say
   `jhaveris`, the same alias `bin/runner` uses):

        git -C ~/memstore remote add origin jhaveris:memstore.git

   A store an older `mem-weekly.sh` created may sit on `master`; run
   `git -C ~/memstore branch -M main` once so `origin main` matches.

3. On a brand-new machine with no `~/memstore` yet, set `LOAM_MEMSTORE_REMOTE`
   to the same URL. The first capture then clones the shared store instead of
   starting empty, so the machine sees the shared history from its first session.

The remote holds scrubbed transcripts, the same content as the local store.
Keep it on a machine you own and never point it at a public host: a secret with
no recognizable shape can reach the store's history and the remote (see Accepted
risks). A capture commits and pushes in the background; recall pulls at
SessionStart and `mem-weekly.sh` pulls then pushes from cron. Every git call runs
with `GIT_TERMINAL_PROMPT=0`, and recall's pull is bounded to five seconds, so an
unreachable remote never blocks a session; it logs one line to
`reports/sync.log` and continues with the local store. Store files are
append-only, so a rebase does not conflict; on the rare conflict the hook logs
one line and leaves the working tree untouched.

### The handoff

To hand the next session a single instruction, write
`.loam/memory/handoff/<repo>.md` (the repo key is the name in the recall
manifest's heading). The next session on any machine or harness, in the same
repo, injects that file once under `## Handoff (claimed now)`, then archives it to
`.loam/memory/handoff/<repo>/archive/<date>-<sid8>.md` and never reads it again.
One writer per workstream, claimed once: it is not a shared last-writer-wins file.

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
  capture runs at most once per ten minutes. The scrub adds one regex pass over
  the transcript per capture. Recall waits at most five seconds for a pull from
  the store's remote; the capture's push runs in the background and never waits.

## Accepted risks, stated rather than hidden

- Git recovers committed work only. A command that dodges the deny prefixes and
  destroys uncommitted or untracked files is unrecoverable.
- The `.env` deny rules do not stop a Python or Node subprocess opening the file.
  The sandbox filesystem deny is the real containment, where the host supports it.
- Secrets typed into an ordinary source file are not caught locally.
- The capture scrubs known key shapes (API keys, Bearer and JWT tokens, PEM
  private-key blocks, URL credentials, and the like) before a transcript is
  stored; a secret with no recognizable shape can still be stored, so delete the
  trace to forget it. The store under `LOAM_MEMSTORE` (default `~/memstore`) is
  per user, outside every repository, never rendered and never committed to the
  project. The store is itself a git repository: `traces/` and `INDEX.md` are
  tracked and pushed to the store's own remote once the scrub has run over them,
  so the trace history and any configured remote hold scrubbed transcripts. A
  secret with no recognizable shape can therefore reach both the store's git
  history and the remote; forgetting a pushed trace means deleting the file,
  committing, and rewriting or reinitialising both the store repo and the remote.
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
