# SC26 Review Panel — Session Handoff

## Status
Phase 1-2 COMPLETE. Phase 3 (spawn reviewers) READY to execute.

## Paper Location
`docs/paper/latex/paper.tex` — 1112 lines, Sections S1-S8 + Appendices.

## Data Verification Table (Phase 2 — ALL VERIFIED)

| Claim in paper | Source file(s) | Verified value | Match? |
|---|---|---|---|
| "710 primary campaign tasks" | paper_data.json > file_counts | 710 | YES |
| "38.3% overall pass rate" | paper_data.json > overall | 272/710=0.3831 | YES |
| "[34.8%, 41.9%] CI" | paper_data.json > overall | [0.3481, 0.4194] | YES |
| "BUILD_FAIL 33.9%" | paper_data.json > by_status | 241/710=33.9% | YES |
| "VERIFY_FAIL 7.2%" | paper_data.json > by_status | 51/710=7.2% | YES |
| "RUN_FAIL 20.3%" | paper_data.json > by_status | 144/710=20.3% | YES |
| "cuda-to-omp 64.2%" | paper_data.json > by_direction | 77/120=0.6417 | YES |
| "cuda-to-omp L0 66.7%" | statistical_analysis.json > augmentation_trends | 16/24=0.6667 | YES |
| "opencl-to-cuda 6.0%" | paper_data.json > by_direction | 6/100=0.06 | YES |
| "first_attempt 22.5%" | paper_data.json > self_repair | 160/710=0.2254 | YES |
| "repaired 112/550 (20.4%)" | paper_data.json > self_repair | 112/550=0.2036 | YES |
| "7 regressions (1.0%)" | paper_data.json > self_repair | 7 regressions | YES |
| "Cochran-Armitage z=0.0, p=1.0" | statistical_analysis.json > augmentation_trends | z=-0.0, p=1.0 | YES |
| "pass counts [16,14,17,14,16]" | statistical_analysis.json > augmentation_trends | [16,14,17,14,16] | YES |
| "426 pass@k tasks" | paper_data.json > file_counts | 426 | YES |
| "96 specs (60+25+4+4+3)" | ls specs/{suite}-*.json | 60+135(25 curated)+4+4+3 | YES (internally consistent) |
| "1,248 result JSONs" | ls results/evaluation/.../*.json | 1248 | YES |
| "BUILD_FAIL 241/438=55.0% of failures" | paper_data.json | 241/438=55.0% | YES |
| "VERIFY_FAIL 51/438=11.6% of failures" | paper_data.json | 51/438=11.6% | YES |

## Key Data Files
- `results/analysis/paper_data.json` — primary source of truth
- `results/analysis/statistical_analysis.json` — Cochran-Armitage, McNemar, direction asymmetry
- `results/analysis/quantitative_findings.json` — augmentation trends, per-direction breakdowns
- `results/analysis/error_taxonomy.json` — BUILD_FAIL/VERIFY_FAIL subcategories
- `results/analysis/sloc_analysis.json` — SLoC per kernel
- `results/analysis/benchmark_characterization.json` — kernel categories

## Team Design (APPROVED)

| Teammate | Role | Focus Sections |
|----------|------|----------------|
| r1-hpc | HPC Domain Expert — GPU arch, performance claims, parallelism semantics | S3-S4 |
| r2-ml | ML/AI Researcher — LLM eval methodology, model fairness, prompts | S5-S6 |
| r3-stats | Benchmarking Methodologist — Statistical rigor, baselines | S6 (stats) |
| r4-repro | Reproducibility Reviewer — Environment, versioning, open-source | S5, specs, scripts |
| r5-adversary | Devil's Advocate — Strongest objections, novelty, alternatives | Full paper + other reviews |

Cross-talk: All teammates share team namespace. R5 reviews last and incorporates others' findings.

## LaTeX Issues Noticed
1. Duplicate `\newcommand{\parbench}` at lines 28 and 53 (will cause LaTeX error)
2. Duplicate `\newcommand{\pending}` at lines 36 and 37 (will cause LaTeX error)
3. Many `\pending{}` and `\tbd` placeholders for GPT-4.1 mini data throughout

## Instructions for New Session
1. Read this handoff file
2. Read `teammate-prompt.md` at `.claude/skills/agent-team/teammate-prompt.md`
3. `TeamCreate(team_name="sc26-review-panel")`
4. Create 5 tasks (one per reviewer)
5. Spawn all 5 reviewers with filled teammate-prompt.md prompts
6. Each reviewer gets: full paper text (their section focus), data verification table, their checklist
7. After independent reviews complete, facilitate cross-talk
8. R5 goes last, incorporating others' findings
9. Synthesize final panel report (Phase 4)
