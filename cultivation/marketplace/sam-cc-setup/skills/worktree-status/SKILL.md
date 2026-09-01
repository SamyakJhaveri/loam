---
name: worktree-status
description: "Report which git worktrees, branches, and PRs are done or ready to merge. Use when asking what's ready to merge, which worktrees or branches are done, or the status of worktrees, branches, and PRs across the repo. Fetches remote refs, then reports deterministically. NOT a session bootstrap (use /catchup) or a pipeline gate (use /validate); never edits worktrees."
argument-hint: "[optional: a single branch name to filter to]"
---

# Worktree / Branch / PR Status

A deterministic merge-readiness snapshot across every worktree and open PR.
No agents, no LLM judgment beyond rendering the table - every cell comes from `git`/`gh`.

**Trigger:** user types `/worktree-status`, or asks "what's ready to merge?", "which
worktrees/branches are done?", "status of the branches/PRs?".

## Iron Law

```
NO WORKTREE WRITES - this skill may run `git fetch --no-write-fetch-head --prune origin`
to refresh remote-tracking refs, but it never edits files, commits, pushes, or deletes
branches.
```

## Why absolute paths

The shell's working directory is not stable across the calls in this survey - it can reset to
the main repo root between commands. Resolve the root once and route every command through
`git -C "$ROOT"` so the survey is correct no matter which worktree the shell sits in.
`git worktree list` from *any* worktree lists them all, so anchoring on the main root is
correct.

## Workflow

### Step 1 - Collect (run these; capture output, do not guess)

```bash
ROOT=$(git rev-parse --show-toplevel)

# All worktrees + their checked-out branch (skip detached-HEAD lines)
git -C "$ROOT" worktree list --porcelain

# Refresh the merge baseline before computing readiness. Avoid FETCH_HEAD because
# the report only needs remote-tracking refs. If the fetch (or origin/main) is
# unavailable - offline, or a sandbox that blocks .git writes - DEGRADE to local
# `main` instead of aborting, and flag the baseline as stale so the verdict is honest.
BASE=origin/main
STALE_BASELINE=0
if git -C "$ROOT" fetch --no-write-fetch-head --prune origin 2>/dev/null \
   && git -C "$ROOT" rev-parse --verify --quiet origin/main >/dev/null; then
  BASE=origin/main
else
  BASE=main
  STALE_BASELINE=1
fi

# Open PRs as JSON (branch, number, draft/review/check/merge status)
gh pr list --state open --limit 200 \
  --json number,headRefName,title,state,isDraft,reviewDecision,mergeable,mergeStateStatus,statusCheckRollup

```

All ahead/behind counts below are relative to `$BASE` - the freshly fetched `origin/main` when the
fetch succeeds, otherwise local `main` (which can lag origin). When `STALE_BASELINE == 1`, print a
bold warning banner **above** the table before anything else:

> **⚠ Baseline may be stale - `git fetch` failed (offline or a sandbox blocking `.git` writes).
> ahead/behind and the STALE verdict are computed vs local `main`, not fresh `origin/main`. Run
> `git fetch` for an accurate merge-readiness verdict.** (READY-TO-MERGE stays reliable - it is driven
> by the PR's own `mergeable`/`mergeStateStatus` from `gh`, which does not depend on the local baseline.)

If there may be more than 200 open PRs, paginate `gh pr list` instead of trusting the
bounded list; otherwise open PRs past the limit can be hidden from the report.

For **each** branch reported by `worktree list` (filter to `$ARGUMENTS` if a branch name
was passed), strip the `refs/heads/` prefix from the porcelain branch ref before matching
PRs, then compute the three per-branch signals:

```bash
branch_ref="refs/heads/<branch-from-porcelain>"
branch="${branch_ref#refs/heads/}"
worktree_path="<worktree-path-from-porcelain>"

# ahead of the baseline (commits on the branch not yet in $BASE)
git -C "$ROOT" rev-list --count "$BASE..$branch"
# behind the baseline (commits in $BASE not yet on the branch)
git -C "$ROOT" rev-list --count "$branch..$BASE"
# dirty (uncommitted changes in that worktree)
git -C "$worktree_path" status --porcelain | wc -l
```

### Step 2 - Render ONE table

Join the per-branch signals with the PR JSON (match `headRefName` == normalized bare
`branch`) and render a single Markdown table:

| worktree | branch | ahead/behind base | dirty | PR | verdict |
|----------|--------|-------------------|-------|----|---------|

- **ahead/behind base** - `<ahead>↑ / <behind>↓` vs `$BASE` (fresh `origin/main`, or local `main` if
  the fetch degraded - see the stale-baseline banner).
- **dirty** - the porcelain line count (0 = clean).
- **PR** - `#<number> <state/draft/reviewDecision/mergeable/mergeStateStatus/checks>`,
  or `—` if no open PR.

### Step 3 - Verdict per row (deterministic; first match wins)

1. **READY-TO-MERGE** - has an open PR **and** `state == "OPEN"` **and**
   `isDraft == false` **and** `mergeable == "MERGEABLE"` **and**
   `mergeStateStatus == "CLEAN"` **and** `reviewDecision` is `APPROVED` or empty
   (no review required) **and** `statusCheckRollup` has no failing, pending, expected,
   action-required, or cancelled entries **and** `dirty == 0`.
2. **IN-PROGRESS** - `dirty > 0` (uncommitted work) **or** `ahead > 0` with no merge-ready
   PR (in-flight/unpushed commits). Checked before STALE so an actively-dirty checkout that
   happens to be level with main still reads IN-PROGRESS, not STALE.
3. **STALE** - `ahead == 0` **and** clean (nothing to merge: already merged, or empty branch).

Detached-HEAD worktrees have no branch - skip them in the table (note the count separately).

### Step 4 - Summary + PRs with no worktree

After the table:
- One-liner: `N ready · M in-progress · K stale` (+ `D detached` if any).
- **Open PRs with no local worktree** - any `gh pr list` branch that did not appear as a
  worktree row. List them (`#<n> <branch> <mergeable>`) so a merge-ready PR is never hidden
  just because its branch isn't checked out locally.

## What NOT to do

- Not a replacement for `/catchup` (session bootstrap) or `/validate` (pipeline gate).
- Never edit files, commit, push, or delete a branch/worktree - reporting only after
  refreshing remote-tracking refs.
- Don't infer merge readiness from memory or a prior summary - recompute from `git`/`gh`.
