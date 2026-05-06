# ChangeNames

> God node · 39 connections · `c_augmentation/augment_dataset.py`

**Community:** [[Community 1]]

## Connections by Relation

### calls
- [[get_prompt_payload()]] `INFERRED`
- [[main()]] `EXTRACTED`
- [[_build_aug_config()]] `INFERRED`
- [[test_real_kernel_pipeline()]] `INFERRED`
- [[available_transforms()]] `INFERRED`
- [[test_change_names()]] `INFERRED`

### contains
- [[augment_dataset.py]] `EXTRACTED`

### inherits
- [[Transform]] `EXTRACTED`

### method
- [[.apply()]] `EXTRACTED`
- [[._renamable_decls()]] `EXTRACTED`
- [[._symbol_edits()]] `EXTRACTED`
- [[._owning_function()]] `EXTRACTED`
- [[._macro_identifiers()]] `EXTRACTED`
- [[._decl_used_in_omp_pragma()]] `EXTRACTED`
- [[._function_has_omp_pragma()]] `EXTRACTED`
- [[.is_applicable()]] `EXTRACTED`
- [[._file_contains_omp_pragma()]] `EXTRACTED`
- [[._fresh_name()]] `EXTRACTED`
- [[._existing_identifiers()]] `EXTRACTED`

### rationale_for
- [[Consistently renames local variables and function parameters using symbol-aware]] `EXTRACTED`

### uses
- [[Return (ci.Index, AugmentationConfig) for the given level, or (None, None).]] `INFERRED`
- [[Read prompt_payload files, apply augmentation, return contents + transforms.]] `INFERRED`
- [[Full augment -> build -> run -> verify pipeline for one spec.      Returns a res]] `INFERRED`
- [[Static helper functions are renamed; non-static (external) functions are not.]] `INFERRED`
- [[main() is in RESERVED and must never be renamed.]] `INFERRED`
- [[Static functions that use CUDA builtins (threadIdx/blockIdx) must not be renamed]] `INFERRED`
- [[Functions whose name appears in a string literal must not be renamed (OpenCL clC]] `INFERRED`
- [[Bug A: nested subscripts like J[iS[i]*cols+j] must not produce overlapping edits]] `INFERRED`
- [[Fix B: *(ptr+i).member form must produce parseable output with base wrapped in p]] `INFERRED`
- [[Bug C: comparisons where an operand contains an assignment must be skipped.]] `INFERRED`
- [[SingleAugMetadata]] `INFERRED`
- [[harness.spec_loader — Load specs, resolve paths, extract prompt payloads.]] `INFERRED`
- [[Load ``config/paths.json`` from the project root.      Returns     -------     d]] `INFERRED`
- [[Load every entry from a ``manifest.jsonl`` file.      Parameters     ----------]] `INFERRED`
- [[Load a single Level-2 spec JSON file.      Parameters     ----------     spec_pa]] `INFERRED`
- [[Resolve all relative paths in *spec* to absolute paths.      Uses ``config/paths]] `INFERRED`
- [[Read every file in *files.prompt_payload* and return their contents.      This i]] `INFERRED`
- [[Enumerate all valid (suite, kernel, source_api, target_api) translation pairs.]] `INFERRED`
- [[Force transform.apply() to take its internal random branches so we reliably appl]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*