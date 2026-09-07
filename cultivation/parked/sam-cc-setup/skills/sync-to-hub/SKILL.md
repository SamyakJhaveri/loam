---
name: sync-to-hub
description: >
  Promote project-side `.claude/` improvements (skills, agents, hooks, rules) into
  the sam-cc-setup plugin in the hub repo. Sync is project -> hub, ADDITIVE ONLY.
  Each new or changed file is offered with a 3-way prompt (sync now / defer /
  never) so trial-only experiments do not pollute the curated hub. Use after a
  session in which you used or refined a tool worth keeping across future
  projects. NOT for mid-session use, uncommitted project work, or deleting
  anything from the hub (edit the hub directly for that).
disable-model-invocation: true
---

# /sync-to-hub

Promote `.claude/` work from a project repo into the sam-cc-setup plugin inside the hub repo, at `<hub>/cultivation/marketplace/sam-cc-setup/`.

> **Prerequisite:** the hub repo must be cloned locally. Its location comes from `SAM_CC_HUB_REPO` (default `$HOME/Desktop/loam`). It is not present on every box; `sync.sh` exits 1 with a hint if missing.

## Direction

**Project -> hub. ADDITIVE ONLY.**

The hub is the curated master set you bootstrap new projects from (via `claude plugin install sam-cc-setup@seed-skills`, or the Copier template for full renders). For generic assets in a template-*rendered* project, the template's own `template-sync promote` into `seed/` is the native path; it requires `.copier-answers.yml` or `template-manifest.json`, so in a repo without those this skill is the only promote path. A project may be a subset of the hub, or extend the hub with experiments. This skill promotes useful project-side experiments INTO the hub; it never deletes from the hub based on what a project lacks.

## Iron law

```
NO HUB MUTATION WITHOUT PER-FILE USER APPROVAL
```

Each new or changed file is presented to you with a 3-way prompt:

- `y` / `yes` / `sync` - sync this file to hub now
- empty / `d` / `defer` - skip this run; ask again after the threshold (default)
- `n` / `never` - skip permanently (until state cleared manually)

Default = defer. Pressing Enter on every prompt syncs nothing. Sync is opt-in.

## State persistence

Decisions are recorded in `<hub>/.sync-state` (gitignored, per-hub-clone). Each `/sync-to-hub` invocation increments a session counter. Three decision types:

- **Defer:** the file is silently skipped (no prompt) until session count reaches the recorded `ask_again_at` value. Defer threshold defaults to 4 sessions; override via env `SAM_CC_DEFER_SESSIONS=N` (3-6 is the recommended range).
- **Never:** the file is silently skipped on every future run. To re-enable, edit `.sync-state` and remove the `never:<path>` line.
- **Synced:** records when the file was last promoted to hub.

State file format (flat KV, no jq dependency):

```
session=12
defer:skills/foo/SKILL.md:16
never:skills/bar/SKILL.md
synced:skills/baz/SKILL.md:8
```

To reset all state: `rm <hub>/.sync-state`.

## Invocation

```
/sync-to-hub
```

Optionally override the hub location via env var `SAM_CC_HUB_REPO=/path/to/hub`.

## Workflow

1. Resolve `SAM_CC_HUB_REPO` (default `$HOME/Desktop/loam`). Verify it exists and is a git repo.
2. Verify the project's `.claude/` has no uncommitted changes. If dirty, refuse - commit or stash first.
3. Verify the hub's working tree is clean. If dirty, warn and ask to continue.
4. Compute the additive diff (`rsync --dry-run -a --itemize-changes ...`). Hub-only files are ignored. Standard exclusions: `audit.log`, `settings.local.json`, `*.local.*`.
5. Print summary: `X new files, Y changed files`.
6. For each ADDED file: prompt `Add <file> to hub? [y/d/n]`. Default defer.
7. For each CHANGED file: prompt `Update <file> in hub? [y/d/n]`. Default defer.
8. If nothing approved: exit 0 with `"Nothing approved - exiting."`.
9. Apply approved files via `rsync --files-from=<approved>`.
10. Show the resulting `git status` in the hub.
11. Prompt `Commit synced files? [Y/n]`. Default Y.
12. On Y: commit with message `sync: from <project> on <YYYY-MM-DD>`, then a separate
    default-NO prompt asks before pushing (pushes are outward-facing).
13. On push failure: report the error and instruct a manual `cd <hub> && git pull --rebase && git push`.

## Record why the change traveled

After a sync batch promotes anything, add one line to the hub's `cultivation/marketplace/UPGRADING.md`.
State WHAT changed and WHY it traveled: a model change, a paper, a blog post, an incident.
Link the source when one exists.
The hub's provenance rule (top of that file) is the authority; this is a nudge, not a gate.
After a promotion commits, the scan prints a stderr reminder if the batch left `UPGRADING.md` untouched; it is advisory and never blocks.

## Implementation

The deterministic logic lives in `sync.sh`, bundled next to this SKILL.md. It is a
thin wrapper that execs the canonical scan engine in the hub
(`<hub>/bin/agent-sync.sh scan`), so the apply path has no LLM in it. Approvals come
from interactive prompts on stdin, so the script can be driven by a human typist OR
by piped stdin (for testing or scripted approval flows).

**Direct invocation (recommended):**

```bash
cd <your-project>
bash <path-to-this-skill>/sync.sh
```

**Scripted invocation:**

```bash
# Approve all additions, accept default-Y commit/push:
yes y | bash <path-to-this-skill>/sync.sh
# Decline everything:
yes 'n' | bash <path-to-this-skill>/sync.sh
```

Passing `--prune` forwards to the engine's `prune` subcommand instead of `scan`.

## Multi-level dependency chains need one rerun per level

The hub-presence guard withholds a consumer until every dependency in its transitive closure already exists in the hub's committed HEAD, so a chain three levels deep - a hook that sources a helper, which in turn sources a lower-level helper - syncs bottom-up: approve the deepest helper first, let the run commit it, rerun, approve the level above it, and so on. A withheld consumer with a "sync the dependency first, then rerun" message is this flow working, not a bug.

## When NOT to use

- During a live debugging session - your `.claude/` may have transient experimental tweaks you have not yet decided to keep. Sync at session end, not mid-session.
- When you have not yet committed your project work - the dirty-check refuses to sync until the project's `.claude/` is committed.
- For removing a skill from the hub - this skill cannot delete from the hub. Edit the hub directly and commit there.

## Interaction from inside Claude Code

If you invoke `/sync-to-hub` from a Claude Code session, the recommended flow is:

1. Claude opens a Bash tool call: `bash <path-to-this-skill>/sync.sh`
2. The interactive prompts appear in the Bash tool output. Claude relays them to you.
3. You answer through Claude's conversation; Claude pipes your answers via stdin.

You may instead run `sync.sh` directly in a separate terminal - the prompts work natively in any TTY.
