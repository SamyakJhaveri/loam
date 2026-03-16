# Spec & Manifest Conventions

> Auto-loaded when working on `specs/` or `manifest.jsonl`.

## Slugification (validator enforces this)

`identity.unique_id` regex: `^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$`

- `kernel_name` = slug: lowercase, `+` removed, no uppercase
- `unique_id` = `{source_suite}-{slug}-{parallel_api}`
- Filename = `{source_suite}-{slug}-{parallel_api}.json`
- Examples: `b+tree`→`btree`, `hotspot3D`→`hotspot3d`, `lavaMD`→`lavamd`

## Category Enum (manifest.jsonl)

**Allowed:** `ml graph physics linear_algebra stencil reduction sort molecular_dynamics image crypto financial other`

**Forbidden aliases:** `simulation`, `image_processing`, `data_structures`, `compression`, `sorting`, `bioinformatics`, `scientific`, `data_mining`, `algorithms`

**Mappings:**
- image processing → `image`
- simulation/physics/fluid → `physics`
- sorting → `sort`
- data structures/compression/bioinformatics/data mining → `other`

## Manifest Rules

- `manifest.jsonl` is **append-only** — never modify existing entries
- Cross-check: `manifest.kernel_name == spec.identity.kernel_name` (both must be identical slugs)
- `source_dir` fields are relative to `downloads_root` in `config/paths.json`

## Validation

```bash
# All specs (120 HeCBench errors are expected)
python3 scripts/validate_schema.py --all

# Single spec
python3 scripts/validate_schema.py --spec specs/<name>.json
```
