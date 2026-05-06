# ChangeFunctionNames

> God node · 37 connections · `c_augmentation/augment_dataset.py`

**Community:** [[Community 1]]

## Connections by Relation

### calls
- [[get_prompt_payload()]] `INFERRED`
- [[main()]] `EXTRACTED`
- [[_build_aug_config()]] `INFERRED`
- [[test_change_function_names_positive()]] `INFERRED`
- [[test_change_function_names_skip_main()]] `INFERRED`
- [[test_change_function_names_skip_kernel()]] `INFERRED`
- [[test_change_function_names_skip_string_literal()]] `INFERRED`

### contains
- [[augment_dataset.py]] `EXTRACTED`

### inherits
- [[Transform]] `EXTRACTED`

### method
- [[.apply()]] `EXTRACTED`
- [[.is_applicable()]] `EXTRACTED`
- [[._renamable_functions()]] `EXTRACTED`
- [[._build_candidate()]] `EXTRACTED`
- [[._collect_call_sites()]] `EXTRACTED`
- [[._is_kernel_function()]] `EXTRACTED`
- [[._uses_parallel_entry_builtins()]] `EXTRACTED`
- [[._fresh_name()]] `EXTRACTED`
- [[._existing_identifiers()]] `EXTRACTED`
- [[._has_internal_linkage()]] `EXTRACTED`

### rationale_for
- [[Consistently renames user-defined functions (free functions and class methods)]] `EXTRACTED`

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
- [[harness.spec_loader — Load specs, resolve paths, extract prompt payloads.]] `INFERRED`
- [[Load ``config/paths.json`` from the project root.      Returns     -------     d]] `INFERRED`
- [[Load every entry from a ``manifest.jsonl`` file.      Parameters     ----------]] `INFERRED`
- [[Load a single Level-2 spec JSON file.      Parameters     ----------     spec_pa]] `INFERRED`
- [[Resolve all relative paths in *spec* to absolute paths.      Uses ``config/paths]] `INFERRED`
- [[Read every file in *files.prompt_payload* and return their contents.      This i]] `INFERRED`
- [[Enumerate all valid (suite, kernel, source_api, target_api) translation pairs.]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*