# Session S2 Execution Prompt — Tier 1 Oracle Framework

> Paste the code block below into a fresh Claude Code session. S2 runs in isolation from S1's context.

> **Note (added 2026-04-19 by s4b-review):** Entry-check inside the prompt expects HEAD `43142bc` and "206 missing oracle_strength" — point-in-time for S2's actual entry. Re-running today against current HEAD (`6b790da` or descendant) will FAIL the entry-check (current state: 153 missing, not 206). This file is preserved as a historical artifact of the S2 session prompt; do not re-execute against the current tree.

---

```
ultrathink. /caveman:caveman lite /andrej-karpathy-skills:karpathy-guidelines /session-start

Execute Session S2 of the Tier 1 Oracle Framework campaign. Read .planning/HANDOFF.md §5 (Session S2) and §3 (Hard Rules) before touching any file. S1 + S1.5 + S1.6 landed as 74345e0, 62f602b, 43142bc; verifier primitives, schema extensions, oracle_strength audit, and all 4 verify_run callers are hardened. S2 ships two artifacts only: the private baseline helper + the trimmed oracle guide.

Entry check (run first, stop if any fails):
  source env_parbench/bin/activate && cd /home/samyak/Desktop/parbench_sam
  git log --oneline HEAD~5..HEAD        # expect 43142bc at HEAD
  python3 -m pytest harness/ tests/ -m "not llm and not integration" -q | tail -3   # expect 196 passed, 3 skipped
  python3 scripts/validate_schema.py --all 2>&1 | grep -E "error\(s\)|oracle_strength:" | tail -3   # expect 15 errors, 206 missing oracle_strength

Hard rules (HANDOFF §3 — inviolable):
- NEVER touch benchmark source (rodinia/rodinia-src, HeCBench-master, XSBench, RSBench, mixbench).
- NEVER modify manifest.jsonl (append-only).
- NEVER modify results/.
- NEVER modify historical plans (.planning/phases/02-llm-eval-testing/02-0[1-9]-*.md).
- Rule 12: file_hash determinism is campaign-wide. The helper IS the tool that enforces this — make the warning loud.
- git push origin main is Bash-blocked; ask user to run `! git push origin main` after all work lands.

T1.5 — scripts/spec_tools/_capture_baseline.py (NEW FILE)
  Single-shot private helper. Invoked: `python3 scripts/spec_tools/_capture_baseline.py specs/<spec>.json --project-root /home/samyak/Desktop/parbench_sam`
  Behavior:
    1. Load spec via harness.spec_loader.load_spec + resolve_paths — reuse, don't reinvent.
    2. CRITICAL same-args invariant: use exactly `spec.run.input_configurations.correctness.arguments`. Document this in the script's module docstring and reject any attempt to override via CLI. Misuse breaks file_hash SHA match at eval time.
    3. Build once via harness.builder.build_spec. Abort on BUILD_FAIL with a clear message.
    4. Snapshot working_dir file list (name + mtime + size) BEFORE run.
    5. Run twice via harness.runner.run_spec (configuration="correctness").
    6. Diff snapshot after each run. Candidate outputs = files that are new or mtime-changed AND NOT in spec.files.prompt_payload (those are inputs).
    7. Compute SHA-256 of each candidate output per run. Compare across run1 vs run2. On mismatch → emit a LOUD warning naming the non-deterministic file; recommend `oracle_strength: "weak"` + Threats note. Do NOT emit a file_hash suggestion for non-deterministic outputs.
    8. Print: run1 stdout (head+tail), run2 stdout (head+tail), candidate output list + SHA-256 per file, a ready-to-paste `verification.strategies` JSON snippet and `reference_files[]` snippet. No auto-edits to the spec — Samyak pastes manually.
    9. Underscore prefix on the filename = explicitly private. No argparse subcommands. No `--strategy` flag. No auto-suggestion logic beyond the paste snippet.
  Do NOT touch benchmark source. Do NOT write to specs/ or manifest.jsonl. Output goes to stdout only.

T1.6 — docs/design/spec_oracle_design.md (NEW FILE, ≤100 lines HARD CAP)
  Trimmed decision guide — not a full contributor rubric (paper Methodology covers the rest).
  Content:
    - 1-paragraph intro stating purpose: classify each spec into one of 5 buckets → pick recommended strategy.
    - 5-bucket decision tree:
        1. already-strong — stdout pattern gated by self-check (e.g., `if (correct) printf(...)`). Action: set oracle_strength="strong".
        2. strong-after-regex-tighten — existing pattern fires but is too loose; narrow to require numeric field. Action: 1-line spec edit.
        3. needs-file_hash — binary writes deterministic output file. Action: run _capture_baseline.py, commit reference, paste file_hash strategy.
        4. needs-numeric_comparison — binary prints timing-independent numeric stdout. Action: add extract_regex + expected + tolerance.
        5. truly-weak — no output file, no numeric stdout, no self-check, or non-deterministic. Action: oracle_strength="weak" + paper Threats note.
    - 1 worked example: bfs-omp (bucket 3 / needs-file_hash). Show the before/after verification JSON blocks + the reference_files entry + the terminal output from `_capture_baseline.py specs/rodinia-bfs-omp.json` that produced the SHA-256. Cite rodinia/rodinia-src/openmp/bfs source line for the print site.
    - Link to HANDOFF.md §4 (escape hatch: `scripts/spec_tools/postprocess_{kernel}.py` via custom_script — invoke only if buckets 3/4 infeasible).
  Keep under 100 lines. Use `wc -l` to verify before commit.

TDD discipline — ATOMIC. One failing test → one fix → verify GREEN → next. No batching.
  tests/test_capture_baseline.py covers:
    - snapshot-diff correctly identifies new output file (ignores prompt_payload files)
    - SHA-256 computed correctly on deterministic content
    - two-run mismatch warning fires with non-deterministic content (simulate by seeding file with time.time())
    - missing spec file raises clear error
    - BUILD_FAIL aborts with clear message
  Use pytest tmp_path. Mock harness.builder.build_spec + harness.runner.run_spec where needed — unit tests must not actually compile CUDA.

Pre-commit review team (mandatory, matches S1 pattern)
  After implementation and before commit: spawn `s2-review` via TeamCreate with 3 teammates — self-critic (Opus, ultrathink), code-reviewer (Opus, ultrathink), code-simplifier (Sonnet 4.6, high effort). All teammates invoke /caveman:caveman lite + /andrej-karpathy-skills:karpathy-guidelines. Cross-talk via SendMessage. Findings go to /tmp/s2-review/{self-critic,code-reviewer,code-simplifier}.md. Main session synthesizes, presents to user, awaits fix approval.

Then /superpowers:verification-before-completion, then /validate waves 1-3. Sentinel must be fresh before commit (single-use).

Commit message:
  feat(03-oracle): _capture_baseline.py private helper + trimmed oracle guide

Do NOT push. After commit, show the log summary and ask user to run `! git push origin main` themselves.

Invariants to preserve (verify in commit message):
  - manifest.jsonl untouched
  - benchmark source untouched
  - results/ untouched
  - schema/spec_schema.json untouched (S2 adds no schema fields)
  - Tests: 196 → 196+N (N = new capture_baseline tests)
  - 15 phantom-spec validator errors unchanged

Estimated effort: 3-4 hrs. Flag immediately if either artifact is trending toward double the time budget.
```
