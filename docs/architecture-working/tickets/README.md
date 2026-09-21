# Generated factory ticket backlog

The loop factory's own roadmap and its frozen items are in `docs/factory/ROADMAP.md`. The archived working corpus is in `docs/archive/architecture-working/`.

**Status: live index; CORE-01, CORE-02, CORE-04 and NATIVE-05 are merged, the first method shipped in SLICE-01 (PR #148), every other ticket is a draft that is assessed before it is built.**

Read the [campaign contract](../ticket-campaign.md), [source inventory](../source-inventory.md), and [tool assessment](../ticketing-tool-assessment.md). Each link below opens the complete issue body. IDs are stable planning identifiers, not GitHub issue numbers. The order is topological; independent capability work is possible, but each integrated step still starts from latest main. Later tickets are revalidated against qualification results before their plan review.

| Order | Ticket and result | Stage | Blocked by |
|---|---|---|---|
| 1 | [CORE-01: Ship and independently verify a buildable factory payload](01-core-01.md) | S1 | Implementation authorization + source packet |
| 2 | [CORE-02: Qualify storage, lifetime locks and candidate containment on both hosts](02-core-02.md) | S1 | CORE-01 |
| 3 | [CORE-04: Admit an isolated installed runtime from an independent trust source](03-core-04.md) | S1 | CORE-02 |
| 4 | [CORE-03: Qualify actual native profile and lead evidence in bounded scratch sessions](04-core-03.md) | S1 | CORE-02, CORE-04 |
| 5 | [CORE-05: Open and retain sole authority over an existing registered store](05-core-05.md) | S2 | CORE-04 |
| 6 | [CORE-06: Resume explicit first setup without replacing an existing instance](06-core-06.md) | S2 | CORE-05 |
| 7 | [CORE-07: Record a bounded task and durably capture its deterministic check](07-core-07.md) | S2 | CORE-06 |
| 8 | [CORE-10: Preserve user control and effort limits across work revisions](33-core-10.md) | S2 | CORE-07 |
| 9 | [CORE-08: Reconnect to the original host and settle captured results once](08-core-08.md) | S2 | CORE-07, CORE-10 |
| 10 | [CORE-09: Back up and restore local history through a durable external barrier](09-core-09.md) | S2 | CORE-08 |
| 11 | [NATIVE-01: Admit an explicit native profile and show truthful readiness](10-native-01.md) | S3 | CORE-03, CORE-08 |
| 12 | [NATIVE-02: Account for dynamic required work and independent review](11-native-02.md) | S3 | NATIVE-01, CORE-08 |
| 13 | [NATIVE-03: Bind Claude root decisions, Workflow and advisor evidence](12-native-03.md) | S3 | NATIVE-01, NATIVE-02, CORE-03 |
| 14 | [NATIVE-04: Bind Codex root decisions and native consultation](13-native-04.md) | S3 | NATIVE-01, NATIVE-02, CORE-03 |
| 15 | [NATIVE-05: Catalog every curated method and supporting native asset (ASSET-01)](14-native-05.md) | S3 | CORE-01 |
| 16 | [NATIVE-06: Repair curated planning and review methods (ASSET-02a)](15-native-06.md) | S3 | NATIVE-03, NATIVE-04, NATIVE-05 |
| 17 | [NATIVE-08: Add cross-project critique and simpler-design review (ASSET-03)](16-native-08.md) | S3 | NATIVE-05, NATIVE-06, NATIVE-03, NATIVE-04 |
| 18 | [NATIVE-09: Capture and assess source-linked project memory](17-native-09.md) | S3 | CORE-08, NATIVE-02, CORE-09 |
| 19 | [NATIVE-10: Deliver corrected memory to fresh native work and record real use](18-native-10.md) | S3 | NATIVE-09, NATIVE-03, NATIVE-04 |
| 20 | [NATIVE-07: Repair curated continuity and execution methods (ASSET-02b)](19-native-07.md) | S3 | NATIVE-05, NATIVE-09, NATIVE-10, NATIVE-02, NATIVE-06 |
| 21 | [NATIVE-11: Evaluate a fixed improvement and record the actual lead decision](20-native-11.md) | S3 | NATIVE-03, NATIVE-04, NATIVE-09, NATIVE-10, CORE-08 |
| 22 | [NATIVE-12: Add generic experiments and source-evidence audits (ASSET-04)](21-native-12.md) | S3 | NATIVE-05, NATIVE-06, NATIVE-07, NATIVE-11 |
| 23 | [NATIVE-13: Prove the connected local research and recovery story](34-native-13.md) | S3 | NATIVE-07, NATIVE-08, NATIVE-10, NATIVE-11, NATIVE-12, CORE-09 |
| 24 | [OPS-01: Explain readiness for the selected local and remote profile](22-ops-01.md) | S4 | CORE-04, NATIVE-05, NATIVE-01 |
| 25 | [OPS-02: Recover one durable Linux launch through lost replies and runner restarts](23-ops-02.md) | S4 | OPS-01, CORE-02, CORE-08 |
| 26 | [OPS-03: Launch remote native work from verified inputs and collect current evidence](24-ops-03.md) | S4 | OPS-02, NATIVE-03, NATIVE-04, NATIVE-02 |
| 27 | [OPS-04: Enforce mixed offline behavior at each job host with a simple personal queue](25-ops-04.md) | S4 | OPS-02, OPS-03 |
| 28 | [OPS-12: Prove real Mac-led Linux native and GPU work](35-ops-12.md) | S4 | OPS-04, NATIVE-13 |
| 29 | [OPS-05: Adopt a staged update only after a race-free drain](26-ops-05.md) | S5 | OPS-04, CORE-04, CORE-09 |
| 30 | [OPS-06: Restore remote history without reopening retired requests or withdrawn memory](27-ops-06.md) | S5 | OPS-04, CORE-09, NATIVE-10, NATIVE-11 |
| 31 | [OPS-07: Fence the old controller before moving ownership to a replacement machine](28-ops-07.md) | S5 | OPS-04, OPS-06 |
| 32 | [OPS-08: Deliver every curated asset and declare specialist prerequisites](29-ops-08.md) | S6 | NATIVE-05, NATIVE-06, NATIVE-07, NATIVE-08, NATIVE-12, OPS-01 |
| 33 | [OPS-09: Prove exact factory source and build survive every render and update](30-ops-09.md) | S6 | OPS-08, OPS-05, OPS-06, OPS-07, CORE-01 |
| 34 | [OPS-10: Prove the connected factory on both hosts and providers without retiring the old controller](31-ops-10.md) | S6 | OPS-09, NATIVE-12, CORE-09, NATIVE-11, NATIVE-03, NATIVE-04, NATIVE-02, OPS-04, OPS-07, NATIVE-13, OPS-12 |
| 35 | [OPS-11: Evaluate installed memory on real project work and retain harmful outcomes](32-ops-11.md) | S7 | OPS-10, NATIVE-11 |

## Session C verdicts (2026-09-20)

Assessed before the first method slice (SLICE-01, `hypothesis-tree` delivered by Copier). None is cut; none is on the path to a runnable method.

- CORE-05: keep open for the work-record line; delivers no method; reassess before building. Not part of SLICE-01.
- CORE-06: keep open for the work-record line; delivers no method; reassess before building. Not part of SLICE-01.
- CORE-07: keep open for the work-record line; delivers no method; reassess before building. Not part of SLICE-01.

## Curation verdicts (2026-09-20)

From `docs/research/curation-2026-09-20.md`, section "The memory design, verified and placed". The accepted memory design and the 2026-09-03 design overlap on retrieval and storage of bodies and differ on who activates a lesson and when to measure; the evidence there (findings 1, 6, 7) says measure before building the store. None is cut.

- NATIVE-09: blocked by the level-2 memory measurement (raw trace capture, recall, `memsearch`, the weekly recurring-errors report, zero model calls). Build only if that report shows recurring errors a card would have prevented; reassess before building.
- NATIVE-10: same block as NATIVE-09.
- NATIVE-11: same block as NATIVE-09; its improvement-evaluation shape stays the reference for OPS-11.

## Approval covers publication only

Recommended: publish this reviewed set under a new generated-factory campaign parent, with native dependency links, planned status and no assignees or `ready-for-agent` label. Existing historical maps stay unchanged. See [publication requirements](../ticket-campaign.md#publication-transaction). The separately scoped real-use evaluation follows S6 and does not block the initial controlled proof.
