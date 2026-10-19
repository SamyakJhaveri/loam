# Post-compact reinjection

After Claude Code compacts a session, `post-compact-reinject.sh` adds one paragraph to the fresh context, starting `After compaction:`, that points the agent back at the handoff note and tells it to compare the note's `Written at` hash with `git rev-parse HEAD` before claiming a result.

## Sub-features

- `compact-reinject` prints the `After compaction:` paragraph on `SessionStart` with source `compact`.
- `compact-survives` lands that text after the compact boundary, so the model sees it in the compacted context.
- `compact-silent` adds nothing at startup: the hook is registered on the `compact` matcher only.
- `compact-capture` runs `mem-capture.sh` on `PreCompact` (see [Session memory](./session-memory.md)).

## How to get to it (user POV)

- Type `/compact` in a session.
- Run `claude -p "/compact" --resume <session id>` in the project.
- Keep working until Claude Code compacts on its own near the context limit (not driven here).

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.

- **Seed a turn.** Run `$C session r1 "Reply with the single word OK." --name c-1 --stub`. `hooks` holds two `SessionStart:startup` entries, both with empty stdout: no `After compaction` text at startup.
- **Compact ($0).** Run `$C session r1 "/compact" --resume c-1 --name c-2 --stub`. `session_id` is c-1's and `stub_requests` is 1 (the summary request). `hooks` holds two `SessionStart:resume` entries, then two `SessionStart:compact` entries, one of whose stdout starts `After compaction: re-read the handoff`.
- **After the boundary.** In `c-2.transcript.jsonl`, the `compact_boundary` record (`trigger: manual`) is followed by an `attachment` of type `hook_success` with `hookName` `SessionStart:compact`, command `.claude/hooks/post-compact-reinject.sh`, and content starting `After compaction:`.
- **Model read it (paid).** Run `$C session r1 "Quote verbatim the first sentence of any text in your context that begins with 'After compaction', or reply NONE. Do not use tools." --resume c-2 --name c-3 --model opus`. `result` is the sentence that starts `After compaction: re-read the handoff` and ends `(format: docs/WORKERS.md).`; `NONE` is a failure. This turn cost $0.81 on `claude-opus-5-5`.
- **Proof.** `c-2.jsonl`, `c-2.transcript.jsonl` and `c-3.jsonl` in evidence.

## Gotchas

- `/compact` needs a turn since the last compaction. Without one, the stream shows `compact_result: failed` with `compact_error: Not enough messages to compact.`, the stub gets no request, and `session` reports `"ok": false`.
- A resumed session keeps its id, so every step's `.transcript.jsonl` copy holds the whole session so far.
- `PreCompact` is not a `hook_response` in the stream; it shows as a user message `Compacted PreCompact [.claude/hooks/mem-capture.sh] completed successfully`.
- `mem-recall.sh` is not on the `compact` matcher. The memory block printed at resume lands before the boundary and compaction drops it; only the `After compaction:` text is in the compacted context.
- The stub's summary is `OK`. That is enough to fire the hook and says nothing about summary quality.
- A paid session without `--model` runs on the user's default model from `~/.claude/settings.json`, even under `--setting-sources project,local`: with that key set to `fable`, the same quote-back without `--model` ran on `claude-fable-5-1` ($0.58). Pass `--model` so the run uses the model you meant.
