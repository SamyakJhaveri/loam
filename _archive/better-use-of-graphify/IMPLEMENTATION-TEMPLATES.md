# Implementation Templates & Ready-to-Use Code

> **Purpose:** Drop-in code templates for implementing the research workflow system described in `RESEARCH-WORKFLOW-MASTERGUIDE.md`. Each template is self-contained and annotated with integration instructions.

> **Usage:** Copy the relevant templates into your new research project and customize the marked `{PLACEHOLDERS}`. Files are ordered by implementation priority — start with Template 1 and work down.

---

## Template 1: Pipeline Fingerprinting Module

**File:** `harness/pipeline_version.py`

**Priority:** CRITICAL — implement before running any experiments.

```python
"""Pipeline fingerprinting: version-stamp every result with a content hash.

This module computes a deterministic hash of the pipeline files that affect
result validity. The hash changes when any critical file changes, providing
an automatic mechanism to detect which results were produced under which
version of the evaluation framework.

Usage:
    from harness.pipeline_version import (
        compute_pipeline_fingerprint,
        get_pipeline_version_record,
        CRITICAL_PIPELINE_FILES,
    )

    # Embed in every result JSON:
    result = {**eval_output, **get_pipeline_version_record(project_root)}

    # Check current version:
    print(compute_pipeline_fingerprint(project_root))
"""

import hashlib
import pathlib
from datetime import datetime, timezone
from typing import Optional


# ──────────────────────────────────────────────────────────────────────
# CONFIGURE THIS LIST FOR YOUR PROJECT
#
# Include ONLY files whose changes invalidate prior results.
# Ask: "If this file changes, should I re-run experiments?"
#   YES → include it
#   NO  → leave it out
#
# Do NOT include:
#   - Analysis scripts (they process results, don't produce them)
#   - Paper source files
#   - Spec files (tracked separately by spec version)
#   - CLI wrappers, logging, formatting code
#   - Test files
# ──────────────────────────────────────────────────────────────────────
CRITICAL_PIPELINE_FILES: list[str] = [
    # {CUSTOMIZE: replace these with your project's critical pipeline files}
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
    """Compute a content hash of files that affect result validity.

    Returns a 12-character hex string. Deterministic: same file contents
    always produce the same hash. Any change to any critical file changes
    the hash.

    Args:
        project_root: Path to the project root directory.
        additional_files: Optional extra files to include (relative paths).

    Returns:
        12-character hex string (e.g., "a3f8b2c1e9d4").

    Raises:
        No exceptions — missing files are hashed as "MISSING:{path}" so
        the fingerprint still changes when a file is added or removed.
    """
    root = pathlib.Path(project_root).resolve()
    files = list(CRITICAL_PIPELINE_FILES)
    if additional_files:
        files.extend(additional_files)

    h = hashlib.sha256()
    for f in sorted(set(files)):  # sorted + deduplicated for determinism
        path = root / f
        if path.exists():
            h.update(f"FILE:{f}:".encode())
            h.update(path.read_bytes())
        else:
            h.update(f"MISSING:{f}".encode())

    return h.hexdigest()[:12]


def get_pipeline_version_record(
    project_root: str | pathlib.Path,
    additional_files: Optional[list[str]] = None,
) -> dict:
    """Return a dict to embed in result JSONs.

    Example return value:
    {
        "pipeline_version": "a3f8b2c1e9d4",
        "pipeline_files_hashed": ["harness/builder.py", ...],
        "pipeline_version_computed_at": "2026-05-21T14:30:00+00:00"
    }
    """
    root = pathlib.Path(project_root).resolve()
    fingerprint = compute_pipeline_fingerprint(root, additional_files)

    all_files = list(CRITICAL_PIPELINE_FILES)
    if additional_files:
        all_files.extend(additional_files)

    return {
        "pipeline_version": fingerprint,
        "pipeline_files_hashed": sorted(set(all_files)),
        "pipeline_version_computed_at": datetime.now(timezone.utc).isoformat(),
    }


def check_result_version(
    result: dict,
    project_root: str | pathlib.Path,
) -> dict:
    """Check whether a result matches the current pipeline version.

    Returns:
        {
            "is_current": bool,
            "result_version": str or "MISSING",
            "current_version": str,
        }
    """
    current = compute_pipeline_fingerprint(project_root)
    result_version = result.get("pipeline_version", "MISSING")
    return {
        "is_current": result_version == current,
        "result_version": result_version,
        "current_version": current,
    }


# ──────────────────────────────────────────────────────────────────────
# CLI entry point: python3 -m harness.pipeline_version
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    fp = compute_pipeline_fingerprint(root)
    print(f"Pipeline fingerprint: {fp}")
    print(f"Files hashed: {sorted(CRITICAL_PIPELINE_FILES)}")
```

---

## Template 2: Claims Verification Script

**File:** `scripts/verify_claims.py`

**Priority:** HIGH — implement before paper-writing phase begins.

```python
#!/usr/bin/env python3
"""Verify paper claims against raw data and current pipeline version.

Reads claims.jsonl and checks:
1. Pipeline version currency (does the claim's version match current?)
2. Source data existence (do the referenced result files exist?)
3. Computation reproducibility (re-run the analysis and compare values)

Usage:
    python3 scripts/verify_claims.py                    # check all claims
    python3 scripts/verify_claims.py --section 4.2      # check section 4.2 only
    python3 scripts/verify_claims.py --stale-only        # show only stale claims
    python3 scripts/verify_claims.py --mark-stale        # update status of stale claims

Exit codes:
    0 = all claims current
    1 = stale claims found
    2 = missing data or errors
"""

import argparse
import glob
import json
import pathlib
import sys
from datetime import date

# Adjust this import to match your project structure
try:
    from harness.pipeline_version import compute_pipeline_fingerprint
except ImportError:
    # Fallback if harness isn't on the path
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from harness.pipeline_version import compute_pipeline_fingerprint


def load_claims(claims_path: pathlib.Path) -> list[dict]:
    """Load claims from a JSONL file."""
    claims = []
    for i, line in enumerate(claims_path.read_text().strip().split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        try:
            claims.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"ERROR: claims.jsonl line {i}: {e}", file=sys.stderr)
    return claims


def check_pipeline_currency(claim: dict, current_version: str) -> dict:
    """Check if a claim's pipeline version matches the current version."""
    claim_version = claim.get("pipeline_version", "MISSING")
    is_current = claim_version == current_version
    return {
        "check": "pipeline_version",
        "passed": is_current,
        "detail": (
            f"current"
            if is_current
            else f"STALE: claim uses {claim_version}, current is {current_version}"
        ),
    }


def check_source_data_exists(claim: dict, project_root: pathlib.Path) -> dict:
    """Check if the source data files referenced by the claim exist."""
    source_pattern = claim.get("source_data", "")
    if not source_pattern:
        return {
            "check": "source_data",
            "passed": False,
            "detail": "no source_data field in claim",
        }

    # Expand glob pattern
    matches = list(project_root.glob(source_pattern))
    if not matches:
        # Try with ** prefix in case pattern is relative
        matches = list(project_root.glob(f"**/{source_pattern}"))

    return {
        "check": "source_data",
        "passed": len(matches) > 0,
        "detail": (
            f"{len(matches)} files found"
            if matches
            else f"no files match pattern: {source_pattern}"
        ),
    }


def check_computation_script_exists(
    claim: dict, project_root: pathlib.Path
) -> dict:
    """Check if the analysis script that computes this claim exists."""
    script = claim.get("computed_by", "")
    if not script:
        return {
            "check": "computed_by",
            "passed": False,
            "detail": "no computed_by field in claim",
        }

    script_path = project_root / script
    return {
        "check": "computed_by",
        "passed": script_path.exists(),
        "detail": (
            f"script exists: {script}"
            if script_path.exists()
            else f"MISSING script: {script}"
        ),
    }


def verify_all_claims(
    project_root: pathlib.Path,
    section_filter: str | None = None,
    stale_only: bool = False,
) -> tuple[list[dict], int]:
    """Run all verification checks on all claims.

    Returns:
        (results_list, exit_code)
    """
    claims_path = project_root / "claims.jsonl"
    if not claims_path.exists():
        print("ERROR: claims.jsonl not found in project root", file=sys.stderr)
        return [], 2

    claims = load_claims(claims_path)
    if not claims:
        print("WARNING: claims.jsonl is empty")
        return [], 0

    current_version = compute_pipeline_fingerprint(project_root)
    print(f"Current pipeline version: {current_version}")
    print(f"Total claims: {len(claims)}")
    print()

    results = []
    stale_count = 0
    error_count = 0

    for claim in claims:
        # Apply section filter
        if section_filter and claim.get("paper_section") != section_filter:
            continue

        checks = [
            check_pipeline_currency(claim, current_version),
            check_source_data_exists(claim, project_root),
            check_computation_script_exists(claim, project_root),
        ]

        is_stale = not checks[0]["passed"]
        has_errors = any(not c["passed"] for c in checks[1:])

        if is_stale:
            stale_count += 1
        if has_errors:
            error_count += 1

        # Apply stale-only filter
        if stale_only and not is_stale:
            continue

        claim_result = {
            "claim_id": claim.get("claim_id", "???"),
            "claim_text": claim.get("claim_text", "")[:80],
            "paper_section": claim.get("paper_section", "?"),
            "paper_element": claim.get("paper_element", "?"),
            "status": claim.get("status", "unknown"),
            "checks": checks,
            "is_stale": is_stale,
            "has_errors": has_errors,
        }
        results.append(claim_result)

        # Print results
        status_icon = "✗" if (is_stale or has_errors) else "✓"
        print(f"  {status_icon} {claim_result['claim_id']}: {claim_result['claim_text']}...")
        print(f"    Section {claim_result['paper_section']}, {claim_result['paper_element']}")
        for check in checks:
            icon = "✓" if check["passed"] else "✗"
            print(f"      {icon} {check['check']}: {check['detail']}")
        print()

    # Summary
    print("=" * 60)
    filtered_total = len(results) if stale_only else len([c for c in claims if not section_filter or c.get("paper_section") == section_filter])
    print(f"Claims checked: {filtered_total}")
    print(f"  Current:  {filtered_total - stale_count - error_count}")
    print(f"  Stale:    {stale_count}")
    print(f"  Errors:   {error_count}")

    exit_code = 0
    if stale_count > 0:
        exit_code = 1
    if error_count > 0:
        exit_code = 2

    return results, exit_code


def mark_stale_claims(project_root: pathlib.Path) -> None:
    """Update claims.jsonl, setting stale claims' status to 'stale'."""
    claims_path = project_root / "claims.jsonl"
    current_version = compute_pipeline_fingerprint(project_root)

    claims = load_claims(claims_path)
    updated = 0

    lines = []
    for claim in claims:
        if (
            claim.get("pipeline_version") != current_version
            and claim.get("status") != "stale"
        ):
            claim["status"] = "stale"
            updated += 1
        lines.append(json.dumps(claim, ensure_ascii=False))

    claims_path.write_text("\n".join(lines) + "\n")
    print(f"Marked {updated} claims as stale (pipeline version mismatch)")


def main():
    parser = argparse.ArgumentParser(
        description="Verify paper claims against raw data and pipeline version"
    )
    parser.add_argument(
        "--project-root",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Filter by paper section (e.g., '4.2')",
    )
    parser.add_argument(
        "--stale-only",
        action="store_true",
        help="Show only stale claims",
    )
    parser.add_argument(
        "--mark-stale",
        action="store_true",
        help="Update claims.jsonl, marking stale claims",
    )
    args = parser.parse_args()

    if args.mark_stale:
        mark_stale_claims(args.project_root)
        return

    _, exit_code = verify_all_claims(
        args.project_root,
        section_filter=args.section,
        stale_only=args.stale_only,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
```

---

## Template 3: Result Version Audit Script

**File:** `scripts/audit_result_versions.py`

**Priority:** HIGH — run before any analysis or paper writing.

```python
#!/usr/bin/env python3
"""Audit result files for pipeline version consistency.

Scans all result JSONs and reports:
- How many distinct pipeline versions exist
- Which results are current vs stale
- Specific files that need re-running

Usage:
    python3 scripts/audit_result_versions.py
    python3 scripts/audit_result_versions.py --results-dir results/evaluation
    python3 scripts/audit_result_versions.py --current-only  # list only current results
    python3 scripts/audit_result_versions.py --stale-only    # list only stale results
"""

import argparse
import json
import pathlib
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness.pipeline_version import compute_pipeline_fingerprint


def audit_results(
    project_root: pathlib.Path,
    results_dir: pathlib.Path,
    show_current: bool = True,
    show_stale: bool = True,
) -> dict:
    current_version = compute_pipeline_fingerprint(project_root)
    print(f"Current pipeline version: {current_version}\n")

    versions: dict[str, list[str]] = defaultdict(list)
    errors: list[str] = []

    for path in sorted(results_dir.rglob("*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
            version = data.get("pipeline_version", "MISSING")
            versions[version].append(str(path.relative_to(project_root)))
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"{path}: {e}")

    total = sum(len(files) for files in versions.values())

    # Summary
    print(f"Total result files: {total}")
    print(f"Distinct pipeline versions: {len(versions)}")
    print()

    for version in sorted(versions.keys()):
        files = versions[version]
        is_current = version == current_version
        label = "CURRENT" if is_current else "STALE"
        marker = "✓" if is_current else "✗"

        if (is_current and not show_current) or (not is_current and not show_stale):
            continue

        print(f"  {marker} Version {version} ({label}): {len(files)} files")

        # Show first few files as examples
        for f in files[:5]:
            print(f"      {f}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
        print()

    if errors:
        print(f"\nErrors reading {len(errors)} files:")
        for e in errors:
            print(f"  {e}")

    # Return structured report
    current_files = versions.get(current_version, [])
    stale_files = [
        f for v, files in versions.items() if v != current_version for f in files
    ]

    return {
        "current_version": current_version,
        "total_results": total,
        "current_results": len(current_files),
        "stale_results": len(stale_files),
        "versions": {v: len(f) for v, f in versions.items()},
        "needs_rerun": len(stale_files) > 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit result file pipeline versions")
    parser.add_argument(
        "--project-root",
        type=pathlib.Path,
        default=pathlib.Path("."),
    )
    parser.add_argument(
        "--results-dir",
        type=pathlib.Path,
        default=None,
        help="Results directory (default: {project-root}/results/evaluation)",
    )
    parser.add_argument("--current-only", action="store_true")
    parser.add_argument("--stale-only", action="store_true")
    args = parser.parse_args()

    results_dir = args.results_dir or (args.project_root / "results" / "evaluation")
    if not results_dir.exists():
        print(f"ERROR: {results_dir} does not exist", file=sys.stderr)
        sys.exit(2)

    report = audit_results(
        args.project_root,
        results_dir,
        show_current=not args.stale_only,
        show_stale=not args.current_only,
    )

    if report["needs_rerun"]:
        print(
            f"\n⚠ WARNING: {report['stale_results']} result files were produced "
            f"by an older pipeline version. Re-run experiments or archive stale results "
            f"before writing paper sections."
        )
        sys.exit(1)
    else:
        print(f"\n✓ All {report['current_results']} results match the current pipeline version.")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Template 4: Claims Auto-Generator for Analysis Scripts

**File:** `scripts/analysis/claims_helper.py`

**Priority:** MEDIUM — integrate into analysis scripts during paper-writing phase.

```python
"""Helper for automatically generating claims.jsonl entries from analysis output.

Usage in analysis scripts:

    from scripts.analysis.claims_helper import ClaimsRecorder

    recorder = ClaimsRecorder(project_root=".")

    # After computing a statistic:
    pass_rate = compute_pass_rate(results, model="qwen", direction="cuda-to-omp")

    recorder.record(
        claim_text=f"Qwen achieves a {pass_rate:.1f}% overall pass rate on CUDA-to-OpenMP",
        paper_section="4.2",
        paper_element="Table T2, row 1",
        value=pass_rate,
        unit="percent",
        source_data="results/evaluation/together-qwen-*/**/cuda-to-omp/*.json",
        computed_by="scripts/analysis/compute_pass_rates.py",
        computation_method="count(PASS) / count(all, excl KNOWN_FAIL) * 100",
    )

    # At the end of the script:
    recorder.save()  # appends new claims to claims.jsonl
"""

import json
import pathlib
from datetime import date
from typing import Optional

from harness.pipeline_version import compute_pipeline_fingerprint


class ClaimsRecorder:
    """Records paper claims with evidence chains for claims.jsonl."""

    def __init__(self, project_root: str | pathlib.Path = "."):
        self.project_root = pathlib.Path(project_root).resolve()
        self.claims_file = self.project_root / "claims.jsonl"
        self.pipeline_version = compute_pipeline_fingerprint(self.project_root)
        self.new_claims: list[dict] = []
        self._existing_ids = self._load_existing_ids()
        self._next_id = self._compute_next_id()

    def _load_existing_ids(self) -> set[str]:
        """Load existing claim IDs to avoid duplicates."""
        ids = set()
        if self.claims_file.exists():
            for line in self.claims_file.read_text().strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        claim = json.loads(line)
                        ids.add(claim.get("claim_id", ""))
                    except json.JSONDecodeError:
                        pass
        return ids

    def _compute_next_id(self) -> int:
        """Compute the next claim ID number."""
        max_id = 0
        for cid in self._existing_ids:
            if cid.startswith("C") and cid[1:].isdigit():
                max_id = max(max_id, int(cid[1:]))
        return max_id + 1

    def record(
        self,
        claim_text: str,
        paper_section: str,
        paper_element: str,
        value: float | int | str,
        unit: str,
        source_data: str,
        computed_by: str,
        computation_method: str,
        denominator_note: Optional[str] = None,
    ) -> str:
        """Record a new claim. Returns the assigned claim ID."""
        claim_id = f"C{self._next_id:03d}"
        self._next_id += 1

        claim = {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "paper_section": paper_section,
            "paper_element": paper_element,
            "value": value,
            "unit": unit,
            "pipeline_version": self.pipeline_version,
            "source_data": source_data,
            "computed_by": computed_by,
            "computation_method": computation_method,
            "last_verified": date.today().isoformat(),
            "status": "current",
        }
        if denominator_note:
            claim["denominator_note"] = denominator_note

        self.new_claims.append(claim)
        self._existing_ids.add(claim_id)

        return claim_id

    def save(self) -> int:
        """Append new claims to claims.jsonl. Returns count of claims added."""
        if not self.new_claims:
            return 0

        with open(self.claims_file, "a") as f:
            for claim in self.new_claims:
                f.write(json.dumps(claim, ensure_ascii=False) + "\n")

        count = len(self.new_claims)
        self.new_claims = []
        return count
```

---

## Template 5: Post-Eval Hook for Automatic Staleness Detection

**File:** `.claude/hooks/post-eval-check.sh`

**Priority:** MEDIUM — fires after eval scripts run to warn about mixed pipeline versions.

```bash
#!/usr/bin/env bash
# Post-eval hook: check for mixed pipeline versions in results.
# Attach to PostToolUse for Bash commands matching eval patterns.

set -euo pipefail

PAYLOAD=$(cat)
COMMAND=$(echo "$PAYLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null || true)

# Only fire after evaluation commands
if ! echo "$COMMAND" | grep -qE 'run_eval_batch|llm_evaluate|eval'; then
    exit 0
fi

# Check for mixed versions
PROJECT_ROOT="${PROJECT_ROOT:-.}"
if [ -f "$PROJECT_ROOT/harness/pipeline_version.py" ]; then
    RESULT=$(python3 scripts/audit_result_versions.py --project-root "$PROJECT_ROOT" 2>&1 | tail -5)
    if echo "$RESULT" | grep -q "WARNING"; then
        echo "{\"hookSpecificOutput\":{\"additionalContext\":\"⚠ MIXED PIPELINE VERSIONS detected in results. Run 'python3 scripts/audit_result_versions.py' for details. Do NOT write paper sections until resolved.\"}}"
    fi
fi
```

---

## Template 6: Starter claims.jsonl

**File:** `claims.jsonl` (project root)

**Priority:** Create at the start of paper-writing phase. Start empty; populate as you compute statistics.

```jsonl
{"claim_id": "C001", "claim_text": "EXAMPLE — replace with your first real claim", "paper_section": "0.0", "paper_element": "N/A", "value": 0, "unit": "example", "pipeline_version": "000000000000", "source_data": "results/evaluation/**/*.json", "computed_by": "scripts/analysis/example.py", "computation_method": "example — delete this line and add real claims", "last_verified": "2026-01-01", "status": "template"}
```

---

## Template 7: Starter CHANGELOG.research.md

**File:** `CHANGELOG.research.md` (project root)

```markdown
# Research Changelog

> Track scientific changes — methodology, metrics, validation, schemas.
> NOT code bug fixes (those are in git log).
>
> Read this before writing any paper section.
> Newest entries at top.

## {DATE} — Pipeline v1 (initial) ({FINGERPRINT})

- **Changed:** Initial evaluation pipeline.
  - {Describe the initial verification method}
  - {Describe the initial result schema}
  - {Describe the initial metrics}
- **Why:** First working version.
- **Impact:** Baseline — no prior results to invalidate.
- **Status:** Initial experiments in progress.
- **Pipeline version:** `{FINGERPRINT}`
```

---

## Template 8: Lean CLAUDE.md

**File:** `CLAUDE.md` (project root)

```markdown
# CLAUDE.md — {PROJECT_NAME}

{One-sentence description of the research project.}

## Environment

- `python3` always, never `python`
- Venv: `source env_{project}/bin/activate`
- Platform: macOS = dev, Linux = GPU machine

## Architecture

| Path | Purpose |
|------|---------|
| `harness/` | Build → Run → Verify pipeline |
| `scripts/evaluation/` | LLM eval batch runner |
| `scripts/analysis/` | Figure and table generation |
| `specs/` | Experiment specification JSONs |
| `results/` | Immutable result JSONs — NEVER modify |
| `docs/paper/` | LaTeX paper source |

## Consistency System

| File | Read when | Purpose |
|------|-----------|---------|
| `CHANGELOG.research.md` | Before ANY paper writing | What changed scientifically, what's invalidated |
| `claims.jsonl` | Before writing results sections | Paper claim → raw evidence mapping |
| `harness/pipeline_version.py` | When checking result validity | Pipeline fingerprinting module |

**Before writing any paper section:** read CHANGELOG.research.md, then claims.jsonl.
**Before citing any number:** verify it has a claims.jsonl entry with status "current".
**Never invent numbers.** Compute from raw data, then record as a claim.

## Invariants

1. `results/` files are immutable — never modify after creation
2. Every result JSON has a `pipeline_version` field
3. Every paper number has a `claims.jsonl` entry
4. `CHANGELOG.research.md` is the ground truth for scientific state
5. {Add project-specific invariants here}

## Graphify

Engineering graph at `graphify-out-engineering/`. Use for code structure
questions only. Do NOT use for paper claims, results, or scientific questions.

## Quality

- Read before editing. No partial implementations.
- Compute values from raw data — never use remembered numbers.
- If unsure, say so explicitly — never guess silently.
```

---

## Template 9: .graphifyignore for Engineering Graph

**File:** `.graphifyignore` (project root — used for the engineering-scoped graph)

```gitignore
# .graphifyignore — Engineering graph scope
# Include: harness/, scripts/, schema/, tests/, config/
# Exclude: everything else

# Research artifacts (use claims.jsonl + CHANGELOG.research.md instead)
results/
analysis/
docs/
specs/
expected_outputs/
manifest.jsonl
claims.jsonl
CHANGELOG.research.md
RESULTS.md

# Project management (NEVER graph)
meeting_notes/
presentations/
planning/
HANDOFF.md
TODO.md
*.pdf
*.png
*.jpg
*.jpeg
*.gif
*.zip
*.tar.gz

# External dependencies
rodinia/
xsbench/
rsbench/
mixbench/
HeCBench*/
external/

# Environment / build artifacts
env_*/
.venv/
venv/
__pycache__/
.pytest_cache/
node_modules/
*.pyc
*.egg-info/

# Graphify output
graphify-out*/

# Git / IDE
.git/
.github/
.claude/
.DS_Store
```

---

## Integration Checklist

Use this checklist when setting up a new research project:

```markdown
## New Project Setup Checklist

### Day 1: Project scaffold
- [ ] Create directory structure per MASTERGUIDE Section 3
- [ ] Copy CLAUDE.md template (Template 8), customize placeholders
- [ ] Copy .graphifyignore (Template 9)
- [ ] Copy .claude/settings.json template (MASTERGUIDE Section 8)
- [ ] Initialize git, create .gitignore
- [ ] Create virtual environment, install dependencies

### When framework code stabilizes (end of Phase 2):
- [ ] Implement pipeline_version.py (Template 1)
- [ ] Integrate fingerprinting into eval runner
- [ ] Build engineering Graphify graph
- [ ] Create initial CHANGELOG.research.md entry (Template 7)

### Before first experiment batch:
- [ ] Verify pipeline_version field appears in a test result JSON
- [ ] Run audit_result_versions.py (Template 3) to confirm

### Start of paper-writing phase:
- [ ] Create claims.jsonl (Template 6, replace example entry)
- [ ] Implement verify_claims.py (Template 2)
- [ ] Integrate ClaimsRecorder (Template 4) into analysis scripts
- [ ] Read MASTERGUIDE Section 10 (Paper-Writing Consistency Protocol)

### Before each paper writing session:
- [ ] python3 scripts/verify_claims.py
- [ ] python3 scripts/audit_result_versions.py
- [ ] Read CHANGELOG.research.md (most recent entry)

### Before submission:
- [ ] python3 scripts/verify_claims.py (all claims "current", 0 stale)
- [ ] python3 scripts/audit_result_versions.py (0 stale results)
- [ ] Manual review: every number in paper has claim ID in LaTeX comment
```
