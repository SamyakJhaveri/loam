# Diagrams Reference

Setup guides, usage patterns, and technical details for the diagrams visual stack.

## Tool Overview

| Tool | Type | Best For | Setup Required |
|------|------|----------|----------------|
| Excalidraw (cloud MCP) | claude.ai MCP | Hand-drawn diagrams, concept maps, architecture sketches | None (auto on claude.ai) |
| [excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | Claude Code skill (fallback) | Hand-drawn diagrams via local Playwright rendering | Clone + Playwright |
| [drawio-mcp](https://github.com/jgraph/drawio-mcp) | MCP server or CLI skill | Flowcharts, ER diagrams, sequence diagrams, formal architecture | MCP config or draw.io Desktop |
| [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) | External CLI/web app | Academic illustrations, research figures, publication diagrams | API keys (Gemini/OpenRouter) |
| [gitdiagram](https://github.com/ahmedkhaleel2004/gitdiagram) | Web service | GitHub repo → interactive architecture diagram | None (gitdiagram.com) |

---

## 1. Excalidraw

### Cloud Excalidraw MCP (claude.ai — no setup)

Available automatically in claude.ai sessions. Provides:
- `create_view` — create diagrams with streaming animation and camera control
- `export_to_excalidraw` — upload to excalidraw.com for a shareable/editable link
- `read_me` — load the complete element format reference (call once per session)
- `read_checkpoint` / `save_checkpoint` — state management for iterative refinement

Call `read_me` first to get the color palette, element types, arrow bindings, camera sizes, and dark mode guide. The MCP handles rendering — no Playwright or local dependencies needed.

### Local skill setup (coleam00 — fallback)

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git /tmp/eds
mkdir -p .claude/skills/excalidraw-diagram
cp -r /tmp/eds/SKILL.md /tmp/eds/references .claude/skills/excalidraw-diagram/
cd .claude/skills/excalidraw-diagram/references
uv sync && uv run playwright install chromium
```

### What it includes

| File | Purpose |
|------|---------|
| `SKILL.md` | Design methodology and workflow |
| `references/color-palette.md` | Brand color customization |
| `references/element-templates.md` | JSON templates for diagram elements |
| `references/json-schema.md` | Excalidraw JSON format reference |
| `references/pyproject.toml` | Python dependencies (used by `uv sync`) |
| `references/render_excalidraw.py` | PNG rendering via Playwright |
| `references/render_template.html` | Browser rendering template |

### Design philosophy

Diagrams should **argue, not display**. Every visual element's shape carries semantic meaning:
- Fan-out patterns → one-to-many relationships
- Convergence patterns → aggregation
- Concrete evidence artifacts (code snippets, JSON samples) over generic placeholders

### Rendering pipeline

1. Generate Excalidraw JSON (section-by-section for large diagrams)
2. Render to PNG via `render_excalidraw.py` (Playwright + Chromium)
3. Visual inspection for layout issues (overlaps, misalignment)
4. Iterative refinement until validation passes

### Example invocations

```
/diagrams excalidraw microservices communication patterns
/diagrams excalidraw data pipeline from Kafka to PostgreSQL
/diagrams excalidraw authentication flow with OAuth2
```

---

## 2. Draw.io (MCP + CLI)

### Setup — MCP server

Add to `.mcp.json`:
```json
"drawio": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@drawio/mcp"]
}
```

MCP tools exposed:
- `open_drawio_xml` — opens native draw.io/mxGraph XML in the browser editor
- `open_drawio_csv` — converts CSV tabular data into a draw.io diagram
- `open_drawio_mermaid` — converts Mermaid syntax into an editable draw.io diagram

All three accept `content` (string, required), `lightbox` (boolean, optional), `dark` (string, optional: "auto"/"true"/"false").

### Setup — CLI skill (alternative, no MCP needed)

```bash
git clone https://github.com/jgraph/drawio-mcp.git /tmp/drawio-mcp
mkdir -p .claude/skills/drawio
cp /tmp/drawio-mcp/skill-cli/drawio/SKILL.md .claude/skills/drawio/SKILL.md
```

Requires draw.io Desktop for PNG/SVG/PDF export.

### Draw.io XML structure

Every `.drawio` file is mxGraphModel XML:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Server" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="100" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="3" value="" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="4" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="4" value="Database" style="shape=cylinder3;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="250" width="120" height="80" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

### Critical XML rules

- **No XML comments** — draw.io ignores them but they add noise
- **Escape characters**: `&amp;` `&lt;` `&gt;` `&quot;`
- **Unique IDs**: every `mxCell` must have a unique `id`
- **Root cells**: `id="0"` (root) and `id="1"` (default parent) are required
- **Edges**: every edge `mxCell` must contain a child `<mxGeometry>` element
- **`html=1`**: include `html=1;` in every style string — without it, labels with line breaks or formatting render as raw text
- **Naming**: use `<subject>.drawio` for files; `<subject>.drawio.png` for exports (double extension preserves embedded XML)

### Common styles

| Shape | Style |
|-------|-------|
| Rounded box | `rounded=1;whiteSpace=wrap;html=1;` |
| Cylinder (DB) | `shape=cylinder3;whiteSpace=wrap;html=1;` |
| Diamond (decision) | `rhombus;whiteSpace=wrap;html=1;` |
| Cloud | `ellipse;shape=cloud;whiteSpace=wrap;html=1;` |
| Container/group | `swimlane;startSize=20;html=1;` |
| Orthogonal edge | `edgeStyle=orthogonalEdgeStyle;html=1;` |

### Export formats

| Format | CLI flag | Extension | Editable in draw.io |
|--------|----------|-----------|---------------------|
| Default | (none) | `.drawio` | Yes |
| PNG | `--format png --embed-diagram` | `.drawio.png` | Yes |
| SVG | `--format svg --embed-diagram` | `.drawio.svg` | Yes |
| PDF | `--format pdf --embed-diagram` | `.drawio.pdf` | Yes |

### Example invocations

```
/diagrams drawio flowchart for user registration
/diagrams drawio png ER diagram for e-commerce schema
/diagrams drawio svg sequence diagram for API authentication
/diagrams drawio architecture overview of microservices
```

---

## 3. PaperBanana

Publication-quality academic illustrations via multi-agent AI pipeline. **External tool — not run by Claude Code.**

- **Quickest path**: [HuggingFace Space](https://huggingface.co/spaces/dwzhu/PaperBanana) (no setup)
- **Self-host / CLI**: see [github.com/dwzhu-pku/PaperBanana](https://github.com/dwzhu-pku/PaperBanana)
- **Output**: PNG (up to 4K), downloadable as ZIP

---

## 4. GitDiagram

Interactive Mermaid.js architecture diagram from any GitHub repo. **External web service — not run by Claude Code.**

- **Use**: replace `hub` with `diagram` in any GitHub URL → `gitdiagram.com/user/repo`
- **Private repos**: requires GitHub PAT in the gitdiagram.com UI
- **Self-host**: see [github.com/ahmedkhaleel2004/gitdiagram](https://github.com/ahmedkhaleel2004/gitdiagram)
- **Output**: interactive Mermaid diagram, exportable as PNG or raw Mermaid code
