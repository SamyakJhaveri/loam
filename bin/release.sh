#!/usr/bin/env bash
# release.sh — tag a new template release.
#
# Usage: bin/release.sh <version>  (e.g., bin/release.sh 1.1.0)
#
# Steps: (1) update VERSION, (2) commit, (3) tag, (4) push commit + tag.

set -euo pipefail

die() { printf 'release: %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m[release]\033[0m %s\n' "$*"; }
ok() { printf '\033[32m[ok]\033[0m %s\n' "$*"; }

VERSION="${1:-}"
[[ -n "$VERSION" ]] || die "usage: bin/release.sh <version> (e.g., 1.1.0)"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "version must be semver (e.g., 1.2.3)"

# Pre-flight
[[ "$(git branch --show-current)" == "main" ]] || die "releases must be created from main"
[[ -z "$(git status --porcelain)" ]] || die "working tree is dirty — commit or stash first"
git tag -l "v$VERSION" | grep -q . && die "tag v$VERSION already exists"

# Step 1: Update VERSION file
info "updating VERSION to $VERSION"
echo "$VERSION" > VERSION

# Step 2: Commit
git add VERSION
git commit -m "release: v$VERSION"

# Step 3: Tag
git tag -a "v$VERSION" -m "Release v$VERSION"

# Step 4: Push
info "pushing commit and tag"
git push origin HEAD
git push origin "v$VERSION"

ok "released v$VERSION"
echo "Copier users can now: copier copy --vcs-ref v$VERSION gh:samyakjhaveri/project-seed-framework ./my-project"
