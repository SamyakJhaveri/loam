# Original-source review: skills, research, review and memory (S43-S56)

Status: design input, not approved implementation. No runtime, install, scanner, model job, automation, commit or deployment was executed. Source archives and selected raw files were downloaded only under `/private/tmp/loam-architecture-design/skills-source-cache/`; downloaded code was never executed. This report is the only design document written by this agent.

Verified: the review ledger and Loam `docs/research/INDEX.md` were read. INDEX's old unused/vet-first/rejected statuses were treated as historical evidence, not decisions governing this review. All assigned original repositories were accessible. GitHub's unauthenticated API rate limit interrupted metadata access for S52-S56; read-only `git ls-remote` and commit-pinned codeload archives resolved access. Reading is deliberately selective, described below. This is not a claim that every README, every source file, every linked paper, or every external license was read fully.

## Access and snapshot identity

| ID | Original repository | Examined commit | Status |
|---|---|---|---|
| S43 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector/tree/1c0eb569a2550172415aaebd83a62ea163cb3c06) | `1c0eb569a2550172415aaebd83a62ea163cb3c06` | Accessible; selected original content read |
| S44 | [anthropics/skills](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624) | `34040c9c568585f6929bedeaad110ad08f079624` | Accessible; selected original content read |
| S45 | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/tree/3097abe2d0d1e83a9023c7a8d054c00aace24990) | `3097abe2d0d1e83a9023c7a8d054c00aace24990` | Accessible; selected original content read |
| S46 | [ZacheryGlass/.claude](https://github.com/ZacheryGlass/.claude/tree/b5a40f790e33cb79501fae7a5097f466ce06dac9) | `b5a40f790e33cb79501fae7a5097f466ce06dac9` | Accessible; selected original content read |
| S47 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278) | `063bee94c3f4df8453406c830b0a7df0f2860278` | Accessible; selected original content read |
| S48 | [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9) | `8da1f030185bdfe8471220585162991eaeb970e9` | Accessible; selected original content read |
| S49 | [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer/tree/94b88b23703bed7df507acae7d6d5876209a0cdf) | `94b88b23703bed7df507acae7d6d5876209a0cdf` | Accessible; selected original content read |
| S50 | [blader/humanizer](https://github.com/blader/humanizer/tree/9862685f575c65a8247f90369951df1b3416e3d6) | `9862685f575c65a8247f90369951df1b3416e3d6` | Accessible; selected original content read |
| S51 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills/tree/91fc74d37e90c879b6a2376e244f4e26fd59cceb) | `91fc74d37e90c879b6a2376e244f4e26fd59cceb` | Accessible; selected original content read |
| S52 | [Imbad0202/academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex/tree/925975e933a20893b81681d925a3404e3b7f73b7) | `925975e933a20893b81681d925a3404e3b7f73b7` | Accessible; selected original content read |
| S53 | [OpenNSWM-Lab/FAROS](https://github.com/OpenNSWM-Lab/FAROS/tree/4e4e96fde842ced39b5bfd805b5666b4ce7cca0e) | `4e4e96fde842ced39b5bfd805b5666b4ce7cca0e` | Accessible; selected original content read |
| S54 | [lishix520/academic-paper-skills](https://github.com/lishix520/academic-paper-skills/tree/c325557646e9418939ccc7b99171b149ad6314f1) | `c325557646e9418939ccc7b99171b149ad6314f1` | Accessible; selected original content read |
| S55 | [Spark-To-Paper-Skills/paperjury](https://github.com/Spark-To-Paper-Skills/paperjury/tree/53c75e86285dc5b38e8d60c6eb0b0adaf4838250) | `53c75e86285dc5b38e8d60c6eb0b0adaf4838250` | Accessible; selected original content read |
| S56 | [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills/tree/77e7c2c1ba06f7d71844873147665437a03aac1b) | `77e7c2c1ba06f7d71844873147665437a03aac1b` | Accessible; selected original content read |

## Exact substantive reading scope

**S43.** README 132-225, 648-735, 763-858 and GitHub overview; models.py 1-259; baseline example 1-38; pyproject.toml 1-72. License identity from source SPDX and project metadata. Scanner implementation beyond finding model not fully read.

**S44.** Root README 1-96; skills/claude-api/SKILL.md 1-116; shared/prompt-audit.md 1-110; skill LICENSE.txt 1-30, 176-202. Language references and remaining prompt-audit groups not read.

**S45.** README 356-457 and repository overview/category inventory; scientific-literature-researcher.md 1-151; architect-reviewer.md 1-65. LICENSE 1-21 complete (MIT); remaining role catalog not read.

**S46.** README 1-104; parallel-phases/references/worktree-protocol.md 1-107; review-gauntlet.md 1-132. Full tree searched for license paths; none found. Parallel-phases entry skill downloaded but not substantively read.

**S47.** README 1-43, 194-239; vercel-optimize/SKILL.md 1-84; vercel-optimize/lib/verify-claim.mjs 1-90. Full tree searched for license paths; none found. README declares MIT. Remaining verifier implementations and discovery builder not read.

**S48.** README 1-62, SKILL.md 1-68, LICENSE 1-21, all complete. Linked phrase/structure/example references not read.

**S49.** README 1-121 and LICENSE 1-17 complete; SKILL.md 1-65, 221-261. Remaining style layers and linked ARMS/blader upstream provenance not independently audited.

**S50.** README opening/usage/pattern overview 1-90 plus displayed full example and release history; SKILL.md 1-73; LICENSE 1-21. Pattern catalog not completely read.

**S51.** README 1-48, 96-155, 280-338; claim_verification_protocol.md 1-55, 228-282; team_collaboration_protocol.md 1-90; harness-retirement-2026-09-model-update.md 1-115; LICENSE 1-24, 137-164, 185-220. Long release history, audit fixtures and full machine validators not read.

**S52.** README 1-76, 221-268, 315-376, 483-515; skill router SKILL.md 268-306 plus targeted native/inquiry contract search; plugin.json 1-45 complete. License identity from README and plugin metadata; LICENSE downloaded and matches S51 bytes but not reread in full. Full runtime implementation not read.

**S53.** README English architecture 264-313 and limitations 394-399; ResearchMemory 1-269 complete; EventLog 1-39 complete; evidence_verifier.py 1-115. Full tree searched for license paths; no actual license file found. Underlying state store and remaining semantic verifier not read.

**S54.** README 1-139 and LICENSE 1-21 complete; strategist/SKILL.md 1-70; strategist/scripts/gap_analysis.py 1-162 plus function inventory. Remaining interactive CLI/report formatting and composer not read.

**S55.** README 147-194, 278-357; references/ledger-schema.md 1-146 complete; scripts/ledger.js 45-180 plus function inventory; review-panel.workflow.js 1-75, 224-292; LICENSE 1-21 complete. Current courtroom workflow family not read; inspected panel explicitly labels itself quick-check.

**S56.** README 1-86, SKILL.md 1-99, LICENSE 1-21 complete; paper-review.md 1-65. Original Peng Sida sources credited by README not independently read.

## Recommendations by concrete unit

### S43: SkillSpector

Verified: source `models.py` gives findings stable identifiers, locations, evidence, immutable source identity/digest, source-aware match fingerprints and serialized occurrences. The baseline example distinguishes exact fingerprints from broad human-authored glob suppressions. README's exit contract explicitly collapses SAFE and CAUTION into success exit zero, and its JSON distinguishes requested/available LLM analysis. The package declares Apache-2.0 and requires Python >=3.12,<3.15 with LangGraph, provider SDKs and YARA among dependencies. Static-only scanning still sends dependency coordinates to OSV; model analysis transmits eligible file content to the configured provider. These are documented behaviors, not newly executed observations.

Recommendation: adapt a versioned external-asset admission adapter, preserving raw reports, source hashes, scanner version, coverage/degradation and explicit waiver rationale. Integrate the pinned scanner as declared factory supporting infrastructure instead of assuming a personal installation. Do not duplicate its scanner in Loam. A completed scan is evidence for admission, not proof of harmless runtime behavior. Never generate an accept-all baseline as routine update policy. Preserve suppressed findings and re-review changed source/scanner identity. Apply the user's approved model/effort policy to any semantic scanning; the upstream cheap-provider defaults do not transfer.

Dependencies: complete asset bundle inventory, pinned scanner installation/distribution plan, licensed notices, egress policy, declared provider binding and failure-state parser.

Probe: use benign, malicious, modified previously-waived, unreadable and resource-limit fixtures. `skillspector scan <fixture> --no-llm --format json` is an upstream documented command, not executed here. Verify CAUTION differs from SAFE, unavailable requested analysis is visible, changed fingerprints revoke acceptance, and incomplete scans cannot admit an asset.

### S44: Anthropic claude-api prompt audit

Verified: `shared/prompt-audit.md` asks for both located findings and a proposed diff, ties changes to target-model behavior and provenance, preserves author-specific context, and permits an empty result. The enclosing SKILL has broad Claude API triggers and an upstream default model outside Samyak's permitted set; it also steers implementation toward SDK surfaces. The particular skill LICENSE.txt identifies Apache-2.0 and Anthropic copyright, while the root repo warns its document skills have different licensing.

Recommendation: adapt the audit unit as driver-maintenance work. An admitted audit names the user-selected driver, target surfaces, official source revision, motivating observed failure and evaluation cases. Produce a reviewable change plus rollback evidence. Do not install its broad API-routing/default-model policy as Loam-wide instructions, and do not interpret generic API guidance as a reason to replace native workers. Model/effort changes remain user-controlled.

Dependencies: prompt/skill/hook/workflow inventory, source provenance, native-specific official guidance, preserved acceptance contracts, comparison runs authorized later.

Probe: give the audit a known obsolete workaround, a currently needed tool contract and a clean prompt. It should propose only the justified change, preserve the contract and leave the clean surface unchanged. Verify no model default changes. These are future behavioral tests, not observed performance.

### S45: VoltAgent subagent catalog

Verified: the scientific-literature researcher names a specific BGPT MCP server and `model: sonnet`; its sample completion message contains illustrative counts. The architect-reviewer currently declares `model: inherit` but includes Write/Edit/Bash despite being described as a reviewer. The README claims generic read-only reviewer tools and automatic cost-oriented routing. Repository metadata identifies MIT.

Recommendation: selectively adapt role questions, especially method comparison and contradictory evidence. Each Loam role needs a real bounded input/output/evidence contract, verified available tools and approved model selection. Replace the fictive context-manager handshake with actual supervisor inputs. Do not inherit universal BGPT dependence, catalog-wide installation, embedded sample statistics, or the premise that a specialist name establishes competence.

Dependencies: project-selected research connectors (Consensus remains preferred when relevant/available), role capability manifest and native permission mapping. Preserve original notices before copying MIT text.

Probe: unavailable BGPT must not produce an imagined search result; reviewer role must not edit candidate code; a deliberately contradictory source must remain visible after synthesis. Actual separate contexts, not role headings, establish the intended independent work arrangement.

### S46: ZacheryGlass parallel phases

Verified: the read protocols record task-to-worktree dispatch, isolate read-only reviews from task writes, give reviewers complete task briefs, and merge through an integration branch after tests. They also use personal-state paths, hardcoded model choices, force cleanup, and a test-through-tee pseudocode example without an explicit pipefail guarantee; a missing test command may still merge. No license/copying/notice path was found in the full repository tree.

Recommendation: use task ownership, separate integration and review-context design as inspiration. Do not copy source absent clarified reuse terms. Build Loam's own receipt-bound integration/recovery semantics. Do not inherit forced worktree cleanup or automatic acceptance of no validation. Source protocols are illustrative instructions, not a crash-safe supervisor implementation.

Dependencies: project-owned task identities, immutable base/candidate commits, a validation owner, retained worktrees and durable recovery records.

Probe: let task branches overlap, move the target branch during a phase, fail the command feeding a tee, and interrupt before merge. Confirm no accepted outcome or worktree deletion occurs without the bound validation result. Test conflict handling separately from ordinary independent work.

### S47: Vercel agent skills

Verified: the optimize skill makes recommendations conditional on production signals, versioned documentation and supported frameworks. `verifyClaim` dispatches concrete check types, reports unknown kinds as unverifiable, and has a separate check against contradictions with project configuration. The README describes immutable per-skill discovery artifacts. Its README declares MIT, but no license file was found in the examined tree.

Recommendation: adapt typed evidence checks and version/applicability checks as extension contracts. Candidate-specific checks belong in optional project/domain packs. Do not require Vercel account access, metrics or framework gates for generic Loam research. Before vendoring concrete code, resolve the missing standalone license/notice packaging and inspect each helper dependency; current recommendation is the interface pattern, not a complete port.

Dependencies: evidence-check registry with explicit unsupported/error outcomes, runtime version evidence, project facts and source-bound citations. Vercel-specific pack additionally needs its documented authenticated CLI, linked project, Node and observability capability.

Probe: unknown claim kind remains unverifiable; wrong framework-version citation fails; recommending an already-enabled setting is caught; a file-existence check cannot establish a performance claim. Inspect the discovery builder before choosing its packaging mechanism.

### S48: Stop Slop

Verified: this MIT skill supplies concise prose-pattern rules and a subjective score threshold. It universally removes adverbs/passive constructions and makes stylistic choices such as preferring two items over three.

Recommendation: adapt selected readability checks as optional project voice guidance. Avoid chaining several overlapping humanizers into every factory result. Do not elevate subjective style scores to acceptance gates or remove scientific hedging, necessary passive voice or parallel facts merely to satisfy a prose pattern.

Dependencies: user/project voice policy and semantic preservation checks; distribute the complete referenced skill folder if adopted, not SKILL.md alone.

Probe: compare prose containing a necessary uncertainty qualifier, a valid passive construction, code/URLs and genuine parallel facts. Content and technical syntax must survive. Cleaner style is a reviewer judgment, not scientific validation.

### S49: Academic Humanizer

Verified: the skill distinguishes papers from proposals, preserves results/citations and asks for an audit/change report. It explicitly permits calibrated scholarly language and uses evidence-to-claim and evidence-to-feasibility reasoning. Its LICENSE is labeled MIT and credits blader/humanizer plus ARMS influence. The text includes an unusually rigid same-paragraph-count rewrite requirement.

Recommendation: use as an academic writing extension after evidence collection. Preserve the genre-specific claim-strength checks; allow justified structural revision rather than copying paragraph-count rigidity. Audit source attribution and the shortened license text before concrete vendoring. Do not treat a rewrite's assertion that numbers survived as a deterministic conservation check.

Dependencies: source manuscript, exact references/results, optional author samples, current venue rules where consequential, attributed supporting assets.

Probe: numeric values, citations, equations and uncertainty survive a rewrite; unsupported strengthening becomes a visible evidence gap. A proposal's ambition statement should not be mistaken for an established experimental result.

### S50: Humanizer

Verified: the inspected MIT skill treats supplied text as editing material, protects code/data/frontmatter/link targets in file mode, supports project voice and includes a factual-conservation pass. The README credits Wikipedia's signs-of-AI-writing list.

Recommendation: prefer one configurable editorial pass over stacking S48/S49/S50. Adapt its separation between file mode and embedded output mode and its preservation boundary. Use academic-specific guidance when needed. Upstream explanations of model psychology are not evaluated evidence for Loam architecture.

Dependencies: exact original draft, project voice, preservation checks; retain author and attribution provenance if copying.

Probe: embed an instruction-looking passage in the draft and verify it remains content rather than execution authority; preserve code, link targets, rankings and simultaneous-event claims while editing surrounding prose.

### S51: Academic Research Skills (Claude)

Verified: the inspected contracts distinguish registered claims from unknown semantic extraction coverage. Claim registry entries bind exact source spans and draft hash; deterministic coverage checks cover only bounded lexical classes. Manuscript/declared-process checks explicitly do not certify real experiment execution. The harness-retirement audit preserves corrections to its own earlier model/effort conclusions. Its team-collaboration protocol concerns human roles, not native agent isolation. LICENSE is CC BY-NC 4.0 and explicitly limits licensed sharing/adaptation to noncommercial purposes.

Recommendation: independently design Loam evidence records using the useful distinctions: registered population, read scope, source bytes, uncertainty, author decisions and correction history. Do not wholesale vendor this noncommercial suite into an unrestricted every-seed payload without a separately resolved permission/distribution plan. Do not import citation quotas, concession scores, hidden dialogue manipulation or paper-specific approval stages as universal research method. Its published correction history is valuable evidence that official model reading must be paired with interface-specific probes.

Dependencies: Loam-owned shared schemas, selected domain methods, source retrieval, explicit evidence population and driver-specific tests. Further source work should inspect inquiry-branch machine code and evaluation fixtures before adopting durability techniques.

Probe: a citation-free qualitative claim omitted by lexical extraction remains an acknowledged coverage limit; a stale draft span is rejected; a source-supported statement still does not certify its underlying experiment; legitimate contrary evidence can revise a conclusion without arbitrary concession thresholds.

### S52: ARS-Codex

Verified: this distribution independently versions its adapter, records upstream source commits, separates active native entrypoints from inactive vendored Claude assets and exposes a manifest of intentionally inactive scripts. The normal router uses inline role prompts; an optional full-runtime profile has separate agents/routes/hooks. The router says separate reviewer sections preserve independence, which does not provide separate context isolation. License is CC BY-NC 4.0.

Recommendation: adapt the architecture of a shared content payload plus explicit native adapter/provenance manifest. Do not inherit weaker Codex operational behavior as parity. Required Loam research teams must actually delegate independently on both native harnesses; optional native capabilities can differ while the shared result contract stays consistent. Do not copy the noncommercial content wholesale. Dead vendored scripts should be excluded from Loam's runnable payload unless there is a specific traceability need.

Dependencies: complete source/adapter manifest, capability matrix, native entrypoint tests, per-asset activation state and approved descendant settings.

Probe: every required role resolves on both harnesses with the intended shared source hash; retired Claude hooks cannot activate in Codex; independent reports cannot access peer reports before critique; a missing capability cannot silently become inline imitation.

### S53: FAROS

Verified: the README separates workflows/capabilities/profiles/providers and explicitly calls the project a research prototype. `ResearchMemory` is mutable run-scoped data, summaries, scopes and archives; compaction trims history and may remove keys. `EventLog` delegates append operations to an uninspected state store, so this wrapper alone proves no durability. The verifier checks claim/evidence links, but its general branch upgrades evidence support based on an attached metric/experiment-report artifact type, independently of stronger specialized checks. No actual license file was found in the tree.

Recommendation: take scoped retrieval, typed cross-stage handoff and traceable experiment identities as inspiration. Keep working memory separate from immutable evidence and reviewed reusable lessons. Do not treat an evidence edge or artifact type as substantive support. Do not port the application/runtime or copy source before permission/provenance is resolved.

Dependencies: project-owned evidence store, append/recovery semantics, declared domain contract and independently checked support relations. Native CLI worker interfaces should replace any API-specific agent runtime if independently implementing these ideas.

Probe: compact/reload memory without losing cited original evidence; retain superseded and negative conclusions; attach an irrelevant experiment artifact and ensure no accepted supported claim results. Inspect state-store writes before borrowing any recovery promise.

### S54: Academic Paper Skills

Verified: the strategist defines gap types and source/quote/context fields. `gap_analysis.py` checks field presence, citation/quote nonemptiness and counts, then calls a portfolio satisfactory based on gap/evidence quantities and self-declared significance. It does not retrieve or validate sources. MIT license text was read.

Recommendation: adapt the gap-candidate template as an optional inquiry aid. Replace its quality label with accurate structural validation and add bounded source-grounding checks. Do not require every inquiry to discover several gaps or meet a subjective outline score before useful work can continue.

Dependencies: project/domain inquiry method and real source-location records. Keep paper composition separate from determining whether an idea is true or useful.

Probe: a structurally complete fabricated-citation fixture must not be called evidence-valid; a single well-supported consequential gap must remain a viable inquiry. Proposed future tests, not newly executed results.

### S55: PaperJury

Verified: the ledger separates an issue's importance, type, disposition, close criterion and lifecycle. It derives Markdown from JSON and gives ledger writes to the orchestrator. The inspected ledger `load()` converts missing/empty files or missing issue arrays into empty state, and `save()` performs direct writes; this is not a sufficient durable supervisor store. The README and schema permit a round gate to pass while author-required issues remain active. The quick-check workflow uses isolated prompts and majority refutation, but explicitly identifies itself as a separate path from the default courtroom engine. MIT license text was read.

Recommendation: adapt evidence-anchored finding triage, required close criteria, retained dismissal reasons and a visible human queue. Separate 'autonomous work finished' from 'ticket accepted'. Replace majority-as-truth with reasoned evidence adjudication and preserved dissent. Use Loam's own validated persistence, not missing-state-as-empty defaults or direct writes. Further code inspection is required before any selected port of the default courtroom mechanisms.

Dependencies: issue schema, evidence anchors, shared actor authority, candidate snapshot identity, durable state and project steering decisions.

Probe: crash during ledger save, corrupt/missing ledger, evidence-backed minority objection, incomplete reviewer response, unresolved human-required major issue. None may silently yield ticket acceptance. Reopening a dismissed issue must preserve its earlier reason and new evidence.

### S56: Research Paper Writing Skills

Verified: the skill offers reverse outlining, on-demand section references and a claim-evidence map. Its review guidance is explicitly oriented to ML/CV/NLP and prioritizes comparative performance/ablations. README gives substantial credit to Peng Sida's open notes, while its own license is MIT.

Recommendation: adapt the portable claim-to-evidence mapping and load-on-demand writing references as a selected paper-writing extension. Do not turn leaderboard gains, experimental superiority or a fixed five-dimension self-review into universal inquiry requirements. Before copying substantial derivative material, verify the credited original source's terms and preserve provenance. That upstream attribution check remains open.

Dependencies: project paper genre, original source terms, actual result artifacts and current publication requirements when needed.

Probe: apply reverse outlining to a systems explanation and preserve its argument; a negative-result or conceptual paper must not be rejected solely for lacking higher benchmark performance. Unsupported headline claims must be reduced or linked to a specific open evidence task.

## Synthesis for Loam

Recommendation: the shared factory should ship the capability to discover, inspect, admit, invoke and update project-selected assets, with local source/adapter provenance and no personal-path dependency. Every seed needs that infrastructure. It need not preload every domain method or paper-writing suite. Required generic inquiry, independent critique, decision and evidence contracts must be complete locally.

Recommendation: separate reusable units into (a) operational contracts such as source identity, output status and actor authority; (b) optional methods such as literature review and paper revision; and (c) editorial preferences. Domain-specific quantitative validation remains a project-selected method. The useful ideas here support bounded source evidence, independent critique, explicit unresolved work and reversible driver adaptation. None warrants replacing Claude Code/Codex with these repositories' full orchestration runtimes.

Strongest gaps discovered by source inspection: scanner success is not SAFE; JSON file presence is not durable state; attached evidence is not semantic support; serial role sections are not independent agents; number-of-citations checks are not evidence validity; style scores are not research quality. These distinctions should enter the implementation acceptance criteria.

## Validation and limits

Verified: access and snapshot identities were produced by GitHub trees or read-only Git remote queries. Scope entries above distinguish read text from merely downloaded assets. No upstream test suite or Loam runtime acceptance test was executed. Future probes above are test designs; any command shown as an upstream command was read in its source and was not run.

Self-attack: Do not infer compatible source reuse from a README badge alone. Do not count downloaded files as read. Do not extrapolate wrapper code to storage guarantees. Do not turn heuristics or limited scope checks into certification. Do not import upstream model defaults, personal setup or autonomous permissions. These risks are reflected in the individual recommendations and remaining-source-work notes.
