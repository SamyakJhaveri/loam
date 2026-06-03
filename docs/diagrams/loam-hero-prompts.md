# Loam Diagram Index — Two-Track Design Language

This file is the index and dashboard for Loam's diagram design language (the filename keeps
its historical `-prompts` suffix; the verbatim prompts themselves now live in `concepts.yaml`).
It catalogs the 16 visual concepts, tracks which renders exist, and points to the authoritative
method. It is Loam's own dogfood content (repo-local, kept out of bootstrapped projects).

The design language runs on **two tracks**:

- **Track A — research-grade legible figures**, produced via self-hosted PaperBanana, which
  optimizes for clear, labeled academic figures.
- **Track B — atmospheric Hiroshi Yoshida woodblock hero art**, produced via the automated
  `render-yoshida.py` engine, which optimizes for evocative shin-hanga mood.

The full method (preamble assembly, palettes, reference handling, and candidate QA) lives in
the design-language spec and quality gate; this dashboard stays a thin index and points there
for detail.

## Two tracks

**Track A — research-grade.** Self-hosted PaperBanana, driven in pipeline mode through its
browser Streamlit `demo.py`. It optimizes for legibility: labeled academic figures (proportion
charts, stacked-layer diagrams, composition figures). The flow is manual and human-in-the-browser:
a person tunes the structured fields and judges the output on the rendering surface.

**Track B — Yoshida shin-hanga.** Direct Gemini `gemini-3-pro-image`, producing atmospheric
woodblock hero art. The flow is automated through `render-yoshida.py`, which reads the concept
registry, assembles the prompt, and calls the model.

## Pointers

- **Design-language spec (authoritative method):** [`../../seed/.claude/skills/diagrams/design-language.md`](../../seed/.claude/skills/diagrams/design-language.md)
- **Quality gate (concept contract + candidate QA):** [`../../seed/.claude/skills/diagrams/quality-gate.md`](../../seed/.claude/skills/diagrams/quality-gate.md)
- **Concept registry (source of truth for all prompts):** [`concepts.yaml`](concepts.yaml) (sibling file)

**Verbatim prompts live in `concepts.yaml` — the single source.** They are NOT duplicated here.
This dashboard names concepts and tracks; the registry holds the exact prompt text and
acceptance criteria per concept.

## Catalog (16 concepts)

The shared design vocabulary. Each concept can be expressed on both tracks. **Track B prompts
are now authored (v1) for all 15 active concepts (#1–#15)**, grounded in
[`design-philosophy.md`](design-philosophy.md) and dry-run-verified against the render engine;
#16 is an intentional reserved stub. Only #1 (identity) has actually been rendered and kept this
round — the other v1 prompts are the consistent starting point for the per-concept render-judge
loop (renders pending). They share one visual vocabulary: glass-box loam source, cutaway with
root-channels, varied plant kinds in the foreground, calm Yoshida lake + layered hills, fresh and
bright (never washed); the glowing return loop belongs to identity only.

| # | Concept | Track A — research figure | Track B — Yoshida hero | Track B prompt |
|---|---------|---------------------------|------------------------|----------------|
| 1 | Identity (the living seed-store) | hub-and-spoke: central store → staged projects, copy out + promote back | glass-box store in a cutaway, 4 root-channels with bidirectional arrows, glowing return seeds | authored · rendered (KEEP c3) |
| 2 | Lifecycle (seed exchange, 4-beat) | one project: seeded→grown→upgraded(sync)→promoted-back | one plant maturing through 4 beats in a cutaway bed; single return at the end | authored (v1) |
| 3 | Context routing (L0/L1/L2) | 3 load layers + token budgets | glass dispatch basin → 3 channels → 3 destination beds at different depths | authored (v1) · re-aligned |
| 4 | Layer triage (60/30/10) | deterministic/rule/probabilistic split (proportion chart) | root mass through 3 unequal earth bands | authored (v1) |
| 5 | Workflow (6 stages) | Orient→…→Verify (gate) | one tended path through 6 beds ending at a harvest gate | authored (v1) |
| 6 | Repo anatomy (garden map) | labeled tree: seed/ soil/ cultivation/ docs/ bin/ | walled-garden map of plots; seed-bed as the shipped region | authored (v1) |
| 7 | Fan-out (one→many) | one template → N projects, outward only | glass box → many outward channels to seedlings, no return | authored (v1) |
| 8 | Cultivation (greenhouse) | wip→marketplace→retired staging | greenhouse with 3 staging areas, plants moving between | authored (v1) |
| 9 | Flavors (cultivars) | base template + research overlay graft | one base plant with a grafted research cultivar | authored (v1) |
| 10 | Validation (three sieves) | 3-wave gate (Det/Rule/Prob) | harvest poured through 3 stacked sieves at a gate | authored (v1) |
| 11 | Soil (knowledge base) | jvc/foundation/playbooks sources | layered living-soil cutaway feeding one plant's roots | authored (v1) |
| 12 | Memory (compost) | write→index→consolidate(dream)→prune | compost cycle: gathered → broken down → returned as nourishment | authored (v1) |
| 13 | Agent teams (pollination) | advisor(Opus)+worker(Sonnet) topology | one coordinator bee directing several worker bees | authored (v1) |
| 14 | Toolkit (the tools) | skills/hooks/agents/rules taxonomy | 4 grouped tool sets in one tidy garden rack | authored (v1) |
| 15 | Cover art (Track B only) | — | seed opening into roots that resolve into circuitry | authored (v1) |
| 16 | Reserved | — | — | reserved stub |

The ids and slugs match `concepts.yaml` exactly (16 entries, ids 1–16). Each entry also carries
`viewer_should_understand`, `must_show`, and `label_strategy` fields used by the quality gate.

## Render / judging tracking

Per concept × track. **Track B prompts are authored (v1) for all active concepts (#1–#15);**
renders are produced separately by the per-concept render-judge loop, and the Keep? column fills
once they land. `todo` = prompt ready, render pending; `VOID` = a prior keeper whose prompt has
since changed (must be re-rendered before re-judging).

> **⚠ Before running any Phase B render:** soften the engine PREAMBLE's hardcoded "still-water
> reflection" clause (in `seed/.claude/skills/diagrams/scripts/render-yoshida.py` and its
> byte-twin in `design-language.md`) — it fights the no-reflection rule in
> [`design-philosophy.md`](design-philosophy.md) §3 on every render. Separate commit + release
> tag (shipped file). See memory `preamble-reflection-fix`.

| # | Slug | Track | Rendered? | Keep? | Notes |
|---|------|-------|-----------|-------|-------|
| 1 | identity | B | rendered (c1–c4, glass-box cross-section) | KEEP c3 (+ label overlay) | c3 best fits the seed-store philosophy: cutaway with one glass-box loam source, four root-channels carrying in-render bidirectional arrows, varied plants (seedling/bamboo/tomato/gourd) in the foreground, calm Yoshida lake. Exact labels added as a vector overlay → `loam-hero-01-identity-c3-labeled.png` (gitignored). Taste captured in `design-philosophy.md` |
| 3 | context-routing | B | prior c1–c2 now stale | ~~KEEP c2~~ **VOID** | the track_b prompt was re-aligned to the glass-box/cutaway vocabulary (`design-philosophy.md` §3); the earlier c2 keeper no longer matches the prompt — re-render before re-judging |
| 2,4–15 | (all other active concepts) | B | todo | | track_b prompt authored (v1) + dry-run-verified; renders pending. Run the per-concept render-judge loop (5 candidates × ≥5 iters, judged vs `design-philosophy.md`) when ready |
| 1–15 | (all active concepts) | A | todo | | Track A (PaperBanana, manual human-in-browser) not run this round |
| 16 | reserved | A + B | — | — | intentional reserved stub; no track_b prompt |

When a parked concept is rendered, split it out of the summary row into its own per-track row
(same columns as the proof rows above) and record its result there.

## Naming convention

Renders are saved in `docs/diagrams/` as `loam-hero-<NN>-<slug>-c<idx>.png`
(e.g. `loam-hero-01-identity-c1.png`), where `<NN>` is the zero-padded concept id, `<slug>`
is the registry slug, and `c<idx>` is the candidate index.
