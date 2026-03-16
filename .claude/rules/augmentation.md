# Augmentation Rules

> Auto-loaded when working on `c_augmentation/` or `scripts/augmentation/` files.

## Overview

AST-driven augmentation transforms (libclang-backed) in `c_augmentation/`.
Pipeline: `scripts/augmentation/augment_verify.py` — augment → build → run → verify.

## Critical: --project-root Flag

`augment_verify.py` auto-detection of project root is broken.
**Always** pass `--project-root` explicitly:

```bash
python3 scripts/augmentation/augment_verify.py specs/<name>.json \
  --augment_level 2 --seed 42 -v \
  --project-root /Users/samyakjhaveri/Desktop/parbench_sam
```

## Augmentable File Suffixes

`augment_verify.py` augments: `.c`, `.cu`, `.cpp`, `.cxx`, `.cc`, `.cl`, `.h`, `.hpp`

**Known inconsistency:** `harness/spec_loader.py:get_prompt_payload` does NOT include `.cl`.
See `.claude/rules/known-issues.md` for details.

## Transform Bugs (levels 3-4)

Three known bugs cause BUILD_FAIL at augment levels 3–4.
Levels 1–2 with seed=42 apply no transforms (no candidates selected).
Full details in `.claude/rules/known-issues.md` (Bugs A, B, C).

## Running Tests

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

## Batch Runs

```bash
python3 scripts/augmentation/run_augment_batch.py --help
python3 scripts/augmentation/combine_aug_results.py --help
```
