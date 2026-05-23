---
name: diagrams
description: >
  Generate diagrams and visuals from code or descriptions.
  Subcommands: extract (pyreverse), render (Mermaid), visualize (AI image gen), arch (Python diagrams).
  Use when the user needs a rendered diagram, code visualization, or architecture image.
  NOT for interactive canvas drawing (use tldraw/excalidraw MCPs directly).
auto-activate: false
argument-hint: <subcommand> <args>
---

# Diagrams & Visual Stack

Generate rendered diagrams from Python source, structured descriptions, or natural language.

## Arguments

`$ARGUMENTS` — one of:

- `extract <module>` — extract class/dependency diagrams from Python via pyreverse
- `render <type> <description>` — render a structured diagram via Mermaid
- `visualize <description>` — generate an AI-styled visual via Gemini image generation
- `arch <description>` — generate an architecture diagram via mingrammer/diagrams
- `<free-form text>` — auto-classify intent and route to the appropriate handler above

## Output Convention

All outputs go to `docs/diagrams/<type>-<subject>-<YYYY-MM-DD>.<ext>`.
Run `mkdir -p docs/diagrams` before writing any output.

## Phase 1: Parse & Route

Parse `$ARGUMENTS` to determine the subcommand. Match the FIRST word:

1. `extract` → Phase 2A
2. `render` → Phase 2B
3. `visualize` → Phase 2C
4. `arch` → Phase 2D
5. Anything else → Phase 2E (free-form classification)

**Do NOT use LLM reasoning for routing when a subcommand keyword is present.** Subcommand dispatch is deterministic.

---

## Phase 2A: Extract (pyreverse — deterministic, Layer 1)

Extract class hierarchies and dependency graphs from Python source code.

1. Check pyreverse is available:
   ```bash
   which pyreverse || echo "Not found. Install: pip install pylint"
   ```
   If missing, tell the user and stop.

2. Run extraction:
   ```bash
   mkdir -p docs/diagrams
   pyreverse -o mmd -d docs/diagrams <module>
   ```

3. Report the output `.mmd` file path. Suggest follow-up:
   > "Mermaid file saved. Render it with `/diagrams render class <path-to-mmd>`"

---

## Phase 2B: Render (Mermaid via claude-mermaid MCP — deterministic, Layer 1)

Render a structured diagram to SVG or PNG using the `mermaid` MCP server.

**Supported types:** sequence, class, ERD, state, architecture, flowchart, C4, dependency

1. Generate valid Mermaid syntax for the requested `<type>` and `<description>`.
   See `${CLAUDE_SKILL_DIR}/reference.md` for syntax templates per type.

2. Use the `mermaid` MCP server's render tool to produce SVG/PNG output.

3. Save to `docs/diagrams/<type>-<subject>-<YYYY-MM-DD>.<ext>`.

4. Report the file path and diagram type.

---

## Phase 2C: Visualize (Gemini image gen — probabilistic, Layer 3)

Generate an AI-styled visual from a natural language description.

**Prerequisite check:** If the `image-gen` MCP server's `generate_image` tool is not available, inform the user:
> "The visualize subcommand requires the image-gen MCP server with GEMINI_API_KEY configured.
> Set it with: `export GEMINI_API_KEY=your-key` and restart Claude Code."

1. Craft a detailed image generation prompt from the user's description. The MCP server
   auto-optimizes prompts via a Subject-Context-Style framework, so focus on technical
   accuracy over artistic direction. Include:
   - The specific system components and their relationships
   - The type of visualization desired (architecture, data flow, overview)

2. Call the `image-gen` MCP server's `generate_image` tool with:
   - `prompt`: the crafted description
   - `fileName`: `visual-<subject>-<YYYY-MM-DD>`
   - `quality`: `"balanced"` (default) or `"quality"` for polished output
   - `aspectRatio`: `"16:9"` for wide diagrams, `"1:1"` for square

   The output directory is pre-configured to `docs/diagrams/` via `IMAGE_OUTPUT_DIR`.

3. Report the file path.

---

## Phase 2D: Architecture (mingrammer/diagrams — hybrid, Layer 1/3)

Generate architecture diagrams using the Python `diagrams` library.

1. Check the library is available:
   ```bash
   python3 -c "import diagrams" 2>/dev/null || echo "Not found. Install: pip install diagrams"
   ```
   If missing, tell the user and stop.

2. Generate a Python script using the `diagrams` library based on the user's description.
   See `${CLAUDE_SKILL_DIR}/reference.md` for API patterns.

3. **STOP. Present the generated script to the user and wait for explicit approval before executing.**
   This is a hard safety gate — never skip it.

4. On approval, execute:
   ```bash
   mkdir -p docs/diagrams
   python3 <script_path>
   ```

5. Save output to `docs/diagrams/arch-<subject>-<YYYY-MM-DD>.png`.

---

## Phase 2E: Free-form Classification (probabilistic, Layer 3)

When no subcommand prefix is matched, classify the user's intent:

| Signal | Route to |
|--------|----------|
| Code structure keywords: class, hierarchy, dependency, module, import | `extract` |
| Diagram type keywords: sequence, ERD, flowchart, state machine, C4 | `render` |
| Visual/style keywords: visualize, show me, explain visually, styled, pretty | `visualize` |
| Architecture keywords: architecture, system, infrastructure, cloud, AWS, GCP | `arch` |

If intent is ambiguous, ask the user to clarify rather than guessing.
After classification, re-enter the appropriate Phase 2 handler.

---

## Rules

1. Never execute user-generated or AI-generated Python scripts without explicit user confirmation
2. All diagram outputs go to `docs/diagrams/` — create the directory if it doesn't exist
3. Subcommand dispatch is deterministic — do not use LLM reasoning when a keyword is present
4. If a required tool (pyreverse, diagrams library, MCP server) is missing, tell the user how to install it and stop — do not attempt workarounds
5. For `render`, always validate Mermaid syntax before sending to the MCP — catch syntax errors early
