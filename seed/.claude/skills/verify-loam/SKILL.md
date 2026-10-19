---
name: verify-loam
description: "Prove a Loam change in a real rendered project: copier-render this checkout, then drive headless and interactive Claude Code sessions, stubbed Codex runs and copier updates in the render and capture hook, memory, deny-rule, update and check evidence. Use before shipping any seed, hook, settings or copier.yml change."
disable-model-invocation: true
---

# Verify Loam

Loam's product is the project it renders.
A change is proven when a fresh render of this checkout behaves right under a real Claude Code session, not when `bin/check` passes.
`bin/check` and `bin/tests/test_render_smoke.py` check files; this skill checks behavior: hooks fire, memory carries across sessions, deny rules hold, the rendered check passes clean and fails on a planted defect.

All driving goes through one CLI, run from the Loam root:

```bash
C=.claude/skills/verify-loam/control-loam
$C --help            # commands; each prints one JSON object
```

This skill is Loam-only: `copier.yml` excludes `.claude/skills/verify-loam`, so it never reaches a rendered project.

## Launch

```bash
$C render --run <id>            # copier copy of this checkout into $TMPDIR/loam-verify/<id>/render
$C render --run <id> --ref v3.0.0 --kind typescript
```

- Default `--ref HEAD` renders the working tree: copier turns a dirty checkout into a temporary commit, so uncommitted seed edits are included. `doctor` says which case you got.
- Ready means `render` printed `"ok": true` and `doctor` passes. A render takes about 4 seconds.
- Every run is its own directory, so runs can go in parallel. Every `claude` and `codex` child points the memory hooks at `<run>/memstore` through `LOAM_MEMSTORE`, unsets `LOAM_MEMSTORE_REMOTE` and gets `TMPDIR=<run>/tmp`, so a run never touches `~/memstore`, pushes anywhere, or shares temp files; only Claude Code's sandboxed Bash tool swaps in its own `/tmp/claude-<uid>`.
- Sessions use `--setting-sources project,local`: the render's own settings and hooks apply, your user-level hooks and plugins do not.

## Doctor

```bash
$C doctor <id>
```

Read-only on the render; it records its result in `run.json`. Checks: the render exists and holds the copier initial commit, `_commit` matches the recorded commit (for a dirty tree, copier's WIP commit one past it), every hook command in the rendered `.claude/settings.json` exists and is executable, and `claude` is on PATH (with its version).
Run it before the first drive and again after any drive that surprised you.

## Drive

Headless, one turn, full hook stream:

```bash
$C session <id> "Reply with the single word OK." --name mem-1
$C session <id> "<prompt>" --model fable      # any claude --model value
$C session <id> "<prompt>" --bypass           # bypassPermissions; deny rules still apply
$C session <id> "<prompt>" --stub             # scripted model on 127.0.0.1; $0
$C session <id> "/compact" --resume mem-1     # continue an earlier session of this run
$C session <id> "<prompt>" --switch-model fable   # switch models first; fires PostModelSwitch
```

The JSON gives `hooks` (event, name, exit code, first 400 characters of stdout), `skills` from the init event, `permission_denials`, the reply, and `cost_usd` (about $0.12 per one-word turn on the default model; Fable costs about five times as much).

`--stub` answers from [`stub-model.py`](stub-model.py), a scripted Messages API started on a free 127.0.0.1 port for that session alone; only the `claude` child gets `ANTHROPIC_BASE_URL` and a dummy key.
It replies `OK`, or, for a prompt holding `STUB_BASH: cmd1 ;; cmd2`, runs each command through Bash in turn.
Claude Code, hooks, settings and deny rules stay real, so it proves wiring at $0 in 1 to 4 seconds: hooks fire, memory is captured and recalled, a deny rule refuses.
It cannot prove that a real model reads or obeys injected text; quote-back and the Fable brief stay paid.
The JSON adds `"stub": true` and `stub_requests`, and its `cost_usd` is an estimate from fake token counts.
Zero requests or a failed session give `"ok": false`, so a Claude Code wire-format change never reads as a pass.

`--resume` takes a `--name` recorded in this run's `run.json`, or a raw session id; the resumed session keeps its id.
`--switch-model` sends a `set_model` control request, then the prompt, on stream-json stdin; it fires `PostModelSwitch` and saves nothing.
Never type `/model` in `tui`: it writes the model to the user's `~/.claude/settings.json`.

Interactive, in tmux, for anything headless cannot show:

```bash
$C tui <id> start --model fable    # accepts the workspace-trust prompt for this render only
$C tui <id> send "<message>"       # submits, waits until the turn finishes, returns the screen
$C tui <id> stop --name fable-tui  # saves the screen to evidence, sends /exit (fires SessionEnd)
```

Watch it live with `tmux attach -t loamv-<id>`.
When a prompt such as a permission request waits on you, `send` exits 1 with `"state": "dialog"`; answer it there.

Codex, one `codex exec` in the render against the stub, $0:

```bash
$C codex <id> "<prompt>" --name cx-1          # trusted render; STUB_BASH works as for session --stub
$C codex <id> "<prompt>" --untrusted          # the project's .codex/ layer stays inert
$C codex <id> "<prompt>" --bypass-hook-trust  # runs .codex/hooks.json without the one-time review
```

It sets `CODEX_HOME=<run>/codex-home`, which holds no login and trusts only this render, so the user's `~/.codex` is never read or changed; stub-model.py answers the Responses API.
The JSON gives the settings the session ran with (`approval_policy`, `permission_profile`, `sandbox`, `network`, `denied`), each command, every tool output (a policy rejection shows only there), Codex's notices, the reply and `stub_requests`.
Zero requests or a failed turn give `"ok": false`.

Template update, the user's `copier update`:

```bash
$C update <id> --ref HEAD     # copier update --trust --defaults in the render
```

It commits nothing and reports `commit_before`, `commit_after` (`_commit` in `.copier-answers.yml`), the number of changed paths and the files with conflict markers, then points `run.json` at the new ref so `doctor` checks it.
Copier refuses a dirty tree and a downgrade; [`features/copier-update.md`](features/copier-update.md) has the recipe.

Rendered checks:

```bash
$C check <id>      # the render's bin/check; expect a last line starting "check: PASSED"
```

A fresh render has no `tests/`, so that check runs no pytest and a pass alone proves little; [`features/render.md`](features/render.md) shows how to see it fail.
`doctor` and `check` record their last outcome in `run.json`.
`bin/release.sh` tags only a HEAD with a clean-tree run (`"dirty": false`) whose doctor and check are both ok, the check run on a pristine render (`"pristine": true`: copier's one commit, nothing edited).

## Sweep

```bash
$C sweep          # render, doctor, mem-1 then mem-2 recall, the deny probe with its ls control, the rendered check
```

It runs the `--stub` recipes of the feature map in one $0 pass of about 10 seconds and cleans up after a pass; a failed run is kept.
The first failure exits 1 with `failed` naming the recipe and `log_tail` from its evidence; zero stub requests is a failure.
CI runs it on every push and PR (job `stub-sweep` in `.github/workflows/test.yml`).

## Evidence

Everything lands in `<run>/evidence/`: `render.log`, `<name>.jsonl` (the stream-json with hook events), `<name>.stderr`, `<name>.transcript.jsonl`, `<name>.stub-requests.jsonl` (one line per stub request), `<name>.rollout.jsonl` (Codex), `<name>.screen.txt`, `check.txt`, `update.log`.

Proof standards:

- Drive the user path: a real `claude` session in a real render. Piping JSON into a hook script by hand proves the script, not the harness.
- Show the trigger and the result: the hook event in the stream and the state it produced (a trace in the memstore, text the model can quote back).
- Prove side effects with a second view: memory capture is proven by the next session's recall, a denial by the file that survived.
- Give every negative claim a control. A denial means nothing unless an allowed command ran in the same session.
- Report a feature you could not reach as unreachable with the command tried and the missing precondition; never as passing.

## Cleanup

```bash
$C cleanup <id> --dry-run   # lists what it would remove
$C cleanup <id>
```

It kills the run's tmux session, removes `render/`, `memstore/`, `tmp/`, `codex-home/` and the `~/.claude/projects/` directory of this render, and keeps `evidence/` and `run.json`.
It never kills by process name and never touches another run.
After cleanup, list `<run>/evidence/` to confirm the proof is still there.

## Feature map

The behavior inventory is in [`features/README.md`](features/README.md), one file per feature with the same four sections.
`$C sweep` runs only the `--stub` recipes; for a broad regression pass, walk the index top to bottom.
Upkeep is `/pstack:maintain-verification-skill` (pstack is installed): a source wave plus one live pass, with edits inside this directory.
A daily launchd job runs it; see `docs/HARNESS-LOAM.md`.
