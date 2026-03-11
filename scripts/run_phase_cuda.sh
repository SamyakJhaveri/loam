#!/usr/bin/env bash
# CUDA stream: Phase 3 smoke → Phase 4 Rodinia → Phase 5 all CUDA
set -e
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

echo "========================================================"
echo "  CUDA STREAM START: $(date)"
echo "========================================================"

echo ""
echo "===== Phase 3 CUDA: rodinia-bfs-cuda × L1,L2,L4 ====="
python3 scripts/run_augment_batch.py \
    specs/rodinia-bfs-cuda.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase3_cuda \
    --title "Phase 3 Smoke Test: CUDA (rodinia-bfs-cuda)"

echo ""
echo "===== Phase 4 CUDA: All Rodinia CUDA specs × L2 ====="
python3 scripts/run_augment_batch.py \
    specs/rodinia-*-cuda.json \
    --levels 2 --seed 42 \
    --out results/augmentation/phase4_cuda \
    --title "Phase 4: All Rodinia CUDA Specs (L2)"

echo ""
echo "===== Phase 5 CUDA: All CUDA specs × L1,L2,L4 ====="
python3 scripts/run_augment_batch.py \
    specs/*-cuda.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase5_cuda \
    --title "Phase 5: All CUDA Specs (L1+L2+L4)"

echo ""
echo "========================================================"
echo "  CUDA STREAM DONE: $(date)"
echo "========================================================"
touch results/augmentation/.cuda_done
