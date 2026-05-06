---
name: spec-validator
description: "Validates new or modified kernel specs against ParBench spec-conventions.md rules. Use when creating a new spec JSON, when modifying run arguments or oracle configuration, when adding a spec to manifest.jsonl, or when /gen-spec produces a draft that needs validation. Checks slugification, category enum, run arg verification against source argc, oracle configuration, and manifest cross-reference. More thorough than schema validation alone — enforces the project's hard-learned conventions."
---

# Spec Validator

Validates kernel spec JSONs against ParBench conventions. Goes beyond schema validation
to enforce the project's hard-learned rules about naming, run arguments, and oracle
configuration.

**Trigger:** `/spec-validator <spec-name>` or when creating/modifying specs.

## Arguments

- `$ARGUMENTS` — spec name without `.json` extension (e.g., `rodinia-srad-cuda`)
- If no argument, validate all specs in `specs/` directory.

## Prerequisites

- Project root: `{{PROJECT_ROOT}}`
- Venv: `source {{PROJECT_ROOT}}/env_parbench/bin/activate`

## Validation Checks

### 1. Slugification (MUST PASS)

Read the spec's `identity` block and verify:

```bash
# unique_id must match regex: ^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$
# kernel_name must be lowercase, no '+' characters
# unique_id = {source_suite}-{slug}-{parallel_api}
# Filename must match unique_id + .json
```

**Known transforms:** `b+tree`→`btree`, `hotspot3D`→`hotspot3d`, `lavaMD`→`lavamd`

### 2. Category Enum (MUST PASS)

Check `identity.category` against allowed values:
```
ml graph physics linear_algebra stencil reduction sort molecular_dynamics image crypto financial other
```

**Forbidden aliases that LLMs commonly produce:**
`simulation`, `image_processing`, `data_structures`, `compression`, `sorting`, `bioinformatics`, `scientific`, `data_mining`, `algorithms`

Apply mappings:
- image processing → `image`
- simulation/physics/fluid → `physics`
- sorting → `sort`
- data structures/compression/bioinformatics/data mining → `other`

### 3. Run Argument Verification (CRITICAL — MUST PASS)

**This check exists because of a real incident where Claude changed run args based on
incorrect source reading, causing 2 specs to silently fail for weeks.**

For each `input_configurations` entry:

```bash
# Step 1: Find the source file
SOURCE_DIR=$(jq -r '.source.source_dir' specs/<spec>.json)
SOURCE_FILE=$(jq -r '.source.source_files[0]' specs/<spec>.json)

# Step 2: Read the argc check
grep -n "argc" <source_path>/<source_file>

# Step 3: Count expected arguments
# argc == N means N-1 user arguments (argv[0] is program name)
# argc != N means exactly N-1 arguments required

# Step 4: Compare with spec's run.arguments array length
SPEC_ARGS=$(jq '.run.arguments | length' specs/<spec>.json)
```

**FAIL if:** spec argument count doesn't match source's argc expectation.

### 4. Oracle Configuration

Check `verification` block:

- `oracle_strength` must be one of: `strong`, `medium`, `weak` (or absent for untagged)
- If `strong`: must have `reference_files` with `file_hash` entries
- If `medium`: must have `numeric_comparison` with `tolerance` and `metric_name`
- If `weak`: should have `stdout_pattern` and/or `exit_code`
- `stdout_pattern` must be valid regex (test with Python `re.compile()`)

### 5. Manifest Cross-Reference

```bash
# Check spec's kernel_name matches manifest entry
grep <kernel_name> manifest.jsonl | jq '.kernel_name'

# Manifest is append-only — NEVER suggest modifying existing entries
# New specs: add a NEW line to manifest.jsonl
```

### 6. Source Directory Existence

```bash
# Verify source_dir resolves to an actual directory
# For Rodinia: rodinia/rodinia-src/<path>
# For HeCBench: HeCBench-master/<path>
# For XSBench/RSBench/mixbench: <suite>/<path>
ls -d <resolved_source_dir>
```

### 7. Executable Name

```bash
# Check outputs.executable matches what the Makefile actually produces
# Common gotcha: spec says "euler3d" but Makefile produces "euler3d.out"
grep -E "^[A-Z]*\s*[:=]" <source_dir>/Makefile | head -5
```

## Output Format

```
=== SPEC VALIDATION: <spec-name> ===

[PASS] Slugification — unique_id matches convention
[PASS] Category — "physics" is valid enum
[FAIL] Run args — spec has 2 args but source expects argc==4 (3 args)
       Source: needle.cpp:249 → if (argc == 4)
       Fix: Add missing 3rd argument
[PASS] Oracle — weak oracle with stdout_pattern
[PASS] Manifest — cross-reference matches
[PASS] Source dir — directory exists
[WARN] Executable — could not verify (no Makefile target found)

Result: 5 PASS, 1 FAIL, 1 WARN
```

## Integration

- Runs as pre-flight before `/eval-run` or `/overnight-eval`
- Complements `spec-auditor` agent (which does bulk validation)
- Complements `/spec-check` (which also runs harness verify)
- Feeds into `/gen-spec` as post-generation validation
