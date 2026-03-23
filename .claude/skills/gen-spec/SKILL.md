# Spec Generation Workflow

Structured workflow for generating ParBench specs for a new benchmark suite.

## Arguments
- `$ARGUMENTS` — suite name (e.g., "polybench", "npb")

## Workflow

### Phase 1: Validate Source
- Confirm suite source is cloned into `parbench_sam/<suite>/<suite>-src/`
- Survey available kernels and APIs (CUDA, OpenCL, OMP)
- Check for build systems, data files, reference outputs

### Phase 2: Write Generator
- Create `scripts/generators/generate_<suite>_specs.py`
- Follow existing pattern from `scripts/generators/generate_rodinia_specs.py`
- Ensure slugification rules are enforced (see `.claude/rules/spec-conventions.md`)
- Map kernel categories using allowed enum values only

### Phase 3: Generate
```bash
python3 scripts/generators/generate_<suite>_specs.py
```
- Review generated specs for correctness
- Spot-check 3-5 specs manually

### Phase 3.5: Set Translation Targets

Run the standardizer to set kernel-centric translation fields:
```bash
python3 scripts/generators/standardize_specs.py --suite <suite> \
    --project-root /home/samyak/Desktop/parbench_sam
```

Or manually set per-API family rules:
- **Family 1 — `opencl`**: `translation_targets` = only `.cl` files from `prompt_payload`
- **Family 2 — `omp`, `omp_target`, `openacc`**: `translation_targets` = curated pragma files, or `prompt_payload`
- **Family 3 — all others** (`cuda`, `hip`, `sycl`, etc.): `translation_targets` = `prompt_payload`

If a kernel does not have a variant in a particular API in the original repo,
do NOT create a spec for it. Document the gap. Never synthesize a missing implementation.

### Phase 4: Validate
```bash
python3 scripts/validate_schema.py --all
```
- All new specs must pass (HeCBench errors are pre-existing, ignore)
- Fix any validation errors before proceeding

### Phase 5: Manifest
- Append entries to `manifest.jsonl` (never modify existing entries)
- Cross-check: `manifest.kernel_name == spec.identity.kernel_name`

### Phase 6: Smoke Test
- Pick 1 spec per API (CUDA, OpenCL, OMP) if hardware is available
- Run: `python3 -m harness -v verify specs/<name>.json`
- Document results in CLAUDE.md smoke tests section
