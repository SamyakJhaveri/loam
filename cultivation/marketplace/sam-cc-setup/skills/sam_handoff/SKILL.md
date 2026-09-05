---
name: sam_handoff
description: Write or update a handoff document so the next agent with fresh context can continue this work. Use for IN-PROGRESS work only, not end-of-session cleanup. Writes to the project root. Renamed from `handoff` on 2026-08-02 to avoid a name clash with the mattpocock-skills plugin, whose `handoff` compacts the conversation into the OS temp dir instead - a different contract.
---

Write or update a handoff document so the next agent with fresh context can continue this work.

Steps:
1. Check if HANDOFF.md already exists in the project
2. If it exists, read it first to understand prior context before updating
3. Create or update the document with these seven headings, in order:
   - **Goal**: What we're trying to accomplish
   - **Files touched**: Every file changed, with its path
   - **Commands run**: Each command with its exit code
   - **Tried and failed**: Approaches that failed, so they are not repeated
   - **Open assumptions**: Anything assumed but not verified
   - **Next single action**: The one next step to take
   - **Written at**: The output of `git rev-parse HEAD`

Save as HANDOFF.md in the project root and tell the user the file path so they can start a fresh conversation with just that path.