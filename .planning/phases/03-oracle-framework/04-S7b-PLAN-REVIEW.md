# S7b Plan Review — Preserved Record

**Source:** `plan-reviewer` agent invocation during S7b plan-mode session, 2026-04-19.
**Verdict:** Plan accepted with scope revisions. All BLOCKERs fixed; FLAGs triaged; Assumptions labeled.
**Preservation rationale:** Agent could not write to `.planning/` under plan mode. Persisted on entry to execution mode (Stage 0, per plan §Entry checks → Stage 0).

---

## BLOCKERs (all resolved before execution began)

### BLOCKER-1 — Stage 6 strong-oracle spec list was under-counted

Original plan named 7 file_hash + 2 numeric_comparison specs. Correct `grep` pattern is `grep -l '"type": "file_hash"' specs/*.json` (the `"strategy":` key returns zero matches — wrong key).

**Ground truth at HEAD `9b1a1f5` (verified via grep during review):** 9 active file_hash specs.

Active 9:

- `rodinia-bptree-{cuda,omp}` (newly surfaced; NOT in original draft)
- `rodinia-cfd-{cuda,omp}`
- `rodinia-hotspot-{cuda,omp}`
- `rodinia-myocyte-{cuda,opencl}` (omp already deferred-weak)
- `rodinia-nw-omp` (singleton — no CUDA counterpart with file_hash)

Plus 2 medium `numeric_comparison` with reference files:

- `hecbench-md-{cuda,omp_target}`

**Resolution:** Plan §Stage 6 updated to enumerate all 11.

### BLOCKER-2 — `known-issues.md` strong-oracle count line is stale

Current line says `14 strong (file_hash or numeric_comparison with reference_files)`. Reality after S7 bfs downgrade + pending S7b downgrades:

- `N_file_hash_strong` = 9 (minus any S7b divergence downgrades)
- `N_numeric_medium` = 2 (`hecbench-md-*`) + 1 (`rodinia-nn-cuda`) = 3
- Total strong+medium = `11 − N_s7b_downgrades`

**Resolution:** Plan §Stage 6 adds explicit count-line update step committed with downgrades.

---

## FLAGs (triaged inline)

### FLAG-1 — `--resume` mandatory on cuda-to-omp / omp-to-cuda commands

`protect-cuda-omp-results.sh:65-72` blocks writes over existing CUDA↔OMP results unless `--resume` is present. Plan §Stage 4 TDD adds RED-assertion (c) — every CUDA↔OMP command must carry `--resume`.

### FLAG-2 — Downgrade checklist per divergent spec (expanded to 8 steps)

See plan §Stage 6 "Downgrade checklist per divergent spec".

### FLAG-3 — `--max-retries 1` must be explicit

Default IS 1, but silence invites assumption drift. Plan §Stage 4 TDD adds RED-assertion (d) and D-RETRIES decision block.

### FLAG-4 — Mixed-temp resume corruption risk (promoted to decision block D-RESUME)

Resume key = `{model}/{src}-to-{tgt}-L{n}-s{k}.json`. Temperature/seed/thinking/num_samples NOT in the key. Plan §Stage 4 §D-RESUME documents jq-assert before any resume command:

```
jq -r '.temperature' results/**/*.json | sort -u
```

Must print exactly the expected canonical (`0.7`) or ablation temperature.

### FLAG-5 — Stage 5 agent-team composition clarified

Advisor: plan-reviewer (Opus). Workers: self-critic (Opus, adversarial pass) + code-simplifier (Sonnet, simplification audit). Cross-talk enabled per `feedback_plan_review_team` memory.

---

## Advisory / Simpler-Alternatives (selectively adopted)

### ADV-1 / Simpler-alt 1 — Fold Stage 3 (oracle-fire) into Stage 4

Smoke artifacts already ~90% verified during planning. Standalone stage is over-engineering. Plan §Stage 4 absorbs as 3-line inline check.

**Adopted.**

### ADV-2 / Simpler-alt 2 — Hash-diff probe instead of full source-code-diff audit

Converts "source-semantic audit" into determinism + cross-pair probe. ~30 min vs. ~1–2 hr.

**Adopted.** Plan §Stage 6 TDD pattern uses two-run hash-diff probe per pair.

### ADV-2 (continued) — `/tmp/s7-artifacts-v3/` may be wiped on reboot

Fallback: re-run v3 smoke (~10 min, ~$0.63) or rely on live-smoke log.

**Adopted as entry-check #6 risk mitigation.**

### ADV-3 — Batch Stage 6 downgrade commits (do NOT one-commit-per-spec)

`fix(specs): downgrade N oracle strategies post-S7b audit` as single session-batch commit per HANDOFF §3 Rule 8.

**Adopted.**

### Simpler-alt 3 — Could drop code-simplifier from Stage 5 team

**Rejected.** Launch-manifest over-engineering is real risk; Sonnet cheap; keep code-simplifier.

---

## Ordering hazards (all addressed)

### HAZARD-1 — Oracle audit must precede manifest authoring

If Stage 6 downgrades specs, Stage 4 manifest must reflect the final corpus and exclude any new KNOWN_FAIL additions. Authoring manifest first forces a re-pass.

**Resolution:** Plan re-orders `Stage 6 → Stage 4`.

### HAZARD-2 — Handoff should batch with commits (not standalone stage)

Per HANDOFF §3 Rule 8 session-natural batch. Standalone Stage 8 risks stale handoff if committer forgets to update.

**Resolution:** Stage 8 folds into Stage 7+8.

### HAZARD-3 — Pre-validate snapshot needed as rollback safety net

If /validate fails 3 iterations, rollback without losing work.

**Resolution:** Plan §Stage 7+8 captures `/tmp/s7b-session-patch.diff` before validate.

### HAZARD-4 — Submodule may become dirty during Stage 6 builds

Per S6 sweep log lesson (myocyte/main.c restoration).

**Resolution:** Post-build reset step added to Stage 6.

---

## Verified claims during plan review (confidence elements the executor relies on)

1. Seed derivation: `_derive_llm_seed(src,tgt,sid)` at `llm_evaluate.py:312-323` produces distinct 31-bit seeds. For `rodinia-bfs-cuda→rodinia-bfs-omp` canonical: `s0=1938840902`, `s1=277232206`, `s2=1223013786`. Direction-sensitive, deterministic across models. **No `--seeds` CLI flag exists** — manifest must not invent one.

2. CLI flag set at `run_eval_batch.py:465-606` argparse: `--suite --kernels --task-list --direction --models --augment-levels --num-samples --temperature --thinking --max-retries --resume --project-root`. **No `--derive` subcommand** — ablation uses `scripts/evaluation/derive_l0_passers.py` → passer JSON → `--task-list passers.json`.

3. Azure reasoning temp gate at `llm_evaluate.py:940-942` (landed `54dc988`): wrapper strips `temperature`/`top_p` for `supports_thinking=True` models. Caller still passes `--temperature 0.7`; gate handles internally. Manifest states behavior; does not re-document the fix.

4. `protect-cuda-omp-results.sh:65-72` blocks CUDA↔OMP overwrites without `--resume`.

5. `scripts/evaluation/derive_l0_passers.py` implements D-16..D-21 pass@1-of-any filter (`project_ablation_filter` memory). Manifest pipes its output to `--task-list`.

---

## Assumptions (labeled; executor verifies at runtime)

- **Assumption-1:** Stage 6 audit finishes in ≤1 hr. Cap: if >3 pairs divergent, document and defer half to S7c.
- **Assumption-2:** Stage 5 agent-team produces zero BLOCKERs in 04-S7b-REVIEW.md within 45 min.
- **Assumption-3:** `derive_l0_passers.py` produces ≥3 passers per (model, direction) cell. If <3, non-fatal but must be reviewed before `--task-list` is consumed.
- **Assumption-4:** `rodinia/rodinia-src` submodule becomes clean after Stage 6 post-step reset. Reality at execution start: persistent env adaptations (HPC SDK 24.3 paths, sm_89 arch, GL header removal, C++ NULL fix) are present and required for builds. Not a regression — S6 sweep was 88/88 PASS with these in place. Only `openmp/myocyte/main.c` must stay at canonical 375 lines (verified at execution start).
- **Assumption-5:** PHASE-3-BLOCKER items (Gal budget re-approval; Le's gpt-5.4 provisioning; TPM quota) are orthogonal to S7b artifacts. Flagged in handoff, not fixed in session.
- **Assumption-6:** Budget recomputation (~$848 gpt-5.4 vs. $559 gpt-5.3-chat baseline) must be framed per `feedback_no_silent_budget_restatement` — recomputation needing fresh approval, NOT silent restatement.

---

## Karpathy + TDD wiring (cross-cutting)

Every stage that edits code or specs follows:

1. **Think Before Coding** — state assumptions; present tradeoffs; ask when unclear.
2. **Simplicity First** — each stage has explicit surgical-scope line capping touched files.
3. **Surgical Changes** — touch only what's needed; clean own mess only.
4. **Goal-Driven Execution** — each stage has RED→GREEN TDD gate with named verification.

---

## Push policy

Do NOT push. User runs `git push origin main` per `CLAUDE.md` invariant 7. S7's automatic push is treated as exception, not precedent.
