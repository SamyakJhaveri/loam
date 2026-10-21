---
name: install-pstack-skills
disable-model-invocation: true
description: "Installs agent-invocable copies of 23 pstack skills (blast-radius, interrogate, how, why, tdd, the principle skills and more) into ~/.claude/skills/ from the newest installed pstack, and refreshes them after a pstack update. Manual only: type /sam-cc-setup:install-pstack-skills on each host."
---

# Install pstack skills for agents

pstack ships every skill as manual-only (`disable-model-invocation: true`), and `skillOverrides` cannot change a plugin skill.
This skill runs the installer beside it, which copies each listed skill from the newest installed pstack into `~/.claude/skills/<name>/` without that line, with its links into the plugin made absolute, and a `.pstack-install` marker.
A re-run refreshes the copies the installer made, refuses any other folder of the same name, and never writes to the plugin cache.
The copies are user-level, so they join every session's skill listing on that host.

**Trigger:** the user types `/sam-cc-setup:install-pstack-skills`. Manual only.

## Steps

1. Run the installer with one Bash call and show its full output:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/install-pstack-skills/install-pstack-skills"
   ```

2. Report the pstack version it installed from and any `REFUSED` or `FAILED` line.
   A `REFUSED` folder is not the installer's: the user decides whether to move it aside and re-run.
   The lock message means another install is running; if none is, the user removes `~/.claude/skills/.pstack-install.lock` and re-runs.
3. Do not edit the copies or the plugin cache by hand. Re-run this skill instead after each pstack update.

How agents use the copies, and which pstack skills stay human-only: the project's `docs/WORKERS.md`, pstack section.
