#!/usr/bin/env python3
"""
scripts/generators/populate_translation_targets.py

Populate files.translation_targets and metadata.translation_complexity
for all 60 Rodinia spec files.

Data sourced from:
  docs/design/kernel_centric_translation.md  (OMP + 8 verified OpenCL specs)
  Best-guess pattern (.cl + host)             (remaining 12 OpenCL specs)

Also fixes spec bloat: moves non-kernel files from prompt_payload to
support_files for 10 specs (documented in section 7 of the architecture doc).

Usage:
    python3 scripts/generators/populate_translation_targets.py \\
        --project-root /home/samyak/Desktop/parbench_sam

    # Preview changes without writing:
    python3 scripts/generators/populate_translation_targets.py \\
        --project-root /home/samyak/Desktop/parbench_sam --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Source-verified data (docs/design/kernel_centric_translation.md § 5-6)
# ---------------------------------------------------------------------------

# OMP translation targets — all source-verified by reading Makefiles + pragma locations.
# tuple: (translation_targets, translation_complexity)
# translation_complexity is for the CUDA→OMP direction (computed from file counts).
# None entries: mummergpu-omp (KNOWN_FAIL — skip; fallback to full prompt_payload).
VERIFIED_OMP: dict[str, tuple[list[str], str] | None] = {
    "rodinia-backprop-omp": (
        ["backprop.c"],
        "multi_to_single",  # backprop-cuda(2) → omp(1)
    ),
    "rodinia-bfs-omp": (
        ["bfs.cpp"],
        "multi_to_single",  # bfs-cuda(3) → omp(1)
    ),
    "rodinia-bptree-omp": (
        ["kernel/kernel_cpu.c", "kernel/kernel_cpu_2.c"],
        "multi_to_multi",   # bptree-cuda(5) → omp(2)
    ),
    "rodinia-cfd-omp": (
        ["euler3d_cpu.cpp"],
        "multi_to_single",  # cfd-cuda(4) → omp(1)
    ),
    "rodinia-heartwall-omp": (
        ["main.c", "kernel.c", "define.c"],
        "multi_to_multi",   # heartwall-cuda(3) → omp(3); single compilation unit via #include
    ),
    "rodinia-hotspot-omp": (
        ["hotspot_openmp.cpp"],
        "single_file",      # hotspot-cuda(1) → omp(1)
    ),
    "rodinia-hotspot3d-omp": (
        ["3D.c"],
        "multi_to_single",  # hotspot3d-cuda(2) → omp(1)
    ),
    "rodinia-kmeans-omp": (
        ["kmeans_openmp/kmeans_clustering.c"],
        "multi_to_single",  # kmeans-cuda(2) → omp(1); only file with #pragma omp parallel for
    ),
    "rodinia-lavamd-omp": (
        ["kernel/kernel_cpu.c"],
        "multi_to_single",  # lavamd-cuda(3) → omp(1)
    ),
    "rodinia-lud-omp": (
        ["omp/lud_omp.c"],
        "multi_to_single",  # lud-cuda(2) → omp(1); only file with OMP pragmas
    ),
    "rodinia-mummergpu-omp": None,  # KNOWN_FAIL — skip; excluded from eval batches
    "rodinia-myocyte-omp": (
        [
            "cam.c", "define.c", "ecc.c", "embedded_fehlberg_7_8.c",
            "file.c", "fin.c", "main.c", "master.c", "solver.c", "timer.c",
        ],
        "multi_to_multi",   # myocyte-cuda(16) → omp(10); single compilation unit via textual #include
    ),
    "rodinia-nn-omp": (
        ["nn_openmp.c"],
        "single_file",      # nn-cuda(1) → omp(1)
    ),
    "rodinia-nw-omp": (
        ["needle.cpp"],
        "multi_to_single",  # nw-cuda(2) → omp(1)
    ),
    "rodinia-particlefilter-omp": (
        ["ex_particle_OPENMP_seq.c"],
        "multi_to_single",  # particlefilter-cuda(2) → omp(1)
    ),
    "rodinia-pathfinder-omp": (
        ["pathfinder.cpp"],
        "single_file",      # pathfinder-cuda(1) → omp(1)
    ),
    "rodinia-srad-omp": (
        ["srad.cpp"],
        "multi_to_single",  # srad-cuda(2) → omp(1)
    ),
    "rodinia-streamcluster-omp": (
        ["streamcluster_omp.cpp"],
        "multi_to_single",  # streamcluster-cuda(2) → omp(1)
    ),
}

# OpenCL translation targets — 8 source-verified (§6), 12 best-guess default pattern.
# Complexity = CUDA→OpenCL direction.
VERIFIED_OPENCL: dict[str, tuple[list[str], str]] = {
    # --- 8 source-verified specs (docs/design/kernel_centric_translation.md §6) ---
    "rodinia-bfs-opencl": (
        ["Kernels.cl", "bfs.cpp"],
        "multi_to_multi",   # bfs-cuda(3) → opencl(2)
    ),
    "rodinia-cfd-opencl": (
        ["Kernels.cl", "euler3d.cpp"],
        "multi_to_multi",   # cfd-cuda(4) → opencl(2)
    ),
    "rodinia-hotspot-opencl": (
        ["hotspot_kernel.cl", "hotspot.c"],
        "single_to_multi",  # hotspot-cuda(1) → opencl(2)
    ),
    "rodinia-hotspot3d-opencl": (
        ["hotspotKernel.cl", "3D.c"],
        "multi_to_multi",   # hotspot3d-cuda(2) → opencl(2)
    ),
    "rodinia-lud-opencl": (
        ["lud_kernel.cl", "ocl/lud.cpp"],
        "multi_to_multi",   # lud-cuda(2) → opencl(2)
    ),
    "rodinia-nw-opencl": (
        ["nw.cl", "nw.c"],
        "multi_to_multi",   # nw-cuda(2) → opencl(2)
    ),
    "rodinia-pathfinder-opencl": (
        ["kernels.cl", "main.cpp"],
        "single_to_multi",  # pathfinder-cuda(1) → opencl(2)
    ),
    "rodinia-srad-opencl": (
        [
            "kernel/kernel_gpu_opencl.cl",
            "kernel/compress_kernel.c",
            "kernel/extract_kernel.c",
            "kernel/kernel_gpu_opencl_wrapper.c",
            "kernel/prepare_kernel.c",
            "kernel/reduce_kernel.c",
            "kernel/srad2_kernel.c",
            "kernel/srad_kernel.c",
            "main.c",
        ],
        "multi_to_multi",   # srad-cuda(2) → opencl(9); all 9 files are computation dispatch
    ),
    # --- 12 best-guess default pattern (.cl + host .cpp/.c) ---
    # WARNING: these are not source-verified against Makefiles.
    # Apply default pattern: device .cl kernel(s) + host driver = translation_targets;
    # utility .c/.cc helpers not in primary build = move to support_files.
    "rodinia-backprop-opencl": (
        ["backprop_kernel.cl", "backprop_ocl.cpp"],
        "multi_to_multi",   # backprop-cuda(2) → opencl(2); UNVERIFIED
    ),
    "rodinia-bptree-opencl": (
        [
            "kernel/kernel_gpu_opencl.cl",
            "kernel/kernel_gpu_opencl_2.cl",
            "kernel/kernel_gpu_opencl_wrapper.c",
            "kernel/kernel_gpu_opencl_wrapper_2.c",
            "main.c",
        ],
        "multi_to_multi",   # bptree-cuda(5) → opencl(5); UNVERIFIED — all 5 appear needed
    ),
    "rodinia-dwt2d-opencl": (
        ["com_dwt.cl", "components.cpp", "dwt.cpp", "main.cpp"],
        "multi_to_multi",   # dwt2d-cuda(8) → opencl(4); UNVERIFIED
    ),
    "rodinia-gaussian-opencl": (
        ["gaussianElim_kernels.cl", "gaussianElim.cpp"],
        "single_to_multi",  # gaussian-cuda(1) → opencl(2); UNVERIFIED
    ),
    "rodinia-heartwall-opencl": (
        [
            "kernel/kernel_gpu_opencl.cl",
            "kernel/kernel_gpu_opencl_wrapper.c",
            "main.c",
        ],
        "multi_to_multi",   # heartwall-cuda(3) → opencl(3); UNVERIFIED
    ),
    "rodinia-hybridsort-opencl": (
        [
            "bucketsort_kernels.cl",
            "histogram1024.cl",
            "mergesort.cl",
            "bucketsort.c",
            "hybridsort.c",
            "mergesort.c",
        ],
        "multi_to_multi",   # hybridsort-cuda(6) → opencl(6); UNVERIFIED
    ),
    "rodinia-kmeans-opencl": (
        ["kmeans.cl", "kmeans.cpp", "kmeans_clustering.c"],
        "multi_to_multi",   # kmeans-cuda(2) → opencl(3); KNOWN_FAIL; UNVERIFIED
    ),
    "rodinia-lavamd-opencl": (
        [
            "kernel/kernel_gpu_opencl.cl",
            "kernel/kernel_gpu_opencl_wrapper.c",
            "main.c",
        ],
        "multi_to_multi",   # lavamd-cuda(3) → opencl(3); UNVERIFIED
    ),
    "rodinia-myocyte-opencl": (
        [
            "kernel/kernel_gpu_opencl.cl",
            "kernel/embedded_fehlberg_7_8.c",
            "kernel/kernel_fin.c",
            "kernel/kernel_gpu_opencl_wrapper.c",
            "kernel/master.c",
            "kernel/solver.c",
            "main.c",
        ],
        "multi_to_multi",   # myocyte-cuda(16) → opencl(7); UNVERIFIED — textual include chain
    ),
    "rodinia-nn-opencl": (
        ["nearestNeighbor_kernel.cl", "nearestNeighbor.cpp"],
        "single_to_multi",  # nn-cuda(1) → opencl(2); KNOWN_FAIL; UNVERIFIED
    ),
    "rodinia-particlefilter-opencl": (
        [
            "particle_double.cl",
            "particle_naive.cl",
            "particle_single.cl",
            "ex_particle_OCL_double_seq.cpp",
            "ex_particle_OCL_naive_seq.cpp",
            "ex_particle_OCL_single_seq.cpp",
        ],
        "multi_to_multi",   # particlefilter-cuda(2) → opencl(6); UNVERIFIED — 3 variants
    ),
    "rodinia-streamcluster-opencl": (
        ["Kernels.cl", "streamcluster.cpp"],
        "multi_to_multi",   # streamcluster-cuda(2) → opencl(2)
    ),
}

# UNVERIFIED_OPENCL_STEMS: stems for the 12 specs not source-verified.
# Used only for logging warnings.
UNVERIFIED_OPENCL_STEMS = {
    "rodinia-backprop-opencl",
    "rodinia-bptree-opencl",
    "rodinia-dwt2d-opencl",
    "rodinia-gaussian-opencl",
    "rodinia-heartwall-opencl",
    "rodinia-hybridsort-opencl",
    "rodinia-kmeans-opencl",
    "rodinia-lavamd-opencl",
    "rodinia-myocyte-opencl",
    "rodinia-nn-opencl",
    "rodinia-particlefilter-opencl",
    "rodinia-streamcluster-opencl",
}

# ---------------------------------------------------------------------------
# Spec bloat fixes (docs/design/kernel_centric_translation.md § 7)
# Files to move from prompt_payload → support_files.
# ---------------------------------------------------------------------------
BLOAT_FIXES: dict[str, list[str]] = {
    "rodinia-kmeans-omp": [
        "kmeans_serial/cluster.c",
        "kmeans_serial/getopt.c",
        "kmeans_serial/kmeans.c",
        "kmeans_serial/kmeans_clustering.c",
    ],
    "rodinia-streamcluster-omp": [
        "streamcluster_original.cpp",
    ],
    "rodinia-lud-omp": [
        "base/lud.c",
        "base/lud_base.c",
        "tools/gen_input.c",
    ],
    "rodinia-cfd-omp": [
        "euler3d_cpu_double.cpp",
        "pre_euler3d_cpu.cpp",
        "pre_euler3d_cpu_double.cpp",
    ],
    "rodinia-nn-omp": [
        "hurricane_gen.c",
    ],
    "rodinia-bfs-opencl": [
        "timer.cc",
    ],
    "rodinia-hotspot-opencl": [
        "OpenCL_helper_library.c",
    ],
    "rodinia-hotspot3d-opencl": [
        "CL_helper.c",
    ],
    "rodinia-pathfinder-opencl": [
        "OpenCL.cpp",
    ],
    "rodinia-lud-opencl": [
        "base/lud.c",
        "base/lud_base.c",
        "tools/gen_input.c",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_bloat_fix(spec: dict, stem: str) -> tuple[int, int]:
    """Move BLOAT_FIXES files from prompt_payload → support_files.

    Returns (n_moved, n_not_found) counts.
    """
    if stem not in BLOAT_FIXES:
        return 0, 0

    files = spec.setdefault("files", {})
    payload: list[str] = files.get("prompt_payload", [])
    support: list[str] = files.get("support_files", [])
    support_set = set(support)

    to_move = BLOAT_FIXES[stem]
    moved = 0
    not_found = 0

    new_payload: list[str] = []
    for fname in payload:
        if fname in to_move:
            if fname not in support_set:
                support.append(fname)
                support_set.add(fname)
            moved += 1
        else:
            new_payload.append(fname)

    not_found = len(to_move) - moved

    files["prompt_payload"] = new_payload
    files["support_files"] = support
    return moved, not_found


def _set_translation_targets(
    spec: dict,
    stem: str,
    targets: list[str],
    complexity: str | None,
    dry_run: bool = False,
) -> bool:
    """Set files.translation_targets and metadata.translation_complexity.

    Validates that all targets are in prompt_payload.
    Returns True if valid, False if validation error.
    """
    files = spec.get("files", {})
    payload_set = set(files.get("prompt_payload", []))

    # Validate subset
    invalid = [t for t in targets if t not in payload_set]
    if invalid:
        logger.error(
            "%s: translation_targets entries NOT in prompt_payload: %s",
            stem, invalid
        )
        return False

    if not dry_run:
        files["translation_targets"] = targets
        # Ensure metadata section exists
        if "metadata" not in spec:
            spec["metadata"] = {}
        if complexity is not None:
            spec["metadata"]["translation_complexity"] = complexity
        else:
            spec["metadata"]["translation_complexity"] = None

    return True


def _write_spec(spec: dict, spec_path: Path) -> None:
    """Write spec back to disk with consistent formatting (4-space indent, trailing newline)."""
    content = json.dumps(spec, indent=4)
    spec_path.write_text(content + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_specs(project_root: Path, dry_run: bool = False) -> int:
    """Process all Rodinia specs. Returns number of errors."""
    specs_dir = project_root / "specs"
    spec_files = sorted(specs_dir.glob("rodinia-*.json"))

    if not spec_files:
        logger.error("No rodinia-*.json specs found in %s", specs_dir)
        return 1

    errors = 0
    bloat_fixed = 0
    tt_set = 0
    skipped = 0

    for spec_path in spec_files:
        stem = spec_path.stem  # e.g. "rodinia-bfs-omp"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))

        parallel_api: str = spec.get("identity", {}).get("parallel_api", "")

        changed = False

        # ---- Step 1: Bloat fix (move non-kernel files to support_files) ----
        if stem in BLOAT_FIXES:
            moved, not_found = _apply_bloat_fix(spec, stem)
            if not_found > 0:
                logger.warning(
                    "%s: %d BLOAT_FIX files not found in prompt_payload "
                    "(already moved or wrong filename)",
                    stem, not_found,
                )
            if moved > 0:
                logger.info("%s: moved %d bloat files → support_files", stem, moved)
                bloat_fixed += 1
                changed = True

        # ---- Step 2: Set translation_targets + complexity ----
        if parallel_api == "cuda":
            # CUDA is always source — translation_targets = full prompt_payload
            # complexity = null (per-pair; depends on target direction)
            targets = list(spec.get("files", {}).get("prompt_payload", []))
            ok = _set_translation_targets(spec, stem, targets, None, dry_run=dry_run)
            if ok:
                logger.info("%s [CUDA]: translation_targets = prompt_payload (%d files)", stem, len(targets))
                tt_set += 1
                changed = True
            else:
                errors += 1

        elif stem in VERIFIED_OMP:
            entry = VERIFIED_OMP[stem]
            if entry is None:
                # KNOWN_FAIL — skip; pipeline falls back to full prompt_payload
                logger.info("%s: KNOWN_FAIL — skipping translation_targets", stem)
                skipped += 1
                continue
            targets, complexity = entry
            if stem in UNVERIFIED_OPENCL_STEMS:
                logger.warning(
                    "%s: UNVERIFIED translation_targets (best-guess) — verify against Makefile",
                    stem,
                )
            ok = _set_translation_targets(spec, stem, targets, complexity, dry_run=dry_run)
            if ok:
                logger.info(
                    "%s [OMP]: translation_targets=%s, complexity=%s",
                    stem, targets, complexity,
                )
                tt_set += 1
                changed = True
            else:
                errors += 1

        elif stem in VERIFIED_OPENCL:
            targets, complexity = VERIFIED_OPENCL[stem]
            if stem in UNVERIFIED_OPENCL_STEMS:
                logger.warning(
                    "%s: UNVERIFIED translation_targets (best-guess) — verify against Makefile",
                    stem,
                )
            ok = _set_translation_targets(spec, stem, targets, complexity, dry_run=dry_run)
            if ok:
                logger.info(
                    "%s [OpenCL]: translation_targets=%s, complexity=%s",
                    stem, targets, complexity,
                )
                tt_set += 1
                changed = True
            else:
                errors += 1

        else:
            logger.warning("%s: unknown parallel_api=%r — skipping", stem, parallel_api)
            skipped += 1
            continue

        # ---- Step 3: Write (unless dry-run or no change) ----
        if changed and not dry_run:
            _write_spec(spec, spec_path)

    logger.info(
        "Done: %d specs updated (bloat fixed: %d), %d skipped, %d errors",
        tt_set, bloat_fixed, skipped, errors,
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Path to parbench_sam root (default: auto-detected from script location)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN — no files will be written")

    return process_specs(args.project_root, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
