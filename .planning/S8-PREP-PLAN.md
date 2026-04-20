# S8 PREP — Paste-in plan for fresh Claude Code session

> Copy this entire file into a new Claude Code session. It is self-contained: everything you need to pick up execution without reading prior sessions is in here. If you are an agent executing this plan, follow it top-to-bottom with no deviation. Surfaces for user approval are marked **ASK USER**.

---

## 0. Session identity

**Session name:** S7c (S7b ops follow-ups + smoke rehearsal, pre-S8)
**Previous session HEAD:** `45c371b` (docs handoff — S7b complete, S8 queued)
**Previous session landed (pushed by user):**

| SHA | Description |
|---|---|
| `ca30a2e` | `fix(specs)` — 8 oracle downgrades + tests + known-issues tally |
| `710e687` | `docs(03-oracle)` — Phase 3 launch manifest + plan review + adversarial review + committed verifier tool |
| `45c371b` | `docs(handoff)` — S7b complete, S8 PHASE-3-BLOCKER items queued |

**S8 is the Phase 3 canonical launch.** S8 is gated on three user-side items outside Claude's control (Gal budget re-approval at ~$848, Le provisioning `azure-gpt-5.4` on his Azure resource, TPM quota check). This plan (S7c) completes the Claude-side prep so that the instant those three items close, `run_eval_batch.py` can launch with zero remaining code churn and fresh smoke evidence.

---

## 1. Mandatory skill loads (do these FIRST, in order, before any tool call)

1. `Skill: caveman:caveman` with args `full` — drop articles/filler/pleasantries/hedging. Fragments OK. Code + commits + security prose stay normal.
2. `Skill: superpowers:test-driven-development` — every code-edit stage writes a RED test first, then the minimum GREEN fix. No exceptions.
3. `Skill: andrej-karpathy-skills:karpathy-guidelines` — Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution. Every stage below has an explicit **Surgical scope** line capping what files may be touched.
4. `Skill: superpowers:using-superpowers` — default superpower behavior (already loaded by session-start; invoke only if missing).

**Do not** invoke `superpowers:brainstorming` — this plan is already scoped. Brainstorming would waste context.

---

## 2. Entry checks (MUST all pass before Stage 1)

```bash
cd /home/samyak/Desktop/parbench_sam && source env_parbench/bin/activate

git log --oneline -4    # expect 45c371b at HEAD, 3 S7b commits landed, origin up-to-date
git status --short      # expect clean

git -C rodinia/rodinia-src status --short | head -5    # env adaptations persist (HPC SDK paths, sm_89)
# acceptable: the same 15 modified Makefile/config files listed in S7b entry-check #3
# NOT acceptable: openmp/myocyte/main.c modified (must be canonical 375 lines)
wc -l rodinia/rodinia-src/openmp/myocyte/main.c    # must print: 375

python3 -m pytest harness/ tests/ -m "not llm and not integration" -q 2>&1 | tail -1
# expect: 220 passed, 3 skipped
python3 scripts/spec_tools/run_verify_sweep.py --project-root /home/samyak/Desktop/parbench_sam --exclude-known-fail --jobs 4 2>&1 | tail -1
# expect: PASS 88/88  FAIL 0

python3 .planning/phases/03-oracle-framework/tools/verify_launch_manifest.py 2>&1
# expect: PASS — verified 5 command blocks, 21 argparse flags, 12 MODEL_REGISTRY entries

ls /tmp/s7-artifacts-v3/ 2>&1 | head    # presence optional per S7b entry-gate #6
```

If any check fails, **stop** and escalate. Do not proceed.

---

## 3. Stages

**Order rationale:** Stage 1 (smoke v4) runs first so any latent pipeline regression surfaces before Stage 2-4 add new code paths. Stages 2 (derive flag) + 3 (bucket2 upgrade) are independent edits to different files — could run in parallel but serial-in-one-session is simpler. Stage 4 (manifest update) depends on Stage 2's new flag. Stage 5 (memory) is last because Stage 3's oracle tally changes memory content.

### Stage 1 — Smoke rehearsal v4 (Option C, ~11 min wall, ~$0.63 spend)

**Goal:** re-run the S7 live-smoke v3 test suite on the post-S7b corpus to confirm the pipeline is still end-to-end green. Catches any regression from the oracle downgrades before Stage 2-4 adds code.

**TDD gate:**
- **RED:** pytest test suite already encodes the expected pipeline contract (canonical → derive_l0_passers → ablation × both models × both directions; 24 result JSONs; 0 null telemetry fields).
- **GREEN:** all 4 `test_eval_integration_smoke.py::test_real_*` tests PASS.

**Surgical scope:** no repo edits. Write one log file + one summary line.

**Action:**

```bash
# Confirm env vars loaded. If any missing, ASK USER.
printenv | grep -E '^(TOGETHER_API_KEY|AZURE_OPENAI_API_KEY|AZURE_OPENAI_ENDPOINT)=' | wc -l
# expect: 3

# Run smoke v4 inside tmux (long-running per memory feedback_use_tmux).
tmux new-session -d -s smoke-v4 "cd /home/samyak/Desktop/parbench_sam && source env_parbench/bin/activate && \
PARBENCH_RUN_LLM_TESTS=1 \
python3 -m pytest tests/test_eval_integration_smoke.py \
    -k 'test_real_e2e_canonical_to_ablation or test_real_direction_independence_omp_to_cuda' \
    --basetemp=/tmp/s7-artifacts-v4 \
    -v -s 2>&1 | tee .planning/phases/03-oracle-framework/04-S7-LIVE-v4.log"

# Monitor (~11 min).
tmux attach -t smoke-v4    # C-b d to detach; when pytest finishes, detach

# After completion, verify.
tail -30 .planning/phases/03-oracle-framework/04-S7-LIVE-v4.log
# expect: 4 passed
jq -r '.translation_type, .verification_mode, .seed, .top_p, .temperature, .overall_status, .model, .augment_level' \
    /tmp/s7-artifacts-v4/**/results/evaluation/**/*.json | grep -c null
# expect: 0

# If 4/4 PASS and 0 nulls: Stage 1 complete. Proceed.
# If any FAIL: stop, compare to v3 log (.planning/phases/03-oracle-framework/04-S7-LIVE-v3.log) for the regression, re-enter plan mode.
```

**Deliverable:** `.planning/phases/03-oracle-framework/04-S7-LIVE-v4.log` with a one-paragraph outcome summary appended at the bottom (wall time, total spend, PASS count).

---

### Stage 2 — `derive_l0_passers.py` `--direction` flag (TDD)

**Goal:** address S7b BLOCKER-1 properly (currently routed around via manifest §6.1). Adds an optional direction filter so one invocation produces one passer file per `(model, direction)` cell without mixing cuda-to-omp and omp-to-cuda results.

**Existing state (verified by S7c exploration):**

- `scripts/evaluation/derive_l0_passers.py` (120 lines) — argparse has `--canonical-dir --model --out`; no direction filter. `derive_passers(canonical_dir, model)` groups by `(source_spec, target_spec)` at `augment_level == 0`.
- `tests/test_derive_l0_passers.py` (128 lines, 10 tests) — all PASS. No direction-filter coverage.
- Call sites: 2 import paths (`tests/test_derive_l0_passers.py`, `tests/test_eval_integration_smoke.py`), 3 runbook doc references (`launch-manifest §6.1`, `docs/neurips2026-gpt5-handoff.md:160`, `HANDOFF.md:81` as ops follow-up).
- Downstream `run_eval_batch.py:127-225` `_build_tasks_from_task_list()` already filters by direction. Does NOT need changes; its direction guard becomes a no-op safety net once derive filters at source.

**TDD: RED first.**

Surgical scope: `tests/test_derive_l0_passers.py` (add 3 tests); `scripts/evaluation/derive_l0_passers.py` (argparse + signature + filter body).

1. Add RED tests to `tests/test_derive_l0_passers.py`:

```python
def test_direction_filter_keeps_matching_entries(tmp_path):
    """--direction cuda-to-omp keeps entries whose source unique_id ends in -cuda
    and target in -omp."""
    # Fixture: two canonical dirs with passes for both directions.
    # Assert: derive_passers(dir, model, direction="cuda-to-omp") returns only
    # cuda-to-omp cells.

def test_direction_filter_drops_non_matching_entries(tmp_path):
    """omp-to-cuda passer is dropped when --direction=cuda-to-omp."""

def test_direction_none_preserves_legacy_behavior(tmp_path):
    """derive_passers(..., direction=None) returns all directions (existing behavior)."""
```

2. Run — all 3 RED FAIL (no such param). Confirm failure messages mention "unexpected keyword argument 'direction'" or similar.

3. GREEN: minimum fix to `scripts/evaluation/derive_l0_passers.py`:

```python
# argparse:
parser.add_argument("--direction", default=None, metavar="SRC-to-TGT",
    help="Optional. When provided, filters passers to the given translation "
         "direction (e.g. cuda-to-omp). Derives source/target API from the "
         "last hyphen-delimited segment of each unique_id. When omitted, "
         "legacy behavior (no direction filter) — the passer file covers "
         "both directions and downstream run_eval_batch.py filters at consumption.")

# derive_passers signature + body:
def derive_passers(canonical_dir: Path, model: str, direction: str | None = None) -> list[dict]:
    src_api = tgt_api = None
    if direction is not None:
        # direction format: {src_api}-to-{tgt_api} (matches run_eval_batch.py parsing)
        if "-to-" not in direction:
            raise ValueError(f"--direction must match pattern SRC-to-TGT, got {direction!r}")
        src_api, tgt_api = direction.split("-to-", 1)
    # ... existing filter loop ...
    # Inside the loop, after the obj filter:
    if src_api is not None:
        # unique_id: {suite}-{kernel}-{api}; last segment after last - is api.
        src_suffix = src.rsplit("-", 1)[-1] if src else ""
        tgt_suffix = tgt.rsplit("-", 1)[-1] if tgt else ""
        if src_suffix != src_api or tgt_suffix != tgt_api:
            continue
    # ... rest of loop ...
```

**Caveat for the implementer:** Spec unique_ids with multi-segment API names (`omp_target`, `sycl_cpu_only`) split correctly on the last `-` because `api` never contains a `-`. Verify with a spot-check of manifest:

```bash
python3 -c "import json; lines=[json.loads(l) for l in open('manifest.jsonl') if l.strip()]; apis={e['parallel_api'] for e in lines}; print(apis); print([a for a in apis if '-' in a])"
# expect apis: {'cuda','omp','opencl','omp_target','sycl_cpu_only',...}; with-dash list: []
```

4. Run 3 new tests — all PASS. Run full `tests/test_derive_l0_passers.py` — 13 PASS. Run `tests/` subtree — no regressions.

5. Atomic commit: `fix(eval): derive_l0_passers gains --direction filter (S7c S2)`.

---

### Stage 3 — 5 mis-labeled-strong specs: upgrade to `numeric_comparison` (paper-value preferred over label downgrade)

**Goal:** S7b audit follow-up §1. Five specs carry `oracle_strength: "strong"` but strategies = `stdout_pattern + exit_code` only (no numeric or file_hash). Paper-explorer advisory: foreground oracle-strength engineering as a contribution — upgrading these to real `numeric_comparison` strengthens the story more than relabeling them weak.

**Target specs (all currently mis-labeled):**

| Spec | Current stdout_pattern (capture) | Action |
|---|---|---|
| `rodinia-hotspot3d-cuda` | `Accuracy:\s+([+-]?\d[\d.eE+-]*)` | add `numeric_comparison` on Accuracy |
| `rodinia-hotspot3d-omp` | same | add `numeric_comparison` on Accuracy |
| `rodinia-hotspot3d-opencl` | same | add `numeric_comparison` on Accuracy |
| `hecbench-md-cuda` | `Max error between host and device:\s+([+-]?\d[\d.eE+-]*)` | add `numeric_comparison` on Max error |
| `hecbench-md-omp_target` | same | add `numeric_comparison` on Max error |

The regex already has a capture group. Only need to: add a `numeric_comparison` strategy with `extract_regex` (same as stdout pattern) + `expected` (captured from baseline) + `tolerance` + refresh the spec's `oracle_strength` classification.

**Pre-flight (capture baselines):** run the kernel under `harness run --config correctness`, extract the printed numeric, set tolerance. For hotspot3d Accuracy: use 3 baseline captures, pick tolerance = 3× max observed variation across runs OR a round order-of-magnitude (e.g. 1e-3 relative). For `Max error`: check current baseline in `specs/hecbench-md-*.json:baseline_results.configurations.correctness.stdout_snippet`.

**TDD: RED first.**

Surgical scope: the 5 spec JSONs; one new test file `tests/test_bucket2_numeric_comparison.py` OR extend `tests/test_oracle_divergence.py`.

1. RED tests — one per spec, assert:
   a. Strategy list includes `numeric_comparison` (will FAIL initially).
   b. `oracle_strength == "medium"` (bucket2 is medium post-upgrade, not strong).
   c. `numeric_comparison.expected` is a finite float (not NaN).
   d. `numeric_comparison.tolerance > 0`.

2. Run — all 5 new tests RED FAIL.

3. GREEN fix (per spec):
   a. Capture baseline: `python3 -c "import subprocess, re; r=subprocess.run(['python3','-m','harness','run','--spec','specs/rodinia-hotspot3d-cuda.json','--config','correctness','--project-root','.'], capture_output=True, text=True); m=re.search(r'Accuracy:\s+([+-]?\d[\d.eE+-]*)', r.stdout); print(m.group(1) if m else 'NO MATCH')"` — record value.
   b. Do TWO runs per spec — confirm values deterministic across runs (determinism pre-flight, per HANDOFF §3 Rule 12).
   c. Edit spec JSON:

```json
{
  "type": "numeric_comparison",
  "extract_regex": "Accuracy:\\s+([+-]?\\d[\\d.eE+-]*)",
  "expected": <captured float>,
  "tolerance": <e.g. 1e-6 absolute if deterministic, else 3× max observed variation>,
  "description": "Numerical accuracy of the 3D-stencil thermal solver; tolerance accommodates FP reduction-order drift across devices. Added 2026-04-20 (S7c): bucket2 mis-label → medium numeric_comparison oracle."
}
```

   d. Keep the existing `stdout_pattern` strategy (conjunctive with numeric — strictly stronger).
   e. Set `oracle_strength: "medium"` (mid-tier; strong is reserved for file_hash + reference_files).

4. Run the 5 RED tests → all GREEN.
5. Run `scripts/spec_tools/run_verify_sweep.py` → still `PASS 88/88`.
6. Run `tests/test_bucket2_regex_rejects_non_numeric.py` → must still pass (regex unchanged).
7. Update `.claude/rules/known-issues.md` oracle tally: `7 strong / 0 medium / 46 weak / 153 untagged` → `2 strong / 5 medium / 46 weak / 153 untagged`. Update S7c row in the Spec Status section.
8. Update `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md` Follow-up §1 — mark "upgraded in S7c" with SHA placeholder.

Atomic commit: `fix(specs): S7c bucket2 upgrade — 5 specs stdout_pattern → numeric_comparison`.

**ASK USER** before this stage: confirm tolerance choice (round e.g. 1e-6, or 3× max variation). Default to 3× max observed if deterministic (typically 0 → set 1e-9 floor). For `hecbench-md` Max-error, check the baseline stdout in `baseline_results`.

---

### Stage 4 — Launch manifest §6.1 update (reflects Stage 2 new flag)

**Goal:** replace the route-around note in `04-S7-LAUNCH-MANIFEST.md §6.1` with the proper invocation using `--direction`.

**Surgical scope:** `.planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md` §6.1 + §6.2.

**Changes:**

- §6.1 rationale paragraph: delete "no `--direction` filter (verified by plan-reviewer 2026-04-19)" and replace with "`--direction` filter added 2026-04-20 (S7c) — one passer file per `(model, direction)` cell; downstream `_build_tasks_from_task_list` direction guard now a no-op safety net".
- §6.1 command block: add `--direction cuda-to-omp` per derive call; emit two files per model (`l0_passers_qwen_c2o.json`, `l0_passers_qwen_o2c.json`, similarly for azure).
- §6.2 command blocks: update passer filenames to the direction-specific ones.
- Re-run `python3 .planning/phases/03-oracle-framework/tools/verify_launch_manifest.py` — must PASS.

Atomic commit: `docs(manifest): S7c §6.1 update — use derive_l0_passers --direction`.

---

### Stage 5 — Memory freshness sweep

**Goal:** fix 3 stale MEMORY.md entries identified during S7c exploration.

**Files to edit** (located at `/home/samyak/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/`):

1. `reference_threats_to_validity.md` — currently says "27 🔴 / 17 🟡 / 3 🟢". Actual header counts in `02-THREATS-TO-VALIDITY.md §§1-5` are **24 🔴 / 16 🟡 / 3 🟢**. Update.
2. `project_neurips_experiment_design.md` — currently says "`azure-gpt-5.4` pending MODEL_REGISTRY entry (Phase 2 02-01)". `azure-gpt-5.4` landed in `MODEL_REGISTRY` via commit `44c6222`. Strike the "pending" clause; replace with "in registry at `llm_evaluate.py:105-112`".
3. `project_gpt5_3_chat_resolution.md` — currently says "both 5.4 and 5.3-chat kept in registry". At HEAD `45c371b`, only `azure-gpt-5.4` is in registry (5.3-chat was purged in `44c6222`). Update to reflect gpt-5.4-only present state.

**Surgical scope:** 3 memory files only. Update the `description:` field in frontmatter AND the body. Do NOT write new memories in this stage; just correct stale ones.

Atomic commit: `chore(memory): refresh 3 stale entries post-S7b` — though memory lives outside the repo, so this is not a git commit. Instead: apply the edits directly (memory files are not tracked by the project git repo; they live in `~/.claude/projects/.../memory/`).

Actually — verify memory location is outside repo before committing. If outside, no commit needed; memory writes are persistent by themselves.

---

### Stage 6 — Adversarial agent-team review

**Goal:** catch rationalization / blind spots in Stages 1-5 before commit + push.

**Composition** (per memory `feedback_plan_review_team`, `feedback_agent_teams`):

| Role | Agent | Model | Notes |
|---|---|---|---|
| Advisor | `.claude/agents/plan-reviewer.md` | Opus | coordinates, verifies claims |
| Worker | `.claude/agents/self-critic.md` | Opus | adversarial pass (rationalization / incomplete / quality-bar) |
| Worker | `.claude/agents/code-simplifier.md` | Sonnet | simplification audit (behavior-preserving) |

Dispatch pattern: 3 parallel `Agent` calls (read-only). Each reviewer loads `caveman:caveman ultra + andrej-karpathy-skills:karpathy-guidelines + superpowers:test-driven-development` at session start. Rule 13 read-only git.

Artifacts to review (all committed before Stage 6):
- `.planning/phases/03-oracle-framework/04-S7-LIVE-v4.log` (Stage 1 log)
- `scripts/evaluation/derive_l0_passers.py` (Stage 2 edit)
- `tests/test_derive_l0_passers.py` (Stage 2 new tests)
- 5 modified spec JSONs (Stage 3)
- `tests/test_bucket2_numeric_comparison.py` or extended `test_oracle_divergence.py` (Stage 3)
- `.claude/rules/known-issues.md` (Stage 3 tally)
- `.planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md` §6 (Stage 4)

Output: `.planning/phases/03-oracle-framework/04-S7c-REVIEW.md` — synthesize the 3 reviewers into Methodology / Findings / Verdict per `04-S7b-REVIEW.md` format.

Fix loop: address every BLOCKER, triage FLAGs inline. Max 3 fix iterations. If reviewers find nothing, still write the doc (skill: verify-before-complete).

---

### Stage 7 — Validate + commit + handoff

1. `/validate` waves 1-3. Expect PASS across `verify-app`, `diff-reviewer`, `security-scanner`, `test-synthesizer`, `regression-checker`, `spec-auditor`, `consistency-checker`, `code-simplifier` (Wave 4 optional).
2. Fix-loop if any FAIL. Max 3 iterations.
3. `.validation_passed` sentinel written. Commit (session-batched per HANDOFF Rule 8). Likely 3 commits:
   - `fix(eval): derive_l0_passers gains --direction filter (S7c S2)` (Stage 2 code+tests)
   - `fix(specs): S7c bucket2 upgrade — 5 specs stdout_pattern → numeric_comparison` (Stage 3 specs+tests+known-issues)
   - `docs(manifest+handoff): S7c — manifest §6.1 refresh + HANDOFF S7c row + review` (Stage 4 + S7c-REVIEW + HANDOFF update)
4. Update `.planning/HANDOFF.md`:
   - S8 row: mark PHASE-3-BLOCKER items still open. No changes.
   - Add S7c row to Commits Landed table (placeholder SHAs filled post-commit).
   - Add S7c row to Pending table: ✓ DONE.
5. Push policy: **DO NOT push.** User runs `git push origin main` themselves per `CLAUDE.md` invariant 7.

---

## 4. Time budget

| Stage | Estimate |
|---|---|
| Entry checks + skill loads | 5 min |
| Stage 1 (smoke v4) | 15 min (~11 min wall + setup/teardown) |
| Stage 2 (derive --direction TDD) | 30 min |
| Stage 3 (bucket2 upgrades) | 45 min (5 specs × 2-run determinism × 5 baseline captures + test wiring) |
| Stage 4 (manifest update) | 10 min |
| Stage 5 (memory sweep) | 10 min |
| Stage 6 (agent-team review) | 30 min |
| Stage 7 (validate + commit) | 20 min |
| **Total** | **~2.5 hr** |

If any single stage runs >1.5× estimate, **stop and escalate**.

---

## 5. Risk register

| Risk | Mitigation |
|---|---|
| Smoke v4 reveals regression | Compare to v3 log diff; if pipeline bug, re-enter plan mode |
| hotspot3d Accuracy value is not deterministic | fall back to `oracle_strength: "weak"` with stdout_pattern only (downgrade not upgrade) — still addresses mis-label |
| `hecbench-md` Max error differs across cuda vs omp_target | same FP-reduction-order problem as S7b; keep separate `expected` per spec, NOT shared |
| Memory files outside project root tree | verify location; edits persist in user's `~/.claude/` tree |
| Agent-team reviewers find a BLOCKER | normal; fix loop before commit |
| `--direction` flag breaks existing runbook in `docs/neurips2026-gpt5-handoff.md` | backward-compat default is None; runbook remains valid |

---

## 6. What NOT to do in S7c

- Do NOT run any Phase 3 canonical eval batch. S7c is prep only.
- Do NOT modify `manifest.jsonl` (append-only).
- Do NOT modify benchmark source under `rodinia/rodinia-src/` or `HeCBench-master/`.
- Do NOT push to `origin/main` — user's job.
- Do NOT touch existing result JSONs in `results/evaluation/` (Qwen + GPT-4.1-mini protected).
- Do NOT open other phase directories' plans (01-pipeline, 02-llm-eval) for edits. This session is entirely 03-oracle-framework.

---

## 7. Exit criteria (all must be met before session ends)

1. Smoke v4 4/4 PASS, log written, 0-null telemetry verified.
2. `tests/test_derive_l0_passers.py` has 13 PASS (10 pre-existing + 3 new).
3. `tests/test_bucket2_numeric_comparison.py` OR extended `test_oracle_divergence.py` has 5 PASS for the upgraded specs.
4. 88/88 sweep still PASS post-Stage 3.
5. `verify_launch_manifest.py` PASS after Stage 4.
6. `.planning/phases/03-oracle-framework/04-S7c-REVIEW.md` written with zero unresolved BLOCKERs.
7. `/validate` waves 1-3 PASS.
8. 3 commits on `main` (local), HANDOFF.md updated, not pushed.
9. 3 memory files updated with correct post-S7b state.

---

## 8. Critical references (for the executor's grepping convenience)

- `scripts/evaluation/run_eval_batch.py:465-606` argparse
- `scripts/evaluation/run_eval_batch.py:127-225` `_build_tasks_from_task_list`
- `scripts/evaluation/llm_evaluate.py:69-134` MODEL_REGISTRY
- `scripts/evaluation/llm_evaluate.py:312-323` `_derive_llm_seed`
- `scripts/evaluation/llm_evaluate.py:940-950` Azure reasoning gate
- `scripts/evaluation/derive_l0_passers.py` (120 lines)
- `tests/test_derive_l0_passers.py` (128 lines, 10 tests)
- `tests/test_eval_integration_smoke.py` (live-smoke fixtures)
- `tests/test_bucket2_regex_rejects_non_numeric.py` (regex locking test; must still PASS post-Stage 3)
- `.planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md` §6 (Stage 4 edit target)
- `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md` §Follow-up (Stage 3 rationale)
- `.claude/rules/known-issues.md` oracle tally (Stage 3 update target)
- `.claude/hooks/protect-cuda-omp-results.sh:65-76` (no Phase 3 batch runs this session, but respect the hook)

End of plan.
