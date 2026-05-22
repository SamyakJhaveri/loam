# Research Workflow Master Guide for Claude Code

> **Purpose:** This document is the authoritative reference for Claude Code (and any AI coding assistant) working on iterative HPC/systems research projects. It encodes lessons learned from the ParBench project (NeurIPS 2026) — a kernel-centric benchmark for LLM-based parallel code translation — where inconsistencies between evolving code, accumulating results, and paper claims caused significant rework. Every recommendation here exists to prevent a specific class of failure that was observed in production research work.

> **Audience:** Claude Code sessions operating on research projects that follow this pattern: design → build framework → run experiments → collect results → iterate on framework → re-run → write paper. The developer (Sam) works in HPC/parallel computing research, uses Claude Code as the primary coding assistant, and uses Graphify for codebase knowledge graphs.

> **When to read this:** At the start of every new research project, and again before any paper-writing phase begins.

---

## Table of Contents

1. [The Research Project Lifecycle and Where Things Break](#1-the-research-project-lifecycle-and-where-things-break)
2. [The Semantic Drift Problem](#2-the-semantic-drift-problem)
3. [Project Architecture: The Four-Concern Separation](#3-project-architecture-the-four-concern-separation)
4. [Pipeline Fingerprinting: Versioning What Matters](#4-pipeline-fingerprinting-versioning-what-matters)
5. [The Research Changelog: Tracking Scientific Evolution](#5-the-research-changelog-tracking-scientific-evolution)
6. [Claims Traceability: Linking Paper to Evidence](#6-claims-traceability-linking-paper-to-evidence)
7. [Graphify Strategy: Scoped Graphs, Not Global Graphs](#7-graphify-strategy-scoped-graphs-not-global-graphs)
8. [Claude Code Configuration: Lean Setup Philosophy](#8-claude-code-configuration-lean-setup-philosophy)
9. [Result Integrity and Immutability Protocol](#9-result-integrity-and-immutability-protocol)
10. [Paper-Writing Phase: The Consistency Protocol](#10-paper-writing-phase-the-consistency-protocol)
11. [Anti-Patterns: What Went Wrong in ParBench](#11-anti-patterns-what-went-wrong-in-parbench)
12. [Templates and File Specifications](#12-templates-and-file-specifications)
13. [Quick Reference: Decision Trees](#13-quick-reference-decision-trees)

---

## 1. The Research Project Lifecycle and Where Things Break

### The typical lifecycle

A research project in Sam's workflow follows this trajectory:

```
Phase 1: DESIGN
  - Define research question and hypotheses
  - Design evaluation framework (metrics, schemas, pipeline)
  - Write initial specs/schemas
  - Get feedback from research team

Phase 2: BUILD
  - Implement the evaluation framework in scripts/
  - Build harness (build → run → verify pipeline)
  - Write utility/analysis scripts
  - Create initial test cases

Phase 3: EXPERIMENT (iterative — this is where drift happens)
  - Run experiments using LLM API calls
  - Collect results into structured JSON files
  - Analyze results, realize framework needs changes
  - Get feedback from research team
  - Update code, metrics, schemas, validation logic
  - Re-run experiments under new framework version
  - Repeat 3-6 times over the course of the project

Phase 4: WRITE
  - Interpret final results
  - Create figures, tables, diagrams
  - Write paper sections referencing specific results
  - Cross-reference claims with evidence
  - Iterate on paper drafts with advisor feedback

Phase 5: SUBMIT
  - Final consistency check
  - Camera-ready preparation
```

### Where things break

The critical failure points are all at **phase boundaries** and during **phase 3 iterations**:

**Failure 1: Stale results referenced in paper.** The framework changed (e.g., verification logic upgraded from string matching to numerical comparison) but old result files were not invalidated or re-generated. Claude Code, reading from the knowledge graph or file system, cannot distinguish "result produced under current framework" from "result produced under obsolete framework." It writes paper text citing stale numbers.

**Failure 2: Schema evolution not tracked.** The JSON schema for results evolved (e.g., adding failure taxonomy categories), but no record exists of which results use which schema version. When writing paper tables, Claude Code encounters a mix of old-format and new-format result files with no way to filter.

**Failure 3: Knowledge graph reflects obsolete state.** The Graphify knowledge graph was built (or last updated) during an earlier iteration. Its nodes and edges describe relationships that no longer hold — e.g., a "verifier" node linked to "string comparison" when the verifier now does numerical comparison. Claude Code navigates these stale edges and produces paper text that describes the old system.

**Failure 4: Meeting notes and task lists contaminate the graph.** Ephemeral project management artifacts (meeting notes, TODOs, team feedback) were included in the knowledge graph. These create false inferred edges to code concepts. A February meeting note saying "we should consider string comparison" becomes a graph edge linking the verifier to string comparison — months after the code moved to numerical comparison.

**Failure 5: Claude Code context overload.** With 35 custom skills, 14 custom agents, 12 conditional rules, and multiple hooks, Claude Code loads thousands of tokens of instructions before reading a single line of actual code. When these instructions themselves become stale (referencing old architecture, old invariants), they actively mislead the model.

**Failure 6: No audit trail from paper claims to raw data.** When a reviewer asks "where does the 34.2% pass rate come from?", there is no machine-readable link from that number in the paper to the specific result files and analysis script that produced it. Claude Code cannot verify claims against evidence without manual guidance.

---

## 2. The Semantic Drift Problem

### What semantic drift is

Semantic drift occurs when the **meaning** of code, data, or terminology changes over the course of a project, even though the surface-level structure may look similar.

Examples from ParBench:

| What changed | Surface appearance | Semantic impact |
|---|---|---|
| Verification logic: string → numerical | `verifier.py` still exports `verify()` | Every prior "PASS" result is now scientifically invalid |
| Result schema: PASS/FAIL → failure taxonomy | Result JSONs still have `overall_status` field | Old results lack `BUILD_FAIL`/`RUN_FAIL` granularity needed for paper tables |
| Augmentation levels added | New `augmentation_level` field in results | Results without this field cannot be used in augmentation analysis |
| Spec `run_args` corrected | Spec JSON structure unchanged | Prior runs used wrong arguments — results are invalid for those specs |

### Why knowledge graphs cannot track semantic drift

Graphify (and similar tools) operate on **structural** relationships — function calls, imports, file references, concept co-occurrence. They answer "what connects X to Y?" not "is X still valid?" or "did the meaning of X change last Tuesday?"

When the verification logic changed from string comparison to numerical comparison:
- Graphify's AST extraction sees the same function names, same module structure
- The graph nodes for `verifier.py`, `verify()`, `VerificationResult` persist with minor edge changes
- Nothing in the graph indicates that every result produced before this change is scientifically worthless
- The `GRAPH_REPORT.md` still describes the verifier's connections to the rest of the pipeline — accurately in structural terms, misleadingly in scientific terms

### What does track semantic drift

Three mechanisms, used together:

1. **Pipeline fingerprinting** — a content hash of the critical pipeline files, embedded in every result. When the pipeline changes, the hash changes, and you can instantly partition results by which framework version produced them. (See Section 4.)

2. **Research changelog** — a human-written, append-only log of what changed scientifically, what it invalidated, and what the current state is. This is the file Claude Code should read before writing any paper section. (See Section 5.)

3. **Claims traceability** — an explicit, machine-readable mapping from every paper claim to the exact data and code that supports it. (See Section 6.)

---

## 3. Project Architecture: The Four-Concern Separation

### The principle

Every file in the project belongs to exactly one of four concerns. These concerns have different change rates, different staleness risks, and different relationships to the paper. Mixing them — especially in knowledge graphs — is the root cause of most consistency failures.

### The four concerns

#### Concern 1: Engineering (the tool)

**What:** The evaluation framework itself — the code that builds, runs, verifies, and evaluates.

**Files:** `harness/`, `scripts/`, `c_augmentation/`, `schema/`, `config/`, `tests/`

**Change rate:** Moderate. Changes during Phase 2 (build) and Phase 3 iterations when framework evolves.

**Staleness risk:** Medium. Code changes are tracked by git, but the *implications* of code changes on result validity are not tracked by git.

**Relationship to paper:** Described in the paper's methodology section. The paper should describe the *final* version of the framework, not intermediate versions.

**Graphify strategy:** Graph this concern separately. Rebuild only on major structural refactors (not every bug fix or parameter tweak).

#### Concern 2: Research artifacts (the science)

**What:** The specs that define experiments, the results that experiments produce, the analysis scripts that compute paper statistics, and the paper itself.

**Files:** `specs/`, `results/`, `analysis/`, `docs/paper/`, `expected_outputs/`

**Change rate:** High during Phase 3, then stabilizes. Results accumulate; specs may be added or corrected; analysis scripts evolve with the paper.

**Staleness risk:** CRITICAL. This is where semantic drift does the most damage. A result file from two framework iterations ago looks identical to a current result file — same JSON structure, same field names — but its scientific meaning may be completely different.

**Relationship to paper:** Direct. Every number, table, and figure in the paper is derived from these files.

**Graphify strategy:** Do NOT rely on Graphify for this concern. Use pipeline fingerprinting + claims traceability instead. If you do graph it, rebuild after every eval batch, and scope it to `specs/` + `results/` + `analysis/` + `docs/paper/` only.

#### Concern 3: Project management (the process)

**What:** Meeting notes, team feedback, task lists, planning documents, presentation slides, brainstorming docs.

**Files:** `meeting_notes/`, `presentations/`, `planning/`, `*.md` files that are task-oriented rather than research-oriented (e.g., `HANDOFF.md`, `TODO.md`)

**Change rate:** High and continuous.

**Staleness risk:** Inherently high, but the risk is to the *graph*, not to the paper. A two-month-old meeting note is fine as a flat file. It becomes dangerous when Graphify ingests it and creates inferred edges to code concepts, giving the note's content false permanence and false authority.

**Relationship to paper:** None (or indirect). These files inform human decision-making but should never be cited in or used to generate paper content.

**Graphify strategy:** NEVER include in any knowledge graph. Keep as flat files. Reference manually when needed.

#### Concern 4: External dependencies (the sources)

**What:** Benchmark source code (git submodules), external datasets, third-party libraries.

**Files:** `rodinia/`, `xsbench/`, `rsbench/`, `mixbench/`, `HeCBench-master/`

**Change rate:** Near-zero. Pinned to specific commits.

**Staleness risk:** Low, but submodule state can be confusing (empty in worktrees, specific commit in main checkout).

**Relationship to paper:** Referenced in the paper's benchmark description. Pinned versions are cited.

**Graphify strategy:** Do not graph. These are too large and their internal structure is irrelevant to your research. Reference them by pinned commit hash in the paper.

### Directory layout recommendation for new projects

```
project-root/
├── CLAUDE.md                        # Lean (1 page max). Points to this guide.
├── CHANGELOG.research.md            # Science changelog (see Section 5)
├── claims.jsonl                     # Paper-to-evidence links (see Section 6)
├── README.md                        # Standard project readme
│
├── harness/                         # Concern 1: Engineering
│   ├── __init__.py
│   ├── builder.py
│   ├── runner.py
│   ├── verifier.py
│   ├── pipeline_version.py          # Pipeline fingerprinting module
│   └── ...
│
├── scripts/                         # Concern 1: Engineering
│   ├── evaluation/                  # LLM eval batch runners
│   ├── analysis/                    # Figure/table generation
│   ├── augmentation/                # Code transform runners
│   └── spec_tools/                  # Spec validation, generation
│
├── specs/                           # Concern 2: Research artifacts
│   └── {suite}-{kernel}-{api}.json
│
├── results/                         # Concern 2: Research artifacts
│   └── evaluation/
│       └── {model}/
│           └── {result}.json        # Each has pipeline_version field
│
├── analysis/                        # Concern 2: Research artifacts
│   ├── data/                        # Generated CSV/Excel data
│   ├── figures/                     # Generated figures
│   └── reports/                     # Generated reports
│
├── docs/                            # Concern 2: Research artifacts
│   └── paper/                       # LaTeX source
│
├── meeting_notes/                   # Concern 3: Project management (NEVER graphed)
├── presentations/                   # Concern 3: Project management (NEVER graphed)
├── planning/                        # Concern 3: Project management (NEVER graphed)
│
├── external/                        # Concern 4: External dependencies
│   ├── rodinia-src/                 # Git submodule, pinned commit
│   └── ...
│
├── config/                          # Machine-specific config (gitignored)
├── tests/                           # Unit and integration tests
│
├── graphify-out-engineering/        # Scoped Graphify graph: Concern 1 only
│   ├── graph.json
│   ├── GRAPH_REPORT.md
│   └── graph.html
│
├── .graphifyignore-engineering      # Ignore file for engineering graph
├── .graphifyignore                  # Default: project-management exclusions
│
└── .claude/
    ├── settings.json                # Lean: minimal hooks, minimal permissions
    └── rules/
        ├── architecture.md          # Framework architecture (Concern 1 context)
        ├── known-issues.md          # Current known issues
        └── research-state.md        # Points to CHANGELOG.research.md and claims.jsonl
```

---

## 4. Pipeline Fingerprinting: Versioning What Matters

### The problem it solves

Git tracks every change to every file, but it does not answer: "which version of the verification logic produced this result?" When you change the verifier and re-run 500 experiments, you need to know which of the 1,000 result files in `results/` were produced under the old logic and which under the new logic. Git blame on each result file would technically work but is impractical and error-prone.

### How it works

A **pipeline fingerprint** is a SHA-256 hash (truncated to 12 hex characters) computed from the content of the files that affect result validity. It is computed automatically by the evaluation runner and embedded in every result JSON.

### Which files to include in the fingerprint

Include ONLY the files whose changes invalidate prior results. This is a judgment call that depends on the project, but the principle is: **if this file changes, should I re-run experiments?**

**Include:**
- Verification logic (`harness/verifier.py`)
- Build logic (`harness/builder.py`)
- Run logic (`harness/runner.py`)
- Result schema (`schema/result_schema.json` or equivalent)
- Any shared constants that affect evaluation (`harness/constants.py`)

**Do NOT include:**
- Analysis scripts (they process results, they don't produce them)
- Paper source files
- Spec files (they change independently of the pipeline — spec changes are tracked by spec version, not pipeline version)
- CLI wrappers, logging, formatting code

### Implementation

```python
# harness/pipeline_version.py

import hashlib
import pathlib
from typing import Optional

# Files that affect result validity — update this list when adding
# new pipeline components that change how results are produced
CRITICAL_PIPELINE_FILES = [
    "harness/verifier.py",
    "harness/builder.py",
    "harness/runner.py",
    "harness/constants.py",
    "schema/result_schema.json",
]

def compute_pipeline_fingerprint(
    project_root: str | pathlib.Path,
    additional_files: Optional[list[str]] = None,
) -> str:
    """Compute a content hash of the files that affect result validity.

    Returns a 12-character hex string. Two runs of this function on
    the same file contents will always produce the same hash. Any
    change to any critical file changes the hash.

    Args:
        project_root: Path to the project root directory.
        additional_files: Optional extra files to include in the hash
            (relative to project_root). Use this for project-specific
            files not in the default CRITICAL_PIPELINE_FILES list.

    Returns:
        12-character hex string (e.g., "a3f8b2c1e9d4").
    """
    root = pathlib.Path(project_root)
    files = list(CRITICAL_PIPELINE_FILES)
    if additional_files:
        files.extend(additional_files)

    h = hashlib.sha256()
    for f in sorted(set(files)):  # sorted + deduplicated for determinism
        path = root / f
        if path.exists():
            h.update(path.read_bytes())
        else:
            # Missing file is a meaningful state — hash its absence
            h.update(f"MISSING:{f}".encode())

    return h.hexdigest()[:12]


def get_pipeline_version_record(project_root: str | pathlib.Path) -> dict:
    """Return a dict suitable for embedding in result JSONs.

    Example output:
    {
        "pipeline_version": "a3f8b2c1e9d4",
        "pipeline_files": ["harness/builder.py", "harness/constants.py", ...],
        "computed_at": "2026-05-21T14:30:00Z"
    }
    """
    from datetime import datetime, timezone

    root = pathlib.Path(project_root)
    fingerprint = compute_pipeline_fingerprint(root)

    return {
        "pipeline_version": fingerprint,
        "pipeline_files": sorted(CRITICAL_PIPELINE_FILES),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
```

### Usage in the evaluation runner

```python
# In your eval batch script (e.g., scripts/evaluation/run_eval_batch.py):

from harness.pipeline_version import get_pipeline_version_record

def run_single_evaluation(spec, model, direction, project_root, ...):
    # ... run the evaluation ...

    result = {
        "overall_status": status,
        "model": model,
        "direction": direction,
        "source_spec": source_spec_id,
        "target_spec": target_spec_id,
        # ... other fields ...

        # CRITICAL: embed pipeline version in every result
        **get_pipeline_version_record(project_root),
    }

    save_result(result, output_path)
```

### Querying results by pipeline version

```python
# In analysis scripts:

import json
import pathlib

def load_results_for_version(results_dir, required_version):
    """Load only results produced by a specific pipeline version."""
    results = []
    for path in pathlib.Path(results_dir).rglob("*.json"):
        with open(path) as f:
            data = json.load(f)
        if data.get("pipeline_version") == required_version:
            results.append(data)
    return results

def detect_mixed_versions(results_dir):
    """Report all pipeline versions present in results."""
    versions = {}
    for path in pathlib.Path(results_dir).rglob("*.json"):
        with open(path) as f:
            data = json.load(f)
        v = data.get("pipeline_version", "UNKNOWN")
        versions.setdefault(v, []).append(str(path))
    return versions
```

### Claude Code instruction

When writing paper sections or generating analysis:

1. **Always check the current pipeline version** by running `compute_pipeline_fingerprint()` or checking a recent result file.
2. **Only reference results that match the current pipeline version.** If mixed versions are detected, alert the user — do not silently use stale results.
3. **When the user changes pipeline-critical files**, proactively note that the pipeline fingerprint has changed and existing results may need re-running.

---

## 5. The Research Changelog: Tracking Scientific Evolution

### The problem it solves

Git log tracks *code* changes. The research changelog tracks *scientific* changes — what changed in the research methodology, what that invalidated, and what the current state of the world is. This is the single most important file for paper-writing consistency.

### Format specification

The file is called `CHANGELOG.research.md` and lives in the project root. It is append-only (new entries go at the top). Each entry has a fixed structure:

```markdown
## YYYY-MM-DD — Pipeline vN (fingerprint)

- **Changed:** What changed, in concrete terms. Name the files, the functions, the logic.
- **Why:** What motivated the change (e.g., team feedback, realized validation was wrong).
- **Impact:** What prior work is invalidated or needs updating.
  - Which results are affected (all? specific suites? specific models?)
  - Which paper sections reference affected results
  - Which figures/tables need regeneration
- **Status:** Current state after the change.
  - Have experiments been re-run? Partially or fully?
  - Are paper sections updated?
  - Any known gaps remaining?
- **Pipeline version:** `{fingerprint}` (from pipeline_version.py)
```

### Example (based on ParBench history)

```markdown
# Research Changelog

> This file tracks scientific changes — not code changes. Read this before
> writing any paper section. The most recent entry describes the current
> state of the research.

## 2026-04-15 — Pipeline v3 (a3f8b2c1e9d4)

- **Changed:** Verification logic in `harness/verifier.py` now compares
  numerical outputs with float tolerance (1e-6) instead of comparing
  stdout strings directly. Function `verify_numerical()` replaces
  `verify_string_match()`.
- **Why:** String comparison was accepting cases where the target code
  produced the right output format but wrong numerical values (e.g.,
  rounding differences masked real bugs in LLM-generated code).
- **Impact:** ALL results from pipeline v1 and v2 are scientifically
  invalid — they may report PASS for translations that produce wrong
  numerical results.
  - Affected: every spec, every model, every direction
  - Paper sections 4.x (results), 5.x (analysis) need full rewrite
  - All tables (T1-T5) and figures (F2-F7) need regeneration
- **Status:** Full re-run complete. 2,262 valid results under pipeline v3.
  Paper sections updated as of 2026-04-20.
- **Pipeline version:** `a3f8b2c1e9d4`

## 2026-03-28 — Pipeline v2 (7bc1d4e5f890)

- **Changed:** Result schema expanded. `overall_status` now uses failure
  taxonomy: BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL (was:
  binary PASS/FAIL). Schema file: `schema/result_schema.json`.
- **Why:** Binary PASS/FAIL provided insufficient granularity for
  analyzing where LLM translations fail in the pipeline.
- **Impact:** Results from pipeline v1 lack failure taxonomy fields.
  They are not invalid (PASS/FAIL is still correct) but cannot be used
  for failure analysis tables.
  - Affected: all results from pipeline v1
  - Paper Table T3 (failure taxonomy) requires v2+ results only
  - Paper Figures F5-F6 (failure breakdown) require v2+ results only
- **Status:** Re-run complete for Rodinia suite. HeCBench re-run complete
  2026-04-02. All results now have failure taxonomy.
- **Pipeline version:** `7bc1d4e5f890`

## 2026-02-15 — Pipeline v1 (initial) (0000deadbeef)

- **Changed:** Initial pipeline. String-based stdout comparison.
  Binary PASS/FAIL results.
- **Why:** First working version of the evaluation framework.
- **Impact:** Baseline. No prior results to invalidate.
- **Status:** Initial experiments complete. 87 specs validated manually.
- **Pipeline version:** `0000deadbeef`
```

### Claude Code instruction

1. **Read `CHANGELOG.research.md` at the start of every session** that involves results, analysis, or paper writing.
2. **The most recent entry is the current ground truth.** If it says "results from pipeline v1 are invalid," treat them as invalid regardless of what the knowledge graph or file system shows.
3. **When the user makes a framework change that affects result validity**, prompt them to add a new entry to the research changelog. Draft the entry for their review.
4. **When writing paper text**, cross-reference every statistical claim against the pipeline version noted in the changelog. If the claim references results from an older pipeline version, flag it.

---

## 6. Claims Traceability: Linking Paper to Evidence

### The problem it solves

A research paper makes dozens of specific claims: pass rates, performance numbers, comparisons, statistical tests. Each claim is derived from specific result files processed by specific analysis scripts. Without an explicit mapping, Claude Code (or any assistant) must *infer* where numbers come from — and inference is where hallucination happens.

### Format specification

The file is called `claims.jsonl` and lives in the project root. Each line is a JSON object mapping one paper claim to its evidence chain:

```json
{
  "claim_id": "C001",
  "claim_text": "Qwen achieves a 34.2% overall pass rate on CUDA-to-OpenMP translation",
  "paper_section": "4.2",
  "paper_element": "Table T2, row 1",
  "value": 34.2,
  "unit": "percent",
  "pipeline_version": "a3f8b2c1e9d4",
  "source_data": "results/evaluation/together-qwen-3.5-397b-a17b/**/cuda-to-omp/*.json",
  "computed_by": "scripts/analysis/compute_pass_rates.py",
  "computation_method": "count(overall_status == 'PASS') / count(all, excluding KNOWN_FAIL) * 100",
  "denominator_note": "Excludes 9 KNOWN_FAIL specs from denominator",
  "last_verified": "2026-04-20",
  "status": "current"
}
```

### Required fields

| Field | Type | Description |
|---|---|---|
| `claim_id` | string | Unique identifier (C001, C002, ...) |
| `claim_text` | string | The claim as it appears (or will appear) in the paper |
| `paper_section` | string | Section number in the paper |
| `paper_element` | string | Table, figure, or paragraph reference |
| `value` | number or string | The specific value claimed |
| `unit` | string | Unit of measurement (percent, seconds, count, etc.) |
| `pipeline_version` | string | Pipeline fingerprint of the results used |
| `source_data` | string | Glob pattern or path(s) to the raw data files |
| `computed_by` | string | Path to the analysis script that computes this value |
| `computation_method` | string | Human-readable description of the computation |
| `last_verified` | string | ISO date when this claim was last verified against raw data |
| `status` | string | `current`, `stale` (pipeline changed), or `disputed` (under review) |

### Lifecycle

1. **During analysis:** When an analysis script produces a number that will appear in the paper, add a claims.jsonl entry. The analysis script itself can do this automatically.
2. **During paper writing:** Claude Code reads claims.jsonl before writing any section. Every number in the paper must have a corresponding claim entry.
3. **After framework changes:** Run a script that checks all claims against the current pipeline version. Any claim whose `pipeline_version` doesn't match the current fingerprint gets its status set to `stale`.
4. **Before submission:** Run a full verification pass — re-compute every claim from raw data and check that the computed value matches `value`.

### Staleness detection script

```python
# scripts/verify_claims.py

import json
import pathlib
from harness.pipeline_version import compute_pipeline_fingerprint

def verify_claims(project_root):
    root = pathlib.Path(project_root)
    current_version = compute_pipeline_fingerprint(root)

    claims_file = root / "claims.jsonl"
    if not claims_file.exists():
        print("ERROR: claims.jsonl not found")
        return

    stale = []
    current = []
    for line in claims_file.read_text().strip().split("\n"):
        if not line.strip():
            continue
        claim = json.loads(line)
        if claim.get("pipeline_version") != current_version:
            stale.append(claim)
        else:
            current.append(claim)

    print(f"Current pipeline version: {current_version}")
    print(f"Claims up-to-date: {len(current)}")
    print(f"Claims STALE: {len(stale)}")

    if stale:
        print("\nStale claims (pipeline version mismatch):")
        for c in stale:
            print(f"  {c['claim_id']}: {c['claim_text'][:80]}...")
            print(f"    Was: {c.get('pipeline_version', 'UNKNOWN')} | Current: {current_version}")
            print(f"    Section: {c['paper_section']}, Element: {c['paper_element']}")
```

### Claude Code instruction

1. **Before writing any paper section**, read `claims.jsonl` and filter for claims in that section.
2. **Never invent a number.** If a statistic is needed and there is no corresponding claim entry, tell the user: "I need to compute this value. Let me run the analysis script and add a claim entry."
3. **If a claim's status is `stale`**, do not use it. Tell the user: "Claim C{id} references pipeline version {old} but the current version is {new}. This claim needs re-verification."
4. **When adding a new claim**, compute the value from raw data first, then create the claims.jsonl entry. Never create a claim entry with an estimated or remembered value.

---

## 7. Graphify Strategy: Scoped Graphs, Not Global Graphs

### What Graphify is (and is not)

**Graphify IS:**
- A structural discovery tool: "what connects module X to module Y?"
- A codebase orientation tool: "what are the god nodes in this project?"
- An AST-level relationship mapper for code files (local, no API calls)
- A semantic extractor for docs/PDFs/images (uses LLM API calls)

**Graphify is NOT:**
- A consistency tracker (it cannot detect semantic drift)
- A source of truth for specific values (it maps relationships, not data)
- A replacement for explicit traceability (claims.jsonl)
- Useful for rapidly-changing content (meeting notes, task lists, evolving results)

### The ParBench lesson

In ParBench, a single global Graphify graph was built over the entire project (199 files, 1.2M words). The resulting graph had:
- 2,890 nodes and 4,696 edges
- 364 communities (heavily fragmented for a project this size)
- 23% inferred edges at 0.65 average confidence (1,101 guessed edges)
- Meeting notes, PDFs, and task lists mixed in with code relationships

This graph was too large, too noisy, and too stale to be useful for paper writing. Claude Code navigated inferred edges to stale meeting-note content and produced paper text that described obsolete system states.

### Recommended Graphify configuration for new projects

#### Graph 1: Engineering graph (Concern 1 only)

**Scope:** `harness/`, `scripts/`, `c_augmentation/`, `schema/`, `tests/`, `config/`

**Purpose:** Understand how the pipeline works. Navigate code dependencies. Orient new sessions.

**When to build:** Once, when the framework architecture stabilizes (end of Phase 2).

**When to rebuild:** Only on major structural refactors — adding a new pipeline stage, splitting a module, changing the harness architecture. NOT on every bug fix, parameter change, or verification logic tweak.

**`.graphifyignore` for engineering graph:**
```
# .graphifyignore-engineering
# Exclude everything except Concern 1 (engineering) files

results/
analysis/
docs/
meeting_notes/
presentations/
planning/
specs/
external/
*.pdf
*.png
*.jpg
*.zip
manifest.jsonl
CHANGELOG.research.md
claims.jsonl
RESULTS.md
HANDOFF.md

# Exclude graphify's own output
graphify-out*/
```

**Build command:**
```bash
graphify extract harness/ scripts/ schema/ tests/ config/ \
  --out graphify-out-engineering/ \
  --no-viz  # skip HTML for faster builds; generate when needed
```

#### Graph 2: Research graph (optional, Concern 2 subset)

**Scope:** `specs/`, `docs/paper/`, and key design documents only. NOT results (too numerous, too frequently changing) and NOT meeting notes.

**Purpose:** Understand the relationship between specs, paper sections, and design decisions. Useful during paper-writing phase only.

**When to build:** At the start of Phase 4 (paper writing), after the final round of experiments.

**When to rebuild:** Only if you add new specs or restructure the paper. NOT after every eval batch.

**`.graphifyignore` for research graph:**
```
# .graphifyignore-research
# Include only specs and paper-related docs

harness/
scripts/
c_augmentation/
tests/
config/
results/
meeting_notes/
presentations/
planning/
external/
*.py
*.json  # except specs — use !specs/ below
*.zip
*.png

# Include specs
!specs/
!specs/**

# Include paper
!docs/paper/
!docs/paper/**
```

**Build command:**
```bash
graphify extract specs/ docs/paper/ \
  --out graphify-out-research/
```

#### What NOT to graph (ever)

- `meeting_notes/` — ephemeral, creates false inferred edges
- `presentations/` — derivative content, duplicates paper concepts with different framing
- `planning/` — task lists and TODOs become stale nodes
- `results/evaluation/` — too numerous (thousands of JSON files), changes with every eval batch, better served by pipeline fingerprinting + claims.jsonl
- Random PDFs, screenshots, ZIP files in the project root

### Configuring Claude Code to use the right graph

In `.claude/settings.json`, configure the Glob/Grep hook to point at the appropriate graph:

```json
{
  "matcher": "Glob|Grep",
  "hooks": [
    {
      "type": "command",
      "command": "PAYLOAD=$(cat); FILE=$(echo \"$PAYLOAD\" | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('pattern',''))\" 2>/dev/null); if echo \"$FILE\" | grep -qE 'harness/|scripts/|c_augmentation/'; then [ -f graphify-out-engineering/graph.json ] && echo '{\"hookSpecificOutput\":{\"additionalContext\":\"Use engineering graph: graphify-out-engineering/GRAPH_REPORT.md\"}}'; elif echo \"$FILE\" | grep -qE 'docs/paper|specs/|results/'; then echo '{\"hookSpecificOutput\":{\"additionalContext\":\"For paper/results questions, read CHANGELOG.research.md and claims.jsonl first. Engineering graph at graphify-out-engineering/ for code structure only.\"}}'; fi"
    }
  ]
}
```

### Graphify MCP server: when to use it

The MCP server (`python -m graphify.serve graph.json`) is useful for interactive graph queries during a Claude Code session. Configure it for the engineering graph only:

```json
// .mcp.json
{
  "mcpServers": {
    "graphify-engineering": {
      "command": "python3",
      "args": ["-m", "graphify.serve", "graphify-out-engineering/graph.json"]
    }
  }
}
```

Do NOT run an MCP server for the research graph. Research questions should be answered by reading `CHANGELOG.research.md` and `claims.jsonl` directly, not by traversing a graph.

---

## 8. Claude Code Configuration: Lean Setup Philosophy

### The problem with heavy configuration

In ParBench, the `.claude/` directory contained:
- 35 custom skills
- 14 custom agents
- 12 conditional rule files
- 6+ hooks (pre-tool-use, post-tool-use, stop)
- Multiple plugins

Each of these consumes context tokens. A skill SKILL.md file might be 500-2000 tokens. A conditional rule file might be 300-1000 tokens. When Claude Code loads a session, it reads `CLAUDE.md` (which references all skills and agents), then loads conditional rules based on file paths, then fires hooks on every tool use. Before Claude Code reads a single line of your actual code, it may have consumed 10,000-20,000 tokens of instruction.

This creates two problems:
1. **Context budget pressure:** Less room for actual code, results, and paper content in the context window.
2. **Instruction staleness:** As the project evolves, skill and rule content becomes outdated. A skill that says "the verifier uses string comparison" actively misleads Claude Code after the verifier changes.

### Lean setup for new projects

**Start with these files only:**

```
.claude/
├── settings.json          # Permissions + 2-3 essential hooks
└── rules/
    ├── architecture.md    # Current framework architecture (update when it changes)
    └── known-issues.md    # Current known issues and gotchas
```

**CLAUDE.md should be ONE PAGE.** It should contain:
- Project name and one-sentence description
- Environment setup (venv activation, python3 not python, platform paths)
- Architecture table (path → purpose, 5-8 rows max)
- Pointer to `CHANGELOG.research.md` for scientific state
- Pointer to `claims.jsonl` for paper claims
- 3-5 non-negotiable invariants (e.g., "results are immutable," "manifest is append-only")
- That's it. No skill tables, no agent tables, no GSD workflow enforcement, no developer profile.

**Add complexity only when you have evidence of a specific, recurring failure.** The bar for adding a new skill or agent should be: "This exact mistake has happened 3+ times and cost me 30+ minutes each time." Not: "This might be useful someday."

### Essential hooks (keep these)

1. **Result immutability guard** — prevents Claude Code from modifying files in `results/`. This is a non-negotiable safety invariant.

2. **Post-edit auto-formatter** — runs ruff (or equivalent) after Python file edits. Low cost, high value.

3. **Pipeline version check on eval runs** — a hook that fires when `scripts/evaluation/` files are invoked, reminding Claude Code to verify the pipeline fingerprint.

### Hooks to remove (from ParBench)

- The Glob/Grep graphify nudge (fires on every search, adds context pressure)
- Context budget tracking (adds overhead without clear benefit)
- Dream/memory consolidation on Stop (interesting but adds complexity)
- Codex cross-model review reminders (valid for ParBench's timeline pressure, not generalizable)
- Sentinel cleanup (artifact of the 4-wave validation protocol, which is itself too complex for most projects)

### Conditional rules: keep only what changes behavior

A conditional rule is worth having if it changes Claude Code's behavior in a way that prevents a specific class of error. "Always use python3 not python" is worth encoding. "Here is the complete history of evaluation fixes" is not — it's reference material that should live in a doc, not a rule.

**Keep:**
- `architecture.md` — but keep it under 50 lines. Module → purpose → key functions.
- `known-issues.md` — but only active issues, not historical ones.

**Remove for new projects:**
- `workflow.md` (GSD workflow enforcement — adds process overhead)
- `tech-stack.md` (if it's just listing versions, a requirements.txt suffices)
- `validation-loop.md` (the 4-wave validation protocol is overkill for most projects)
- `evaluation.md`, `augmentation.md`, `spec-conventions.md` (these are documentation, not behavioral rules — move to a `docs/` folder and reference when needed)
- `known-issues-archive.md` (historical — does not affect current behavior)
- `active-gotchas.md` (fold active gotchas into `known-issues.md`; archive the rest)
- `frontend-design.md`, `github-pages.md` (only relevant if building visualizations)

---

## 9. Result Integrity and Immutability Protocol

### Core principle

Result files are scientific data. Once produced, they are NEVER modified. If the pipeline changes and results need re-running, new result files are produced alongside the old ones (or old ones are archived). This is a non-negotiable invariant.

### Implementation

1. **Result files include pipeline version** (see Section 4). This is how you distinguish current from stale results.

2. **Directory structure encodes provenance:**
   ```
   results/evaluation/
   ├── {model}/
   │   └── {spec_id}__sample{N}__L{augmentation_level}.json
   ```

3. **Archival on pipeline change:** When the pipeline version changes and you re-run experiments, move old results to an archive:
   ```bash
   # Before re-running:
   mv results/evaluation/ results/archive/evaluation-pipeline-v2-7bc1d4e5/
   mkdir -p results/evaluation/
   ```
   This makes it physically impossible to accidentally reference stale results.

4. **Hook protection:** The `.claude/settings.json` pre-tool-use hook should block any Edit or Write operation targeting `results/`:
   ```json
   {
     "matcher": "Edit|Write",
     "hooks": [
       {
        "type": "command",
        "command": "PAYLOAD=$(cat); FILE=$(echo \"$PAYLOAD\" | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))\" 2>/dev/null); if echo \"$FILE\" | grep -q 'results/'; then echo 'BLOCKED: Result files are immutable. To re-run experiments, archive old results first.' >&2 && exit 2; fi",
        "timeout": 10
       }
     ]
   }
   ```

5. **`--resume` flag:** All evaluation scripts must support `--resume`, which skips specs that already have result files. This is the standard way to restart interrupted eval batches without re-running completed work.

---

## 10. Paper-Writing Phase: The Consistency Protocol

### Before writing any paper section

Claude Code must follow this checklist:

1. **Read `CHANGELOG.research.md`** — understand the current pipeline version and what has changed.
2. **Read `claims.jsonl`** — understand which claims exist and their verification status.
3. **Check for stale claims** — run `python3 scripts/verify_claims.py` (or equivalent) to ensure all claims match the current pipeline version.
4. **Read the engineering graph report** (`graphify-out-engineering/GRAPH_REPORT.md`) only if writing about the framework/methodology — NOT when writing about results.

### When writing a results section

1. **Every number must have a claim entry.** If you compute a new statistic, add it to `claims.jsonl` first.
2. **Compute, don't remember.** Always run the analysis script to get the number. Never use a number from memory, from the graph, or from a previous session.
3. **Cite the evidence chain.** In a comment in the LaTeX source, note the claim ID:
   ```latex
   Qwen achieves an overall pass rate of 34.2\% % claim:C001
   on CUDA-to-OpenMP translation tasks.
   ```
4. **Flag inconsistencies immediately.** If a newly computed number doesn't match an existing claim, stop and investigate. Do not silently update the number.

### When updating figures and tables

1. **Regenerate from raw data** — never edit a figure/table file directly.
2. **The generation script should read `claims.jsonl`** to verify that its outputs match the claimed values.
3. **After regeneration, update the `last_verified` date** in the corresponding claims.jsonl entries.

### When receiving reviewer feedback

1. **Add a research changelog entry** if the feedback requires methodology changes.
2. **If feedback requests re-running experiments**, the process is: update code → update pipeline fingerprint → archive old results → re-run → update claims.jsonl → regenerate figures → update paper text.
3. **Never patch results** — even if a reviewer points out a single wrong number, trace it back to the raw data and understand why it's wrong before fixing it.

---

## 11. Anti-Patterns: What Went Wrong in ParBench

This section documents specific anti-patterns observed in the ParBench project. Each is a concrete lesson for future projects.

### Anti-pattern 1: Global knowledge graph over the entire project

**What happened:** Graphify was run on all 199 files (1.2M words), producing a 2,890-node graph with 364 communities and 23% inferred edges.

**Why it was harmful:** The graph mixed engineering context (how the harness works), research context (what results mean), and project management context (meeting notes, task lists). Claude Code couldn't distinguish between authoritative code relationships and speculative inferred edges from meeting notes.

**Fix:** Scope graphs to single concerns. Graph engineering code separately. Don't graph meeting notes or results.

### Anti-pattern 2: No pipeline versioning on results

**What happened:** When the verification logic changed (string → numerical comparison), old result files remained in `results/` alongside new ones. Nothing in the file format distinguished them.

**Why it was harmful:** Analysis scripts and paper-writing sessions pulled numbers from a mix of old and new results. Some paper tables reported pass rates computed partially from invalid (string-comparison-era) results.

**Fix:** Pipeline fingerprinting in every result file + archival of stale results.

### Anti-pattern 3: Over-engineered Claude Code setup

**What happened:** 35 skills, 14 agents, 12 conditional rules, 6+ hooks accumulated over the project's lifetime.

**Why it was harmful:** Enormous instruction overhead consumed context tokens. Many skills and rules became stale as the project evolved but were never updated or removed. Stale instructions actively misled Claude Code.

**Fix:** Start lean (CLAUDE.md + 2 rule files + 2-3 hooks). Add complexity only with evidence of recurring failure.

### Anti-pattern 4: Meeting notes in the knowledge graph

**What happened:** PDFs and markdown files from `meeting_notes/` and `presentations/` were included in the Graphify extraction. These contained team discussions about design options, including options that were later rejected.

**Why it was harmful:** Graphify created inferred edges from meeting-note concepts to code concepts. A meeting note discussing "string comparison for verification" created a persistent graph edge linking the verifier to string comparison — even after the code switched to numerical comparison.

**Fix:** Never graph project management artifacts. Keep them as flat files.

### Anti-pattern 5: No explicit claim-to-evidence mapping

**What happened:** Paper claims were written by Claude Code navigating the knowledge graph and reading result files. There was no machine-readable record of which specific files and computations supported each claim.

**Why it was harmful:** When results were regenerated or the pipeline changed, there was no way to automatically detect which paper claims were affected. Stale claims persisted through multiple draft revisions.

**Fix:** `claims.jsonl` with explicit evidence chains.

### Anti-pattern 6: Research evolution not tracked separately from code evolution

**What happened:** Git log was the only history of changes. But git log tracks file diffs, not scientific implications. The commit "update verifier.py to use numerical comparison" is a code change; the scientific implication "all prior results are invalid" was communicated verbally to the team but never recorded in a machine-readable format.

**Fix:** `CHANGELOG.research.md` — a separate, human-curated log of scientific changes and their implications.

---

## 12. Templates and File Specifications

### Template: CLAUDE.md for new research projects

```markdown
# CLAUDE.md — {PROJECT_NAME}

{One-sentence project description}.

## Environment

- `python3` always, never `python`
- Venv: `source env_{project}/bin/activate`
- Platform: {macOS path} = dev, {Linux path} = GPU machine

## Architecture

| Path | Purpose |
|------|---------|
| `harness/` | Build → Run → Verify pipeline |
| `scripts/evaluation/` | LLM eval batch runner |
| `scripts/analysis/` | Figure/table generation from results |
| `specs/` | Experiment spec JSONs |
| `results/` | Immutable result JSONs (NEVER modify) |
| `docs/paper/` | LaTeX paper source |

## Critical Files for Consistency

| File | What it is | When to read |
|------|-----------|--------------|
| `CHANGELOG.research.md` | Scientific evolution log | Before ANY paper writing |
| `claims.jsonl` | Paper claim → evidence mapping | Before writing results sections |
| `harness/pipeline_version.py` | Pipeline fingerprinting | When checking result validity |

## Invariants

1. `results/` files are immutable — never modify after creation
2. Every result JSON contains a `pipeline_version` field
3. Every paper claim has a corresponding `claims.jsonl` entry
4. Read `CHANGELOG.research.md` before writing paper sections

## Graphify

Engineering graph only: `graphify-out-engineering/`
- Use for code structure questions ("how does X connect to Y?")
- Do NOT use for results, paper claims, or scientific questions
- Rebuild only on major refactors

## Quality

- Read before editing. No partial implementations.
- Compute values from raw data — never use remembered numbers.
- If unsure, say so explicitly.
```

### Template: CHANGELOG.research.md

```markdown
# Research Changelog — {PROJECT_NAME}

> This file tracks scientific changes — methodology, metrics, validation,
> schemas. NOT code bug fixes or refactors (those are in git log).
>
> Read this before writing any paper section. The most recent entry
> describes the current state of the research.
>
> Format: newest entries at top. Each entry has: Changed, Why, Impact,
> Status, Pipeline version.

## {DATE} — Pipeline vN ({fingerprint})

- **Changed:** {What changed, naming specific files and functions}
- **Why:** {Motivation — team feedback, discovered flaw, new requirement}
- **Impact:** {What prior work is invalidated}
  - Affected results: {all / specific subset}
  - Affected paper sections: {list}
  - Affected figures/tables: {list}
- **Status:** {Current state — re-run complete? Paper updated?}
- **Pipeline version:** `{fingerprint}`
```

### Template: claims.jsonl

```jsonl
{"claim_id": "C001", "claim_text": "{exact text of the claim}", "paper_section": "4.2", "paper_element": "Table T2", "value": 34.2, "unit": "percent", "pipeline_version": "a3f8b2c1e9d4", "source_data": "results/evaluation/{model}/**/{direction}/*.json", "computed_by": "scripts/analysis/{script}.py", "computation_method": "{human-readable description}", "last_verified": "2026-04-20", "status": "current"}
```

### Template: .graphifyignore-engineering

```
# .graphifyignore-engineering
# Scope: engineering code only (Concern 1)

# Exclude research artifacts (Concern 2)
results/
analysis/
docs/
specs/
expected_outputs/
manifest.jsonl
claims.jsonl
CHANGELOG.research.md
RESULTS.md

# Exclude project management (Concern 3)
meeting_notes/
presentations/
planning/
HANDOFF.md

# Exclude external dependencies (Concern 4)
rodinia/
xsbench/
rsbench/
mixbench/
HeCBench-master/
external/

# Exclude non-code files
*.pdf
*.png
*.jpg
*.jpeg
*.gif
*.zip
*.tar.gz

# Exclude graphify output
graphify-out*/

# Exclude environment
env_*/
.venv/
venv/
__pycache__/
.pytest_cache/
```

### Template: .claude/settings.json (lean)

```json
{
  "permissions": {
    "allow": [
      "Bash(date:*)",
      "Bash(echo:*)",
      "Bash(cat:*)",
      "Bash(ls:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(grep:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git status:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(rm -fr:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "PAYLOAD=$(cat); FILE=$(echo \"$PAYLOAD\" | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))\" 2>/dev/null); if echo \"$FILE\" | grep -q 'results/'; then echo 'BLOCKED: Result files are immutable.' >&2 && exit 2; fi",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(cat | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))\" 2>/dev/null); if [ -n \"$FILE\" ] && echo \"$FILE\" | grep -qE '\\.py$'; then python3 -m ruff check --fix \"$FILE\" 2>/dev/null || true; fi"
          }
        ]
      }
    ]
  }
}
```

---

## 13. Quick Reference: Decision Trees

### "Should I graph this file?"

```
Is it in harness/, scripts/, schema/, tests/, config/?
  YES → Include in engineering graph
  NO  →
    Is it a meeting note, task list, presentation, or planning doc?
      YES → NEVER graph. Keep as flat file.
      NO  →
        Is it a spec file (specs/*.json)?
          YES → Include in research graph (if building one)
          NO  →
            Is it a result file (results/**/*.json)?
              YES → NEVER graph. Use pipeline fingerprinting + claims.jsonl.
              NO  →
                Is it paper source (docs/paper/)?
                  YES → Include in research graph (if building one)
                  NO  → Probably don't graph it. Ask: "Would a stale
                         version of this file in the graph mislead
                         Claude Code?" If yes, don't graph it.
```

### "Should I rebuild the graph?"

```
Did you change files in harness/, scripts/, schema/?
  YES →
    Was it a major structural change (new module, new pipeline stage,
    changed architecture)?
      YES → Rebuild engineering graph
      NO  → Don't rebuild (bug fixes, parameter tweaks don't change structure)
  NO →
    Did you change specs/ or docs/paper/?
      YES → Rebuild research graph (if you have one)
      NO  → Don't rebuild
```

### "Should I add a CHANGELOG.research.md entry?"

```
Did the change affect how results are produced or interpreted?
  YES → Add an entry. Examples:
    - Changed verification logic
    - Changed result schema
    - Added/removed metrics
    - Changed spec run arguments
    - Changed what counts as PASS/FAIL
    - Changed which specs are excluded from analysis
  NO → Don't add an entry. Examples:
    - Fixed a typo in a docstring
    - Refactored code without changing behavior
    - Updated a dependency
    - Changed logging format
```

### "Should I add a claims.jsonl entry?"

```
Will this number appear in the paper?
  YES → Add a claim entry BEFORE writing the paper text.
  NO  →
    Is it a computed statistic that informs a paper claim?
      YES → Consider adding it as a supporting claim.
      NO  → Don't add it.
```

### "What should Claude Code read before this task?"

```
Task: Writing or editing code in harness/ or scripts/
  Read: CLAUDE.md, .claude/rules/architecture.md, engineering graph report

Task: Running an evaluation batch
  Read: CLAUDE.md, CHANGELOG.research.md (current pipeline version),
        .claude/rules/known-issues.md

Task: Writing a paper section about methodology
  Read: CLAUDE.md, engineering graph report, CHANGELOG.research.md

Task: Writing a paper section about results
  Read: CHANGELOG.research.md, claims.jsonl, raw result files.
        Do NOT read the engineering graph — it's irrelevant.

Task: Creating figures or tables
  Read: claims.jsonl (to verify computed values match claims),
        the specific analysis script that generates the figure.

Task: Responding to reviewer feedback
  Read: CHANGELOG.research.md (full history), claims.jsonl,
        the specific reviewer comment and the paper section it targets.
```

---

## Appendix A: Graphify Command Reference (Relevant Subset)

These are the Graphify commands relevant to the scoped-graph workflow:

```bash
# Build engineering graph (Concern 1 only)
graphify extract harness/ scripts/ schema/ tests/ config/ \
  --out graphify-out-engineering/

# Update engineering graph after structural refactor
graphify update graphify-out-engineering/

# Query engineering graph
graphify query "how does the verifier connect to the runner?" \
  --graph graphify-out-engineering/graph.json

# Explain a node in the engineering graph
graphify explain "VerificationResult" \
  --graph graphify-out-engineering/graph.json

# Find path between two nodes
graphify path "Builder" "Verifier" \
  --graph graphify-out-engineering/graph.json

# Build research graph (optional, Concern 2 subset)
graphify extract specs/ docs/paper/ \
  --out graphify-out-research/

# Serve engineering graph as MCP server
python3 -m graphify.serve graphify-out-engineering/graph.json
```

## Appendix B: Pipeline Fingerprint Quick Reference

```bash
# Check current pipeline fingerprint
python3 -c "from harness.pipeline_version import compute_pipeline_fingerprint; print(compute_pipeline_fingerprint('.'))"

# Check what pipeline version a result was produced under
python3 -c "import json; print(json.load(open('results/evaluation/{model}/{result}.json')).get('pipeline_version', 'MISSING'))"

# Find all pipeline versions in results
python3 -c "
import json, pathlib, collections
versions = collections.Counter()
for f in pathlib.Path('results/evaluation').rglob('*.json'):
    v = json.load(open(f)).get('pipeline_version', 'MISSING')
    versions[v] += 1
for v, count in versions.most_common():
    print(f'{v}: {count} results')
"

# Verify all claims against current pipeline version
python3 scripts/verify_claims.py
```

## Appendix C: Revision History of This Document

| Date | Change | Author |
|------|--------|--------|
| 2026-05-21 | Initial creation based on ParBench lessons learned | Claude (with Sam) |

---

*This document is itself subject to the lean philosophy it advocates. If a section becomes stale or irrelevant to the current project, remove it. If a new failure pattern emerges, add a section. The document should reflect the current state of the workflow, not accumulate historical cruft.*
