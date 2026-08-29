# Reference audit: vercel-labs/agent-skills (planning-stage assets)

> Audited 2026-08-29 against a shallow clone of `https://github.com/vercel-labs/agent-skills` (default branch HEAD at clone time).
> Scope: planning-stage assets only - plan review, adversarial/spec review, architecture and system design, concept-to-design, technology selection, fleshing out the "how" of an implementation plan.
> All judgments come from reading the actual `SKILL.md` and `references/*.md` files, not the README.
> Note on quoting: block quotes and fenced excerpts are reproduced verbatim from the source, so they keep the source's own punctuation (including em dashes). All of my own prose uses plain dashes.

## Headline finding

**This repo contains zero planning-stage skills.** The full inventory is 9 skills, and every one of them is implementation, styling, framework, or ops:

| Skill | Path | Category |
|---|---|---|
| `vercel-optimize` | `skills/vercel-optimize/` | ops / audit pipeline |
| `vercel-react-best-practices` | `skills/react-best-practices/` | implementation rules (70 rules) |
| `vercel-composition-patterns` | `skills/composition-patterns/` | implementation rules (9 rules) |
| `react-view-transitions` | `skills/react-view-transitions/` | framework how-to |
| `react-native-skills` | `skills/react-native-skills/` | framework how-to |
| `deploy-to-vercel` | `skills/deploy-to-vercel/` | ops |
| `vercel-cli-with-tokens` | `skills/vercel-cli-with-tokens/` | ops |
| `web-design-guidelines` | `skills/web-design-guidelines/` | review (thin wrapper, see below) |
| `writing-guidelines` | `skills/writing-guidelines/` | review (thin wrapper, see below) |

There are no `agents/`, no `commands/`, and no plugin manifest anywhere in the tree. There is no plan reviewer, no architecture skill, no design-decision skill, no tech-selection skill.

So the value here is **not adoptable assets**. It is one asset - `vercel-optimize` - that happens to be the most rigorously engineered *evidence-bound review pipeline* I have read in a public skills repo, and whose machinery transfers cleanly to plan review even though its subject matter does not. The rest of this document audits that machinery at the technique level.

---

## 1. `vercel-optimize` - Doctrine (the four non-negotiables)

**Path:** `skills/vercel-optimize/references/doctrine.md` (105 lines), entry point `skills/vercel-optimize/SKILL.md` (322 lines).

**What it does:** States four rules that constrain every action the skill takes, each paired with an explicit "why this fails when skipped" failure mode. It opens by declaring itself the tiebreaker: "The four non-negotiable rules that shape every action this skill takes. If a future change conflicts with one of these, the change is wrong."

**Best technique - the signal-before-inspection rule:**

> ## Rule 1: Observability before investigation
>
> The skill never reads a source file without an observability signal pointing at it. Step 1 (`node scripts/collect-signals.mjs`) is always first. Nothing reads source code until `signals.json` exists.
>
> **Why this fails when skipped:** without metrics, the skill defaults to "grep the repo for known anti-patterns and complain." That produces noisy, low-impact recs that aren't tied to traffic, cost, or user pain.

**Best technique - the anti-drift scope clamp:**

> If you find yourself wanting to grep the whole codebase, stop and re-read the current candidate's `question` field. If the question doesn't constrain the search, the candidate is malformed — log it as `gated` and skip. Do NOT compensate with a wider search.

The doctrine also ships an explicit **"What good looks like" / "What bad looks like"** pair, where the bad list is populated with real anti-recommendations the team has actually seen ship (`"Enable Fluid Compute" without a cold-start signal`, `"Add caching to /api/users" when the route has cookies() and is auth-gated`, `"Save $340/mo by doing X" — invented precision`), plus a four-item **Out of scope** section that names non-goals and says where to route them instead.

**Quality judgment:**
- (a) Bounded findings, hard. Budget is 6 candidates by default; scope is clamped to files named by the candidate.
- (b) Explicit rubric. Yes, and unusually the rubric is stated as failure modes rather than virtues.
- (c) Fresh-context/blind design. Partially - sub-agents get only the brief, but the doctrine is about scope, not blindness.
- (d) Evidence over assertions. This is the entire document.
- (e) Generic competence? **No.** A strong model does not spontaneously refuse to look at a file until a metric points at it. The default model behavior is exactly the failure mode Rule 1 names: grep broadly, list anti-patterns, sound thorough.

---

## 2. `vercel-optimize` - Mechanical claim verification

**Path:** `skills/vercel-optimize/references/verification.md` (102 lines).

**What it does:** Defines a deterministic, LLM-free verifier that extracts every checkable claim from a generated recommendation and checks it against the filesystem, grep, a signals JSON, and a citation allow-list. Thirty claim types (`pattern_count`, `pattern_absent`, `file_exists`, `contradiction`, `code_snippet`, `arithmetic`, `citation_in_library`, `citation_applies_to_version`, and 22 domain-specific ones). Four dispositions. A pass-rate-triggered regeneration loop.

**Best technique - refusing to let the author grade itself:**

> The recommender is an LLM. LLMs hallucinate counts, miscount file occurrences, and confuse code snippets between similar-looking files. Mechanical verification — grep + filesystem reads + JSON checks against `signals.json` and `references/docs-library.json` — catches these failures before the customer sees them.
>
> The contract: every numeric claim, file reference, code snippet, citation URL, and contradiction-with-other-claims is verified. **The LLM is not asked to judge whether its own output is correct.**

**Best technique - four dispositions, with unverifiable claims excluded from the score rather than counted as passes:**

| Disposition | Meaning | Counted toward `passRate`? |
|---|---|---|
| `verified` | Claim matches reality | yes (counts as pass) |
| `failed` | Claim contradicts reality | yes (counts as fail) |
| `unsupported` | Claim can't be checked mechanically | no |
| `unverifiable` | Out of scope | no |

Plus three named verifier guards that encode real past false positives, the most transferable being:

> **`prose-of-absence`**: "no cache headers" without an explicit grep confirmation → `unsupported`; absence claims require evidence.

And a re-run rule with an accept criterion, so the loop cannot degrade the output:

> | `passRate < 0.8 AND verifiableClaimCount >= 2` | Re-run Step 3.3 (the recommender) with `topFailures` injected as feedback |
>
> Re-gen accept criteria:
> - `regenPassRate >= originalPassRate` AND
> - Rec count not gutted (regen doesn't drop more than 50% of recs) AND
> - Findings still cited (no rec orphaning)
>
> If re-gen makes things worse, keep the original output unless the trigger was hard safety.

The file even records why a threshold moved: "_(Floor lowered 5 → 2 in May 2026 audit: a rec with 1/1 failed claim is just as broken as 1/5, and the old floor let many small recs escape re-gen entirely.)_"

**Quality judgment:**
- (a) Bounded. Claims are enumerated types; anything outside them is `unverifiable` and scored as nothing.
- (b) Explicit rubric. The strongest in the repo - a 30-row claim table plus a disposition table plus accept criteria.
- (c) Fresh-context/blind. Yes in the important sense: the verifier is a pure function with no access to the author's reasoning, only to the artifact and the ground truth.
- (d) Evidence over assertions. This is the definitional example.
- (e) Generic competence? **No.** A strong model asked to "double-check your findings" will re-read its own text and confirm itself. Separating claim extraction from claim checking, and denying the author a vote, is a structural move a model will not make on its own.

---

## 3. `vercel-optimize` - The deterministic gate and the "Not investigated" ledger

**Path:** `references/doctrine.md` Rule 2, `references/candidates.md` (176 lines, generated), `SKILL.md` step 2.

**What it does:** Every candidate class has its trigger threshold written as a pure JS predicate with a stated numeric threshold and a source citation, so the decision "is this worth reviewing" is never an LLM judgment call. Skipped candidates are not discarded - they are carried into the report with the reason they were held back.

**Best technique - mechanical triage plus a visible skip ledger:**

> **Failed gates surface in the final report**, under "Not investigated in this run," with the exact reason they were held back. This is the user-facing trust mechanism: you see what we considered and chose to skip, and the reason.
>
> **Why this matters:** the agent never decides "should I look at this route?" via LLM judgment. The threshold is mechanical. This eliminates the entire failure mode where the agent investigates routes it shouldn't (cold-path) and recommends fixes for routes that don't need them.

Each gate carries a defended threshold rather than a vibe, for example:

> ### `cold_start`
> - **Threshold**: `coldPct > 0.4 AND total >= 1000`
>
> Routes where > 40% of invocations are cold-start, at meaningful traffic (>=1,000 total invocations in window). ... The 40% threshold is where cold-rate becomes a real signal vs Poisson noise on serverless.

And the report template turns the skip list into a first-class section with a per-reason table ("Not investigated in this run ... This section earns the user's trust. For every metric signal we considered but didn't act on, group by candidate type and reason").

**Quality judgment:**
- (a) Bounded. `MAX_CODE_CANDIDATES = 6` with a diversity guardrail; expanding requires an explicit flag and, above a threshold, an explicit user question.
- (b) Explicit rubric. Yes - 15 gates, each with a threshold expression and a defense of the number.
- (c) Fresh-context/blind. Not applicable.
- (d) Evidence over assertions. Yes; thresholds cite either a doc URL or are labeled `vercel-optimize gate threshold` (honest about being a house number).
- (e) Generic competence? **Partly.** A strong model can prioritize sensibly. What it will not do unprompted is publish what it chose *not* to examine and why. That half is genuinely novel and cheap to steal.

---

## 4. `vercel-optimize` - The bounded sub-agent brief contract

**Path:** `SKILL.md` sections 2.3-2.4.

**What it does:** Converts each gated candidate into a generated brief file, fans out one sub-agent per brief, and constrains what a sub-agent may read, cite, and emit. Outputs are collected by a script that enforces a manifest and fails on drift.

**Best technique - the brief is the whole prompt:**

> Sub-agent contract:
>
> - The brief is the whole prompt.
> - Read only files listed in the brief, plus route-local imports when needed.
> - Emit one JSON recommendation or one JSON no-change finding using [references/recommendations.md](references/recommendations.md).
> - Do not cite URLs outside the provided citation subset.
> - Do not recommend framework features unavailable in the detected version.
>
> If a sub-agent reaches for repo-wide grep, the candidate is malformed; drop or abstain rather than widening scope.

Two more details worth noting. The fan-out threshold is stated rather than left to taste ("1-2 briefs: investigate inline. 3+ briefs: spawn one sub-agent per brief"). And the collector is adversarial toward its own workers: "The collector extracts JSON, prepends pre-resolved records, enforces manifest order, and fails on missing, duplicate, unknown, or mismatched `candidateRef` values."

**Quality judgment:**
- (a) Bounded. Maximally so - one finding per agent, allowed to be a no-change finding.
- (b) Explicit rubric. The output schema is the rubric.
- (c) Fresh-context/blind. Yes, and this is the cleanest blind-review mechanic in the repo: the sub-agent gets the artifact and the constraints, never the pipeline's reasoning about why it was selected beyond the brief's stated question.
- (d) Evidence over assertions. Enforced downstream by the verifier.
- (e) Generic competence? **No.** The "abstain rather than widen scope" clause inverts the default agent instinct, which is to broaden the search when the narrow one finds nothing.

---

## 5. `vercel-optimize` - Calibrated impact language (precise vs magnitude)

**Path:** `references/scoring.md` (205 lines) and `references/doctrine.md` "Cost framing is magnitude, never precise".

**What it does:** Splits claim precision by claim provenance. Observed quantities are stated exactly; extrapolated quantities are stated only in coarse buckets, and a sanitizer strips any precise dollar figure from customer-facing text at render time.

**Best technique - precision follows provenance:**

> **Performance: be precise.** Use observed numbers. ... Performance numbers come from `signals.json.metrics.*` — they're observed, not extrapolated.
>
> **Dollar cost: never precise.** Use MAGNITUDE BUCKETS ...
>
> **Why magnitudes:**
> - Traffic varies. A "20% reduction in edge requests" is exact at today's traffic and meaningless next quarter.
> - Pricing changes. ... precise dollar projections rot.
> - The user is smart. They'd rather see "hundreds of dollars per month" with a real metric backing it than `$340/mo` with a hand-wave behind it.

with the closing line from the doctrine: "We trust observed metrics; we don't trust dollar projections."

The scoring file also carries a **quality floor** with a defense of the number ("Drop recommendations with `quality.overall < 0.55` ... Bad-grade recs erode trust faster than they help") and a **prune cap** that protects against an over-aggressive pruner ("Prune cap on findings: 30% of input. Stops the pruner from wiping the report when LLM merit-grades are noisy").

**Quality judgment:**
- (a) Bounded. Quality floor plus a 3-item cap on account-level recommendations.
- (b) Explicit rubric. Yes, with a bucket table.
- (c) Blind. Not applicable.
- (d) Evidence over assertions. Yes, and this is the most portable single idea in the repo: the *unit of precision you are allowed to use is a function of where the number came from*.
- (e) Generic competence? **No.** Confident false precision on estimates is a well-known model failure, and models do not self-impose bucket vocabularies.

---

## 6. `vercel-optimize` - The four-axis grading rubric and the sanitizer stack

**Path:** `references/recommendations.md` (203 lines).

**What it does:** Defines the recommendation schema (including a required `risk` field and a required `verify` field - how to confirm the fix worked), a 12-sanitizer post-processing stack with an audit trail, and a four-axis 0-1 grading rubric with an operational signal for each axis.

**Best technique - a rubric whose axes have mechanical detectors:**

> | Axis | What it measures | Strong (1.0) signal |
> |---|---|---|
> | Specificity | Concrete files, line numbers, code snippets | Triple-backtick code fence OR inline code ≥10 chars + verified file path |
> | Actionability | Clear "do this then that" steps | Numbered steps; verbs present in each step; no "consider"/"might" |
> | Grounding | Claims trace to findings or metric data | `sourceIndex` matches a finding OR rec has affectedFiles + code fences |
> | Evidence | Numeric, observed claims | Count words (errors, queries, invocations) + units (% / ms / s / K / M) |

**Best technique - the paired bad/good examples are about hedging, not correctness:**

> - ❌ "Consider enabling caching on the /api/products route" (filler before substance)
> - ✅ "Add Cache-Control with s-maxage to /api/products" (verb-first, scope-explicit)
>
> - ❌ "The route is uncached" (could apply anywhere)
> - ✅ "src/app/api/products/route.ts:22 returns Response without Cache-Control; observability shows 0% cache hit on 1.2M invocations/mo"

The test embedded in the second pair - "could apply anywhere" - is a one-line falsifiability check that would catch most of what is wrong with generic review output.

The sanitizer stack is mostly domain-specific (12 sanitizers, of which roughly 8 are Vercel/Next-specific), but three are general: `count-correct` / `count-strip` (rewrite a cited count that exceeds the verified count down to "~N" or to "a number of"), and `missing-citation` (drop the finding entirely). The ordering rationale is stated: "dollar-strip runs first (cheap, deterministic), then content sanitizers, then citation sanitizers last. This guarantees citation count is computed against the final state."

**Quality judgment:**
- (a) Bounded. Yes, via floor and caps.
- (b) Explicit rubric. Yes - the best-specified rubric here, because each axis names what would make a grader score it 1.0.
- (c) Blind. No.
- (d) Evidence over assertions. Yes.
- (e) Generic competence? **Mixed.** "Be specific, cite lines, don't hedge" is competence a strong model already has and often ignores under load. The non-generic part is the mechanical detector column, which turns taste into something a checker can run.

---

## 7. `web-design-guidelines` and `writing-guidelines` - the fetch-fresh-rules pattern

**Path:** `skills/web-design-guidelines/SKILL.md` (39 lines), `skills/writing-guidelines/SKILL.md` (39 lines).

**What it does:** Both are 39-line shells. Neither contains any rules. Each fetches its rule set from a raw GitHub URL at review time, applies it, and emits terse `file:line` findings.

> ## Guidelines Source
>
> Fetch fresh guidelines before each review:
>
> ```
> https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
> ```

**Quality judgment:**
- (a) Bounded? Unknown - the bound lives in the fetched file, not here.
- (b) Explicit rubric? Not in the skill. Deferred entirely.
- (c) Blind? No.
- (d) Evidence over assertions? Only the `file:line` output convention.
- (e) Generic competence? The skill body is essentially "go read the rules and apply them," which is generic. The *pattern* - keep zero rules in the skill, keep the checklist in one canonical remote file, always re-fetch - is a real architectural choice with a real cost (a network dependency and an unpinned, unversioned rubric that can change under you between two runs of the same review). For Loam, whose whole thesis is a versioned template, this pattern is a warning, not a model.

---

## 8. `vercel-composition-patterns` and `vercel-react-best-practices` - the rules-file format

**Paths:** `skills/composition-patterns/` (9 rules), `skills/react-best-practices/` (70 rules across 8 categories).

**What they do:** Not planning skills, but they share an authoring format worth noting. A thin `SKILL.md` holds only a priority table and a one-line-per-rule index; each rule is a separate file with frontmatter (`title`, `impact`, `impactDescription`, `tags`) and a fixed body of explanation, an Incorrect example, a Correct example, and a reference link. A `_template.md` and a `_sections.md` enforce the shape, and a compiled `AGENTS.md` concatenates everything for hosts that want one file.

The one genuinely design-stage idea inside them is `architecture-avoid-boolean-props`, which is a real interface-design argument rather than a lint rule:

> Don't add boolean props like `isThread`, `isEditing`, `isDMThread` to customize component behavior. Each boolean doubles possible states and creates unmaintainable conditional logic. Use composition instead.

**Quality judgment:**
- (a) Bounded? The rule *set* is bounded and prioritized; a review using it is not.
- (b) Explicit rubric. Yes - impact tier per rule, priority per category.
- (c) Blind? No.
- (d) Evidence over assertions? Incorrect/Correct code pairs, which is the strongest form of evidence available for a style rule.
- (e) Generic competence? **Largely yes.** A strong model knows most of these 70 React rules. The transferable part is the format (index in SKILL.md, one file per rule, frontmatter-carried impact tier, template-enforced shape, compiled single-file variant), not the content. Loam already does something close to this with its rules layer.

---

## Shortlist: what is actually worth taking

Three techniques, in priority order. None of the nine skills is worth adopting as an asset; all three items below are mechanics to fold into Loam's own plan-reviewer.

1. **Mechanical claim verification with four dispositions and a pass-rate re-run gate** (`references/verification.md`). Fold into the merged blind plan-reviewer as a second, non-authoring pass: extract every checkable claim the reviewer made (file exists, symbol exists, count, "X is absent", arithmetic), check each against the repo with grep and Read, score `verified / (verified + failed)` with unsupported and unverifiable excluded, and require a re-run when the rate is under 0.8 with two or more checkable claims. The load-bearing rule is that the reviewer never grades itself, and the `prose-of-absence` guard alone - absence claims require an explicit confirming grep - would catch a large share of confidently wrong review findings.

2. **The visible skip ledger: publish what you deliberately did not examine, and why** (`doctrine.md` Rule 2 plus the "Not investigated in this run" section of `scoring.md`). Cheap to add, immediately raises trust in a bounded reviewer, and directly answers the standing objection to capping findings at N: the reader can see the N+1th candidate and the reason it was cut, instead of wondering whether the cap hid something.

3. **Precision-follows-provenance in impact language** (`scoring.md` plus `doctrine.md` "Cost framing is magnitude, never precise"). Observed quantities get exact numbers; extrapolated or projected quantities get coarse magnitude buckets and never a fabricated precise figure. Pair it with the falsifiability test embedded in the recommendations examples: if a finding "could apply anywhere," it is not a finding. Both are one-paragraph additions to a reviewer prompt and both attack the specific way review output goes wrong under a strong model, which is fluent, specific-sounding, unfalsifiable prose.

Worth noting for the record and then setting aside: the bounded sub-agent brief contract (item 4) is excellent but Loam's existing fan-out reviewer already implements most of it; the one clause worth importing verbatim is "if a sub-agent reaches for repo-wide grep, the candidate is malformed; drop or abstain rather than widening scope." And the fetch-fresh-rules pattern (item 7) should be explicitly rejected for Loam - an unpinned remote rubric is not reproducible across two runs of the same review.
