---
name: pstack
description: "Pick a pstack method before a non-trivial task: a bug or failing test, code you have not read, a multi-file or batch change, writing or changing tests, an API or shared-state change, a measured number, a review, a hard multi-part job, or calling work done."
allowed-tools: Bash(bash *pstack-path.sh)
---
pstack folder `<P>`: !`bash ${CLAUDE_SKILL_DIR}/pstack-path.sh`
If the folder line above is empty or not an absolute path (you read this file directly, not through the Skill tool), run: jq -r '.plugins["pstack@cursor-plugins"][0].installPath' ~/.claude/plugins/installed_plugins.json
`<S>`: the folder above this file's folder (`${CLAUDE_SKILL_DIR}/..`), holding owner skills; read `<S>/<name>/SKILL.md` by path, never through the Skill tool.

- Skip this skill when your brief came from a pstack skill or already names the method.
- Read each chosen `<P>/skills/<name>/SKILL.md` in full and follow it. Read `<P>/docs/harness/claude-code.md` only when that skill says to.
- Log each method you follow in your decision log (decisions.md in a factory run): `pstack: <skill> | <SKILL.md path read> | <sha256 of that file> | <one line quoted from it> | <the decision it changed>`.
- Never call the Skill tool on a `pstack:` skill. Never use setup-pstack, poteto-help, sharpen, in-your-own-words or make-bot-ui.
- A skill marked (spawns) starts agents. In the main session, state the agent count first, then hand the task and the skill path to one `worker`. A worker runs it within about a dozen agents. Without the Agent tool, use the skill's one-context prompt in its `references/`, or do the delegated role yourself in one context: interrogate's adversary work too, never skipped.
- poteto-mode only for a contested design, concurrency or a cross-cutting change (standing ruling: 1.9x cost, no quality gain in the pilot). Stop before any push or PR that a playbook asks for.
- When two rows fit, take the higher row, and also read every principle whose line fits.

| Situation (broad to narrow) | Skill |
|---|---|
| A hard multi-part job or large migration | figure-it-out (spawns) |
| A contested design, concurrency or a cross-cutting change | poteto-mode (spawns) |
| Several competing designs | principle-exhaust-the-design-space; arena (spawns) |
| A better approach or a missed problem, before or after a design is settled | `<S>/surprise-me` |
| Caller usage, types and module shape before a new module | architect (spawns) |
| Explaining a change or subsystem to the owner | teach |
| Many similar units | principle-build-the-lever; swarm (spawns) |
| A bug or failing test | principle-fix-root-causes; tdd for a cheap local test; principle-attack-the-premise after two failed fixes |
| How or why code works | how, why (spawns) |
| A multi-step change | principle-sequence-verifiable-units |
| A measured number | principle-explain-the-number; benchmark-checklist for a timing |
| Shared, retried or concurrent code | blast-radius; principle-make-operations-idempotent; principle-separate-before-serializing-shared-state |
| Merged code changed what a formal-verification skill models | maintain-formal-verification-skill |
| Review of finished non-trivial work | `<S>/audit` (spawns; its size scales with the work) |
| A diff you do not trust | interrogate (spawns) |
| A long or unattended run | show-me-your-work (spawns 1) |
| A long task or a batch of runs landed: capture what worked as a skill or rule edit | reflect (spawns; unattended, its input is the run transcripts and ledgers it is given, not its own chat) |
| The same mistake corrected twice, or a batch of runs showing a repeated mistake class | correct (fix at the highest level that works: structure, then a check, then a test, docs last); principle-encode-lessons-in-structure |
| Repeated manual steps or owner corrections to mine | automate-me (spawns; in an agent run, draft its output in the repo, never under `~/`) |
| Before saying done | principle-prove-it-works |

Principles:
- principle-attack-the-premise: two fixes on one premise failed
- principle-boundary-discipline: wiring validation, error handling or adapters
- principle-build-the-lever: work a script could do or prove
- principle-encode-lessons-in-structure: the same correction a second time
- principle-exhaust-the-design-space: novel architecture or UI, no precedent
- principle-experience-first: product, UX or feature-scope tradeoffs
- principle-explain-the-number: measuring, trusting or reporting a number
- principle-fix-root-causes: debugging any symptom
- principle-foundational-thinking: choosing core types and data structures
- principle-guard-the-context-window: large outputs or long files fill context
- principle-laziness-protocol: refactoring, or tempted to add a layer
- principle-make-operations-idempotent: steps that must survive crashes, retries
- principle-migrate-callers-then-delete-legacy-apis: new internal API, old callers remain
- principle-minimize-reader-load: code that is hard to trace
- principle-model-the-domain: stateful logic or heavily branching code
- principle-never-block-on-the-human: tempted to ask about reversible work
- principle-outcome-oriented-execution: planned rewrites and migrations in phases
- principle-prove-it-works: before declaring done
- principle-redesign-from-first-principles: a new requirement in an existing design
- principle-separate-before-serializing-shared-state: concurrent writers to one file or key
- principle-sequence-verifiable-units: multi-step work, stacked commits or PRs
- principle-subtract-before-you-add: sequencing an addition, refactor or rewrite
- principle-test-behavior-not-implementation: writing, changing or keeping a test
- principle-type-system-discipline: designing types or function signatures
