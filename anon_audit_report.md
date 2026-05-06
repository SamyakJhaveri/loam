# Anonymization Audit Report — `parbench_artifact_neurips.zip`

**Date:** 2026-05-06

---

## Issues Found

### 1. `erel` branch name (HIGH — clear identifier)

**File:** `results/augmentation/_archive/pre-phase3-2026-03-16/augmentation_status_report_2026-03-10.md` (lines 3, 11, 24)

References to `erel/aug` (a git branch name) appear 3 times:

```
Branch: main (post `Merge branch 'erel/aug'`, commit 8efe990)
The augmentation pipeline (`erel/aug`) is merged into main
Is `erel/aug` merged into main? | YES
```

This leaks a username/author identifier. **Fix:** Delete the file or replace `erel/aug` with `[author-branch]/aug`.

---

### 2. `/home/sam` path fragment (MEDIUM — partial username leak)

**File:** `results/evaluation/azure-gpt-5.4/mixbench-mixbench-opencl-to-mixbench-mixbench-cuda-s1.json` (lines 24, 63)

A compiler error snippet contains `/home/sam\n...[truncated]...` — this is a truncated `/home/samyak/...` path from the evaluation server, captured in the `build_error_snippet` field. Appears twice (baseline entry + sample 0).

**Fix:** Replace `/home/sam` with `/home/[user]` or `[project-root]` in both occurrences.

---

## Clean (no issues)

| File / Area | Status |
|-------------|--------|
| `pyproject.toml` | Clean — no author fields |
| `croissant.json` | Clean — uses "Anonymous" and `anonymous.4open.science` URL |
| `README.md`, `artifact/README.md` | Clean |
| All Python scripts (`harness/`, `scripts/`, `c_augmentation/`) | Clean — no names or emails |
| All spec JSONs (`specs/`) | Clean — only upstream benchmark repo URLs, not author repos |
| `config/paths.json` | Clean — uses relative `.` paths only |
| `harness/runner.py` `/home/...` mention | Clean — code comment about argv parsing, not a real path |
| All other result JSONs | Clean |

---

## Summary

| Severity | Count | Files |
|----------|-------|-------|
| HIGH | 1 | `results/augmentation/_archive/.../augmentation_status_report_2026-03-10.md` |
| MEDIUM | 1 | `results/evaluation/azure-gpt-5.4/mixbench-mixbench-opencl-to-mixbench-mixbench-cuda-s1.json` |
| None | all others | — |

Both issues are in results/archive files rather than core code. Two targeted edits (or deleting the archive status report) are sufficient to clear the artifact for submission.
