# Session S1 Kickoff Prompt

Paste this verbatim into a new Claude Code session.

> **Note (added 2026-04-19 by s4b-review):** Entry-check below references HEAD `7facfc0` — point-in-time for S1's actual entry. Re-running today against current HEAD will not match (current HEAD is `6b790da` or descendant). This file is preserved as a historical artifact of the S1 session prompt; do not re-execute against the current tree.

---

## PROMPT

/session-start

Then execute Session S1 of the Tier 1 Oracle Framework campaign. Read `.planning/HANDOFF.md` §5 (Session S1) and §3 (Hard Rules) before touching any file.

**Entry check (run these first, stop if any fails):**
```bash
source env_parbench/bin/activate && cd /home/samyak/Desktop/parbench_sam
git log --oneline HEAD~3..HEAD   # confirm 7facfc0 or later is HEAD
python3 -m pytest -m "not llm and not integration" -q | tail -3   # baseline must pass
```

**Use `/superpowers:test-driven-development` for T1.1 + T1.2 + T1.4** — write the unit tests first (they will FAIL), then implement until they pass.

**Tasks (in order):**

**T1.4 first — write failing tests:**
- `tests/test_verifier_numeric_comparison.py`: regex match within tolerance → PASS; outside tolerance → FAIL; missing `extract_regex` key → FAIL; regex no-match → FAIL; unparseable capture → FAIL.
- `tests/test_verifier_file_hash.py`: correct SHA-256 → PASS; wrong SHA-256 → FAIL; file missing → FAIL; `working_dir=None` with `file_hash` strategy → ERROR.

**T1.1 + T1.2 — implement to make tests pass:**
In `harness/verifier.py`:
- Add `working_dir: Path | None = None` optional kwarg to `verify_run()`.
- Implement `_verify_numeric_comparison(strategy, run_result)` — regex-extract stdout via `strategy["extract_regex"]`, parse float, compare to `strategy["expected"]` within `strategy.get("tolerance", 0.0)`. FAIL if key missing, no regex match, or unparseable.
- Implement `_verify_file_hash(strategy, working_dir)` — read `working_dir / strategy["path"]`, SHA-256 it, compare to `strategy["expected_sha256"]`. ERROR if `working_dir is None`. FAIL if file missing or hash mismatch.
- Wire both into `verify_run()` dispatcher (replace the `_stub_strategy` calls for `numeric_comparison` and `file_hash`).

**T1.3 — one complete schema bump** in `schema/spec_schema.json`:
- ADD `"file_hash"` to `strategies[].type` enum (currently lines ~473–479; `numeric_comparison` already exists — do NOT re-add it).
- ADD `"expected_sha256": {"type": "string"}` to strategy item properties.
- ADD `"extract_regex": {"type": "string"}` to strategy item properties.
- ADD per-strategy `if/then` required-field constraints inside strategy item schema (use `allOf`):
  - `file_hash` requires `path` + `expected_sha256`
  - `numeric_comparison` requires `extract_regex` + `expected`
  - `stdout_pattern` requires `pattern`
- ADD `"oracle_strength": {"type": "string", "enum": ["strong", "medium", "weak", "unknown"]}` to `verification.properties`.
- ADD `"reference_files"` array to `verification.properties` (items: `{path, sha256, size_bytes?, description?}`, `additionalProperties: false`).
- The `verification` block has `"additionalProperties": false` at ~line 451 — add all new properties explicitly so they pass schema validation.

**T1.7 — ~10 LoC in `scripts/validate_schema.py`:**
After the consistency-check block in `_validate_all()`, iterate all loaded specs, count `oracle_strength` values, and print summary: `X strong, Y medium, Z weak, W unknown`. Emit `⚠ WARNING` for each spec with `oracle_strength` in `{"weak", "unknown"}` or missing entirely.

**T1.extra — update `.claude/rules/evaluation.md`:**
Add a short "Verifier Strategies" subsection documenting `numeric_comparison` and `file_hash` semantics, required fields, and the `working_dir` kwarg requirement.

**Verify after implementation:**
```bash
python3 -m pytest tests/test_verifier_numeric_comparison.py tests/test_verifier_file_hash.py -v
python3 scripts/validate_schema.py --all   # must stay within 15 known errors
```

**Before committing, invoke `/superpowers:verification-before-completion`.**

**Then run `/validate` (waves 1-3 required).**

**Commit message:**
```
feat(03-oracle): Tier 1 numeric_comparison + file_hash verifiers + schema v1.1
```

**Hard rules (NEVER violate):**
- Never touch benchmark source: `rodinia/rodinia-src/`, `HeCBench-master/`, XSBench, RSBench, mixbench.
- Never modify `manifest.jsonl` or `results/`.
- `numeric_comparison` already exists in the schema enum — do NOT re-add it.
- `if/then` constraints must be Draft-07 compatible (use `allOf` array in the strategy item).
