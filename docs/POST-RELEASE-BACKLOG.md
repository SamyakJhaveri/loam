# Post-Release Backlog — Loam v3.x

> Work through at your own pace after the repo is public. Nothing here is release-blocking.
> Created: 2026-05-22.

---

## Matt Pocock Skills — Deep Dive Results

Full analysis of [mattpocock/skills](https://github.com/mattpocock/skills) (100k+ stars, 26 skills). Seven recommended for adoption, eight for pattern study, eleven to skip.

### Skills to ADOPT (7) — in priority order

| # | Skill | What it does | Lines | Why adopt | Loam placement |
|---|-------|-------------|-------|----------|----------------|
| 2 | **triage** | Issue state machine: needs-triage -> needs-info -> ready-for-agent -> ready-for-human -> wontfix. Agent-brief template | 140 + 180 ref | Fills genuine gap — no Loam issue management skill. `ready-for-agent` concept key for AFK work | `seed/.claude/skills/` (core) |
| 3 | **to-issues** | Decompose plan/spec/PRD into vertical-slice GitHub issues. HITL vs AFK classification | 100 | Pairs with `gen-spec` + `feature-dev`. No Loam equivalent | `seed/.claude/skills/` (core) |
| 4 | **grill-with-docs** | Grilling session that challenges plans against domain model, updates CONTEXT.md + ADRs inline | 100 + 80 ref | Highest architectural impact — ties grilling to living domain glossary. Closes the CONTEXT.md-as-routing-only gap | `seed/.claude/skills/` (core) |
| 5 | **improve-codebase-architecture** | Find "deepening opportunities" via Ousterhout vocabulary (Module, Interface, Seam, Depth, Leverage). HTML report | 190 + 250 ref | Superior to surface-level techdebt scanning. "Deletion test" heuristic | `seed/.claude/skills/` (complement to techdebt) |
| 6 | **tdd** | Red-green-refactor with vertical slices. Anti-horizontal-slice discipline. Mocking guidelines + deep-modules reference | 130 + 100 ref | Loam has no core TDD skill (only superpowers plugin). Better version | `seed/.claude/skills/` (core) |
| 7 | **prototype** | Throwaway prototypes. Routes to LOGIC (terminal apps) or UI (multiple radical variations). "Delete when done" discipline | 95 + 190 ref | Research-relevant design-space exploration | `seed/.claude/skills/` or marketplace |
https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnose
https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs
https://github.com/mattpocock/skills/tree/main/skills/engineering/to-prd
https://github.com/mattpocock/skills/tree/main/skills/engineering/zoom-out


### Design Patterns to Absorb (into existing skills)

| Pattern | Source skill | Absorb into |
|---------|-------------|-------------|
| Living domain glossary in CONTEXT.md | grill-with-docs | `scaffold-context` — upgrade from routing-only to domain glossary |
| `disable-model-invocation: true` flag | zoom-out | New micro-skill tier in Loam |
| ADR three-part test (hard to reverse + surprising + real trade-off) | grill-with-docs | `gen-spec` |
| Vertical slices / tracer bullets | tdd, to-issues | `feature-dev`, `gen-spec` |
| Standards + Spec dual-axis review | review (in-progress) | `multi-review` |
| "Build a feedback loop" as explicit debugging phase | diagnose | `fix-bug` |

### Architectural Insights

1. **Domain Language gap**: Matt's skills compound — each session refines a shared domain glossary in CONTEXT.md. Loam treats CONTEXT.md as routing (ICM L1), not domain knowledge. `grill-with-docs` adoption closes this.
2. **Issue lifecycle gap**: Loam has no plan->issues->triage pipeline. `to-issues` + `triage` form a coherent workflow. `ready-for-agent` state is key for AFK agent dispatch.
3. **Structural > Surface**: `improve-codebase-architecture` uses Ousterhout's vocabulary to find structural problems. Complements, not replaces, `techdebt` (which finds surface issues).
4. **Micro-skill tier**: 3-15 line behavioral nudges (`zoom-out`, `caveman`) are high-value and nearly free to load. Loam's lightest skill is ~100 lines.

### Skills to STUDY (8) — design patterns worth absorbing

| Skill | What to learn | Absorb into |
|-------|--------------|-------------|
| **diagnose** | 6-phase debugging with "Build a feedback loop" phase (10 concrete strategies). Deeper than `fix-bug`'s reproduce step | `fix-bug` |
| **to-prd** | Synthesize conversation context into a PRD without interviewing. Complement to `gen-spec` (which interviews) | `gen-spec` |
| **zoom-out** | 10-line micro-skill — pure behavioral nudge. Uses `disable-model-invocation: true` to inject context without consuming an invocation | New micro-skill tier |
| **grill-me** | 15-line Socratic method skill. Matt's self-reported most popular skill. No output artifact, just pure questioning | Reference for simplicity |
| **write-a-skill** | Skill authoring guidance. "The description is the only thing your agent sees" — better description-writing advice than Loam's `create-skill` | `create-skill` |
| **design-an-interface** (deprecated) | "Design It Twice" framing from Ousterhout. Generate 3+ radically different interface designs via parallel sub-agents | `gen-spec`, `feature-dev` |
| **ubiquitous-language** (deprecated) | Extract DDD-style glossary from conversation. "Flagged ambiguities" section. Now absorbed into grill-with-docs as CONTEXT-FORMAT.md | `scaffold-context` |
| **review** (in-progress) | Two-axis review: Standards + Spec. Insight: "a change can pass one axis and fail the other" | `multi-review` |

### Skills to SKIP (11) — and why

| Skill | Why skip |
|-------|---------|
| setup-matt-pocock-skills | Specific to Matt's ecosystem config |
| handoff | Direct overlap with Loam's handoff |
| git-guardrails | Loam already has pre-commit-gate.sh |
| migrate-to-shoehorn | Matt's library-specific |
| scaffold-exercises | Matt's course platform-specific |
| setup-pre-commit | Node/JS-specific (Husky + lint-staged) |
| qa (deprecated) | Subsumed into triage |
| request-refactor-plan (deprecated) | Subsumed into to-prd + to-issues |
| writing-beats | Content creation, not SWE/research |
| writing-fragments | Content creation |
| writing-shape | Content creation |

---

## Tools to Evaluate

### P0 — High value, low effort (timebox: 15 min each)

| Tool | What | Decision |
|------|------|----------|
| [GitHub Official MCP](https://github.com/github/github-mcp-server) | OAuth GitHub access — repos, issues, PRs, Actions | Wire into `.mcp.json.jinja` as optional? |
| [GitMCP](https://gitmcp.io) | Read 3rd-party repo docs via llms.txt. Zero config, no auth | Useful for skill reference loading? |
| [Repomix](https://github.com/yamadashy/repomix) | Pack entire repo into LLM-friendly file. Tree-sitter compression | Worth documenting in BOOTSTRAP.md? |
| [DeepWiki](https://deepwiki.com) | Pre-indexed wiki + Q&A for 50k+ repos. MCP server available | Try the MCP server |
| [madge](https://github.com/pahen/madge) | JS/TS dependency graph. Circular dependency detection. CommonJS/AMD/ES6 | Useful for JS/TS projects bootstrapped from Loam |

### Completed evaluations

| Tool | Status | Notes |
|------|--------|-------|
| [Semble](https://github.com/MinishLab/semble) | **Done** — wired in `seed/.mcp.json.jinja` | Semantic code search MCP. Verify CLI invocation works in a bootstrapped project |
| [drawio-mcp](https://github.com/jgraph/drawio-mcp) | **Done** — wired in `seed/.mcp.json.jinja` + `/diagrams drawio` subcommand | Official draw.io MCP (opens XML/CSV/Mermaid in editor). Replaces claude-mermaid |
| [excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | **Done** — `/diagrams excalidraw` subcommand | Hand-drawn diagrams with Playwright visual self-validation. External skill (user clones) |
| [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) | **Done** — `/diagrams paper` subcommand | Academic illustrations. External tool (HuggingFace Space or self-host) |
| [GitDiagram](https://github.com/ahmedkhaleel2004/gitdiagram) | **Done** — `/diagrams gitdiagram` subcommand | Repo → interactive Mermaid architecture diagram. External web service |
| claude-mermaid MCP | **Replaced** by drawio-mcp | Removed from `.mcp.json.jinja` |
| pyreverse | **Replaced** by excalidraw-diagram-skill | Removed from `/diagrams` skill |
| mcp-image (Gemini image gen) | **Replaced** by PaperBanana | Removed from `.mcp.json.jinja` |
| mingrammer/diagrams | **Replaced** by drawio-mcp | Removed from `/diagrams` skill |

### P1 — Worth evaluating

| Tool | Stars | What | Question |
|------|-------|------|----------|
| [code-review-graph](https://github.com/tirth8205/code-review-graph) | 17k | GraphRAG code review MCP + VSCode ext. Claims 6.8x fewer tokens on reviews | Complements multi-review? |
| [planning-with-files](https://github.com/othmanadi/planning-with-files) | 22k | Manus-style persistent markdown planning. Claude Code skill + multi-editor | Overlaps feature-dev + plan mode? |
| [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | 27k | Task management MCP server + CLI. TypeScript monorepo | Overlaps TaskCreate/TaskUpdate? |
| [Understand-Anything](https://github.com/Lum1104/Understand-Anything) | — | Codebase -> interactive knowledge graph dashboard. 5-agent pipeline. Semantic search | Very new, very capable |
| [UI-UX Pro Max](https://www.claudepluginhub.com/plugins/nextlevelbuilder-ui-ux-pro-max) | — | UI/UX design skill from Claude Plugin Hub | Marketplace candidate? |
| [Impeccable](https://www.claudepluginhub.com/plugins/pbakaus-impeccable) | — | Design quality/polish skill | Marketplace candidate? |

### P2 — Explore when time permits

| Tool | Stars | What | Notes |
|------|-------|------|-------|
| [STORM](https://github.com/stanford-oval/storm) | 28k | LLM-powered knowledge curation, Wikipedia-quality articles with citations | Sheet 1 priority: 10/10. Research lit review + background writing |
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | 20.5k | Autonomous deep-research agent, $0.10/task, Claude MCP integration | Sheet 1 priority: 9/10. Rapid literature surveys |
| [Code2Tutorial](https://github.com/PocketFlow-AI/code2tutorial) | 6k | Codebase -> shareable tutorial. Compare with codebase-to-course in `cultivation/wip/` | Most mature tutorial option |

### Existing WIP — Decision needed

| Item | Status | Decision |
|------|--------|----------|
| `cultivation/wip/codebase-to-course` | Already in repo | Promote to seed, move to marketplace, or compare with Code2Tutorial (6k stars, more mature) first? |

---

## Reference Spreadsheets (human-only, not agent-accessible)

- [AI Repo Master Index](https://docs.google.com/spreadsheets/d/1XijE4g04FVEx3A4cWkLdgZfeBE3i8mcVEjhE9RSwUDw/) — 28+ repos with priority scores for PhD/research use
- [Workflow Alignment](https://docs.google.com/spreadsheets/d/1e_QzjVgDBAl983EzksDp33-0GfU6IoiBVMO7YZBP4SU/) — historical (Graphify eval decisions, completed). Contains tool-to-need mapping for code retrieval, paper-evidence traceability, decision tracking, and codebase orientation
- [Diagram & Tool Matrix](https://docs.google.com/spreadsheets/d/1GtINS1HuMRKGgLFbo0joyWUkLS5erRubGu4kWPhO6VU/) — most actionable, P0-P2 prioritized tools

---

## Techdebt Status (as of 2026-05-22)

Scan completed. **No blockers found.**

- No TODO/FIXME/HACK markers in active template code (all references are in agent/hook logic that scans FOR todos — meta, not debt)
- Marketplace skill formatting drift (agent-team, session-critique have older single-line descriptions vs core's folded scalar) — low priority, not shipped to users
- `cultivation/retired/` empty — intentional slot for future use, leave as-is
- `docs/FUTURE-WORK.md` tracks 2 open design questions (depth-on-demand for dissolved skills, skill composition/middleware pattern) — no action needed now
