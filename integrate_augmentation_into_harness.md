 Architecture Analysis: Augmentation + Harness Integration

  Current State

  Here is what exists and what is working:

  ✅ Completed integration on erel/aug branch:
  - c_augmentation/augment_dataset.py — 5 AST-driven transforms (ArithmeticTransform, SwapCondition, PointerArithmeticToArrayIndex, TypedefExpansion,
  ChangeNames)
  - harness/spec_loader.py:get_prompt_payload() — already wired up with augment_level parameter that applies transforms to file content
  - harness/cli.py — prompt subcommand already has --augment_level [0-4] flag
  - libclang and c_augmentation are importable from the venv (confirmed)

  The integration path as it stands:
  harness prompt <spec> --augment_level N
    → get_prompt_payload(spec, root, augment_level=N)
      → reads each prompt_payload file
      → if augment_level > 0: calls augment_code(content, config, ci_index)
      → returns augmented content (printed to stdout only)

  The Critical Gap

  The harness verify command builds and runs the original source files on disk — it never applies augmentation to the actual build directory. The
  augmentation is currently only applied to the LLM prompt view (the prompt command output), not to the compiled binary.

  To verify semantic equivalence of augmented code, we need a path from:
  augmented code → temp build directory → compiled binary → run → verify against baseline

  This path does not exist yet. It must be built.

  ---
  Step-by-Step Plan (Iterative, Small-to-Large)

  ---
  Phase 0: Pre-flight Sanity Checks

  Goal: Confirm the environment works before touching anything.

  Tasks:
  1. Run the c_augmentation unit tests:
  source env_parbench/bin/activate
  cd c_augmentation && python3 -m pytest test_transforms.py -v
  2. Run harness prompt with and without --augment_level on one simple spec and diff the output:
  python3 -m harness prompt specs/rodinia-bfs-cuda.json > /tmp/orig.txt
  python3 -m harness prompt specs/rodinia-bfs-cuda.json --augment_level 1 > /tmp/aug.txt
  diff /tmp/orig.txt /tmp/aug.txt
  3. Confirm transforms actually change something (the diff should be non-empty for level 1+).

  Deliverable: All 8 unit tests pass; prompt --augment_level 1 produces a visibly different output.

  ---
  Phase 1: Understand the Build Directory Structure

  Goal: Confirm what the harness builder actually uses before writing the augment-verify script.

  Tasks:
  1. Run python3 -m harness -v build specs/rodinia-bfs-cuda.json and observe which directory it builds in.
  2. Check the actual source directory on disk:
  ls rodinia/rodinia-src/cuda/bfs/
  3. Understand that build.working_directory in the spec maps to a subdirectory of repo_root, and repo_root is relative to downloads_root (= project
  root on this machine).

  Key insight to confirm: The build runs in /home/samyak/Desktop/parbench_sam/rodinia/rodinia-src/cuda/bfs/. The prompt_payload files are a subset of
  everything in that directory. The Makefile and support files also live there.

  Deliverable: A clear picture of which files in the source dir are prompt_payload vs support_files vs verification_only.

  ---
  Phase 2: Design and Implement scripts/augment_verify.py

  Goal: Write the missing bridge that applies augmentation to disk files, builds them, and runs the harness verify pipeline.

  Design:
  augment_verify.py <spec_file> [--augment_level N] [--seed S] [--config correctness]
    1. Load spec → resolve working_dir, source_dir, prompt_payload list
    2. Create a temp copy:
         tempdir = /tmp/parbench_aug_<spec_id>_<seed>/
         shutil.copytree(working_dir, tempdir)   # copies Makefile + ALL files
    3. Get augmented code:
         augmented = get_prompt_payload(spec, project_root, augment_level=N)
    4. Overwrite prompt_payload files in tempdir with augmented content
    5. Patch the spec in memory:
         spec['_overridden_working_dir'] = tempdir
    6. Call build_spec() with patched spec
    7. Call run_spec() + verify_run()
    8. Report: PASS/FAIL, which transforms applied, diff vs baseline
    9. Clean up tempdir (unless --keep-temp)

  This requires a small modification to build_spec() in harness/builder.py to accept an optional override_working_dir parameter, OR we can patch the
  spec dict directly before passing it (simpler, no harness modification needed).

  Alternative approach (simpler, zero harness changes):
  Instead of patching build_spec(), write the script to:
  1. shutil.copytree(working_dir → tempdir)
  2. Write augmented files directly into tempdir
  3. Call subprocess.run(build_cmd, cwd=tempdir) directly (same commands from spec)
  4. Run the executable with the same args from the spec
  5. Compare output to baseline_results in the spec

  This keeps it self-contained in scripts/augment_verify.py and touches nothing in harness/.

  Deliverable: scripts/augment_verify.py that takes a spec and augment level, and reports PASS/FAIL.

  ---
  Phase 3: Small-Scale Test — 3 Smoke-Test Specs

  Goal: Validate the script works on the 3 specs we already know build and run correctly.

  Specs (already verified passing in smoke tests):
  - specs/rodinia-bfs-cuda.json
  - specs/rodinia-hotspot-omp.json
  - specs/rodinia-bfs-opencl.json

  Test matrix:

  ┌─────────────────────┬─────────┬─────────┬─────────┐
  │        Spec         │ Level 1 │ Level 2 │ Level 4 │
  ├─────────────────────┼─────────┼─────────┼─────────┤
  │ rodinia-bfs-cuda    │ ?       │ ?       │ ?       │
  ├─────────────────────┼─────────┼─────────┼─────────┤
  │ rodinia-hotspot-omp │ ?       │ ?       │ ?       │
  ├─────────────────────┼─────────┼─────────┼─────────┤
  │ rodinia-bfs-opencl  │ ?       │ ?       │ ?       │
  └─────────────────────┴─────────┴─────────┴─────────┘

  Run:
  for spec in rodinia-bfs-cuda rodinia-hotspot-omp rodinia-bfs-opencl; do
    for level in 1 2 4; do
      python3 scripts/augment_verify.py specs/${spec}.json --augment_level $level --seed 42
    done
  done

  Deliverable: 9 results (3 specs × 3 levels). All should be PASS if transforms are truly semantics-preserving.

  ---
  Phase 4: Medium-Scale Test — All 51 Passing Rodinia Specs

  Goal: Scale up to the full Rodinia suite across all passing specs.

  The 51 passing specs:
  - 18 CUDA (excluding cfd, hybridsort, kmeans, mummergpu)
  - 17 OMP (excluding mummergpu)
  - 16 OpenCL (excluding cfd, pathfinder, kmeans, nn)

  Test approach:
  Write a batch runner script scripts/run_augment_batch.sh:
  source env_parbench/bin/activate
  python3 scripts/augment_verify.py specs/rodinia-*.json --augment_level 2 --seed 42 --json > results/augmentation/rodinia_aug_results.json
  Or iterate per-spec and collect a results matrix.

  Deliverable: results/augmentation/rodinia_aug_results.md — a matrix showing which specs pass augmentation at each level, plus a summary of which
  transforms were applied.

  ---
  Phase 5: Full-Scale Test — All 152 Passing Specs (HeCBench + Rodinia)

  Goal: Run augmentation validation on the full benchmark.

  Note: This includes HeCBench specs whose source directories are on disk. The 120 HeCBench specs that fail with "source not found" will naturally
  fail at step 2 (copytree) and can be skipped.

  Test approach:
  python3 scripts/augment_verify.py specs/*.json --augment_level 2 --seed 42 --json \
    > results/augmentation/full_aug_results.json

  Deliverable: Full augmentation pass/fail matrix, summary statistics:
  - What % of specs pass at each augment level?
  - Which transforms are most/least disruptive?
  - Are there any specs where augmentation changes semantics (false negatives)?

  ---
  Phase 6: Wire Augmentation into Harness Pairs Workflow (Optional/Future)

  Goal: Enable the full LLM evaluation pipeline to use augmented source code.

  Currently harness prompt --augment_level N already shows augmented LLM input. But the full end-to-end evaluation (LLM translates augmented CUDA →
  verifies translated OpenCL) would require the target spec's verify step to still pass against the same baseline. This is fine because the baseline
  is in the target spec and the augmentation only affects the source (what the LLM translates from).

  No changes needed here — this already works by design.

  ---
  Summary Table

  ┌───────┬─────────────────────────────┬─────────────────────────────────────┬────────────┬───────────────────────────────────────────┐
  │ Phase │            What             │                 How                 │   Scale    │                Deliverable                │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 0     │ Pre-flight                  │ pytest + harness prompt diff        │ Unit tests │ All 8 tests pass; augmentation visible    │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 1     │ Build dir analysis          │ Read specs, harness build -v        │ 1 spec     │ Confirm file structure understanding      │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 2     │ Implement augment_verify.py │ New script in scripts/              │ Code       │ Bridge from augmentation → build → verify │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 3     │ Smoke test                  │ 3 known-good specs × 3 levels       │ 9 runs     │ PASS/FAIL matrix                          │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 4     │ Rodinia batch               │ 51 passing specs, level 2           │ ~51 runs   │ rodinia_aug_results.md                    │
  ├───────┼─────────────────────────────┼─────────────────────────────────────┼────────────┼───────────────────────────────────────────┤
  │ 5     │ Full batch                  │ All 152 passing specs, levels 1+2+4 │ ~450 runs  │ Full aug validation report                │
  └───────┴─────────────────────────────┴─────────────────────────────────────┴────────────┴───────────────────────────────────────────┘

  ---
  What Needs to Happen First

  The single most important task is Phase 2: implementing scripts/augment_verify.py. Without it, there is no automated way to test whether augmented
  code still compiles and produces correct output. Everything else (Phases 3–6) depends on this.

  Want me to start with Phase 0 (running the unit tests and diffing prompt output) and then move to implementing the augment_verify.py script? Or do
  you want to review and adjust the plan first?