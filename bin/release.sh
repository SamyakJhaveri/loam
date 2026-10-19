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

# Push the release commit and tag atomically, then render the tag from GitHub the way users do.
publish() {
  git push --atomic origin "$(git rev-parse HEAD):refs/heads/main" "refs/tags/v$VERSION" \
    || die "push failed; fix the cause and rerun bin/release.sh $VERSION (it resumes at the push)"
  COPIER=(copier); command -v copier >/dev/null 2>&1 || COPIER=(uvx copier)
  OUT="$(mktemp -d)"
  "${COPIER[@]}" copy --trust --defaults --vcs-ref "v$VERSION" --data project_name=release-check \
    --data github_repo= gh:samyakjhaveri/loam "$OUT/render" >"$OUT/render.log" 2>&1 \
    || die "v$VERSION IS PUSHED BUT DOES NOT RENDER from gh:samyakjhaveri/loam; log: $OUT/render.log"
  ok "released v$VERSION; rendered from gh:samyakjhaveri/loam into $OUT/render"
}

# Main's rules must make a red CI run block a merge. The contexts are the job ids in test.yml.
require_ci_checks() {
  local have missing="" c
  have="$(gh api 'repos/{owner}/{repo}/rules/branches/main' \
    --jq '.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context')" \
    || die "cannot read the rules on main (gh api repos/{owner}/{repo}/rules/branches/main failed)"
  for c in verify stub-sweep; do
    grep -qxF "$c" <<<"$have" || missing="${missing:+$missing, }$c"
  done
  [[ -z "$missing" ]] || die "main's active rules do not require the status check(s) $missing; a red CI run would not block a merge. Add them to the main ruleset in Settings, Rules"
}

SELF="$(cd "$(dirname "$0")/.." && pwd)"; cd "$SELF"
[[ "$(git branch --show-current)" == "main" ]] || die "release from main only"
git fetch origin main --quiet
# Rerun after a failed push: HEAD is the release commit, its tag points at it, origin/main is its parent.
if [[ "$(git log -1 --format=%s)" == "release: v$VERSION" &&
      "$(git rev-parse -q --verify "refs/tags/v$VERSION^{commit}")" == "$(git rev-parse HEAD)" &&
      "$(git rev-parse HEAD^)" == "$(git rev-parse origin/main)" ]]; then
  warn "release commit and tag v$VERSION exist locally but not on origin; resuming at the push"
  publish
  exit 0
fi
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
  || die "main is not equal to origin/main; run git pull --ff-only. If HEAD is an unpushed 'release:' commit from an earlier run, drop it and its tag first: git tag -d vX.Y.Z && git reset --keep HEAD^"
[[ -z "$(git status --porcelain --untracked-files=all)" ]] || die "working tree is dirty"
[[ -z "$(git tag -l "v$VERSION")" ]] \
  || die "tag v$VERSION already exists. If origin has it (git ls-remote --tags origin v$VERSION) it is public: fix main and release the next version. If not, delete it (git tag -d v$VERSION) and rerun"

require_ci_checks

# The latest run on HEAD must be green. Keyed off the workflow NAME in test.yml.
STATUS="$(gh run list --commit "$(git rev-parse HEAD)" --workflow Test --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "")"
[[ "$STATUS" == "success" ]] || die "latest Test run on HEAD is '$STATUS', not success"

# CI checks files; a live render of this exact HEAD must also pass verify-loam's doctor and check (no model calls).
VERIFY_ROOT="${LOAM_VERIFY_ROOT:-${TMPDIR:-/tmp}/loam-verify}"
RUN="v$VERSION-$(git rev-parse --short=8 HEAD)"
python3 - "$VERIFY_ROOT" "$(git rev-parse HEAD)" <<'PY' || die "no clean-tree verify-loam run of HEAD with doctor ok and check ok on the unedited render under $VERIFY_ROOT; make one: C=.claude/skills/verify-loam/control-loam; \$C render --run $RUN && \$C doctor $RUN && \$C check $RUN"
import json, pathlib, sys
root, head = pathlib.Path(sys.argv[1]), sys.argv[2]
runs = [json.loads(f.read_text()) for f in root.glob("*/run.json")]
sys.exit(not any(m.get("commit") == head and m.get("dirty") is False and m.get("doctor", {}).get("ok")
                 and m.get("check", {}).get("ok") and m.get("check", {}).get("pristine") for m in runs))
PY

# The one local gate CI cannot run: the private IP terms file is off-GitHub.
IP_SWEEP_STRICT=1 bash "$SELF/bin/ip-sweep.sh" || die "ip-sweep failed"

echo "$VERSION" > VERSION
git add VERSION
GITID=(-c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL")
git "${GITID[@]}" commit -m "release: v$VERSION" -- VERSION
RELEASE_COMMIT="$(git rev-parse HEAD)"
git "${GITID[@]}" tag -a "v$VERSION" -m "Release v$VERSION" "$RELEASE_COMMIT"
publish
