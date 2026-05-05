# reproduce.sh — Changes from Original

## Problem

The original script was written for a Docker container where the project was mounted at `/app`.
Running it outside Docker failed in two ways:

1. `ModuleNotFoundError: No module named 'harness'` — Python couldn't find the `harness` package because the project root wasn't on `PYTHONPATH`.
2. Steps 2, 3, and 5 silently read from and wrote to `/app/...` paths that don't exist outside the container, producing empty results and crashing Step 3.

## Changes Made

### 1. Dynamic project root detection (new, lines 6–8)

```bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
```

Resolves the project root from the script's own location, changes into it, and adds it to
`PYTHONPATH`. This makes `import harness` work regardless of where the script is called from.

### 2. Dependency pre-check (new, lines 10–13)

```bash
if ! python3 -c "import harness" 2>/dev/null; then
    echo "ERROR: 'harness' module not found. Run: pip install -e ." >&2
    exit 1
fi
```

Fails fast with a clear message instead of crashing mid-run on a missing import.

### 3. Default output directory (line 18, was line 12)

```bash
# Before
OUTPUT_DIR="${1:-/app/output}"

# After
OUTPUT_DIR="${1:-$PROJECT_ROOT/output}"
```

### 4. `--project-root` flags (Steps 2, 3, 5)

All five occurrences of `--project-root /app` replaced with `--project-root "$PROJECT_ROOT"`:

- Step 2: `quantitative_findings.py` × 3 calls
- Step 3: `statistical_analysis.py` × 1 call
- Step 5: `generate_paper_figures.py` × 1 call

### 5. Missing dependency: `scienceplots`

`scripts/generate_paper_figures.py` imports `scienceplots` which is not listed in
`requirements-lock.txt`. Install it before running:

```bash
pip install scienceplots
```

Or add it to `requirements-lock.txt` / `pyproject.toml` so it is pulled in automatically.

## Verified Output

After these changes, `bash reproduce.sh` completes all 5 steps and produces 35 files:

- `output/t1_overall_pass.tex` through `t5_stats.tex` (5 LaTeX tables)
- `output/f2_*` through `f7_*` and `c4_*` (15 figures × PNG + PDF = 30 files)

C.1, C.2, C.3 are skipped with warnings (`No multi-attempt results found`) — this is
expected behaviour when the artifact does not include multi-attempt / self-repair result data.
