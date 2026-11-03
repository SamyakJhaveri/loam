#!/usr/bin/env bash
# release.sh - tag a new Loam release. Usage: bin/release.sh X.Y.Z
# The merged release/X.Y.Z PR bumped VERSION and carries the release's proofs. Run this with HEAD
# detached at that PR's merge commit: it runs the local preconditions, tags that commit, and
# pushes only the tag, never main.
set -euo pipefail
LIB_PREFIX="release"
source "$(dirname "$0")/lib.sh"

NOREPLY_NAME="Samyak Jhaveri"
NOREPLY_EMAIL="39847642+SamyakJhaveri@users.noreply.github.com"

VERSION="${1:-}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "usage: bin/release.sh X.Y.Z"

# Push only the tag (main's ruleset covers the branch, not the tag), then render the tag from GitHub the way users do.
publish() {
  # --no-follow-tags: a push.followTags setting would also push any other annotated tag behind the merge.
  git push --no-follow-tags origin "refs/tags/v$VERSION" \
    || die "tag push failed; fix the cause and rerun bin/release.sh $VERSION (it resumes at the push)"
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
# Before any push, on the resume path too: the rules could have changed since the first run.
require_ci_checks

# The release commit is the merge commit of the release/X.Y.Z PR merged into main. --state merged
# passes over a closed earlier attempt with the same head branch; --base main over one merged elsewhere.
PR="$(gh pr list --head "release/$VERSION" --base main --state merged --json state,mergeCommit \
  --jq '.[0] // empty | "\(.state) \(.mergeCommit.oid // "")"')" \
  || die "cannot read the pull request from release/$VERSION (gh pr list --head release/$VERSION failed)"
[[ -n "$PR" ]] || die "no merged pull request from release/$VERSION into main; open one that bumps VERSION to $VERSION with the release's proof outputs in its body, and merge it once CI is green"
read -r STATE MERGE <<<"$PR"
[[ "$STATE" == "MERGED" && -n "${MERGE:-}" ]] || die "the pull request from release/$VERSION is '$STATE', not MERGED with a merge commit"
# HEAD itself, not a descendant: every gate below reads HEAD or the checked-out tree.
[[ "$(git rev-parse HEAD)" == "$MERGE" ]] \
  || die "HEAD is $(git rev-parse HEAD), not $MERGE, the merge commit of release/$VERSION; run git fetch origin && git checkout --detach $MERGE"
GOT="$(git show "$MERGE:VERSION" 2>/dev/null || true)"
[[ "$GOT" == "$VERSION" ]] || die "VERSION at the merge commit $MERGE of release/$VERSION is '$GOT', not $VERSION"
[[ -z "$(git status --porcelain --untracked-files=all)" ]] || die "working tree is dirty"

REMOTE_TAG="$(git ls-remote --tags origin "refs/tags/v$VERSION")" || die "cannot read origin's tags (git ls-remote --tags origin failed)"
[[ -z "$REMOTE_TAG" ]] || die "tag v$VERSION is already on origin, so it is public; release the next version"
# Rerun after a failed tag push: the annotated tag exists locally at the merge commit.
LOCAL_TAG="$(git rev-parse -q --verify "refs/tags/v$VERSION^{commit}" || true)"
if [[ -n "$LOCAL_TAG" ]]; then
  [[ "$LOCAL_TAG" == "$MERGE" && "$(git cat-file -t "refs/tags/v$VERSION")" == "tag" ]] \
    || die "local tag v$VERSION is not an annotated tag at the merge commit $MERGE; delete it (git tag -d v$VERSION) and rerun"
  warn "tag v$VERSION exists locally at the merge commit but not on origin; resuming at the push"
fi

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
# IDENTITY_ONLY=0: an exported IP_SWEEP_IDENTITY_ONLY=1 must not shrink this to the identity check.
IP_SWEEP_STRICT=1 IP_SWEEP_IDENTITY_ONLY=0 bash "$SELF/bin/ip-sweep.sh" || die "ip-sweep failed"

if [[ -z "$LOCAL_TAG" ]]; then
  git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" tag -a "v$VERSION" -m "Release v$VERSION" "$MERGE"
fi
publish
