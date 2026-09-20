# Current-main evidence and design validation

Evidence time: 2026-09-14T00:12:37Z, from date -u.
Repository: /Users/samyakjhaveri/Desktop/loam.
Original review: /Users/samyakjhaveri/Documents/Codex/2026-09-11/create-an-image-of/outputs/architecture-review/.

## Access and baseline

Verified: actual reads succeeded for start-architecture-session.md, README.md, loam-research-and-factory-review.md, comment-responses.md, revision-evidence.md, code-evidence.md, source-ledger.md and validation.md. The actual report filename has no backslash before .md. At that earlier checkpoint the PDF was not newly inspected. The subsequent complete-folder grounding pass inspected every rendered PDF page, the architecture image and the JSON ledger; see grounding-record.md for full coverage and artifact hashes.

Verified: git status --short --branch, git branch --show-current, git rev-parse HEAD/main and git log main --oneline -10 identified clean main at d627bb2755ad49865f798bcb095800ddd2ad1ced. Read-only git ls-remote origin refs/heads/main returned the same commit. Historical baseline: eed83d179a5f9423eeee209b994edb9da4d6c444. No fetch or branch update was needed.

Verified: root AGENTS.md was read; ancestor checks for both locations found no additional AGENTS.md. Read asset-layer, factory architecture/contract, seed harness/worker docs and relevant code/config/skills. Current request/handoff supersede conflicting historical proposals.

Verified: git diff --name-only eed83d179a5f9423eeee209b994edb9da4d6c444 main -- seed copier.yml returned no paths. Baseline-to-main diff showed supervisor, account helper, scheduler, prompts, plugin metadata and documentation changes.

Write limitation: original review folder is outside session writable roots; approval policy is never. The file-edit tool also rejected temporary-path writes as outside the project. Shell writes to the explicitly permitted /private/tmp root supply the fallback. Files staged in /private/tmp/loam-architecture-design are reviewable but do not satisfy permanent placement in the original review folder.

## Current source evidence

| ID | Verified source | Finding |
|---|---|---|
| C1 | [copier.yml:2](/Users/samyakjhaveri/Desktop/loam/copier.yml:2), git ls-tree -r --name-only main seed, baseline diff | Only seed renders; full factory absent; seed unchanged. |
| C2 | [bin/factory:197](/Users/samyakjhaveri/Desktop/loam/bin/factory:197), [220](/Users/samyakjhaveri/Desktop/loam/bin/factory:220), [467](/Users/samyakjhaveri/Desktop/loam/bin/factory:467), [508](/Users/samyakjhaveri/Desktop/loam/bin/factory:508), [723](/Users/samyakjhaveri/Desktop/loam/bin/factory:723) | Cache grader/skill resolution, unshipped prose policy, skills outside frozen set. |
| C3 | [bin/factory:1135](/Users/samyakjhaveri/Desktop/loam/bin/factory:1135), [1031](/Users/samyakjhaveri/Desktop/loam/bin/factory:1031), [1005](/Users/samyakjhaveri/Desktop/loam/bin/factory:1005), [1151](/Users/samyakjhaveri/Desktop/loam/bin/factory:1151) | Check exit ignored, review parsing defaults no blockers, block-once review and cap reach PR. Current source, not fresh runtime reproduction. |
| C4 | [bin/factory:374](/Users/samyakjhaveri/Desktop/loam/bin/factory:374), [1166](/Users/samyakjhaveri/Desktop/loam/bin/factory:1166), [1195](/Users/samyakjhaveri/Desktop/loam/bin/factory:1195), [1237](/Users/samyakjhaveri/Desktop/loam/bin/factory:1237), [1343](/Users/samyakjhaveri/Desktop/loam/bin/factory:1343), [bin/claude-account:43](/Users/samyakjhaveri/Desktop/loam/bin/claude-account:43) | Global state/ticket namespace, filename resume, broad timer removal, ticket-only session names, global account mutation. Likely: project interference; not reproduced. |
| C5 | [bin/factory:381](/Users/samyakjhaveri/Desktop/loam/bin/factory:381), [815](/Users/samyakjhaveri/Desktop/loam/bin/factory:815), [843](/Users/samyakjhaveri/Desktop/loam/bin/factory:843), [1045](/Users/samyakjhaveri/Desktop/loam/bin/factory:1045), [seed/.codex/config.toml](/Users/samyakjhaveri/Desktop/loam/seed/.codex/config.toml) | Opus worker/Fable grading defaults with environment overrides; Codex native settings rather than ledger label; unconditional graders; no seed model/effort pin. |
| C6 | [ARCHITECTURE.md:48](/Users/samyakjhaveri/Desktop/loam/docs/factory/ARCHITECTURE.md:48), [CONTRACT.md:24](/Users/samyakjhaveri/Desktop/loam/docs/factory/CONTRACT.md:24), [brief:42](/Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md:42) | Issue authority, baseline-failing behavior checks, figure-out forces Track C. |
| C7 | [catchup:16](/Users/samyakjhaveri/Desktop/loam/seed/.agents/skills/catchup/SKILL.md:16), [surprise-me](/Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/sam-cc-setup/skills/surprise-me/SKILL.md), [HARNESS.md](/Users/samyakjhaveri/Desktop/loam/seed/docs/HARNESS.md) | Claude private memory lookup, plugin-layer creativity, documented sandbox/test integrity limits. |

Distribution has independent render-configuration and tracked-inventory evidence. Completion has current branch inspection and comparison with historical isolated observations. Historical reproductions are not fresh tests. No factory worker or grader was invoked.

## Targeted current external sources

| ID | Source/read scope | Design consequence and limits |
|---|---|---|
| N1 | [Codex noninteractive](https://learn.chatgpt.com/docs/non-interactive-mode), official body including events, schema and resume; installed codex --version, exec --help, app-server --help | CLI reported 0.153.4. Supports proposed staged adapter. No live config/permission certification. |
| N2 | [Codex app-server](https://learn.chatgpt.com/docs/app-server), steering/interruption/transport/experimental sections | Live steering documented; command experimental; prototype before reliance. |
| N3 | [Claude programmatic use](https://code.claude.com/docs/en/headless), output/resume/config/bare/cancellation sections | Native scripted path exists; bare removes useful context/subscription access; actual profile needs testing. |
| N4 | [Claude teams](https://code.claude.com/docs/en/agent-teams), enablement and noninteractive limitation | Headless sessions use subagents, not interactive teammates. |
| N5 | [Claude goals](https://code.claude.com/docs/en/goal), evaluation/model/tool limits | Auxiliary policy requires audit; conversation verdict is not executed checking. |
| N6 | [Multi-LLM Debate: Framework, Principals, and Interventions](https://proceedings.nips.cc/paper_files/paper/2024/file/32e07a110c6c6acf1afbf2bf82b614ad-Paper-Conference.pdf) | Agent used selected Consensus search/fetch, then original abstract/selected paper sections. Shared misconceptions motivate preserving independent findings; no current-model/Loam outcome claim. |

Verified: Consensus tools were discovered and used by the research agent, with fetch before reliance. This does not establish that the connector/subscription exists in a recipient project's CLI. Ship explicit discovery readiness and alternative paths; detailed routing remains deferred. No other source-ledger entry is silently revalidated. Historical chat attachments, inaccessible source bodies and external benchmark claims retain prior limitations.

## Task list and checks

1. Read sources and pin main. Check: successful reads and matching rev-parse/ls-remote commit above. Completed.
2. Audit distribution/completion against main. Check: tracked seed inventory, baseline diff and current source branches. Completed.
3. Write separate living design/decision/evidence files. Check: file reads, internal-link and required-section validation. Expected: complete records outside original report and runtime source. Completed; final post-review check recorded below.
4. Cross-critique and final preservation check. Check: independent critique of documents; git status --porcelain=v1 and rev-parse main. Expected: empty repository status and unchanged commit. Completed; final post-review check recorded below.

## Risks and not done

- Not done: permanent save in original review folder, blocked by session writable roots. Temporary fallback supplied.
- Not done: runtime prototypes, bin/check, live native evaluations, generated-project execution, installs, scheduling, commits/push/deployment. Initial phase excludes them; no tests-pass claim.
- Assumption: single execution host per instance and staged steering suit the initial common adapter; discuss before implementation.
- Not verified: auxiliary model visibility, full sandbox enforcement, connector portability, snapshot-update compatibility, memory quality.
- Pending: project-file versus GitHub authority; recommendation is not accepted policy.

## Document self-attack and fresh review

Verified: a fresh-context reviewer inspected the staged design and handoff and spot-checked current completion branches. It found missing isolation for candidate code launched by evaluation and missing explicit model-specific setup adaptation/evaluation/rollback. Both were added to the proposal and decision record.

Self-attack questions and resolution:
- What input breaks this? A test importing malicious or faulty candidate code could mutate state if run with supervisor authority. Fixed the design boundary and added a proposed evaluation-tampering fixture.
- Which path was not checked? Real native resume/auth/auxiliary models and external jobs were not run. They remain explicit prototype requirements, not guarantees.
- What is unexercised? All proposed runtime behavior. Document checks only validate artifact structure and traceability.
- Which claim lacks evidence? Performance/security/portability benefits are recommendations or test targets. Temporary staging is not claimed to be permanent review-folder placement.

Completeness mapping: source access and baseline are above; existing/proposed behavior, seed delivery, idea routing, component interaction, alternatives and probes are in living-design.md; settled/pending choices and cross-critique are in decisions.md. Permanent target-folder placement is explicitly not done. No runtime work or outward action occurred.

Final verification: artifact validation exited 0 and printed "Artifact check: PASSED (file structure, local links, required concepts; not runtime validation)". Git status was empty, main remained d627bb2755ad49865f798bcb095800ddd2ad1ced, and both working-tree and staged diffs exited 0. A narrow second review confirmed the corrections resolve its findings and found no remaining concrete gap in those corrections. This is document coverage, not runtime enforcement or profile quality.

## Subsequent complete-folder grounding

See [grounding-record.md](grounding-record.md) for the recursive inventory, cumulative substantive reading, independent source audits, cross-critique and current limits. No runtime tests or native workers were run in that grounding pass.

## Original-reference integration validation

Verified: all source reports were read by the lead and integrated into source-informed-design.md, loop-design.md and memory-design.md. The reference-reading.md coverage map includes every original ledger ID and the supplemental direct URLs. Independent inventory review found no missing literal direct URLs from the repository research INDEX and output source registers. Historical Git objects were available; changed-file diffs were inspected against current main. Exact selected/partial/blocked scopes are retained, including moving-branch source reads that require pins before copying.

Verified: the coverage validator exited 0 and printed "Coverage check: PASSED (84 ledger entries mapped to existing scoped reports)". The artifact validator exited 0 and printed "Artifact check: PASSED (coverage, local links and required design clauses; not runtime validation)". Git status showed clean main, working-tree and staged diff commands both exited 0, and HEAD/main remained d627bb2755ad49865f798bcb095800ddd2ad1ced.

Verified: independent design cross-critique identified native replay/null coverage, goal accounting, automatic native plan approval, model-policy runtime handling and intended-versus-observed context delivery gaps. The integrated clauses address them explicitly. This is design review, not proof of runtime behavior.

Self-attack: missing originals retain blocked status; source inspection is not empirical reproduction; every-seed capability availability is distinct from optional activation; context delivery is distinct from source inspection; a known policy violation prevents continued dispatch and acceptance. Source claims with incomplete observability remain limited. Permanent placement in the original review folder remains blocked by the active write policy; the separate temporary design documents are the delivered fallback.

## Accepted storage and record-contract step

Verified: the user explicitly selected SQLite plus artifact files and agreed with the preceding storage recommendations. decisions.md now records D-STORE, D-INSTANCE, D-DURABLE and D-STATE-UPDATE as accepted direction. The new records-and-transitions.md remains a detailed proposal. Runtime selection does not block this work; implementation remains deferred under the earlier instruction.

Verified: current bin/factory review/main-loop source was reread. Independent actual-draft review sharpened queue-time ownership, acceptance coverage, named steering barriers and evidence invalidation. The document validator returned "Records design check: PASSED (accepted decisions, links, transition coverage and review repairs; no runtime tests)". Staged and unstaged diffs exited 0; repository remained clean main d627bb2755ad49865f798bcb095800ddd2ad1ced. No runtime test or native worker was invoked.

Self-attack: budget scopes survive revisions; cancelled producers cannot accept late output; recovery adoption retains original identity; new required assignments invalidate stale completion coverage; each steering barrier resolves independently; evidence loss blocks dependent current certification while preserving history. Unknown native execution, actual persistence and permission enforcement remain later validation obligations. Review-folder write placement remains unavailable under the active permission profile; separate temporary records are the delivered fallback.

## Native adapter and research-engineering design step

Verified: the user endorsed the record/transition direction and emphasized original-source grounding plus engineering judgment. decisions.md records that authority separately from the new native transport recommendation. Both provider evidence reports were read by the lead and integrated into native-adapter-design.md. Current main remained d627bb2755ad49865f798bcb095800ddd2ad1ced, with clean status and staged/unstaged diff exit 0.

Verified: independent investigation inspected Codex help/offline generated schemas and official documentation, and Claude original documentation plus published SDK type declarations. No provider server, model job or live prototype ran. Exact read scopes and blocked HTML recovery are in native-codex-evidence.md and native-claude-evidence.md. Source inspection establishes interfaces, not execution guarantees.

Verified: independent correctness critique found execution-triggering input authorization, reviewer conversation independence and continuation profile revalidation gaps. The draft now addresses each; the bounded second review confirmed all findings resolved. The document validator exited 0 and printed "Native design check: PASSED (source links, accepted records, provider evidence, research flow and critique repairs; no runtime tests)".

Self-attack: raw queue receipts cannot establish application or quiescence; configured models cannot certify every hidden helper; strict parsing cannot establish profile isolation; schema-conforming reports cannot establish scientific validity; session continuity cannot substitute for independent review. These remain explicit design constraints and later probe obligations. The full adapters and work methods must ship in every seed, with original intent and inquiry outcomes preserved.

Not done: permanent placement in the original review folder, because the active filesystem policy permits reads there but not writes. The living documents remain in /private/tmp/loam-architecture-design/. Runtime implementation, installation and native probes remain deferred by the user's instruction.

## Expanded cookbook and native-workflow audit completion

Verified: current main remains d627bb2755ad49865f798bcb095800ddd2ad1ced. Final git status shows clean main; both staged and unstaged diff checks exited 0. The independent rg URL count returned 65, matching the structured INDEX inventory. All direct INDEX URLs have scoped evidence/disposition.

Verified: the Claude catalog inventory contains 95 recipes. Its 36 delegated rows were joined to final actual read scopes/dispositions, not left as assignments. The SDK owner read all 10 SDK notebooks among its 23 full selected notebooks; the patterns report records complete and selected source cells separately, including its expanded context/tool/memory supplement. The OpenAI audit reads all 8 Codex topic originals, all 16 Codex-named textual sources and 38 selected cookbook textual sources, with the broader 95-candidate metadata inventory explicitly distinguished. Native Python SDK source has a separate repository pin and selected read scope. No whole-repository, every-dependency, image/video or stored-output full-read claim is made.

Verified: the lead read the completed source reports and supplements, reconciled their placement alternatives and integrated them into cookbook-integration-design.md plus cookbook-practice-registry.md/json. The registry has 32 practice dispositions, each with source evidence, implementation owner, native mapping, seed distribution and a proposed future acceptance command/case. cookbook-current-code-map.md binds proposed changes to current Loam code. This completes the requested source-to-design layer; memory implementation remains the next design topic.

Verified: independent actual-draft critique corrected dynamic child admission/identity, interactive team guarantees and authenticated input, explicit fresh-store setup, redacted consultation semantics and changed-method Workflow successor identity. Bounded follow-up review confirmed the repairs. The final document validator exited 0 and printed: "Cookbook integration check: PASSED (source inventories, selected-source hashes, practice coverage, links and critique repairs; no runtime tests)".

Self-attack: source catalog inventory can hide unread bodies, so dispositions preserve full/selected/metadata/deferred status and delegated rows are resolved. API-only examples were evaluated for useful methods rather than automatically dismissed. Native SDK and app-server are separate client/protocol choices; source-backed interface gaps justify the direct client without rebuilding the model loop. Proposed tests are not passing runtime tests. Source claims are static inspections, not reproduced outcome/performance evidence.

Completeness mapping: requested index and new catalog roots -> source inventories/reports; subagent readings -> independent cohort reports; advisor/subagents/teams/dynamic/long-horizon/adversarial and adjacent practices -> registry; concrete Loam and every-seed implementation -> integration design/current-code map; finalization and cross-critique -> reviewed baseline and this record. Not done: permanent writes to the original review folder, because the active filesystem profile denies that write location. Runtime implementation, installs, automation, native model probes, commits/push/deploy remain deferred and were not performed.
