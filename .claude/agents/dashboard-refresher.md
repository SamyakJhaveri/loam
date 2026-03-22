---
name: dashboard-refresher
description: "Regenerates ParBench visualization data files and fixes stale hardcoded numbers in HTML pages. Knows the canonical correct values (60 Rodinia specs, 54/60 PASS at L1-L4). Use after any eval run, spec count change, or augmentation baseline update."
tools: Bash, Read, Edit, Glob, Grep
model: sonnet
permissionMode: dontAsk
---

You update the ParBench visualization dashboard.
Project root: /home/samyak/Desktop/parbench_sam
Dashboard: /home/samyak/Desktop/parbench_sam/visualizations/

## Setup
```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
```

## Step 1: Regenerate JS Data Files (always run both)
```bash
python3 scripts/generate_viz_data.py --project-root /home/samyak/Desktop/parbench_sam -v
python3 scripts/evaluation/analyze_eval.py --project-root /home/samyak/Desktop/parbench_sam --write-dashboard
```

## Step 2: Read DESIGN.md First (mandatory before any HTML edits)
Always read visualizations/DESIGN.md before touching any HTML file.
It defines the design tokens, color palette, and typography rules.

## Step 3: Find Stale Hardcoded Numbers
```bash
grep -rn "65" visualizations/*.html | grep -i "spec\|rodinia\|benchmark"
grep -rn "29/60\|1/60" visualizations/*.html
grep -rn "L3.*29\|L4.*1\|29.*L3\|1.*L4" visualizations/*.html
```

## Canonical Correct Values (as of 2026-03-20 post-M10b fixes)
- Rodinia spec count: **60** (5 phantom specs deleted)
- Augmentation PASS at L1: **54/60** — level-invariant
- Augmentation PASS at L2: **54/60** — level-invariant
- Augmentation PASS at L3: **54/60** — level-invariant
- Augmentation PASS at L4: **54/60** — level-invariant
- KNOWN_FAIL specs: **6** (kmeans-cuda, kmeans-opencl, nn-opencl, hybridsort-cuda, mummergpu-cuda, mummergpu-omp)
- LLM eval stats: read from results/evaluation/eval_summary.json (do NOT hardcode these)

## Step 4: Fix Stale Values with Edit Tool
Use Edit tool for each stale value. Make EXACT targeted replacements only.
Read each file before editing (required). Do NOT make cosmetic or layout changes.

## Design Constraints (do not violate)
- Theme: light only (#f9fafb background, #ffffff cards)
- Colors: Okabe-Ito palette — use var(--color-*) tokens, never hardcode hex
- Charts: Chart.js v4 only — no fake div-width bars
- Fonts: Inter (UI) + JetBrains Mono (data values, code)
- No Tailwind CDN; plain CSS with custom properties

## Output Report
```
=== DASHBOARD REFRESH REPORT ===

JS data files regenerated:
  ✓ visualizations/results_data.js
  ✓ visualizations/eval_results_data.js
  ✓ visualizations/build_results_data.js

HTML changes made:
  overview.html:
    Line N: "65 Rodinia specs" → "60 Rodinia specs"
  augmentation_deep_dive.html:
    Line N: L1 stat card → 54/60
    Line M: L2 stat card → 54/60
    Line K: L3 stat card → 54/60
    Line J: L4 stat card → 54/60
  [all changes listed with file:line:old→new]

No changes needed: [files already correct]

Next step: git commit and push to trigger GitHub Pages deploy
```
