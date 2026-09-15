# Independent final planning-packet correctness review

Changes requested: one capability dependency is missing.

Critical point: the ticket dependency graph must retain the maintenance authority prerequisite for applying later schema migrations.

## Finding

### P2: Add CORE-09 as a prerequisite of NATIVE-09

Verified: `docs/architecture-working/tickets/05-core-05.md:20` explicitly keeps non-initial migration unavailable until CORE-09 supplies the protected external maintenance-marker machinery. `tickets/17-native-09.md:23` adds the next versioned migration, and `tickets/20-native-11.md:23` adds another S2-managed migration. However, NATIVE-09 lists only CORE-08 and NATIVE-02 as blockers (`tickets/17-native-09.md:9`). A recursive graph walk of the current backlog shows CORE-09 is absent from both NATIVE-09 and NATIVE-11 ancestor sets.

This graph permits the memory and improvement schema work to become capability-ready while the explicitly required migration authority is unavailable. The printed example order happens to place CORE-09 first, but the campaign says edges express capability prerequisites and permits independent capability work. That order cannot substitute for the missing edge. Fresh-store fixtures could still run, but they would not demonstrate safely applying those schema additions to an existing registered store.

Repair: add CORE-09 to NATIVE-09's dependencies and regenerate the ticket header, README and backlog body hashes. NATIVE-11 then receives the prerequisite transitively. In the per-step acceptance, retain a named existing-store migration case using CORE-09's external marker, rather than allowing creation-only tests to imply existing-store migration support.

## Verification and scope

Verified: read all 34 current ticket bodies from `ticket-backlog.json`, the campaign contract, ticket README, source-inventory routing section, consolidated implementation plan, delivery workflow, first complete slice, decision delta, curated adoption contract, remote operator-flow contract, and relevant ownership/storage, native lead-binding and memory-delivery contract sections. Reviewed capability dependencies, preservation obligations, packet availability, hash populations, both-host requirements and the local S3 / remote S4 / full S6 proof boundaries.

Verified: the planning validator exited 0 with:

```text
Ticket packet: PASSED; 34 tickets; dependency DAG valid; source paths and body hashes match
INDEX URL coverage: 65 checked; historical snapshots: 35 unchanged; upstream source files: 74 unchanged
Stages: {'S1': 4, 'S2': 6, 'S3': 13, 'S4': 4, 'S5': 3, 'S6': 3, 'S7': 1}
```

Verified: an independent per-file rehash checked 84 unique source-manifest files with 0 mismatches. Reviewed backlog SHA-256: `0b5ca3c1fd10b3c7f769745ab81c9b0f17bef341ca0639b009eac05832cfa439`.

Verified: the packet expressly blocks execution until its reviewed source packet is accessible to the fresh seat/worktree. Original upstream sections and current implementation/support callers must be inspected and added before code changes. Current packet hashes therefore do not purport to certify every external original. The existing manifest entries resolve to existing files. Proposed runtime and test paths are future implementation destinations, not missing-current-file defects.

Verified: NATIVE-13 owns a nonempty connected local proof on both hosts and providers. OPS-04 owns the separately bounded actual remote native/GPU proof. OPS-10 extends and reruns the full recipient populations. The common campaign clauses retain both-host gates and mark incomplete full groups non-passing until S6. No further actionable gap was found in those boundaries or the stated conservation/preservation requirements within the inspected scope.

## Review limits

Read-only review of the planning packet. No runtime code, bin/check, native provider probe, GPU work, publication or runtime authorization. No author temporary drafts, earlier review reports, ticketing-validation.md or provider/private memory were consulted. The validator hashes referenced files and preserved snapshots without using their review verdicts as review evidence. External originals and actual native/host behavior were not requalified.

Self-attack completed: checked whether the missing edge was supplied transitively, whether printed ordering made it unnecessary, and whether fresh-store setup could satisfy the migration claim. The graph and explicit CORE-05 restriction support the finding; creation-only fixtures remain insufficient evidence for existing-store migration. No additional unsupported correctness claim is made.
