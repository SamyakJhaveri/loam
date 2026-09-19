# Original loop repository source review

Verified: all assigned original repositories were accessed using GitHub metadata/tree APIs and commit-pinned raw files. No source program, installer, agent, worker, automation, test suite or runtime from these repositories was executed. Only read-only acquisition and inspection occurred. Local Loam source was not changed. Downloads live under `/private/tmp/loam-architecture-design/loop-originals/`.

Critical point: confusing a durable receipt or a native host status with verified task completion. Independent evidence must bind the exact candidate and check definition; recovery must not duplicate an already executed effect.

Scope uses READ to mean content actually displayed and inspected, SEARCH to mean targeted text search, and DOWNLOADED to mean acquisition only. Large files are explicitly partial. Neither README nor source inspection proves runtime behavior or vendor benchmarks. Probes below are proposed acceptance fixtures, not executed tests.

The task requirements supersede old rejection criteria: complete independent factory availability in every seed; native Codex and Claude worker autonomy; Astra/Fable drivers with the user-selected effort and allowed roster; durable recovery; truthful checks; evidence-linked memory without automatic policy mutation. No model/effort configuration was changed. Existing local docs inspected for comparison: `docs/research/loop-repos.md`, `docs/research/primary-2026-09-08/loop-repos.md`, `docs/ASSET-LAYERS.md`, `docs/factory/ARCHITECTURE.md`, and selected `bin/factory` freeze/accounting/resume functions.

## Highest-value design corrections

- Do not preserve obsolete rejection rationale. S10 has actual implementation; S02 now has provider-aware `_resolve_role_model`; S03 now calls Anthropic directly. Their current incompatibilities are narrower and independently identifiable.
- Make the supervisor recover execution identities and receipts, not merely the last round filename. S01's journal/session reconciliation and S07's event/snapshot binding offer concrete shapes.
- Make completion a supervisor decision over exact evidence. S06 checks command results and definition freshness; S03 honestly labels unperformed semantic verification; S10 separates successful command execution from accepted outcomes.
- Keep native workers free to choose tools and delegation within permissions. Reject S02's executor Agent prohibition and S07's persona hierarchy. Independence is a reviewer property, not a mandate to destroy worker context every turn.
- Treat artifact and memory identity as content, not size, line counts or presentation state. S10's numstat snapshot and S08's length-based image hash are insufficient; X07's disk/config dictionaries are not persistence.
- Reopen earlier rejection of small leases, typed retries and transactional storage. The full independent multi-day factory requirement makes concurrency and restart correctness mandatory. There is no need to wait for a production failure before validating a known recovery invariant.
- Ship the whole local runtime/configuration/check capability in seed with on-demand operational guidance. “Small prompt footprint” and “complete factory installed” are compatible. Optional global/plugin availability cannot be a hidden dependency.

## S01: huangruiteng/loopx

Verified source revision: `4e73428ff3f170578a3be12bde15c2612cf55f99`. [Original README at revision](https://github.com/huangruiteng/loopx/blob/4e73428ff3f170578a3be12bde15c2612cf55f99/README.md). Access status: original accessible.

Read scope: selected README sections covering control-plane boundary, peer ownership, evidence limits, installation and native host drivers; full Claude adapter README; full `loopx/control_plane/turn_driver/recovery.py`, `session_recovery.py`, and `loopx/control_plane/quota/refresh_recovery.ts`. Metadata/tree, LICENSE header, LICENSE-MIT header, NOTICE and relevant package manifests read. `task_lease_acquire.ts` was downloaded but not read and is not evidence here.

Verified: `assess_existing_turn_recovery` makes one typed decision from journal and host-session inspection. `assess_failed_turn_retry_request` refuses wrong schema, wrong failed phase, unavailable resolver, and failed session binding. `build_turn_recovery_audit` records planned decision separately from actual status and whether the host was invoked. `refreshRecovery` distinguishes first append, identical replay, missing receipt repair, bounded missing checkpoint/workspace supplementation, and conflicting committed-payload rejection. These are concrete recovery mechanisms, independent of the optional Claude tool-matcher hook.

Recommendation: ADAPT these recovery contracts into the full seed factory supervisor. Preserve native Astra/Fable execution and same-session continuation when host identity can be verified. Reconcile durable results before relaunching. Do not blindly repeat a worker because the controller missed its result. Keep execution identity, receipt identity, artifact revision and intended effect bound together. REJECT whole dependency and optional destructive-command substring hardening as the factory's permission boundary.

Historical revision: the prior `/goal` incompatibility remains true for its Claude adapter, but rejecting that adapter does not reject typed journal recovery. Its current README explicitly supports native Codex `/goal`; no blanket anti-native conclusion is justified.

Loam target: replacement for `bin/factory::cmd_run` resume-by-last-check-file and frozen manifest handling, distributed under the seed factory rather than an optional plugin. Probe: interrupt after result persistence but before receipt publication; restart must reconstruct the receipt without invoking the worker again. Change the native session binding or replay a different payload under the same turn ID; continuation must refuse with an explicit typed reason.

Reuse: current code Apache-2.0; NOTICE retains historical MIT distribution through a previous release, so do not label current source simply dual-licensed. Python core plus a Node TypeScript control plane; README/package require Python >=3.11 and Node >=22.18.0. Selected recovery functions depend on internal driver/projection/decoder modules. Borrow contracts and reimplement narrowly, or carry the dependency closure and notices if literal code is copied.

Implementation links: [loopx/control_plane/turn_driver/recovery.py](https://github.com/huangruiteng/loopx/blob/4e73428ff3f170578a3be12bde15c2612cf55f99/loopx/control_plane/turn_driver/recovery.py), [loopx/control_plane/turn_driver/session_recovery.py](https://github.com/huangruiteng/loopx/blob/4e73428ff3f170578a3be12bde15c2612cf55f99/loopx/control_plane/turn_driver/session_recovery.py), [loopx/control_plane/quota/refresh_recovery.ts](https://github.com/huangruiteng/loopx/blob/4e73428ff3f170578a3be12bde15c2612cf55f99/loopx/control_plane/quota/refresh_recovery.ts).

## S02: AMAP-ML/LongHorizon-Harness

Verified source revision: `a1dd930614972b92361c1b9cd6aac441a6db5a65`. [Original README at revision](https://github.com/AMAP-ML/LongHorizon-Harness/blob/a1dd930614972b92361c1b9cd6aac441a6db5a65/README.md). Access status: original accessible.

Read scope: README introduction/loop/roles and CLI configuration/recovery sections; `src/lh_harness/manager.py` 325-360, 499-568, 1516-1540; `role_prompts.py` 238-279, 428-440, 481-511; `adapters/claude_permissions.py` 1-90; `cli.py` 2015-2077. Other downloaded manager/service content was searched or unreviewed, not fully audited. LICENSE header and pyproject read.

Verified: manager reconstruction consumes original task, maintained task state and auditor reports. `MANAGER_NEXT_DONE` requires `_latest_auditor_is_clean_complete`; an unsupported completion produces an invalid-completion repair record. Auditor prompt requires direct inspection of actual application/files and treats executor prose and old reports as claims. The role resolver now stops model and effort inheritance at an explicit backend switch.

Recommendation: ADAPT artifact-grounded state promotion, explicit invalid completion, and provider-aware role resolution. Preserve the user's selected effort and allowed roster; unresolved cross-provider settings must produce a clear configuration error, never silently lower effort or change model. ADAPT recovery by rereading the real workspace after an interrupted native session, without making every worker step a fresh manager/executor/auditor microcycle. REJECT permission bypass, executor `Agent` prohibition, and parsing natural-language control headers as the acceptance protocol.

Historical revision: local `loop-repos.md` says there is no `_resolve_role_model`; current `cli.py:2030` defines it, with `_resolve_role_reasoning_effort` at 2050. Old fixed Opus-worker/Fable-judge requirements are superseded by the user's two native ecosystems. Current permissions still explicitly set bypassPermissions and disallow Agent for executors, so that disqualifier remains concrete.

Loam target: seed factory adapter configuration and acceptance-state reducer. Probe: manager claims done with no independent receipt, or only an older receipt for a changed candidate; done must remain false. Switch the configured backend without a supported explicit model/effort resolution; preflight must reject before spawning. Native worker delegation must remain available.

Reuse: MIT. Full runtime requires Python >=3.10, packaging, conditional tomli, FastAPI, uvicorn and websockets. The resolver pattern can be implemented with standard configuration code; do not import the GUI supervisor merely to obtain it.

Implementation links: [src/lh_harness/cli.py](https://github.com/AMAP-ML/LongHorizon-Harness/blob/a1dd930614972b92361c1b9cd6aac441a6db5a65/src/lh_harness/cli.py), [src/lh_harness/manager.py](https://github.com/AMAP-ML/LongHorizon-Harness/blob/a1dd930614972b92361c1b9cd6aac441a6db5a65/src/lh_harness/manager.py), [src/lh_harness/adapters/claude_permissions.py](https://github.com/AMAP-ML/LongHorizon-Harness/blob/a1dd930614972b92361c1b9cd6aac441a6db5a65/src/lh_harness/adapters/claude_permissions.py).

## S03: ray-r-ren/agent-apprenticeship

Verified source revision: `4beafff2ff41da7d97a4faee9b516ccde466fb4b`. [Original README at revision](https://github.com/ray-r-ren/agent-apprenticeship/blob/4beafff2ff41da7d97a4faee9b516ccde466fb4b/README.md). Access status: original accessible.

Read scope: full README; `src/agent_apprenticeship_trace/verifier.py` full; `loop.py` baseline/revision control flow and final signal emission; `openai_structured.py` provider discovery search and 321-363; pyproject/package and LICENSE header. Downloaded evaluator.py was not substantively read.

Verified: `deterministic_verify` marks `verification_status='not_run'` and explicitly describes structural guardrails. Model verification separately records provider/model, prompt hash and artifact-preview provenance. `run_task` is a baseline then one revision, setting actual_iterations=2. It writes traces, grading, feedback and signal packages rather than providing a native persistent driver.

Recommendation: ADAPT the distinction between package integrity, semantic verification and unavailable verification. ADAPT experience packages as evidence-linked memory candidates containing attempted approach, actual result, reviewer correction, artifact references and applicability conditions. Do not automatically promote extracted lessons into always-on policy. REJECT its fixed training pipeline as Loam's runtime, and do not equate the highest scalar score with accepted completion.

Historical revision: the prior claim that mentors are forced through an OpenAI-shaped API is false for current source. `_anthropic_response` calls Anthropic Messages directly and provider dispatch includes Anthropic and Google. However verifier per-role model overrides still apply only when provider is openai, and this is an API judge rather than the user's required native Fable driver. Narrow the rejection to those actual incompatibilities.

Loam target: receipt schema, memory candidate archive and retrieval/review workflow. Probe: make the semantic verifier unavailable while structural checks pass; result must say not_run and cannot promote accepted state. A lesson derived from a rejected attempt remains retrievable with rejection evidence but cannot alter seed rules.

Reuse: MIT. Full package Python >=3.11 with pydantic, typer and openai dependencies. Selected verifier code is coupled to project schemas, artifact previews and provider layer. Reimplement the result-status and provenance contract instead of vendoring the training stack.

Implementation links: [src/agent_apprenticeship_trace/verifier.py](https://github.com/ray-r-ren/agent-apprenticeship/blob/4beafff2ff41da7d97a4faee9b516ccde466fb4b/src/agent_apprenticeship_trace/verifier.py), [src/agent_apprenticeship_trace/loop.py](https://github.com/ray-r-ren/agent-apprenticeship/blob/4beafff2ff41da7d97a4faee9b516ccde466fb4b/src/agent_apprenticeship_trace/loop.py), [src/agent_apprenticeship_trace/openai_structured.py](https://github.com/ray-r-ren/agent-apprenticeship/blob/4beafff2ff41da7d97a4faee9b516ccde466fb4b/src/agent_apprenticeship_trace/openai_structured.py).

## S04: cobusgreyling/loop-engineering

Verified source revision: `336c3296bcd51a60cca251196d723821bee64b48`. [Original README at revision](https://github.com/cobusgreyling/loop-engineering/blob/336c3296bcd51a60cca251196d723821bee64b48/README.md). Access status: original accessible.

Read scope: full README; full `tools/loop-context/src/context-manager.ts` and `daily-spend.ts`; LICENSE header and root package manifest. `skills/loop-verifier/SKILL.md` downloaded but not needed as primary evidence for the mechanisms below.

Verified: `pruneLedger` returns a new compact view while preserving original ledger. `errorSignature` normalizes volatile values; circuit breaker compares character trigrams. `recordDailySpend` serializes read-modify-write with an exclusive lock file but persists via direct writeFile. `readState` treats every read/parse error as no state. A lock older than its fixed stale threshold can be removed without checking owner liveness.

Recommendation: ADAPT compact projections over retained raw evidence, and one atomic transaction for quota reservation and settlement. REJECT fuzzy action-similarity as automatic stop policy: a native worker can repeat commands productively and normalization can erase meaningful distinctions. REJECT literal daily-spend implementation as crash-safe accounting: malformed state must become unknown/error, not zero; live owners must not lose locks solely because time passed. Loam's scope now needs durable multi-project independence; machine/global budget aggregation may be optional, but each seed must own its local run state.

Historical revision: token accounting rather than dollar accounting was correctly clarified locally. Prior rejection of fuzzy frustration checks remains justified. Prior simplicity estimates and old model-inheritance rejection do not govern the new design. State integrity is required by recovery semantics even before a ledger has recorded a failure.

Loam target: seed factory event projection, budget store and progress diagnosis. Probe: kill during spend persistence, then reopen; usage cannot reset to zero. Concurrent reservations cannot oversubscribe an explicit cap. Repeating a diagnostic command after a real code change must not automatically trip an action-text breaker.

Reuse: MIT; selected TypeScript modules use Node built-ins and no third-party runtime imports. Preserve attribution if adapting code. Prefer a transactional local store or robust append/commit protocol to copying its lock-and-overwrite code.

Implementation links: [tools/loop-context/src/context-manager.ts](https://github.com/cobusgreyling/loop-engineering/blob/336c3296bcd51a60cca251196d723821bee64b48/tools/loop-context/src/context-manager.ts), [tools/loop-context/src/daily-spend.ts](https://github.com/cobusgreyling/loop-engineering/blob/336c3296bcd51a60cca251196d723821bee64b48/tools/loop-context/src/daily-spend.ts).

## S05: Forward-Future/loopy

Verified source revision: `75966cbd572a4185064971c9fe5e9c52e8f8456d`. [Original README at revision](https://github.com/Forward-Future/loopy/blob/75966cbd572a4185064971c9fe5e9c52e8f8456d/README.md). Access status: original accessible.

Read scope: substantive README through workflow/receipt/discovery sections; full `skills/loopy/references/run.md` and `debrief.md`; LICENSE header. These Markdown references are the actual implementation of the selected skill behavior; website code was not reviewed because it is unrelated to factory execution.

Verified: run preparation preserves exact loop definition or immutable identity, conditions, scope and stopping boundary. It distinguishes success, no-op, blocked, approval required, exhausted and no progress. Debrief separates loop design, execution choice, environment failure and changed/unrealistic goal, and limits single-run conclusions to that run.

Recommendation: ADAPT a compact run receipt and evidence-linked debrief with these distinct causes. Make durable receipts normal for the explicitly requested long-running factory, using established project convention. Preserve full local factory availability in every seed while loading instructional prose only on demand. REJECT its conversational-only receipt default and user interview for every missing run boundary as runtime behavior. Resolve authorized defaults at factory configuration/preflight, with honest blocked status when a genuinely required bound is absent.

Historical revision: correctly rejected as an executable supervisor, but that is not a reason to reject its task outcome and debrief schema. Its arbitrary-budget caution supports progress-sensitive stop policy, not unlimited execution or overriding user limits.

Loam target: shared seed factory skill/reference plus receipt/debrief schema; no dependence on hosted loop catalog. Probe: the same task has a successful no-op, command error, missing approval and exhausted bound; each maps to a different terminal result. Debrief a single failed receipt; generated memory must cite that run and cannot claim a general policy from it.

Reuse: MIT prose adaptation with attribution if copied. Selected references need no runtime dependency. Website and installation tooling are not dependencies of the borrowed pattern.

Implementation links: [skills/loopy/references/run.md](https://github.com/Forward-Future/loopy/blob/75966cbd572a4185064971c9fe5e9c52e8f8456d/skills/loopy/references/run.md), [skills/loopy/references/debrief.md](https://github.com/Forward-Future/loopy/blob/75966cbd572a4185064971c9fe5e9c52e8f8456d/skills/loopy/references/debrief.md).

## S06: Leonxlnx/unlazy

Verified source revision: `16671491f6679ad9378f52604d3bc2415b4120c7`. [Original README at revision](https://github.com/Leonxlnx/unlazy/blob/16671491f6679ad9378f52604d3bc2415b4120c7/README.md). Access status: original accessible.

Read scope: README lines 1-160; `scripts/lib/gates.mjs` 427-496, 509-554, 696-730, 907-941; `scripts/gate-check.mjs` 603-648, 725-753, 811-860 and targeted function searches; package manifest and LICENSE header. Neither full checker nor dispatch implementation was audited.

Verified: gateDefinitionDigest binds CHECK, EXPECT and raw CWD; automatic evidence binds definition plus output hash and successful exit/match. Check execution fails on timeout/output overflow. Before publishing results it reloads the ledger under lock and refuses changed definition/runtime identity. Parent reverify reruns even previously met gates. `globsOverlap` conservatively proves disjointness; `claimLeases` checks conflicts and writes under the same registry lock. README explicitly says unkeyed digest is drift detection, not tamper resistance, and approval does not hash transitive scripts/fixtures.

Recommendation: ADAPT check receipts bound to command, execution environment, candidate content digest and declared dependency digest. Preserve named abandonment as incomplete handoff. Retain parent integration checks on the actual combined candidate. Revisit blanket rejection of leases: the new supervisor needs durable ownership across restarts and cooperating drivers, even if native workers choose their own delegation. A small root-run lease plus native child-handle records can satisfy this without importing dispatch-wave bureaucracy. REJECT tree-depth quotas and hook-based claims of hard isolation.

Historical revision: previous one-process ownership rationale does not establish safety after a crash or concurrent independent launch. Prior decision to omit gate-lint remains reasonable only if alternative checks catch the same defect. Baseline failure alone cannot prove English criterion and oracle actually correspond; retain independent contract review.

Loam target: frozen check contract, receipt commit, ownership/recovery ledger and final integration verification. Probe: edit a called check script without changing command text; old evidence must become stale. Change the gate while it runs; its result must not publish. Concurrent conflicting claims cannot both succeed, and abandonment cannot become success.

Reuse: MIT; Node >=16, no third-party runtime packages in manifest. The selected functions depend on local safe-state/locking helpers. Existing Loam attribution for globsOverlap should be preserved; do not copy the entire checker merely for digest logic.

Implementation links: [scripts/lib/gates.mjs](https://github.com/Leonxlnx/unlazy/blob/16671491f6679ad9378f52604d3bc2415b4120c7/scripts/lib/gates.mjs), [scripts/gate-check.mjs](https://github.com/Leonxlnx/unlazy/blob/16671491f6679ad9378f52604d3bc2415b4120c7/scripts/gate-check.mjs).

## S07: Spielewoy/autoprompt-skill

Verified source revision: `b6516cf52a7891d797621fdd2a8ca0311e1ae0a9`. [Original README at revision](https://github.com/Spielewoy/autoprompt-skill/blob/b6516cf52a7891d797621fdd2a8ca0311e1ae0a9/README.md). Access status: original accessible.

Read scope: README 1-140; `agents/claude/workflow/autoprompt-gate.js` 915-968 and 1763-1827; `agents/codex/workflow/recovery-checkpoint.js` 1-56, 985-1050, 1103-1159 plus function/field search; LICENSE header and package manifest selected fields. Full hierarchy, checkpoint dependency closure, and worker runtime were not audited. Downloaded GATES.md not used as substitute for implementation.

Verified: `groundedVerifyReasons` does not treat omitted affirmative evidence as a pass. `withRetry` splits non-transient failures from bounded retries. Codex recovery records bind run/activation/mission/target, event sequence, accounting sequence, candidate hash, native session/continuation/lease/result identities. It rejects incomplete crash tails, hash-chain mismatch and snapshots ahead of or foreign to the authoritative log. A behind snapshot is discarded for rebuilding. Append uses O_NOFOLLOW where available, physical-file checks, fsync and directory fsync.

Recommendation: ADAPT small durable recovery records with monotonic sequence, authoritative append log plus replaceable projection, idempotent result IDs and candidate-bound checks. ADOPT the invariant that absent verification evidence cannot authorize success. REJECT full persona hierarchy, arbitrary universal coverage floors and constrained worker choreography. Native worker autonomy does not remove the supervisor's responsibility to account for a live child and survive partial writes.

Historical revision: 'no observed empty evidence in prior judge rounds' is not a reason to omit schema/evidence validation. It is a cheap correctness invariant. 'no prior transient failure' likewise does not meet a multi-day recovery requirement. Retry may be added only around typed recoverable failure and reconciled operation state; blindly redispatching a potentially side-effecting call remains wrong.

Loam target: seed factory recovery and result admission, strict grader envelope validation. Probe: crash between event append and snapshot; reopen must rebuild. Inject a truncated last record, foreign session result, missing evidence field and replayed result ID; each must be explicitly rejected/reconciled with no duplicate worker or usage settlement.

Reuse: MIT. Repository requires Node >=20 plus Python/PyYAML and Bash for full tooling. Recovery file itself uses Node built-ins but imports event-log, safe-run-root, runtime-state, mission-lock and schemas. Adapt its invariants, not that whole dependency graph.

Implementation links: [agents/codex/workflow/recovery-checkpoint.js](https://github.com/Spielewoy/autoprompt-skill/blob/b6516cf52a7891d797621fdd2a8ca0311e1ae0a9/agents/codex/workflow/recovery-checkpoint.js), [agents/claude/workflow/autoprompt-gate.js](https://github.com/Spielewoy/autoprompt-skill/blob/b6516cf52a7891d797621fdd2a8ca0311e1ae0a9/agents/claude/workflow/autoprompt-gate.js).

## S08: chenxiachan/thoughtdag

Verified source revision: `ef04210f6106a0dbc30f353cf67b25bee47d769c`. [Original README at revision](https://github.com/chenxiachan/thoughtdag/blob/ef04210f6106a0dbc30f353cf67b25bee47d769c/README.md). Access status: original accessible.

Read scope: README 1-140; `src/store/context-builder.ts` 1-180; full `src/lib/session-handoff.ts`; package manifest and LICENSE header. Context graph partition/query CLI and benchmark artifacts were not inspected; no claim of benchmark reproduction or full retrieval audit.

Verified: context-builder defines an ordered material/reference/live-chain/current-question assembly and parallel per-message provenance. Upstream fingerprints deliberately ignore presentation-only collapse/summary changes, so display state does not masquerade as changed source evidence. It marks answers stale when upstream context changes. Its hashContext is a small noncryptographic rolling hash and image contribution uses data lengths, unsuitable as a trust-grade artifact digest.

Recommendation: ADAPT context manifests: every memory item records source artifact/turn, exact content digest, scope, status and dependencies; derived summaries carry upstream links and become stale when evidence changes. Retrieve relevant excerpts into a native session instead of injecting all history or requiring forced fresh sessions. Preserve old source records so a reviewer can reopen evidence. REJECT UI/canvas dependency and use cryptographic content hashes for receipts.

Historical revision: local note calls the pilot the strongest argument for fresh context per round. The source scope here does not establish that universal policy for Astra or Fable. The concrete lesson is selective provenance and invalidation; use native continuation unless context is contaminated or the task boundary calls for independent judgment. A stale item is evidence to inspect, not automatic global policy.

Loam target: seed memory store, retrieval context packet and derived-summary invalidation. Probe: change an upstream artifact with identical byte length; its summary/receipt must become stale. Toggle a display-only flag; evidence validity must not change. A retrieved lesson must open the exact source turn or file revision and show whether that attempt was accepted.

Reuse: MIT. Full app has React, Zustand, Vite and AI SDK ecosystem dependencies; selected code imports graph, attachment, tokenizer and UI helpers. Reimplement the provenance/invalidation schema independently; no desktop runtime needed.

Implementation links: [src/store/context-builder.ts](https://github.com/chenxiachan/thoughtdag/blob/ef04210f6106a0dbc30f353cf67b25bee47d769c/src/store/context-builder.ts).

## S09: anthropics/cwc-long-running-agents

Verified source revision: `ad107a974bced5244f74dd283dbf2bfd3baee3a1`. [Original README at revision](https://github.com/anthropics/cwc-long-running-agents/blob/ad107a974bced5244f74dd283dbf2bfd3baee3a1/README.md). Access status: original accessible.

Read scope: full README; full `claude-code-config/.claude/hooks/verify-gate.sh` and `.claude/agents/evaluator.md`; LICENSE header. track-read and commit-on-stop were downloaded but not relied on for uninspected implementation details.

Verified: README labels this an unmaintained event demo. verify-gate comments explicitly identify Bash bypass, basename/case-sensitive matching and unrelated evidence unlocking any row. Evaluator metadata admits Bash is not a hard read-only boundary. The example evaluator is prohibited by prose from running the application, so it cannot establish live runtime quality by itself. README itself suggests wrapper-owned contract updates after independent PASS.

Recommendation: ADAPT independent evaluation against original criteria and a named candidate, and supervisor-owned acceptance state. Let evaluators inspect the real target when relevant, with native enforced access bounds or an isolated snapshot. REJECT evidence-read-as-proof, automatic commit-on-stop behavior, and the literal grep/first-line shell loop as durable acceptance. A native goal mechanism can drive work, but its hidden completion checker cannot substitute for explicit allowed-model independent acceptance where the user's roster requires it.

Historical revision: prior fresh-context evaluator principle remains; forced fresh worker every feature does not follow as a requirement for current models. The demo's simplicity is pedagogical and does not prove production crash recovery or sandbox isolation.

Loam target: acceptance ownership and evaluator contracts in both native seed factories. Probe: worker writes all criteria true without a supervisor check receipt; run must remain unaccepted. Read unrelated screenshot before a result claim; no gate unlock occurs. A failed application render must be observed by the evaluator even if static screenshots claim success.

Reuse: Apache-2.0, not MIT. Shell examples use Bash and Python; selected evaluator is Markdown. Prefer new implementation of receipt ownership and evaluation protocol, retaining notices if copying text/code.

Implementation links: [claude-code-config/.claude/hooks/verify-gate.sh](https://github.com/anthropics/cwc-long-running-agents/blob/ad107a974bced5244f74dd283dbf2bfd3baee3a1/claude-code-config/.claude/hooks/verify-gate.sh), [claude-code-config/.claude/agents/evaluator.md](https://github.com/anthropics/cwc-long-running-agents/blob/ad107a974bced5244f74dd283dbf2bfd3baee3a1/claude-code-config/.claude/agents/evaluator.md).

## S10: disler/super-simple-software-factory

Verified source revision: `de31374882e7a4e3e5b7bb9bd09e69dc2f779356`. [Original README at revision](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/README.md). Access status: original accessible.

Read scope: substantive README architecture/phases/envelopes/traces/failure sections; full `.claude/skills/sssf/templates/adws/adw_modules/runner.py`, `gates.py`, `permissions.py`, `agent_cc.py`; targeted quality.py placeholder/command search; LICENSE header. Other downloaded Pi/session files not substantively audited.

Verified: current tree contains real stamped workflow modules. `Run.finish` makes acceptance and successful phase execution jointly determine final status/banner/exit code. `verdict_consistent` rejects approved-with-blockers, approved-with-unmet-requirements and unexplained rejection. `diff_matches_claims` only checks existence of claimed files. permissions.snapshot fingerprints dirty tracked files by added/deleted line counts and untracked files with literal 'untracked'; equal-count content changes evade comparison. It is post-hoc detection and rollback, not isolation. Claude adapter raises NotImplementedError. quality.py test/lint/typecheck/build use echo placeholders that exit zero.

Recommendation: ADAPT one explicit result reducer and consistent review envelopes; known repeatable commands execute directly in supervisor code while native workers retain discretion inside tasks. ADAPT per-seed stamping of complete factory runtime, configuration, tools and recipes. REJECT wholesale dependency, Pi/default roster, existence-only diff gate, numstat permissions and successful placeholder tests. Use actual content/candidate identity, native permission enforcement, and unconfigured checks that fail closed.

Historical revision: `docs/research/loop-repos.md` says the repo ships no code and the runner/gates were all prose. That statement is false for this pinned source. The earlier primary note and review ledger describing implementation are closer to current source. Revisit SQLite rejection: durable independent factories make transactional recovery valuable; choose store based on invariants and deployability rather than an arbitrary JSONL-only preference.

Loam target: packaged seed supervisor modules, default preflight, acceptance reducer and artifact checks. Probe: run a check command that executes successfully but reports failed assertions; run status, process exit and displayed outcome must all fail. Empty/unconfigured checks cannot pass. Two dirty-file edits with the same numstat must still yield different candidate hashes.

Reuse: MIT. Selected modules import internal data_types/tracer/agents and use Python standard library; full implementation requires its native Pi runtime and configuration dependencies, so not a drop-in Codex/Claude factory. Copy only narrow reviewed helpers with notice, or implement equivalent contracts.

Implementation links: [.claude/skills/sssf/templates/adws/adw_modules/runner.py](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/runner.py), [.claude/skills/sssf/templates/adws/adw_modules/gates.py](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/gates.py), [.claude/skills/sssf/templates/adws/adw_modules/permissions.py](https://github.com/disler/super-simple-software-factory/blob/de31374882e7a4e3e5b7bb9bd09e69dc2f779356/.claude/skills/sssf/templates/adws/adw_modules/permissions.py).

## X07: paoloap-py/agent-harness-guide

Verified source revision: `9a05d2c7e7337eca7c1b0de5360c9745810efa1b`. [Original README at revision](https://github.com/paoloap-py/agent-harness-guide/blob/9a05d2c7e7337eca7c1b0de5360c9745810efa1b/README.md). Access status: original accessible.

Read scope: full original README via redirected repository; full `harness.py`, `shared/fake_agent.py`, `layers/03_memory_persistence.py`, `layers/05_context_pipelines.py`; `test_harness.py` 1-80; pyproject and LICENSE header. Original GitHub URL redirects to paolo-perrone/agent-harness. No demo or test was executed.

Verified: FakeAgent emits a deterministic sequence of calls; tests check both guard-on and guard-off expected output. `Denied` is a typed result rather than a generic string interpretation. `Store` calls its dictionaries disk/config but never writes them to disk; reset only clears another in-memory list. `read_only` is a shallow dict/list copy, not immutability. `allowlist` normalizes paths without resolving filesystem symlinks. Distiller counts words and source comments say these are not provider token counts.

Recommendation: ADAPT deterministic fake-native event streams and paired failure/control fixtures for the supervisor. Include real process restart, child identity, receipt corruption and equal-byte-length artifact changes. ADAPT typed refusal states only at the supervisor/host boundary. REJECT Store as durable persistence, read_only as isolation, path normalization as sandbox, and word counts as billing. The context/disk/config distinction is useful vocabulary, but memory-to-policy promotion must remain explicit and evidence-reviewed.

Historical revision: the earlier review correctly said wrappers are not OS isolation; the actual source adds stronger reason to avoid copying its persistence and read-only implementations. Guard-on/off demos establish their toy model, not the real CLI permission boundary.

Loam target: seed factory focused fixture tests plus actual native adapter contract tests, also exercised when rendering a new independent project. Probe: fake native child writes a result then crashes before acknowledgment; restart must adopt/reconcile exactly once. Kill the supervisor process and launch a new one; durable state must survive, which the source Store cannot provide.

Reuse: MIT. FakeAgent uses standard-library dataclasses; package requires Python >=3.8 with no runtime dependencies. This is the most straightforward literal fixture reuse candidate, with attribution, but strengthen tests to inspect actual files/processes rather than only fixed stdout strings.

Implementation links: [harness.py](https://github.com/paoloap-py/agent-harness-guide/blob/9a05d2c7e7337eca7c1b0de5360c9745810efa1b/harness.py), [shared/fake_agent.py](https://github.com/paoloap-py/agent-harness-guide/blob/9a05d2c7e7337eca7c1b0de5360c9745810efa1b/shared/fake_agent.py), [test_harness.py](https://github.com/paoloap-py/agent-harness-guide/blob/9a05d2c7e7337eca7c1b0de5360c9745810efa1b/test_harness.py).

## Cross-source replay and native capability assessment

Additional verified S01 read scope: `loopx/control_plane/turn_driver/driver.py` 164-296; `executor.py` 805-842, 1327-1380, 1400-1465; `turn_journal.ts` 330-545; full `subagent_host_adapter.py`. These files were fetched at the same pinned S01 commit.

Verified: `run_loopx_turn_once` takes an exclusive journal lock and returns an existing terminal result with `host_invoked=False`. But `_host_result_stage` invokes the host when `typed_result` is not recorded. The recovery reducer checks host-session binding when the failed journal contains `host_recovery`; it is not a universal proof that every incomplete native operation can be safely replayed. `_session_plan` compares goal/agent/todo lineage and distinguishes fresh versus resume-if-available. The child adapter table models Codex fresh/forked children and Claude fresh Task only. This is a limited source-specific projection, not proof that all current native capabilities are preserved.

Recommendation: distinguish replaying a committed controller receipt, resuming a native session, rerunning a check, and repeating a worker's external operation. These have different consequences. S01's same-effect local settlement is useful, but cannot guarantee an exactly-once external operation whose result was lost. A stable operation ID, external idempotency support or outcome readback is necessary for automatic recovery across that uncertainty; otherwise retain unknown-outcome and request the specific missing evidence before repeating the operation. Never let a generic transient retry redispatch an entire successful sibling's effect.

Input from the other original-source reviewers: native Workflow replay can reexecute a later successful sibling after an earlier sibling fails; null can represent API failure, cancellation or denial. This specific upstream behavior was supplied by the parent reviewer, not independently reread here. It strengthens the acceptance probe, but is not attributed to LoopX code.

Proposed probe: a native child group contains an earlier failed child and a later successful child that changes an external fixture. Interrupt before acknowledgment, resume the workflow, and assert the operation's external count does not increase unless explicitly authorized. The supervisor must preserve child status distinctions, reconcile the effect, and keep missing/null results unaccepted. Another probe replaces the declared native child capability with an unsupported placeholder; preflight must refuse or explicitly report unsupported capability, not silently remove delegation, skills, tools, model choice or effort. Default native continuation remains compatible with independent fresh reviewers; neither a stale cache nor another repository's old fresh-session policy justifies forcing all worker sessions to reset.

## Self-attack and limits

Verified: the source mechanisms have been inspected, not executed. No benchmark or runtime correctness claim is inferred from source assertions. Downloaded-but-unread files are explicitly excluded from evidence. The most serious discovered holes are retained above: S10 equal-numstat changes/existence-only diff checks, X07 nonpersistent Store/shallow copies/normpath, S04 corrupt spend becoming zero, and S08 noncryptographic/length identity. These are reasons to adapt ideas with stronger invariants, not claims that Loam already contains the same defects.

Likely: a small transactional local store is easier to make restart-correct than loosely coordinated status files, because admission, reservation, result commit and acceptance share state. This is an architectural inference, not a measured benchmark or a requirement to adopt SQLite without implementation review.

Risks: proposed probes were not executed and no framework was installed. Scope was targeted source review, not security audit or full transitive dependency/license audit. Any literal code reuse needs attribution and examination of the complete dependency closure. No blanket claim of enforceable isolation, exactly-once external effects, or empirical model superiority is made. Same-session native recovery also depends on actual host APIs and identity evidence, which must be checked in the adapter implementation phase.
