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

The full method (preamble assembly, palettes, reference handling) lives in the design-language
spec; this dashboard stays a thin index and points there for detail.

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
- **Concept registry (source of truth for all prompts):** [`concepts.yaml`](concepts.yaml) (sibling file)

**Verbatim prompts live in `concepts.yaml` — the single source.** They are NOT duplicated here.
This dashboard names concepts and tracks; the registry holds the exact prompt text per concept.

## Catalog (16 concepts)

The shared design vocabulary. Each concept can be expressed on both tracks. Only the proof
concepts are authored this round — **#1 and #3 on Track B (Gemini) and #4 on Track A
(PaperBanana)**; every other entry is a stub, filled during iteration.

| # | Concept | Track A — research figure | Track B — Yoshida hero | Authored this round? |
|---|---------|---------------------------|------------------------|----------------------|
| 1 | Identity (grows itself) | template ⊕ project; .claude→seed/.claude symlink | ouroboros vine, fruit→seed | Yes — Track B proof |
| 2 | Lifecycle (seed exchange, 4-beat) | drop→expand-to-fill→upgrade-in-place→sync-back | seed in crate ⇄ "New Project" bed | stub |
| 3 | Context routing (L0/L1/L2) | 3 load layers + token budgets | 3 soil strata + "gate" ring | Yes — Track B proof |
| 4 | Layer triage (60/30/10) | deterministic/rule/probabilistic split (proportion chart) | root mass in 3 unequal zones | Yes — Track A proof |
| 5 | Workflow (6 stages) | Orient→…→Verify (gate = #10) | seasonal tending cycle on a ring | stub |
| 6 | Repo anatomy (garden map) | labeled tree: seed/ soil/ cultivation/ docs/ bin/ | terrarium cross-section | stub |
| 7 | Fan-out (one→many) | one template → N projects | one seed → many seedlings | stub |
| 8 | Cultivation (greenhouse) | wip→marketplace→retired staging | nursery with seedling trays | stub |
| 9 | Flavors (cultivars) | research overlay graft | seed-variety chart / grafted plant | stub |
| 10 | Validation (three sieves) | 3-wave gate (Det/Rule/Prob) | harvest sieved at a garden gate | stub |
| 11 | Soil (knowledge base) | jvc/foundation/playbooks sources | living-soil cross-section | stub |
| 12 | Memory (compost) | write→index→consolidate(dream)→prune | compost layer; seed vault | stub |
| 13 | Agent teams (pollination) | advisor(Opus)+worker(Sonnet) topology | bees pollinating | stub |
| 14 | Toolkit (the tools) | skills/hooks/agents/rules taxonomy | botanical key / toolshed | stub |
| 15 | Cover art (Track B only) | — | seed-packet · roots-as-circuitry | stub |
| 16 | Reserved | — | — | stub |

The ids and slugs match `concepts.yaml` exactly (16 entries, ids 1–16).

## Render / judging tracking

Per concept × track. The three proof concepts are this round's render targets; everything
else stays parked until its iteration. `todo` = queued for this round; `SKIPPED` = not run
this round. Renders are produced separately; the Keep? column fills once they land.

| # | Slug | Track | Rendered? | Keep? | Notes |
|---|------|-------|-----------|-------|-------|
| 1 | identity | B | rendered (c1, c2) | | sap-green ouroboros, still-water reflection; model added 2-word titles |
| 3 | context-routing | B | rendered (c1, c2) | | indigo strata + gate ring; c1 has a faux signature + seal (see design-language "drop hanko"), c2 is clean |
| 4 | layer-triage | A | todo | | proof target this round (manual PaperBanana, human-in-browser) |
| 1 | identity | A | SKIPPED | | not run this round |
| 3 | context-routing | A | SKIPPED | | not run this round |
| 4 | layer-triage | B | SKIPPED | | not run this round |
| 2,5–16 | (remaining concepts) | A + B | todo | | both tracks, filled during iteration |

When a parked concept is rendered, split it out of the summary row into its own per-track row
(same columns as the proof rows above) and record its result there.

## Naming convention

Renders are saved in `docs/diagrams/` as `loam-hero-<NN>-<slug>-c<idx>.png`
(e.g. `loam-hero-01-identity-c1.png`), where `<NN>` is the zero-padded concept id, `<slug>`
is the registry slug, and `c<idx>` is the candidate index.
