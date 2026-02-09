{
  "kernel_name": "adam",
  "parallel_api": "cuda",
  "code": {
    "main.cu": "... full source code embedded ..."
  }
}
```

## Statistics from the Example File
- **Total entries:** 178
- **Unique kernels:** ~40-45
- **API distribution:** 
  - CUDA: 41
  - HIP: 42
  - SYCL: 39
  - OpenMP: 28
  - Serial: 28 (baseline/reference)

## Key Observations

| Aspect | Teammate's Format | Notes |
|--------|------------------|-------|
| **Granularity** | One entry per kernel-API | Same as our approach! |
| **Code storage** | Embedded (full source in JSON) | Good for self-contained datasets |
| **File handling** | Single file per entry | May need extension for multi-file kernels |
| **Build info** | Not included | We add this |
| **Verification** | Not included | We add this |
| **Dependencies** | Not included | We add this |
| **Serial baseline** | Included as `parallel_api: "serial"` | Good for correctness reference |

---

# Reconciled Two-Level Metadata System

## Overview
```
rosetta-stone/
├── manifest.jsonl              # Level 1: Discovery & Pairing
├── specs/                      # Level 2: Execution Details
│   ├── adam-cuda.json
│   ├── adam-hip.json
│   ├── adam-sycl.json
│   ├── adam-omp.json
│   ├── adam-serial.json
│   └── ...
└── code/                       # Optional: Embedded code archive
    └── (mirrors teammate's code storage)


# Level 1 Manifest:
Purpose: Quick enumeration, pairing visibility, lightweight querying
Format: One line per kernel-API combination (compatible with teammate's format)
```
{"kernel_name": "adam", "parallel_api": "cuda", "spec_file": "specs/adam-cuda.json", "category": "ml", "source_suite": "HeCBench"}
{"kernel_name": "adam", "parallel_api": "hip", "spec_file": "specs/adam-hip.json", "category": "ml", "source_suite": "HeCBench"}
{"kernel_name": "adam", "parallel_api": "sycl", "spec_file": "specs/adam-sycl.json", "category": "ml", "source_suite": "HeCBench"}
{"kernel_name": "adam", "parallel_api": "omp", "spec_file": "specs/adam-omp.json", "category": "ml", "source_suite": "HeCBench"}
{"kernel_name": "adam", "parallel_api": "serial", "spec_file": "specs/adam-serial.json", "category": "ml", "source_suite": "HeCBench"}
{"kernel_name": "bfs", "parallel_api": "cuda", "spec_file": "specs/bfs-cuda.json", "category": "graph", "source_suite": "HeCBench"}
```

## Fields:
FieldTypeRequiredDescriptionkernel_namestring✓Logical kernel name (used for pairing)parallel_apistring✓API: cuda, hip, sycl, omp, omp_target, openacc, kokkos, mpi, omp_mpi, serialspec_filestring✓Path to detailed Level 2 speccategorystring○Domain: ml, graph, physics, linear_algebra, etc.source_suitestring○Origin benchmark suitecodeobject○Embedded code (teammate's format, optional)
Key insight: The kernel_name field implicitly defines pairing — all entries with the same kernel_name are equivalent implementations across different APIs.


Quesrying Examples:
```
# Find all APIs available for "adam" kernel
grep '"kernel_name": "adam"' manifest.jsonl

# Find all CUDA kernels
grep '"parallel_api": "cuda"' manifest.jsonl

# Find all graph kernels
grep '"category": "graph"' manifest.jsonl
```

# Level 2: Detailed Specs (JSON) — Execution Details
Purpose: Full build/run/verify information for the harness
Linked from Level 1: The spec_file field in manifest points here
```
{
  "$schema": "https://rosetta-stone.example.com/kernel-spec/v1.json",
  "spec_version": "1.0.0",
  
  "identity": {
    "kernel_name": "adam",
    "parallel_api": "cuda",
    "unique_id": "hecbench-adam-cuda"
  },
  
  "provenance": {
    "source_suite": "HeCBench",
    "repository": {
      "url": "https://github.com/zjin-lcf/HeCBench",
      "commit": "abc123def456",
      "branch": "master"
    },
    "source_path": "src/adam-cuda/",
    "files": ["main.cu", "reference.h", "Makefile"],
    "license": "MIT"
  },
  
  "implementation": {
    "api": "cuda",
    "api_version": "11.0+",
    "language": "C++",
    "language_standard": "C++17"
  },
  
  "build": {
    "environment": {
      "preferred": "conda",
      "conda": {
        "environment_file": "environment.yml",
        "channels": ["conda-forge", "nvidia"],
        "packages": ["cudatoolkit>=11.0", "cmake", "make"]
      },
      "system": {
        "dependencies": ["CUDA Toolkit >= 11.0", "GCC >= 9.0"]
      }
    },
    "system": "make",
    "working_directory": "src/adam-cuda/",
    "commands": {
      "build": "make ARCH=${GPU_ARCH}",
      "clean": "make clean"
    },
    "variables": {
      "GPU_ARCH": {
        "description": "NVIDIA GPU compute capability",
        "default": "sm_70",
        "detection": "nvidia-smi --query-gpu=compute_cap --format=csv,noheader"
      }
    },
    "outputs": {
      "executable": "main"
    }
  },
  
  "run": {
    "executable": "./main",
    "arguments": ["10000", "200", "100"],
    "timeout_seconds": 300,
    "environment": {},
    "problem_sizes": {
      "small": { "arguments": ["1000", "50", "10"] },
      "medium": { "arguments": ["10000", "200", "100"] },
      "large": { "arguments": ["100000", "500", "100"] }
    }
  },
  
  "verification": {
    "method": "self_checking",
    "strategies": [
      {
        "type": "stdout_pattern",
        "pattern": "^PASS$",
        "multiline": true
      },
      {
        "type": "numeric_comparison",
        "reference_api": "serial",
        "tolerance": {
          "type": "relative",
          "value": 1e-3
        }
      }
    ],
    "floating_point": {
      "tolerance": 1e-3,
      "tolerance_type": "absolute",
      "parallel_variance_note": "Results may vary slightly due to floating-point associativity in parallel reductions"
    }
  },
  
  "performance": {
    "metrics": [
      {
        "name": "kernel_time_ms",
        "extraction": {
          "type": "stdout_regex",
          "pattern": "Average kernel execution time\\s+([\\d.]+)\\s*\\(ms\\)",
          "capture_group": 1
        },
        "unit": "milliseconds"
      }
    ],
    "warmup_runs": 1,
    "measurement_runs": 10
  },
  
  "hardware": {
    "target": "gpu",
    "vendor": "nvidia",
    "min_compute_capability": "6.0",
    "min_memory_gb": 2
  },
  
  "metadata": {
    "description": "Adam optimizer kernel for machine learning",
    "domain": "machine_learning",
    "complexity": "O(n)",
    "tags": ["optimizer", "gradient_descent", "deep_learning"]
  }
}
```

---

## How the Two Levels Work Together
```
┌─────────────────────────────────────────────────────────────┐
│                    Level 1: manifest.jsonl                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ {"kernel_name": "adam", "parallel_api": "cuda",     │   │
│  │  "spec_file": "specs/adam-cuda.json", ...}          │───┼──┐
│  │ {"kernel_name": "adam", "parallel_api": "hip",      │   │  │
│  │  "spec_file": "specs/adam-hip.json", ...}           │───┼──┼─┐
│  │ {"kernel_name": "adam", "parallel_api": "serial",   │   │  │ │
│  │  "spec_file": "specs/adam-serial.json", ...}        │───┼──┼─┼─┐
│  └─────────────────────────────────────────────────────┘   │  │ │ │
│                                                             │  │ │ │
│  Pairing: All entries with same kernel_name are equivalent  │  │ │ │
└─────────────────────────────────────────────────────────────┘  │ │ │
                                                                  │ │ │
┌─────────────────────────────────────────────────────────────┐  │ │ │
│                 Level 2: specs/*.json                       │  │ │ │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐ │  │ │ │
│  │ adam-cuda.json   │ │ adam-hip.json    │ │adam-serial   │ │  │ │ │
│  │ ───────────────  │ │ ───────────────  │ │.json         │ │  │ │ │
│  │ • build commands │ │ • build commands │ │──────────────│ │  │ │ │
│  │ • run args       │ │ • run args       │ │• reference   │ │  │ │ │
│  │ • verification   │ │ • verification   │ │  impl        │ │  │ │ │
│  │ • hardware reqs  │ │ • hardware reqs  │ │• verification│ │  │ │ │
│  └────────▲─────────┘ └────────▲─────────┘ └──────▲───────┘ │  │ │ │
│           │                    │                   │         │  │ │ │
└───────────┼────────────────────┼───────────────────┼─────────┘  │ │ │
            │                    │                   │            │ │ │
            └────────────────────┴───────────────────┴────────────┘─┴─┘
```