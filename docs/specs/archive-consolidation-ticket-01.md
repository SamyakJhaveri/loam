# Ticket 01 — Tag, safe harvest + local archive cleanup

> Spec: `docs/specs/archive-consolidation.md` · Plan: `~/.claude/plans/so-i-want-to-dazzling-manatee.md` (v2, Part 0)
> Status: TODO · Blocks: Ticket 02 · Risk: low (every deletion is tagged first, so it's gc-proof reversible; the only unrecoverable item — the untracked working-tree scratchpad — is fully read before removal)

## Goal

Create a reversibility net (tags) over every tip, harvest the untracked scratchpad's live pointers into `soil/`, then delete the four stale local branches, drop the stash, and remove the harvested working-tree scratchpad. Archive `main` is a frozen quarantine and is never touched.

**Every mutating command runs in `~/Desktop/loam-dev-archive`. The only touch of the public repo is a read-only HEAD capture.**

## Steps

### 0. Capture the public-repo baseline (read-only)

```bash
PUBLIC_HEAD=$(git -C ~/Desktop/loam rev-parse HEAD); echo "public loam HEAD at start: $PUBLIC_HEAD"
# Record this value; Ticket 02's final check asserts it is unchanged.
```

### 1. Tag every tip BEFORE any deletion (the reversibility net)

```bash
cd ~/Desktop/loam-dev-archive
git tag archive/pre-cleanup/feat-lsp     feat/lsp-code-intelligence-default
git tag archive/pre-cleanup/codex-audit  fix/codex-audit-followups
git tag archive/pre-cleanup/web-frontend web-frontend-bundle
git tag archive/pre-cleanup/yoshida      worktree-yoshida-image-experiment
git tag archive/pre-cleanup/stash        'stash@{0}'   # a stash is a commit; the tag also preserves its untracked-files parent (the 14-line scratchpad)
git tag -l 'archive/pre-cleanup/*'                     # expect 5 tags
```

Every object about to be deleted is now reachable from a tag (gc-proof). Nothing recoverable can be lost from here on; the branch/stash deletions below are freely reversible.

### 2. Safe harvest of the untracked working-tree scratchpad

This file is untracked — no tag or reflog protects it — so read the WHOLE file, not a sample, before removing it.

```bash
cd ~/Desktop/loam-dev-archive
wc -l loam_scratchpad.md                       # expect 440
cat loam_scratchpad.md                         # READ ALL 440 LINES — do not sample
git show 'archive/pre-cleanup/stash:loam_scratchpad.md' 2>/dev/null \
  || git show 'stash@{0}^3:loam_scratchpad.md' # the 14-line stashed scratchpad (already tag-preserved)
```

Create `soil/harvested-scratchpad-pointers.md` with the live pointers (everything else is stale diagram/session logs — do not copy it):

```markdown
# Harvested scratchpad pointers (from loam-dev-archive, 2026-07-18)

Salvaged before deleting the two stale scratchpads. Source: working-tree
loam_scratchpad.md (440 lines) + stash@{0}^3 loam_scratchpad.md (14 lines).
Full 440-line file was read before removal.

## Tool / capability candidates
- **codex-plugin-cc** — https://github.com/openai/codex-plugin-cc — relevant to the
  campaign's Codex-runtime conformance track (fixing the shipped seed/.codex harness).
- **codeburn** — setup to evaluate.
- **ccstatusline** — status-line setup to evaluate.

## Already done (no action)
- "codex for review, wired to trigger from a Claude Code session" — realized:
  Codex reviewed the Phase-1 plan on 2026-07-18.

## Other
- (Add any additional live URL or unfinished "STILL NEEDS TO BE DONE" item found in
  lines 41–440 that is NOT already covered by the plan or a shipped feature. If none, delete this heading.)
```

### 3. Informational stash check (not a safety gate — the stash is tagged)

```bash
cd ~/Desktop/loam-dev-archive
git stash show --include-untracked stash@{0}                    # expect 3 files, 54 ins / 14 del
AP=$(git stash show --include-untracked --name-only stash@{0} | grep align-prompt)
echo "stashed align-prompt path: $AP"                           # double quotes below so $AP expands
git show "stash@{0}:$AP" | diff - ~/Desktop/loam/seed/.claude/skills/align-prompt/SKILL.md
git show "stash@{0}:$AP" | diff - ~/Desktop/loam/cultivation/marketplace/helpers/skills/align-prompt/SKILL.md
```

Expected: the stash is an older align-prompt draft; the public copies are the same feature with tightened wording + a trailing newline (a later revision). Confirms nothing unique is lost. (Even if it were, `archive/pre-cleanup/stash` preserves it.)

### 4. Delete — safe verb for ancestors, force only for the tagged feat/lsp

```bash
cd ~/Desktop/loam-dev-archive
git branch -d fix/codex-audit-followups web-frontend-bundle worktree-yoshida-image-experiment
# -d accepts all three (they're ancestors of main). If -d ever REFUSES one, STOP — that branch
# carries unexpected unique work; investigate before forcing.
git branch -D feat/lsp-code-intelligence-default   # not an ancestor; safe to force ONLY because it's tagged + verified in public v1.0.0
git stash drop stash@{0}                           # content preserved by archive/pre-cleanup/stash
rm loam_scratchpad.md                              # the harvested 440-line working-tree file
```

## Verification (must all pass before Ticket 02)

```bash
cd ~/Desktop/loam-dev-archive
git branch                                              # expect: only * main
git tag -l 'archive/pre-cleanup/*' | wc -l              # expect: 5
git stash list                                          # expect: empty
test -f soil/harvested-scratchpad-pointers.md && \
  grep -q codex-plugin-cc soil/harvested-scratchpad-pointers.md && echo "harvest OK"
test ! -f loam_scratchpad.md && echo "scratchpad removed OK"
git rev-parse main                                      # expect: d132c23c... (quarantine untouched)
```

## Done when

Five `archive/pre-cleanup/*` tags exist, local branches reduced to `main`, stash empty, harvest file present with the three pointers, the full 440-line scratchpad was read then removed, and `main` is still `d132c23c`. Remote branches → Ticket 02.
