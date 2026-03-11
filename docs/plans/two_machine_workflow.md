# ParBench Two-Machine Workflow

## Architecture

```
┌──────────────────────────────────┐         ┌──────────────────────────────────┐
│        MacBook Pro (M1)          │         │     Linux LC (Ryzen 9 + 4070)    │
│                                  │  git    │                                  │
│  • Schema design                 │ push/   │  • Build CUDA/OpenMP kernels     │
│  • Spec authoring                │ pull    │  • Run benchmarks                │
│  • Harness Python code           │◄───────►│  • Collect baselines             │
│  • Validation (structural)       │  SSH    │  • Test harness end-to-end       │
│  • Claude Code (VS Code)         │────────►│  • Download benchmark repos      │
│                                  │         │                                  │
│  Phases 1-4: HERE                │         │  Phase 5: HERE                   │
└──────────────────────────────────┘         └──────────────────────────────────┘
```

## Git Repo Structure

```
parbench/                          ← git root
├── schema/                        ← JSON schemas
├── specs/                         ← per-kernel spec files
├── manifest.jsonl                 ← registry
├── harness/                       ← Python harness code
├── scripts/                       ← validation, reporting
├── templates/                     ← blank spec template
├── reports/                       ← generated reports
├── config/                        ← machine-specific config (NEW)
│   ├── paths.json                 ← maps logical names to local paths
│   └── paths.example.json         ← template for new machines
├── .gitignore                     ← excludes downloads/, baselines, etc.
└── README.md
```

**NOT in git** (machine-local, too large):
```
downloads/                         ← benchmark repos (on Linux LC only)
├── HeCBench-master/
├── gpu-rodinia-master/
├── BabelStream-main/
└── ...
```

## Path Configuration

To make specs work on both machines, we use a `config/paths.json` that maps
logical names to actual local paths. This file is in `.gitignore` — each
machine has its own copy.

```json
{
  "project_root": "/home/samyak/parbench",
  "downloads_root": "/home/samyak/parbench/downloads",
  "hecbench_root": "/home/samyak/parbench/downloads/HeCBench-master"
}
```

Specs use RELATIVE paths from `downloads_root`:
- `repo_root`: "HeCBench-master/"  (not a full absolute path)
- The harness resolves: `config.downloads_root / spec.repo_root / spec.source_path`

This means:
- On Mac: specs can be authored and structurally validated (schema checks)
- On Linux LC: specs can be built, run, and verified (needs compilers + repos)
- Switching machines only requires updating `config/paths.json`

## Phase Assignment

| Phase | Machine | What |
|-------|---------|------|
| Phase 1: Scaffolding + Schema | Mac | Create project structure, JSON schemas, validation script |
| Phase 2: Inspect + Create Specs | Mac (authoring) + Linux LC (inspecting source) | SSH into Linux to read HeCBench files, write specs on Mac |
| Phase 3: Validation + Report | Mac | Structural validation (paths won't resolve without repos, but schema checks work) |
| Phase 4: Harness Skeleton | Mac | Write Python harness code |
| Phase 5: Testing + Baselines | Linux LC | Clone repo, download HeCBench, build/run/verify everything |
