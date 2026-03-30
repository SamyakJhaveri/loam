# Claude Desktop App: F1 Architecture Diagram Guide

> **Purpose:** Step-by-step guide for creating ParBench's F1 system architecture diagram
> using Claude Desktop App (Opus 4.6) on macOS, targeting IEEE SC26 publication quality.
>
> **Created:** 2026-03-30 | **Author:** desktop-guide agent

---

## Part 1: MCP Server Setup

### 1.1 Configuration File Location (macOS)

All MCP server configurations go in:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**To access:** Claude Desktop > Menu Bar > Settings > Developer > Edit Config

If the file does not exist, Claude Desktop creates it when you first open Edit Config.

---

### 1.2 Diagram MCP Servers Evaluated

#### A. `claude-mermaid` (veelenga) -- GOOD for flowcharts, LIMITED for architecture

- **Install:**
  ```bash
  git clone https://github.com/veelenga/claude-mermaid.git
  cd claude-mermaid
  npm install && npm run build && npm install -g .
  ```
- **Config snippet:**
  ```json
  {
    "mcpServers": {
      "mermaid": {
        "command": "claude-mermaid"
      }
    }
  }
  ```
- **What it does:** Renders Mermaid diagrams in a browser tab with live reload via WebSocket. Supports SVG, PNG, and PDF export via the `mermaid_save` tool. Themes: default, forest, dark, neutral.
- **Limitations:** Live preview only works for SVG (PNG/PDF rendered without live reload). Mermaid's layout engine has limited control over precise positioning -- fine for flowcharts and sequence diagrams, but architecture diagrams with nested boxes, custom shapes, and precise spatial layout are difficult to achieve. Font control is limited to what Mermaid supports.
- **Verdict:** Not the best choice for a publication-quality architecture diagram. Mermaid's automatic layout fights against the precise spatial control needed for IEEE figures.

#### B. `@drawio/mcp` (official, jgraph) -- GOOD for interactive editing, MODERATE for publication

- **Install (zero-install via npx):**
  ```bash
  # No pre-installation needed -- npx handles it
  ```
- **Config snippet:**
  ```json
  {
    "mcpServers": {
      "drawio": {
        "command": "npx",
        "args": ["-y", "@drawio/mcp"]
      }
    }
  }
  ```
- **Alternative (hosted, no install):** Use `https://mcp.draw.io/mcp` as a remote MCP server (check Claude Desktop's remote MCP support).
- **What it does:** Opens draw.io editor in browser, supports native draw.io XML format, CSV-to-diagram import, and Mermaid-to-draw.io conversion. Rich shape library with full drag-and-drop editing.
- **Limitations:** The MCP opens a browser-based editor -- you lose the conversational iteration loop (Claude generates XML, you manually edit in browser). Export to PDF is draw.io-native (good quality but may not match LaTeX fonts). No direct TikZ export.
- **Verdict:** Best if you want a WYSIWYG editor with AI-generated starting points. Less ideal for rapid conversational iteration within Claude Desktop itself.

#### C. `d2mcp` (i2y) -- BEST for architecture diagrams, GOOD publication quality

- **Install:**
  ```bash
  # Requires Go installed
  go install github.com/i2y/d2mcp/cmd@latest
  # Or clone and build:
  git clone https://github.com/i2y/d2mcp.git
  cd d2mcp && make build
  ```
- **Config snippet:**
  ```json
  {
    "mcpServers": {
      "d2": {
        "command": "/path/to/d2mcp"
      }
    }
  }
  ```
  Replace `/path/to/d2mcp` with the actual binary path (e.g., `~/go/bin/cmd` or the build output). Find it with `which d2mcp` or `ls ~/go/bin/`.
- **What it does:** D2 is a modern diagram scripting language purpose-built for software architecture diagrams. The MCP exposes an Oracle API for incremental diagram building -- you describe changes in conversation, and Claude applies them step by step. Supports SVG and PNG export. Multiple layout engines: dagre (hierarchical), ELK (node-link with ports), TALA (architecture-specific).
- **Limitations:** PDF export currently uses Playwright to capture a PNG (rasterized, not vector). For publication quality, export as SVG and convert externally. D2 requires the `d2` CLI to be installed separately (`brew install d2` on macOS).
- **Verdict:** Strong choice for architecture diagrams. D2's text-based syntax gives Claude precise control over layout, and the Oracle API enables true conversational iteration. SVG output is clean and editable.

#### D. `excalidraw-mcp` (official) -- BEST for rapid iteration, MODERATE publication quality

- **Install (zero-install via npx):**
  ```bash
  npx excalidraw-mcp
  ```
- **Config snippet:**
  ```json
  {
    "mcpServers": {
      "excalidraw": {
        "command": "npx",
        "args": ["-y", "excalidraw-mcp"]
      }
    }
  }
  ```
- **What it does:** Streams hand-drawn-style Excalidraw diagrams with smooth viewport camera control and interactive fullscreen editing. Supports real-time canvas sync -- Claude can update the diagram as you talk. Works as an MCP App that renders inline in the chat or in a fullscreen canvas.
- **Limitations:** Excalidraw's hand-drawn aesthetic is charming but may not suit a formal IEEE publication. Export to SVG is supported, but font rendering uses Excalidraw's handwriting-style fonts by default. You would need post-processing to match IEEE template fonts.
- **Verdict:** Fastest iteration loop of all options. Excellent for brainstorming and draft layout. Not ideal as the final publication format without significant post-processing.

#### E. Other Notable MCP Servers

| Server | What it does | Publication suitability |
|--------|-------------|----------------------|
| `mcp-mermaid` (hustcc) | Alternative Mermaid renderer, multi-transport | Same Mermaid limitations |
| `@peng-shawn/mermaid-mcp-server` | Puppeteer-based Mermaid-to-PNG/SVG | Same Mermaid limitations |
| `sailor` (aj-geddes) | Web UI + MCP for Mermaid | Nice UI, same limitations |
| `drawio-mcp-server` (lgazo) | Community draw.io MCP | Similar to official @drawio/mcp |
| `mcp_excalidraw` (yctimlin) | Community Excalidraw with Claude Code skill | Good for Claude Code, not Desktop |
| `ai-diagram-maker-mcp` (erajasekar) | Multi-format diagram maker | Newer, less tested |

---

### 1.3 Claude Desktop's Built-In Capabilities

#### SVG Artifacts (NO MCP needed)

Claude Desktop can generate SVG code directly as an artifact. This is the **simplest approach** and requires zero setup:

- Claude generates inline SVG code
- It renders in the artifact preview panel
- You can download the `.svg` file directly (download button in artifact panel)
- You can iterate conversationally: "move the Harness box to the right", "make the arrow dashed"
- Supports full SVG spec: gradients, patterns, text, paths, groups, transforms

#### Interactive Visuals (March 2026 feature)

As of March 2026, Claude Desktop renders interactive visuals (HTML+SVG) inline between paragraphs of responses -- not in a separate artifact panel. These support hover and click interactions. However, they are more conversational aids than exportable publication figures.

#### Mermaid in Artifacts

Claude can render Mermaid diagrams directly in artifacts without any MCP server. The artifact panel has built-in Mermaid rendering. This is useful for quick diagrams but has the same layout limitations as the MCP-based Mermaid approach.

---

### 1.4 Filesystem MCP (for repo access)

To give Claude Desktop read/write access to your ParBench repo:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/samyakjhaveri/Desktop/parbench_sam"
      ]
    }
  }
}
```

This lets Claude read your spec files, harness code, and results to inform the diagram, and write the final SVG directly to your repo.

---

### 1.5 Claude Desktop Projects Feature (March 2026)

As of March 20, 2026, Claude Desktop supports **Projects** (part of Cowork):

1. Click "New Project" > "Use an existing folder"
2. Select `/Users/samyakjhaveri/Desktop/parbench_sam`
3. Name it "ParBench SC26"
4. Add custom instructions (e.g., "You are helping create figures for an IEEE SC26 paper")
5. Attach key files as context (e.g., `CLAUDE.md`, spec examples)

Projects give you persistent context, memory, and file access across conversations. This is **complementary** to MCP servers -- use Projects for context, MCP for diagram tools.

---

### 1.6 Recommended `claude_desktop_config.json`

This configuration gives you the best combination of tools:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/samyakjhaveri/Desktop/parbench_sam"
      ]
    },
    "drawio": {
      "command": "npx",
      "args": ["-y", "@drawio/mcp"]
    },
    "excalidraw": {
      "command": "npx",
      "args": ["-y", "excalidraw-mcp"]
    }
  }
}
```

**Why this combination:**
- **Filesystem**: Lets Claude read your codebase for accurate diagram content
- **Draw.io**: For polished, publication-ready diagram editing when you need fine control
- **Excalidraw**: For rapid brainstorming and layout iteration

**Optional additions** (if you install the prerequisites):
```json
    "d2": {
      "command": "/usr/local/bin/d2mcp"
    },
    "mermaid": {
      "command": "claude-mermaid"
    }
```

After editing, **fully quit Claude Desktop** (Cmd+Q, not just close window) and relaunch. Look for the MCP server indicator (hammer icon) in the bottom of the chat input box.

---

## Part 2: Recommended Workflow

### 2.1 Decision Matrix

| Approach | Iteration speed | Publication quality | Setup effort | Best for |
|----------|----------------|-------------------|-------------|---------|
| **Built-in SVG artifact** | Fast | High (with care) | None | **RECOMMENDED** |
| D2 via d2mcp | Medium | High (SVG export) | Moderate (Go + D2) | Complex layouts |
| Draw.io via @drawio/mcp | Slow (browser) | High | Low (npx) | WYSIWYG polish |
| Excalidraw via MCP | Fastest | Low (hand-drawn style) | Low (npx) | Brainstorming |
| Mermaid (built-in or MCP) | Fast | Medium | None/Low | Simple flowcharts |

### 2.2 Recommended Approach: Built-in SVG Artifact

**The built-in SVG artifact is the best balance of iteration speed and publication quality for this task.** Here is why:

1. **Zero setup**: No MCP servers needed. Works immediately.
2. **Full control**: Claude generates raw SVG, giving pixel-perfect control over every element -- positions, sizes, colors, fonts, arrows, text.
3. **Fast iteration**: Describe changes in natural language, Claude regenerates the SVG. Each iteration takes seconds.
4. **Direct export**: Download the `.svg` file from the artifact panel.
5. **Font matching**: SVG `<text>` elements can specify any font family, so you can match your LaTeX template's fonts exactly.
6. **Grayscale safety**: You can ask Claude to verify that the color scheme works in grayscale by rendering a desaturated version.

**The workflow:**

```
1. Paste the prompt from Part 3 into Claude Desktop (Opus 4.6)
2. Claude generates an SVG artifact showing the architecture
3. Review the artifact preview
4. Request changes: "Make the self-repair arrow loop back from Verify to Evaluation"
5. Claude regenerates the SVG with your changes
6. Repeat until satisfied (typically 5-10 iterations)
7. Download the final .svg
8. Convert to PDF for LaTeX inclusion (see Part 4)
```

### 2.3 Alternative: Two-Phase Approach (Excalidraw then SVG)

If you prefer to brainstorm layout first:

1. **Phase 1 (Excalidraw MCP):** "Draw a rough architecture diagram of ParBench" -- iterate quickly on layout and component placement using Excalidraw's fast canvas
2. **Phase 2 (SVG Artifact):** Once layout is settled, ask Claude to recreate it as a precise SVG artifact with publication styling

### 2.4 Can Claude Desktop Export to TikZ or PDF Directly?

- **TikZ:** No. Claude can *generate TikZ code* as a text artifact, but cannot preview/render it. You would paste the TikZ into your LaTeX document and compile to see the result. This breaks the visual iteration loop.
- **PDF:** No direct PDF export from artifacts. Export as SVG, then convert (see Part 4).
- **Recommendation:** Stay in SVG for iteration, convert to PDF only at the end.

---

## Part 3: Ready-to-Paste Prompt

Copy everything between the `---START---` and `---END---` markers and paste it into a new Claude Desktop conversation (Opus 4.6):

---START---

I need you to create a publication-quality system architecture diagram for my SC26 paper as an SVG artifact. This is Figure 1 (F1) of the paper.

## System Being Diagrammed: ParBench

ParBench is a benchmark and evaluation framework for assessing LLM-based parallel code translation. The system has these components and data flows:

### Components (boxes/nodes)

1. **Benchmark Specs** (input) -- JSON spec files defining benchmark kernels, each specifying source code location, build commands, run arguments, and verification criteria. Shape: document/cylinder icon.

2. **Source Code** -- Original parallel source code in CUDA, OpenMP, or OpenCL from benchmark suites (Rodinia, XSBench, HeCBench). Shape: code file icon or folder.

3. **Augmentation Engine** -- AST-driven code transformation pipeline (`c_augmentation/`) that applies semantic-preserving transforms (variable renaming, loop restructuring, condition swapping, comment stripping) at 4 difficulty levels (L1-L4) to create augmented variants of the source. Shape: gear/processor box.

4. **LLM Evaluation Pipeline** -- Orchestrates the translation task: constructs prompts from specs + source code (original or augmented), sends to LLM APIs, extracts translated code from responses, and manages multi-attempt self-repair. Shape: large central box. Internal label: "Evaluation Pipeline".

5. **LLM** -- The language model being evaluated (Claude Sonnet 4, Gemini 2.5 Flash-Lite, Groq Llama 3.3 70B). External service. Shape: cloud.

6. **Harness** -- Build/Run/Verify pipeline that tests translated code. Contains three internal stages: (a) Build -- compiles translated code with appropriate toolchain, (b) Run -- executes with spec-defined arguments, (c) Verify -- compares output against reference using stdout pattern matching + exit code. Shape: box with 3 internal compartments.

7. **Result JSON** (output) -- Structured evaluation results recording overall_status (PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL), timing data, attempt history, error snippets. Shape: document icon.

### Data Flows (arrows)

- Benchmark Specs --> Evaluation Pipeline (spec defines the translation task)
- Source Code --> Augmentation Engine (original code fed to augmenter)
- Augmentation Engine --> Evaluation Pipeline (augmented code variants fed as input)
- Source Code --> Evaluation Pipeline (original code also fed directly for L0 baseline)
- Evaluation Pipeline --> LLM (prompt with source + target API specification)
- LLM --> Evaluation Pipeline (translated code response)
- Evaluation Pipeline --> Harness (extracted translated code files)
- Harness/Build --> Harness/Run --> Harness/Verify (internal pipeline flow)
- Harness --> Result JSON (verification outcome)
- Harness --> Evaluation Pipeline (self-repair feedback loop: on BUILD_FAIL or RUN_FAIL, error information feeds back to construct a repair prompt for the next attempt, up to 3 attempts)

### Layout

- Left-to-right primary flow: Specs + Source on left, Pipeline in center, Harness and Results on right
- Augmentation Engine below or above the main flow, connecting Source Code to Pipeline
- Self-repair feedback arrow loops back from Harness to Pipeline (curved arrow, below the main flow)
- LLM cloud above the Pipeline, with bidirectional arrows

## Publication Requirements

- **Target:** IEEE SC26 conference paper
- **Figure width:** 7.16 inches (full double-column width = 182mm)
- **Minimum font size:** 8pt (approximately 10.67px in SVG at 96 DPI)
- **Font family:** Use "Helvetica, Arial, sans-serif" for labels (close match to IEEE template sans-serif). Use "Courier New, monospace" only for code-like labels if needed.
- **Output format:** SVG artifact that I can download
- **Must be grayscale-safe:** The diagram must remain legible when printed in black and white

## Color Palette: Okabe-Ito (colorblind-safe)

Use these colors for component fills (with white/light text or black text as appropriate for contrast):

| Color | Hex | Use for |
|-------|-----|---------|
| Blue | #0072B2 | Evaluation Pipeline (central, primary) |
| Orange | #E69F00 | Augmentation Engine |
| Sky Blue | #56B4E9 | Harness (Build/Run/Verify) |
| Bluish Green | #009E73 | Result JSON (success/output) |
| Vermillion | #D55E00 | Self-repair feedback arrow |
| Black | #000000 | Text, borders, standard arrows |
| Light Gray | #F0F0F0 | Benchmark Specs, Source Code (input documents) |

Use these at reduced opacity (0.15-0.25) as background fills with full-opacity borders, so text remains readable. Or use them as border/accent colors with white fills. Whichever produces better contrast.

## Style Requirements

- Clean, professional appearance suitable for a top-tier HPC venue
- Rounded rectangle corners (rx=4-6) for component boxes
- Arrowheads on all flow arrows
- Dashed border for the LLM cloud (external service)
- The self-repair feedback loop should be visually distinct (vermillion color, curved/looping arrow)
- Include a minimal legend if more than 4 colors are used
- No decorative elements -- every visual element must convey information

## SVG Technical Requirements

- ViewBox sized for 7.16 inches wide (687px at 96 DPI) by approximately 4-5 inches tall
- All text as `<text>` elements (not paths) so fonts can be changed later
- Group related elements with `<g>` tags for easy editing
- Use `marker-end` for arrowheads defined in `<defs>`
- Include XML namespace: `xmlns="http://www.w3.org/2000/svg"`

Please generate the SVG as an artifact. After I review it, I will request specific changes iteratively until we reach the final version.

---END---

---

## Part 4: From Draft to Publication

### 4.1 Export the SVG from Claude Desktop

1. In the artifact panel, click the **download icon** (arrow pointing into box) in the lower-right corner
2. Save as `f1_architecture.svg` to your repo:
   ```
   /Users/samyakjhaveri/Desktop/parbench_sam/docs/paper/figures/f1_architecture.svg
   ```

### 4.2 Convert SVG to PDF (for LaTeX)

**Option A: Inkscape CLI (recommended -- preserves vectors)**
```bash
# Install Inkscape if not present
brew install --cask inkscape

# Convert SVG to PDF (vector, no rasterization)
inkscape docs/paper/figures/f1_architecture.svg \
  --export-type=pdf \
  --export-filename=docs/paper/figures/f1_architecture.pdf
```

**Option B: Inkscape with LaTeX text overlay (best font matching)**
```bash
# Export PDF + LaTeX text overlay
inkscape docs/paper/figures/f1_architecture.svg \
  --export-type=pdf \
  --export-latex \
  --export-filename=docs/paper/figures/f1_architecture.pdf
```
This creates two files:
- `f1_architecture.pdf` -- the graphics (no text)
- `f1_architecture.pdf_tex` -- LaTeX commands that overlay text

In your LaTeX document:
```latex
\begin{figure*}[t]
  \centering
  \def\svgwidth{\textwidth}
  \input{figures/f1_architecture.pdf_tex}
  \caption{ParBench system architecture. Benchmark specs and source code
    (optionally augmented) are translated by an LLM, then verified through
    a Build/Run/Verify harness with self-repair feedback.}
  \label{fig:architecture}
\end{figure*}
```

**Option C: CairoSVG (Python, quick conversion)**
```bash
pip install cairosvg
python3 -c "import cairosvg; cairosvg.svg2pdf(url='docs/paper/figures/f1_architecture.svg', write_to='docs/paper/figures/f1_architecture.pdf')"
```

**Option D: Direct PDF includegraphics (simplest)**
```bash
# After Inkscape conversion (Option A), use in LaTeX:
```
```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/f1_architecture.pdf}
  \caption{ParBench system architecture...}
  \label{fig:architecture}
\end{figure*}
```

### 4.3 Convert SVG to TikZ (optional, for full LaTeX-native figures)

If you want the figure entirely in TikZ (for perfect font matching):

**Tool: svg2tikz**
```bash
pip install svg2tikz

# Convert SVG to TikZ
svg2tikz docs/paper/figures/f1_architecture.svg > docs/paper/figures/f1_architecture.tex
```

Then in your main paper file:
```latex
\begin{figure*}[t]
  \centering
  \input{figures/f1_architecture.tex}
  \caption{ParBench system architecture...}
  \label{fig:architecture}
\end{figure*}
```

**Caveat:** svg2tikz output often needs manual cleanup. Complex SVGs with gradients or filters may not convert cleanly. For architecture diagrams with simple shapes, it works well.

**Alternative approach:** Ask Claude Desktop to generate TikZ code directly (as a text artifact), paste into your LaTeX project, compile, review, and iterate. This skips the SVG step entirely but loses the visual preview loop in Claude Desktop.

### 4.4 Font Matching Considerations

| IEEE template font | SVG equivalent | Notes |
|-------------------|---------------|-------|
| Times New Roman (body) | `font-family="Times New Roman, Times, serif"` | Only if figure labels match body text |
| Helvetica/Arial (figures) | `font-family="Helvetica, Arial, sans-serif"` | Most IEEE figures use sans-serif |
| Computer Modern (LaTeX default) | No SVG equivalent | Use Inkscape PDF+LaTeX export (Option B) for perfect matching |

**Recommendation:** Use Helvetica/Arial in the SVG. IEEE templates typically use sans-serif fonts in figures, so this matches well. If your paper uses Computer Modern, use the Inkscape `--export-latex` option (Option B above) to let LaTeX render the text natively.

### 4.5 Grayscale Verification

Before finalizing, verify the diagram is readable in grayscale:

```bash
# Convert to grayscale PNG for verification
inkscape docs/paper/figures/f1_architecture.svg \
  --export-type=png \
  --export-filename=/tmp/f1_grayscale_check.png

# Then desaturate with ImageMagick
convert /tmp/f1_grayscale_check.png -colorspace Gray /tmp/f1_grayscale.png
open /tmp/f1_grayscale.png
```

Or ask Claude Desktop: "Show me this diagram in grayscale to verify readability."

### 4.6 Bringing the Final Figure into the Repo

```bash
# Create figures directory if needed
mkdir -p /Users/samyakjhaveri/Desktop/parbench_sam/docs/paper/figures

# Save SVG (source of truth)
# Already saved in step 4.1

# Generate PDF
inkscape docs/paper/figures/f1_architecture.svg \
  --export-type=pdf \
  --export-filename=docs/paper/figures/f1_architecture.pdf

# Commit both
cd /Users/samyakjhaveri/Desktop/parbench_sam
git add docs/paper/figures/f1_architecture.svg docs/paper/figures/f1_architecture.pdf
git commit -m "Add F1 system architecture diagram for SC26 paper"
```

---

## Quick Reference: Complete Setup Checklist

- [ ] Open Claude Desktop > Settings > Developer > Edit Config
- [ ] Add filesystem MCP server pointing to `/Users/samyakjhaveri/Desktop/parbench_sam`
- [ ] (Optional) Add draw.io and/or excalidraw MCP servers
- [ ] Fully quit and relaunch Claude Desktop (Cmd+Q, then reopen)
- [ ] Verify MCP indicator (hammer icon) appears in chat input
- [ ] Start a new conversation with Opus 4.6
- [ ] Paste the prompt from Part 3
- [ ] Iterate on the SVG artifact (aim for 5-10 rounds)
- [ ] Download final SVG
- [ ] Convert to PDF via Inkscape
- [ ] Include in LaTeX with `\includegraphics` or `\input` (pdf_tex)
- [ ] Verify grayscale readability
- [ ] Commit SVG + PDF to repo

---

## Appendix: Okabe-Ito Palette Reference

```
Orange:        #E69F00  rgb(230, 159, 0)
Sky Blue:      #56B4E9  rgb(86, 180, 233)
Bluish Green:  #009E73  rgb(0, 158, 115)
Yellow:        #F0E442  rgb(240, 228, 66)
Blue:          #0072B2  rgb(0, 114, 178)
Vermillion:    #D55E00  rgb(213, 94, 0)
Reddish Purple:#CC79A7  rgb(204, 121, 167)
Black:         #000000  rgb(0, 0, 0)
Gray:          #999999  rgb(153, 153, 153)
```

The Okabe-Ito palette was proposed by Okabe and Ito (2008) and is the gold standard for
colorblind-safe categorical color palettes in scientific figures. It is recommended by
Nature Methods (also known as the "Wong palette") and is the default in Claus Wilke's
"Fundamentals of Data Visualization."
