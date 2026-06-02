# Loam Diagram Design Philosophy (dynamically updated)

> **Repo-local, living document.** This is the single source of *taste and meaning* for Loam's
> diagrams — what Loam *is* conceptually, and how that must read visually. It distills the
> decisions made while art-directing the diagrams so that every concept's prompt in
> [`concepts.yaml`](concepts.yaml) can be updated consistently from one shared understanding.
>
> **Dynamically updated:** when a new art-direction decision is made, append it to the
> Decision Log (§6) and fold its rule into §1–§5. Treat this file as authoritative for *intent*;
> the generic, shippable rendering *method* lives in
> [`../../seed/.claude/skills/diagrams/design-language.md`](../../seed/.claude/skills/diagrams/design-language.md)
> (that file stays project-agnostic — Loam-specific taste belongs here).

---

## 1. The core mental model of Loam

- **Loam is one evolving seed-store** — a persistent hub/store, not a closed self-loop.
- **The seed = the user's Claude Code operation**: their workflow, setup, and infrastructure —
  skills, hooks, rules, slash commands. It is *not* a generic botanical seed.
- **Loam ports that seed OUT to many projects, and grows richer from what each sends BACK.**
  Improvements return via `promote` / `copier update`, so the store *accumulates* over time.
- **Projects are the plants.** The seed is *standardized*; the projects it grows are *varied kinds*.
  One standardized seed → many different kinds of project. This is harness engineering / harness
  porting: the same Claude Code harness, ported out to seed every project.
- **The relationship is bidirectional and cross-project**: out (copy) and back (promote, enriched).

## 2. What Loam is NOT (rejected framings)

- **Not an ouroboros / self-eating loop.** That depicts the `.claude → seed/.claude` symlink
  dogfood detail — an implementation mechanic, a lonely closed loop — not the value proposition.
- **Not the symlink mechanic** of "the repo runs on its own output."
- **Not a generic seed**, and **not a single project** (that conflates `identity` with `lifecycle`).

## 3. Visual taste & rules (Track B hero art)

Crystallized from the art-direction sessions:

- **The source is a glass box.** Depict loam's seed-store as a clear **rectangular glass box** —
  a cuboid case with flat upright faces and softly rounded edges/corners — holding the glowing
  seeds *inside* it. **Not** a dirt pile; **not** a rounded pot / jar / bowl.
- **Cross-section / cutaway.** Show **above ground and below ground** at once. Loam seeds each plant
  **at its roots, underground** — seeds travel through the soil to the root-ball, *not* showered
  on top of the plants.
- **One source, N channels.** Exactly **one** central loam box; **one channel per plant**
  (N plants → N channels). For the identity hero: 4 plants → 4 channels.
- **Directional flow, rendered in-image.** Each channel carries **bidirectional arrows** (rendered
  by the model, pictorially) showing seeds flowing *out* to the roots and *back* to the box. The
  returning seeds are the enrichment — the store ends up holding more.
- **Variety of plants = variety of project kinds.** Use distinct plant *kinds* (seedling, bamboo,
  fruiting tomato, gourd) to show one standardized seed growing different *kinds* of project.
  All plants sit in the **foreground**, spread out — none in the background.
- **Yoshida shin-hanga, per the reference images.** Atmospheric woodblock; include the calm
  **lake / water + soft layered hills** background. Adhere to the local `yoshida_hiroshi/`
  references. Aim **fresh, not washed/worn**, but stay inside the Yoshida idiom — do *not*
  over-saturate into a non-Yoshida brightness, and do *not* drift into a flat "textbook" look
  (structural clarity — the cutaway, the channels — is welcome; clip-art flatness is not).

## 4. Labeling

- **Exact text is never trusted to the image model** — it garbles lettering. Labels go on a
  **vector overlay** (composited after rendering) or on **Track A** (the `loam-identity.drawio`
  figure). Pictorial *flow arrows* may be rendered in-image; exact *words* may not.
- **Canonical labels** (identity concept):
  - source box → `loam = your Claude Code setup (skills · hooks · rules · commands)`
  - each plant → `project`
  - title → `IDENTITY · the living seed-store`
  - *Track A split:* the [`loam-identity.drawio`](loam-identity.drawio) figure splits this — a
    container labelled `loam (seed-store)` holds a box labelled
    `seed = your Claude Code setup (skills · hooks · rules · commands)` (container = the store,
    contents = the seed). Keep these in sync with the canonical labels above.
- **Why `label-free`, not `vector-overlay`:** the identity render uses `label_strategy: label-free`
  (the model is asked for blank margins) and the labels are composited as a **post-render vector
  overlay** — equivalent in effect to `vector-overlay`, but it feeds the model cleaner blank-margin
  input than reserving in-image label space would.
- **Overlay placement rules:** every plant tag **hovers precisely over its plant** (x-centered on
  the plant); **no text overlaps any other text** (audit box rectangles before saving).

## 5. How to write a `track_b.prompt` consistently

Apply this checklist to every concept (and especially wherever Loam-as-a-system appears):

1. Positive framing only; **subject-only** (no style boilerplate — the `PREAMBLE` supplies the
   Yoshida style); **≤ 6 refs**; **no artist name**; no literal marginalia / date column / red seal.
2. If Loam itself appears: show the **glass-box store + outward reach + return/accumulation**.
3. Distinguish sibling concepts by the **facet each isolates**:
   `identity` = the whole system, out *and* back; `fan-out` = outward only; `lifecycle` = one
   project over time.
4. Prefer the **cutaway / cross-section + root-channel** vocabulary wherever the *seeding mechanic*
   matters.
5. Reuse the **seedling / bamboo / fruiting tomato / gourd** vocabulary to express multiplicity of
   project *kinds*.
6. Keep the **lake + layered hills** background and the **luminous garden** palette family for
   Loam-system scenes.

## 6. Decision Log

> Append new decisions here (newest at the bottom). Each entry: date, the decision, and its source.

### 2026-06-02 — identity hero, art-direction sessions

1. **Reframe.** Identity moves from the ouroboros (self-eating loop = symlink dogfood detail) to the
   **seed-store** model: one store ports the workflow out to many projects and grows richer from
   each. (Plan `2026-06-01-identity-concept-realign-reviewed.md`, decisions table.)
2. **Render in Phase A**, with the user gating each paid render.
3. **Round-1 critique** (first seed-store render): remove the water reflection; brighter/fresher,
   not washed/worn; plants spread across the foreground (none in background); add arrows + clear
   seed trajectories; outbound seeds plain, **returning seeds glowing**; add labels
   (seed = Claude workflows/setups/infrastructure; plants = projects); the *variety* of plants
   shows a standardized seed growing **various kinds** of project (harness porting). Chose **both
   tracks** (Track B atmosphere + Track A labels).
4. **Round-2 critique:** keep the tall **bamboo** + big fruitful **tomato**; only **one** loam
   (not multiple seed piles); switch to a **cross-section** view where loam seeds the plants at
   their **roots underground**, not on top; bring back the **lake** (liked c4's lake); **more
   Yoshida, less textbook** (adhere to the reference images); arrows for seed direction; exactly
   **4 channels** for 4 plants; add labels.
5. **Round-3** (cross-section render): chose the c1 composition; the loam source must be a **glass
   box with curved edges** — *not* a pot, *not* a pile; **bidirectional arrows at the channel
   ends**; labels via overlay.
6. **Round-4** (glass-box render): preferred the **c3** serene-lake composition; reiterated **glass
   box, not a rounded pot**; **arrows must be rendered in the image** by the model (not overlaid);
   overlaid **labels are fine**.
7. **Overlay refinement:** each `project` tag must **hover precisely over its plant**; **no text
   may overlap other text**.

## 7. How to use this file

- This is the **taste reference for updating all concept prompts** in `concepts.yaml` (the Phase B
  re-alignment of the other concepts). Read §1–§5 before editing any `track_b.prompt`. Phase B
  re-aligns all 15 non-identity concepts — **including #3 (context-routing) and #4 (layer-triage),
  whose existing renders go stale** and must be re-authored and re-rendered; follow the plan's
  Phase B section for the per-concept loop.
- When a new art-direction decision lands, **append to §6** and update the affected rule in §1–§5.
- Keep it consistent with its siblings:
  - [`concepts.yaml`](concepts.yaml) — the actual prompts (source of truth for prompt text).
  - [`loam-hero-prompts.md`](loam-hero-prompts.md) — the render/keeper dashboard.
  - [`../../seed/.claude/skills/diagrams/design-language.md`](../../seed/.claude/skills/diagrams/design-language.md)
    — the **generic, shippable** rendering method (keep project-specific taste *out* of it; it lives here).
