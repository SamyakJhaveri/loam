# Phase 13: Paper.tex Figure & Table Wiring - Research

**Researched:** 2026-04-06
**Domain:** LaTeX paper.tex / appendices.tex figure and table reference wiring
**Confidence:** HIGH

## Summary

Phase 13 is a surgical LaTeX editing phase: update stale filenames, captions, and labels in `paper.tex` and `appendices.tex`, insert one new figure block, uncomment the architecture diagram, remove three placeholder figure blocks from appendices, and delete three obsolete files from disk. No code generation, no analysis scripts, no data pipeline changes.

All target files have been verified on disk. The changes are narrowly scoped: 7 edits to `paper.tex`, 8 edits to `appendices.tex`, 1 new figure block insertion, 3 file deletions. The CONTEXT.md provides exact line numbers and content for every change. Line numbers have been re-verified against the current files (paper.tex = 1117 lines, appendices.tex = 1365 lines) and all match.

**Primary recommendation:** Implement as 3-4 small plans: (1) architecture diagram wiring in paper.tex, (2) F3/F6/aug-heatmap figure updates across both files, (3) survey figure cleanup in appendices.tex, (4) stale file deletion. Each plan is independently verifiable via grep for stale references.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Add `aug_heatmap.pdf` in appendices.tex after the F7 figure block (after line 1221). F7 is now in appendices, so the per-kernel drill-down belongs there too.
- **D-02:** Add a reference in paper.tex's augmentation robustness section (around line 895) as "Appendix Figure~\ref{fig:aug-heatmap}".
- **D-03:** Brief caption: "Per-kernel augmentation status across levels L0--L4 (CUDA-to-OMP, Qwen~3.5). Cell color: pass/fail status."
- **D-04:** Skip `aug_trend.pdf` -- F7 covers the aggregate trend line.
- **D-05:** Update filename: `f6_xsbench_comparison.pdf` -> `f6_cross_suite_comparison.pdf` at appendices.tex:1254.
- **D-06:** New suite-focused caption at appendices.tex:1255.
- **D-07:** Rename label: `fig:xsbench` -> `fig:cross-suite` at appendices.tex:1256.
- **D-08:** Update `\ref{fig:xsbench}` -> `\ref{fig:cross-suite}` at paper.tex:977.
- **D-09:** Keep F6 in current appendix location (Appendix D, after pass@k figure).
- **D-10:** Delete old `f6_xsbench_comparison.pdf` and `.png` from `docs/paper/latex/figures/`.
- **D-11:** Update F3 caption at paper.tex:831 from "Triple-panel" to descriptive single-panel caption with 5 status colors.
- **D-12:** User exports drawio manually -> PDF before Phase 13 executes.
- **D-13:** Unconditionally uncomment `\includegraphics` at paper.tex:288, remove `\fbox` placeholder at line 289.
- **D-14:** Remove TODO comments at paper.tex lines 5, 284, and helper comment at line 285.
- **D-15:** Figure 1 caption (line 290) is accurate as-is -- no changes needed.
- **D-16:** Skip T2 table entirely.
- **D-17:** Delete stale `docs/paper/figures/t2_model_comparison.tex`.
- **D-18:** Skip all four companion figures (c1-c4).
- **D-19:** Remove all 3 figure blocks with `\fbox` placeholders for deleted images in appendices.tex.
- **D-20:** Update surrounding prose to remove undefined figure references after block removal.

### Claude's Discretion
- Exact `\begin{figure}` environment sizing for aug_heatmap (`figure` vs `figure*`)
- Whether aug_heatmap needs `\label` for cross-referencing (yes -- D-02 uses `\ref{fig:aug-heatmap}`)
- Minor prose adjustments around F6 in paper.tex:977 to match new cross-suite framing
- How to rephrase appendix survey prose after figure removal

### Deferred Ideas (OUT OF SCOPE)
- c1-c4 companion figures -- could be supplementary material in future revision
- `aug_trend.pdf` -- redundant with F7
- XSBench-specific comparison figure -- covered in Section 4.3 text
- Survey visualization images (api_cooccurrence, bipartite) -- could be restored if appendix page budget allows in camera-ready
- `quality_tiers.png` -- would need regeneration from scratch
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUG-04 | Augmentation trend graphs produced (per-kernel + aggregate, publication quality PDF+PNG, Okabe-Ito palette) | Graphs already exist on disk (aug_heatmap.pdf 37KB, f7_augmentation_robustness.pdf 14KB). Phase 13 wires them into LaTeX. The per-kernel heatmap (aug_heatmap.pdf) gets a new figure block in appendices.tex; the aggregate trend (F7) is already wired. This phase completes the "wiring" portion of AUG-04. |
</phase_requirements>

## Standard Stack

This phase uses no libraries or packages. It is a pure LaTeX text editing phase.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| LaTeX (IEEEtran) | N/A | Paper format | IEEE conference template -- already in use |
| Text editor (Claude Code) | N/A | Edit .tex files | Direct file editing via Edit tool |

### Supporting
No supporting libraries needed. All changes are hand-edits to two `.tex` files plus file deletion.

**Installation:** None required. No packages to install.

## Architecture Patterns

### File Layout
```
docs/paper/latex/
  paper.tex           # Main paper body (1117 lines) -- 7 edits
  appendices.tex      # Appendix content (1365 lines) -- 8 edits + 1 insertion
  figures/            # All figure PDFs and PNGs
    aug_heatmap.pdf              # EXISTS (37KB) -- to be wired
    f3_kernel_model_heatmap.pdf  # EXISTS (55KB) -- caption update
    f6_cross_suite_comparison.pdf # EXISTS (22KB) -- filename already correct
    f6_xsbench_comparison.pdf    # EXISTS (14KB) -- TO DELETE
    f6_xsbench_comparison.png    # EXISTS (86KB) -- TO DELETE
    f7_augmentation_robustness.pdf # EXISTS (14KB) -- already wired
    parbench_architecture.drawio # EXISTS (36KB) -- source for manual export
    parbench_architecture.pdf    # DOES NOT EXIST -- user must export before execution
docs/paper/figures/
  t2_model_comparison.tex        # EXISTS (395B) -- TO DELETE
  parbench_architecture.drawio   # EXISTS (36KB) -- source copy
```

### Pattern: LaTeX Figure Block (Single-Column)
Used by F7 and the new aug_heatmap block. [VERIFIED: appendices.tex lines 1216-1221]
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{filename.pdf}
\caption{Caption text.}
\label{fig:label-name}
\end{figure}
```

### Pattern: LaTeX Figure Block (Full-Width)
Used by Figure 1 (architecture). [VERIFIED: paper.tex lines 286-292]
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{parbench_architecture.pdf}
\caption{Caption text.}
\label{fig:architecture}
\end{figure*}
```

### Pattern: Cross-File References
`appendices.tex` is included via `\input{appendices}` at paper.tex:1108. All `\label` and `\ref` commands work across both files within the same compilation unit. A `\ref{fig:aug-heatmap}` in paper.tex will resolve to a `\label{fig:aug-heatmap}` in appendices.tex. [VERIFIED: paper.tex line 1108]

### graphicspath
`\graphicspath{{figures/}{../../analysis/visualizations/}}` at paper.tex:24. Both paper.tex and appendices.tex resolve figure paths relative to `docs/paper/latex/`. The `figures/` subdirectory is where all target PDFs live. [VERIFIED: paper.tex line 24]

### Anti-Patterns to Avoid
- **Editing line numbers without re-verifying**: After the first edit to a file, all subsequent line numbers shift. The planner must sequence edits bottom-to-top (highest line numbers first) within each file to preserve line references, OR re-read after each edit.
- **Forgetting the `\label` on new figure blocks**: D-02 uses `\ref{fig:aug-heatmap}` in paper.tex -- the label MUST exist in the appendices.tex figure block or LaTeX will produce an undefined reference warning.
- **Assuming parbench_architecture.pdf exists**: It does NOT exist yet. D-12 states the user exports it manually before execution. Phase 13 must verify file existence as a pre-condition.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drawio-to-PDF export | CLI export script | User's draw.io desktop app | drawio CLI not installed on this machine; user decision D-12 explicitly makes this manual |
| LaTeX compilation check | Custom build script | Grep for undefined refs / stale filenames | pdflatex is NOT installed on this Linux machine; verify via grep instead |
| Figure existence validation | Inline file stat in LaTeX | `ls` / `test -f` shell commands | Simple and reliable |

**Key insight:** LaTeX is not installed on this machine (no pdflatex, no bibtex). All verification must be done via text-based checks (grep for undefined `\ref`, grep for stale filenames, `ls` for file existence) rather than compilation.

## Common Pitfalls

### Pitfall 1: Line Number Drift After Edits
**What goes wrong:** CONTEXT.md specifies exact line numbers (e.g., paper.tex:831, appendices.tex:1254). After the first edit adds or removes lines, all subsequent line numbers are stale.
**Why it happens:** LaTeX files have no stable anchors like function names -- only line numbers and surrounding content.
**How to avoid:** Either (a) edit bottom-to-top within each file so earlier line numbers remain valid, or (b) use content-based matching (grep for the specific text) rather than line numbers for each edit.
**Warning signs:** An edit lands on the wrong line, corrupting adjacent content.

### Pitfall 2: Missing Architecture PDF Pre-Condition
**What goes wrong:** Phase 13 uncomments `\includegraphics{parbench_architecture.pdf}` but the PDF does not exist, causing LaTeX compilation failure.
**Why it happens:** D-12 requires the user to manually export the drawio file before Phase 13 runs.
**How to avoid:** First task in the plan must verify `docs/paper/latex/figures/parbench_architecture.pdf` exists. If not, STOP and alert the user.
**Warning signs:** `ls docs/paper/latex/figures/parbench_architecture.pdf` returns "No such file".

### Pitfall 3: Orphaned Cross-References
**What goes wrong:** Renaming `\label{fig:xsbench}` to `\label{fig:cross-suite}` but missing a `\ref{fig:xsbench}` somewhere, causing an undefined reference.
**Why it happens:** References can appear in either paper.tex or appendices.tex.
**How to avoid:** After all edits, grep BOTH files for any remaining `fig:xsbench`, `fig:api-network`, `fig:bipartite`, `fig:quality-tiers` references. All must return zero matches.
**Warning signs:** Grep finds residual old labels/refs.

### Pitfall 4: Deleting Wrong Files
**What goes wrong:** Deleting a file that's still referenced, or deleting from the wrong directory.
**Why it happens:** There are TWO figure directories: `docs/paper/figures/` and `docs/paper/latex/figures/`.
**How to avoid:** Double-check exact paths. The old F6 files are in `docs/paper/latex/figures/`. The T2 table is in `docs/paper/figures/` (no `latex/` prefix).
**Warning signs:** `git status` shows unexpected deletions.

### Pitfall 5: Figure Block Removal Leaving Orphan Prose
**What goes wrong:** Removing a `\begin{figure}...\end{figure}` block but leaving the prose that references it with `Figure~\ref{fig:X}`.
**Why it happens:** The prose and figure block are separate in the LaTeX source.
**How to avoid:** For each of the 3 survey figure removals (D-19), also update the surrounding prose (D-20). The exact lines are documented in CONTEXT.md's `code_context` section.
**Warning signs:** Grep finds `\ref{fig:api-network}` or `\ref{fig:bipartite}` after cleanup.

## Code Examples

### Example 1: Uncommenting Architecture Diagram (D-13/D-14)

**Before** (paper.tex lines 284-289):
```latex
% TODO: Export parbench_architecture.drawio to PDF before compilation
% Once the PDF exists, uncomment the \includegraphics and remove the \fbox placeholder.
\begin{figure*}[t]
\centering
% \includegraphics[width=\textwidth]{parbench_architecture.pdf}
\fbox{\parbox{0.95\textwidth}{\centering\vspace{2em}\textbf{[Figure placeholder --- export parbench\_architecture.drawio to PDF]}\vspace{2em}}}
```
[VERIFIED: paper.tex lines 284-289]

**After:**
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{parbench_architecture.pdf}
```

Also remove TODO at line 5: `% TODO: Export parbench_architecture.drawio to PDF before compilation`

### Example 2: F6 Reference Update (D-05/D-06/D-07)

**Before** (appendices.tex lines 1252-1257):
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f6_xsbench_comparison.pdf}
\caption{XSBench cross-granularity comparison. ParBench kernel-level vs.\ ParEval-Repo repository-level pass rates on the same computational kernel.}
\label{fig:xsbench}
\end{figure}
```
[VERIFIED: appendices.tex lines 1252-1257]

**After:**
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f6_cross_suite_comparison.pdf}
\caption{Cross-suite pass rate comparison (L0, Qwen~3.5). Per-suite aggregate pass rates with Wilson 95\% CIs across all 5 benchmark suites.}
\label{fig:cross-suite}
\end{figure}
```

### Example 3: F6 Reference in paper.tex (D-08)

**Before** (paper.tex line 977):
```latex
Cross-suite comparison is shown in Appendix Figure~\ref{fig:xsbench}.
```
[VERIFIED: paper.tex line 977]

**After:**
```latex
Cross-suite comparison is shown in Appendix Figure~\ref{fig:cross-suite}.
```

### Example 4: F3 Caption Update (D-11)

**Before** (paper.tex line 831):
```latex
\caption{Kernel $\times$ model heatmap. Triple-panel: CUDA-to-OMP, OMP-to-CUDA, CUDA-to-OpenCL. Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), blue (VERIFY\_FAIL), pink (EXTRACTION\_FAIL).}
```
[VERIFIED: paper.tex line 831]

**After:**
```latex
\caption{Per-kernel pass/fail heatmap across 6 standard translation directions (29 kernels, L0, Qwen~3.5). Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), blue (VERIFY\_FAIL), pink (EXTRACTION\_FAIL).}
```

### Example 5: Aug Heatmap Insertion (D-01/D-02/D-03)

**New block** inserted in appendices.tex after line 1221 (after F7 figure):
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{aug_heatmap.pdf}
\caption{Per-kernel augmentation status across levels L0--L4 (CUDA-to-OMP, Qwen~3.5). Cell color: pass/fail status.}
\label{fig:aug-heatmap}
\end{figure}
```

**Reference** added in paper.tex after line 895:
```latex
The per-kernel augmentation heatmap is provided in Appendix Figure~\ref{fig:aug-heatmap}.
```

### Example 6: Survey Figure Block Removal (D-19/D-20)

**api-network prose fix** (appendices.tex line 51):
- **Before:** `The force-directed network visualization in Figure~\ref{fig:api-network} makes`
- **After:** `The force-directed network visualization makes` (or similar rephrasing that removes the figure reference)

Then remove the entire figure block at lines 56-73 (the TODO comment + `\begin{figure}...\end{figure}`).

**bipartite prose fix** (appendices.tex lines 357-358):
- **Before:** `with~14). Figure~\ref{fig:bipartite} visualizes this heterogeneity as a bipartite network.`
- **After:** `with~14). This heterogeneity forms a bipartite network structure.` (or similar)

Then remove the entire figure block at lines 360-378.

**quality-tiers block** (appendices.tex lines 410-421): Remove entire block. No prose reference exists (verified: grep for `\ref{fig:quality-tiers}` returns zero matches).

## Verified File State (Pre-Execution Inventory)

All claims verified by direct file reads on 2026-04-06:

| File | Status | Verified |
|------|--------|----------|
| `docs/paper/latex/paper.tex` | 1117 lines, all target lines verified | [VERIFIED: wc -l + Read] |
| `docs/paper/latex/appendices.tex` | 1365 lines, all target lines verified | [VERIFIED: wc -l + Read] |
| `docs/paper/latex/figures/aug_heatmap.pdf` | EXISTS, 37KB | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/f3_kernel_model_heatmap.pdf` | EXISTS, 55KB | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/f6_cross_suite_comparison.pdf` | EXISTS, 22KB | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/f6_xsbench_comparison.pdf` | EXISTS, 14KB -- TO DELETE | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/f6_xsbench_comparison.png` | EXISTS, 86KB -- TO DELETE | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/f7_augmentation_robustness.pdf` | EXISTS, 14KB | [VERIFIED: ls -la] |
| `docs/paper/latex/figures/parbench_architecture.pdf` | DOES NOT EXIST | [VERIFIED: ls -la returns ENOENT] |
| `docs/paper/latex/figures/parbench_architecture.drawio` | EXISTS, 36KB | [VERIFIED: ls -la] |
| `docs/paper/figures/t2_model_comparison.tex` | EXISTS, 395B -- TO DELETE | [VERIFIED: ls -la] |
| `docs/paper/figures/parbench_architecture.drawio` | EXISTS, 36KB (copy) | [VERIFIED: ls -la] |

### Cross-Reference Audit

| Label | Current Location | References | Action |
|-------|------------------|------------|--------|
| `fig:xsbench` | appendices.tex:1256 | paper.tex:977 | Rename to `fig:cross-suite`, update ref |
| `fig:api-network` | appendices.tex:72 | appendices.tex:51 | Delete label (block removal), update prose |
| `fig:bipartite` | appendices.tex:377 | appendices.tex:357 | Delete label (block removal), update prose |
| `fig:quality-tiers` | appendices.tex:420 | NONE | Delete label (block removal), no prose fix needed |
| `fig:aug-heatmap` | NEW (to be created) | paper.tex:~895 (to be added) | Create label in new block, add ref |
| `fig:architecture` | paper.tex:291 | paper.tex:297 (and others) | No change -- just uncomment includegraphics |
| `fig:kernel-heatmap` | paper.tex:832 | paper.tex (multiple) | No label change -- caption update only |
| `t2_model_comparison` | NOT referenced in .tex | NONE | Safe to delete from disk |

[VERIFIED: All cross-references checked via grep across both files]

## Edit Sequencing Strategy

**Critical insight:** Edits within a single file must be sequenced to avoid line-number drift. Two strategies:

### Strategy A: Bottom-to-Top (Recommended)
Edit the highest line numbers first within each file. This ensures earlier line numbers remain valid.

**paper.tex edit order:**
1. Line 977: `\ref{fig:xsbench}` -> `\ref{fig:cross-suite}` (+ prose tweak)
2. Line ~895: Insert aug_heatmap reference line
3. Line 831: F3 caption update
4. Lines 284-289: Architecture diagram (remove TODO, comments, placeholder; uncomment includegraphics)
5. Line 5: Remove TODO comment

**appendices.tex edit order:**
1. Lines 1252-1257: F6 filename, caption, label update
2. After line 1221: Insert aug_heatmap figure block
3. Lines 410-421: Remove quality_tiers figure block
4. Lines 360-378: Remove bipartite figure block + update prose at 357
5. Lines 56-73: Remove api-network figure block + update prose at 51

### Strategy B: Content-Based Matching
Use `grep` to find exact content strings rather than relying on line numbers. More robust but slower.

**Recommendation:** Strategy A (bottom-to-top) is simpler for this phase because CONTEXT.md provides exact content at each line, and there are few enough edits to track.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pdflatex | LaTeX compilation verification | NO | -- | Verify via grep for stale refs and file existence checks |
| bibtex | Bibliography compilation | NO | -- | Not needed for figure/table wiring |
| drawio CLI | Architecture diagram export | NO | -- | User exports manually per D-12 |
| git | File deletion and commit | YES | (system) | -- |

**Missing dependencies with no fallback:**
- None that block execution. All changes are text edits and file deletions.

**Missing dependencies with fallback:**
- pdflatex not installed -- verification of "no LaTeX warnings" (Success Criterion 5) must use text-based grep checks instead of compilation. This is sufficient for the types of errors this phase can introduce (undefined refs, stale filenames).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Shell-based grep verification (no LaTeX compiler) |
| Config file | None needed |
| Quick run command | `grep -rn 'fig:xsbench\|f6_xsbench\|Triple-panel\|api_cooccurrence_network\|benchmark_api_bipartite\|quality_tiers\.png\|t2_model_comparison' docs/paper/latex/` |
| Full suite command | Quick run + file existence checks |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUG-04-wire | aug_heatmap.pdf wired into appendices.tex | grep | `grep -c 'aug_heatmap' docs/paper/latex/appendices.tex` (expect >= 1) | N/A (shell) |
| SC-F6 | F6 updated to cross-suite | grep | `grep -c 'f6_xsbench' docs/paper/latex/appendices.tex` (expect 0) | N/A |
| SC-F3 | F3 caption updated | grep | `grep -c 'Triple-panel' docs/paper/latex/paper.tex` (expect 0) | N/A |
| SC-ARCH | Architecture diagram wired | grep | `grep -c 'includegraphics.*parbench_architecture' docs/paper/latex/paper.tex` (expect 1, not commented) | N/A |
| SC-T2 | T2 deleted | file | `test ! -f docs/paper/figures/t2_model_comparison.tex` | N/A |
| SC-F6DEL | Old F6 deleted | file | `test ! -f docs/paper/latex/figures/f6_xsbench_comparison.pdf` | N/A |
| SC-REFS | No stale refs | grep | `grep -rn 'fig:xsbench\|fig:api-network\|fig:bipartite\|fig:quality-tiers' docs/paper/latex/` (expect 0) | N/A |

### Sampling Rate
- **Per task commit:** Quick grep command above
- **Per wave merge:** Full suite (grep + file existence)
- **Phase gate:** All 7 checks pass before `/gsd-verify-work`

### Wave 0 Gaps
None -- verification is shell-based grep, no test framework needed.

## Security Domain

Not applicable. This phase edits LaTeX files only. No authentication, user input handling, cryptography, or access control involved.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The user will export `parbench_architecture.drawio` to PDF before Phase 13 execution | Architecture Patterns | If PDF missing, `\includegraphics` will cause LaTeX compile error; mitigated by pre-condition check in plan |
| A2 | No other files reference `fig:xsbench` besides paper.tex:977 | Cross-Reference Audit | If another ref exists, it becomes undefined; mitigated by grep verification |
| A3 | `\graphicspath` in paper.tex applies to appendices.tex (since it's `\input`-ed) | Architecture Patterns | If not, figure paths in appendices need different resolution; LOW risk -- this is standard LaTeX behavior |

A1 is user-confirmed (D-12). A2 and A3 are verified by grep and file read respectively.

## Open Questions

1. **Architecture PDF pre-condition**
   - What we know: User committed to export manually (D-12). File does NOT exist yet.
   - What's unclear: Whether the user has done this yet.
   - Recommendation: Plan Wave 0 / Task 1 checks for file existence. If missing, task blocks with clear message to user.

2. **Aug heatmap figure sizing**
   - What we know: CONTEXT.md leaves `figure` vs `figure*` to Claude's discretion. F7 uses `figure` (single-column).
   - What's unclear: Whether the heatmap (29 kernels x 5 levels) is legible at single-column width.
   - Recommendation: Use `figure` (single-column) to match F7's style. The heatmap is a matrix with color cells, not detailed text, so single-column should be legible. If not, it can be changed to `figure*` in camera-ready.

3. **Prose rephrasing for removed survey figures**
   - What we know: Two paragraphs reference figures that will be removed. `fig:quality-tiers` has no prose refs.
   - What's unclear: Exact wording for rephrased prose.
   - Recommendation: Minimal rephrasing -- remove the `Figure~\ref{...}` clause and adjust grammar. The descriptive content stays.

## Sources

### Primary (HIGH confidence)
- paper.tex direct read (lines 1-1117) -- all target line content verified
- appendices.tex direct read (lines 1-1365) -- all target line content verified
- `ls -la` on all figure files -- existence and sizes confirmed
- `grep` across both .tex files for all affected labels and references

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions D-01 through D-20 -- user-confirmed in discuss phase, line numbers re-verified against current files

### Tertiary (LOW confidence)
- None. All claims verified against actual files.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no libraries needed, pure text editing
- Architecture: HIGH -- all file locations, line contents, and cross-references verified by direct read
- Pitfalls: HIGH -- based on verified file state and known LaTeX behavior

**Research date:** 2026-04-06
**Valid until:** 2026-04-08 (SC26 deadline -- line numbers may shift if other phases edit these files first)
