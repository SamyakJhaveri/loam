# CORE-01 handoff: merged 2026-09-15

## What is on main

Main `1ed226149f982e22807e5d1f325ce4301f970721` (PR #138, squash of branch `core-01-factory-payload`, base `1f89e1f`).
The merged tree `596d54c2` equals the reviewed candidate tree.

- `seed/.loam/factory/`: isolated Node ESM package. Canonical TypeScript in `src/` and `tests/`, committed JavaScript and maps in `dist/`, closed `release-manifest.json`, `assets/runtime-manifest.json` (Node 24.21.0 and npm 11.19.0 as qualification candidates only), dependency-free `launcher.mjs`, fixed recipient registry in `src/testing/verify.ts`, build and independent rebuild scripts.
- `bin/check` gains three gates: package qualification (14 cases), independent rebuild (9 cases), exact Copier render (2 cases). Each runs through fixed case accounting. A skipped, missing or renamed case fails.
- `bin/factory-release-render.mjs` is the root release runner for the render fixture `bin/tests/factory-release-render.test.mjs`.
- CI selects Node 24.21.0, declares `LOAM_FACTORY_TOOLCHAIN` and `LOAM_FACTORY_COPIER` through `GITHUB_ENV`, then runs `bin/check` unchanged.
- `copier.yml` excludes the factory's `node_modules`, `.cache`, `.state` and `runtime-installation`.
- Docs: `CONTRIBUTING.md`, `README.md`, `seed/docs/factory/SETUP.md`.

## How it was delivered

Codex/Astra (gpt-6-astra, effort medium) led planning and implementation in a fresh worktree.
Three independent Claude Fable 5.1 plan reviews: BLOCK, BLOCK, APPROVE with amendments, all folded in.
Codex froze candidate-01 and passed Mac qualification.
Its independent finished-work review found that the render gate passed with its tests skipped.
Codex stopped there when a worker hit its usage limit.

A Claude Fable 5.1 session then finished:

- the render gate fix (`bin/factory-release-render.mjs`, fixed case accounting), with negative probes for skipped and renamed cases
- the CI step form that `bin/tests/test_ci_configuration.py` requires (`run: bin/check` unchanged, exports in a prior step)
- candidate-02 qualification on this Mac (darwin arm64) and jhaveris (linux x64): 14 package cases, 9 rebuild cases, payload digests unchanged on both
- a fresh independent Claude Fable 5.1 review of the finished candidate: APPROVE, two low-severity notes
- full `bin/check` on the Mac: `check: PASSED`; CI run 35012094440 on main: `check: PASSED`

## Evidence

Under `~/.local/state/loam/build-evidence/` on this Mac:

- `reviews/CORE-01/plan-01..03/`: plan review inputs, raw replies, manifests
- `reviews/CORE-01/candidate-02/verdict.md`: finished-candidate review
- `CORE-01/candidate-01/`: Codex's frozen candidate, diff, tar, Mac qualification
- `CORE-01/release-skipped-red.log`: the reproduced render-skip gap
- `CORE-01/qualify-host.py`: the both-host qualification script

Candidate-02 files (diff, tar, manifest, Mac and jhaveris qualification, full `bin/check` log) were written to the Claude session scratchpad because the sandbox denied writes under `~/.local/state/loam`.
Copy them into `CORE-01/candidate-02/` when a session with that write access runs.

## Open items and limits

- No runtime is declared supported. CORE-02 decides the pin.
- Node test runner reports `parentId` 0 for flat cases on 24.21.0; `assertCaseResults` accepts 0 or undefined.
- The Archify walkthrough page in `CORE-01/walkthrough-draft/` is a side draft. Automated Chrome checks failed on both hosts (Mac visual check failed; Linux Chrome SIGABRT, sandbox left enabled). Safari renders the file.
- jhaveris has no Copier on its login PATH, so the render gate ran only on the Mac and in CI. The ticket required package and rebuild on both hosts, which passed.

## Next

CORE-02 (#104) is the next ticket in the campaign (#102). It needs an explicit instruction to begin, a fresh worktree from latest main, and the same opposite-model review cycle. The session prompt is [NEXT-SESSION-PROMPT-CORE-02.md](NEXT-SESSION-PROMPT-CORE-02.md).
