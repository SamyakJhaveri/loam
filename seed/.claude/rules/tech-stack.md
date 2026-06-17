---
paths:
  - "**/*.py"
  - "requirements*.txt"
  - "pyproject.toml"
  - "**/Makefile"
  - "setup.py"
  - "setup.cfg"
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
