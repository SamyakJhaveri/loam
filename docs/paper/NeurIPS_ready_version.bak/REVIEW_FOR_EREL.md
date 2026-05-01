# ParBench NeurIPS Paper — Self-Critic Review & Page-Limit Fix Instructions

**Date:** 2026-04-28 (revised 2026-04-29 after cross-model critique)
**Reviewer:** Claude Opus (adversarial self-review) + Codex GPT-5.4 (cross-model critique)
**For:** Erel (co-author implementing fixes)
**Paper:** `docs/paper/NeurIPS_ready_version/main_neurips.tex`

> **Revision note (2026-04-29):** A cross-model critique session (Codex/GPT-5.4 + Opus self-review) found 8 issues with the original review. This revision fixes: CUT-1 dangling colon, CUT-2 lost disjoint-set semantics, CUT-4 missing strategy type, Qwen-only augmentation table in main body (FRAMING-4), architecture figure PNG→PDF (BUG-5), `\tbd` macro removal (BUG-4), rounding precision note, and bibliography cleanup note.

## Background for Someone Reading This Fresh

This paper presents **ParBench**, a benchmark for evaluating whether LLMs can translate parallel code (e.g., CUDA → OpenMP → OpenCL). The paper has:

- A **main body** (abstract through Discussion) — must fit in **9 pages** per NeurIPS rules
- An **appendix** after the references — unlimited pages
- A **NeurIPS checklist** at the end — required, does not count toward page limit

The main body is currently **~11–12 pages** when compiled. We need to cut ~2–3 pages by moving detail to the appendix without losing the core narrative. There are also several bugs and checklist issues.

All file paths below are relative to `docs/paper/NeurIPS_ready_version/`.

---

## Part 1: CRITICAL BUGS (fix immediately, regardless of page limit)

### BUG-1: Broken citation command (discussion.tex, line 12)

**What's wrong:** The text reads `ParaCodex~cite{ADD\_CITE\_TODO}`. Two bugs:
1. Missing backslash — should be `\cite{...}` not `cite{...}`
2. The key is a placeholder — but `ParaCodex2026` already exists in `references.bib`

**How it renders:** The PDF will show the literal text "cite" followed by "ADD_CITE_TODO" in the bibliography-error style. Instantly visible to any reviewer.

**Fix:** In `sections/discussion.tex`, line 12, change:
```
ParaCodex~cite{ADD\_CITE\_TODO}
```
to:
```
ParaCodex~\cite{ParaCodex2026}
```

**Verification:** Compile the paper and confirm no "undefined citation" warnings for ParaCodex.

---

### BUG-2: Triple-duplicated sentence (experimental-setup.tex, ~line 107)

**What's wrong:** In Section 4.5 "Canonical Evaluation (L0)", the sentence "Most specs verify via exit-code and stdout-pattern checks that rely on each benchmark's self-checking output; a subset additionally declare numeric-comparison or file-hash oracles for quantitative output verification (Section~\ref{sec:harness})." appears **three times in a row**.

**How it renders:** Reviewers will see the same sentence repeated three times consecutively. This signals careless editing and wastes ~4 lines of space.

**Fix:** In `sections/experimental-setup.tex`, find the paragraph starting "The canonical campaign evaluates all 142 unique pairs". Keep only the **first** occurrence of the duplicated sentence. Delete the second and third copies.

The paragraph should end after one occurrence of that sentence.

**Verification:** Read the paragraph aloud — it should flow naturally without repetition.

---

### BUG-3: Abstract mixes metric scopes (abstract.tex, line 4)

**What's wrong:** The abstract reports pass@1 and pass@3 (computed over 142 L0 tasks only, per `paper_data` files), then states "Build-stage adaptation failures account for 39.1% of Qwen outcomes." The 39.1% figure comes from **all 626 records** (426 L0 + 200 ablation), not from the 142 L0 tasks. In L0-only, BUILD_FAIL is actually **50.0%** (213/426).

**Why it matters:** A reviewer who checks the 39.1% against L0-only data will get 50.0% and think the paper is wrong. The 39.1% is technically correct (it says "outcomes" not "L0 outcomes"), but the abstract is discussing L0 results in the preceding sentences, making this misleading.

**Two options:**
- **(A) Use the L0-only figure:** Change "39.1%" to "50.0%" and add "of L0" — e.g., "Build-stage adaptation failures account for 50.0% of L0 Qwen outcomes"
- **(B) Clarify the scope:** Change to "Across all evaluation records (canonical and ablation), build-stage adaptation failures account for 39.1% of Qwen outcomes"
- **(C) Keep 39.1% but make scope explicit:** "Overall, build-stage failures account for 39.1% of all 626 Qwen records"

**Recommendation:** Option A is cleanest for the abstract since everything else there is about L0.

**Data verification:**
- L0 BUILD_FAIL: 213 / 426 = 50.0% (from `paper_data_together-qwen-3.5-397b-a17b.json` > `passk_campaign > overall > by_status`)
- Overall BUILD_FAIL: 245 / 626 = 39.1% (from `quantitative_findings_qwen.json` > `canonical > failure_taxonomy`)

---

## Part 2: PAGE LIMIT — What to Move to Appendix

The NeurIPS Datasets & Benchmarks track allows **9 pages** for the main body. References, appendix, and checklist are unlimited. The current main body is ~11–12 pages. Below are the cuts, ordered by space savings (largest first). Each cut includes the exact text to remove and what to replace it with.

**Target: cut ~2.5–3 pages** from the main body.

### CUT-1: Remove Listing 1 (BFS spec JSON) — saves ~0.5 pages

**File:** `sections/framework.tex`, lines 60–101

**What it is:** A 35-line JSON code listing showing a condensed BFS spec. This is already duplicated in the appendix (`appendices_neurips.tex`, lines 37–74, label `lst:bfs_spec_appendix`).

**What to cut:** Everything from `\begin{lstlisting}[` (line 60) through the `\end{lstlisting}` and the `\noindent` sentence after it (line 101).

**IMPORTANT — also fix line 58:** The line just before the listing currently ends with a colon:
```
Listing~\ref{lst:bfs_spec_appendix} illustrates the essential structure using an example of the BFS benchmark from Rodinia suite~\cite{Rodinia2009}:
```
After removing the listing, this colon will dangle. **Replace the entire line 58** with the following (note: period instead of colon, and adds the appendix cross-reference):

```latex
Listing~\ref{lst:bfs_spec_appendix} in Appendix~\ref{sec:appendix-framework} 
illustrates the spec structure using Rodinia's BFS kernel. Most specs declare 
\texttt{exit\_code} and \texttt{stdout\_pattern} checks; a subset use 
\texttt{numeric\_comparison} or \texttt{file\_hash} for stronger oracles 
(Section~\ref{sec:harness}).
```

**Why this is safe:** The listing is already in the appendix with label `lst:bfs_spec_appendix`, so the `\ref` resolves. The main-body listing uses a *different* label (`lst:bfs_spec`) which is never referenced anywhere — removing it breaks nothing. The main body retains the conceptual description of what a spec contains.

---

### CUT-2: Condense spec schema field-group descriptions — saves ~0.6 pages

**File:** `sections/framework.tex`, lines 45–57

**What it is:** Four bold-headed paragraphs describing the five field groups in a spec JSON (Identity and provenance, File partitioning, Build/run/verification, Baseline results). These are detailed descriptions of JSON schema fields — important for reproducibility but too granular for a 9-page main body.

**What to cut:** Everything from "A spec is organized into the following field groups:" (line 45) through the end of the "Baseline results" paragraph (line 56), *including* the paragraph about "This design separates the definition of correctness..." (line 54) — keep only its last sentence about the 96 specs.

**What to replace it with:**

```latex
Each spec encodes five field groups: identity and provenance (unique 
identifier, source suite, API, repository commit), file partitioning 
(disjoint sets of prompt payload, support files, and verification-only 
files, with \texttt{translation\_targets} identifying the subset of 
prompt payload the LLM must translate), build configuration (compiler 
commands, expected executable), run configuration (arguments, timeouts), 
and conjunctive verification strategies applied via five strategy types 
(exit code, stdout pattern, stdout exclusion pattern, numeric comparison, 
and file hash). The file partitioning is central to the kernel-centric 
methodology: the LLM translates only the designated kernel files while 
build infrastructure remains fixed 
(Section~\ref{sec:eval-pipeline}). Full field definitions appear in 
Appendix~\ref{sec:appendix-framework-schema}.

We have defined 96 such specs spanning five benchmark suites: 60 from 
Rodinia~\cite{Rodinia2009}, 4 from XSBench~\cite{XSBench2014}, 4 from 
RSBench, 3 from mixbench, and 25 from a curated subset of 
HeCBench~\cite{HeCBench2023}. Of these, 87 pass the baseline 
build/run/verify pipeline; the remaining 9 (\knownfail{} specs) are 
excluded from evaluation (Section~\ref{sec:benchmark-curation}).
```

**Why this is safe:** The appendix already contains the full schema description (Appendix A). The replacement preserves two details the original CUT-2 draft lost: (1) that the file sets are **disjoint** and `translation_targets` is a **subset** of `prompt_payload` (the key design choice), and (2) that there are **five** verification strategy types (including `stdout_exclude_pattern`, which is used by `backprop-opencl` and mentioned elsewhere in the paper).

---

### CUT-3: Condense Response Extraction + Complexity Taxonomy — saves ~0.3 pages

**File:** `sections/framework.tex`, lines 125–127

**What it is:** Two paragraphs at the end of Section 2.2:
1. "Response extraction" — a detailed description of the 4-tier fallback parser
2. "Complexity taxonomy" — defines single_file, multi_to_single, etc.

These are implementation details. The response extraction is important but the 4-tier detail is appendix material. The complexity taxonomy is used in results but can be defined briefly.

**What to cut:** The full "Response extraction" paragraph (starting "The evaluation pipeline parses each LLM response...") and the "Complexity taxonomy" paragraph.

**What to replace it with:**

```latex
\textbf{Response extraction.} The pipeline parses each LLM response 
using a multi-tier fallback strategy to recover translated files from 
fenced code blocks (details in Appendix~\ref{sec:appendix-framework}). 
If any expected file cannot be recovered, the task is classified as 
\extractionfail{}.

\textbf{Complexity taxonomy.} Each task is classified by file 
cardinality: \texttt{single\_file} ($1{\to}1$), 
\texttt{multi\_to\_single} ($N{\to}1$), \texttt{single\_to\_multi} 
($1{\to}N$), or \texttt{multi\_to\_multi} ($N{\to}M$).
```

**Why this is safe:** The 4-tier parsing strategy is an implementation detail that doesn't affect the paper's claims. Moving it to appendix reduces main-body density without losing information.

*Note:* You need to add a subsection in the appendix's "Framework and Evaluation Details" (Appendix A) describing the 4-tier response extraction. Take the original paragraph from framework.tex and paste it there.

---

### CUT-4: Condense harness pipeline detail — saves ~0.4 pages

**File:** `sections/framework.tex`, lines 163–178

**What it is:** Section 2.4 "Harness Pipeline: Build, Run, Verify" — currently ~40 lines with three bold subsections (Build stage, Run stage, Verify stage) each describing subprocess-level implementation details (template variable substitution, `/usr/bin/time -v` wrapping, etc.), plus the oracle-strength distribution paragraph.

**What to keep (essential):**
- The 3-stage concept with short-circuit-on-failure
- The Gaussian elimination example (proves conjunctive verification matters)
- The five failure classifications
- One sentence about oracle strength

**What to cut:** The detailed subprocess descriptions in each stage paragraph. The "Of the 87 non-KNOWN_FAIL specs, 5 use numeric comparison..." paragraph can be condensed to one sentence.

**What to replace it with:**

```latex
\subsection{Harness Pipeline: Build, Run, Verify}
\label{sec:harness}

The harness pipeline evaluates translated code through three sequential 
stages—build, run, verify—with failure at any stage short-circuiting 
subsequent stages (Figure~\ref{fig:architecture}, light blue). The build 
stage compiles the translated code using the spec's build commands with 
platform-specific path substitution; the run stage executes the binary 
with spec-defined arguments and timeout; the verify stage applies the 
spec's verification strategies in conjunction (all must pass).

Conjunctive verification is essential for accurate measurement. For 
example, a CUDA translation of Gaussian elimination compiles without 
error, runs to completion with exit code zero, and produces partial 
output—but fails to print the expected timing summary. 
Compilation-only~\cite{CodeRosetta2024} or exit-code-only verification 
would misclassify this as successful. Five verification strategy types 
are available (exit code, stdout pattern, stdout exclusion pattern, 
numeric comparison, file hash); of the 87 non-\knownfail{} specs, 7 use 
stronger oracles (numeric comparison or file hash) while the remaining 
80 rely on exit-code and stdout-pattern checks that capture each 
benchmark's self-checking output. Implementation details for each stage 
appear in Appendix~\ref{sec:appendix-framework}.

Each invocation produces one of four classifications—\buildfail{}, 
\runfail{}, \verifyfail{}, or TIMEOUT—enabling the failure-mode analysis 
in Section~\ref{sec:failure-taxonomy}. The evaluation pipeline adds 
\extractionfail{} when the LLM response is unparseable.
```

**Why this is safe:** The core argument (conjunctive verification catches errors other approaches miss) is preserved. Implementation details (template variables, `/usr/bin/time -v`, etc.) move to appendix.

*Note:* Copy the original detailed Build/Run/Verify stage paragraphs into Appendix A under a new subsection "Harness Implementation Details."

---

### CUT-5: Condense HeCBench selection funnel — saves ~0.25 pages

**File:** `sections/benchmark-curation.tex`, lines 57–67

**What it is:** A 5-item enumerated list detailing each stage of the HeCBench selection funnel (4-API filter → build system filter → self-checking filter → complexity filter → domain diversity). This funnel is already documented in *much more detail* in Appendix B3 (`appendices_neurips.tex`, lines 523–554).

**What to cut:** The full `\begin{enumerate}...\end{enumerate}` block (lines 59–65).

**What to replace it with:**

```latex
A structured five-stage selection funnel 
(Appendix~\ref{sec:appendix-b3}) reduced HeCBench's 516 kernels to a 
curated subset: filtering for 4-API completeness (327), build 
infrastructure (325), self-checking output (242), complexity bounds, and 
domain diversity yielded 60 candidates, from which \textbf{10 kernels} 
with verified OMP-target variants were selected for the evaluation 
corpus.
```

**Why this is safe:** The funnel is reproduced in full in Appendix B3. The main body retains the key numbers (516 → 10) and the selection criteria summary.

---

### CUT-6: Remove API feature coverage paragraph — saves ~0.2 pages

**File:** `sections/benchmark-curation.tex`, lines 205–208

**What it is:** A paragraph cataloging OpenMP version ranges (v1.0 through v4.5), CUDA features (`__syncthreads`, Unified Memory, warp shuffle), and OpenCL version. This is reference material, not narrative.

**What to cut:** The entire paragraph starting "The corpus exercises API features spanning multiple specification versions."

**What to replace it with:**

```latex
The corpus exercises API features spanning OpenMP versions 1.0 through 
4.5 (including target offload), CUDA features from basic synchronization 
through warp intrinsics, and OpenCL~1.x command queues; the full API 
feature inventory appears in Appendix~\ref{sec:appendix-b}.
```

*Note:* Move the detailed paragraph to Appendix B (Benchmark Kernel Survey), adding it as a new subsection "API Feature Coverage" after the existing content.

---

### CUT-7: Condense augmentation ablation design — saves ~0.15 pages

**File:** `sections/experimental-setup.tex`, lines 112–118

**What it is:** Section 4.6 (Augmentation Ablation) — currently explains the L0-conditional filter design in detail, including the rationale for the filter, qualifying pair counts, and the single-sample tradeoff.

**What to keep:** The key facts — the filter definition, qualifying counts, and caveat.

**What to replace it with:**

```latex
\subsection{Augmentation Ablation (L1--L4)}
\label{sec:augmentation-ablation}

The ablation applies an L0-conditional filter: only pairs where 
$\geq$1 of 3 L0 samples passes enter the ablation, avoiding budget on 
untranslatable pairs. For \qwenshort{}, 50 of 142 pairs qualify (35\%); 
for \gptnew{}, 99 (70\%). Each qualifying pair is evaluated once at 
L1--L4. The single-sample design trades precision for budget: apparent 
failures may reflect noise rather than augmentation-induced difficulty.
```

---

### CUT-8: Trim the cross-API argument handling paragraph — saves ~0.15 pages

**File:** `sections/framework.tex`, lines 115

**What it is:** A long paragraph about how the pipeline handles argument/verification asymmetry between source and target APIs (full-program vs. kernel-only translations, union of stdout patterns, etc.).

**What to keep:** The key insight that source and target may need different args/patterns, and how ParBench handles it.

**Condense to:**

```latex
\textbf{Cross-API argument and verification handling.} Source and target 
implementations may expect different arguments and produce different 
stdout formats. For full-program translations (e.g., CUDA to OpenMP), 
the pipeline uses the source spec's run arguments—since the translated 
binary retains the source's argument-parsing logic—and constructs a 
union of source and target stdout patterns for verification. For 
kernel-only translations (e.g., targeting OpenCL \texttt{.cl} files 
where the host binary is unchanged), the target spec's arguments and 
patterns are used directly.
```

---

## Part 3: ESTIMATED SAVINGS SUMMARY

| Cut | Section | Savings | Difficulty |
|-----|---------|---------|------------|
| CUT-1 | JSON listing removal | ~0.50 pp | Easy — already in appendix |
| CUT-2 | Schema field groups | ~0.60 pp | Medium — write summary |
| CUT-3 | Response extraction | ~0.30 pp | Easy — move to appendix |
| CUT-4 | Harness detail | ~0.40 pp | Medium — preserve Gaussian example |
| CUT-5 | HeCBench funnel | ~0.25 pp | Easy — already in appendix |
| CUT-6 | API feature catalog | ~0.20 pp | Easy — move to appendix |
| CUT-7 | Ablation design | ~0.15 pp | Easy — condense |
| CUT-8 | Cross-API handling | ~0.15 pp | Easy — condense |
| BUG-2 | Triple duplication | ~0.10 pp | Trivial — delete duplicates |
| **Total** | | **~2.65 pp** | |

This should bring the paper from ~11.5 to ~8.85 pages — safely within the 9-page limit with a small margin.

---

## Part 4: NeurIPS CHECKLIST ISSUES

The checklist is in `appendices_neurips.tex`, lines 1394–1476. It has all 16 items answered. Three need attention:

### CHECKLIST-1: Item 5 (Code and Data) — Fix wording

**Current justification (line 1419):** "ParBench will be released as an open-source repository containing all 206 kernel specifications..."

**Problem:** "Will be released" is future tense. For NeurIPS submission, the code/data should be included as anonymized supplementary material or an anonymized URL. Reviewers need access *now*, not after acceptance.

**Fix:** Change to: "ParBench is included as anonymized supplementary material containing all 206 kernel specifications, the build/run/verify harness, the evaluation pipeline, augmentation engine, and per-record result JSONs for both models."

**Action needed:** Also actually create the anonymized supplementary zip/repo before submission.

---

### CHECKLIST-2: Item 10 (Broader Impacts) — Strengthen justification

**Current justification (line 1444):** "Section~\ref{sec:discussion} discusses implications for HPC code migration and identifies the limitation that LLM-generated parallel code should not be trusted without verification."

**Problem:** This is thin. NeurIPS reviewers expect at least acknowledgment of potential negative impacts. For a code translation benchmark:

**Fix — add to the justification:**
```
ParBench evaluates translation correctness but not performance; 
practitioners who deploy LLM-translated parallel code based on 
correctness-only benchmarks may deploy code with severe performance 
regressions (e.g., 100× slowdown) that waste energy and compute 
resources. Additionally, improved LLM translation capability could 
accelerate vendor lock-in migration, potentially disrupting the 
competitive balance in GPU hardware markets. The benchmark itself 
poses no direct misuse risk: it evaluates publicly available code 
using commercial APIs.
```

---

### CHECKLIST-3: Item 12 (Licenses) — Add license names

**Current justification (line 1453):** Cites the five suites and mentions commit hashes, but does not explicitly name the licenses.

**Fix — add license names:**
```
Rodinia is distributed under the Rodinia license (BSD-like); 
XSBench and RSBench under MIT; HeCBench under MIT; mixbench under 
GPL-3.0. All are compatible with academic use and redistribution. 
Repository URLs and commit hashes are recorded in each kernel spec.
```

**Action needed:** Verify these license claims against the actual LICENSE files in each repo before submission. The licenses above are from my knowledge — they must be double-checked.

---

## Part 5: CONTENT & FRAMING ISSUES

### FRAMING-1: The abstract claims 96 specs but the paper evaluates 87

**What's happening:** The abstract says "96 specifications over 35 kernels" but later the paper says 9 are KNOWN_FAIL and excluded, leaving 87 for evaluation. The abstract number (96) is the total defined specs, not the evaluation corpus.

**Is this wrong?** Not strictly — the abstract says "contains 96 specifications" not "evaluates 96." But a reviewer who reads "96 specs" and then sees all results computed over 87 or 142 pairs will wonder where 9 specs went.

**Recommended fix:** Add a parenthetical: "96 specifications (87 verified-pass, 9 excluded for platform issues) over 35 kernels"

---

### FRAMING-2: "142 unique source-target pairs" needs clearer setup in abstract

**What's happening:** The abstract jumps from "96 specifications" to "142 unique source-target pairs" without explaining why 96 specs → 142 pairs. The connection (6+4 translation directions × varying kernel coverage per direction, minus KNOWN_FAIL exclusions) is explained in Section 4 but not in the abstract.

**Recommended fix:** Already partially addressed by the phrase "yielding six standard translation directions plus four OpenMP Offload case-study directions" — just make sure the 142 number follows logically. Consider: "yielding 142 unique source-target translation tasks across ten directions."

---

### FRAMING-3: Discussion section is too short relative to its scope

**What's happening:** Section 7 is titled "Discussion, Limitations, and Conclusion" but is only ~25 lines of non-comment text. It tries to cover cross-model comparison, limitations, future work, and conclusion in one compressed section. The limitations paragraph is long but the conclusion is only 3 sentences.

**Is this a problem for NeurIPS?** NeurIPS checklist Item 2 asks for a "separate Limitations section." Currently limitations are embedded in the Discussion section, not a standalone section. This is technically acceptable (the checklist says "encouraged to create a separate section" — not required), but a clearly labeled `\subsection{Limitations}` would strengthen the checklist answer.

**Recommended fix:** Split into:
```latex
\subsection{Discussion}    % Cross-model comparison, what the results mean
\subsection{Limitations}   % The current Limitations paragraph
\subsection{Future Work}   % The current Future Work paragraph  
\subsection{Conclusion}    % The current final paragraph
```
This doesn't add words — it just adds structure. Use `\paragraph{}` if `\subsection{}` takes too much vertical space.

---

### FRAMING-4: Main-body augmentation table shows only Qwen — must include GPT-5.4

**What's happening:** Table 5 (`tab:aug-balanced` in `sections/results.tex`, lines 194–211) presents augmentation robustness results for **Qwen only** on a 12-kernel CUDA-to-OpenMP subset. GPT-5.4 augmentation data exists (L1–L4 pass rates of 87–91% from `quantitative_findings_gpt54.json`) but appears only in the appendix (Table D2, `tab:augmentation-rates`).

**Why it matters:** Both models are first-class subjects of the evaluation. Showing augmentation robustness for only one model in the main body is asymmetric and weakens the claim. A reviewer will ask: "Does GPT-5.4 show the same stability?" The answer is yes (87–91%), which actually *strengthens* the paper's argument — so there's no reason to hide it.

**Data (from `quantitative_findings_gpt54.json > canonical > augmentation_trends > aggregate > per_level`):**
- GPT-5.4 L0: 62.7% (n=426, all pairs)
- GPT-5.4 L1: 88.9% (n=99, L0-conditional subset)
- GPT-5.4 L2: 90.9% (n=99)
- GPT-5.4 L3: 86.9% (n=99)
- GPT-5.4 L4: 90.9% (n=99)

**Fix — two options:**

**(A) Add GPT-5.4 column to existing Table 5 (recommended):** Extend the table to show both models side-by-side on the balanced CUDA-to-OMP subset. GPT-5.4 has 22 qualifying CUDA-to-OMP kernels (vs Qwen's 12), so the table needs a note explaining the different subset sizes. Add a sentence: "GPT-5.4 shows comparable stability on its larger qualifying subset (22 kernels): L1–L4 rates range from 82–96\% (Table~\ref{tab:augmentation-rates})."

**(B) Add a sentence referencing the appendix table:** After the Qwen augmentation paragraph, add: "\gptnew{} exhibits similar augmentation robustness: pass rates on the L0-conditional subset range from 86.9\% to 90.9\% across L1--L4, with no monotonic degradation (Appendix Table~\ref{tab:augmentation-rates})."

Option B is simpler and doesn't change page count. Option A is more rigorous but adds table width.

---

### FRAMING-5: The paper never explicitly states the 9-page structure

**What's happening:** NeurIPS convention is that the paper should be self-contained in the main body (reviewers are not required to read the appendix). Several claims in the main body require the reader to consult the appendix for evidence — which is fine, as long as the main body's narrative stands on its own.

**Check:** Read the main body without the appendix. Can a reviewer follow the narrative, understand the contributions, and evaluate the claims? If yes — fine. If not — bring the missing evidence back.

**Current assessment:** The main body is self-contained for all primary claims. The appendix contains supporting detail (survey figures, full per-kernel table, case studies) but nothing essential to understanding the paper. This is correct structure.

---

## Part 6: DATA CROSS-VERIFICATION RESULTS

I verified every quantitative claim in the paper against the raw data files. Here are the results:

| Claim (paper location) | Paper value | Data file value | Status |
|------------------------|-------------|-----------------|--------|
| Qwen pass@1 (abstract) | 23.9% | 23.94% | ✅ MATCH |
| Qwen pass@3 (abstract) | 35.2% | 35.21% | ✅ MATCH |
| GPT-5.4 pass@1 (abstract) | 62.7% | 62.68% | ✅ MATCH |
| GPT-5.4 pass@3 (abstract) | 69.7% | 69.72% | ✅ MATCH |
| Qwen overall pass rate (Table 1) | 36.7% | 36.74% | ✅ MATCH |
| GPT-5.4 overall pass rate (Table 1) | 75.5% | 75.55% | ✅ MATCH |
| Qwen BUILD_FAIL count (Table 1) | 245 | 245 | ✅ MATCH |
| GPT-5.4 BUILD_FAIL count (Table 1) | 123 | 123 | ✅ MATCH |
| Qwen total valid records | 626 | 626 | ✅ MATCH |
| GPT-5.4 total valid records | 822 | 822 | ✅ MATCH |
| Qwen CUDA→OMP L0 (Table 3) | 40.3% | 40.28% | ✅ MATCH |
| GPT-5.4 CUDA→OMP L0 (Table 3) | 83.3% | 83.33% | ✅ MATCH |
| Qwen OCL→CUDA L0 (Table 3) | 0.0% | 0.0% | ✅ MATCH |
| GPT-5.4 OCL→CUDA L0 (Table 3) | 19.3% | 19.30% | ✅ MATCH |
| Qwen hard fail tasks | 92/142 (64.8%) | 92/142 | ✅ MATCH |
| GPT-5.4 hard fail tasks | 43/142 (30.3%) | 43/142 | ✅ MATCH |
| Total specs on disk | 206 | 206 | ✅ MATCH |
| Rodinia specs | 60 | 60 | ✅ MATCH |
| HeCBench specs | 135 (25 curated) | 135 | ✅ MATCH |
| SLoC min/max/median | 80/3304/271 | 80/3304/271 | ✅ MATCH |
| Kernels above ParEval-Repo threshold | 31/35 (89%) | 31/35 (88.57%) | ⚠️ MINOR — paper rounds up to 89%, data is 88.6%. Consider using "89%" consistently or changing paper to "88.6%" for precision. Not a blocking issue. |
| Abstract BUILD_FAIL "39.1%" | 39.1% of 626 | 245/626=39.14% | ⚠️ SEE BUG-3 |
| Qwen aug L1 (Table D) | 74.0% | 74.0% (n=50) | ✅ MATCH |
| GPT-5.4 aug L1 (Table D) | 88.9% | 88.89% (n=99) | ✅ MATCH |

**All quantitative claims match the data files.** The only concern is BUG-3 (scope mixing in the abstract's BUILD_FAIL percentage).

---

## Part 7: IMPLEMENTATION ORDER

Recommended order of operations for Erel:

1. **BUG-1** (broken cite) — 30 seconds, prevents compilation warning
2. **BUG-2** (triple duplication) — 30 seconds, embarrassing if left
3. **CUT-1** through **CUT-8** — implement all cuts, compile after each to verify no broken refs. Pay special attention to CUT-1 (fix the dangling colon at line 58).
4. **BUG-3** (abstract scope) — decide Option A/B/C with Samyak
5. **FRAMING-3** (split Discussion into subsections) — structural, quick
6. **FRAMING-4** (add GPT-5.4 augmentation to main body) — either extend Table 5 or add a sentence
7. **FRAMING-1** (96 vs 87 in abstract) — word-level fix
8. **CHECKLIST-1, 2, 3** — update checklist justifications
9. **BUG-4** — Remove `\tbd` macro from `sections/macros.tex` line 23 (renders bold red "TBD" text — dangerous to leave in a submission even if unused)
10. **BUG-5** — Export `figures/parbench_architecture.drawio` to PDF. Currently only `.png` exists; NeurIPS strongly prefers vector graphics for figures. Use draw.io → Export → PDF.
11. **Final compile** — verify total page count ≤ 9 for main body
12. **Grep check** — run `grep -rn 'TODO\|FIXME\|TBD\|ADD_CITE' sections/ appendices_neurips.tex` to confirm no remaining placeholders

---

## Part 8: THINGS THAT ARE FINE (no action needed)

- **Title** — clear, specific, includes key terms (LLM, parallel code translation, build-run-verify)
- **Author block** — correctly anonymized ("Anonymous Author(s)")
- **Bibliography** — 18 citations used, 25 defined in bib. Unused entries (`AlphaTrans2025`, `HPCorpus2023`, `OMPGPT2024`, `RepoTransBench2025`, `Tramm:rs`) won't appear in the PDF. Optional cleanup: remove them from `references.bib` to reduce source clutter, but not required.
- **Figure 2 (failure taxonomy)** — correct, PDF vector version exists
- **Related work** — well-structured by methodology, correctly positions against LASSI, ParEval-Repo, CodeRosetta
- **Statistical methodology** — Wilson CIs, McNemar tests, Cochran-Armitage, Cohen's h — all appropriate
- **NeurIPS style file** — `neurips_2026.sty` with `\answerYes/No/NA` macros defined
- **Appendix structure** — well-organized (A: Framework, B: API Selection, C: Survey, D: Extended Related Work, E: Detailed Results, F: Prompt Template, G: GPT figures, H: Cost)
- **All quantitative claims** — verified against raw data (see Part 6)
- **Cross-references** — all `\ref{}` labels used in the main body resolve to defined `\label{}` entries in either the main body or appendix. No dangling references (verified via grep).
- **Figure files** — all `\includegraphics` targets exist on disk (except Figure 1 needs PDF export — see BUG-5 above)
