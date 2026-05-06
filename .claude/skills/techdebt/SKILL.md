# .claude/skills/techdebt/SKILL.md
---
name: techdebt
description: >
  Scan for tech debt: duplicated logic, dead code, magic numbers.
  Run at end of every session before final commit.
model: opus
allowed-tools: [Read, Grep, Glob, Edit, Bash(bun run typecheck:*)]
---
 
Scan recently changed files (git diff --name-only HEAD~5) for:
1. Duplicated logic — consolidate into shared utility
2. Dead code — unused imports/exports/functions (grep to verify before removing)
3. Magic numbers/strings — extract to named constants
4. Nested conditionals >3 levels — refactor with early returns
5. TODO/FIXME — list but don't auto-fix without asking
 
For each finding: file:line, category, description, proposed fix
Ask before applying fixes that touch >3 files.
After fixes: run bun run typecheck to confirm no regressions.
