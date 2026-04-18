# Session Handoff — Tier 1 Oracle Framework + Tier 2 Spec Upgrade — Before Phase 3 Launch

> **Multi-session campaign.** 7-9 sessions from 2026-04-18 to Phase 3 launch,
> then 3-5 wall-clock days for Phase 3 eval, then 3-5 days paper write. Each
> session below has independently closable entry/exit criteria — safe to pause
> and resume across calendar days.
>
> **Supersedes the post-A2+A4 handoff** (handoff version 2026-04-18 evening;
> 3 commits landed in the preceding fix series: `7b56b8d` A1, `c8316d9` C1-C4,
> `7facfc0` A2+A4).
>
> **Reviewed** by the `tier1-tier2-plan-review` team (plan-reviewer Opus +
> critic Opus + worker Sonnet, all ultrathink) on 2026-04-18. Review findings
> + convergence matrix captured in §12.

---

## 1. Campaign Goal

Every PASS in the Phase 3 Qwen + GPT-5.3-chat evaluation must be **semantically
gated** — i.e., the verdict reflects correctness of the LLM-translated kernel
output, not merely "binary exited and printed a literal string." This requires
two orthogonal bodies of work, done in order:

**Tier 1 — Oracle framework** (minimal, defensible, scoped to what the 88 specs need):
- Implement `numeric_comparison` and `file_hash` verifier strategies (currently TODO stubs in `harness/verifier.py`).
- Extend `schema/spec_schema.json` to declare strategy types + `oracle_strength` enum + `reference_files` block — **including explicit removal of `additionalProperties: false` on the `verification` block** so the new keys validate.
- Ship `scripts/spec_tools/capture_baseline.py` as a **private helper script** (used internally for S4-S5; no polished CLI).
- Author `docs/design/spec_oracle_design.md` as a **~100-line 2-page decision tree + 1 worked example**, not a full authoring rubric.

**Tier 2 — Spec upgrade** (data, in-place JSON edits on the 88 in-scope specs):
- Classify ALL 53 target specs (18 confirmed-weak Rodinia + 35 unknown) via source grep with 5-way classification: `strong` (preserve) / `regex-tighten` (literal-string patch) / `file_hash` (output-file SHA-256) / `numeric_comparison` (stdout capture group) / `post-processor` (Python custom_script).
- Per-spec **determinism pre-flight**: 2 baseline runs, byte-compare output file; if nondeterministic, `file_hash` is excluded → route to `numeric_comparison` or post-processor.
- Upgrade each weak spec using the strategy chosen in the audit.
- Store reference output files in `specs/references/` (in-repo for NeurIPS May 1 submission). Zenodo deposit deferred to camera-ready (post-May-1).
- Run `harness verify` full sweep — all 88 specs must PASS post-upgrade.

**Success criterion:** harness verify all 88 specs at L0, every spec passes, no spec's `verification.oracle_strength` is `"unknown"` or `"weak"` (except specs where the Threats section justifies weakness). Phase 3 eval launches from this state.

---

## 2. Current State (as of 2026-04-18, HEAD = `7facfc0`)

### Commits landed (this series)

| SHA | Description |
|---|---|
| `7b56b8d` | A1: `_load_complexity_lookup()` returns `None` when CSV missing |
| `c8316d9` | C1-C4: SHA-256 `_derive_llm_seed()` + `seed` + `top_p` kwargs in `call_llm` + all 6 provider branches + result JSON schema bump |
| `7facfc0` | A2+A4: per-cell `pass_at_1_mean` + `pass_at_1_of_any` + level-invariance scope note referencing L0-passer subset |

### Pending this campaign

| ID | Description | Session |
|---|---|---|
| T1.1 | Implement `numeric_comparison` verifier | S1 |
| T1.2 | Implement `file_hash` verifier | S1 |
| T1.3 | Extend spec schema: strategies enum + `oracle_strength` + `reference_files` + drop `additionalProperties:false` | S1 |
| T1.4 | Unit tests for new verifiers | S1 |
| T1.5 | `scripts/spec_tools/capture_baseline.py` — private helper (used S4-S5 only) | S2 |
| T1.6 | `docs/design/spec_oracle_design.md` — ~100 lines, decision tree + 1 worked example | S2 |
| T1.7 | `scripts/validate_schema.py` WARN on weak/unknown oracle_strength | S2 |
| T2.1 | Source-grep audit of 53 specs (18 weak + 35 unknown) → 5-way classification + determinism pre-flight | S3 |
| T2.2 | Upgrade Rodinia weak specs (batch a) | S4a |
| T2.3 | Upgrade Rodinia weak specs (batch b) + audit-identified weaks | S4b |
| T2.4 | Harness verify sweep — all 88 specs PASS | S5 |
| T2.5 | `specs/references/MANIFEST.md` + in-repo reference-file index | S5 |
| Phase 3 launch | Qwen canonical + ablation; GPT-5.3-chat canonical + ablation | S6+ |

### Deferred (explicit non-goals for this campaign)

- A3 (Clopper-Pearson CIs), A5 (paper Threats prose only), A6 (repair-loop tests)
- T1.8 (standalone MANIFEST index) — **CUT** per critic R1; replaced by a simple `specs/references/MANIFEST.md` populated in S5
- Zenodo deposit + DOI embed — **CUT from May 1 submission**; rescheduled to camera-ready post-May-1
- `specs/helpers/{kernel}/verify_{kernel}.c` C-escape-hatch — **CUT** per critic R6; Python `custom_script` strategy or Threats prose instead
- Polished `capture_baseline.py` CLI — **CUT**; tool stays private-helper, no documentation polish
- B4 BLOCK flip (from WARN) — separate post-campaign commit
- D1 unconditional probe + D2 kernel-selection — post-Phase-3 analysis
- Refactor `random.seed(42 + augment_level)` at `llm_evaluate.py:1501` — orthogonal follow-up

---

## 3. Hard Rules (Inviolable — Every Session)

These apply across every session in this campaign. No exceptions, no `--no-verify`.

1. **NEVER modify benchmark source code.** `.cu` / `.cpp` / `.cl` / `.c` / `.h` / `.hpp` / `.cuh` inside `rodinia/rodinia-src/`, `HeCBench-master/src/`, and the upstream trees of XSBench, RSBench, mixbench are read-only for this campaign.
2. **Makefile patches inside benchmark trees** are already tracked in `docs/rodinia_toolchain_patches.diff`; do not add new patches unless absolutely required, and if so, record in the patch file.
3. **NEVER modify `manifest.jsonl`** — append-only. Spec JSON edits happen in-place at the existing `unique_id` (no `-v2` suffix, no renaming). Old eval result JSONs continue to reference unchanged spec IDs.
4. **NEVER modify `results/`** — historical result JSONs are immutable.
5. **NEVER modify `.planning/phases/02-llm-eval-testing/02-0{1..9}-*.md`** historical plans — write-once.
6. **Reference output files** live in-repo under `specs/references/{suite}/{kernel}/` for the May 1 submission. Max ~50 MB total across all specs (compressed where possible). Zenodo DOI embed is a camera-ready task.
7. **Every session runs `/validate` waves 1-3** before commit. Pre-commit hook enforces.
8. **spec JSON mutations are per-suite batched.** One commit per suite (Rodinia / HeCBench / XSBench / RSBench / mixbench), not one commit per spec, to keep the diff reviewable.
9. **If a spec cannot be upgraded without touching benchmark source** (no output file, no numeric stdout, no self-check, determinism failure), it gets `oracle_strength: "weak"` + a paragraph in the paper Threats section. It is NOT silently shipped as passing.
10. **Before any irreversible / paid action** (Phase 3 launch, any reference file >10MB checked in), stop and ask user. No silent deposit.

---

## 4. The Benchmark-Code-vs-ParBench-Code Question (Answered)

**Benchmark code is NEVER modified.** All work in this campaign is in ParBench-framework files only:

### Files that MAY be modified

| Path | Purpose |
|---|---|
| `harness/verifier.py` | Implement new verifier strategies |
| `harness/models.py` | If new result fields required |
| `schema/spec_schema.json` | Schema extension for new strategies + oracle_strength; drop `additionalProperties:false` on the `verification` block |
| `scripts/spec_tools/capture_baseline.py` | NEW file — private helper for baseline capture during S4-S5 |
| `scripts/validate_schema.py` | Add WARN for weak/unknown oracle_strength |
| `specs/*.json` | In-place oracle upgrade (verification block + oracle_strength + reference_files) |
| `specs/references/{suite}/{kernel}/` | NEW directory — in-repo reference output files + SHA-256 manifest |
| `docs/design/spec_oracle_design.md` | NEW file — ~100-line decision tree + 1 worked example |
| `tests/test_*.py` | New unit tests |
| `.claude/rules/evaluation.md` | Document schema bump + new verifier semantics |
| `.planning/phases/03-oracle-framework/*.md` | NEW phase directory with plan + execution docs |

### Files that MUST NOT be modified

| Path | Rule |
|---|---|
| `rodinia/rodinia-src/**/*.cu`, `*.cpp`, `*.c`, `*.cl`, `*.h`, `*.hpp` | Benchmark source — read-only |
| `HeCBench-master/src/**/*.cu`, `*.cpp`, `*.c`, `*.cl`, `*.h`, `*.hpp` | Benchmark source — read-only |
| `manifest.jsonl` | Append-only; in-place spec edits preserve existing entries |
| `results/evaluation/**`, `results/augmentation/**` | Historical eval/aug JSONs — immutable |
| `.planning/phases/02-llm-eval-testing/02-0{1..9}-*.md` | Historical plans — write-once |

### How the oracle upgrade works without touching benchmark source

For a weak spec like `rodinia-bfs-omp` whose binary prints `"Result stored in result.txt"` unconditionally:

1. Baseline run captures `result.txt` (produced by the binary with known-good input).
2. Binary-determinism pre-flight: 2 baseline runs, byte-compare. If bit-identical → `file_hash` viable. If not → re-route to `numeric_comparison` or Python post-processor.
3. SHA-256 of `result.txt` stored in the spec: `verification.strategies: [{"type": "file_hash", "path": "result.txt", "expected_sha256": "abc123..."}]`.
4. Reference file committed to `specs/references/rodinia/bfs/graph1MW_6_result.txt`.
5. Harness runs the binary → `file_hash` verifier reads `result.txt` post-execution → SHA-256s it → compares to expected.
6. If LLM translation produces garbage `result.txt`, the hash differs → FAIL. Semantic gate achieved.
7. **Binary source was never touched.** We only post-process the file it produced.

For FP-heavy kernels where `file_hash` fails determinism pre-flight (srad, cfd, hotspot, lavamd — OMP reduction order varies):
- Route to `numeric_comparison` on a stdout capture group (final RMSE, iteration count, or reduction-invariant total).
- If no usable stdout number: Python post-processor in `scripts/spec_tools/postprocessors/{kernel}.py` reads the output file, computes an integer invariant, invoked via `custom_script` strategy.
- Last resort: spec flagged `oracle_strength: "weak"` + Threats-section justification.

---

## 5. Session Plan

Each session is an atomic unit: entry criteria → work → exit criteria + committed. Designed to fit a 4-10 hr block so one session closes cleanly per calendar day.

### Session S1 — Tier 1 Verifier Primitives + Schema (T1.1 + T1.2 + T1.3 + T1.4)

**Entry criteria**
- On `main` at HEAD `7facfc0` (or descendant)
- Clean working tree (or only carrying known unstaged `.claude/settings.json` + `.planning/HANDOFF.md`)
- Baseline `pytest -m "not llm and not integration"` passes (305 expected)

**Work**
1. Extend `harness/verifier.py`:
   - `_verify_numeric_comparison(run_result, strategy)` — regex-extract stdout capture group, parse float, compare to `expected` within `tolerance` (default `0.0`).
   - `_verify_file_hash(run_result, strategy, working_dir)` — read `working_dir / strategy.path`, SHA-256, compare to `strategy.expected_sha256`. FAIL if file missing.
2. Extend `schema/spec_schema.json`:
   - **Drop `additionalProperties: false` from the `verification` object** (currently at `:451`) OR whitelist the new keys — confirm the exact schema delta by reading the file first, don't guess.
   - Add `numeric_comparison` and `file_hash` enum values to `verification.strategies[].type`.
   - Per-type required fields:
     - `numeric_comparison`: `extract_regex`, `expected`, optional `tolerance` (default `0.0`), optional `description`.
     - `file_hash`: `path`, `expected_sha256`, optional `description`, optional `reference_url` (for future Zenodo).
   - Add top-level `verification.oracle_strength: enum ["strong", "medium", "weak", "unknown"]` with default `"unknown"`.
   - Add top-level `verification.reference_files: [{path, sha256, size_bytes}]` optional array.
3. Unit tests in `tests/test_verifier_numeric_comparison.py` + `tests/test_verifier_file_hash.py`:
   - `numeric_comparison`: in-tolerance → PASS; out-of-tolerance → FAIL; regex miss → FAIL; unparseable capture → FAIL.
   - `file_hash`: correct SHA → PASS; wrong SHA → FAIL; missing file → FAIL.
4. Update `.claude/rules/evaluation.md` verifier section to document the 2 new strategies + `oracle_strength` semantics.

**Exit criteria**
- 1 commit: `feat(03-oracle): Tier 1 numeric_comparison + file_hash verifiers + schema v1.1`
- Unit tests pass; new verifier types callable from spec JSON
- Existing `python3 scripts/validate_schema.py --all` still within known-errors threshold (~15 phantoms)
- `/validate` waves 1-3 PASS

**Estimated effort: 5-7 hrs.** (Raised from 4-6 to account for the additionalProperties schema work flagged by plan-reviewer.)

---

### Session S2 — Tier 1 Baseline Helper + Compact Authoring Guide (T1.5 + T1.6 + T1.7)

**Entry criteria**
- S1 commit landed
- New verifier strategies are callable from spec JSON

**Work**
1. `scripts/spec_tools/capture_baseline.py` (private helper, no CLI polish):
   - Input: spec file path.
   - Runs build + correctness config.
   - Captures stdout + enumerates output files in the resolved working dir.
   - For each output file: runs the binary a second time, byte-compares → determinism flag.
   - For each candidate file: computes SHA-256 + size.
   - For stdout: scans for numeric capture-group candidates (e.g., lines with `\d+`).
   - Emits a suggested `verification.strategies` block to stdout for paste-in.
   - Output JSON skeleton ready-to-edit.
2. `scripts/validate_schema.py`:
   - Add WARN (non-blocking) when `verification.oracle_strength` is `"unknown"` or `"weak"`.
   - Print summary: `X specs strong, Y medium, Z weak, W unknown`.
3. `docs/design/spec_oracle_design.md`:
   - ~80-120 lines total.
   - Decision tree: "output file?" → "deterministic?" → `file_hash`; else → "numeric stdout invariant?" → `numeric_comparison`; else → post-processor or `weak` with Threats prose.
   - 1 worked example: `rodinia-bfs-omp` before + after upgrade.

**Exit criteria**
- 1 commit: `feat(03-oracle): Tier 1 capture_baseline helper + authoring decision-tree + validator WARN`
- Running `python3 scripts/spec_tools/capture_baseline.py specs/rodinia-bfs-omp.json` prints a valid suggested `verification` block.
- `python3 scripts/validate_schema.py --all` prints the oracle_strength summary.
- `/validate` waves 1-3 PASS.

**Estimated effort: 3-4 hrs.** (Reduced from 4-6 by dropping polished CLI + full rubric + MANIFEST index.)

---

### Session S3 — Tier 2 Audit of ALL 53 Specs (T2.1) — 5-way Classification + Determinism Pre-flight

**Entry criteria**
- S1 commit landed (verifier names finalized so audit can cite them)
- S2 commit landed (capture_baseline helper available for determinism pre-flight)

**Work**
- For each of the **53 target specs** (18 Rodinia-weak + 35 unknown, per `/tmp/b1_inscope.log`):
  1. Read current `verification.strategies` + source print-site.
  2. Run `capture_baseline.py` to identify output files + stdout numeric candidates.
  3. Binary-determinism pre-flight: 2 baseline runs, byte-compare.
  4. Classify 5-way:
     - **`strong`** — current regex is already semantic-gated (e.g., HeCBench `PASS`/`FAIL` self-check). Preserve as-is; annotate `oracle_strength: "strong"`.
     - **`regex-tighten`** — current regex is loose but a tighter regex (e.g., matching a numeric format) would be semantic. Upgrade pattern in place.
     - **`file_hash`** — output file is deterministic; upgrade to SHA-256 match.
     - **`numeric_comparison`** — stdout has a correctness-carrying number; upgrade to capture-group extraction + tolerance.
     - **`post-processor`** — output needs transformation (FP-tolerance, sort, etc.); author Python post-processor.
- Record in `.planning/phases/03-oracle-framework/03-B1-AUDIT.md`:
  - Per-spec row: `spec_id | current_pattern | source_line_evidence | classification | determinism | recommended_strategy | estimated_fix_time`
  - Summary counts by classification.
  - Prioritized fix list grouped by strategy (batch similar fixes in S4a/S4b).

**Exit criteria**
- 1 commit: `docs(03-oracle): B1 audit — 53 specs classified 5-way with determinism pre-flight`
- `.planning/phases/03-oracle-framework/03-B1-AUDIT.md` complete.
- `/validate` waves 1-3 PASS (docs-only ~90s).

**Estimated effort: 4-6 hrs.** (Was 2-3 for 35 specs; bumped to 53 specs + 5-way classification + determinism pre-flight per plan-reviewer R3 and critic R7.)

---

### Session S4a — Tier 2 Rodinia File-Hash + Regex-Tighten Upgrades (T2.2)

**Entry criteria**
- S3 audit committed
- User sign-off on the audit matrix (per §7 Parallel Tasks — Samyak reviews 03-B1-AUDIT.md before S4 begins)

**Work**
- Fix all Rodinia specs that the audit classifies as `file_hash` or `regex-tighten` (the quicker fixes — estimated 10-12 specs).
- Per spec:
  1. Run `capture_baseline.py` → get suggested block.
  2. Edit spec JSON in place — add new strategy, set `oracle_strength: "strong"`, add `reference_files` entry.
  3. For `file_hash`: commit reference file to `specs/references/rodinia/{kernel}/`.
  4. Run `python3 -m harness verify` on the spec with its new oracle → must PASS.
  5. If FAIL: diagnose; fall back to `numeric_comparison` OR defer to S4b post-processor track.
- Commits: 1-2 per batch of 5-6 specs, grouped by strategy (file_hash batch, regex-tighten batch).

**Exit criteria**
- All audit-classified file_hash and regex-tighten Rodinia specs upgraded.
- Reference files committed in-repo.
- Every touched spec passes harness verify.
- 2-3 commits landed.

**Estimated effort: 8-10 hrs.** (Was 5-7 hrs for 18 specs @ 20-30 min; bumped to 45-60 min per spec per plan-reviewer R2; S4a covers ~10-12 specs only.)

---

### Session S4b — Tier 2 numeric_comparison + post-processor Upgrades (T2.3)

**Entry criteria**
- S4a commits landed
- Remaining specs (from S3 audit) are those classified `numeric_comparison` or `post-processor` — the harder fixes

**Work**
- Fix the ~20-25 remaining specs. These typically need:
  - Stdout capture-group regex design (per-kernel)
  - Tolerance value justification (FP noise bounds)
  - Python post-processor (`scripts/spec_tools/postprocessors/{kernel}.py`) when neither stdout nor bit-identical output file works
- Per spec:
  1. `capture_baseline.py` for stdout candidates.
  2. Design regex + tolerance; cite physics/math rationale in spec `description` field.
  3. If post-processor needed: author Python script; invoke via `custom_script` strategy (extend `harness/verifier.py` with a minimal `custom_script` strategy — scoped ADD in S4b if not in S1).
  4. Verify with harness.
- Per-suite batching: Rodinia remainder, HeCBench md-{cuda,omp_target}, mixbench 3 specs.

**Exit criteria**
- All 53 in-scope specs have `oracle_strength` ∈ {"strong", "medium"} OR are explicitly documented as `"weak"` with Threats prose justification.
- 2-3 commits landed.
- Every touched spec passes harness verify.

**Estimated effort: 8-10 hrs.**

---

### Session S5 — Full-Sweep Verify + In-repo Reference Index (T2.4 + T2.5)

**Entry criteria**
- S4a + S4b complete
- All 53 target specs upgraded or explicitly-weak-and-justified

**Work**
1. Run `python3 -m harness verify --all-suites` (or scripted equivalent across 88 non-KF specs) → all must PASS.
2. Build `specs/references/MANIFEST.md` — flat index of all checked-in reference files:
   - Per-row: `spec_id | path | sha256 | size_bytes`
   - Include total size (must be ≤50 MB per §3 Rule 6).
3. Update `.claude/rules/known-issues.md` current-spec-status block with the post-upgrade oracle_strength distribution.
4. If total references exceed 50MB: flag largest files for git-lfs OR compression OR post-processor invariant instead of file storage.

**Exit criteria**
- 88/88 non-KF specs PASS harness verify.
- `specs/references/MANIFEST.md` populated.
- `known-issues.md` updated.
- 1-2 commits landed.
- `/validate` waves 1-3 PASS.

**Estimated effort: 3-4 hrs.**

---

### Session S6 — Phase 3 Launch Prep (pre-flight)

**Entry criteria**
- S5 complete. All 88 specs pass harness verify. Reference files in-repo.
- Samyak has `gpt-5.3-chat` deployed on Azure (parallel user track — see §7).

**Work**
1. Dry-run smoke: 1-sample `--dry-run` of each (source, target, model) combo for Phase 3 task list.
2. 3-kernel live test: 3 canonical samples on 3 representative kernels (bezier, bfs, srad) against `together-qwen-3.5-397b-a17b` and `azure-gpt-5.3-chat`, run in a tmp project-root via `stage_tmp_project_root` fixture.
3. Confirm: `seed` + `top_p` present in result JSONs; new oracles fire correctly; PASS rates align with stronger-oracle expectations (bfs-omp may no longer show 3/3 — any outcome is valid, just document).
4. Docs: update `.planning/HANDOFF.md` with Phase 3 launch-ready state + final budget estimate.

**Exit criteria**
- Phase 3 command is ready to paste-and-run.
- 1 commit (docs update + launch manifest).
- `/validate` waves 1-3 PASS.
- User has clear go/no-go call.

**Estimated effort: 2-3 hrs (mostly API wait time).**

---

### Session S7-S9 — Phase 3 Eval (user-driven, wall-clock)

Compute sessions, not engineering. Run tmux. Samyak launches, Claude monitors passively.

**S7:** Qwen canonical (3 samples × all kernels × direction matrix). ~12-20 hrs wall-clock, ~$400-600 API.

**S8:** Qwen L0-conditional ablation. ~6-10 hrs, ~$100-200.

**S9:** Azure GPT-5.3-chat canonical + ablation. ~24-36 hrs, ~$300-500.

All three use `run_eval_batch.py --resume` so restarts are cheap.

---

### Session S10 — Paper Write (user-driven)

- Oracle methodology section grounded in `docs/design/spec_oracle_design.md`
- Results tables from `analyze_eval.py` output with both pass@1 metrics
- Threats section update grounded in `02-THREATS-TO-VALIDITY.md`
- In-repo reference-file index cited (Zenodo DOI in camera-ready)

**Estimated effort: 10-15 hrs over 3-5 days.**

---

## 6. Timeline — NeurIPS May 1, 2026 (13 days from 2026-04-18)

Post-review hour totals: **Tier 1 ~8-11 hrs, Tier 2 audit+upgrade ~20-26 hrs, full-sweep+launch-prep ~5-7 hrs = 33-44 engineering-hrs over ~7-9 Claude sessions.**

| Day | Session(s) | Owner | Outcome |
|---|---|---|---|
| D1 (Apr 18 tonight) | S1 | Claude | Verifier primitives + schema v1.1 committed |
| D2 (Apr 19) | S2 | Claude | Baseline helper + compact authoring guide + validator WARN |
| D3 (Apr 20) | S3 | Claude | B1 audit committed (53 specs 5-way + determinism) |
| D4 (Apr 21) | S4a | Claude | Rodinia file_hash + regex-tighten upgrades |
| D5 (Apr 22) | S4b | Claude | numeric_comparison + post-processor upgrades |
| D6 (Apr 23) | S5 + buffer | Claude | Full-sweep verify, MANIFEST, known-issues update |
| D7 (Apr 24) | S6 | Claude | Phase 3 pre-flight green |
| D8 (Apr 25) | S7 start | Samyak (tmux overnight) | Qwen canonical running |
| D9 (Apr 26) | S7 finish + S8 | Samyak | Qwen complete |
| D10 (Apr 27) | S9 | Samyak (tmux) | GPT-5.3-chat launching |
| D11 (Apr 28) | S9 finish + analyze_eval | Samyak | All eval runs done; tables ready |
| D12 (Apr 29) | S10 | Samyak + Gal | Paper draft |
| D13 (Apr 30) | S10 final polish | Samyak + Gal | Submit |
| **D14 (May 1)** | — | — | **NeurIPS deadline** |

**Slack markers:**
- D6 includes a buffer if S5 runs short.
- D4-D5 can compress if S3 audit surfaces easy fixes.
- D11 can compress if Phase 3 eval finishes faster (Qwen TPM quota allowing).
- **Risk flag:** if S3 audit reveals >5 specs need post-processors, S4b may expand to S4c (+1 day); D9 reserved as fallback.

---

## 7. User Parallel Tasks (START TODAY — Do Not Wait for Claude)

These block Phase 3 launch but are not on Claude's critical path. Samyak starts these IMMEDIATELY on Day 1:

| Task | Blocks | Est. effort |
|---|---|---|
| Deploy `gpt-5.3-chat` in Azure; confirm `AZURE_OPENAI_ENDPOINT` URL resolves (current points to `gpt-4.1`, returns 404 for 5.3-chat) | S6, S9 | 30 min - 2 hrs (depends on Azure quota approval) |
| Review + sign-off on S3 B1 audit document before S4a batch upgrades begin | S4a | 30 min |
| Sign off on Phase 3 go/no-go after S6 | S7 | 15 min |
| (Deferred to post-May-1 camera-ready) Zenodo account + draft deposit for "ParBench reference outputs v1" | camera-ready | 10 min |

---

## 8. Hard Constraints Summary (cross-reference)

- Memory `feedback_never_touch_benchmark_source`: respected throughout (§3 Rule 1, §4 table).
- Memory `feedback_protect_qwen_results` + `feedback_protect_cuda_omp_results`: respected (§3 Rule 4).
- Memory `feedback_extensible_pipeline`: Tier 1 delivers 2 new verifier primitives + schema extension + a private helper — sufficient for the 88 specs in scope. The "authoring guide for future contributors" is a 2-page decision tree, not a polished rubric, per critic R1.
- Memory `feedback_no_primary_benchmark`: all 5 suites treated equally.
- Memory `feedback_critic_loop`: this handoff was reviewed by a 3-person plan-review team before finalization (§11 + §12).
- Memory `feedback_plan_review_team`: applied — plan-reviewer + critic + worker team reviewed with cross-talk.
- CLAUDE.md invariant 1 (manifest append-only): respected (§3 Rule 3).
- CLAUDE.md invariant 6 (KNOWN_FAIL exclusion): respected — 8 KNOWN_FAIL specs are NOT upgraded.
- CLAUDE.md `ultrathink` trigger for architecture decisions: applied to this handoff.

---

## 9. How to Resume — Per Session

Every session starts with the same entry command:

```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
git status   # confirm clean working tree OR acknowledge carried .claude/settings.json + HANDOFF.md diffs
git log --oneline HEAD~5..HEAD   # confirm you are at expected HEAD for this session
python3 -m pytest -m "not llm and not integration" -q | tail -1   # baseline pass count
```

Per-session entry criteria are in §5. If entry criteria not met, STOP and escalate to user.

---

## 10. What NOT to Do (explicit non-goals)

| Item | Why excluded |
|---|---|
| Rebuild spec corpus from scratch with v2 unique_ids | User chose `fix-in-place` — less risk, preserves 35 already-strong specs, no manifest churn |
| Touch benchmark source to add `printf("PASS")` | Inviolable — §3 Rule 1 + memory `feedback_never_touch_benchmark_source` |
| Commit reference binary blobs >10MB to git | git-lfs or compression first; §3 Rule 10 |
| Upgrade HeCBench-curated specs that already use `PASS`/`FAIL` semantic gates | 21 of 23 are already strong; no change |
| Zenodo deposit for May 1 submission | Deferred to camera-ready (critic R3) |
| Polished contributor CLI for `capture_baseline.py` | Private helper only (critic R1) |
| C post-processors under `specs/helpers/{kernel}/verify_{kernel}.c` | Python post-processor via `custom_script` strategy instead (critic R6) |
| Promote `oracle_strength` BLOCK (from WARN) in validator | Separate post-campaign commit, after audit stabilizes |
| Run D1 unconditional probe or D2 kernel-selection | Post-Phase-3 analysis |
| Refactor `random.seed(42 + augment_level)` at `llm_evaluate.py:1501` | Orthogonal follow-up session |

---

## 11. Provenance

- Plan drafted 2026-04-18 after the A1/C1-C4/A2+A4 fix series landed (commits `7b56b8d`, `c8316d9`, `7facfc0`).
- Reviewed 2026-04-18 by the `tier1-tier2-plan-review` team:
  - **plan-reviewer** (Opus, ultrathink) — systemic review, identified 3 🔴 critical + 4 🟡 medium findings. Delivered inline via team messages per "no findings.md" rule.
  - **critic** (Opus, ultrathink) — anti-rationalization review, identified 3 🔴 scope-cut recommendations + 4 secondary. Written to `/tmp/critic-findings.md` (237 lines).
  - **worker** (Sonnet, ultrathink) — designated synthesizer. Went idle mid-synthesis; team-lead completed synthesis directly from cross-talk findings.
  - Cross-talk convergence: plan-reviewer and critic accepted each other's R1+R3+R4+R7; diverged on R6 (critic won — C-escape-hatch deleted).
- Draft: `/tmp/tier1-tier2-DRAFT.md` (pre-review version).
- Final: `.planning/HANDOFF.md` (this file, post team review).
- Review memory: `feedback_plan_review_team.md` (plan-review team required for non-trivial plans).

---

## 12. Review Log — Adopted / Deferred / Rejected

### Adopted changes (integrated into §5 Session Plan + §6 Timeline)

- **R-🔴-1 (plan-reviewer) ADOPT:** Explicit schema `additionalProperties:false` fix in S1. Verification block at `schema/spec_schema.json:451` currently prohibits new keys. Every S4 spec edit would fail without this. Rationale: non-negotiable ordering dependency.
- **R-🔴-2 (plan-reviewer) ADOPT:** S4 timeline rebudgeted to 12-18 hrs (was 5-7) split into S4a + S4b. Per-spec realistic 45-90 min. Rationale: evidence-based timing from grep-triage spot-check.
- **R-🔴-3 (plan-reviewer) ADOPT:** Per-spec strategy triage moved from S4 to S3. S3 scope expanded from 35 to all 53 specs (18 + 35). Determinism pre-flight added to S3. Rationale: FP-nondeterministic Rodinia kernels need strategy classification before S4 bulk edits.
- **R-🟡-4 (plan-reviewer) PARTIAL ADOPT:** S2/S3 parallel ordering risk — resolved by making S3 sequential on S2 (was drafted as parallel). S3 now uses the S2 `capture_baseline.py` for determinism pre-flight.
- **R-🟡-5 (plan-reviewer) ADOPT:** `capture_baseline.py` specification strengthened — per-spec determinism flag + output-file enumeration + stdout numeric-candidate scan called out explicitly in §5 S2.
- **C-🔴-1 (critic) ADOPT:** Drop T1.8 (MANIFEST index as standalone deliverable). Keep `specs/references/MANIFEST.md` as a lightweight index populated in S5 — no standalone framework tooling. Trim T1.6 authoring guide to ~100 lines. Keep T1.5 as private helper, no CLI polish. Rationale: NeurIPS May 1 deadline; scope cut aligns with Karpathy simplicity-first.
- **C-🔴-3 (critic) ADOPT:** Zenodo deposit deferred to camera-ready. In-repo `specs/references/` sufficient for May 1 submission. Rationale: deletes Samyak-coordination blocker; camera-ready allows time for DOI workflow.
- **C-R5 (critic) ADOPT:** Binary-determinism pre-flight added to S3 per-spec workflow.
- **C-R6 (critic) ADOPT:** C-escape-hatch (`specs/helpers/{kernel}/verify_{kernel}.c`) deleted. Python post-processors via `custom_script` strategy instead. Rationale: YAGNI; Python is simpler per Karpathy.
- **C-R7 (critic) ADOPT:** Audit is 5-way classification (strong / regex-tighten / file_hash / numeric_comparison / post-processor), not 3-way. Rationale: "regex-tighten" bucket is a real quick-win category for specs where the existing pattern is almost-strong.
- **C-R11 (critic) ADOPT:** Scope cuts net ~25% time reduction; freed buffer redirected to S3 expansion + S4 per-spec realistic timing. Campaign total stays within 13-day window.

### Rejected changes (with rationale)

- **C-🔴-2 (critic) REJECT:** "Build `numeric_comparison` only if 3+ specs need it; ship single-strategy and be honest." Rationale: FP-heavy Rodinia specs (srad, cfd, hotspot, lavamd) per plan-reviewer R3 will fail `file_hash` determinism pre-flight. If those route to `numeric_comparison`, we need it from the start. Implementation cost is small (~3 hrs in S1). Deferring it would force S1/S4 re-work if S3 audit shows need. Net: build both strategies in S1.
- **R-🟡-6 (plan-reviewer) REJECT for this campaign, DEFER to follow-up:** Manifest+result immutability collision — concern that upgraded oracles "change the question measured." Rationale: in-place spec mutation preserves `unique_id`; old eval result JSONs remain valid historical artifacts (they measured the old oracle); new eval runs produce new result JSONs measuring the new oracle. No collision. A paper-prose note in Threats covers it. No structural change needed.

### Deferred (post-May-1 / post-campaign)

- Zenodo DOI deposit + embed → camera-ready.
- B4 oracle-strength BLOCK flip → post-audit-stabilization commit.
- Polished contributor CLI + full authoring rubric → post-paper open-source push.
- D1 unconditional probe + D2 kernel-selection grid → post-Phase-3 analysis.
- Refactor `random.seed(42 + augment_level)` → orthogonal follow-up session.

---

**End of handoff.** Next session: S1. Entry conditions at top of §5 S1.
