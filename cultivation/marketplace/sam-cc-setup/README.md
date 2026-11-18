# sam-cc-setup

The portable core of Sam's Claude Code setup.
Cut to three skills in v3.0.0 under design law 7: the burden of proof is on keeping, and everything with zero recorded use is parked, not shipped.
Since v3.0.0 it has gained the `brief` skill and the factory grader agents `judge` and `reviewer`.

**Audience:** repositories that want optional planning-review and cross-model review skills.
This includes projects rendered by [Loam](https://github.com/SamyakJhaveri/loam).

## What the plugin exposes after installation

- **Skill `pstack`, model-invocable:** Claude calls it before a task; it picks a pstack method from a table and the principle list and names the pstack `SKILL.md` to read (`docs/PSTACK.md`).
- **Skills (10), manual-only, so type `/<name>`:** `audit` (the owner's end-of-work audit prompt, lightly edited, on a plan or finished work: blind Fable and Codex review, Opus verifiers and fixers, a surprise-me agent, a six-part report under 400 words, then the fixed work), `brief` (turns a raw request into a factory brief and ticket), `codex-review` (read-only cross-model second opinion on a diff; requires the Codex CLI), `factory-watch` (one read of `bin/factory status` per call, reporting stopped runs, opened PRs and failing preconditions; for a loop, type the plain prompt the skill's description gives, since a `/loop` fire cannot run a manual-only skill), `plan-review` (blind merged plan review: correctness checklist plus elegance gate in one unit), `research-gap` (research questions and literature gap checks ending in one cheap validation, with a reading log whose quotes are checked against the PDFs; its scripts need Python 3 and poppler's `pdftotext`), `run-spec` (a spec's ticket graph as one branch and PR, parallel workers in worktrees), `surprise-me` (a better route to a named goal than the current plan: ranked, evidence-backed ideas from independent lenses, with one run as proof), and owner copies of two pstack skills with the owner's edits, which the `pstack` router reads by path: `principle-explain-the-number` (an eval gap inside the run-to-run spread is reported as no measurable difference; ceilings, rubrics that reward defects, and shared-host contention are ruled out) and `reflect` (reviewers write findings files under the session's agent cap, and the synthesizer reads those files).
- **Agents (4):** `plan-reviewer`, used by `plan-review`; `lean-critic`, a read-only Opus 5.5 critic that cuts verbosity from code and prose another model wrote; `judge` and `reviewer`, the fresh-context graders the Loam factory runs on each ticket (`docs/factory/LOOP.md`).
- Regenerate both counts with `find cultivation/marketplace/sam-cc-setup -name SKILL.md | wc -l` and `ls cultivation/marketplace/sam-cc-setup/agents`.
- **Hooks (4), in `hooks/hooks.json`:** `agent-route.py` (PreToolUse on `Agent`) refuses the built-in `general-purpose` and `Explore` agents, naming `worker` and `scout`, when those agents are defined; `no-foreground-sleep.py` (PreToolUse on `Bash`) refuses a foreground `sleep` or sleep-poll loop, naming `run_in_background`, a job waiter and Monitor; `remote-command-shape.py` (PreToolUse on `Bash`) refuses an `ssh`, `scp` or `gh` call that settings `sandbox.excludedCommands` exempts but whose shape makes the sandbox run it anyway (a local pipe, redirect, heredoc, `$(`, `<(` or brace expansion, a chain part that is not itself excluded, or `$(`, a backtick, `<(` or `=name` inside its quoted arguments), and prints the bare rewrite; `prompt-context.py` (UserPromptSubmit) adds each message's time and turns each `/pstack:<name>` into a read-by-path line.
- The three PreToolUse hooks break design law 3 (no hook on a tool matcher): the law now has this exception, because the prose rules against both mistakes failed in use (one audited session spawned `general-purpose` 17 times, 4 of them after a review restated the rule). Each hook is a short local script with a 5-second timeout; the sleep hook scans for the shell forms an agent plausibly writes and lists its known gaps in its docstring. The remote-shape hook's rules are the shapes measured to fail or run bare on 17 Nov 2026; ssh, scp and gh calls in one audited session kept failing on them while a written rule stated them.
- **Workflows:** none.

Everything else that used to ship here now sits unmodified in `cultivation/parked/sam-cc-setup/`, preserving its subpaths: 23 skills, 5 agents, the `hooks/` directory (`protect-paths`, `check_stale_counts`, `generated-file-guard`, `concurrent-checkout-guard`, `codex-review-reminder`, `pre-commit`, and their control suites), the `plan-review-fanout` workflow, and `THIRD_PARTY_LICENSES/`.
Parked assets are kept for reference and can be promoted again when a real project uses one.

## What it cannot ship

Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
A Loam-rendered project already carries that layer.
The `bootstrap-cc-setup` skill that wrote it for non-Loam repos is parked.

## Versioning

Semver in `.claude-plugin/plugin.json`, kept equal to the `sam-cc-setup` entry in `cultivation/marketplace/.claude-plugin/marketplace.json`.
Bump both by hand when plugin content changes, and record the change in `cultivation/marketplace/UPGRADING.md`.
The `release/X.Y.Z` PR bumps only the top-level `VERSION` (the Copier template version), and `bin/release.sh` writes no file and never touches either plugin version field.
