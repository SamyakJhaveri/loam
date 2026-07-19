# archive-consolidation

> Spec for Part 0 of the Phase-1 campaign plan (`~/.claude/plans/so-i-want-to-dazzling-manatee.md`, v2).
> Generated via `/gen-spec`, 2026-07-18. Revised 2026-07-18 to the tag-then-delete approach after adversarial spec review (verdict: APPROVE WITH CHANGES; feat/lsp supersession confirmed byte-identical at source). Implementation deferred to a later session.

## Identity

- **Name:** archive-consolidation
- **Owner:** Sam
- **Status:** draft (review change-set applied; awaiting Sam's sign-off to mark `ready`)
- **Scope:** safe harvest of two scratchpads + reversible deletion of stale branches, stash, and one remote branch in the private `loam-dev-archive` repo. Nothing in the public `loam` repo is modified.
- **Tickets:** `docs/specs/archive-consolidation-ticket-01.md`, `docs/specs/archive-consolidation-ticket-02.md`

## Inputs

- **Target repo:** `~/Desktop/loam-dev-archive` (private, quarantined dev history; `main` = `d132c23c`).
- **Verified ground truth** (commands, 2026-07-17/18; feat/lsp re-verified byte-level in spec review):
  - Stale local branches: `fix/codex-audit-followups` (same SHA as `main`), `web-frontend-bundle` (ancestor of `main`), `worktree-yoshida-image-experiment` (ancestor of `main`; a plain branch with NO attached worktree) - all three are ancestors, so `git branch -d` accepts them. `feat/lsp-code-intelligence-default` is 1 commit ahead (NOT an ancestor), so `-d` will refuse it - that refusal is a deliberate tripwire; its unique commit `8b3bd87a` touches three files (`seed/.claude/rules/tech-stack.md` +33 lines, `seed/CLAUDE.md.jinja` +1 bullet, `seed/.claude/settings.json` pyright+clangd) and all three are already in public v1.0.0 (tech-stack + jinja byte-identical; settings.json a superset).
  - `stash@{0}`: three files - `align-prompt/SKILL.md` (an older align-prompt draft; public tightened the wording + added a trailing newline, so public is a later revision, not lost work), a 2026-05-27 plan doc (matches `main`), and a 14-line untracked `loam_scratchpad.md`.
  - Working-tree untracked `loam_scratchpad.md`: 440 lines / 49 KB, distinct blob from the stashed one; untracked, so NO tag or reflog can recover it once removed - it must be fully read before removal.
- **Supersession-check references** (must both exist): `seed/.claude/skills/align-prompt/SKILL.md` and `cultivation/marketplace/helpers/skills/align-prompt/SKILL.md` (verified present in public `loam`).
- **Harvest destination:** `~/Desktop/loam-dev-archive/soil/` (local, gitignored; directory already exists).

## Behavior

Runs in strict order. A reversibility net (tags) is created before any deletion, so no destructive step can lose recoverable data.

1. **Capture the public-repo baseline.** Record `~/Desktop/loam` HEAD SHA at the start, to assert it is unchanged at the end.
2. **Tag every tip before deleting (the reversibility net).** One lightweight tag per stale branch AND one for the stash commit. Tags are gc-proof and keep every deleted object reachable; a stash commit tag also preserves its untracked-files parent (the 14-line scratchpad). This dissolves the need for per-branch supersession arguments - deletion becomes freely reversible.
3. **Safe harvest of the untracked working-tree scratchpad.** Read the ENTIRE 440-line file (not a sample), extract the live forward-pointers (the `github.com/openai/codex-plugin-cc` link; the tool names `codeburn`, `ccstatusline`; a note that "codex-for-review" is already realized) into a dated file under `soil/`. Everything else is stale session logs.
4. **Informational stash check.** Diff the stashed `align-prompt/SKILL.md` against both public copies to confirm public is the same-or-later revision. This is informational now (the stash is tagged in step 2), not a safety gate.
5. **Delete, using the safe verb where possible.** `git branch -d` the three ancestor branches (the `-d` refusal is a free tripwire if any unexpectedly carries unique work); `git branch -D` only the tagged `feat/lsp` (safe because tagged + verified); `git stash drop`; `rm` the harvested working-tree scratchpad.
6. **Remote deletion behind a fresh gate** (Ticket 02): `git fetch`, require `rev-list --count origin/main..origin/web-frontend-bundle == 0`, then `git push origin --delete`.
7. **Leave the frozen quarantine intact.** `main`, `origin/main`, and all other history untouched (the new `archive/pre-cleanup/*` tags are the only additions).

## Outputs

- New file: `~/Desktop/loam-dev-archive/soil/harvested-scratchpad-pointers.md` (the three harvested pointers, dated).
- New refs: five `archive/pre-cleanup/*` tags (feat-lsp, codex-audit, web-frontend, yoshida, stash) - the permanent reversibility net.
- Deleted: four local branches, `stash@{0}`, both scratchpad files (440-line working-tree + 14-line stashed), and the remote `web-frontend-bundle`. All except the untracked working-tree scratchpad remain recoverable via the tags.
- Unchanged: archive `main` / `origin/main`; public `loam` (zero commits, zero file changes).
- Recorded evidence: the public-HEAD baseline SHA; the five tags; the full-file-read confirmation; the `rev-list --count == 0` gate output.

## Constraints (must NOT)

- MUST NOT run any command in the public `~/Desktop/loam` repo (except the read-only HEAD baseline capture + final assertion) - every mutating command targets `~/Desktop/loam-dev-archive`.
- MUST NOT delete any branch or drop the stash before all five `archive/pre-cleanup/*` tags exist.
- MUST NOT `rm` the working-tree `loam_scratchpad.md` before the entire 440-line file has been read for live pointers (it is untracked and unrecoverable).
- MUST NOT use `git branch -D` on the three ancestor branches - use `-d` so its refusal acts as a tripwire; `-D` is reserved for the tagged `feat/lsp`.
- MUST NOT `git push origin --delete web-frontend-bundle` unless a fresh `rev-list --count origin/main..origin/web-frontend-bundle` returns exactly `0` in the same session.
- MUST NOT touch archive `main`, `origin/main`, or any history other than the four named branches + the one stash.
- MUST NOT commit or push anything to public `loam` (archive hygiene only).
- MUST NOT expand scope into the mechanism spike, the review campaign, or any Codex-harness fix.

## Acceptance Criteria

1. `git -C ~/Desktop/loam-dev-archive branch -a` lists exactly `main`, `remotes/origin/main` (+ `remotes/origin/HEAD`) - no other branches.
2. `git -C ~/Desktop/loam-dev-archive tag -l 'archive/pre-cleanup/*' | wc -l` equals `5`, and each tag resolves to a commit (`git cat-file -t` = `commit`) - the reversibility net exists.
3. `git -C ~/Desktop/loam-dev-archive stash list` is empty.
4. `git -C ~/Desktop/loam-dev-archive worktree list` prints one entry. (Pre-satisfied guard: `worktree-yoshida` was a plain branch with no attached worktree, so this is already true before any work - it confirms nothing broke, not that work happened.)
5. `~/Desktop/loam-dev-archive/soil/harvested-scratchpad-pointers.md` exists and contains `codex-plugin-cc`, `codeburn`, and `ccstatusline`.
6. The implementation transcript records that the full 440-line `loam_scratchpad.md` was read before removal (go-signal for the one unrecoverable step), and `test -f ~/Desktop/loam-dev-archive/loam_scratchpad.md` fails afterward.
7. `git -C ~/Desktop/loam-dev-archive rev-parse main` equals `d132c23c` (quarantine `main` untouched).
8. The transcript records `rev-list --count origin/main..origin/web-frontend-bundle` = `0` immediately before the remote deletion.
9. Public repo untouched by the cleanup: within each ticket's run, the `~/Desktop/loam` HEAD SHA captured at that run's start equals its HEAD at the run's end, and `git -C ~/Desktop/loam status --porcelain` shows nothing introduced by this work. (Per-ticket capture-vs-capture, so committing the spec + tickets between Ticket 01 and Ticket 02 does not create a false failure - each ticket only proves it made no public change during its own run.)

## Review gate (before implementation)

Adversarial spec review completed 2026-07-18 (APPROVE WITH CHANGES; this revision applies the full change-set: tag-then-delete, split `-d`/`feat-lsp`, full-file harvest, recorded go-signals, robust criteria #4/#9). Remaining gate: Sam's sign-off → mark `Status: ready`, then a later session implements the two tickets in order.
