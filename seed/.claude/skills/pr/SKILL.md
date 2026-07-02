---
name: pr
description: >
  Push and open a GitHub PR. Use when user says "open a PR", "create a pull
  request", or "push and PR". NOT for: committing changes (use /commit),
  running validation (use /validate), or reviewing code (use /multi-review) — only the push-and-PR step.
model: sonnet
allowed-tools:
  - Bash(git push:*)
  - Bash(git log:*)
  - Bash(gh pr create:*)
  - Bash(gh pr view:*)
---

<recent_commits>
!`git log --oneline -10 --no-merges`
</recent_commits>

<branch>
!`git branch --show-current`
</branch>

1. Push: `git push -u origin HEAD`.
2. Write PR title: type + concise description (under 72 chars).
3. Write PR body: what changed, why, how to test, risks.
4. For multi-line bodies, use a HEREDOC: `gh pr create --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"`.
5. Output PR URL.

If push fails: stop and report the exact error. Do NOT force push.
