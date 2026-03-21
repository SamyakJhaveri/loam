# Session 5: Commit All Uncommitted Work + Refresh Dashboard + Push

> **Depends on:** Sessions 3 AND 4 (both must be committed)
> **Blocks:** Nothing (final session)
> **Estimated time:** 30–45 minutes
> **Thinking level:** `think hard` (multi-commit workflow), `ultrathink` for submodule decisions

---

## Objective

1. Check submodule remote (can we push Rodinia source patches?)
2. Commit all remaining uncommitted Day 3 work in logical groups
3. Refresh dashboard visualization data
4. Run final validation
5. Push everything to remote

---

## Claude Code Prompt

Copy-paste this into a fresh `/clear` session:

```
I need to complete Session 5 of the Sprint Audit Fix Plan: commit remaining work, refresh dashboard, push.

**Pre-checks:** Confirm Sessions 3 and 4 are committed:
```bash
git log --oneline -8
```
Should show commits from Sessions 1-4. If any are missing, STOP.

## Phase 1: Survey uncommitted state

```bash
source env_parbench/bin/activate
git status
git diff --stat
```

Get the FULL picture of what's still uncommitted. Compare against this expected list:

**Staged (should already be committed by Sessions 1-4):**
- `harness/spec_loader.py` — Session 1 (ChangeFunctionNames)
- `.claude/rules/evaluation.md` — Session 1 (OMP args)
- `scripts/evaluation/llm_evaluate.py` — Session 4 (B1, B6)
- `scripts/evaluation/run_eval_batch.py` — Session 4 (B2)
- `results/augmentation/retest_post_session2.*` — Session 3

**Remaining uncommitted (from Day 3 work):**

Group 1 — Rodinia submodule source patches:
- `rodinia/rodinia-src/cuda/mummergpu/src/suffix-tree.cpp` (#include <unistd.h>)
- `rodinia/rodinia-src/openmp/mummergpu/src/suffix-tree.cpp` (#include <unistd.h>)
- `rodinia/rodinia-src/opencl/cfd/euler3d.cpp` (if(file==NULL) → if(!file))
- `rodinia/rodinia-src/opencl/pathfinder/main.cpp` (data → grid_data)
- Other Makefile/config changes in submodule

Group 2 — M10b spec changes:
- `specs/rodinia-cfd-cuda.json` (KERNEL_DIM include)
- `specs/rodinia-cfd-opencl.json` (CL_TARGET_OPENCL_VERSION)
- `specs/rodinia-pathfinder-opencl.json` (grid_data + CL version)
- `specs/rodinia-nn-cuda.json` (filelist_4)
- `specs/rodinia-hotspot-omp.json` (restored grid_cols)
- `specs/rodinia-nw-omp.json` (restored num_threads)
- Deleted: gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl

Group 3 — Augmentation code fixes (G1/G2):
- `c_augmentation/augment_dataset.py` (filename kwarg + set() fix)
- `c_augmentation/test_transforms.py` (4 new ChangeFunctionNames tests)

Group 4 — Documentation:
- `.claude/rules/known-issues.md` (full M10/M10b documentation)
- `.claude/rules/spec-conventions.md` (updated conventions)
- `.claude/rules/workflow.md` (minor updates)
- `docs/sprint_to_SC26.md` (Day 2/3 progress)

Group 5 — Dashboard:
- `visualizations/sprint_dashboard.html` (minor updates)

Group 6 — Results:
- `results/augmentation/retest_post_m9.json` (original 65-spec retest)
- `results/augmentation/retest_post_m9.md`

## Phase 2: Handle the submodule

```bash
git -C rodinia/rodinia-src remote -v
git -C rodinia/rodinia-src status
git -C rodinia/rodinia-src diff --stat
```

**Decision tree:**
- If remote is Erel's fork or our fork → we CAN commit + push submodule changes
- If remote is upstream Rodinia → we CANNOT push; document patches separately

**If we can't push submodule changes:**
Create a patches file:
```bash
cd rodinia/rodinia-src && git diff > ../../docs/rodinia_toolchain_patches.diff && cd ../..
```
Then commit the .diff file as documentation. The submodule pointer stays at the same commit.

**If we CAN push submodule changes:**
```bash
cd rodinia/rodinia-src
git add -A
git commit -m "Toolchain fixes: GCC 12 / C++17 / OpenCL 3.0 compatibility

- Add #include <unistd.h> to cuda/mummergpu and openmp/mummergpu (GCC 12)
- Fix if(file==NULL) → if(!file) in opencl/cfd/euler3d.cpp (C++14 strict)
- Rename global data → grid_data in opencl/pathfinder (C++17 std::data conflict)
- Add -DCL_TARGET_OPENCL_VERSION=120 flags to OpenCL Makefiles"
cd ../..
git add rodinia/rodinia-src
```

## Phase 3: Commit remaining work in logical groups

**Important:** Check what Sessions 1-4 already committed. Only commit what's LEFT.
Run `git status` before each commit to verify.

### Commit A: Augmentation code fixes (G1 + G2)
```bash
git add c_augmentation/augment_dataset.py c_augmentation/test_transforms.py
git commit -m "$(cat <<'EOF'
Fix augmentation gaps G1 (ChangeFunctionNames tests) and G2 (filename threading)

- G1: Add 4 unit tests for ChangeFunctionNames transform
  Also fix set vs list bug in _string_literals_in_file
- G2: Pass filename= kwarg in augment_sample() for correct libclang parsing

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Commit B: M10b spec fixes
```bash
git add specs/rodinia-cfd-cuda.json specs/rodinia-cfd-opencl.json \
  specs/rodinia-pathfinder-opencl.json specs/rodinia-nn-cuda.json \
  specs/rodinia-hotspot-omp.json specs/rodinia-nw-omp.json
# Also stage the deleted phantom specs (git tracks deletions automatically if already deleted)
git add specs/rodinia-gaussian-omp.json specs/rodinia-huffman-omp.json \
  specs/rodinia-huffman-opencl.json specs/rodinia-hybridsort-omp.json \
  specs/rodinia-mummergpu-opencl.json
git commit -m "$(cat <<'EOF'
M10b spec fixes: 6 corrections + 5 phantom spec deletions

Spec corrections:
- cfd-cuda: Add KERNEL_DIM include for helper_cuda.h
- cfd-opencl: Add -DCL_TARGET_OPENCL_VERSION=120 + fix NULL comparison
- pathfinder-opencl: Rename data→grid_data + OpenCL version flag
- nn-cuda: filelist.txt → filelist_4 (file didn't exist)
- hotspot-omp: Restore grid_cols arg (7 args, not 6)
- nw-omp: Restore num_threads arg (3 args, not 2)

Phantom spec deletions (pointed to non-existent dirs at commit 9c10d3ea):
- gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Commit C: Documentation
```bash
git add .claude/rules/known-issues.md .claude/rules/spec-conventions.md \
  .claude/rules/workflow.md docs/sprint_to_SC26.md
git commit -m "$(cat <<'EOF'
Update project docs: M10/M10b results, spec conventions, sprint progress

- known-issues.md: Full M10 retest results, M10b fixes, KNOWN_FAIL list
- spec-conventions.md: Updated conventions
- workflow.md: Minor session workflow updates
- sprint_to_SC26.md: Day 2/3 completion notes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Commit D: Results (if not already committed by Session 3)
```bash
git add results/augmentation/retest_post_m9.json results/augmentation/retest_post_m9.md
# Also add Session 3 results if they exist
git add results/augmentation/retest_post_session2.json results/augmentation/retest_post_session2.md 2>/dev/null
git commit -m "$(cat <<'EOF'
Add augmentation retest results (M10 + post-Session 2)

- retest_post_m9: 65 specs × L1-L4, 48/65 PASS (pre-M10b fixes)
- retest_post_session2: 60 specs × L1-L4 (post-M10b fixes)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### Commit E: Dashboard (after Phase 4 refresh)
Deferred until after `generate_viz_data.py` runs.

## Phase 4: Refresh dashboard data

```bash
python3 scripts/generate_viz_data.py
```

Read the script first to understand what it generates and from where.
If it fails, check the data source files it expects.

After generation:
```bash
git add visualizations/
git commit -m "$(cat <<'EOF'
Refresh dashboard visualization data (post-M10b results)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

## Phase 5: Final validation

Run ALL validators to confirm clean state:

```bash
# Schema validation (expect ~135 errors: 120 HeCBench + 15 phantom manifest refs)
python3 scripts/validate_schema.py --all

# Unit tests (expect 15 pass)
python3 -m pytest c_augmentation/test_transforms.py -v

# Clean git state
git status
```

## Phase 6: Push

Only after Phase 5 passes cleanly. Review commits then push immediately — no additional approval needed beyond verification passing:

```bash
git log --oneline -15  # Review all commits about to be pushed
git push origin main
```

## Cleanup

Delete the screenshot artifact (do NOT commit it):
```bash
rm -f "Screenshot 2026-03-20 at 10.29.09 AM.png"
```
```

---

## Files Reference — What Should Be Committed By End of Session 5

### Already committed by Sessions 1-4:

| Session | Files | Commit Message Pattern |
|---------|-------|----------------------|
| 1 | `harness/spec_loader.py`, `.claude/rules/evaluation.md` | "ChangeFunctionNames" |
| 2 | (testing only, maybe fixes + known-issues update) | "M10b targeted retest" |
| 3 | `results/augmentation/retest_post_session2.*`, known-issues update | "full retest" |
| 4 | `scripts/evaluation/llm_evaluate.py`, `scripts/evaluation/run_eval_batch.py` | "eval pipeline bugs" |

### Committed in Session 5:

| Group | Files | Description |
|-------|-------|-------------|
| A | `c_augmentation/augment_dataset.py`, `test_transforms.py` | G1+G2 augmentation fixes |
| B | 6 modified specs + 5 deleted specs | M10b spec corrections |
| C | `.claude/rules/*`, `docs/sprint_to_SC26.md` | Documentation |
| D | `results/augmentation/*` | Retest result files |
| E | `visualizations/*` | Dashboard data refresh |
| (submodule) | `rodinia/rodinia-src/` | Toolchain patches (depends on remote) |

### NOT committed (cleanup):

| File | Action |
|------|--------|
| `Screenshot 2026-03-20 at 10.29.09 AM.png` | Delete |

## Submodule Decision Tree

```
git -C rodinia/rodinia-src remote -v
           │
           ├── Our fork (github.com/samyakjhaveri/...)
           │     → commit + push submodule changes
           │     → git add rodinia/rodinia-src (updates pointer)
           │
           ├── Erel's fork (github.com/erel/...)
           │     → ask Samyak whether to push to Erel's fork
           │     → OR create patch file
           │
           └── Upstream (github.com/yuhc/...)
                 → CANNOT push
                 → Create docs/rodinia_toolchain_patches.diff
                 → Commit .diff as documentation
```

## Validation Expected Output

**`validate_schema.py --all`:**
- ~120 HeCBench `source_dir` disk-not-found errors → EXPECTED (HeCBench not cloned)
- 15 errors from 5 deleted phantom specs (still in manifest.jsonl) → EXPECTED (append-only)
- 0 errors from Rodinia specs → REQUIRED

**`pytest c_augmentation/test_transforms.py -v`:**
- 15 tests, all PASS → REQUIRED

**`git status` after all commits:**
- Clean working tree (nothing to commit) → REQUIRED

## Success Criteria

- [ ] Submodule state assessed and handled correctly
- [ ] All uncommitted work committed in logical groups
- [ ] Dashboard data refreshed with latest results
- [ ] `validate_schema.py --all` shows only expected errors
- [ ] All 15 unit tests pass
- [ ] `git status` is clean
- [ ] All commits verified then pushed to remote (push triggered by verification passing, not manual approval)
- [ ] Screenshot artifact deleted
