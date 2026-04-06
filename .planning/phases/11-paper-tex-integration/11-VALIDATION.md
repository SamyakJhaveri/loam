---
phase: 11
slug: paper-tex-integration
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
audited: 2026-04-06
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + custom audit script |
| **Config file** | pyproject.toml (project root) |
| **Quick run command** | `python3 scripts/analysis/cross_consistency_audit.py --project-root .` |
| **Full suite command** | `python3 -m pytest c_augmentation/test_transforms.py scripts/analysis/ -x && python3 scripts/analysis/cross_consistency_audit.py --project-root .` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 scripts/analysis/cross_consistency_audit.py --project-root .`
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green + audit script reports zero unverified critical numbers
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | D-01/D-03/D-04 | — | N/A | automated | Float migration verify (17 moved, 7 kept, ref pointers) | in-plan | ✅ green |
| 11-01-02 | 01 | 1 | D-02 | — | N/A | automated | Condensed per-kernel table verify (label, caption, appendix ref) | in-plan | ✅ green |
| 11-01-03 | 01 | 1 | D-05/TEX-05 | — | N/A | automated | Inline key facts verify (RTX 4070, Qwen 397B, GCC, sm_89) | in-plan | ✅ green |
| 11-02-01 | 02 | 2 | TEX-02/TEX-03 | — | N/A | automated | S1+S3 number verify (38.3%, 96, prompt_payload, LASSI) | in-plan | ✅ green |
| 11-02-02 | 02 | 2 | TEX-01/TEX-08 | — | N/A | automated | Abstract+S2+S8 verify (38.3%, CIs, related work systems) | in-plan | ✅ green |
| 11-03-01 | 03 | 3 | TEX-04/TEX-05/TEX-06 | — | N/A | automated | SC26 items verify (MDES, case studies, HeCBench hash, spectrum, tiers) | in-plan | ✅ green |
| 11-03-02 | 03 | 3 | TEX-07 | — | N/A | automated + manual | S7 subsection count (3); manual: claim preservation review | in-plan (partial) | ✅ green |
| 11-04-01 | 04 | 4 | TEX-09 | — | N/A | automated | `python3 scripts/analysis/cross_consistency_audit.py --project-root .` | `scripts/analysis/cross_consistency_audit.py` | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `scripts/analysis/cross_consistency_audit.py` — the audit script itself (TEX-09, created in Plan 04 Wave 4)
- [x] `scripts/analysis/test_cross_consistency_audit.py` — 15 unit tests, all passing
- [x] No new test file needed — the audit script IS the validation tool
- [x] Each plan (01-03) embeds inline `<verify><automated>` Python scripts for immediate feedback

*Note: The audit script was created as Plan 04 (Wave 4). Plans 01-03 each contained inline automated verify scripts that ran immediately after task completion, providing feedback before the audit script existed. These inline scripts were the primary validation mechanism for Waves 1-3.*

---

## Manual-Only Verifications

| Behavior | Requirement | Plan-Task | Why Manual | Test Instructions | Status |
|----------|-------------|-----------|------------|-------------------|--------|
| S3 architecture accuracy | TEX-03 | 02-01 | Prose description of framework design cannot be machine-verified | Review S3 text against actual harness/ codebase structure | ⬜ pending user review |
| S7 Discussion merge quality | TEX-07 | 03-02 | Structural rewrite (merging S7.1-S7.5) requires editorial judgment | Verify S7 has exactly 3 subsections focused on implications, not restating S6 | ✅ verified (3 subsections confirmed) |
| S7 claim preservation | TEX-07 | 03-02 | Need to verify all original S7 claims survive the merge | Check each of: kernel-centric advantage, BUILD_FAIL dominance, MoE observation, OpenCL ceiling, LASSI spectrum, bimodal pass@k, direction asymmetry, augmentation invariance | ⬜ pending user review |
| S2/S8 related work positioning | TEX-08 | 02-02 | Positioning against 7+ papers requires domain judgment | Verify LASSI, TransCoder, OMPify, HPC-Coder-V2, CodeRosetta differentiators are concrete and accurate | ⬜ pending user review |
| MDES power analysis interpretation | TEX-04 | 03-01 | Statistical interpretation nuance | Verify MDES=34.1pp is honestly reported as a limitation, not dismissed | ⬜ pending user review |
| VERIFY_FAIL case study representativeness | TEX-06 | 03-01 | Case selection requires domain judgment | Verify 3 cases cover distinct failure categories (type-system mapping, thread mapping, conditional compilation) | ⬜ pending user review |

---

## Known Discrepancies (read-only source documents)

| Source | Says | Actual | Impact |
|--------|------|--------|--------|
| CONTEXT.md D-08 | "4 plans in 3 waves" | 4 plans in 4 waves (Plan 04 is Wave 4, not sharing Wave 3 with Plan 03) | Low — CONTEXT.md is locked; plans and ROADMAP correctly use 4 waves |
| ROADMAP.md SC-6 (P1-8) | "5-10 case studies" | CONTEXT.md D-12 scoped to 3 main-text case studies (full table in appendix) | None — CONTEXT.md decision overrides ROADMAP's original scope |
| ROADMAP.md SC-9 | "grep-based audit" | CONTEXT.md D-17 specifies automated Python script | None — CONTEXT.md decision upgraded the approach |

---

## Validation Audit 2026-04-06

| Metric | Count |
|--------|-------|
| Tasks audited | 8 |
| Automated COVERED | 8 |
| Automated PARTIAL | 0 |
| Automated MISSING | 0 |
| Manual-only items | 5 (pending user review) |
| Unit tests (audit script) | 15/15 pass |
| Audit script result | PASS: 283 verified, 12 unverified (all non-critical counts), 0 broken provenance |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** PASSED — all automated verifications green, 2026-04-06
