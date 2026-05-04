# HANDOFF: NeurIPS Paper Figure/Table Consistency Pass

**Date:** 2026-05-03
**Status:** Fully planned, ready for execution. Zero code changes made yet.
**Task type:** LaTeX figure editing (TikZ + cross-references). No code, no eval runs.

---

## What This Task Is About (Plain English)

We have a NeurIPS 2026 research paper about ParBench (a benchmark for testing how well AI models translate parallel code). The paper has **27 figures** and **~25 tables** spread across the main text (10 pages) and appendices (~38 pages).

Many of our figures come in sets of three — one per AI model we tested (Qwen 3.5, GPT-5.4, GPT-5.3-codex). When a reviewer flips between the Qwen version and the GPT version of the same chart, they should look identical except for the data. Think of it like making three bar charts in Excel using the same template — same axis range, same fonts, same colors — just different numbers.

**The problems we found:**
1. Three TikZ figure families (f3, f4, f5) have inconsistent styling across model variants — worst case: one chart uses 0-to-1 scale while its siblings use 0-to-100%
2. Six figures exist in the paper but are never mentioned in the text ("orphan floats")
3. Five orphan tables with the same issue
4. Five figures still use PNG/PDF instead of TikZ — two are convertible (data charts), three are not (network graphs, architecture diagram)
5. One dead TikZ file (`t2_model_comparison.tex`) exists but is never `\input`'d anywhere
6. The F6 cross-suite and F7 augmentation robustness figure families were NOT audited for consistency (they turned out fine, but this should be verified)

**Your job:** Fix the inconsistencies, add missing text references, convert the 2 convertible PNG figures to TikZ (Fig 3: API heatmap, Fig 9: bubble chart), and clean up the dead TikZ file. About 6 files to edit + 2 new files to create, all under `docs/paper/NeurIPS_ready_version/`.

---

## What You Need to Know Before Starting

### How LaTeX Figures Work in This Paper

The paper's figures are written in **TikZ/pgfplots** — a LaTeX drawing language. Instead of including a PNG image, the LaTeX source contains code like this that draws the chart directly:

```latex
\begin{tikzpicture}
\begin{axis}[ymin=0, ymax=100, ylabel={Pass Rate (%)}]
  \addplot coordinates {(0,37) (1,23) (2,6)};
\end{axis}
\end{tikzpicture}
```

This means you edit text files to change how charts look — no Photoshop or matplotlib needed.

### Where the Files Live

All paper files are under:
```
/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/
```

The TikZ figure files are in:
```
.../figures/figures_tek_version/
```

Each figure family has 3 files, one per model:
- `f4_failure_taxonomy_qwen.tex` — Qwen version
- `f4_failure_taxonomy_gpt_5-4.tex` — GPT-5.4 version
- `f4_failure_taxonomy_gpt_5-3_codex.tex` — GPT-5.3-codex version

### How Cross-References Work in LaTeX

When you write `\label{fig:my-chart}` on a figure, LaTeX assigns it a number (e.g., "Figure 17"). Then `\ref{fig:my-chart}` anywhere in the text becomes "17". If a figure has a `\label` but no `\ref` points to it, the figure exists in the PDF but no sentence ever says "see Figure 17" — that's an **orphan figure**.

### What "parbench compact" Means

All our TikZ charts share a common style template called `parbench compact` defined in `main_neurips.tex` (lines 56-77). It sets default width, height, grid style, and font sizes. Individual charts can override these defaults. When we say "harmonize," we mean making the overrides identical across model variants.

---

## The Three Problems and Their Fixes

### Problem 1: F5 Pass@k Charts — Scale Mismatch (CRITICAL)

**What it looks like in the PDF:** The Qwen pass@k bar chart (Figure 18) has tiny bars labeled "0.37", "0.23". The GPT chart (Figure 19) has tall bars labeled "83.3", "55.9". They're showing the same KIND of data (pass rates) but one is 0-to-1 and the other is 0-to-100%.

**Why it's wrong:** A reviewer comparing the two charts would think Qwen's performance is essentially zero, when actually 0.37 means 37%. The charts need the same y-axis scale to be visually comparable.

**The fix:** Open the Qwen F5 file, multiply all data values by 100, and update the axis parameters to match GPT/Codex.

**File to edit:** `.../figures/figures_tek_version/f5_pass_at_k_by_direction_qwen.tex`

**Specific changes (line numbers are approximate — always Read first):**

1. The data block near the top (lines 6-16) looks like:
   ```
   dir  p1    p3
   0    0.37  0.46
   1    0.23  0.31
   ...
   ```
   Change to:
   ```
   dir  p1    p3
   0    37    46
   1    23    31
   2    6     13
   3    1     4
   4    32    50
   5    8     20
   6    0     0
   7    63    90
   ```

2. In the axis options block:
   - `ymax=1.12` → `ymax=112`
   - `ytick={0,0.25,0.5,0.75,1.0}` → `ytick={0,20,40,60,80,100}`
   - DELETE the line `yticklabels={0.00,0.25,0.50,0.75,1.00}` (pgfplots will auto-label from ytick)
   - `ylabel={Average pass@$k$}` → `ylabel={Average pass@$k$ (\%)}`

3. In the `nodes near coords` format (the numbers printed on top of each bar):
   - `\pgfmathprintnumber[fixed,fixed zerofill,precision=2]` → `\pgfmathprintnumber[fixed,precision=1]`
   - This changes "0.37" → "37.0". (If you want integers like GPT/Codex, use `precision=0` instead for "37".)

**How to verify (no compilation needed):**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/figures_tek_version
grep -A20 'pgfplotstableread' f5_pass_at_k_by_direction_qwen.tex
# Data values should be 37, 46, 23, 31, etc. (NOT 0.37 or 3700)
grep 'ymax' f5_pass_at_k_by_direction_qwen.tex
# Should show: ymax=112
grep 'ylabel' f5_pass_at_k_by_direction_qwen.tex
# Should show: ylabel={Average pass@$k$ (\%)}
```

**Why these exact numbers:** The 0-1 values in the original file ARE correct — they just need to be expressed as percentages. 0.37 = 37% pass@1 for CUDA→OMP. This is consistent with Table 3 in the paper (which shows 40.3% per-record rate for the same direction — the difference is because pass@k uses the Chen et al. estimator while the table shows raw per-record rates).

---

### Problem 2: F4 Failure Taxonomy — Axis Inconsistencies

**What it looks like:** The Qwen failure taxonomy stacked bar chart (Figure 2, main text) auto-scales its y-axis, while the GPT (Figure 25) and Codex (Figure 27) versions lock to ymax=26 with gridlines every 5 units. The Qwen chart also uses a slightly larger font for x-axis labels.

**The fix:** Make Qwen match GPT/Codex on font size, y-axis limits, and tick marks.

**File to edit:** `.../figures/figures_tek_version/f4_failure_taxonomy_qwen.tex`

**IMPORTANT detail the plan-reviewer caught:** The tallest Qwen bars sum to exactly 26 (direction 0: 16+10+0+0+0 = 26). GPT/Codex bars peak at 24. If we set ymax=26 (like GPT), the bar annotations at the very top would be clipped. So we set **ymax=28** instead (giving 2 units of headroom, same relative margin as GPT/Codex have).

**Specific changes:**

1. Around line 10, change the x-tick label font:
   - `font=\footnotesize` → `font=\scriptsize`

2. Around line 13, after `ymin=0,` add two new lines:
   ```
   ymax=28,
   ytick={0,5,10,15,20,25},
   ```

**How to verify:**
```bash
grep 'ymax\|ytick\|scriptsize\|footnotesize' f4_failure_taxonomy_qwen.tex
# Should show: ymax=28, ytick={0,5,10,15,20,25}, font=\scriptsize
# Should NOT show: font=\footnotesize
```

---

### Problem 3: F3 Kernel Heatmaps — Four Visual Differences

**What it looks like:** The Qwen kernel heatmap (Figure 17) looks different from GPT (Figure 24) and Codex (Figure 26) in four ways:
1. Cells blend together (no white grid borders)
2. Legend says "Pass" / "N/A" instead of "PASS" / "NO EVAL"
3. Legend swatches have black borders instead of being borderless
4. No thick black lines separating Rodinia kernels from HeCBench kernels

**The fix:** Change the Qwen F3 to match GPT/Codex (since 2 of 3 already agree).

**File to edit:** `.../figures/figures_tek_version/f3_kernel_model_heatmap_qwen.tex`

**Specific changes:**

1. **Replace the 5 legend entries** (around lines 356-365). The Qwen file currently has something like:
   ```latex
   \addlegendentry{Pass}
   \addlegendentry{Build Fail}
   ...
   \addlegendentry{N/A}
   ```
   Replace with the GPT/Codex format (read the GPT file at `f3_kernel_model_heatmap_gpt_5-4.tex` lines 319-323 for the exact syntax):
   ```latex
   \addlegendimage{area legend, fill=pbPass!85, draw=none} \addlegendentry{PASS}
   \addlegendimage{area legend, fill=pbBuildFail!85, draw=none} \addlegendentry{BUILD FAIL}
   \addlegendimage{area legend, fill=pbRunFail!85, draw=none} \addlegendentry{RUN FAIL}
   \addlegendimage{area legend, fill=pbVerifyFail!85, draw=none} \addlegendentry{VERIFY FAIL}
   \addlegendimage{area legend, fill=pbNA!55, draw=none} \addlegendentry{NO EVAL}
   ```

2. **Add the white cell grid** BEFORE the legend entries (this draws thin white borders around each cell in the heatmap):
   ```latex
   \draw[white, line width=0.45pt] (axis cs:-0.5,-0.5) grid[xstep=1, ystep=1] (axis cs:7.5,34.5);
   ```

3. **Add black separator lines** (these thick horizontal lines visually separate Rodinia kernels from HeCBench-only kernels):
   ```latex
   \draw[black, line width=1.2pt] (axis cs:-0.5,22.5) -- (axis cs:7.5,22.5);
   \draw[black, line width=1.2pt] (axis cs:-0.5,24.5) -- (axis cs:7.5,24.5);
   ```

**How to verify:**
```bash
grep 'NO EVAL' f3_kernel_model_heatmap_qwen.tex        # Should appear once
grep -c 'draw=none' f3_kernel_model_heatmap_qwen.tex    # Should show 5
grep 'draw\[white' f3_kernel_model_heatmap_qwen.tex     # Should appear once
grep -c 'draw\[black.*1.2pt' f3_kernel_model_heatmap_qwen.tex  # Should show 2
```

---

### Problem 4: Orphan Figures — 6 Figures Nobody References

**What it looks like in the PDF:** These figures appear in the appendix with proper captions and numbers, but nowhere in the body text does it say "see Figure X." A reviewer would notice this.

**File to edit:** `.../appendices_neurips.tex`

**The 6 orphan figures:**

| Label | What it is | Where to add the reference |
|-------|-----------|---------------------------|
| `fig:augmentation` | Augmentation robustness line chart | After line ~1262, in the text discussing augmentation trends |
| `fig:aug-heatmap` | Per-kernel augmentation heatmap | Same location, same sentence |
| `fig:f3-qwen` | Qwen kernel heatmap | Appendix G intro (around line 1134) |
| `fig:pass-at-k-qwen` | Qwen pass@k by direction | Same Appendix G intro |
| `fig:cross-suite-qwen` | Qwen cross-suite comparison | Same Appendix G intro |
| `fig:f4-codex` | Codex failure taxonomy | Appendix I intro (around line 1613) |

**Exact edits:**

**4a.** Around line 1262, after the paragraph ending "...limit the strength of this conclusion.", INSERT:
```latex
Figure~\ref{fig:augmentation} plots the augmentation robustness trend across all three models; Figure~\ref{fig:aug-heatmap} shows the per-kernel augmentation status for the CUDA-to-OMP subset under \qwenshort{}.
```

**4b.** Around lines 1134-1135, REPLACE the existing intro text:
```
This appendix contains detailed evidence tables and figures referenced from the main text. Floats are ordered by their original section appearance.
```
WITH:
```latex
This appendix contains detailed evidence tables and figures referenced from the main text. Floats are ordered by their original section appearance. Per-kernel translation heatmaps appear in Figure~\ref{fig:f3-qwen} (\qwenshort{}), Figure~\ref{fig:f3-gpt} (\gptnew{}), and Figure~\ref{fig:f3-codex} (\codex{}). Pass@$k$ by direction appears in Figures~\ref{fig:pass-at-k-qwen}, \ref{fig:pass-at-k-gpt54}, and~\ref{fig:pass-at-k-codex}. Cross-suite comparisons appear in Figures~\ref{fig:cross-suite-qwen}, \ref{fig:cross-suite-gpt54}, and~\ref{fig:cross-suite-codex}.
```

**4c.** Around line 1613, find the sentence ending `"The full per-kernel table is in Table~\ref{tab:per-kernel-full-codex}."` and APPEND:
```latex
 The failure taxonomy appears in Figure~\ref{fig:f4-codex}.
```

**How to verify:**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
for fig in fig:aug-heatmap fig:augmentation fig:cross-suite-qwen fig:f3-qwen fig:f4-codex fig:pass-at-k-qwen; do
  count=$(grep -c "$fig" appendices_neurips.tex)
  echo "$fig: $count occurrences (need >=2: 1 label + 1 ref)"
done
```

---

### Problem 5: Orphan Tables — 5 Tables Nobody References

**Same file:** `.../appendices_neurips.tex`

**Strategy:** For each orphan table, first run the lookup command to find it, then add a `\ref` in the nearest discussion text.

```bash
# Run these first to locate each table:
grep -n 'tab:pass-at-k\b' appendices_neurips.tex | grep -v '%'
grep -n 'tab:stats-summary\b' appendices_neurips.tex | grep -v '%'
grep -n 'tab:aug-balanced\b' appendices_neurips.tex | grep -v '%'
grep -n 'tab:augmentation-rates\b' appendices_neurips.tex | grep -v '%'
grep -n 'tab:per-kernel-main\b' appendices_neurips.tex | grep -v '%'
```

**Fixes (apply after locating each table):**

1. **`tab:pass-at-k`** (the 3-model pass@k table): Add near line 1300: `"The full pass@$k$ estimates appear in Table~\ref{tab:pass-at-k}."`
2. **`tab:stats-summary`** (Qwen statistical summary): Add near the direction discussion: `"Table~\ref{tab:stats-summary} summarizes the direction asymmetry and augmentation trend tests."`
3. **`tab:aug-balanced`** (CUDA→OMP balanced augmentation): Add near line 1257 in the augmentation discussion.
4. **`tab:augmentation-rates`** (full augmentation rates): Add near the augmentation rates discussion.
5. **`tab:per-kernel-main`** (condensed per-kernel): Check if it's a duplicate of `tab:per-kernel-full`. If so, skip. If it's a condensed version, add a reference.

---

## Final Verification Checklist (Step 6)

Run this entire block after all edits are complete:

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/figures_tek_version

echo "=== F5 SCALE CHECK ==="
for f in f5_pass_at_k_by_direction_*.tex; do
  echo "--- $f ---"; grep 'ymax\|ytick\|ylabel' "$f"
done

echo "=== F4 AXIS CHECK ==="
for f in f4_failure_taxonomy_*.tex; do
  echo "--- $f ---"; grep 'ymax\|ytick\|scriptsize\|footnotesize' "$f"
done

echo "=== F3 LEGEND CHECK ==="
for f in f3_kernel_model_heatmap_*.tex; do
  echo "--- $f ---"; grep 'addlegendentry\|draw\[white\|draw\[black.*1.2' "$f"
done

echo "=== ORPHAN CHECK ==="
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
for label in fig:aug-heatmap fig:augmentation fig:cross-suite-qwen fig:f3-qwen fig:f4-codex fig:pass-at-k-qwen tab:pass-at-k tab:stats-summary tab:aug-balanced tab:augmentation-rates; do
  refs=$(grep -c "\\\\ref{$label}" appendices_neurips.tex sections/*.tex 2>/dev/null)
  echo "$label: $refs refs (need >=1)"
done
```

**What success looks like:**
- F5: All three files show `ymax=112`, `ytick={0,20,40,60,80,100}`, `ylabel` containing `(%)`
- F4: All three files show `font=\scriptsize`, explicit ymax and ytick
- F3: All three files show `NO EVAL` in legend, `draw[white` grid line, `draw[black.*1.2pt` separators
- Orphans: Every label shows ≥ 1 ref

**Additional checks for Steps 7-9 (run after those steps):**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version

echo "=== PNG-to-TikZ CONVERSION CHECK ==="
# Fig 3: should now use \input, not \includegraphics
grep -n 'api_cooccurrence_heatmap' appendices_neurips.tex
# Should show \input line, NO \includegraphics line

# Fig 9: same check
grep -n 'kernel_api_bubble' appendices_neurips.tex
# Should show \input line, NO \includegraphics line

# New TikZ files exist and are non-empty
for f in figures/figures_tek_version/api_cooccurrence_heatmap.tex figures/figures_tek_version/kernel_api_bubble.tex; do
  test -s "$f" && echo "OK: $f" || echo "FAIL: $f missing or empty"
done

echo "=== DEAD FILE CHECK ==="
# t2_model_comparison.tex should be deleted/moved
test -f figures/figures_tek_version/t2_model_comparison.tex && echo "FAIL: dead file still exists" || echo "OK: dead file removed"

echo "=== F6/F7 CONSISTENCY CHECK ==="
for f in figures/figures_tek_version/f6_cross_suite_comparison_*.tex; do
  echo "--- $f ---"; grep 'ymax\|ytick\|ylabel\|bar width' "$f"
done
grep 'parbench compact' figures/figures_tek_version/f7_augmentation_robustness.tex && echo "OK: F7 uses parbench compact"

echo "=== REMAINING PNG CHECK ==="
# Only 3 PNGs should remain (non-convertible): architecture PDF, 2 network graphs
grep -c 'includegraphics' appendices_neurips.tex sections/*.tex
# Should show 3 total (network_color_v7.png, verification_network.png, parbench_architecture)
```

---

## Things NOT To Do

1. **Do NOT modify GPT or Codex TikZ files** for F3/F4/F5 — only the Qwen variants need changes (2 of 3 already agree)
2. **DO convert the 2 data-chart PNGs to TikZ** (Fig 3: API heatmap, Fig 9: bubble chart) — see Steps 7-8. Do NOT convert the 3 non-convertible PNGs (architecture diagram, network graphs)
3. **Do NOT try to compile** — pdflatex is not installed. The user compiles via Overleaf.
4. **Do NOT modify result JSONs** — they are immutable research data
5. **Do NOT use GSD workflow commands** — direct editing is fine for this task per user instruction

---

## Skills to Load Before Starting

| When | Skill | Why |
|------|-------|-----|
| Before any edit | `andrej-karpathy-skills:karpathy-guidelines` | Required by CLAUDE.md for code changes |
| Before commit | `/validate` | Pre-commit hook requires waves 1-3 |

---

## Pre-flight Safety

Before making ANY edits, create a checkpoint:
```bash
cd /home/samyak/Desktop/parbench_sam
git stash push -m 'pre-figure-consistency' -- docs/paper/NeurIPS_ready_version/
```
If something goes wrong: `git stash pop` restores everything.

---

## Step 7: Convert Fig 3 (API co-occurrence heatmap) PNG → TikZ

**Current source:** `appendices_neurips.tex:469` includes `api_cooccurrence_heatmap.png` via `\includegraphics`.

**Why convert:** This is a data heatmap (29x29 matrix of integer counts). We already have a nearly identical TikZ heatmap: `kernel_level_cooccurrence_heatmap.tex` (Fig 5). Use that as a template.

**New file to create:** `.../figures/figures_tek_version/api_cooccurrence_heatmap.tex`

**How to build it:**
1. Read `.../figures/figures_tek_version/kernel_level_cooccurrence_heatmap.tex` as a template.
2. Read the PNG at `.../figures/api_cooccurrence_heatmap.png` to extract the data values (cell counts from the 29x29 matrix). The data is the number of repositories providing implementations in both row and column APIs.
3. Create the TikZ file with the same `parbench heatmap` style, same colorbar, same font sizing. Key differences from the kernel-level heatmap: 29 APIs instead of 12, and repository counts instead of kernel counts.
4. Update `appendices_neurips.tex:469` to replace:
   ```latex
   \includegraphics[width=\columnwidth]{api_cooccurrence_heatmap.png}
   ```
   with:
   ```latex
   \input{NeurIPS_ready_version/figures/figures_tek_version/api_cooccurrence_heatmap}
   ```

**Verification:**
```bash
test -f figures/figures_tek_version/api_cooccurrence_heatmap.tex && echo "File created"
grep 'input.*api_cooccurrence_heatmap' appendices_neurips.tex && echo "Reference updated"
grep -c 'includegraphics.*api_cooccurrence_heatmap' appendices_neurips.tex
# Should show 0 (PNG reference removed)
```

---

## Step 8: Convert Fig 9 (kernel-API bubble chart) PNG → TikZ

**Current source:** `appendices_neurips.tex:691` includes `kernel_api_bubble.png` via `\includegraphics`.

**Why convert:** This is a scatter/bubble chart with ~20 data points. pgfplots handles this natively with `scatter` + `visualization depends on` for bubble size.

**New file to create:** `.../figures/figures_tek_version/kernel_api_bubble.tex`

**How to build it:**
1. Read the PNG at `.../figures/kernel_api_bubble.png` to extract the data: each point is (x=number of APIs, y=number of kernels, size=total kernel count, color=benchmark type).
2. Key data points visible in the PDF (page 30): HeCBench (6 APIs, 522 kernels), RAJAPerf (5, 80), CloverLeaf (11, 23), BabelStream (12, 5), Rodinia (3, 22).
3. Use `parbench compact` style. Use `scatter` plot type with `scatter/@pre marker code` or `visualization depends on={\thisrow{size} \as \perpointmarksize}` for bubble sizing.
4. Color by benchmark type using the `pb*` palette colors (pbRodinia, pbHeCBench, etc.) or a category-based colormap.
5. Update `appendices_neurips.tex:691` to replace `\includegraphics` with `\input{...}`.

**Verification:**
```bash
test -f figures/figures_tek_version/kernel_api_bubble.tex && echo "File created"
grep 'input.*kernel_api_bubble' appendices_neurips.tex && echo "Reference updated"
grep -c 'includegraphics.*kernel_api_bubble' appendices_neurips.tex
# Should show 0
```

---

## Step 9: Clean up dead TikZ file + verify F6/F7 consistency

### 9a. Dead TikZ file
**File:** `.../figures/figures_tek_version/t2_model_comparison.tex`

This file exists but is NEVER `\input`'d anywhere in the paper. It is a dead asset. **Delete it** or move it to a `_unused/` subdirectory.

**Verification:**
```bash
grep -r 't2_model_comparison' /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/*.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/*.tex 2>/dev/null
# Should return no results (confirming it's unused)
```

### 9b. F6 cross-suite consistency audit
Read all three F6 files and confirm they are consistent (our earlier audit found them fully consistent — this is a verification step, not an edit step):
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/figures_tek_version
for f in f6_cross_suite_comparison_*.tex; do
  echo "=== $f ==="; grep 'ymax\|ytick\|ylabel\|bar width\|font.*footnotesize\|font.*scriptsize' "$f"
done
```
All three should show identical parameters. If any differ, harmonize them following the same pattern as Steps 1-3.

### 9c. F7 augmentation robustness audit
Only one F7 file exists (`f7_augmentation_robustness.tex`) — it combines all three models in a single chart. No cross-variant consistency issue. Just verify it uses `parbench compact` style:
```bash
grep 'parbench compact' f7_augmentation_robustness.tex
# Should return a match
```

---

## Files You Will Edit (6 total, + 2 new files)

| # | Absolute Path | What Changes |
|---|--------------|-------------|
| 1 | `.../figures/figures_tek_version/f5_pass_at_k_by_direction_qwen.tex` | Multiply data by 100, change ymax/ytick/ylabel/annotation format |
| 2 | `.../figures/figures_tek_version/f4_failure_taxonomy_qwen.tex` | Set ymax=28, ytick explicit, font=\scriptsize |
| 3 | `.../figures/figures_tek_version/f3_kernel_model_heatmap_qwen.tex` | Add white grid + black separators, fix legend to all-caps + "NO EVAL" + draw=none |
| 4 | `.../appendices_neurips.tex` | Add \ref{} for 6 orphan figures + 4-5 orphan tables; switch Fig 3 and Fig 9 from \includegraphics to \input |
| 5 | **NEW:** `.../figures/figures_tek_version/api_cooccurrence_heatmap.tex` | TikZ replacement for Fig 3 PNG (Step 7) |
| 6 | **NEW:** `.../figures/figures_tek_version/kernel_api_bubble.tex` | TikZ replacement for Fig 9 PNG (Step 8) |
| 7 | **DELETE:** `.../figures/figures_tek_version/t2_model_comparison.tex` | Dead file — never \input'd (Step 9a) |

All `...` = `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version`

## Files You Should READ (for reference, do not edit)

| File | Why |
|------|-----|
| `.../f3_kernel_model_heatmap_gpt_5-4.tex` | Reference for F3 legend format (lines 316-323) |
| `.../f4_failure_taxonomy_gpt_5-4.tex` | Reference for F4 axis params |
| `.../f5_pass_at_k_by_direction_gpt_5-4.tex` | Reference for F5 scale |

---

## Execution Order

```
Step 1 (F5 scale fix) — CRITICAL, do this first
  ↓
Step 2 (F4 axis fix)
  ↓
Step 3 (F3 heatmap fix)
  ↓
Step 4 (orphan figures)
  ↓
Step 5 (orphan tables)
  ↓
Step 6 (verification checklist for Steps 1-5)
  ↓
Step 7 (convert Fig 3 PNG → TikZ)
  ↓
Step 8 (convert Fig 9 PNG → TikZ)
  ↓
Step 9 (dead file cleanup + F6/F7 audit)
  ↓
Re-run Step 6 verification to cover all changes
  ↓
/validate → commit
```

Steps 1-5 are independent of each other. Steps 7-8 are independent of each other but should come after Steps 1-5 (so the appendices_neurips.tex orphan fixes from Step 4 don't conflict with the \input swaps in Steps 7-8). Step 9 can run anytime.
