---
name: verify-loam
description: "Prove a Loam change in a real rendered project: copier-render this checkout, then drive headless and interactive Claude Code sessions in the render and capture hook, memory, deny-rule and check evidence. Use before shipping any seed, hook, settings or copier.yml change."
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
- Every run is its own directory, so runs can go in parallel. Sessions point the memory hooks at `<run>/memstore` through `LOAM_MEMSTORE` and unset `LOAM_MEMSTORE_REMOTE`, so a run never touches `~/memstore` or pushes anywhere.
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
```

The JSON gives `hooks` (event, name, exit code, first 400 characters of stdout), `skills` from the init event, `permission_denials`, the reply, and `cost_usd` (about $0.12 per one-word turn on the default model; Fable costs about five times as much).

Interactive, in tmux, for anything headless cannot show:

```bash
$C tui <id> start --model fable    # accepts the workspace-trust prompt for this render only
$C tui <id> send "<message>"       # submits, waits until the turn finishes, returns the screen
$C tui <id> stop --name fable-tui  # saves the screen to evidence, sends /exit (fires SessionEnd)
```

Watch it live with `tmux attach -t loamv-<id>`.
When a prompt such as a permission request waits on you, `send` exits 1 with `"state": "dialog"`; answer it there.

Rendered checks:

```bash
$C check <id>      # the render's bin/check; expect a last line starting "check: PASSED"
```

A fresh render has no `tests/`, so that check runs no pytest and a pass alone proves little; [`features/render.md`](features/render.md) shows how to see it fail.
`doctor` and `check` record their last outcome in `run.json`.
`bin/release.sh` tags only a HEAD with a clean-tree run (`"dirty": false`) whose doctor and check are both ok, the check run on a pristine render (`"pristine": true`: copier's one commit, nothing edited).

## Evidence

Everything lands in `<run>/evidence/`: `render.log`, `<name>.jsonl` (the stream-json with hook events), `<name>.stderr`, `<name>.transcript.jsonl`, `<name>.screen.txt`, `check.txt`.

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

It kills the run's tmux session, removes `render/`, `memstore/` and the `~/.claude/projects/` directory of this render, and keeps `evidence/` and `run.json`.
It never kills by process name and never touches another run.
After cleanup, list `<run>/evidence/` to confirm the proof is still there.

## Feature map

The behavior inventory is in [`features/README.md`](features/README.md), one file per feature with the same four sections.
For a broad regression sweep, walk the index top to bottom.
Upkeep is `/pstack:maintain-verification-skill` once the pstack plugin is installed (source wave plus one live pass; edits stay inside this directory).
Until then, rerun the feature map recipes by hand after a seed change.
