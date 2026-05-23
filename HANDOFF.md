# HANDOFF — Loam v3.0 Public Release (Final Steps)

> **For:** Fresh Claude Code session with Opus + ultrathink.
> **Project:** Loam (`/Users/samyakjhaveri/Desktop/loam`) — a Copier template that bootstraps Claude Code projects.
> **Date:** 2026-05-23.
> **Branch:** main (commit directly, no feature branches).

---

## Goal

Ship Loam v3.0 as a public GitHub repo. The template is structurally complete, all release checklist items are done, and the diagrams skill has been activated. Three things remain: push the commits, test the diagrams live, and make the repo public.

---

## Current Progress

### What's been done (this session — 2026-05-23)

**Release checklist (all 5 steps complete):**
- Step 1: LICENSE rewritten (commit `15fee966`)
- Step 2: seed/README.md.jinja fixed (commit `95f30b31`)
- Step 3: Stale artifacts cleaned (commit `f57246c1`)
- Step 4: Root README.md written (commit `7c2fbb6d`)
- Step 5: Full verification — `bin/verify-template.sh` ALL OK, copier default/research/update tests all pass

**Diagrams activation (2 commits, not yet pushed):**
- `ffd90bd7` — `fix: accept 'Use for' in skill description linter`
- `3f8af9ce` — `feat(diagrams): add cloud Excalidraw MCP as primary path`

**Pocock skills (prior session — 2026-05-23):**
- `edae0b72` — 7 mattpocock/skills adopted as marketplace bundle
- `6ac5201b` — Registered in marketplace.json + patterns absorbed into existing skills

**Current state:**
- Branch: main, 2 commits ahead of origin
- Working tree: clean
- `bin/verify-template.sh`: ALL OK
- `bin/lint-skill-descriptions.sh`: 0 warnings

### What was changed in the diagrams activation

Three files modified (30 insertions, 7 deletions):

1. **`bin/lint-skill-descriptions.sh` (line 51)** — Added `Use for` to the linter's accepted trigger patterns. The grep pattern previously only accepted `Use when`, `Use before`, `Use after`, etc. Two marketplace skills (`diagnose`, `improve-codebase-architecture`) use "Use for" which is valid conditional language. Decision: fix the linter, not the descriptions.

2. **`seed/.claude/skills/diagrams/SKILL.md` (Phase 2A)** — Rewrote the Excalidraw section from a single-path (coleam00 local skill only) to a two-path design:
   - **Path 1: Cloud Excalidraw MCP** — Detects if claude.ai's Excalidraw MCP tools are available (`create_view`, `export_to_excalidraw`, `read_me`, `read_checkpoint`, `save_checkpoint`). If yes, uses them directly. Zero setup required.
   - **Path 2: Local coleam00 skill (fallback)** — Same as before. Checks for `.claude/skills/excalidraw-diagram/SKILL.md`, delegates if found, tells user how to install if not.

3. **`seed/.claude/skills/diagrams/reference.md`** — Added cloud Excalidraw MCP documentation section before the existing local skill setup. Updated the Tool Overview table to show both integration paths (cloud MCP row + local skill fallback row).

4. **`.mcp.json` (local, gitignored)** — Added drawio MCP entry so `/diagrams drawio` works in this repo's local dev. This file is gitignored and not committed — it only affects the template repo itself. Bootstrapped projects get drawio via `seed/.mcp.json.jinja` (which already has it).

---

## Findings and Decisions (Full Context)

### Excalidraw MCP tool names — verified, not fabricated

The cloud Excalidraw MCP is a claude.ai feature. Its 5 tools are:

| Tool | Actual Description (from schema) |
|------|----------------------------------|
| `create_view` | "Renders a hand-drawn diagram using Excalidraw elements. Elements stream in one by one with draw-on animations. Call read_me first to learn the element format." |
| `export_to_excalidraw` | "Upload diagram to excalidraw.com and return shareable URL." |
| `read_me` | "Returns the Excalidraw element format reference with color palettes, examples, and tips. Call this BEFORE using create_view for the first time." |
| `save_checkpoint` | "Update checkpoint with user-edited state." |
| `read_checkpoint` | "Read checkpoint state for restore." |

**How verified:** `ToolSearch` loaded the full JSON schemas for all 5 tools. `read_me` was called and returned a ~5000-word element format reference including color palettes, element types, camera control, arrow bindings, animation mode, dark mode, and worked examples.

**Important nuance:** `export_to_excalidraw` uploads to excalidraw.com and returns a shareable URL — it does NOT create a local `.excalidraw` file. The SKILL.md was corrected to reflect this after the self-critic review caught the initial misdescription.

### Self-critic false positive

During Wave 3 validation, the self-critic agent raised a FAIL claiming the Excalidraw MCP tool names were "fabricated" and that the session only had tldraw MCP. This was a false positive — the self-critic subagent could only see the tldraw system reminder in its context, not the deferred Excalidraw tools in the parent session's tool list. The FAIL was overridden with direct evidence (tool schemas loaded via `ToolSearch`).

**Lesson:** Subagents don't see the parent's full tool environment. When a critique questions tool existence, verify from the parent context.

### Three Excalidraw integration paths exist

| Path | Type | Setup | Best For |
|------|------|-------|----------|
| Cloud Excalidraw MCP (claude.ai) | Platform MCP | None — auto on claude.ai | Interactive diagrams with streaming animations, camera control, checkpoints |
| coleam00/excalidraw-diagram-skill | Claude Code skill | Clone repo + `uv sync` + Playwright/Chromium | Local PNG rendering, portable across platforms |
| Official excalidraw/excalidraw-mcp | Standalone server | Vercel deployment (`.mcpb` file, not npm) | Self-hosted — not suitable for `.mcp.json` wiring |

The SKILL.md uses Path 1 (cloud) as primary and Path 2 (coleam00) as fallback. Path 3 was evaluated and rejected because it's deployed via Vercel, not installable via npm.

### The `.mcp.json` is gitignored

The template repo's `.mcp.json` is gitignored — it's for local dev only. What ships to bootstrapped projects is `seed/.mcp.json.jinja`, which already includes drawio, codegraphcontext, semble, and memory MCPs.

### Release checklist "Must NOT" override

The release checklist (`docs/RELEASE-CHECKLIST.md` line 271) says "Must NOT modify existing skill files." This session modified the diagrams SKILL.md and reference.md. The override was explicitly approved by the user because: (a) the project targets Claude Code users who benefit from the cloud MCP, and (b) the modification adds a capability path, not a behavior change to existing functionality.

---

## What Worked

- **Plan-reviewer agent** caught real issues: missing `/session-critique`, fabricated-looking tool names (turned out valid but forced verification), imprecise lint fix description, separate commits recommendation
- **Self-critic agent** caught a real inaccuracy in `export_to_excalidraw` description even though its FAIL verdict was a false positive
- **ToolSearch** for MCP tool verification — loading the actual JSON schemas proved tool existence definitively
- **Separate commits** for independent changes — clean history, easy rollback
- **Linter fix over description fix** — "Use for" is valid conditional language; the linter was too narrow

## What Didn't Work

- **Self-critic can't see deferred tools** — subagents have limited visibility into the parent session's tool environment. Don't trust a subagent's claim about tool existence without verifying in the parent context
- **Copier update test without `--trust`** — fails because the template uses tasks. Always use `--trust` flag
- **Copier copy without `project_name`** — fails because `project_name` is required without a default. Always provide `-d project_name=<name>`
- **Initial plan skipped `/session-critique`** — the plan-reviewer caught this. Always include `/session-critique` before `/validate` in the shipping sequence

---

## Next Steps

### Step 1: Push to origin

```bash
git push
```

The branch is 2 commits ahead of origin. This pushes both the linter fix and the diagrams activation.

**Verify:** `git status` shows "Your branch is up to date with 'origin/main'."

### Step 2: Test diagrams live

Test at least two subcommands to validate the skill works end-to-end:

**Test A — Excalidraw (cloud MCP):**
```
/diagrams excalidraw architecture overview of the Loam template skill routing
```
The cloud Excalidraw MCP should render an inline diagram with streaming animations. If the MCP is not available in your session, skip this test — Path 2 (coleam00) will still work if the user installs it.

**Test B — Draw.io:**
```
/diagrams drawio flowchart of the Loam session workflow
```
This requires the drawio MCP to be connected. The `.mcp.json` already has it wired. If the MCP isn't connected, restart Claude Code or check that `npx -y @drawio/mcp` works.

**Verify Test B:** `docs/diagrams/` should contain a `.drawio` file with valid mxGraphModel XML:
```bash
test -f docs/diagrams/*.drawio && grep -q "mxGraphModel" docs/diagrams/*.drawio && echo "OK" || echo "FAIL"
```

**Clean up after testing:** Remove test diagram artifacts (they're test outputs, not template content):
```bash
rm -r docs/diagrams/
```

### Step 3: Make the repo public

This is a GitHub settings change:
1. Go to github.com/samyakjhaveri/loam → Settings → General
2. Scroll to "Danger Zone" → "Change repository visibility"
3. Change from Private to Public

**Verify:** Visit `https://github.com/samyakjhaveri/loam` in an incognito window — should load the README.

### Step 4 (optional): Post-release smoke test

Bootstrap a project from the public repo to verify the full flow:

```bash
tmpdir=$(mktemp -d)
uvx copier copy --trust -d project_name=smoke-test gh:samyakjhaveri/loam "$tmpdir/smoke-test"
cd "$tmpdir/smoke-test"
ls .claude/skills/diagrams/SKILL.md && echo "OK: diagrams skill present"
cat .mcp.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'drawio' in d['mcpServers']; print('OK: drawio MCP wired')"
```

---

## Must NOT

- Must NOT modify `copier.yml`
- Must NOT create feature branches (commit to main)
- Must NOT leave test diagram files committed to the repo
- Must NOT skip cleanup of `docs/diagrams/` after testing

## Skills to use

- `/diagrams excalidraw <description>` — test the cloud Excalidraw MCP path
- `/diagrams drawio <description>` — test the draw.io MCP path
- `/commit` — if any cleanup is needed after testing
- `/validate` — before any commit

## Files referenced in this handoff

| File | Purpose | Status |
|------|---------|--------|
| `seed/.claude/skills/diagrams/SKILL.md` | Diagrams skill with 4 subcommands | Updated (cloud Excalidraw MCP added) |
| `seed/.claude/skills/diagrams/reference.md` | Setup guides and technical details | Updated (cloud MCP docs + table) |
| `bin/lint-skill-descriptions.sh` | Skill description quality linter | Updated (accepts "Use for") |
| `.mcp.json` | Local dev MCP config (gitignored) | Updated (drawio wired) |
| `seed/.mcp.json.jinja` | MCP config shipped to projects | Unchanged (already had drawio) |
| `docs/RELEASE-CHECKLIST.md` | Release checklist (all 5 steps done) | Unchanged |
| `docs/POST-RELEASE-BACKLOG.md` | Post-release work items | Unchanged |
