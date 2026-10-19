# Copier update

A user with an existing project runs `copier update` to take a newer template: copier merges the template's changes into the project and leaves them uncommitted for review, marks a clash with the user's own committed edit with inline conflict markers, moves `_commit` in `.copier-answers.yml` to the new version, and refuses a dirty tree or an older version.

## Sub-features

- `update-merge` applies template changes to files the user did not edit and adds new files, committing nothing.
- `update-pin` moves `_commit` in `.copier-answers.yml` to the new version.
- `update-conflict` wraps a template change that clashes with a committed user edit in `<<<<<<< before updating` and `>>>>>>> after updating`, still exits 0, and leaves the file unmerged (`UU` in `git status`).
- `update-dirty` refuses to run on a working tree with uncommitted changes.
- `update-downgrade` refuses a ref older than `_commit`.
- `update-hooks` puts the newer hooks in play: the next session fires them.

## How to get to it (user POV)

- `cd my-project && uvx copier update --trust` (the newest release tag).
- `uvx copier update --trust --vcs-ref <ref>` (a named ref, such as `HEAD` of a local Loam checkout).

## Driving it with control-loam

Preconditions:

- `copier` or `uvx` is on PATH, and this checkout has the tag `v3.0.0`.
- Commits in a render use `git -C <root>/<id>/render -c user.name=verify -c user.email=verify@example.invalid commit -qam <message>`, written `commit` below.

- **Old project.** Run `$C render --run u1 --ref v3.0.0`, then `$C doctor u1`. Doctor passes with `_commit=v3.0.0` and `2 hook scripts`.
- **Dirty refusal.** Run `$C update u1 --name update-dirty`. Exit 1 and `tail` reads `Destination repository is dirty; cannot continue. Please commit or stash your local changes and retry.`; `update-dirty.log` shows ` D _gh_setup.sh`. Every v3.0.0 render starts dirty: its initial commit tracks `_gh_setup.sh` and a later copier task deletes the file.
- **Clean the tree.** `commit "remove _gh_setup.sh"` in u1.
- **Update.** Run `$C update u1`. Exit 0, `commit_before` is `v3.0.0`, `commit_after` is `v3.0.0-<n>-g<HEAD sha>`, `conflicts` is empty, and `tail` holds `Updating to template version 3.0.0.post<n>.dev0+<sha>`. At 18445b9, `changed` was 24 (13 modified, 11 new paths). Nothing is committed, and `.codex/config.toml` now reads `hooks = true`.
- **Doctor after.** Run `$C doctor u1`. `render came from the recorded commit` passes against the new `_commit` and the hook count is `4 hook scripts`; `render is a git repo with the initial commit` fails because HEAD is now the user's commit.
- **Hooks in play.** `git -C <root>/u1/render add -A`, `commit "copier update"`, then run `$C session u1 "Reply with the single word OK." --stub --name post-update`. `hooks` holds two `SessionStart:startup` entries and one `Stop`, and `<root>/u1/memstore/traces/render/INDEX.md` gains a line. Control: the same session in a fresh `--ref v3.0.0` render holds one `SessionStart:startup` and no `Stop`.
- **Check.** Run `$C check u1`. `last_line` is `check: PASSED (skipped: pytest)`.
- **Conflict.** Run `$C render --run u2 --ref v3.0.0`. In `<root>/u2/render/AGENTS.md`, add the line `- Deploys go through the staging branch first.` under `## Gotchas`, then `commit "remove _gh_setup.sh; add a project gotcha"` (it also stages the deletion). Run `$C update u2`. Exit 0, `conflicts` is `["AGENTS.md"]`, and `update.log` shows `UU AGENTS.md`. Under the new `## Memory` heading, `AGENTS.md` holds the old gotchas plus the user's line between `<<<<<<< before updating` and `=======`, and the template's `bin/memsearch` line before `>>>>>>> after updating`. `README.md`, which the user did not touch, merged clean (4 lines added).
- **Conflict caught.** Run `$C check u2`. Exit 1, and `check.txt` has `AGENTS.md:18: leftover conflict marker` and `FAIL: whitespace or conflict markers in staged or unstaged edits`.
- **Downgrade refused.** Run `$C render --run u3` (HEAD), then `$C update u3 --ref v3.0.0`. Exit 1, `tail` reads `You are downgrading from 3.0.0.post<n>.dev0+<sha> to 3.0.0. Downgrades are not supported.`, `_commit` is unchanged, and the tree stays clean. **Update** is the control: the same command upward succeeds.
- **Proof.** `update.log` and `update-dirty.log` (copier's output, then `git status --porcelain`) in each run's evidence. Each `$C update` overwrites `<name>.log`, so give a step you want to keep its own `--name`.

## Gotchas

- copier never prints the word conflict. It exits 0; only `git status` (`UU`) and the markers show the clash. The `conflicts` list is control-loam's scan of changed files for markers and `.rej` files.
- copier's output includes the git tasks it ran in its temporary old and new copies (`Initialized empty Git repository in .../copier._main.old_copy...`, `[main (root-commit) ...] Initial commit from loam`). They do not touch the project's repository.
- `Make sure Git >= 2.24 is installed to improve updates.` printed with git 2.55.0. It is noise.
- `$C update` points `run.json` at the new ref, so `doctor` checks `_commit` against it, and drops the old `doctor` and `check` records. An updated render is not pristine; use a fresh run for the `bin/release.sh` gate.
- `$C update` defaults to `--ref HEAD`; a user's plain `copier update` takes the newest release tag instead (see [Render](./render.md) Gotchas).
- `--ref HEAD` on a dirty checkout updates to copier's WIP commit, as `render` does.
