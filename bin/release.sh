#!/usr/bin/env bash
# release.sh — tag a new template release.
#
# Usage: bin/release.sh <version>  (e.g., bin/release.sh 1.1.0)
#
# Steps: (1) update VERSION, (2) commit, (3) tag, (4) push commit + tag.
#
# Identity: the release commit AND the annotated tag are hard-pinned to the
# public GitHub noreply identity via `git -c`. A plain `git commit`/`git tag`
# inherits ambient config — and a fresh clone's global identity may be a
# personal/academic email that would then be baked permanently into public
# history (and a tag's `tagger` line). Pinning needs zero operator setup and
# closes both leak vectors.

set -euo pipefail

# shellcheck disable=SC2034
LIB_PREFIX="release"
# shellcheck source=bin/lib.sh
source "$(dirname "$0")/lib.sh"

# Public release identity — the only identity allowed in public history.
NOREPLY_NAME="Samyak Jhaveri"
NOREPLY_EMAIL="39847642+SamyakJhaveri@users.noreply.github.com"

VERSION="${1:-}"
[[ -n "$VERSION" ]] || die "usage: bin/release.sh <version> (e.g., 1.1.0)"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "version must be semver (e.g., 1.2.3)"

# Operate on the script's OWN repository, not the caller cwd. release.sh runs git
# against the working directory (branch/status/tag/commit/push), while the hub-ci
# gate is resolved from the script path; without this, an absolute-path invocation
# from a different repo would validate this repo but tag and push the other one.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
SELF_REPO="$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null)"
[[ -n "$SELF_REPO" ]] || die "cannot locate the script repository (is bin/release.sh inside a git repo?)"
cd "$SELF_REPO" || die "cannot enter the script repository: $SELF_REPO"

# Pre-flight. Each git query is captured with its exit status checked: a FAILED
# git command prints nothing, and a bare `[[ -z "$(...)" ]]` or `| grep -q` would
# read that empty output as a clean tree / an absent tag and mutate anyway. Fail
# closed - refuse on any git error (matches bin/agent-sync-scan.sh, 76ad1c5).
BRANCH="$(git branch --show-current)" || die "cannot read current branch"
[[ "$BRANCH" == "main" ]] || die "releases must be created from main"
set +e; PORCELAIN="$(git status --porcelain)"; PORCELAIN_RC=$?; set -e
[[ "$PORCELAIN_RC" -eq 0 ]] || die "git status failed (exit $PORCELAIN_RC); refusing to release"
[[ -z "$PORCELAIN" ]] || die "working tree is dirty — commit or stash first"
set +e; EXISTING_TAG="$(git tag -l "v$VERSION")"; TAG_RC=$?; set -e
[[ "$TAG_RC" -eq 0 ]] || die "git tag query failed (exit $TAG_RC); refusing to release"
[[ -z "$EXISTING_TAG" ]] || die "tag v$VERSION already exists"

# assume-unchanged / skip-worktree guard (reuses bin/agent-sync-scan.sh H5,
# 72c7b5d). `git status` above is BLIND to a tracked file marked
# --assume-unchanged (lowercase ls-files -v tag) or skip-worktree (S): its
# worktree bytes can diverge from the committed bytes the tag will publish, and
# the hub-ci gate below validates the worktree. Refuse if any tracked path
# carries a non-`H` tag. Scope is the WHOLE repo (no pathspec) because the tag
# ships the whole tree - unlike H5, which scoped to .claude because the sync only
# promotes that subtree. ls-files failure fails closed.
set +e; VTAGS="$(git ls-files -v)"; VTAGS_RC=$?; set -e
[[ "$VTAGS_RC" -eq 0 ]] || die "git ls-files -v failed (exit $VTAGS_RC); refusing to release"
if grep -qvE '^H ' <<<"$VTAGS"; then
  die "a tracked file is marked assume-unchanged or skip-worktree, so its committed state cannot be trusted; refusing to release. Clear it (git update-index --no-assume-unchanged / --no-skip-worktree). Offending: $(grep -vE '^H ' <<<"$VTAGS" | tr '\n' ' ')"
fi

# Hub CI gate: refuse to cut a release while any hub health check is red. This
# runs BEFORE any mutation (the VERSION write at Step 1) and before the
# commit/tag/push, so a red gate stops the release with zero side effects.
# NOTE: hub-ci validates the live WORKTREE. The tracked-only discovery in hub-ci
# and the assume-unchanged guard just above close the two reachable ways the
# worktree can diverge from the committed objects the tag publishes (an untracked
# file running in the gate; an assume-unchanged file hidden from the clean check).
# A clean/smudge filter that rewrites content on checkout is NOT covered - that
# residual needs the gate to run against an isolated checkout of HEAD (Ticket 9).
info "running hub-ci gate"
bash "$SELF_DIR/hub-ci.sh" || die "hub-ci failed - refusing to release (run: bin/hub-ci.sh)"

# IP gate (defense-in-depth): if the private-dev sweep is present, it must pass
# in strict mode before we publish. Absent (e.g. public clone) → skip loudly.
if [[ -x "$SELF_DIR/ip-sweep.sh" ]]; then
  info "running IP sweep (strict)"
  IP_SWEEP_STRICT=1 bash "$SELF_DIR/ip-sweep.sh" || die "ip-sweep failed — refusing to release"
else
  warn "bin/ip-sweep.sh not present — skipping IP gate"
fi

# Re-verify the pre-flight invariants immediately before mutating (C2). The gates
# above (hub-ci, ip-sweep) take time, and a gate side-effect or a concurrent
# process could have staged content, moved off main, or created the tag in that
# window. Any drift -> refuse; never commit into a repo that changed under us.
[[ "$(git branch --show-current)" == "main" ]] || die "branch changed during pre-flight; refusing to release"
set +e; PORCELAIN2="$(git status --porcelain)"; PORCELAIN2_RC=$?; set -e
[[ "$PORCELAIN2_RC" -eq 0 && -z "$PORCELAIN2" ]] || die "working tree/index changed during the pre-flight gates; refusing to release"
set +e; EXISTING_TAG2="$(git tag -l "v$VERSION")"; TAG2_RC=$?; set -e
[[ "$TAG2_RC" -eq 0 && -z "$EXISTING_TAG2" ]] || die "tag v$VERSION appeared during pre-flight; refusing to release"

# Step 1: Update VERSION file
info "updating VERSION to $VERSION"
echo "$VERSION" > VERSION

# Step 2: Commit (identity hard-pinned — see header). Scoped to `-- VERSION` so
# only that file can ever land in a release commit, whatever else may be staged.
git add VERSION
git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
  commit -m "release: v$VERSION" -- VERSION

# Step 3: Tag (tagger identity hard-pinned — annotated tags record a tagger line)
git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
  tag -a "v$VERSION" -m "Release v$VERSION"

# Step 4: Push
info "pushing commit and tag"
git push origin HEAD
git push origin "v$VERSION"

ok "released v$VERSION"
echo "Copier users can now: copier copy --trust --vcs-ref v$VERSION gh:samyakjhaveri/loam ./my-project"
