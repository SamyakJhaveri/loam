#!/usr/bin/env bash
# GitHub repo setup for Copier post-generation. Assumes remote name "origin".
# Usage: _gh_setup.sh <owner/repo[.git]>
set -euo pipefail

[[ -z "${1:-}" ]] && { echo "[copier] Usage: _gh_setup.sh <owner/repo>"; exit 1; }

REPO="${1%.git}"

if ! command -v gh >/dev/null 2>&1; then
  echo "[copier] gh CLI not found. To connect GitHub, run:"
  echo "  gh repo create \"${REPO}\" --private --source=. --remote=origin --push"
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "[copier] gh not authenticated. Run 'gh auth login' first, then:"
  echo "  gh repo create \"${REPO}\" --private --source=. --remote=origin --push"
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"

if gh repo view "${REPO}" >/dev/null 2>&1; then
  echo "[copier] Repo ${REPO} already exists; connecting..."
  git remote add origin "https://github.com/${REPO}.git" 2>/dev/null ||
    git remote set-url origin "https://github.com/${REPO}.git"
  if ! git push -u origin "${BRANCH}"; then
    echo "[copier] Push failed; the remote may have existing commits."
    echo "  Try: git pull --rebase origin ${BRANCH} && git push -u origin ${BRANCH}"
  fi
else
  echo "[copier] Creating repo ${REPO}..."
  gh repo create "${REPO}" --private --source=. --remote=origin --push ||
    echo "[copier] Repo creation failed. Create it by hand: https://github.com/new"
fi

# Repository ruleset on the default branch: pull request plus a green `check`,
# no bypass actors. Without it, main is directly pushable; docs/HARNESS.md
# states that case. Needs admin rights on the repo, so the call can legitimately
# fail on a token scope or a plan that lacks rulesets.
if gh api --method POST "/repos/${REPO}/rulesets" \
  --input - >/dev/null 2>&1 <<'RULESET'
{
  "name": "loam-default-branch",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "pull_request" },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [ { "context": "check" } ]
      }
    }
  ]
}
RULESET
then
  echo "[copier] Ruleset added: the default branch needs a PR and a green 'check'."
else
  echo "[copier] Ruleset call failed; the default branch is directly pushable."
  echo "  Add it by hand under repo Settings > Rules, or re-run with an admin token."
fi
