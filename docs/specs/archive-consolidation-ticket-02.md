# Ticket 02 — Remote branch deletion + final verification

> Spec: `docs/specs/archive-consolidation.md` · Plan: `~/.claude/plans/so-i-want-to-dazzling-manatee.md` (v2, Part 0)
> Status: TODO · Depends on: Ticket 01 · Risk: **medium — one irreversible outward action** (deleting a remote branch)

## Goal

Delete the stale remote branch `web-frontend-bundle` from `origin`, but only after re-proving from fresh remote state that its tip adds nothing over `origin/main`. Then confirm the whole archive is clean and that this ticket introduced no change in the public repo.

**Every mutating command runs in `~/Desktop/loam-dev-archive`. The only touch of the public repo is a read-only HEAD capture + final assertion.**

## Why the gate (do not skip)

At review time (2026-07-18) `origin/web-frontend-bundle` was an ancestor of `origin/main` (0 commits ahead). Remote state can drift between then and execution, so the deletion is guarded by a fresh `fetch` + `rev-list` check. Only a `0` result authorizes the push.

## Steps

### 0. Capture a FRESH public-repo baseline (read-only)

```bash
PUB=$(git -C ~/Desktop/loam rev-parse HEAD); echo "public loam HEAD at Ticket 02 start: $PUB"
```

> Do NOT reuse the SHA recorded in Ticket 01. The `archive-consolidation` spec + tickets were committed to public `loam` between the two tickets, so its HEAD legitimately advanced. Each ticket proves its OWN non-interference: capture here, assert unchanged at the end. Record this value as a literal too (shell vars do not survive across separate tool calls).

### 1. Refresh remote state and run the gate

```bash
cd ~/Desktop/loam-dev-archive
git fetch origin --prune
git rev-list --count origin/main..origin/web-frontend-bundle    # record this value; must be 0
```

- If the count is `0` → proceed to step 2.
- If it is not `0` → **STOP.** The remote tip now carries unique commits. Do not delete. Inspect with `git log --oneline origin/main..origin/web-frontend-bundle` and bring the delta to Sam.

### 2. Delete the remote branch (only if the gate == 0)

```bash
cd ~/Desktop/loam-dev-archive
git push origin --delete web-frontend-bundle
```

### 3. Final verification of the whole consolidation

```bash
cd ~/Desktop/loam-dev-archive
git fetch origin --prune
git branch -a                              # expect: main, remotes/origin/main, remotes/origin/HEAD only
git tag -l 'archive/pre-cleanup/*' | wc -l # expect: 5 (reversibility net intact)
git stash list                             # expect: empty
git worktree list                          # expect: one entry
git rev-parse main                         # expect: d132c23c... (quarantine untouched)

# Public repo untouched BY THIS TICKET — assert HEAD equals the fresh step-0 baseline
# (use the literal you recorded there):
test "$(git -C ~/Desktop/loam rev-parse HEAD)" = "$PUB" && echo "public HEAD unchanged by Ticket 02 OK"
git -C ~/Desktop/loam status --porcelain   # expect: nothing introduced by this work
```

## Done when

`git branch -a` in the archive shows only `main` + `origin/main` (+ `origin/HEAD`), the five `archive/pre-cleanup/*` tags are intact, stash empty, one worktree, `main` still `d132c23c`, the recorded remote-gate value was `0`, and public `loam` HEAD equals this ticket's step-0 baseline. This closes the `archive-consolidation` spec (mark its `Status: implemented`).
