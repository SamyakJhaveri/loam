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

# Pre-flight
[[ "$(git branch --show-current)" == "main" ]] || die "releases must be created from main"
[[ -z "$(git status --porcelain)" ]] || die "working tree is dirty — commit or stash first"
git tag -l "v$VERSION" | grep -q . && die "tag v$VERSION already exists"

# IP gate (defense-in-depth): if the private-dev sweep is present, it must pass
# in strict mode before we publish. Absent (e.g. public clone) → skip loudly.
if [[ -x "$(dirname "$0")/ip-sweep.sh" ]]; then
  info "running IP sweep (strict)"
  IP_SWEEP_STRICT=1 bash "$(dirname "$0")/ip-sweep.sh" || die "ip-sweep failed — refusing to release"
else
  warn "bin/ip-sweep.sh not present — skipping IP gate"
fi

# Step 1: Update VERSION file
info "updating VERSION to $VERSION"
echo "$VERSION" > VERSION

# Step 2: Commit (identity hard-pinned — see header)
git add VERSION
git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
  commit -m "release: v$VERSION"

# Step 3: Tag (tagger identity hard-pinned — annotated tags record a tagger line)
git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
  tag -a "v$VERSION" -m "Release v$VERSION"

# Step 4: Push
info "pushing commit and tag"
git push origin HEAD
git push origin "v$VERSION"

ok "released v$VERSION"
echo "Copier users can now: copier copy --trust --vcs-ref v$VERSION gh:samyakjhaveri/loam ./my-project"
