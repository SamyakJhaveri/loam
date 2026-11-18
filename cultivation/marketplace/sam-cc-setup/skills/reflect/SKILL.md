---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

In Claude Code, read the Claude Code adapter (`<P>/docs/harness/claude-code.md`; `<P>` is the pstack folder that `bash <this file's folder>/../pstack/pstack-path.sh` prints) once per session before you follow this skill. It maps the Cursor names in pstack skills to Claude Code.

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript in the `agent-transcripts/` directory the system prompt names. Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.

```bash
ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
```

That covers the legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`) layouts. For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt. If none matches, pass a tight digest of the session instead.
Print that transcript's owner words and auto-mode classifier refusals, with line numbers, by `python3 <this file's folder>/words-and-refusals.py <transcript> <transcript folder>/subagents/*.jsonl`, and give reviewers its output as the owner's words: an entry is his only when its `origin.kind` is exactly "human", never when the origin is missing.

## 2. Spawn three reviewers

Make a findings folder `<dir>` (a fresh `mktemp -d`, or the run's evidence folder). Start reviewers as agent slots free under the session's cap, each a `Task` call, `subagent_type: worker` where `worker` is a defined agent type (the plugin's agent-route hook then refuses `general-purpose`), else `general-purpose`, agent mode (`readonly: false`). Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and readonly strips MCPs.

Each reviewer and the synthesizer name a role line in the `pstack-models.mdc` rule and a default. Set `model` to that line's value, or to the default if the rule or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the Task tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **poteto-mode** skill.

| Lens | Role line | Default `model` | Prompt template |
|---|---|---|---|
| Judgment | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `grok-4.7-xhigh-fast` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest and the findings path `<dir>/<lens>.md` (`judgment`, `tooling`, `divergent`) where marked. Each reviewer writes its findings to `<dir>/<lens>.md` with a Bash heredoc, states the last transcript line it read, lists live-state to-dos apart from learnings, and returns at most 20 lines.

## 3. Synthesize

One `Task` call, the same `subagent_type`, `model` from the `reflect judgment, divergent, synthesizer` line (default `claude-opus-5-5-xhigh`), agent mode (`readonly: false`). It spot-verifies citations through MCP, and readonly strips MCPs. Pass `references/synthesizer.md` verbatim, with the three findings paths and the transcript path (or an updated digest) where marked. The synthesizer reads the three files (in a fresh session if the lead hands off) and drops to-dos resolved after the last line read. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit a skill under `~/.claude/plugins/cache/`. Before approval, show its destination: the owner copy `<S>/<skill>/` (`<S>` is the folder above `<this file's folder>`, which the `pstack` router reads), edited in its source checkout (Loam's `cultivation/marketplace/sam-cc-setup/skills/<skill>/`), never in the installed plugin. After approval, for a pstack skill with no owner copy yet, copy its folder there and point every router reference to it, the table row and the principle-list line, at `<S>/<skill>`; then edit the copy. Never open a PR or push.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): in Claude Code, which has no `create-skill`, edit the owner copy directly, `git add` each new or changed SKILL.md and its support files (the check lists files with `git ls-files`, so an unstaged new skill is never checked), and validate it with the "skill and agent frontmatter + references" step of Loam's `bin/check`, which reads each SKILL.md, and `claude plugin validate --strict` on the marketplace folder.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): edit the description in the owner copy directly and validate it the same way.
- `new skill via create-skill: <kebab-name>`: write it in `<S>/<kebab-name>/` in the shape of a skill beside it, and validate it the same way.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
