---
paths:
  - "**/*.py"
  - "requirements*.txt"
  - "pyproject.toml"
  - "**/Makefile"
  - "setup.py"
  - "setup.cfg"
  - "**/*.c"
  - "**/*.cc"
  - "**/*.cpp"
  - "**/*.cu"
---

# Technology Stack

> Conditional: loads on Python/build files. Fill in your project's specifics below.

## Languages

<!-- List primary languages used in this project -->
- Python 3.12+ — Pipeline code, scripts, tooling

## Runtime

<!-- Describe your runtime environment -->
- Python 3.12+
- uv-managed: `uv run <cmd>` / `uv sync --group <group>` (no manual venv activation)
- Always `python3`, never bare `python`

## Package Manager

- uv (`uv sync`, `uv run`) — never pip; deps live in `[dependency-groups]`
- Build system: configured in `pyproject.toml`

## Key Dependencies

<!-- Fill in your project's key dependencies -->
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | latest | Test runner |
| ruff | latest | Lint/format |

## Build Tools

<!-- List compilers, build systems, etc. -->
- setuptools (configured in `pyproject.toml`)

## Configuration

<!-- Describe config file locations and formats -->
- `pyproject.toml` — Project metadata, dependencies, tool config

## Platform Requirements

<!-- Describe target platform(s) -->
- macOS / Linux
- Python 3.12+

## Code intelligence (LSP plugins)

`.claude/settings.json` `enabledPlugins` ships two `claude-plugins-official` LSP
plugins enabled by default — `pyright-lsp` (Python) and `clangd-lsp` (C/C++) —
for go-to-definition, find-references, and post-edit diagnostics in place of
grep-then-read sweeps.

**Collaborator enablement.** `claude-plugins-official` auto-registers the first
time you launch Claude Code *interactively*, so trusting the repo should prompt
you to enable the project-declared plugins. If the prompt doesn't appear (a known
gap on some Claude Code versions) or you run non-interactively / in CI, register
+ enable manually: `claude plugin marketplace add anthropics/claude-plugins-official`,
then enable via `/plugin`. Codex does **not** read `enabledPlugins` — this is
Claude-Code-only.

**Binaries (per-machine, required on PATH):**
- `pyright-langserver` — `npm i -g pyright`
- `clangd` — macOS: Xcode CLT or `brew install llvm`; Linux: `apt install clangd`

A missing binary is non-fatal: it shows only in the `/plugin` Errors tab and
Claude falls back to grep — so `clangd` enabled in a pure-Python project costs
nothing.

**clangd needs a compile DB to be accurate.** Without a `compile_commands.json`,
clangd reports valid C/C++ as broken (missing system / third-party headers,
unknown macros or pragmas, custom toolchains). Treat its diagnostics on such
trees as unreliable and don't act on them; when you need accuracy, generate a
compile DB (CMake `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`, or `bear -- make`).
