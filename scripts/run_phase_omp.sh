#!/usr/bin/env bash
# OMP stream: Phase 3 smoke → Phase 4 Rodinia → Phase 5 all OMP
set -e
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

echo "========================================================"
echo "  OMP STREAM START: $(date)"
echo "========================================================"

echo ""
echo "===== Phase 3 OMP: rodinia-hotspot-omp × L1,L2,L4 ====="
python3 scripts/run_augment_batch.py \
    specs/rodinia-hotspot-omp.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase3_omp \
    --title "Phase 3 Smoke Test: OMP (rodinia-hotspot-omp)"

echo ""
echo "===== Phase 4 OMP: All Rodinia OMP specs × L2 ====="
python3 scripts/run_augment_batch.py \
    specs/rodinia-*-omp.json \
    --levels 2 --seed 42 \
    --out results/augmentation/phase4_omp \
    --title "Phase 4: All Rodinia OMP Specs (L2)"

echo ""
echo "===== Phase 5 OMP: All OMP specs × L1,L2,L4 ====="
python3 scripts/run_augment_batch.py \
    specs/*-omp.json \
    --levels 1 2 4 --seed 42 \
    --out results/augmentation/phase5_omp \
    --title "Phase 5: All OMP Specs (L1+L2+L4)"

echo ""
echo "========================================================"
echo "  OMP STREAM DONE: $(date)"
echo "========================================================"
touch results/augmentation/.omp_done
