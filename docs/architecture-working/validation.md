# Memory and loop design validation

Scope: documentation preservation and specification review only. No runtime implementation, native model jobs, dependency installation, scheduler activation, commits or publication were performed.

## Evidence checked

- Git verified local main at `d627bb2755ad49865f798bcb095800ddd2ad1ced` before and after the design work. Initial working tree was clean. Final scoped status contains only the new `docs/architecture-working/` directory.
- Read repository instructions, asset-layer guidance, the original architecture-session handoff, current catchup/domain guidance and the relevant current factory progression code. Independent loop inspection checked grader evaluation, recovery, prompt assumptions and learning guidance.
- Reused the preserved source audits with their exact pins/read limits. Reopened the Claude context cookbook and context-engineering article, OpenAI pinned personalization source and the long-running harness article. Directly read relevant cached personalization fallback and memory/compaction source. Independent memory review inspected the concrete memory lifecycle examples.
- Every preserved prior record was compared byte-for-byte to its staged source at copy time. A subsequent SHA-256 check validated the snapshot manifest again. Nested raw research caches were intentionally not copied; the README records that limitation.

## Results observed

```text
Snapshot digest check: PASSED; 35 preserved records
Current design document check: PASSED (links and whitespace; historical snapshots unchanged)
Memory-loop review repairs: PRESENT (specification checks only)
Repository scope check: PASSED (new documentation directory only)
git diff --check: exit 0
```

The checks used Python file reads, hashlib and assertions for manifest digests, current-document local links, whitespace, expected contract clauses and exact Git status scope. Historical snapshots preserve original links, including references to external temporary caches; the current-document link check does not claim those caches are permanently archived. No test suite was run and no proposed future fixture exists by virtue of its command appearing in the design.

## Independent critique

Independent memory and loop readers proposed concrete ownership and evaluation contracts. A fresh-context correctness reviewer then identified that baseline and candidate evaluations could share learned state. The design now requires separate workspaces/memory namespaces, declared initial snapshots, native continuity/reset rules, no transfer between comparison arms and separately reviewed import of evaluation-created lessons. A decisive future contamination case was added.

The final review also checked activation after intervening source correction. Activation now rechecks assessment eligibility, source/criterion dependencies, correction generations, authority and the current predecessor. Rollback rechecks current eligibility. The bounded rereview reported no remaining concrete correctness gap. This is specification critique, not proof of isolation or transactional behavior at runtime.

## Self-attack

- What input breaks the design? A delayed consolidation or contaminated evaluation could restore obsolete advice or claim a false improvement. Explicit revision/correction checks, separate evaluation arms and future fixtures now address those cases in the specification.
- Which caller/path remains unchecked? Real native memory inclusion, retained private caches, interruption and correction delivery. These require the named provider probes and remain unverified.
- What changed without runtime tests? Only design documentation and saved historical records. All future runtime contracts remain unimplemented and untested.
- Which claim lacked evidence? Saving files to the original review directory would have been false. That directory remains unchanged; the README explicitly identifies the repository fallback and omitted raw caches. No empirical memory-quality benefit is claimed.

## Completeness and remaining work

The requested prior work is now saved in repository documentation with verified snapshot hashes. Memory and loop engineering has progressed to a concrete source-grounded contract, alternatives, review policy, current-code mapping and future acceptance cases. Settled user direction and new recommendations are distinct. Independent review and synthesis are recorded. Runtime work remains deferred.

Not done: permanent writes into the originally requested review directory, because the filesystem policy prevents them. Raw research caches are not fully archived in this bundle. Exact production schema, native capability probes, mechanical fixtures and empirical usefulness evaluations remain subsequent design/implementation work. The next discussion is the advisory-promotion policy and concrete record/context-delivery schema.
