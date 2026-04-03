#!/usr/bin/env bash
# OpenCL stream: Phase 3 smoke → Phase 4 Rodinia → Phase 5 all OpenCL
# Note: All OpenCL specs are Rodinia (no HeCBench OpenCL)
set -e
PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
cd "$PROJECT_ROOT"
source env_parbench/bin/activate

echo "========================================================"
echo "  OPENCL STREAM START: $(date)"
echo "========================================================"

echo ""
echo "===== Phase 3 OpenCL: rodinia-bfs-opencl × L1,L2,L4 ====="
python3 scripts/augmentation/run_augment_batch.py \
    specs/rodinia-bfs-opencl.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase3_opencl \
    --title "Phase 3 Smoke Test: OpenCL (rodinia-bfs-opencl)"

echo ""
echo "===== Phase 4 OpenCL: All Rodinia OpenCL specs × L2 ====="
python3 scripts/augmentation/run_augment_batch.py \
    specs/rodinia-*-opencl.json \
    --levels 2 --seed 42 \
    --out results/augmentation/phase4_opencl \
    --title "Phase 4: All Rodinia OpenCL Specs (L2)"

echo ""
echo "===== Phase 5 OpenCL: All OpenCL specs × L1,L2,L4 ====="
python3 scripts/augmentation/run_augment_batch.py \
    specs/*-opencl.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase5_opencl \
    --title "Phase 5: All OpenCL Specs (L1+L2+L4)"

echo ""
echo "========================================================"
echo "  OPENCL STREAM DONE: $(date)"
echo "========================================================"
touch results/augmentation/.opencl_done
