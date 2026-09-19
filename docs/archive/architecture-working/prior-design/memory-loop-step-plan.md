# Memory and loop design step

Design only. No runtime edits, dependencies, automations, commits or publication.

Critical point: memory and generated improvements cannot acquire policy or acceptance authority.

1. Verify current main, existing records and current source. Check: git status --short --branch; git rev-parse main; direct source reads. Expected unchanged main d627bb2755ad49865f798bcb095800ddd2ad1ced and preserved work. Completed before edits.
2. Preserve the existing design records in docs/architecture-working/prior-design with a SHA-256 manifest. Check: Python recomputes every saved file digest against its source. Expected exact copies; no runtime paths changed.
3. Develop memory lifecycle and loop/improvement contracts using independent source/code review. Check: documented ownership, correction, lifecycle, alternatives, source links and future acceptance cases are present; review reports name concrete gaps.
4. Cross-critique the new design and verify saved documentation. Check: independent correctness review, Markdown local-link validation, manifest recheck, git diff --check and scoped status. Expected design-only changes; future runtime tests explicitly unrun.

The original review directory is readable but not writable in this session. The durable repository documentation folder is a fallback working location, not a claim that the original review was updated. Existing snapshots remain historical. The current step document and decision delta govern proposed refinements.
