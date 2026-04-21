# S5 Review — Adversarial Post-Landing Audit (Round 1)

Review of S5 commits `d29d187..02868e8` by team `s5-review` (advisor + s5-self-critic + s5-code-reviewer, all Opus ultrathink). Two fix commits landed:

- `0adea0c` — s5-self-critic — `_resolved` threading in 2 verify_run callers + strengthened contract test + cli smoke test
- `f814a72` — s5-code-reviewer — bucket2 regex tighten across 5 specs (hotspot3d×3 + md×2) + new `-nan` regression test

---

## s5-self-critic section

### Methodology

Invoked `andrej-karpathy-skills:karpathy-guidelines`, `superpowers:verification-before-completion`,
`superpowers:test-driven-development` before the first tool call. Read HANDOFF.md §1-§12
(HANDOFF.md was the live tracker at S5 time; deleted post-S7c during the pre-Phase-3 cleanup
on 2026-04-20), CLAUDE.md invariants, `known-issues.md` current guardrails, 03-B1-AUDIT.md,
and the full diff/commit-body of all 5 S5 commits. Did NOT trust commit-message claims —
re-ran every verification command fresh in the review session.

### Round-1 evidence (fresh runs)

**Reference-file integrity (Batch 1 file_hash):**
```
$ sha256sum specs/references/myocyte/{cuda,opencl}_output.txt
1e329f029af6524ec9cf589852b560c39c03f9d3badebab7f146fc9b9d7ead05  cuda_output.txt
59efddcb7914a312d4de57cf1ee30cfaad9ef9457afac70f099fb3d60457e40c  opencl_output.txt
```
Both match spec `expected_sha256` byte-for-byte. A third independent `harness run` of
myocyte-cuda reproduced `1e329f02...ead05` — determinism beyond the 2-run pre-flight required
by HANDOFF §3 Rule 12.

**End-to-end `harness verify` on all 8 strategy-upgraded specs:** all PASS.
```
myocyte-cuda     | VERIFY: PASS (file_hash+exit_code)
myocyte-opencl   | VERIFY: PASS (file_hash+exit_code)
nn-cuda          | VERIFY: PASS (stdout_pattern+numeric_comparison+exit_code)
hotspot3d-cuda   | VERIFY: PASS (stdout_pattern+exit_code)
hotspot3d-omp    | VERIFY: PASS (stdout_pattern+exit_code)
hotspot3d-opencl | VERIFY: PASS (stdout_pattern+exit_code)
md-cuda          | VERIFY: PASS (stdout_pattern+exit_code)
md-omp_target    | VERIFY: PASS (stdout_pattern+exit_code)
```

**myocyte-omp BUILD_FAIL reproducibility:** confirmed
`main.c:1374` — `kernel_fin` called with 4 type errors + too few arguments. Weak-tag
(Batch 4) is the correct call under HANDOFF §3 Rule 12 (can't determinism-preflight an
unbuildable binary) and Rule 1 (benchmark source read-only).

**FAIL probes (Python-level, against live spec JSONs):**

| Probe | Spec | Result |
|---|---|---|
| `Distance=99.99` (wrong value) | nn-cuda | FAIL (numeric_comparison > tol) |
| empty stdout | nn-cuda | FAIL (sentinel missing) |
| `Accuracy:` bare literal | hotspot3d-cuda | FAIL (regex requires digit tail) |
| zeroed `expected_sha256` | myocyte-cuda | FAIL (file_hash mismatch) |

**Test + schema sweep:**
- `pytest tests/ harness/ -m "not llm and not integration" -q` → 212 passed / 3 skipped / 0 failed (post-commit A).
- `python3 scripts/validate_schema.py --all` → 15 baseline phantom errors, unchanged.
- `tests/test_regex_combiner_integration.py` → 41 passed (confirms nn-cuda sentinel restore preserved cross-API verify).

### Round-1 findings

| ID | Severity | Summary | Resolution |
|---|---|---|---|
| BLOCK-1 | BLOCK | `llm_evaluate.py:1821` + `reverify_pass_results.py:214` use `target_spec_resolved["working_dir"]` — KeyError at runtime because `resolve_paths()` returns `_resolved` sub-dict. Grep-only contract test missed it. | Fixed in `0adea0c` (self-critic): 2-line fix + whitelist regex in contract test + new parametrized functional test at `tests/test_verify_run_working_dir_resolution.py`. TDD red/green cycle verified. |
| FLAG-1 | FLAG | hotspot3d×3 + md×2 regex `[0-9.eE+-]+` admits `-nan` false-PASS (captures bare `-`, stdout_pattern doesn't float-parse). | Assigned to code-reviewer Commit B. |
| FLAG-2 | FLAG | `oracle_strength=strong` overstates given FLAG-1. | Resolved-by-fixing-FLAG-1. No relabel needed after tighten. |
| ADV-1 | advisory | Batch 4 spot-check 6/27 specs. | Pure-additive metadata, no semantic risk. No-op. |
| ADV-2 | advisory | `known-issues-archive.md` myocyte-omp "TRUE PASS 2026-03-27" is stale vs. current GCC 12 BUILD_FAIL. | Out of edit scope. Advisor logged for S6/S7 docs-hygiene. |
| ADV-3 | advisory | nn-cuda missing `tolerance_type` field. | Cosmetic only — verifier is absolute-only. Advisor ruled reject fix. |

### Round-2 verification (post Commit B `f814a72`)

Fresh runs against `main` after code-reviewer's commit landed:

- `git log --oneline HEAD~3..HEAD` confirms `f814a72` on `main`, stacked on my `0adea0c`.
- All 5 bucket2 specs: **VERIFY PASS** with `stdout_pattern+exit_code` under the new regex.
- FAIL probes against new regex `[+-]?\d[\d.eE+-]*`:
  ```
  Accuracy: -nan   → NO MATCH ✓  (was FALSE PASS under old regex)
  Accuracy: nan    → NO MATCH ✓
  Accuracy: inf    → NO MATCH ✓
  Accuracy: -      → NO MATCH ✓
  Accuracy: 4.096975e-05 → MATCH '4.096975e-05' ✓
  Accuracy: 0.0    → MATCH '0.0' ✓
  ```
- Full pytest suite: **217 passed / 3 skipped / 0 failed** (+5 from 212 — exactly matches
  the code-reviewer's new `test_bucket2_regex_rejects_non_numeric.py` case count).

**Caveat carried through to advisor:** the new regex tails (`[\d.eE+-]*`) still admit
pathological captures like `0-1` or `1e+-`. These are harmless false-*positives* on
correct output — never false-PASS on broken output — because the `\d` anchor after the
optional sign is what closes the `-nan` hole. Accept the trade.

**Round-2 findings: zero.** No new defects surfaced. Commit B resolves FLAG-1 + FLAG-2
cleanly, preserves `oracle_strength=strong` defensibly, and adds a regression test that
would have caught the bug under TDD.

### Provenance

- Cross-talk with `s5-code-reviewer`: exchanged findings lists, converged on BLOCK-1 +
  FLAG-1 + FLAG-2 with no disagreement.
- Code-reviewer retracted BLOCK-1 mid-review based on stale grep against post-fix tree.
  Team-lead corrected; original finding was valid (see §BLOCK-1).
- `/validate` waves 1-4 applied inline for Commit A (`0adea0c`); Agent-tool spawning is
  disabled in this team config so wave agents ran as bash checks against documented
  invariants. Sentinel consumed by pre-commit hook on commit.
- Tools: `sha256sum`, live `python3 -m harness verify`, Python regex probes via `re.search`,
  `git stash` red-probe TDD cycles, `pytest`, `scripts/validate_schema.py`.

### Karpathy review (all 5 S5 commits + my Commit A)

- **Batch 1 (`d29d187`):** 2 spec edits + 1 CLI line + 1 new smoke test. Every line traces to scope.
- **Batch 2 (`f6950b6`):** 1 spec edit. Subsequently extended in Batch 3 to restore sentinel — justified by 5 regex-combiner tests that broke.
- **Batch 3 (`dc125f7`):** 5 regex tightenings + sentinel restore. Subsequently patched by Commit B for `-nan` — not a defect of scope, defect of adversarial test coverage. Lesson: bucket2 regex-tighten should default-require a digit anchor on first authoring.
- **Batch 4 (`255bf0d`):** 27 pure-additive `oracle_strength` fields. No logic changes.
- **Commit A (`0adea0c`, mine):** 2-line fix + 1 narrow whitelist test + 1 parametrized smoke. First-draft dead helper removed mid-session. Every remaining line traces to the bug class S1.6 left latent.

No speculative abstractions, no error handling for impossible scenarios, no scope creep.

### Stopping condition

Round 1: 1 BLOCK, 2 FLAGs, 3 advisories.
Round 2: zero new findings.
Per protocol (2 consecutive rounds with no new findings from either teammate), I vote
**converge**. Awaiting advisor signal.

---

## s5-code-reviewer section

### Methodology

Invoked `andrej-karpathy-skills:karpathy-guidelines`, `superpowers:test-driven-development`, `superpowers:requesting-code-review` before first tool call. Established baseline:

- Schema validator: 15 baseline errors (expected per `known-issues.md`)
- Unit tests: 335 passed, 43 skipped, 2 pre-existing figure-test failures + 24 pre-existing paper-data errors (verified pre-S5 via `git stash` bisect — unrelated to these commits)
- All 22 S5-related verifier/cli/contract/regex-combiner tests PASS at baseline

Reviewed all 5 S5 commits via `git diff` + direct Read of every S5-touched spec/test/source file. Cross-referenced against `03-B1-AUDIT.md` bucket classifications + `HANDOFF.md` §2 distribution claim (see post-S7c tombstone above) + `known-issues.md` guardrails.

### Findings

#### BLOCK-1 — 2 verify_run callers still KeyError on `resolve_paths` return shape

**First-pass identification:** I initially filed this BLOCK after a partial Read of `scripts/evaluation/reverify_pass_results.py:214` that showed `target_spec_resolved["working_dir"]`. `resolve_paths()` returns the spec with a `_resolved` sub-dict (spec_loader.py:72), so direct access raises `KeyError: 'working_dir'`. Repro:

```
>>> resolved = resolve_paths(spec, Path('.'))
>>> resolved['working_dir']
KeyError: 'working_dir'
>>> resolved['_resolved']['working_dir']
'/home/samyak/Desktop/parbench_sam/rodinia/cuda/bfs'
```

**Retraction + re-adoption:** I retracted the BLOCK after a follow-up clean grep showed zero hits for `target_spec_resolved["working_dir"]`. Advisor corrected: s5-self-critic had applied the fix to the working tree in-flight, and my retraction grep saw the post-fix state. BLOCK-1 was real in HEAD `02868e8`.

**Resolution:** Landed by s5-self-critic as Commit A `0adea0c` — fixes `scripts/evaluation/llm_evaluate.py:1821` + `scripts/evaluation/reverify_pass_results.py:214`, strengthens `tests/test_verifier_caller_contract.py` with a second parametrized test that rejects the `<raw_return>["working_dir"]` pattern by tracking identifier bindings to `resolve_paths(...)`.

**Lesson for future reviewers:** When working in parallel with another agent, always verify with `git status` + `git diff` whether the working tree differs from HEAD before concluding a finding is false. My initial grep was correct for the working tree but wrong for HEAD. The retraction was also wrong.

#### FLAG-1 — bucket2 regex `[0-9.eE+-]+` false-PASSES on `-nan`

The S5 Batch 3 (dc125f7) regex-tighten upgraded `stdout_pattern` on hotspot3d×3 + md×2 from bare-literal match to `([0-9.eE+-]+)` capture. That capture is a character class — `re.search` only requires one class-char to match. `printf("%e", 0.0/0.0)` produces `-nan` on glibc (verified empirically by compiling a C test), and `-nan` matches the regex via the bare `-` character alone. `stdout_pattern` verifier (`harness/verifier.py:196`) does *not* float-parse the capture — just checks `re.search` fires — so the overall verification PASSES under `oracle_strength=strong`.

**Per bucket2 definition** (`03-B1-AUDIT.md`, line 2 of bucket defs): "existing stdout_pattern fires on garbage; narrowing to require a numeric field makes it strong." The S5 Batch 3 regex fires on garbage (bare sign), failing the definition.

**Verified empirical cases under old regex:**

| input | regex match? | FAIL-mode intent? |
|---|---|---|
| `Accuracy: 4.096975e-05` | yes | legitimate PASS |
| `Accuracy: -nan` | yes (capture=`-`) | should FAIL |
| `Accuracy: nan` | no | correct |
| `Accuracy: inf` | no | correct |
| `Max error between host and device: -nan` | yes (capture=`-`) | should FAIL |

**Scope-gated fix:** Advisor approved tightening to `([+-]?\d[\d.eE+-]*)` — requires ≥1 digit after optional sign. Rejects `-nan`, `nan`, `inf`, `-inf`, bare `+`/`-`. Accepts all realistic IEEE-754 printf/iostream outputs.

**Verified empirical cases under new regex:**

| input | new regex match? |
|---|---|
| `Accuracy: 4.096975e-05` | yes (real hotspot3d-cuda output) |
| `Max error between host and device: 1.86265e-09` | yes (real md-cuda output) |
| `Accuracy: -nan` | no |
| `Accuracy: nan` | no |
| `Accuracy: inf` | no |
| `Accuracy: 0` | yes |
| `Accuracy: -1.5e+10` | yes |

**Resolution:** Landed as Commit B `f814a72`. 5 spec edits (1-line each: pattern only) + new `tests/test_bucket2_regex_rejects_non_numeric.py` (5 test cases documenting the bug, the fix, and edge-case coverage). All 5 specs PASS `harness verify --config correctness` post-edit. 87 unit tests pass. Schema validator unchanged (15 baseline errors).

**nn-cuda unaffected:** the nn-cuda strategy (Batch 2 + Batch 3) includes `numeric_comparison` whose verifier *does* float-parse the capture (`harness/verifier.py:272`), so `-nan` → FAIL correctly. Only `stdout_pattern`-only bucket2 specs needed the regex tightening.

#### FLAG-2 — oracle_strength=strong label overstates (resolved by FLAG-1 fix)

Contingent on FLAG-1. With the regex tightened, `oracle_strength=strong` meets bucket2 definition. Resolved.

#### ADVISORY-1 — cli smoke test only exercises stdout_pattern strategy path

`tests/test_cli_verify_smoke.py` (added in S5 Batch 1) uses bfs-cuda with mocked stdout matching its stdout_pattern. Does not exercise file_hash or numeric_comparison at the CLI level. My team-lead protocol item asked for parametrized coverage. I recommended SKIP per Karpathy §2: the cli.py `["_resolved"]["working_dir"]` fix is pre-dispatch (before any strategy-specific branch in verify_run), so one strategy path is sufficient to exercise the KeyError site. The contract test + new `test_bucket2_regex_rejects_non_numeric.py` cover other strategies in isolation. Advisor accepted SKIP.

### Verified clean (no action needed)

- **myocyte determinism (Rule 12 pre-flight):** re-verified with 2 fresh runs post-commit (`./myocyte.out 100 1 0`); both produce output.txt with SHA-256 `1e329f029af6...` matching spec. Source `work.cu:178-182` confirms output.txt contains only `WORKLOAD/TIME/y[i][j][k]` values via `fprintf(pFile,...)`. Timestamps are `printf(...)` → stdout, never written to the hashed file. File_hash strategy is safe.
- **Cross-variant spec consistency:** hotspot3d×3 (cuda/omp/opencl) identical `pattern`, `oracle_strength`, `description`; md×2 (cuda/omp_target) identical; myocyte×2 (cuda/opencl) identical structure with per-API `expected_sha256`.
- **nn-cuda sentinel restore (Batch 3):** `Distance=` preserved as stdout_pattern alongside `numeric_comparison` on `Distance=([0-9.eE+-]+)` with tolerance 1e-3. 41 `test_regex_combiner_integration.py` tests pass — cross-API verify for `nn-opencl→nn-cuda` works under conjunction semantics. Sentinel is NOT redundant: the regex-combiner fix (`_build_cross_api_verify_spec`) requires target-side `stdout_pattern` to combine with source patterns.
- **HANDOFF §2 oracle distribution:** live state matches claim (`7 strong / 1 medium / 27 weak / 0 unknown / 171 missing`). Commit SHAs `d29d187`, `f6950b6`, `dc125f7`, `255bf0d`, `02868e8` all accurate.
- **myocyte-omp BUILD_FAIL weak-tag decision (Batch 4):** reproduced locally — GCC 12 rejects `kernel_fin` call at `main.c:1374` due to argument-type mismatch (signature at `main.c:1173` takes different types than the call provides). This is a benchmark source inconsistency, not a toolchain flag issue. `HANDOFF §3 Rule 1` forbids modifying benchmark source. Weak-tag is the correct call; Rule 12 determinism pre-flight is impossible without a passing build. Note: `known-issues-archive.md` claims myocyte-omp was "TRUE PASS 2026-03-27" via run-args fix — that environmental record is now stale (environmental drift post-2026-03, not a S5 regression).
- **Batch 4 (27 weak-tags):** metadata-only addition; no strategies changed. Pre-existing PASS/KNOWN_FAIL status preserved.
- **Schema compliance:** all 5 FLAG-1-fixed specs + all 8 S5-upgraded specs individually pass `validate_schema.py --spec`. Per-strategy `if/then` constraints from S1 schema v1.1 enforced.

### Provenance

- Cross-talk with s5-self-critic: we exchanged findings lists. Overlap on BLOCK-1 (both teammates identified the `_resolved` bug class, self-critic applied the fix first). s5-self-critic originally missed FLAG-1 but accepted my evidence (`-nan` repro) and advisor ruling.
- Tooling: `rg`/`grep`, direct `python3 -c 're.search(...)'` probes, fresh binary runs (`./3D`, `./main`, `./myocyte.out`), compiled `/tmp/nan_test.c` to empirically verify glibc emits `-nan`.
- Commit B `f814a72` passed `/validate` waves 1-3 (inline) before commit. Waves: schema (15 baseline), pytest (87 passed), diff review (6 files, all in scope), regression (spec counts stable at 206/60/4/135).

### Round-2 cross-review of Commit A `0adea0c`

Re-read every changed file end-to-end post-commit. **Zero new BLOCK/FLAG findings.**

- **Source fix (`scripts/evaluation/llm_evaluate.py:1821` + `reverify_pass_results.py:214`):** 2-line dereference, matches same-file convention for `source_dir` at `llm_evaluate.py:200,444,491,553` and `reverify_pass_results.py:71,72,166`. Consistent.
- **Contract-test whitelist (`test_caller_uses_resolved_working_dir`):** probed the regex independently:

| input | accepted? | expected? |
|---|---|---|
| `working_dir=target_spec_resolved["_resolved"]["working_dir"]` | yes | yes |
| `working_dir=resolved["working_dir"]` (post pre-unwrap) | yes | yes |
| `working_dir=tempdir` | yes | yes |
| `working_dir=target_spec_resolved["working_dir"]` (buggy) | no | no (correct rejection) |
| `working_dir=other_ident["working_dir"]` | no | no |
| `working_dir=Path("/tmp/foo")` | no | strict but acceptable |

Rigid whitelist is a trade: rejects legitimate `wd = ...; verify_run(..., working_dir=wd)` indirection. Future refactor hazard only, not a current bug. Out of scope to soften.

- **Functional smoke (`tests/test_verify_run_working_dir_resolution.py`):** 3 parametrized cases run identical assertion bodies — `caller` param is a label, unused in asserts. Mild Karpathy §2 redundancy, but provides a descriptive failure mode per call-site. Acceptable; self-critic noted team-lead protocol explicitly required it.

- **Full pytest post-Commit-B:** 347 passed / 43 skipped / 0 failed (matches self-critic's 217 `tests/+harness/` count × broader discovery scope). Pre-existing 2 figure failures + 24 paper-data errors unchanged (verified pre-S5 via `git stash` bisect).

- **Harness verify sweep:** myocyte×2 (file_hash), nn-cuda (numeric_comparison + stdout_pattern sentinel), hotspot3d×3 + md×2 (tightened stdout_pattern) all PASS against live binaries.

- **`0adea0c` scope vs. Karpathy §3 (surgical changes):** every line traces directly to BLOCK-1. No adjacent refactor, no speculative abstraction, no scope creep into other callers or strategies.

**Round-2 findings: zero.** Vote: **converge.**

### Stopping condition

Round 1: 1 BLOCK, 2 FLAGs, 1 advisory (self-converged after re-reading peer's new test file).
Round 2: zero new findings from either teammate.
Per protocol (2 consecutive rounds with no new findings), the review is complete.
Lists converge. Final state: `HEAD = f814a72`, 2 fix commits landed (`0adea0c` + `f814a72`),
all S5 strategy-upgraded specs PASS live `harness verify`, pytest + schema validators
stable at documented baselines.
