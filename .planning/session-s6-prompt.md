# Session S6 Execution Prompt — Harness Verify Full Sweep (T2.3)

> Paste the code block below into a fresh Claude Code session. S6 runs in isolation from S4b's context.

---

```
ultrathink. /caveman:caveman lite /andrej-karpathy-skills:karpathy-guidelines /session-start

Execute Session S6 of the Tier 1 Oracle Framework + Tier 2 Spec Upgrade campaign. Read .planning/HANDOFF.md §5 (Session S6) and §3 (Hard Rules) before touching any file. S5 + S4a + S4b are landed. Oracle strength distribution: 14 strong / 1 medium / 38 weak / 0 unknown / 153 missing (HeCBench bulk + remainder; S6 tags those during the sweep).

Entry check (run first, stop if any fails):
  source env_parbench/bin/activate && cd /home/samyak/Desktop/parbench_sam
  git log --oneline HEAD~5..HEAD                              # expect 6b790da at HEAD
  python3 -m pytest harness/ tests/ -m "not llm and not integration" -q | tail -3   # expect 217 passed, 3 skipped
  python3 scripts/validate_schema.py --all 2>&1 | grep -E "error\(s\)|oracle_strength:" | tail -3   # expect 15 errors

Hard rules (HANDOFF §3 — inviolable):
- NEVER touch benchmark source (rodinia/rodinia-src, HeCBench-master, XSBench, RSBench, mixbench).
- NEVER modify manifest.jsonl (append-only).
- NEVER modify results/.
- NEVER modify historical plans (.planning/phases/02-llm-eval-testing/02-0[1-9]-*.md).
- Rule 12: file_hash determinism is campaign-wide. If a sweep regression surfaces a non-deterministic file_hash spec, downgrade to oracle_strength="weak" with Threats note — do NOT mask the failure.
- git push origin main is Bash-blocked; ask user to run `! git push origin main` after all work lands.

T2.3 — scripts/spec_tools/run_verify_sweep.py (NEW FILE, ~30-40 lines)
  Purpose: invoke `harness verify --config correctness` on every non-KNOWN_FAIL spec; collect PASS/FAIL summary; emit non-zero exit on regression.
  Behavior:
    1. Load KNOWN_FAIL list — single source of truth is .claude/rules/known-issues.md table (8 entries: rodinia-{kmeans,mummergpu,hybridsort}-cuda, rodinia-mummergpu-omp, rodinia-{nn,kmeans}-opencl, hecbench-stencil1d-omp_target, hecbench-scan-omp_target). Hard-code the set in the script with a citation comment pointing at known-issues.md so successors can see drift.
    2. Glob specs/*.json. Filter out KNOWN_FAIL set. Expect 88 specs (206 total - 8 KNOWN_FAIL - 110 omp_target/sycl variants etc; verify count matches HANDOFF claim and STOP if not).
    3. For each spec, invoke `python3 -m harness verify --config correctness <path>` via subprocess. Capture stdout last line (verdict line). Time per-spec.
    4. Print compact table: spec | BUILD | RUN | VERIFY | total_s. PASS count, FAIL count.
    5. Exit non-zero if any non-KNOWN_FAIL spec fails. Emit FAIL details to stderr.
  Args: --project-root (required, matches HANDOFF convention), --exclude-known-fail (default True, no-op flag for clarity), --jobs N (parallelism; default 1 for safety — concurrent nvcc compiles can OOM).
  Do NOT touch benchmark source. Do NOT write to specs/. Do NOT mutate manifest.

S4b-REVIEW FOLLOWUP (F2 — bptree-cuda audit miss):
  s4b-review (2026-04-19) flagged that `rodinia-bptree-cuda` was S3-audit-classified as bucket5 (weak), but the source actually writes a deterministic `output.txt`: `rodinia/rodinia-src/cuda/b+tree/main.c:1881` defines `output="output.txt"`; `:1956` opens it `w+`; `:2221` appends per-`k` query results. Default `command.txt` runs `j 6000 3000` then `k 10000` → 10000 deterministic query results written. During the sweep, run a 2-run determinism pre-flight on bptree-cuda's `output.txt`. If bit-identical and ≤1 MiB → upgrade to `file_hash` (commit reference to `specs/references/bptree/cuda_output.txt`, set `oracle_strength="strong"`). Same check applies to `bptree-omp` (likely shares the write path). If non-deterministic → leave as weak + retain Threats note. This is an audit-error remediation, NOT a regression in S4b. If S6 also bypasses this, bptree must be explicitly disclosed in the paper Threats section as a "could-have-been-strong" weak spec.

T2.3 sweep execution
  Run: `python3 scripts/spec_tools/run_verify_sweep.py --project-root /home/samyak/Desktop/parbench_sam --exclude-known-fail`
  Expected: 88/88 PASS. Any FAIL = regression — STOP and triage before proceeding.
  Time budget: ~30-60 min wall-clock (most specs build+run+verify in <10s; XSBench CUDA ~22s; bptree-cuda ~2s build).
  Run in tmux per memory feedback_use_tmux. Capture full stdout/stderr to .planning/phases/03-oracle-framework/03-S6-SWEEP.log (gitignored or committed at session author's discretion).

S6 wrap-up — known-issues.md update + oracle_strength summary tag
  After sweep PASSes 88/88:
  1. Update .claude/rules/known-issues.md "Current Spec Status" block with the post-S5+S4a+S4b oracle distribution (14 strong / 1 medium / 38 weak / 0 unknown / 153 missing).
  2. Confirm via `python3 scripts/validate_schema.py --all 2>&1 | grep oracle_strength` that NO spec has `oracle_strength: "unknown"`. Zero unknowns is a hard exit criterion.
  3. The 153 "missing" specs are HeCBench bulk + variants not in the 53-spec audit scope. They are NOT failures — they have NO oracle_strength field at all. Future S6.5 (post-NeurIPS) can bulk-tag them. Document this in the known-issues.md update.

Pre-commit review team (mandatory, matches S1/S2/S5 pattern)
  After implementation and before commit: spawn `s6-review` via TeamCreate with 3 teammates — self-critic (Opus, ultrathink), code-reviewer (Opus, ultrathink), code-simplifier (Sonnet 4.6, high effort). All teammates invoke /caveman:caveman lite + /andrej-karpathy-skills:karpathy-guidelines. Cross-talk via SendMessage. Findings go to /tmp/s6-review/{self-critic,code-reviewer,code-simplifier}.md. Main session synthesizes, presents to user, awaits fix approval.

Then /superpowers:verification-before-completion, then /validate waves 1-3. Sentinel must be fresh before commit (single-use).

Commits (1-2 per HANDOFF Rule 8):
  1. feat(03-oracle): S6 — run_verify_sweep.py + 88/88 non-KNOWN_FAIL PASS
  2. docs(03-oracle): known-issues.md — post-S5+S4a+S4b oracle distribution + S6 sweep summary

Do NOT push. After commits, show the log summary and ask user to run `! git push origin main` themselves.

Post-commit: update HANDOFF.md §2 (mark T2.3 ✓ DONE, add S6 commit SHAs, bump HEAD ref). Chore commit: `chore(docs): HANDOFF — mark S6 complete (T2.3, 88/88 sweep PASS)`.

Then invoke /handoff for S7 (Phase 3 launch prep — pre-flight smoke test on 10 representative combos).

Invariants to preserve (verify in commit message):
  - manifest.jsonl untouched
  - benchmark source untouched
  - results/ untouched
  - schema/spec_schema.json untouched (S6 adds no schema fields)
  - Tests: 217 → 217 (S6 adds no unit tests; sweep IS the test)
  - 15 phantom-spec validator errors unchanged
  - Zero `oracle_strength: "unknown"` specs (hard exit criterion)

Estimated effort: 2-3 hrs (HANDOFF estimate). Sweep itself is the long pole; script is ~30 LoC.
```
