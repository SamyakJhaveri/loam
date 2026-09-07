#!/usr/bin/env bash
# release.sh - tag a new Loam release. Usage: bin/release.sh X.Y.Z
# CI gated the tree on the PR; this runs the local preconditions, then bumps
# VERSION, commits, tags, and pushes atomically.
set -euo pipefail
LIB_PREFIX="release"
source "$(dirname "$0")/lib.sh"

NOREPLY_NAME="Samyak Jhaveri"
NOREPLY_EMAIL="39847642+SamyakJhaveri@users.noreply.github.com"

VERSION="${1:-}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "usage: bin/release.sh X.Y.Z"

SELF="$(cd "$(dirname "$0")/.." && pwd)"; cd "$SELF"
[[ "$(git branch --show-current)" == "main" ]] || die "release from main only"
git fetch origin main --quiet
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || die "main is not equal to origin/main"
[[ -z "$(git status --porcelain --untracked-files=all)" ]] || die "working tree is dirty"
[[ -z "$(git tag -l "v$VERSION")" ]] || die "tag v$VERSION already exists"

# The latest run on HEAD must be green. Keyed off the workflow NAME in test.yml.
STATUS="$(gh run list --commit "$(git rev-parse HEAD)" --workflow Test --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "")"
[[ "$STATUS" == "success" ]] || die "latest Test run on HEAD is '$STATUS', not success"

# The one local gate CI cannot run: the private IP terms file is off-GitHub.
if [[ -x "$SELF/bin/ip-sweep.sh" ]]; then
  IP_SWEEP_STRICT=1 bash "$SELF/bin/ip-sweep.sh" || die "ip-sweep failed"
else
  warn "bin/ip-sweep.sh absent - skipping IP gate"
fi

echo "$VERSION" > VERSION
git add VERSION
GITID=(-c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL")
git "${GITID[@]}" commit -m "release: v$VERSION" -- VERSION
RELEASE_COMMIT="$(git rev-parse HEAD)"
git "${GITID[@]}" tag -a "v$VERSION" -m "Release v$VERSION" "$RELEASE_COMMIT"
git push --atomic origin "${RELEASE_COMMIT}:refs/heads/main" "refs/tags/v$VERSION"
ok "released v$VERSION"
