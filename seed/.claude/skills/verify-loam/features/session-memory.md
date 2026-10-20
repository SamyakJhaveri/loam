# Session memory

Every Claude Code session in a rendered project is scrubbed, gzipped and stored as a trace; the next session starts with a `## Memory (<repo>)` block listing recent sessions, so the agent knows what happened before.

## Sub-features

- `mem-capture-stop` captures on `Stop` (throttled to once per 600 seconds per session).
- `mem-capture-end` captures on `SessionEnd` and `PreCompact`.
- `mem-index` appends one line per session to `traces/<repo>/INDEX.md` in the store.
- `mem-link` links `<project>/.loam/memory` to the store after the first capture.
- `mem-recall` prints the memory block on `SessionStart` (startup, resume, clear) when the store has traces.

## How to get to it (user POV)

- Work in the project; the hooks run on their own.
- Start the next session and read the `## Memory` block at the top of context.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.

- **First session.** Run `$C session r1 "Reply with the single word OK." --name mem-1`. `hooks` shows two `SessionStart:startup` entries with exit 0 and empty stdout (the store is empty), and one `Stop` with exit 0.
- **Captured.** Read `<root>/r1/memstore/traces/render/INDEX.md`. It has one line with the session id and the prompt. `<root>/r1/render/.loam/memory` is a symlink to `<root>/r1/memstore`.
- **Recalled.** Run `$C session r1 "Quote the line that starts with 'Loaded:' under '## Memory (' in your context, verbatim, or say NONE." --name mem-2`. One `SessionStart:startup` stdout starts with `## Memory (render)`, and `result` is `Loaded: 1 recent sessions, 0 hint bullets, 0 handoff`.
- **Stub variant ($0).** Add `--stub` to `mem-1`, and run `$C session r1 "Reply with the single word OK." --name mem-2 --stub`. `hooks` and INDEX.md read as above, and one `SessionStart:startup` stdout starts with `## Memory (render)` and holds mem-1's INDEX line, the one with mem-1's session id; a bare heading does not count. `result` is the stub's `OK`, so this proves the block was produced, not that a model read it.
- **SessionEnd.** Run `$C tui r1 start`, then `$C tui r1 stop`. INDEX.md gains a line for that session.
- **Proof.** `mem-1.jsonl`, `mem-2.jsonl` in evidence; copy INDEX.md into evidence before cleanup if the change touched capture.

## Gotchas

- The store directory name is the render's directory name, `render`, so every run's block reads `## Memory (render)`.
- `SessionEnd` does not appear in a headless stream: the process exits first. Prove it through INDEX.md, or with `tui stop`.
- Rendered projects also get Claude Code's own auto-memory (`# Memory` in the system prompt). It is a separate system; ask for the `## Memory (` block by name.
- The `Stop` throttle means a second capture of the same session within 600 seconds is skipped by design.
