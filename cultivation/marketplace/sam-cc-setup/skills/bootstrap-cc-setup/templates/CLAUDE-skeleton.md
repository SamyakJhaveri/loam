# CLAUDE.md - {{PROJECT_NAME}}

<!-- One paragraph: what this project is and what "done" means for it.
     This file is a map, not a tour. The codebase is the README.
     Budget: keep this file under ~800 tokens; move anything conditional
     to .claude/rules/ (path-scoped) or a skill. -->

{{PROJECT_NAME}}: <purpose - fill in one or two sentences>.

## Pipeline gate

- `/validate` must pass before every commit.
  The sam-cc-setup plugin's pre-commit hook enforces this via the `.validation_passed`
  sentinel, which is deleted on any edit.
- Add `.validation_passed` to `.gitignore`.

## Gotchas

<!-- Empty on day one, on purpose. Add entries ONLY when a real mistake happens
     here: the command that surprised you, the invariant that got violated, the
     fix. One line each. Delete entries that stop being true. -->

(none yet)
