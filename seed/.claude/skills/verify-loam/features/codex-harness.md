# Codex harness

A rendered project carries `.codex/` for users who work in it with Codex. Once the user trusts the project, Codex runs with the `loam` permission profile (workspace writes, network on, `.env*` unreadable), refuses the destructive commands in `.codex/rules/loam.rules`, reads `AGENTS.md` and the shared `.agents/skills/`, and, after the user reviews the hooks once, runs the same memory hooks as Claude Code through `.codex/hooks.json`.

## Sub-features

- `codex-trust` keeps the project's `.codex/` layer inert until the project is trusted.
- `codex-profile` applies `default_permissions = "loam"`: `workspace-write`, network on, reads of `.env*` and `**/.env*` denied.
- `codex-rules` refuses each `loam.rules` spelling with its justification (`Recursive delete blocked.`, `Hard reset blocked.` and the rest).
- `codex-env` stops a command from reading `.env`.
- `codex-context` gives the model `AGENTS.md` and the seed skills from `.agents/skills/`.
- `codex-hooks` runs `mem-recall.sh` on SessionStart and `mem-capture.sh` (Stop, SessionEnd, PreCompact), once the hooks are reviewed.

## How to get to it (user POV)

- Run `codex` in the project and trust it when asked; review the project's hooks when Codex asks (not driven here).
- Run `codex exec "<task>"` in a trusted project.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes; `codex` is on PATH (0.163.0 observed).
- `$C codex` costs $0: it runs `codex exec --json` against stub-model.py with `CODEX_HOME=<root>/r1/codex-home`, which has no login and trusts only this render.

- **Config loads.** Run `$C codex r1 "Reply with the single word OK." --name cx-trusted`. `permission_profile` is `loam`, `sandbox` is `workspace-write`, `network` is true, `denied` lists `<render>/**/.env*` and `<render>/.env*`, and `notices` holds `clamping SessionEnd hook timeout to 3s in <render>/.codex/hooks.json`, so `hooks.json` was read. `reply` is `OK`.
- **Inert until trusted.** Run the same with `--untrusted --name cx-untrusted`. `permission_profile` is `:read-only`, `sandbox` is `read-only`, `network` is null, `denied` is empty, and `notices` is empty. `approval_policy` is `never` in both runs (the `exec` default), so it does not tell them apart.
- **Context.** In `cx-trusted.rollout.jsonl`, a user message starts `# AGENTS.md instructions for <render>`, and the skills list has `catchup`, `fable-prompting` and `hypothesis-tree` under the root `r2` = `<render>/.agents/skills`.
- **Rule holds.** Run `mkdir -p <root>/r1/render/deny-probe && touch <root>/r1/render/deny-probe/keep`, then `$C codex r1 "STUB_BASH: ls deny-probe ;; rm -rf deny-probe" --name cx-deny`. `commands` shows `ls deny-probe` with output `keep`, the second `tool_outputs` entry contains `rejected: Recursive delete blocked.`, and `ls <root>/r1/render/deny-probe` still shows `keep`.
- **Rule control.** Run the same with `--untrusted --name cx-deny-untrusted`. Codex's own check still refuses `rm -rf`, but with `rm -f style commands are not permitted. Use a safer approach`. Only the `Recursive delete blocked.` justification proves `loam.rules` fired.
- **A rule Codex lacks.** Run `$C codex r1 "STUB_BASH: ls deny-probe ;; git reset --hard" --name cx-reset`; the second output contains `rejected: Hard reset blocked.`. Save `<root>/r1/render/.codex/rules/loam.rules`, delete its `"reset", "--hard"` line, and rerun with `--name cx-reset-norule`: the command now runs and exits 128 with `fatal: Unable to create '<render>/.git/index.lock': Operation not permitted`, because the sandbox keeps `.git` read-only. Put the saved file back.
- **.env denied.** Run `printf 'PROBE=1\n' > <root>/r1/render/.env`, then `$C codex r1 "STUB_BASH: ls deny-probe ;; cat .env" --name cx-env`. The second output is `cat: .env: Operation not permitted` with exit code 1. Control: with `--untrusted --name cx-env-untrusted` it prints `PROBE=1` with exit code 0.
- **Hooks wait for review.** With no memstore yet, run `$C codex r1 "Reply with the single word OK." --name cx-hooks`. No `<root>/r1/memstore/traces/render/INDEX.md` appears.
- **Hooks run once reviewed.** Run the same with `--bypass-hook-trust --name cx-hooks-bypass`, which stands in for the review. `notices` warns that `--dangerously-bypass-hook-trust` is enabled, and INDEX.md gains one line keyed by the full thread id, with the prompt in its last column.
- **Recall.** Run it again with `--bypass-hook-trust --name cx-recall`. `cx-recall.rollout.jsonl` holds a `developer` message starting `## Memory (render)` with `Loaded: 1 recent sessions`.
- **Proof.** `<name>.jsonl` (exec events), `<name>.rollout.jsonl` (effective settings and every tool output) and `<name>.stub-requests.jsonl` in evidence; copy INDEX.md into evidence before cleanup.

## Gotchas

- A policy rejection or a sandbox-denied command does not appear as a `command_execution` item in the `--json` stream. Read `tool_outputs`, which come from the rollout.
- The user's shell may wrap `codex` in a function with its own flags (here `--ask-for-approval on-request`), which override the project's `approval_policy`. control-loam calls the binary on PATH.
- The model is pinned to `gpt-5.5`: under the catalog default (`gpt-6.1-sol` in 0.163.0) the request carries no tools, so `STUB_BASH` cannot run a command.
- The interactive trust prompt and the one-time hook review are not driven. `--bypass-hook-trust` skips the review for one invocation and saves nothing.
- `CODEX_HOME` is isolated, but the user-level skills root `~/.agents/skills` still loads (`r0` in the skills list).
- Cleanup removes `codex-home`, so `$C codex` copies each rollout into evidence.
