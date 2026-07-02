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
  echo "[copier] Repo ${REPO} already exists — connecting..."
  git remote add origin "https://github.com/${REPO}.git" 2>/dev/null ||
    git remote set-url origin "https://github.com/${REPO}.git"
  if ! git push -u origin "${BRANCH}"; then
    echo "[copier] Push failed — remote may have existing commits."
    echo "  Try: git pull --rebase origin ${BRANCH} && git push -u origin ${BRANCH}"
  fi
else
  echo "[copier] Creating repo ${REPO}..."
  gh repo create "${REPO}" --private --source=. --remote=origin --push ||
    echo "[copier] Repo creation failed. Create manually: https://github.com/new"
fi
