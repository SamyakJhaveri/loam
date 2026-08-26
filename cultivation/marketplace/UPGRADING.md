# Upgrading to marketplace v1.2.0 (2026-08-14 teardown)

This release retires the sentinel commit gate, forks superpowers, and prunes sam-cc-setup.
Follow the steps below in each project that uses these plugins.

## Adding an entry: the provenance rule (read before you write one)

Every promoted change gets one line here that says WHAT changed and WHY it traveled.
The WHY is a reason a reader can act on: a model change, a paper, a blog post, an incident.
Add a link when a source exists.
A line that says only what changed, with no why, is incomplete.

The sync scan helps you remember.
After a batch commits a promotion without touching this file, its commit step prints to stderr:

> Reminder: cultivation/marketplace/UPGRADING.md was not updated in this batch. Consider adding a provenance line (WHAT changed and WHY) for the promoted change(s).

The reminder is a nudge, not a gate.
It prints only after the commit already succeeded, changes no exit code, and asks for nothing.
It stays silent when the batch did touch this file.

## What changed

1. **sam-superpowers is new.**
   It is a fork of obra/superpowers 5.0.7 with the same 14 skills.
   The mandatory SessionStart gate ("you MUST invoke a skill before ANY response") is replaced by a 5-line judgment router.
2. **sam-cc-setup is now v0.3.0.**
   Removed: the sentinel gate family (`pre-commit-gate.sh`, `gate_detect.py`, `sentinel-cleanup.sh`, `test_pre_commit_gate.py`), `create-skill`, `mode-routing`, `techdebt`, the `pr-review` agent, and `codebase-review-fanout`.
   Added: `hooks/pre-commit.sh`, a native git pre-commit hook installed by `/bootstrap-cc-setup`.
3. **The sync engine gained a prune mode.**
   `sync.sh --prune` (or `agent-sync.sh prune`) lists hub files whose project source is gone and offers deletion.
   `portability-manifest.tsv` is the authority; hub-only curated files are never offered.

## Per-project upgrade steps

1. Update the marketplace and plugins in Claude Code (`/plugin`), or pull the loam repo if you reference it by directory.
2. Enable `sam-superpowers@seed-skills`.
   Then disable `superpowers@claude-plugins-official` and `superpowers@superpowers-dev` in your settings.
   Running both the fork and an upstream install duplicates every skill name.
3. If the project vendored the old gate, delete these files from `.claude/hooks/`:
   `pre-commit-gate.sh`, `gate_detect.py`, `diff_hash.sh`, `hash_stdin.sh`, `sentinel-cleanup.sh`, `test_pre_commit_gate.py`, `test_gate_sentinel.py`.
   Remove their PreToolUse/PostToolUse entries from `.claude/settings.json`.
   Delete any `.validation_passed` file and its `.gitignore` line.
4. Install the native hook once per clone:
   `ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit` (after copying `hooks/pre-commit.sh` to `scripts/pre-commit.sh`).
   `/bootstrap-cc-setup` does both steps for a fresh repo.
5. Run `sync.sh --prune` from the project to clear any hub files your project retired.

## Sync engine update: base records and folded-in prune (Ticket 8a)

This applies to anyone who runs `/sync-to-hub` or `bin/agent-sync.sh` against a hub clone.

### What changed

1. **Base records and a `--bootstrap-bases` pass.**
   The engine now records a merge base for each path shared by a project and the hub.
   An unchanged file is no longer re-offered on every run: a candidate whose project content still equals its recorded base is suppressed.
   `bin/agent-sync.sh scan --bootstrap-bases` is a one-time, state-only pass that records a base for every already-shared path.
   It never prompts and never copies; it only writes `.sync-state`.
2. **Prune folds into the normal scan.**
   A hub file whose project source is gone is now offered for deletion inside the ordinary scan run, in the same pass as adds and changes.
   A folded prune is offered only when the portability manifest marks the path `travels`; a retired `stays`, `rework`, or unclassified path is withheld (fail closed).
   The standalone `bin/agent-sync.sh prune` subcommand still works unchanged.
3. **A declined or failed commit rolls back this run.**
   The engine holds this run's new ledger records pending and writes them only when the commit succeeds.
   Decline the commit, or let it fail, and the engine restores exactly the paths this run touched to their pre-scan state and drops the pending records.
   The one exception is an untracked-copy prune: it executes on approval and is kept even when you decline, so the deletion is never re-offered forever.
4. **Ledger records are per-project keyed.**
   `.sync-state` records now carry a per-project prefix, so two projects that share one hub clone no longer overwrite each other's decisions.

### What you must do

Run `~/Desktop/loam/bin/agent-sync.sh scan --bootstrap-bases` once from each project that already has files in the hub, with that project as your working directory.
The scan tool lives in your loam hub clone (`~/Desktop/loam` by default, or `$SAM_CC_HUB_REPO`), not in the project.
This records the bases, so files you synced before the upgrade stop being re-offered as changes.
Run it again after any crash mid-batch: it re-records any file that was installed but whose base was never written.

### Safe to ignore

An existing `.sync-state` from before this change needs no manual migration.
A legacy unprefixed record is adopted as the current project's on the next write and rewritten with the project prefix.

## Rollback

The old gate lives in git history (hub tag v1.1.0).
Check out the tag and re-copy the hook family if a project truly needs the sentinel design back.
