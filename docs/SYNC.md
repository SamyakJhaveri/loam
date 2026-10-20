# Sync model

Since the 2026-08 rebuild there are three distribution mechanisms: Copier forward, the plugin marketplace in reverse, and attach mode for an existing directory.

## Forward: Copier (template -> projects)

- `uvx copier copy --trust gh:samyakjhaveri/loam ./my-project` bootstraps.
- `bin/sync-project <owner/repo> [<loam-commit>]` carries one Loam commit into a rendered project as a pull request.
  Use it for every update.
- A plain `uvx copier update --trust` in the project still works.
  It resolves the latest tag, reads the template from the project's `_src_path`, and runs the template's tasks (see below).
- Copier `copy` and a plain `update` resolve git TAGS, not HEAD, so nothing reaches them until `bin/release.sh <version>` tags it.
  `bin/sync-project` takes any commit.

### bin/sync-project

```bash
bin/sync-project --dry-run SamyakJhaveri/distbench            # Loam HEAD; stop before the push
bin/sync-project --draft SamyakJhaveri/distbench e90bfce0     # push loam-sync/e90bfce0, open a draft PR
```

Flags: `--loam DIR` (the Loam checkout to render from, default the script's own), `--branch NAME` (default `loam-sync/<sha8>`), `--work DIR` (the scratch dir, default a new one under `$TMPDIR`), `--rulings FILE` (default the project's `.loam/sync-rulings.md`), `--data KEY=VALUE` (a Copier answer, repeatable), `--dry-run`, `--no-port`, `--draft`.
`--data` is how a project changes an answer, since nobody edits `.copier-answers.yml` by hand: a project that runs no hooks syncs once with `--data memory=false`, Copier records `memory: false`, and later syncs keep it.
It needs `git`, `copier` (or `uvx`), `claude` and `gh`.

What it does, in order:

1. It clones the project into the scratch dir and works only there.
   `<project>` is `owner/repo` or its github.com git URL; with `--dry-run` any repo path works too.
   Without `--dry-run` it first refuses a project that names no GitHub repo and a branch name the project already has, so a push or PR that would fail costs no model call.
2. It points `_src_path` at the local Loam checkout in a throwaway commit, runs `copier update --trust --defaults --skip-tasks --conflict inline --vcs-ref <sha>` plus any `--data` answers and the rulings' Copier flags (see Sync rulings), and then puts the project's own `_src_path` back.
   Copier `update` has no source flag and refuses a dirty tree, hence the throwaway commit.
   Copier runs with `merge.conflictStyle=merge` forced, because `diff3` and `zdiff3` add a base section to every hunk.
   The exact `--vcs-ref` makes Copier clone that commit, and Copier folds a checkout's uncommitted files in only when the ref is `HEAD`, so they cannot leak in.
   In `.copier-answers.yml` `_src_path` keeps its value, so the PR never rewrites where the project says its template lives; `_commit` changes, and so does an answer a `--data` flag or a new question's default sets.
3. It does by hand the two tasks an update needs, and commits Copier's result, conflict markers included.
   It deletes `_gh_setup.sh`.
   Task 1 strips from `.claude/settings.json` what the answers turn off: the pyright-lsp plugin for a non-Python `project_kind`, the memory hooks for `memory=false`.
   For `memory=false` it also sets `hooks = false` in `.codex/config.toml`, and the script does the same when that file has no conflict.
   When Copier conflicts on that file, the script applies the strip to both renders and merges the file again; once the file has no conflict, it strips the file itself when that removes something, as a plain update does.
   This first commit is deterministic: the same Loam commit on the same project base gives the same tree.
4. It runs one `claude -p` on `claude-opus-5-5` over every file Copier left conflicted, with a fixed brief.
   The brief says to keep the project's content, adopt the template's change where it does not contradict it, decide each question once and apply it the same way in every file, remove every marker, and list each choice per file.
   It points the model at the project's own docs to learn which design the project chose, and gives it the project's sync rulings when it has them (see Sync rulings).
   It also carries the template's own diff for each file, from the old and new renders that Copier records as index stages 1 and 3.
   The model edits copies outside the tree with only the Read and Edit tools, and the script copies them back to the conflicted paths it holds in memory, so an edit in the scratch dir cannot redirect a write.
   `LOAM_MEMSTORE` and `TMPDIR` point into the scratch dir, and `LOAM_MEMSTORE_REMOTE` is unset, so no memory hook pushes.
5. It refuses to go on if a marker or a `.rej` file remains, if a conflicted JSON file no longer parses, or if any other file changed.
   Otherwise the port becomes the second commit, with the model's choices in its message, so a reviewer reads Copier's part and the model's part apart.
6. It runs the project's `bin/check`, and each `.claude/skills/verify-*` skill through `claude -p`, and puts the results in the PR body.
   Neither gates the PR, because a sandbox can fail a check that CI passes; the PR's CI is the gate.
   The verify agent has Bash, so the script saves the port's commit and refuses to push if the pushed branch or a tracked file changed since.
7. It pushes the branch without force and opens the PR with `gh` in the repo it pushed to, not the `github_repo` answer, which a renamed or forked project leaves stale.
   The body names the command, each conflicted file with the model's choices, and the check lines.
   `--dry-run` stops before the push and leaves the clone and `pr-body.md` in the scratch dir.
   `--no-port` skips step 4, so any conflict stops the run at step 5 with the first commit in the scratch clone.

Why these choices:

- Tasks are skipped because on `update` Copier runs `_tasks` three times: in its temporary old render, in the project, and in its temporary new render.
  The temporary renders have no `.git` and no origin, so Loam's tasks there run `git init` and then `_gh_setup.sh`, which tries a push and GitHub API writes.
  Skipping task 1 there leaves its settings strip a project change, and a template change beside it conflicts with a template side that re-adds what it stripped; hence the second merge in step 3.
- Inline markers beat `.rej` files here.
  Copier 9 merges each rejected file with `git merge-file` and records the template's old and new renders in the index, so the model sees each hunk in place and gets the template's own diff.
  A `.rej` file holds only the failed hunk.
- One call over every conflicted file lets the model make a decision that spans files once.
  With one call per file, the distbench port moved the catchup skill to the memory-store handoff, while the project's `docs/WORKERS.md` keeps the handoff at the root `HANDOFF.md`.
- The model edits copies because Claude Code refuses writes under `.claude/` in `acceptEdits` mode.
  It loads only user settings because a conflicted `.claude/settings.json` is invalid JSON while the port runs.
- A verification skill is prose plus a project-specific CLI with no shared entry point, so an agent reads its `SKILL.md` and picks the recipes.

After a sync to an untagged commit, `_commit` reads like `v3.0.0-361-ge90bfce0`.
A plain `copier update` from `gh:` then refuses, because the latest tag is older and Copier does not downgrade.
Keep using `bin/sync-project` until a newer tag exists.

### Sync rulings

Some conflicts are owner calls that no brief can infer, such as whether the project wires the template's hooks or where its handoff lives.
The project's tracked file `.loam/sync-rulings.md` records them as plain prose that the owner writes, one short line per call.
`bin/sync-project` puts its text in the port prompt, where a ruling wins over the brief's keep-or-adopt rules, and names the file and its git blob sha in the PR body.
A ruling about a file Copier did not conflict on lands in the PR's notes, because the port edits only conflicted files.
When nothing conflicts, no port runs, and the PR body asks the reviewer to check the diff against the rulings.
Each sync PR that makes a new owner call adds a line to the file, so the next sync repeats the call.
`--rulings FILE` tries a draft in place of the tracked file.

A ruling that a path must take no template change at all also goes in a `## Copier flags` section, as a fenced block with one Copier flag and one pattern per line:

````markdown
## Copier flags

```text
--skip /bin/check
--skip /AGENTS.md
--exclude /docs/runtime
```
````

`bin/sync-project` passes these lines to `copier update` as they are, so the ruling holds by structure instead of through the port.
`--skip` keeps a file the project has exactly as it is.
Copier neither renders over it nor applies the template's diff to it, so even a change Copier would merge cleanly stays out.
`--skip` still lets Copier create the file when the project lacks it, and delete it when the template removes it.
So `--skip` re-creates a file the project deleted on purpose, at the template's new content; give such a path `--exclude` instead.
`--exclude` keeps the path from rendering at all, so Copier never creates, changes or deletes it.
Patterns follow `.gitignore` rules, and a leading `/` anchors one at the project root, so `/AGENTS.md` does not also match a nested `AGENTS.md`.
Write patterns without quotes.
The section holds only blank lines and that one fenced block, up to the next heading.
The run refuses before Copier starts when a line in the block is anything else, when the section holds any other line or a second block, when the heading appears twice, or when a heading names Copier flags in another form, such as `## Copier Flags`, `### Copier flags` or `## Copier flag`.
Inside another fenced block only the exact heading counts, so a code comment such as `# copier flags are set below` does not refuse the run.
When the file has no exact heading, such a line refuses it, so a fence left open cannot hide a misspelled heading below it.
The port still reads the whole file, with a line saying these paths need no note, so keep the prose ruling and its reasons elsewhere in the file.
The PR body and Copier's commit message show the full command with the flags.

### Release note: projects rendered from v3.0.0 start dirty

Loam v3.0.0's first commit tracked `_gh_setup.sh`, and its last task deletes the file.
A project that still tracks it shows ` D _gh_setup.sh` in `git status` after the first render and after every plain `copier update`, and Copier refuses the next update until that deletion is committed.
`bin/sync-project` deletes `_gh_setup.sh` and commits the deletion with Copier's result, so the project ends clean.
Later updates leave the file out, because Copier skips template files the project has deleted.

## Reverse: the plugin marketplace (improvements -> other projects)

There is no file-sync engine anymore (agent-sync, template-sync, and hub-ci were retired 2026-08-29; the last implementation is readable at git tag history before commit feee2e4).
An asset proven in one project is promoted by hand into `cultivation/marketplace/sam-cc-setup/` (or a bundle) and reaches every other project as a plugin update.
That gives versioned releases and in-place updates without custom machinery.

## Attach mode: the harness into an existing directory

`bin/loam-attach.sh <dir>` drops the Claude harness into a directory Copier never rendered, without turning it into a Loam project.
It copies `seed/.claude/settings.json` and the `seed/.claude/hooks/` scripts over `<dir>/.claude/` (any foreign hooks already in `<dir>/.claude/hooks/` survive; only the seed-named files are replaced), appends the harness `.gitignore` lines, and writes `<dir>/.claude/settings.local.json` that registers this checkout's `cultivation/marketplace` and enables the `sam-cc-setup` plugin.
It refuses to overwrite an existing harness (a `<dir>/.claude/settings.json` file or a `<dir>/.claude/hooks/` directory) unless `--force`, and never overwrites an existing `settings.local.json`.
The marketplace path it writes is this checkout's absolute path, so run it from the canonical checkout rather than a throwaway worktree.
