# CLAUDE.md — ParBench Project Instructions

## Environment

- **Always activate the venv first:** `source env_parbench/bin/activate`
- **Python version:** 3.12.3 (interpreter: `python3.12`)
- **Inside the venv**, `python`, `python3`, and `python3.12` all resolve to the same `python3.12` binary.
- **Use `python3`** for all commands within the venv (not bare `python`).
- **Install packages** with `python3 -m pip install <pkg>` inside the activated venv if missing.
- **Site-packages:** fully isolated (`include-system-site-packages = false`) — system packages are not visible inside the venv.
- **Venv was created from** `python3` which resolved to `python3.12` at creation time.

## config/paths.json

The `config/paths.json` file has been updated for this Mac:

```json
{
    "project_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "downloads_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "hecbench_root": "/Users/samyakjhaveri/Desktop/parbench_sam/HeCBench-master"
}
```

**`downloads_root` is the project root** (`/Users/samyakjhaveri/Desktop/parbench_sam`). All `source_dir` fields in `manifest.jsonl` are relative to `downloads_root`. So a Rodinia entry like `"source_dir": "rodinia/rodinia-src/cuda/hotspot"` resolves to `<project_root>/rodinia/rodinia-src/cuda/hotspot`.

HeCBench is **not present** on this Mac. The 120 HeCBench `source_dir` disk-not-found errors from `validate_schema.py --all` are pre-existing and expected — do not try to fix them.

## Spec Generation Rules

### unique_id and kernel_name must be slugified

The `identity.unique_id` must match `^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$` (lowercase only). Therefore:

- `identity.kernel_name` must also be the **slug** (lowercase, `+` removed, no uppercase)
- `unique_id` = `{source_suite}-{slug}-{parallel_api}`
- The filename = `{source_suite}-{slug}-{parallel_api}.json`

Examples of required slugification:
- `b+tree` → `btree`
- `hotspot3D` → `hotspot3d`
- `lavaMD` → `lavamd`

The cross-checker in `validate_schema.py` builds `expected_id = source_suite + kernel_name + parallel_api`. If `kernel_name` in the spec identity is not slugified, the check will report a mismatch.

### manifest category enum

The `category` field in `manifest.jsonl` must be one of:

```
ml, graph, physics, linear_algebra, stencil, reduction, sort,
molecular_dynamics, image, crypto, financial, other
```

Do NOT use: `simulation`, `image_processing`, `data_structures`, `compression`, `sorting`, `bioinformatics`, `scientific`, `data_mining`, `algorithms`.

Mapping to use:
- image processing → `image`
- simulation / physics / fluid dynamics → `physics`
- sorting → `sort`
- data structures, compression, bioinformatics, data mining → `other`

### manifest kernel_name must match spec identity.kernel_name

The validator cross-checks `manifest.kernel_name == spec.identity.kernel_name`. Both must use the same slugified name.

## Validation

```bash
python3 scripts/validate_schema.py --all
```

Expected: 120 pre-existing HeCBench errors (source dirs not on disk). All Rodinia and new specs should show `✓`.

To validate a single spec:
```bash
python3 scripts/validate_schema.py --spec specs/<name>.json
```

## Project Layout

- `specs/` — one `{suite}-{slug}-{api}.json` per kernel-API variant
- `manifest.jsonl` — one JSON line per variant (append only; do not modify existing entries)
- `analysis/` — survey JSONs and reports
- `schema/spec_schema.json` — Level 2 spec schema (v1.0.0)
- `schema/manifest_schema.json` — manifest entry schema
- `scripts/generate_rodinia_specs.py` — Rodinia spec generator (use `--force` to overwrite, `--dry-run` to preview)
- `rodinia/rodinia-src/` — Rodinia source (commit `9c10d3ea`, from https://github.com/yuhc/gpu-rodinia)

## Adding New Benchmark Suites

1. Clone source into a subdirectory of `parbench_sam/` (e.g., `polybench/polybench-src/`)
2. Update `config/paths.json` only if `downloads_root` needs to change
3. Write a generator script in `scripts/`
4. Spec filenames: `{suite}-{slug}-{api}.json`
5. Run `python3 scripts/validate_schema.py --all` and fix any errors before committing
