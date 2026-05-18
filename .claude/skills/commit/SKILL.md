---
name: commit
description: >
  Create a conventional commit. Use when user says "commit", "make a commit",
  or "save changes". NOT for: drafting code, running tests, or anything that
  changes files — this skill only stages and commits already-finished work.
model: haiku
allowed-tools:
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git status:*)
  - Bash(git diff:*)
argument-hint: "[optional commit message override]"
---

<git_status>
!`git status --short`
</git_status>

<staged_diff>
!`git diff --cached`
</staged_diff>

1. Review the staged diff above.
2. Write a Conventional Commit message: feat: / fix: / chore: / docs: / refactor: / test: / perf:
3. If `$ARGUMENTS` is provided, use it as the commit subject.
4. Format: `<type>(<optional-scope>): <subject>` — subject under 72 chars.
5. Run: `git commit -m "<message>"`
6. Run: `git status` to confirm clean state.
7. Output the commit hash and message.
