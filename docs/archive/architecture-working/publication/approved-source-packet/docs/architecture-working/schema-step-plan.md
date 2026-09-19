# Record and context-delivery design step

Design only. Runtime implementation remains explicitly deferred.

1. Verify current source and preserve pre-existing documentation. Check: `git status --short --branch`, `git rev-parse main`, direct file reads and a SHA-256 inventory stored in `/private/tmp/loam-schema-step-before.json`. Expected local main `d627bb2755ad49865f798bcb095800ddd2ad1ced`; pre-existing changes limited to the documentation directory. Completed before edits.
2. Record the user's acceptance and real-use evaluation requirement. Check: Python assertions over `decision-delta.md` for accepted architecture, no runtime authorization and ongoing evaluation. Expected prior proposals accepted at architecture level, new schema detail still proposed.
3. Refine the proposal, assessment and delivery schemas with independent memory/native-interface review. Check: schema example parses; required identity, authority, source, correction and observation fields are present; all current local document links resolve. Expected concise worker input separated from server-derived authority.
4. Cross-critique and verify preservation. Check: fresh-context correctness review; snapshot manifest plus pre-step digest comparison for untouched files; current document link/whitespace checks and `git diff --check`. Expected documentation-only changes and no claim that future runtime fixtures have passed.

Critical point: context delivery during resume cannot revive obsolete instructions or turn a memory interpretation into current authority.

Completed: acceptance/ongoing-evaluation assertions, proposal JSON and current link checks, preserved prior snapshot checks, source-reader synthesis and fresh-context critique. The review/subject-revision contradiction was repaired and independently rechecked. See [schema-step-validation.md](schema-step-validation.md). Future runtime fixtures remain unimplemented and unrun.
