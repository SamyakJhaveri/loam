# Citation Audit Report

**Date**: 2026-05-06
**Bib file**: references.bib
**Total entries**: 46

## Summary

| Verdict | Count |
|---------|------:|
| KEEP | 46 |
| FIX | 0 |
| REPLACE | 0 |
| REMOVE | 0 |

## Findings

- Existence: all 46 cited entries were found online via DOI, venue page, arXiv, OpenReview, DBLP, or an official project/publication page.
- Metadata: published journal or conference records are used wherever verified; the remaining arXiv-only entries are HumanEval2021, MemorizeOrGeneralize2025, OMPar2024, ParaCodex2026, QiMengMuPa2025, SWEbenchIllusion2025, TRACE2025, VibeCodeHPC2025.
- Context: no citation use in the current draft required REPLACE or REMOVE in this audit pass.
- Residual risk: this run was completed as a local web-assisted audit because the fresh cross-model MCP reviewer specified in the skill was not available in this environment.

## Manual Review Queue

These entries still use arXiv-style citations because I did not verify a published journal or conference record for them in this pass. They should be reviewed manually before final submission in case a venue version has appeared very recently.

- `HumanEval2021`
  Current state: arXiv-only citation in the bibliography.
  Review task: confirm whether you want to keep the canonical arXiv citation or replace it with another preferred archival reference.

- `MemorizeOrGeneralize2025`
  Current state: arXiv preprint `arXiv:2503.02296`.
  Review task: check whether a conference or journal version now exists.

- `OMPar2024`
  Current state: arXiv preprint `arXiv:2409.14771`.
  Review task: check whether a published venue version now exists.

- `ParaCodex2026`
  Current state: arXiv preprint `arXiv:2601.04327`.
  Review task: check whether a published venue version now exists.

- `QiMengMuPa2025`
  Current state: arXiv preprint `arXiv:2506.11153`; I did not verify a NeurIPS proceedings record in this pass.
  Review task: confirm whether a conference publication exists, otherwise keep the arXiv citation.

- `SWEbenchIllusion2025`
  Current state: arXiv preprint `arXiv:2506.12286`.
  Review task: check whether a published venue version now exists.

- `TRACE2025`
  Current state: canonical live preprint is `arXiv:2508.11468`.
  Important note: a later record, `arXiv:2603.16479`, is a withdrawn duplicate that explicitly points back to `arXiv:2508.11468`, so the bibliography should keep `2508.11468` unless a real venue publication appears.
  Review task: check whether a published venue version now exists; do not switch to `2603.16479`.

- `VibeCodeHPC2025`
  Current state: arXiv preprint `arXiv:2510.00031`.
  Review task: check whether a published venue version now exists.

## Next Action

If you verify published venue records for any entry in the manual review queue, update `references.bib` to the published citation and rerun the citation audit so the report and hashes match the final bibliography state.
