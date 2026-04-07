# Phase 15: Paper Review Tools for SC26 - Research

**Researched:** 2026-04-06
**Domain:** Claude Code plugins / skills for academic paper review, editing, and quality improvement
**Confidence:** MEDIUM — all external tools verified via WebFetch; project-internal tool (paper-review-sim) verified directly from disk

---

## Summary

This project already contains a purpose-built SC26 review skill (`paper-review-sim`) in `.claude/skills/paper-review-sim/SKILL.md`. It simulates a 5-reviewer SC26 panel (HPC domain, ML/AI, benchmarking, reproducibility, devil's advocate), verifies every number against result JSONs before spawning reviewers, and outputs a priority-ranked action list. This is the highest-relevance tool and requires zero installation.

Beyond the in-project skill, the Claude Code ecosystem (as of April 2026) has a dense set of community-built academic writing skills. Several are directly applicable to the four stated needs: structured paper review, length reduction, appendix migration, and writing quality improvement. No single external tool covers all four needs simultaneously; the best approach is composing two or three targeted skills.

For the SC26 deadline (April 8, 2026), the time-critical path is: (1) run the existing `/paper-review-sim` for reviewer feedback, (2) use `bahayonghang/academic-writing-skills` `paper-audit` for submission-blocker detection, (3) apply `LimHyungTae/awesome-claudecode-paper-proofreading` for LaTeX-level proofreading. Length reduction and related-work gap checking are best handled by custom prompting against the existing skills rather than a new tool install.

**Primary recommendation:** The project already has the best SC26-specific review tool (paper-review-sim). Add `LimHyungTae/awesome-claudecode-paper-proofreading` for LaTeX proofreading. All other needs can be met by using these two plus direct Claude prompting — no additional installs needed before April 8.

---

## Project Constraints (from CLAUDE.md)

- Python: always `python3`; venv at `env_parbench`
- Paper: `docs/paper/latex/paper.tex`, IEEE double-column, ~10 pages
- Deadline: April 8, 2026 (hard SC26 submission)
- Result immutability: never modify existing result JSONs
- Two tmux sessions (`qwen_hecbench`, `qwen_small`) must not be touched
- Model selection: Opus for all substantive work
- Framing: benchmark paper, not model evaluation paper
- Every data claim must trace to a file on disk

---

## Existing In-Project Asset

### `.claude/skills/paper-review-sim/SKILL.md`

**Location:** `/home/samyak/Desktop/parbench_sam/.claude/skills/paper-review-sim/SKILL.md`
**Trigger:** `/paper-review-sim [path-to-paper]`
**Relevance:** 5/5 — purpose-built for SC26

This skill is the most relevant tool found. It:

- **Phase 1:** Locates and reads the draft, catalogues every quantitative claim
- **Phase 2:** Verifies every number against `results/evaluation/` and `results/augmentation/` before any review begins. Mismatches become P0 action items.
- **Phase 3:** Spawns 5 parallel subagent reviewers:
  - **R1 (HPC Domain Expert):** GPU architecture correctness, CUDA/OMP/OpenCL semantics, hardware documentation
  - **R2 (ML/AI Researcher):** Model comparison fairness, prompt engineering, thinking-confound handling
  - **R3 (Benchmarking Methodologist):** Statistical rigor, sample size, failure taxonomy consistency
  - **R4 (Reproducibility Reviewer):** Fresh-clone recoverability, dependency documentation, result versioning
  - **R5 (Devil's Advocate):** Novelty vs. SWE-bench/HumanEval/LASSI/CodeRosetta, strongest objections
- **Phase 4:** Aggregates into a panel report with STRONG ACCEPT → STRONG REJECT verdict, SC26 criteria scores (1-5), and priority-ranked P0/P1/P2 action items
- **Phase 5:** (optional) Author response coaching per reviewer

**Iron Law in the skill:** "NO REVIEWER MAY ACCEPT A CLAIM WITHOUT TRACING IT TO DATA." This directly enforces the CLAUDE.md requirement that every data claim must trace to a file.

**Install:** Already installed — no action needed.

[VERIFIED: disk read of `/home/samyak/Desktop/parbench_sam/.claude/skills/paper-review-sim/SKILL.md`]

---

## External Tools — Ranked by Relevance

### Tier 1: High Relevance — Recommended for Install

#### 1. LimHyungTae/awesome-claudecode-paper-proofreading
**URL:** https://github.com/LimHyungTae/awesome-claudecode-paper-proofreading
**Relevance:** 4/5
**Covers:** LaTeX workspace audit + paper content proofreading
**Install:**
```bash
git clone https://github.com/LimHyungTae/awesome-claudecode-paper-proofreading.git \
  ~/.claude/tools/paper-proofreading
```
Then reference prompt files with absolute path in Claude Code.

**What it does (verified via WebFetch):**
- Two-phase workflow: detect-first (numbered issues), then user approves which to fix
- Mode 1 — LaTeX Workspace Audit: preamble config, package load order, macro safety, cross-reference integrity, citation integrity, figure/table safety, hidden errors (TODOs, formatting hacks)
- Mode 2 — Paper Content Proofreading: grammar, tense consistency, scientific clarity, structure, figure captions, notation consistency, abstract quality, hyphenation
- Built on 100+ real conference paper reviews; designed for non-native English writers
- Works in CI/headless environments

**SC26 fit:** Addresses two classes of risk: LaTeX compilation errors that waste submission slots, and language/consistency issues that lose points with reviewers. The detect-first model is safe for a 2-day deadline because the user controls which fixes get applied.

[VERIFIED: WebFetch of github.com/LimHyungTae/awesome-claudecode-paper-proofreading]

---

#### 2. bahayonghang/academic-writing-skills — `paper-audit` mode
**URL:** https://github.com/bahayonghang/academic-writing-skills
**Relevance:** 4/5
**Covers:** Submission-blocker detection, deep reviewer-style critique, grammar/weak-verb replacement
**Install:**
```bash
git clone https://github.com/bahayonghang/academic-writing-skills.git \
  ~/.claude/tools/academic-writing-skills
```
Copy skills to `.claude/commands/` or reference with absolute path.

**What it does (verified via WebFetch):**
- `latex-paper-en` skill: targets IEEE/ACM/Springer/conference venues; grammar analysis, weak-verb replacement, subject-verb agreement, decomposition of sentences >50 words
- `paper-audit` skill (3 modes): `quick-audit` (fast screening), `deep-review` (full reviewer-style critique), `gate` (submission blockers only)
- Focus on "post-writing formatting, validation, and deep polishing" — explicitly NOT from-scratch generation

**SC26 fit:** The `gate` mode is specifically useful 2 days before a deadline — it surfaces only must-fix items without generating noise. The `deep-review` mode is equivalent to what `/paper-review-sim` does at the SC level but with a different angle (writing quality vs. technical rigor).

[VERIFIED: WebFetch of github.com/bahayonghang/academic-writing-skills]

---

### Tier 2: Medium Relevance — Useful if Time Permits

#### 3. andrehuang/academic-writing-agents
**URL:** https://github.com/andrehuang/academic-writing-agents
**Relevance:** 3/5
**Covers:** 12-agent parallel review covering all writing dimensions, review persistence, incremental re-review

**12 agents (verified via WebFetch):**
- Review agents: `consistency-checker`, `logic-reviewer`, `technical-reviewer`, `writing-reviewer`, `latex-layout-auditor`
- Audit agents: `bibliography-auditor`
- Research agents: `research-analyst` (related work landscape + novelty positioning), `brainstormer`
- Survey agents: `paper-crawler` (DBLP + OpenAlex)
- Action agents: `prose-polisher`, `section-drafter`, `latex-figure-specialist`

**SC26 fit:** The `research-analyst` agent is specifically useful for the related-work gap (LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus flagged in paper-review-sim skill). The `bibliography-auditor` catches citation format issues. **However**, auto-triggers on `.tex` files and may fire unsolicited during normal paper editing — needs configuration.

**Notable:** Saves findings to `.review/` directory; incremental review checks unchanged content. 30 codified principles built in.

[VERIFIED: WebFetch of github.com/andrehuang/academic-writing-agents]

---

#### 4. Imbad0202/academic-research-skills — `academic-paper-reviewer` mode
**URL:** https://github.com/Imbad0202/academic-research-skills
**Relevance:** 3/5
**Covers:** Multi-perspective peer review with 0-100 rubrics, revision coaching, citation format conversion

**Academic Paper Reviewer modes (verified via WebFetch):**
- Comprehensive review: Editor + 3 reviewers + Devil's Advocate
- Quick assessment
- Guided improvement suggestions
- Methodology-focused evaluation
- Re-review verification after revisions

**Academic Paper writing modes (relevant to shortening):**
- Revision mode: structured response to feedback
- Revision-coach mode: creates a roadmap for revisions
- Writing polish: style refinement
- Format conversion: LaTeX ↔ citation style conversion (APA/Chicago/MLA/IEEE/Vancouver)

**SC26 fit:** The revision-coach mode is useful for creating a structured plan to address `/paper-review-sim` P0 items. The citation format conversion handles the IEEE bibliography formatting. However, the full pipeline (10-stage orchestrator) consumes >200K input tokens — too heavy for a 2-day deadline unless used selectively.

[VERIFIED: WebFetch of github.com/Imbad0202/academic-research-skills]

---

#### 5. JeanDiable/academic-research-plugin — `paper-reviewing` + `paper-polishing`
**URL:** https://github.com/JeanDiable/academic-research-plugin
**Relevance:** 3/5
**Covers:** Conference-style peer review (NeurIPS/ICML/CVPR/ACL/AAAI/ICCV/ICLR formats), citation insertion, related-work gap detection

**Relevant skills (verified via WebFetch):**
- `/academic-research:paper-reviewing` — conference-style review; note: SC26/IEEE format not in the supported list (ICML meta-review style is closest)
- `/academic-research:paper-polishing` — ICML meta-review style; analyzes correctness, motivation, methodology, presentation
- `/academic-research:citation-assistant` — automatic citation insertion for LaTeX; finds uncited claims, searches for correct papers

**SC26 fit:** The `citation-assistant` is useful for finding missing references (LASSI, CodeRosetta, etc.) given uncited claims. The venue format mismatch (no SC/IEEE HPC format) is a limitation — the review lens will be ML-conference-centric rather than systems/HPC-centric.

**Install (verified):**
```bash
claude plugin marketplace add JeanDiable/academic-research-plugin
claude plugin install academic-research
# Plus: pip install -r academic-research-plugin/lib/requirements.txt
```

[VERIFIED: WebFetch of github.com/JeanDiable/academic-research-plugin]

---

#### 6. pedrohcgs/claude-code-my-workflow (clo-author)
**URL:** https://github.com/pedrohcgs/claude-code-my-workflow
**Relevance:** 2/5 (designed for economics/LaTeX/R, not HPC systems)
**Covers:** LaTeX multi-pass compilation, bibliography validation, adversarial QA loop, manuscript review

**Relevant features (verified via WebFetch):**
- `/review-paper`: structure, econometrics, referee objections
- `/proofread`: grammar, typos, overflow, consistency
- `/compile-latex`: 3-pass XeLaTeX compilation with bibtex
- `/validate-bib`: cross-references citations against bibliography files
- `/devils-advocate`: challenges design decisions
- Automated 0-100 scoring with 80/90 thresholds

**SC26 fit:** The `/compile-latex` and `/validate-bib` commands are genuinely useful for any LaTeX paper. However the `/review-paper` is calibrated for economics venues (AER, QJE, JPE, Econometrica), not CS systems conferences — the review will miss HPC-specific issues.

[VERIFIED: WebFetch of github.com/pedrohcgs/claude-code-my-workflow]

---

### Tier 3: Low Relevance — Reference Only

#### 7. hpcgroup/paper-check
**URL:** https://github.com/hpcgroup/paper-check
**Relevance:** 2/5 (general paper quality, not Claude Code integration)

**What it does (verified via WebFetch):**
- Standalone Python tool (not a Claude Code skill); requires `XAI_API_KEY`
- Checks: title/section formatting, figure labeling, number formatting, informal language, italics usage
- LLM-based evaluation of introduction completeness and overall writing quality
- Accepts both PDF and LaTeX source as input; generates markdown report

**Install:**
```bash
pip install -r requirements.txt
export XAI_API_KEY=xxx
python paper_check.py --pdf path/to/paper.pdf --latex path/to/source
```

**SC26 fit:** Useful for a quick automated scan, but requires xAI API key (not Anthropic), and the checks are more formatting-focused than content-focused. Does not integrate into the Claude Code session flow.

[VERIFIED: WebFetch of github.com/hpcgroup/paper-check]

---

#### 8. Galaxy-Dawn/claude-scholar — `writing-anti-ai` skill
**URL:** https://github.com/Galaxy-Dawn/claude-scholar
**Relevance:** 2/5

**Relevant feature (verified via WebFetch):**
- `writing-anti-ai`: reduces robotic phrasing, improves clarity, rhythm, and human academic tone
- `citation-verification`: checks references, metadata, and claim-citation alignment
- `latex-conference-template-organizer`: cleans messy conference templates

**SC26 fit:** The `writing-anti-ai` skill is useful if reviewers are likely to flag AI-generated prose patterns. For an HPC systems paper this is lower priority than technical rigor, but worth running on the abstract and introduction.

[VERIFIED: WebFetch of github.com/Galaxy-Dawn/claude-scholar]

---

#### 9. claesbackman/AI-research-feedback
**URL:** https://github.com/claesbackman/AI-research-feedback
**Relevance:** 2/5 (calibrated for economics journals, not CS conferences)

**Skills (verified via WebFetch):**
- `review-paper`: 6-agent review (spelling, consistency, unsupported claims, math, figures, contribution value) — calibrated for AER/QJE/JPE/Econometrica
- `review-paper-light`: fast 2-agent pre-submission check
- `review-paper-code`: paper-code alignment, reproducibility, empirical claim verification
- `review-grant`: NSF/NIH/ERC proposal review

**SC26 fit:** `review-paper-code` is uniquely relevant — it checks whether empirical claims in the paper match the underlying code/analysis. For ParBench, this maps directly to the requirement that every data claim traces to a result JSON. However the journal calibration (economics) means the content review will not understand HPC semantics.

[VERIFIED: WebFetch of github.com/claesbackman/AI-research-feedback]

---

## Addressing the Four Specific Needs

### Need 1: Paper Review (structure, clarity, arguments, reviewer perspective)

**Best tool:** Existing `/paper-review-sim` skill (already installed)
- SC26-specific reviewer personas (HPC expert, ML researcher, benchmarking methodologist, reproducibility reviewer, devil's advocate)
- Verifies data before spawning reviewers — no false positives from unverified numbers
- Outputs SC26-format verdict and ranked action items

**Backup:** `bahayonghang/academic-writing-skills` `deep-review` mode for a second opinion on writing quality

### Need 2: Paper Shortening (cut length without losing HPC benchmark narrative)

**No dedicated tool found.** [ASSUMED] No Claude Code skill specifically addresses IEEE page-limit enforcement or HPC-narrative-preserving cuts.

**Best approach (no install needed):** Direct Claude prompting after `/paper-review-sim` identifies P2 (nice-to-have) items:
1. Run `/paper-review-sim` — P2 items are the first candidates for removal
2. Prompt: "The paper is over the 10-page IEEE limit. Identify the 3-5 paragraphs with lowest information density that can be cut or moved to appendix, while preserving: (a) every quantitative result, (b) the methodology description, (c) the related work positioning."
3. For each candidate cut, ask Claude to verify the paragraph contains no unique data before removing

**Pattern from ecosystem:** `ndpvt-web/latex-document-skill` has `cheat sheet compression` and `Telegram-style compression` templates [CITED: github.com/ndpvt-web/latex-document-skill] but these are for creating new condensed documents, not editing existing papers.

### Need 3: Moving Content to Appendix Intelligently

**No dedicated tool found.** [ASSUMED]

**Best approach:** After shortening analysis above:
1. IEEE conference papers (IEEEtran class) support appendix via `\appendix` + `\section{}`
2. Candidate content for appendix: detailed proof sketches, full spec tables, extended related work, augmentation level tables beyond what fits in the main body
3. The `paper-review-sim` R3 (Benchmarking Methodologist) reviewer will flag which tables/figures are essential vs. supplementary

**Relevant skill:** `lishix520/academic-paper-skills` Strategist Phase 3 (Outline Optimization with reviewer-assessed quality scoring) can be used to re-plan section structure after appendix migration [CITED: github.com/lishix520/academic-paper-skills].

### Need 4: Writing Quality Improvement for Peer Review

**Best tools (ranked):**
1. `LimHyungTae/awesome-claudecode-paper-proofreading` — LaTeX workspace + content proofreading, detect-first safety model
2. `bahayonghang/academic-writing-skills` `latex-paper-en` — weak-verb replacement, sentence simplification for IEEE/ACM
3. `Galaxy-Dawn/claude-scholar` `writing-anti-ai` — removes AI-pattern prose

---

## Installation Priority Given April 8 Deadline

Given 2 days to deadline:

| Priority | Action | Time Cost | Risk |
|----------|--------|-----------|------|
| 0 | Run `/paper-review-sim docs/paper/latex/paper.tex` | ~10-15 min | None — already installed |
| 1 | `git clone` LimHyungTae/awesome-claudecode-paper-proofreading, run LaTeX audit | ~30 min total | LOW |
| 2 | Manual shortening pass using `/paper-review-sim` P2 items as guide | ~1-2 hours | MEDIUM — judgment required |
| 3 | Run `bahayonghang/academic-writing-skills` gate mode | ~20 min | LOW |
| 4 | Install JeanDiable/academic-research-plugin for citation gap filling | ~45 min | MEDIUM — pip dependency |

---

## Related Work Gap: Known Missing References

The `paper-review-sim` skill explicitly flags these as red flags if absent from the paper's related work section [VERIFIED: disk read of SKILL.md]:

| Paper | Why It Matters |
|-------|---------------|
| LASSI | LLM-based code translation for scientific apps |
| CodeRosetta | CUDA↔C++ bidirectional translation |
| HPC-Coder-v2 | LLM fine-tuning for HPC code |
| OMPify | OpenMP pragma prediction |
| HPCorpus | HPC code corpus |
| TransCoder | Code-to-code translation baseline |

The `JeanDiable/academic-research-plugin` `citation-assistant` can automatically find and insert BibTeX entries for uncited claims matching these papers. The `andrehuang/academic-writing-agents` `research-analyst` + `paper-crawler` can also fetch from DBLP/OpenAlex.

---

## Architecture Patterns for Using These Tools

### Recommended Workflow (2-day deadline)

```
Step 1: Data verification
  /paper-review-sim docs/paper/latex/paper.tex
  → captures all P0 data mismatches before any editing

Step 2: LaTeX audit (parallel with step 1 analysis)
  Reference ~/.claude/tools/paper-proofreading/prompts/01_latex_workspace_review.md
  → fix compilation risks, broken cross-refs, bad macro patterns

Step 3: Content proofreading
  Reference ~/.claude/tools/paper-proofreading/prompts/02_paper_proofreading.md
  → detect grammar/consistency issues, select subset to fix

Step 4: Length analysis
  Prompt Claude directly using P2 items from /paper-review-sim as cut candidates
  → identify appendix candidates

Step 5: Related work gap
  Use /academic-research:citation-assistant on uncited LASSI/CodeRosetta/HPC-Coder-v2 claims
  → or direct web search + manual BibTeX addition (faster for 3-4 papers)
```

### Anti-Pattern to Avoid

Do NOT install and run the full `Imbad0202/academic-research-skills` 10-stage pipeline — it consumes >200K input + 100K output tokens and is designed for writing papers from scratch, not polishing an existing draft 2 days before deadline.

---

## Common Pitfalls

### Pitfall 1: Tool Calibration Mismatch
**What goes wrong:** Running a tool calibrated for ML conferences (NeurIPS, ICML) on an SC26 systems/HPC paper. Reviewers will focus on ML methodology critique and miss HPC-specific issues.
**Prevention:** Use `/paper-review-sim` (SC26-calibrated) as primary review. Use external tools only for writing quality, not technical content review.

### Pitfall 2: Over-Installation Before Deadline
**What goes wrong:** Spending the deadline window installing, configuring, and learning 3-4 new tools instead of actually improving the paper.
**Prevention:** The project already has the most critical tool. Install at most one external tool (LimHyungTae proofreading) for LaTeX safety checks.

### Pitfall 3: Trusting Tool Output Without Data Verification
**What goes wrong:** A review tool says "pass rate X%" based on the paper text — which may differ from the actual result JSONs.
**Prevention:** The `paper-review-sim` iron law prevents this at the review stage. For any editing pass, re-verify numbers against `results/evaluation/` before committing.

### Pitfall 4: Auto-Triggered Skills During Editing
**What goes wrong:** `andrehuang/academic-writing-agents` auto-triggers on `.tex` files, consuming context mid-editing session.
**Prevention:** Do not install tools with auto-trigger behavior unless configured to be explicit-invocation-only.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No Claude Code skill specifically targets IEEE page-limit enforcement for conference papers | Need 2 (shortening) | Low — the manual prompting approach is effective regardless |
| A2 | No Claude Code skill specifically handles appendix migration with HPC narrative preservation | Need 3 (appendix) | Low — direct prompting is sufficient |
| A3 | The JeanDiable plugin marketplace install command works on this Linux machine | Tier 2 tools | Medium — plugin marketplace API may not be available; fallback is manual git clone |

---

## Open Questions (RESOLVED)

1. **Does `/paper-review-sim` require the paper to be in Markdown or does it handle `.tex`?**
   - RESOLVED: It reads `.tex` files directly when path is specified as argument. Already tested successfully with `docs/paper/latex/paper.tex` in Phase 15 panel simulation.

2. **Are the related work papers (LASSI, CodeRosetta, etc.) in the existing bibliography?**
   - RESOLVED: Yes. All papers (LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus, TransCoder) are present in `docs/paper/latex/references.bib` and cited in `paper.tex`.

3. **What is the current page count of `paper.tex`?**
   - RESOLVED: Not applicable for Phase 15 scope (specific fixes, not shortening). Page count is a Phase 16-18 concern during GPT data integration.

---

## Sources

### Primary (HIGH confidence)
- Disk read: `/home/samyak/Desktop/parbench_sam/.claude/skills/paper-review-sim/SKILL.md` — full skill spec verified
- WebFetch: github.com/LimHyungTae/awesome-claudecode-paper-proofreading — features, install, usage verified
- WebFetch: github.com/bahayonghang/academic-writing-skills — skill list, modes verified
- WebFetch: github.com/andrehuang/academic-writing-agents — 12 agents, capabilities verified
- WebFetch: github.com/JeanDiable/academic-research-plugin — 8 skills, install commands verified
- WebFetch: github.com/pedrohcgs/claude-code-my-workflow — LaTeX and review commands verified
- WebFetch: github.com/hpcgroup/paper-check — install, usage, scope verified
- WebFetch: github.com/Imbad0202/academic-research-skills — modes and token cost verified
- WebFetch: github.com/claesbackman/AI-research-feedback — skill list verified
- WebFetch: github.com/lishix520/academic-paper-skills — workflow phases verified
- WebFetch: github.com/Galaxy-Dawn/claude-scholar — writing-anti-ai skill verified

### Secondary (MEDIUM confidence)
- WebSearch: "claude code academic paper review plugin github 2025 2026" — discovery of tool landscape
- WebSearch: "awesome claude code skills list academic writing LaTeX paper 2025" — additional tool discovery
- WebSearch: "related work section checker paper HPC systems conference review tool github 2025 2026" — hpcgroup/paper-check discovery

### Tertiary (LOW confidence)
- None — all tool claims were verified via direct WebFetch of repositories

---

## Metadata

**Confidence breakdown:**
- In-project tool (paper-review-sim): HIGH — read directly from disk
- External tool features: MEDIUM-HIGH — verified via WebFetch of each repo's README
- Paper shortening / appendix migration: MEDIUM — no dedicated tool found; based on verified absence across 10+ repos
- Related work gaps: HIGH — directly in paper-review-sim SKILL.md on disk

**Research date:** 2026-04-06
**Valid until:** 2026-05-06 (stable ecosystem, tools unlikely to change in 30 days)
