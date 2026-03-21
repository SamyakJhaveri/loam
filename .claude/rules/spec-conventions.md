---
paths:
  - "specs/**"
  - "manifest.jsonl"
---

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

## Run Argument Verification Protocol (MANDATORY)

**This protocol exists because of a March 2026 incident where Claude "fixed" nw-omp and
hotspot-omp run args based on incorrect source reading, documented the wrong fix as correct
in known-issues.md, and caused 2 specs to fail for weeks. Read the actual source. Always.**

Before changing any `run.arguments`, `default_arguments`, or `input_configurations` in a spec:

### Step 1 — Read the source's argument parser
Run these in the source directory, not from memory:
```bash
grep -n "argc" <source_file>        # Find argc checks (e.g. argc != 8, argc == 4)
grep -n "argv\[" <source_file>      # Find argument accesses (e.g. argv[1], argv[7])
grep -n "usage\|Usage\|fprintf" <source_file>  # Find usage string with expected arg names
```
**Record the exact line and the exact check.** Do not guess.

### Step 2 — Check the baseline evidence
Read the spec's `baseline_results.configurations.correctness.stdout_snippet`.
This is recorded output from a working run — it often contains runtime evidence
of the expected arguments (e.g., "Num of threads: 4" proves a thread count arg is required).

If the baseline `status` is `"pass"`, the recorded stdout is ground truth.
If args are being "fixed" but the baseline was passing, the fix is almost certainly wrong.

### Step 3 — Document the source evidence
When recording a fix in `known-issues.md`, include:
- The exact source file and line number of the argc check
- The exact argc comparison (e.g., `needle.cpp:249: if (argc == 4)`)
- The expected arg count derived from that check
- The baseline stdout snippet that confirms the behavior

### Step 4 — Do not trust known-issues.md as source of truth for code behavior
`known-issues.md` documents human observations, which can be wrong.
The actual source code and the baseline stdout_snippet are ground truth.
When known-issues.md contradicts the source, the **source wins** — update known-issues.md.

## Validation

```bash
# All specs (~135 errors are expected as of 2026-03-20 — see known-issues.md)
python3 scripts/validate_schema.py --all

# Single spec
python3 scripts/validate_schema.py --spec specs/<name>.json
```
