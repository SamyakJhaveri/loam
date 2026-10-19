# Handoff

A session that stops mid-task leaves a note at `.loam/memory/handoff/<repo>.md` in the format `docs/WORKERS.md` defines; the next session on any machine injects it once under `## Handoff (claimed now)`, archives it, commits the archive in the store and pushes it when the store has a remote. Whether the note still holds is judged later, by the `catchup` skill's `red-flags.sh`, against the note's `Written at` hash.

## Sub-features

- `handoff-claim` prints the note (its first 1500 bytes) under `## Handoff (claimed now)` on `SessionStart` (startup, resume, clear) and counts it as `1 handoff` on the `Loaded:` line.
- `handoff-once` moves the note to `handoff/<repo>/archive/<date>-<sid8>.md` in the store in the same hook run, so the next start prints `0 handoff`.
- `handoff-commit` commits the archive as `handoff <date> <repo> <sid8>` and, when the store has an `origin` remote, pushes it in the background.
- `handoff-stale` sits outside recall. `mem-recall.sh` injects a stale note as it is; `red-flags.sh` flags the live note, else the newest archived one, when its `Written at` hash is not HEAD or its status words contradict git.

## How to get to it (user POV)

- Stop mid-task and write `.loam/memory/handoff/<repo>.md` with the seven headings in `docs/WORKERS.md`.
- Start the next session in the same repo, on any machine that shares the store.
- Run `/catchup`, which names the note on its `Handoff:` line and flags it when it is stale.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.
- `$C session r1 "Reply with the single word OK." --name mem-1 --stub` has run, so `<root>/r1/render/.loam/memory` links the store.

- **Write the note.** `mkdir -p <root>/r1/render/.loam/memory/handoff`, then write `render.md` there with the seven `docs/WORKERS.md` headings as `##` headings and `0000000000000000000000000000000000000000` under `## Written at`, so the note is stale.
- **Claimed ($0).** Run `$C session r1 "Reply with the single word OK." --name ho-1 --stub`. One `SessionStart:startup` stdout reads `## Memory (render)`, then `Loaded: 1 recent sessions, 0 hint bullets, 1 handoff`, then `## Handoff (claimed now)` and the whole note. The `hooks` summary cuts stdout at 400 characters; read `ho-1.jsonl` for the full note.
- **Archived and committed.** `.loam/memory/handoff/render.md` is gone. `<root>/r1/memstore/handoff/render/archive/` holds one file, `<date>-<ho-1's first 8 id characters>.md`, identical to the note. `git -C <root>/r1/memstore log --diff-filter=A --format=%s -- handoff/render/archive/<file>` prints `handoff <date> render <sid8>`.
- **Once.** Run `$C session r1 "Reply with the single word OK." --name ho-2 --stub`. The `## Memory (render)` stdout has `Loaded: 2 recent sessions, 0 hint bullets, 0 handoff` and no `## Handoff (claimed now)`; the archive still holds one file.
- **Stale.** From `<root>/r1/render`, run `bash .agents/skills/catchup/red-flags.sh`, the script `/catchup` runs first. It prints `Handoff: .loam/memory/handoff/render/archive/<file>` and `FLAG: STALE .loam/memory/handoff/render/archive/<file>: Written at 0000000000000000000000000000000000000000 is not HEAD <short HEAD>`.
- **Fresh control.** In a second fresh render, repeat with the output of `git rev-parse HEAD` in the render under `## Written at`. The note is claimed and archived the same way, and `red-flags.sh` names it on `Handoff:` with no `STALE` line.
- **Pushed.** Before `ho-1`, give the store a remote: `git init -q --bare -b main <root>/r1/store-remote.git`, `git -C <root>/r1/memstore remote add origin <root>/r1/store-remote.git`, `git -C <root>/r1/memstore push -q origin main`. After `ho-1`, `git -C <root>/r1/store-remote.git log --format=%s main` lists `handoff <date> render <sid8>`, and `ls-tree -r main` lists the archive.
- **Sweep.** `$C sweep` runs the stale note through Claimed, Archived and committed, Once and Stale as recipes `handoff-1`, `handoff-2` and `handoff-stale`.
- **Proof.** `ho-1.jsonl` and `ho-2.jsonl` in evidence, plus the `red-flags.sh` output; copy the archive into evidence before cleanup.

## Gotchas

- `mem-recall.sh` has no staleness check. It injects any note it finds, whatever its `Written at`, and its closing trust line tells the agent to check `git log -1` before acting. Only `red-flags.sh` compares the hash with HEAD, and only when `/catchup` runs.
- `red-flags.sh` reads the hash only on or just under a line starting `Written at`. A note without that heading is never flagged by hash, only by its status words.
- The recipe writes the note itself, standing in for the session that stopped. The proof starts at the claim; a stub cannot show that a model writes a good note.
- `ho-1`'s `Stop` capture also commits and pushes the store, so a remote that holds the claim commit does not prove that the claim's own background push ran.
- `cleanup` does not remove `store-remote.git`; remove it by hand.
- Two machines that start at the same moment each inject the note once and keep both archives (`docs/HARNESS.md`, The handoff); not driven here.
