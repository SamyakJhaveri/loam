# eval-selections/

Landing directory for **per-model canonical L0-passer sets** produced between Phase A (canonical runs) and Phase C (L0-conditional ablation) of the NeurIPS 2026 evaluation — see `.planning/ROADMAP.md` Phase 3 and `docs/neurips2026-experiment-plan.md` §2.4.

> `azure-gpt-5.3-chat` resolved 2026-04-17 — entry registered in `MODEL_REGISTRY` (Plan 02-01).

## Contents (produced at runtime)

| File | Produced by | Consumed by |
|---|---|---|
| `l0_passers_qwen.json` | `scripts/evaluation/derive_l0_passers.py --model together-qwen-3.5-397b-a17b --condition any_of_3_pass` | `run_eval_batch.py --task-list l0_passers_qwen.json --augment-levels 1 2 3 4` |
| `l0_passers_gpt5_3_chat.json` | `scripts/evaluation/derive_l0_passers.py --model azure-gpt-5.3-chat --condition any_of_3_pass` | `run_eval_batch.py --task-list l0_passers_gpt5_3_chat.json --augment-levels 1 2 3 4` |

## Expected schema (`l0_passers_{model}.json`)

```json
{
  "version": "1.0",
  "generated_at": "2026-04-20T09:00:00Z",
  "model": "azure-gpt-5.3-chat",
  "source_canonical_dir": "results/evaluation/azure-gpt-5.3-chat-canonical/",
  "filter": "pass@1-of-any (>= 1 of 3 canonical samples has overall_status == PASS)",
  "total_cells_evaluated": 522,
  "passer_count": 287,
  "failer_count": 235,
  "passers": [
    {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "samples_passed": 2},
    ...
  ]
}
```

`passers[]` is the authoritative input list for the Phase C ablation launcher. Each entry expands to 4 task invocations (L1, L2, L3, L4) × 1 sample each. The `samples_passed` field is diagnostic only (for cross-correlation with ablation results during analysis).

## Reproducibility

These files are **committed to git** as part of the evaluation's reproducibility contract: any reviewer re-running the ablation from scratch must start from the same L0-passer set we did. The derivation script is deterministic given the canonical result JSONs.

## What is NOT stored here

- Canonical result JSONs themselves (live under `results/evaluation/{model}-canonical/`)
- Ablation result JSONs (live under `results/evaluation/{model}-ablation/`)
- Audit samples (none — see `docs/neurips2026-experiment-plan.md` §2.4)

---
*Stub created 2026-04-16 per `.planning/STATE.md` Session Continuity.*
