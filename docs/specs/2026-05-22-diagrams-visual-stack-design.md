# Design Spec: Loam Diagramming & Visual Stack

> Owner: Samyak Jhaveri
> Status: Approved (revised after adversarial review)
> Created: 2026-05-22
> Scope: Phased diagramming stack — 3 sessions

## Identity

- **Name:** diagrams-visual-stack
- **Type:** Copier template feature (new skill + MCP additions)
- **Tier:** Specialized (`auto-activate: false`)

## Problem

Loam has no diagram rendering or code-extraction visualization tools. tldraw and excalidraw MCPs exist in the environment but are interactive canvas tools — they don't produce rendered output files (PNG/SVG). Engineers and researchers need:

1. **Deterministic** rendered diagrams (sequence, class, ERD) as files
2. **Code-extracted** diagrams (class hierarchies, dependency graphs) from Python
3. **AI-generated** styled visuals (SWE explainers, polished overviews) as images
4. **Academic figures** (research flavor only) with iterative refinement

## Inputs

- User intent via `/diagrams <subcommand> <args>` or free-form description
- Python source code (for extraction)
- Natural language descriptions (for AI-generated visuals)
- GEMINI_API_KEY environment variable (for Gemini image gen)

## Behavior

### Routing: Hybrid subcommand + free-form fallback

```
/diagrams extract <module>          → pyreverse (deterministic, Layer 1)
/diagrams render <type> <desc>      → winning structured renderer (deterministic, Layer 1)
/diagrams visualize <description>   → winning Gemini MCP (probabilistic, Layer 3)
/diagrams paper <description>       → PaperBanana CLI (research only, Layer 3)
/diagrams <free-form description>   → LLM classifies intent → routes to above
```

Subcommands are deterministic dispatch (no LLM reasoning). Free-form fallback uses LLM only when no subcommand is given.

### Skill structure

```
seed/.claude/skills/diagrams/
├── SKILL.md          # Subcommand parsing, routing, process steps
└── reference.md      # Per-backend examples, prompts, output format
```

Research-only extension:
```
seed/_research/skills/diagrams-research/
└── SKILL.md          # PaperBanana integration (extends core skill)
```

### Tool inventory (verified)

| Tool | Category | Install | Integration | Session |
|------|----------|---------|-------------|---------|
| **pyreverse** | Code extraction | `pip install pylint` | CLI: `pyreverse -o mmd -d ./docs/diagrams <module>` | 1 |
| **claude-mermaid** | Structured render | `npm install -g claude-mermaid` | MCP: `{"command":"claude-mermaid"}` | 1 (eval) |
| **D2 MCP** | Structured render | See repo README | MCP: TBD | 1 (eval) |
| **UML MCP (Kroki)** | Structured render | Docker or cloud API | MCP: TBD | 1 (eval) |
| **nanobanana-mcp-server** | AI visuals | `uvx nanobanana-mcp-server@latest` | MCP: `{"command":"uvx","args":["nanobanana-mcp-server@latest"]}` | 2 (eval) |
| **shinpr/mcp-image** | AI visuals | `npx -y mcp-image` | MCP: `{"command":"npx","args":["-y","mcp-image"]}` | 2 (eval) |
| **mingrammer/diagrams** | Architecture | `pip install diagrams` | Bash: Claude generates `.py`, user confirms before exec | 2 |
| **PaperBanana** | Academic figures | Clone + manual setup | CLI: `python main.py` | 3 (research only) |

### Eliminated tools (with reasons)

| Tool | Why eliminated |
|------|---------------|
| lansespirit/image-gen-mcp | Clone-and-run only, Vertex AI complexity. Bad for template distribution |
| guinacio/claude-image-gen | Too few stars (37), limited documentation |
| CodeBoarding | Unverified install, marginal benefit over pyreverse for code extraction |
| Structurizr DSL | Java-based, user is Python-only |
| madge | JS/TS only, user is Python-focused |

## Outputs

- Rendered diagram files in `docs/diagrams/<type>-<subject>-<date>.<ext>`
- Updated `.mcp.json.jinja` with winning MCP servers
- `/diagrams` skill in `seed/.claude/skills/diagrams/`
- Research extension in `seed/_research/skills/diagrams-research/` (Session 3)

## Constraints (Must NOT)

- Must NOT ship PaperBanana or heavy academic tools in the generic template
- Must NOT execute generated Python scripts (mingrammer/diagrams) without user confirmation
- Must NOT hard-require GEMINI_API_KEY — Gemini MCP must be conditional or gracefully degrade
- Must NOT use LLM routing when a subcommand is provided (deterministic dispatch only)
- Must NOT add >2 MCP servers to `.mcp.json.jinja` (one renderer + one image gen)
- Must NOT mark skill as `auto-activate: true` (specialized skill per known-issues.md)

## Acceptance Criteria

1. `pyreverse -o mmd -d ./docs/diagrams <module>` produces a valid `.mmd` file from any Python module
2. Winning structured renderer produces SVG/PNG from Mermaid input for all 8 test diagram types (sequence, class, ERD, state machine, architecture, flowchart, C4, dependency)
3. Winning Gemini MCP produces a PNG image from "Draw an architecture diagram showing a FastAPI backend connecting to PostgreSQL via SQLAlchemy" — image renders without errors and is >50KB
4. `/diagrams extract <module>` invokes pyreverse and saves output to `docs/diagrams/`
5. `/diagrams render sequence "user login flow"` produces a sequence diagram via the winning renderer
6. `/diagrams visualize "how the auth system works"` produces an AI-generated visual via Gemini
7. Free-form `/diagrams show me the class hierarchy of auth` routes correctly to `extract`
8. `bin/verify-template.sh` passes after all changes
9. `.mcp.json.jinja` has exactly 2 new MCP servers (renderer + image gen), both with graceful degradation when deps are missing

## Phasing

| Session | Scope | Deliverables |
|---------|-------|-------------|
| **1** | Evaluate structured renderers + pyreverse | Renderer winner chosen, pyreverse verified, skeleton skill with `extract` + `render` subcommands |
| **2** | Evaluate Gemini MCPs + wire winners + full skill | Gemini winner chosen, both MCP servers in `.mcp.json.jinja`, `visualize` subcommand, mingrammer/diagrams, free-form fallback |
| **3** | Research flavor + polish | PaperBanana in `_research/`, `paper` subcommand, end-to-end test suite, BOOTSTRAP.md updates |
