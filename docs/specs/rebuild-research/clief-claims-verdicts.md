# Clief claims: verdicts

**Checked:** 2026-08-31 PDT (all source access dates 2026-08-31 unless noted).
**Inputs:** `soil/loam-rebuild-checkpoint/normalized-claims.jsonl` (928 records), `docs/specs/cliefnotes-wisdom.md`, the Clief corpus (session-local `$CLIEF_CORPUS_ROOT`, 888 files), current code.claude.com/docs, current Anthropic engineering and Claude blog posts, and the primary literature read in full text.
**Method:** `docs/specs/rebuild-research/clief-claims-validation-method.md`, executed by a 7-agent read-only research team (corpus auditor, Claude Code docs, Anthropic practice, academic literature with a full-PDF deep-read, Loam mapper, dormant-assets hunter, adversary), synthesized by one lead editor.
**Decisions:** Samyak ruled on D1-D5 on 2026-08-31 (recorded below).

## Coverage statement (command-produced)

- 928 normalized records; 928 unique `norm_id`s; zero duplicates.
- 1,270 raw IDs; 1,270 unique; every raw ID in exactly one normalized record.
- 104 unique cited corpus pages; all 104 exist. Zero missing.
- Family partition: deterministic recipe over (theme, subtheme) with six oversized buckets split by ordered topic match; 68 families; all 928 IDs assigned; zero hand assignments.
- Known gap: 48 normalized records (83 raw claims) grade `linked` on assets the audit never opened. They stay marked incomplete.

## Verdict matrix (theme level)

Verdicts: `supported`, `partially supported`, `unsupported`, `conflicting`, `time-sensitive`.
Evidence classes: F = feature exists, M = mechanism plausible, O = measured outcome.

| # | Family (n) | Verdict | Key evidence | Confidence |
|---|---|---|---|---|
| 1a | Context routing / progressive disclosure (~140) | partially supported | F real (memory docs). O: no significant success gain, +20-23% cost (Gloaguen arXiv 2602.11988); efficiency proven, correctness not | high |
| 1b | Folder/file numeric thresholds | unsupported | Affirmative null, BF10 0.05-0.10 (McMillan arXiv 2605.10039) | high |
| 1c | Staged pipelines / filesystem-as-architecture (~50) | partially supported | M only; author experience; no outcome study | medium |
| 2a | CLAUDE.md as short router (62) | conflicting + partially supported | Source contradicts itself 3x on budget (15 / 30-50 / unfittable content mandates); docs say 200 as rule of thumb; human-written beats LLM-generated +7% (p=.038) | high |
| 3 | Skills (44) | supported (revised up) | F strong (docs). O: +28.2 instruction-following points on Opus 4.8, ~38k trajectories (arXiv 2606.17819, vendor-adjacent). Procedural skills, not descriptive prose | high on F, medium on O |
| 4 | Hooks (6) | supported (narrow) | Docs verbatim: enforcement layer; trigger guaranteed, outcome not. Corpus itself nearly silent on hooks | high on F/M |
| 5a | Subagent context isolation | supported | Docs + first-party reports | medium-high |
| 5b | Multi-agent parallel coding | partially supported, leaning against | Claude Code Agent Teams scored below a sequential baseline on both Co-Coder benchmarks (arXiv 2606.00953); dependency-graph partitioning is the one positive; coordinated teams beat compute-matched independent runs (arXiv 2607.28430) | medium |
| 5c | Verifier must not be author (N-0705) | partially supported | Holds for subjective grading; not for deterministic self-checks; no head-to-head study; LLM review precision 3.6-5.1% (CR-Bench arXiv 2603.11078) | medium |
| 6 | Memory / durable handoffs (34) | partially supported | Handoffs cut tokens 42-63%; raw trace beats structured notes on solve rate (arXiv 2606.02875); stale-handoff harm untested; native auto-memory supersedes hand-rolled formats | medium |
| 7a | Plan before multi-file work | supported | 21,120 trajectories (arXiv 2604.12147) + CodePlan 5/6 vs 0/6 | medium-high |
| 7b | Universal PRD / plan-always | unsupported | Docs: skip the plan for one-sentence diffs; an incomplete or reordered plan hurts more than none | high |
| 7c | Verification gates, hidden fixtures, end-state grading | supported | SpecBench holdout gap (arXiv 2605.21384); ImpossibleBench method; the corpus's only demo-dominant pages practice exactly this | high |
| 8 | Prompting (69) | partially supported | Specific context and output shape are testable; no universal schema; hidden step-by-step reasoning is not a product control | medium |
| 9 | Model/effort selection, 60/30/10 (33) | unsupported + time-sensitive | Routing beats fixed splits and always-frontier (arXiv 2606.22902); recheck each model release | medium |
| 10a | Deterministic checks after fixtures pass | supported | Corpus demo pages + SpecBench + Loam's own gate stack | high |
| 10b | Step-count bands, remote-control mechanics | unsupported / time-sensitive | No evidence; remote pages grade-inflated (prose scored as demo); 154 records perishable | high |
| 11a | Dependency security block (22) | supported (delegated) | Cites OpenSSF/CISA/SBOM; validate against the owning standards | medium |
| 11b | Code craft rules (~30) | unsupported | One author's one page, all assertion | high |

## Model-specific evidence (the models Samyak runs)

Only three sources test Opus 4.7 or newer.
Zero published software-engineering studies test Claude Fable 5 or Claude Opus 5; their coding numbers are Anthropic system-card figures.

- Skills gave Opus 4.8 +28.2 instruction-following points (59.8 to 88.0) across ~38,000 trajectories ([arXiv 2606.17819](https://arxiv.org/abs/2606.17819), workshop-reviewed, authors sell agent tooling).
- Fable 5 vs Opus 4.8 on the same harness: 92.9 vs 92.0 overall while the skill context added ~17 points to both; Opus 4.8 wins quality-per-dollar 125 to 74 (Tessl blog, vendor-published).
- Opus 4.6 to 4.8 alone was worth +24.9 points on SWE-Atlas QnA; a coordinated 4-agent team on 4.6 (62.1%) still beat single-agent 4.8 (57.2%); compute-matched independent runs reached only 37.9% ([arXiv 2607.28430](https://arxiv.org/abs/2607.28430)).
- The synthesis that reconciles the nulls with the positives: describing the repository to the agent is worthless and costs 20-23% more tokens; giving it a procedure is worth ~28 points even at the frontier.
- Long-horizon decay is the measured enemy: quality erosion in 80% of long trajectories (SlopCodeBench [arXiv 2603.24755](https://arxiv.org/abs/2603.24755)); compliance odds drop ~5.6% per generated function (McMillan).
- Frontier Lag ([arXiv 2605.04135](https://arxiv.org/abs/2605.04135)): the median paper evaluates ~10.85 ECI points behind the frontier and 52.5% of conclusions over-generalize to "AI"; treat sub-frontier positives as upper bounds.
- Withdrawn: "Scaling Coding Agents via Atomic Skills" (arXiv 2604.05013). Never cite its +18.7%.

## Contradiction register

All 11 contradictions published in `cliefnotes-wisdom.md` verified, with one correction: #2 (40-50 vs 30-50 lines) is not preserved in the normalized ledger; N-0249's conditions carry neither figure.
Four new contradictions found:

1. A third uncaptured CLAUDE.md budget: page `02-the-foundation/05-04-44` says "15 lines is enough"; no ledger record captures it. The source's own budget varies more than 3x.
2. Four incompatible starter shapes: N-0006 (three files) vs N-0254 (one file plus one or two workspaces) vs N-0046 (two to four workspaces) vs N-0123 (four named folders).
3. Human review after a green gate (N-0598, demonstrated) vs run unmonitored on a clear spec (N-0373, asserted).
4. Skills as on-demand tooling (N-0311) vs an always-loaded doctrine layer before every agent (N-0414).

External conflict: "examples constrain exploration" (new-rules post, 2026) vs "curate canonical examples" (context-engineering post, 2025). Both verified current; the newer governs for Claude 5-generation models.

## Corrections to `cliefnotes-wisdom.md`

1. The "34 raw claims cite a linked repository or asset that the audit explicitly did not inspect" figure is wrong. Correct figures: 48 normalized records covering 83 raw claims. (Fixed in that file, dated.)
2. Contradiction #2's claim that "both conditions are preserved in the ledger" is wrong; the normalized record preserves only 30-50. (Annotated in that file.)
3. The step-4 note naming "Codex `/status`" matches no ledger record; either dropped in normalization or in error.
4. Grade-inflation pattern: Remote Control pages graded `demo` for in-page prose that never executed anything; F-AUTO-MISC-REMOTE is overstated, and the corpus demonstration count of 118 is an upper bound.

## Decisions (Samyak, 2026-08-31)

- **D1** Fix certain defects first, then pilots.
- **D2** Rebuild toward ~27 curated skills (refined 2026-09-01: they live in the sam-cc-setup plugin, not the seed, preserving the asset-layer rule), as on-demand procedural skills with invocation control and a trigger eval before each promotion. Evidence note: the always-loaded tier stays lean; the listing budget carries on-demand skills.
- **D3** Adopt the revised evaluation portfolio (deterministic + efficiency pilots). The dropped success-rate A/Bs are recorded below as unfunded hypotheses. Status: E1 shipped as hook fixtures; E2 and E3 ran 2026-09-01 with both falsifiers firing; E4 ran 2026-09-01 and found a live force-push bypass (now fixed); E5 ran 2026-09-01 (30/36, one description sharpened). All five pilots complete. See Pilot results.
- **D4** Ship a minimal handoff convention in seed now, justified on token savings; keep it cheap; preserve raw-trace access.
- **D5** This document is the tracked verdicts artifact.

## Retired heuristics

Removed from all normative Loam documents (historical research records keep them as records):

- The 30-50-line (and 15-line, and 40-50-line) CLAUDE.md budget.
- The 8-10-files-per-directory and 150-line context-file thresholds.
- The 60/30/10 model split.
- The 3-15-step automation band.
- The 1-5 impact/risk scoring scale as a fixed rule.

## Unfunded hypotheses (dropped evaluation designs)

The method doc's Tests 1, 2, 4, 5 (router A/B, plan A/B, agent-team A/B, skill-packaging A/B) need on the order of 150 trials per arm to detect a 15-point adherence effect, have no valid grader for a solo developer, and expire at each model release.
They are recorded as designs, not run.
If ever funded, Test 4 must equalize token budgets across arms ([arXiv 2604.02460](https://arxiv.org/abs/2604.02460)) or it is confounded.
Kept instead: E1 deterministic hook-gate fixtures; E2 mid-session re-anchor pilot; E3 handoff economics incl. a stale-handoff arm (the case no literature has tested); E4 reviewer replay on the labeled defect corpus in `.superpowers/sdd/`; E5 skill trigger precision/recall evals.

## Pilot results (E2, E3 - run 2026-09-01)

Both pilots ran headless (`claude -p`, model pinned `claude-opus-4-8`, permission mode acceptEdits) on fresh Copier-rendered fixture projects from loam HEAD, graded deterministically (AST checks, hidden tests, git history), never by the agent's own claims.

### E2: mid-session re-anchor hook - FALSIFIER FIRED, do not ship

Design: 3 arms x 4 trials x 6 user turns; each turn asks for 2 functions (12 per session, 48 per arm); AGENTS.md carries 5 unusual machine-checkable rules (qz_ prefix, [v] docstring marker, full type hints, __all__ registration, log() not print()).
Arm A control; arm B a UserPromptSubmit hook re-injecting a ~60-token rule reminder every turn; arm C the negative control injecting equal-length irrelevant text.

Result: 100.0% adherence in every arm, both session halves (720/720 rule checks passed; 0 turn errors).
Arm B cost +5% for zero gain.
The salience-decay effect (~5.6% compliance-odds drop per generated function, McMillan on Sonnet 4.6) predicts roughly halved adherence odds by function 12; observed adherence at functions 7-12 was 48/48 perfect in the control arm.
Reading: the decay effect did NOT transfer to Opus 4.8 in a clean small-context fixture; this is evidence against it at this scale, not merely an underpowered null.
Decision: no re-anchor hook ships. Revisit only if real long sessions in large repos show late-session rule violations (the audit log now makes that observable).

### E3: handoff economics - FALSIFIER FIRED for the token claim; stale-handoff harm NOT observed

Design: 4 arms x 4 trials resuming a mid-task fixture (feature 1 of 3 implemented and committed by a real prior session; feature 2 next per SPEC.md).
Arms: Structured HANDOFF.md (the shipped D4 convention), Raw transcript of the prior session, None, and STALE handoff (claims nothing is implemented, points at the pre-work commit).
Graded by hidden tests: correct next step (feature 2 works), no scope creep (feature 3 untouched), no redo of feature 1, one commit.

Result: 16/16 trials fully correct in every arm, including all 4 stale trials - the agent checked the repository, contradicted the stale artifact, and did the right next step every time.
Cost per trial (mean): None $0.92 / 24.5 turns; Structured $0.89 / 22.8; Raw trace $0.82 / 20.5; Stale $0.90 / 23.2.
The structured handoff saved 3%, far below its >=20% falsifier threshold, and the raw trace beat it (matching arXiv 2606.02875's direction).
Reading: on Opus 4.8 in a small repo with a written spec, re-orientation from the repository itself is nearly free; handoff artifacts add little, and a stale one does no harm because repo evidence wins.
Decision: the shipped D4 convention stays (six lines, harmless, correct in all trials) but is NOT expanded, and its justification is recorded as convenience, not measured token savings. No further handoff machinery.

### E4: reviewer replay - cross-family reviewer found a live bug the shipped tests missed

Design deviation (stated honestly): the method-doc arm was producer-self-check vs cross-family reviewer. This run instead used two independent fresh reviewers, Claude Opus 4.8 and Codex (gpt-5.6-sol), each blind to authorship, on the pre-fix commit `0db3d5b~1` where four known defect classes were present. It therefore measures fresh-reviewer rediscovery and compares the two model families; it does NOT test self-review (neither model wrote the code), so the "cross-family beats self" falsifier could not be evaluated as written.

Result: both families rediscovered seeded defects and, more valuably, both surfaced defects beyond the original fix.
- Claude and Codex both flagged that the workflow gate check ignores step conditions; Codex named `continue-on-error: true` and `if: ${{ false }}` exactly (the class commit 0db3d5b fixed with `_workflow_gate_is_unconditional`).
- Claude found the dangling-symlink topology gap (the class the same commit fixed).
- NEW and LIVE on current HEAD: Claude's arm found the Codex policy hook fails open when a force push hides behind an unrecognized git global option. Reproduced end-to-end: `git --no-literal-pathspecs push --force` and `git --attr-source=HEAD push --force` both returned ALLOW. This is a real security-relevant defect in shipped seed code, now fixed (commit closing "force-push bypass behind an unknown git global option") with regression tests and a non-over-deny guard (`git help push --force` still allowed).
- Also raised, latent not live: a cross-job release.yml with no `needs:` would bypass the position check. Current release.yml keeps both steps in one job, so it is not exploitable today; recorded as a contract-hardening follow-up.

Outcome: E4 paid for itself by finding a live bypass. The cost was ~$7 across 4 review sessions. The honest reading: a fresh independent reviewer of either family catches real defects; the specific self-vs-cross question remains unanswered and is a candidate for a future run with a proper self-review arm.

### E5: skill trigger precision and recall - 30 of 36 correct, two descriptions sharpened

Design: for each of the 9 new model-invocable skills, 2 should-trigger probes and 2 should-not-trigger probes (36 total), asking a fresh Claude which single listed skill it would pick. Graded by exact match.

Result: 30/36 correct. All 9 skills fired on at least one positive probe. Six misses:
- 2 recall misses: worktree-status and agent-team each missed one positive (the model answered NONE where the skill fit).
- 4 precision misses: ship, auto-phase, critique-swarm, gen-spec each pulled a neighbor skill (codex-review, brainstorming, writing-plans) on one should-not-trigger probe.
Action taken: sharpened the agent-team description so a "should I use a team?" question triggers it (that was its recall miss). The other five misses were near-neighbor confusions on deliberately ambiguous probes, within tolerance for a 24-skill listing; left as-is and recorded.
Falsifier check: no skill missed BOTH its positive probes, so none is demoted or inlined.

### Limits of both pilots

n=4 per arm; single small fixture repos; every E3 arm had SPEC.md (a no-spec resume was not tested); short sessions; one model.
The frontier pattern from the literature repeats exactly: scaffolding effects measured on smaller models did not reproduce on Opus 4.8.
Raw data and runners: session scratchpad `pilots/` (not tracked).

## Follow-on: external-skill vetting (built 2026-09-01)

The E5 skill work exposed a gap the Clief corpus flags but Loam had no control for:
adopting an external skill is a trust decision (corpus claim N-0331, N-0339). So a
vetting layer was added after the pilots.

What shipped:

1. `bin/vet-skill.sh` wraps NVIDIA SkillSpector (static scan, offline, no API key).
   Exit 0 (LOW/NONE) adopts, 1 (MEDIUM) needs a recorded human decision, 2
   (HIGH/CRITICAL) rejects. A `--safe` mode strips a skill's executables and
   re-scans, for skills whose value is prose not code.
2. A `CONTRIBUTING.md` rule: every external skill or bundle must pass the gate
   before it enters the repo.
3. The manual-only `sam-cc-setup:vet-skill` skill ships the procedure to any
   project (plugin 0.7.0, the 27th skill).
4. A macOS LaunchAgent keeps SkillSpector current weekly.

Evidence it earns its place: run against a real batch of ~17 externally-requested
research skills, the gate cleared 8 and blocked 9. Blocked items included a
reverse-shell code pattern (`gpt-researcher`), credential-file reads and a
vulnerable dependency (`FAROS`), and multiple prompt-injection payloads scoring
100/100 CRITICAL. `--safe` demonstrably lowered a paper-writing skill from HIGH to
MEDIUM by stripping its build Makefile, but could not salvage two skills whose
risk lived in rogue-agent prose rather than code. Popularity did not predict
safety, matching the corpus's own warning that community adoption is not evidence.

This layer is not one of the original Clief verdicts; it is a control the
validation surfaced as necessary and is recorded here for completeness.

## Recheck triggers

- Docs-based verdicts: recheck at each Claude Code minor release.
- Model/effort verdicts: recheck at each model release.
- 154 of 928 records (16.6%) are perishable product mechanics; defer to current docs rather than the corpus.
- Method notes: arXiv PDFs are unparseable via WebFetch; use `arxiv.org/html/<id>`. WebFetch page summaries can false-negative on large pages; for absence claims, fetch the raw page and grep.

## Full family table (68 families)

Grades are occurrences within the family (a record may carry several grades). D=demonstration, L=linked, C=community, E=experience, A=assertion.
Strength grades how well the source supports itself, not whether the claim is true.

| Family | n | D/L/C/E/A | Representative IDs | Strength |
|---|---|---|---|---|
| F-WORK-MISC-VERIFY | 66 | 16/3/2/6/44 | N-0543, N-0517, N-0509 | mixed |
| F-FOLD-MISC-CTX | 57 | 6/2/5/5/42 | N-0134, N-0006, N-0101 | weak |
| F-WORK-MISC-PLAN | 38 | 1/0/10/9/26 | N-0477, N-0473, N-0520 | weak |
| F-FOLD-MISC-ARCH | 33 | 2/2/1/4/26 | N-0043, N-0148, N-0007 | weak |
| F-FOLD-MISC-ROUTE | 31 | 1/4/2/2/30 | N-0023, N-0032, N-0029 | weak |
| F-WORK-SECURITY | 28 | 13/4/0/0/11 | N-0595, N-0591, N-0592 | strong |
| F-PROMPT-MISC-GEN | 27 | 1/1/1/3/21 | N-0728, N-0763, N-0735 | weak |
| F-FOLD-CODECRAFT | 26 | 0/1/0/0/25 | N-0204, N-0087, N-0213 | absent |
| F-WORK-MISC-GEN | 26 | 7/1/1/1/16 | N-0518, N-0607, N-0481 | mixed |
| F-AGENT-MISC-GEN | 24 | 0/1/3/0/20 | N-0371, N-0373, N-0365 | weak |
| F-MEM-MISC | 24 | 2/4/4/5/13 | N-0432, N-0427, N-0428 | mixed |
| F-WORK-SETUP | 24 | 3/0/1/0/21 | N-0463, N-0504, N-0507 | weak |
| F-SKILL-MISC | 23 | 0/5/0/1/17 | N-0310, N-0314, N-0313 | weak |
| F-WORK-MISC-REVIEW | 23 | 3/0/0/3/17 | N-0626, N-0486, N-0634 | weak |
| F-FOLD-SECURITY | 22 | 0/15/0/0/7 | N-0042, N-0014, N-0025 | linked-only |
| F-OTHER-SECURITY | 22 | 0/10/0/0/15 | N-0901, N-0904, N-0921 | best external grounding |
| F-MODEL-MISC | 21 | 1/6/3/3/13 | N-0796, N-0801, N-0795 | mixed |
| F-AUTO-MISC-GEN | 21 | 0/1/7/3/14 | N-0828, N-0827, N-0886 | weak |
| F-FOLD-MISC-GEN | 20 | 6/0/2/0/12 | N-0107, N-0108, N-0033 | mixed |
| F-RULE-MISC-GEN | 19 | 2/1/0/0/16 | N-0257, N-0259, N-0260 | weak |
| F-WORK-MISC-MAINT | 18 | 2/2/3/2/12 | N-0465, N-0547, N-0544 | weak |
| F-AUTO-SECURITY | 17 | 0/5/0/0/14 | N-0860, N-0831, N-0880 | mixed |
| F-FOLD-MISC-IFACE | 16 | 0/10/0/0/6 | N-0078, N-0085, N-0086 | linked-only (uninspected) |
| F-WORK-MISC-TEST | 16 | 13/1/0/0/2 | N-0464, N-0562, N-0572 | strong (best in corpus) |
| F-AUTO-MISC-REMOTE | 15 | 10/0/0/0/10 | N-0857, N-0853, N-0854 | overstated (prose graded demo) |
| F-FOLD-SETUP | 14 | 1/2/1/1/9 | N-0109, N-0003, N-0004 | weak |
| F-AUTO-SETUP | 14 | 3/0/0/0/13 | N-0856, N-0850, N-0863 | weak |
| F-FOLD-MISC-MAINT | 12 | 0/1/0/0/12 | N-0097, N-0189, N-0178 | absent |
| F-RULE-MISC-ROUTE | 12 | 0/0/1/3/10 | N-0252, N-0249, N-0251 | absent |
| F-PROMPT-MISC-CTX | 12 | 0/0/1/2/10 | N-0732, N-0725, N-0726 | absent |
| F-PROMPT-SETUP | 12 | 2/0/0/0/12 | N-0749, N-0742, N-0752 | weak |
| F-WORK-CODECRAFT | 11 | 1/0/2/1/7 | N-0468, N-0510, N-0522 | weak |
| F-SKILL-SETUP | 10 | 0/1/0/1/8 | N-0321, N-0312, N-0315 | weak |
| F-SKILL-SECURITY | 10 | 0/0/2/0/8 | N-0340, N-0318, N-0331 | weak |
| F-PROMPT-MISC-PLAN | 10 | 3/0/1/0/10 | N-0736, N-0741, N-0743 | mixed |
| F-MODEL-BUSINESS | 10 | 0/1/1/2/8 | N-0803, N-0819, N-0808 | weak |
| F-FOLD-MISC-DOC | 9 | 1/1/1/0/8 | N-0058, N-0099, N-0140 | weak |
| F-AGENT-MISC-ORCH | 9 | 1/0/0/4/7 | N-0361, N-0393, N-0414 | weak |
| F-AGENT-BUSINESS | 9 | 0/0/0/4/5 | N-0399, N-0411, N-0413 | absent |
| F-RULE-CODECRAFT | 8 | 0/0/0/0/8 | N-0267, N-0293, N-0294 | absent |
| F-WORK-BUSINESS | 8 | 0/0/1/2/5 | N-0631, N-0625, N-0628 | absent |
| F-RULE-MISC-YAGNI | 7 | 0/0/2/0/5 | N-0254, N-0266, N-0278 | absent |
| F-RULE-SECURITY | 7 | 1/0/0/0/6 | N-0256, N-0286, N-0263 | weak |
| F-RULE-BUSINESS | 7 | 1/0/1/1/4 | N-0301, N-0302, N-0303 | weak |
| F-AGENT-MISC-PLAN | 7 | 0/0/2/0/5 | N-0368, N-0384, N-0385 | absent |
| F-MEM-SECURITY | 7 | 2/2/0/0/3 | N-0436, N-0437, N-0441 | mixed |
| F-WORK-MISC-HANDOFF | 7 | 5/0/0/1/1 | N-0546, N-0537, N-0538 | strong-ish |
| F-AGENT-SETUP | 6 | 1/0/0/3/2 | N-0374, N-0362, N-0375 | weak |
| F-AGENT-SECURITY | 6 | 1/0/0/1/4 | N-0391, N-0380, N-0366 | weak |
| F-PROMPT-MISC-VERIFY | 6 | 1/0/3/0/4 | N-0776, N-0727, N-0733 | weak |
| F-FOLD-BUSINESS | 5 | 0/0/0/2/3 | N-0060, N-0077, N-0181 | absent |
| F-OTHER-SETUP | 5 | 3/0/0/0/2 | N-0895, N-0896, N-0897 | weak |
| F-OTHER-CODECRAFT | 5 | 0/0/0/0/5 | N-0924, N-0925, N-0926 | absent |
| F-HOOK-MISC | 4 | 0/0/1/0/3 | N-0354, N-0356, N-0357 | absent |
| F-AGENT-MISC-ROUTE | 4 | 1/0/0/0/4 | N-0360, N-0382, N-0383 | weak |
| F-FOLD-MISC-TMPL | 2 | 0/0/0/0/2 | N-0040, N-0130 | absent |
| F-RULE-SETUP | 2 | 0/1/0/0/1 | N-0264, N-0269 | absent |
| F-MEM-CODECRAFT | 2 | 0/0/0/0/2 | N-0451, N-0452 | absent |
| F-PROMPT-SECURITY | 2 | 0/0/0/0/2 | N-0734, N-0785 | absent |
| F-OTHER-MISC | 2 | 0/0/1/0/2 | N-0917, N-0920 | absent |
| F-SKILL-CODECRAFT | 1 | 0/0/0/0/1 | N-0316 | absent |
| F-HOOK-BUSINESS | 1 | 0/0/0/0/1 | N-0355 | absent (SOUL.md, misfiled) |
| F-HOOK-CODECRAFT | 1 | 0/0/0/0/1 | N-0358 | absent (Vue rule, misfiled) |
| F-AGENT-CODECRAFT | 1 | 0/0/0/0/1 | N-0392 | absent |
| F-MEM-BUSINESS | 1 | 0/0/0/1/0 | N-0457 | weak |
| F-MODEL-SECURITY | 1 | 0/0/0/0/1 | N-0798 | absent |
| F-MODEL-SETUP | 1 | 0/0/0/0/1 | N-0826 | absent |
| F-AUTO-MISC-SESS | 1 | 1/0/0/0/0 | N-0873 | weak |

Partition recipe (recomputable): base key is (theme, subtheme) mapped to `F-<ABBR>-<SUBTHEME>` with abbreviations folders=FOLD, workflow=WORK, automation=AUTO, prompting=PROMPT, agents=AGENT, rules=RULE, models=MODEL, skills=SKILL, memory=MEM, other=OTHER, hooks=HOOK.
Six oversized `misc` buckets split by first matching topic in an ordered list (workflow: human review/human-in-the-loop -> REVIEW, tests -> TEST, verification -> VERIFY, planning -> PLAN, maintenance -> MAINT, handoff -> HANDOFF; folders: routing -> ROUTE, interfaces -> IFACE, documentation -> DOC, architecture -> ARCH, context -> CTX, maintenance -> MAINT, templates -> TMPL; prompting: planning -> PLAN, verification -> VERIFY, context -> CTX; agents: orchestration -> ORCH, routing -> ROUTE, planning -> PLAN; rules: routing -> ROUTE, YAGNI -> YAGNI; automation: remote -> REMOTE, sessions -> SESS); no match falls to `-GEN`.
