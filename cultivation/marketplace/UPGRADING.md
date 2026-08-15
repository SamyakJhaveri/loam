# Upgrading to marketplace v1.2.0 (2026-08-14 teardown)

This release retires the sentinel commit gate, forks superpowers, and prunes sam-cc-setup.
Follow the steps below in each project that uses these plugins.

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

## Rollback

The old gate lives in git history (hub tag v1.1.0).
Check out the tag and re-copy the hook family if a project truly needs the sentinel design back.
