# Fresh correctness review of the ticket packet

Verdict: CHANGES REQUESTED for explicit acceptance coverage and a dependency edge. This is a documentation review, not a runtime verdict.

Critical point: capability dependencies and focused acceptance must prevent a completed predecessor from handing later workers authority machinery that was only assumed.

## Findings

### R1. Assign ordered human steering to a concrete implementation and acceptance population

Verified: `tickets/07-core-07.md:15` creates lifecycle and fixed ingress for submit/status/events/cancel/collect. Its acceptance at lines 21-25 tests stale revisions and evidence capture, but does not assign pause/resume/revise/answer transactions or their ordering cases. The later memory ticket uses authenticated steering, and `tickets/20-native-11.md:27` consumes pause barriers, without another ticket explicitly delivering the general user-steering state machine. Full-body review of all tickets and a case-insensitive search found no acceptance case for resume racing with a newer revision or informational classification racing with a separate pause.

Verified: this behavior is accepted, not optional extra scope. `prior-design/decisions.md:65` records D-STEERING. `prior-design/records-and-transitions.md:88` through its steering section require individually identified requests/barriers, pause versus terminal cancellation, authorized successor runs, stale-answer protection, and resolving only the named barrier. The concrete failure cases are already specified in that contract's proposed steering fixture row.

Impact: the ticket's existing checks could pass a single paused flag or a resume operation that clears every barrier. Such an implementation could resume a cancelled job or accept old work while a newer user change remains unresolved. Merely requiring later transactions to check a barrier does not test how that barrier is established and resolved.

Repair: explicitly assign the typed steering ingress and transition behavior to CORE-07 or a bounded S2 predecessor before CORE-08/NATIVE-02. Add nonempty cases for pause during valid completion, cancel plus late success, stop before/after dispatch, requirement change during checking, duplicate/conflicting steering, stale answers, resume versus newer revision, and informational classification versus unrelated pause. Connect actual provider ingress in NATIVE-03/04 and repeat the relevant races through native integration. Keep the inherited detailed contract; no new service is needed.

### R2. Preserve the accepted shared accounting contract in named cases before native work

Verified: CORE-07/08 use generic settlement and reservation language, NATIVE-02 accounts for required children, and OPS-04 preserves a fixed remote GPU budget. None of the ticket bodies explicitly assigns or tests an effort-wide accounting scope that survives retries, native resume and successor runs. Nor do they assign parent/child usage overlap, provider query-counter resets, unknown usage or elapsed versus active-time semantics to a required population. This was checked across all ticket bodies, not inferred from a single omission.

Verified: `prior-design/decisions.md:64` records D-ACCOUNTING. `prior-design/records-and-transitions.md:22`, `:113` and `:115` define the shared scope, reservations, unknown amounts and time semantics. `prior-design/native-claude-evidence.md:112` specifically warns that native result totals can overlap and counters can reset on resume or clear. CORE-08's exactly-once receipt replay addresses duplicate ingestion, which is a different case from overlapping parent/child totals or reset native accounting epochs.

Impact: every named ticket population can pass while a resumed native attempt receives fresh limits, a successor requirement silently renews the effort allowance, unknown usage is treated as zero, or cumulative provider totals are counted repeatedly. The remote GPU non-reset case does not establish this local/native contract.

Repair: assign the accounting schema, reservations and shared-scope transition cases to CORE-07/08, with provider observation normalization in NATIVE-03/04 and descendant binding in NATIVE-02. Explicitly test retry/successor/resume scope preservation, unknown usage, overlapping parent/child totals, provider-counter reset, retained unresolved reservations, and elapsed/active-time semantics. If exact enforcement is unavailable, require the dependent profile to report that limitation rather than certifying a cap. These are accepted obligations, not a request to invent budget values or change models.

### R3. OPS-06 can become unblocked before the adoption subsystem it must restore exists

Verified: `tickets/27-ops-06.md:9` lists OPS-04, CORE-09 and NATIVE-10. A recursive walk of `ticket-backlog.json` confirms NATIVE-11 is absent from OPS-06's transitive predecessor set. Yet `tickets/27-ops-06.md:33` requires a resurrected adoption negative case. `tickets/20-native-11.md:23` is the ticket that creates the versioned evaluation/decision/activation records and the actual adoption transaction.

Impact: the recommended display order happens to place NATIVE-11 earlier, but `ticket-campaign.md` says dependencies express capability prerequisites and permits independent capability work. A dependency-driven executor could reach OPS-06 without the actual activation records or behavior it is expected to protect. A synthetic marker cannot establish restore safety for the later adoption transaction.

Repair: add NATIVE-11 as an OPS-06 dependency, or explicitly move the actual post-adoption restore regression into a separately blocked integration ticket. Prefer the direct edge because OPS-06 already owns this acceptance requirement. Update JSON, issue body, README and digests together.

## Read coverage and mechanical evidence

Verified by file reads:

- Root AGENTS.md; ticket-campaign.md; decision-delta.md; delivery-workflow.md; consolidated-implementation-plan.md; tickets/README.md.
- All 32 ticket bodies and metadata in ticket-backlog.json. A Python comparison verified each corresponding Markdown file contains the exact body and matches its recorded SHA-256. Every source_paths entry exists. Dependency recursion found no cycle. Output: `Ticket file/count verification: 32 tickets; PASSED`.
- All tickets share one identical campaign suffix, verified programmatically. That suffix was read in full.
- Relevant detailed material: prior-design/configuration-design.md, prior-design/records-and-transitions.md, relevant accepted decision rows in prior-design/decisions.md, native-profile-and-lead-binding.md, relevant first-run-ownership-storage-recovery.md sections, curated-asset-adoption-plan.md, and source-inventory.md routing/current-authority and final source-use sections. Some long combined command output was truncated; claims above use subsequently read targeted passages and do not assert full source-inventory row coverage.
- The baseline adoption map contains 30 entries. A programmatic comparison found every baseline ID explicitly named in the NATIVE-06/07 adaptation batches. This checks assignment, not semantic fidelity of future adaptations.

Reviewed backlog SHA-256: `43387c443813dadf06bda246ee81dc89cda7098983f5d2f532c8f0d4f9d583c6`.

## Scope and self-check

No implementation edits, runtime tests, bin/check, native model calls, GPU work, publication or source-project mutations were performed. This review does not certify native feasibility or empirical usefulness.

The steering/accounting findings are acceptance-assignment gaps. The detailed contracts are present and remain inherited authority; I am not claiming those decisions were deleted. Explicit ticket cases are needed because this packet claims a complete actionable breakdown with nonempty per-step acceptance. The dependency finding was checked independently against both the rendered blocker list and the JSON transitive graph.

No additional actionable gap was confirmed in the reviewed text for full-group early PASS, source/build self-authentication, actual root attribution/withdrawal, historical registry edits, curated baseline deletion, or implementation deferral. This is limited to the read coverage above and is not a claim of runtime correctness.
