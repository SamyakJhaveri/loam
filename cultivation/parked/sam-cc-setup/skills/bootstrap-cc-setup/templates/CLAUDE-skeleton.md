# CLAUDE.md - {{PROJECT_NAME}}

<!-- One paragraph: what this project is and what "done" means for it.
     This file is a map, not a tour. The codebase is the README.
     Budget: keep this file under ~800 tokens; move anything conditional
     to .claude/rules/ (path-scoped) or a skill. -->

{{PROJECT_NAME}}: <purpose - fill in one or two sentences>.

## Validation

- Run `/validate` before every substantive commit.
  A native git pre-commit hook (`scripts/pre-commit.sh`, symlinked at
  `.git/hooks/pre-commit`) runs the fast deterministic checks on every commit.
  Install once per clone: `ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit`.

## Gotchas

<!-- Empty on day one, on purpose. Add entries ONLY when a real mistake happens
     here: the command that surprised you, the invariant that got violated, the
     fix. One line each. Delete entries that stop being true. -->

(none yet)
