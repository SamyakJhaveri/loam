---
status: diagnosed
trigger: "Per-kernel table has 31 rows but paper describes 35 kernels — no explanation for the 4 missing"
created: 2026-04-05T23:30:00Z
updated: 2026-04-05T23:45:00Z
---

## Current Focus

hypothesis: 4 kernels (kmeans, mummergpu, hybridsort, huffman) are excluded from per-kernel table because all their non-KNOWN_FAIL/non-phantom specs cannot form valid translation pairs, but the paper never explains this gap
test: confirmed — traced each kernel's spec status and translation pair availability
expecting: n/a — root cause confirmed
next_action: return diagnosis

## Symptoms

expected: Paper explains why per-kernel table has 31 rows instead of 35
actual: Table caption says "KNOWN_FAIL source specs excluded" but does not name the 4 kernels or explain why they are fully excluded when some have PASS specs
errors: UAT tests 2 and 6 failed — user asked for explanation of the 35-to-31 gap
reproduction: Read S6.3 per-kernel table and count rows (31), compare to "35 kernels" stated in S4/S5
started: Since Phase 12-02 expanded table to all-suite scope

## Eliminated

(none — first hypothesis was correct)

## Evidence

- timestamp: 2026-04-05T23:35:00Z
  checked: KNOWN_FAIL list (8 specs) and phantom spec list (5 deleted)
  found: |
    The 4 missing kernels and their spec status:
    1. kmeans: 3 specs (cuda=KF, omp=PASS, opencl=KF) — OMP is PASS but has no valid translation partner (CUDA and OpenCL are both KF)
    2. mummergpu: 2 specs (cuda=KF, omp=KF) + 1 phantom deleted (opencl) — ALL specs are KF or phantom
    3. hybridsort: 2 specs (cuda=KF, opencl=PASS) + 1 phantom deleted (omp) — OpenCL is PASS but CUDA target is KF and OMP is phantom
    4. huffman: 1 spec (cuda=PASS) + 2 phantoms deleted (omp, opencl) — CUDA is PASS but has no translation target (OMP and OpenCL are phantom)
  implication: These 4 kernels cannot form any valid translation pair because every direction involves at least one KNOWN_FAIL or phantom spec

- timestamp: 2026-04-05T23:38:00Z
  checked: Eval results on disk for these 4 kernels
  found: kmeans has 48 result files (32 BUILD_FAIL, 16 VERIFY_FAIL), mummergpu has 16 (all BUILD_FAIL), hybridsort has 16 (8 BUILD_FAIL, 8 RUN_FAIL), huffman has 0. These are excluded from the primary campaign because the target baselines are broken.
  implication: Results exist but are meaningless — translations target specs whose baselines are broken

- timestamp: 2026-04-05T23:40:00Z
  checked: Contrast with nn kernel (nn-opencl is KNOWN_FAIL but nn-cuda and nn-omp are PASS)
  found: nn forms valid CUDA<->OMP pairs (10 tasks in table, 70% pass rate). Similarly stencil1d and scan have omp_target KF but their cuda/omp specs are PASS.
  implication: The exclusion criterion is not "has any KNOWN_FAIL spec" but "cannot form any valid translation pair from non-KF specs"

- timestamp: 2026-04-05T23:42:00Z
  checked: paper.tex line 845 (LaTeX comment)
  found: Comment reads "31 evaluated kernels = 35 corpus kernels - 4 with all specs KNOWN_FAIL/phantom (kmeans, mummergpu, hybridsort, huffman)" — the information is in a source comment but NOT in any reader-visible text
  implication: The author (Claude) knew the reason but did not surface it in the paper text

## Resolution

root_cause: The per-kernel table excludes 4 kernels (kmeans, mummergpu, hybridsort, huffman) that cannot form any valid translation pair because every potential direction involves at least one KNOWN_FAIL or phantom-deleted spec. The paper has this information only in a LaTeX source comment (line 845) but never states it in reader-visible text — not in the S6.3 table caption, not in the surrounding prose, and not in the S7 Discussion.
fix: (pending — diagnosis only)
verification: (pending)
files_changed: []
