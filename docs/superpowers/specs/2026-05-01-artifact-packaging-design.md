# Anonymous Executable Artifact for NeurIPS 2026

**Date:** 2026-05-01
**Status:** Draft
**Scope:** Package ParBench into an anonymous, self-contained, Zenodo-hosted artifact that lets reviewers reproduce all paper tables and figures with a single Docker command.

## Context

NeurIPS Datasets & Benchmarks track expects a stable, executable artifact link in the paper. Reviewers need to verify that published numbers are reproducible without requiring GPU hardware or LLM API keys. ParBench already has pre-computed evaluation results for 3 models (2,262 records) and an analysis pipeline that generates tables/figures from those results.

## Design

### Deliverable

`parbench-artifact-v1.tar.gz` (~110 MB), uploaded to Zenodo with a DOI. Paper includes the DOI as an anonymous footnote.

### Artifact Structure

```
parbench-artifact/
├── README.md                    # Quick-start, table/figure mapping, scope
├── LICENSE                      # Project license
├── Dockerfile                   # CPU-only, python:3.12-slim based
├── requirements-lock.txt        # Exact dependency pins
├── pyproject.toml               # Anonymized package metadata
├── reproduce.sh                 # Single entry point
├── manifest.jsonl               # Kernel registry (append-only source)
├── specs/                       # 207 kernel spec JSONs (2.2 MB)
├── schema/                      # JSON validation schemas
├── config/
│   └── paths.json.template      # Template (no machine-specific paths)
├── results/
│   ├── evaluation/              # Raw per-task result JSONs (97 MB)
│   │   ├── together-qwen-3.5-397b-a17b/
│   │   ├── azure-gpt-5.4/
│   │   └── azure-gpt-5.3-codex/
│   └── analysis/                # Pre-computed analysis summaries (1.9 MB)
├── scripts/
│   ├── generate_paper_figures.py
│   ├── validate_schema.py
│   └── analysis/                # Full analysis pipeline
├── harness/                     # Build-run-verify pipeline (inspection only)
├── c_augmentation/              # AST transforms (inspection only)
└── expected_outputs/            # Reference tables/figures for diff
    ├── tables/                  # LaTeX table files
    └── figures/                 # PDF/PNG figure files
```

### Reviewer Workflow

```bash
tar xf parbench-artifact-v1.tar.gz
cd parbench-artifact
docker build -t parbench .
docker run --rm -v $(pwd)/output:/app/output parbench ./reproduce.sh
diff -r output/ expected_outputs/   # bit-for-bit match
```

Total time: ~5 minutes (build) + ~2 minutes (reproduce).

### reproduce.sh

Runs the full analysis-to-tables pipeline inside the container:

1. Aggregate raw evaluation results → analysis summaries
2. Compute quantitative findings (pass rates, Wilson CIs, error taxonomy)
3. Run statistical analyses (McNemar, Cohen's h, Cochran-Armitage)
4. Generate all paper figures (F2–F7, appendix C.1–C.4)
5. Generate all paper tables (current T1–T2 + planned T3–T5)
6. Write outputs to `/app/output/`

### Anonymization

| Item | Action |
|------|--------|
| `.git/` | Excluded — no commit history |
| `.claude/`, `.planning/`, `.git/hooks/` | Excluded — dev artifacts |
| `pyproject.toml` author fields | Replaced with "Anonymous" |
| `config/paths.json` | Replaced with template (no real paths) |
| Script headers/comments | Grep for author names, emails, institution |
| Result JSON metadata | Check for machine hostnames, usernames |
| Evaluation logs (`.log`, `.marker`) | Excluded — may contain paths/timestamps |
| API key env vars | Not present in artifact |
| `docs/paper/` | Excluded — paper is separate from artifact |

### What's NOT Included (documented in README)

- LLM API keys (required for evaluation from scratch)
- NVIDIA GPU / CUDA toolkit (required for kernel compilation)
- Benchmark source trees (Rodinia, HeCBench — external repos, separate licenses)
- Docker image (reviewer builds from Dockerfile)
- Paper LaTeX source (submitted separately)

### Packaging Script

`scripts/build_artifact.sh`:
- Copies curated files into a staging directory
- Runs anonymization checks (grep for known author patterns)
- Generates `expected_outputs/` by running reproduce.sh locally
- Creates the tarball
- Reports artifact size and file count

### Dockerfile Changes (vs existing)

The existing Dockerfile is close to what's needed. Modifications:
- Add `COPY results/ results/` for bundled evaluation data
- Add `COPY expected_outputs/ expected_outputs/`
- Add `COPY reproduce.sh .` and `RUN chmod +x reproduce.sh`
- Change CMD to show usage instructions
- Remove references to c_augmentation editable install if not needed for tables

### Paper Integration

Add anonymous footnote in Section 1 (Introduction) or Section 5 (Reproducibility):
```latex
\footnote{Artifact: \url{https://doi.org/10.5281/zenodo.XXXXXXX}}
```

### Size Budget

| Component | Size |
|-----------|------|
| Raw evaluation results | ~97 MB |
| Specs + manifest | ~2.5 MB |
| Analysis summaries | ~1.9 MB |
| Scripts + harness + augmentation code | ~5 MB |
| Expected outputs | ~2 MB |
| Dockerfile + config + README | <1 MB |
| **Total (uncompressed)** | **~110 MB** |
| **Compressed (.tar.gz)** | **~40-60 MB** |

Well within Zenodo's 50 GB limit.

### Verification

1. Build Docker image from artifact Dockerfile → succeeds
2. Run `reproduce.sh` → generates all tables and figures
3. `diff -r output/ expected_outputs/` → no differences
4. Inspect `README.md` for completeness and clarity
5. Grep entire artifact for author names, emails, institution → zero hits
6. Verify Zenodo upload is accessible from a different machine
