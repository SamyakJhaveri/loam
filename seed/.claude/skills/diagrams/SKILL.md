---
name: diagrams
description: >
  Generate diagrams and visuals from code or descriptions.
  Use when the user needs a rendered diagram, code visualization,
  or architecture image. Subcommands — excalidraw (hand-drawn),
  drawio (formal XML), paper (academic illustrations),
  gitdiagram (repo architecture),
  yoshida (atmospheric Hiroshi Yoshida woodblock hero art).
auto-activate: false
argument-hint: excalidraw|drawio|paper|gitdiagram|yoshida <description>
---

# Diagrams — The Visual Stack

Generate diagrams using one of several specialized tools, each suited to different use cases.

## Arguments

`$ARGUMENTS` — one of:

- `excalidraw <description>` — hand-drawn Excalidraw diagrams with visual self-validation
- `drawio [format] <description>` — native draw.io XML diagrams with optional PNG/SVG/PDF export
- `paper <description>` — publication-quality academic illustrations via PaperBanana
- `gitdiagram <github-url>` — interactive architecture diagram from any GitHub repo
- `yoshida <concept-slug>` — render a Yoshida-style Track B atmospheric hero image for a concept defined in `docs/diagrams/concepts.yaml`
- `<free-form text>` — auto-classify intent and route to the appropriate tool

## Output Convention

All outputs go to `docs/diagrams/`. Run `mkdir -p docs/diagrams` before writing any output.

## Phase 1: Parse & Route

Parse `$ARGUMENTS` and match the FIRST word:

1. `excalidraw` → Phase 2A
2. `drawio` → Phase 2B
3. `paper` → Phase 2C
4. `gitdiagram` → Phase 2D
5. `yoshida` → Phase 2F
6. Anything else → Phase 2E (free-form classification)

Subcommand dispatch is deterministic — do not use LLM reasoning when a keyword is present.

---

## Phase 2A: Excalidraw (Layer 3)

Generate hand-drawn style Excalidraw diagrams. Two integration paths:

### Path 1: Cloud Excalidraw MCP (if available — no setup required)

Check if Excalidraw MCP tools are available in the current environment (look for `create_view`, `export_to_excalidraw`). These are provided automatically by claude.ai — no local setup needed.

If available:
1. Call the MCP's `read_me` tool once to load the element format reference (color palette, element types, camera control, dark mode)
2. Use `create_view` to generate the diagram — elements stream in with draw-on animations
3. Optionally use `export_to_excalidraw` to upload to excalidraw.com for a shareable/editable link
4. Use `save_checkpoint` / `read_checkpoint` for iterative refinement across turns

### Path 2: Local excalidraw-diagram skill (fallback)

If no cloud MCP is available, check for the local skill:
```bash
ls .claude/skills/excalidraw-diagram/SKILL.md 2>/dev/null || echo "Not installed"
```

If not installed, tell the user:
> Install with: `git clone https://github.com/coleam00/excalidraw-diagram-skill.git /tmp/eds && mkdir -p .claude/skills/excalidraw-diagram && cp -r /tmp/eds/SKILL.md /tmp/eds/references .claude/skills/excalidraw-diagram/ && cd .claude/skills/excalidraw-diagram/references && uv sync && uv run playwright install chromium`

If installed, delegate to the excalidraw-diagram skill directly — it handles the full workflow: concept mapping → JSON generation → PNG rendering → visual validation → iterative refinement.

---

## Phase 2B: Draw.io (MCP or CLI — Layer 1/2)

Generate native `.drawio` XML diagrams. Two integration paths:

### Path 1: MCP server (if `drawio` MCP is configured)

Generate the XML, then open it in the draw.io editor using MCP tools:
- `open_drawio_xml` — opens native draw.io/mxGraph XML in the editor
- `open_drawio_csv` — converts CSV tabular data into a diagram
- `open_drawio_mermaid` — converts Mermaid syntax into an editable draw.io diagram

All three accept a `content` string and optional `lightbox` (read-only) and `dark` mode params.

### Path 2: Direct XML generation (no MCP needed)

1. Generate draw.io mxGraphModel XML directly.
2. Write to `docs/diagrams/<subject>.drawio`.
3. If the user requested a format (png, svg, pdf), export:
   ```bash
   # macOS
   /Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --embed-diagram docs/diagrams/<subject>.drawio
   # Linux
   drawio --export --format png --embed-diagram docs/diagrams/<subject>.drawio
   ```
4. The `--embed-diagram` flag keeps the XML inside the exported file so it remains editable in draw.io.

**Critical draw.io XML rules:**
- Never include XML comments
- Escape special characters: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Unique `id` for every `mxCell`
- Every edge needs a child `<mxGeometry>` element
- Root requires cells `id="0"` (root) and `id="1"` (default parent)

See `reference.md` for the XML generation guide and shape reference.

---

## Phase 2C: PaperBanana (Track A — manual, external tool — Layer 3)

**External tool — Claude Code cannot run it directly.** Direct the user to the [HuggingFace Space](https://huggingface.co/spaces/dwzhu/PaperBanana) for zero-setup use, or to the [GitHub repo](https://github.com/dwzhu-pku/PaperBanana) for self-hosting. See `reference.md` §3.

---

## Phase 2D: GitDiagram (web service — Layer 3)

**External web service — Claude Code cannot run it directly.** Tell the user to replace `hub` with `diagram` in any GitHub URL (e.g. `gitdiagram.com/user/repo`). See `reference.md` §4.

---

## Phase 2E: Free-form Classification (Layer 3)

When no subcommand prefix is matched, classify intent:

| Signal | Route to |
|--------|----------|
| Hand-drawn, sketch, whiteboard, Excalidraw | `excalidraw` |
| Flowchart, ER, sequence, architecture, export to PNG/SVG/PDF, draw.io | `drawio` |
| Academic, paper, publication, scientific illustration, research figure | `paper` (research projects only — ask user to confirm) |
| GitHub repo URL, repo architecture, codebase overview | `gitdiagram` |

If ambiguous, ask the user to clarify.

---

## Phase 2F: Yoshida (Track B — Layer 3)

The **automated Track B** path: atmospheric hero art in Hiroshi Yoshida's shin-hanga
woodblock style, rendered via the Gemini Image API (`gemini-3-pro-image`). This is the
automated counterpart to PaperBanana's manual Track A in Phase 2C — here the render runs from
a committed repo script rather than a human in a browser.

Invocation:

```bash
uv run .claude/skills/diagrams/scripts/render-yoshida.py --concept <slug> --candidates 2
```

- **`GEMINI_API_KEY` must be set.** If it is unset, the script prints a clear `SKIP` line and
  exits cleanly with no render (the scaffold stays intact). Set the key before a real render.
- **References are optional.** They come from a local `yoshida_hiroshi/` directory (gitignored)
  — the prose prompt carries the style on its own, but local references boost fidelity when
  present. The model accepts at most 6 references per concept; the script hard-fails rather
  than silently truncate a longer list, and warns (without failing) on a missing file.
- **Label discipline.** Yoshida prints carry almost no text. For label-heavy concepts, get the
  labels from Track A (PaperBanana) or a `drawio` / `excalidraw` vector overlay, not the image
  model — deterministic text belongs in a deterministic layer.
- **Full method.** See [`design-language.md`](design-language.md) for the two-track design
  language, the canonical Yoshida preamble, the style principles, label discipline, the
  reference-image guidance, and the Track A 3-field recipe.

`render-yoshida.py` is a committed repo script, not generated at runtime, so invoking it does
not trip Rule 1 below. It does make a real, paid Gemini API call once `GEMINI_API_KEY` is set
— run it only with the user's awareness.

---

## Rules

1. Never execute user-generated or AI-generated scripts without explicit user confirmation
2. All diagram outputs go to `docs/diagrams/` — create the directory if it doesn't exist
3. Subcommand dispatch is deterministic — do not use LLM reasoning when a keyword is present
4. If a required tool is not installed, tell the user how to install it and stop — do not attempt workarounds
5. For draw.io XML, validate structure before writing (unique IDs, proper escaping, required root cells)
