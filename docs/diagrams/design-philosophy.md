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

> **Provenance (so this file is auditable against the source).** Distilled from the
> identity art-direction work captured in session `1e5975fc-e1c7-423b-a92d-6daa6f1f039f`
> and its inputs:
> - **Your hand sketch** `IMG_9389.JPG` (repo root) — the origin mental model.
> - **Your own words** in `loam_scratchpad.md` — the conceptual brief and the image critique
>   (reproduced verbatim in §0).
> - **The reviewed plan** [`../plans/2026-06-01-identity-concept-realign-reviewed.md`](../plans/2026-06-01-identity-concept-realign-reviewed.md)
>   — the nine resolved decisions and the concept taxonomy.
>
> §7 maps every rule below back to the exact source line, so anyone can confirm this file
> reflects what *you* put into the image-creation process, not a paraphrase.

---

## 0. In your own words (the primary source)

Everything below is a distillation of these two passages. They are reproduced here, lightly
normalized for spelling (with light emphasis added and the occasional bracketed gloss for
direction), so the rules in §1–§5 can always be checked against intent.

### 0.1 The conceptual brief (`loam_scratchpad.md`, the "identity" brief)

> Some additional notes about the conceptual idea behind Loam, to help write better prompts:
>
> 1. **"Seed" evolves at every project, for all kinds of projects.** "Seed" is a metaphor for
>    the Claude Code operation — the user's engineering practices and workflow within Claude Code.
> 2. When working on any project, the user **adds a new skill, a workflow of their own, or new
>    project-specific tools** to their Claude Code operational workflow. The seed captures this
>    and puts it into their **"loam."**
> 3. **"Loam" lets users take their updated "seed" into the other projects** they're currently
>    working on and into future projects. The goal and intent behind Loam is to **solve the pain
>    point of having to manually "port" your workflow from one project to another.** Loam helps
>    port your Claude Code workflow — your slash commands, custom skills, hooks, and engineering
>    best practices.
> 4. **Loam already has one of the best-practice Claude Code setups**, based on my own
>    experiments and projects as a researcher of software engineering and AI. Start with the
>    "identity" image, and we shall then propagate these ideas through all the prompts.

### 0.2 The image critique that fixed the taste (`loam_scratchpad.md`, "describing loam and its philosophy")

> Keeper: **c3** (recommendation). Criticisms:
> - **Get rid of the reflection in the water** — it does not look good.
> - The colors are **muted** and the image seems **"washed."** Change that — the colors should be
>   **brighter**; the image should look **fresh and new, not washed and worn out.**
> - The plants should be **more spread out** so that **none of the plants are in the background —
>   they should all be in the foreground.**
> - Add **arrows and sharp, clear trajectories** for the seeds going from "loam" to the plants and
>   back. There should be an **intuitive understanding that the seeds start the plants and keep
>   coming back to loam, enriched.**
> - Seeds going **out** (loam → plants) should be **normal**; seeds coming **back** (plants → loam)
>   should be **glowing.**
> - Add **labels** for what the seed means — **Claude workflows, setups, and the user's
>   infrastructure for creating projects**; the **projects are the plants.**
> - The **variety of plants** was chosen to show that the seeds may look the **same and
>   standardized**, but they are capable of seeding **various kinds of projects.** This is
>   essentially **harness engineering and harness porting.**

### 0.3 The sketch (`IMG_9389.JPG`)

A labelled **"loam"** box (soft-cornered) holding a single **"seed"** on the left;
**bidirectional arrows** reaching out to a row of plants at different stages —
**"maturing plant," a bamboo, a fruit plant** — each annotated as a **"project"** at the
**"current time."** Margin notes restate the brief: the seed is standardized yet seeds varied
project kinds; this is harness porting. The soft-cornered box is the origin of the later
"glass box with curved edges" decision; the row of staged plants is the origin of the
"variety of plant kinds in the foreground" rule.

---

## 1. The core mental model of Loam

- **Loam is one evolving seed-store** — a persistent hub/store, not a closed self-loop.
- **The seed = your Claude Code operation**: your workflow, setup, and engineering practices —
  skills, hooks, rules, slash commands, project-specific tools. It is *not* a generic botanical
  seed. The seed **evolves at every project**: when you build a new skill/workflow/tool, the seed
  captures it.
- **Loam exists to kill one pain point: manual porting.** Without Loam you re-port your workflow
  from project to project by hand. Loam ports it for you — your slash commands, custom skills,
  hooks, and best practices travel automatically.
- **Loam ports that seed OUT to many projects, and grows richer from what each sends BACK.**
  Improvements return via `promote` / `copier update`, so the store *accumulates* over time.
- **Projects are the plants.** The seed is *standardized*; the projects it grows are *varied kinds*.
  One standardized seed → many different kinds of project. This is **harness engineering / harness
  porting**: the same Claude Code harness, ported out to seed every project.
- **The relationship is bidirectional and cross-project**: out (copy) and back (promote, enriched).
- **Loam is opinionated.** It already encodes a best-practice Claude Code setup drawn from the
  author's experiments as a researcher of software engineering and AI — so the imagery should feel
  *cultivated and abundant*, not tentative.

## 2. What Loam is NOT (rejected framings)

- **Not an ouroboros / self-eating loop.** That depicts the `.claude → seed/.claude` symlink
  dogfood detail — an implementation mechanic, a lonely closed loop — not the value proposition.
- **Not the symlink mechanic** of "the repo runs on its own output."
- **Not a generic seed**, and **not a single project** (that conflates `identity` with `lifecycle`).
- **Not seeds showered on top of the plants.** Loam seeds each plant *at its roots, underground*.

## 3. Visual taste & rules (Track B hero art)

Crystallized from the art-direction sessions. Each rule carries *why* (the rule is only useful if
the next prompt-author understands the intent, not just the instruction).

- **The source is a glass box.** Depict loam's seed-store as a clear **rectangular glass box** —
  a cuboid case with flat upright faces and softly rounded edges/corners — holding the glowing
  seeds *inside* it. **Not** a dirt pile; **not** a rounded pot / jar / bowl.
  *Why:* the store is a deliberate, engineered container (your standardized setup), not loose
  earth; the soft-cornered box in the sketch became the glass box.
- **Cross-section / cutaway.** Show **above ground and below ground** at once. Loam seeds each plant
  **at its roots, underground** — seeds travel through the soil to the root-ball, *not* showered
  on top of the plants. *Why:* the seed *originates* the plant; it feeds the roots, it is not
  fertilizer sprinkled on a finished plant.
- **One source, N channels.** Exactly **one** central loam box; **one channel per plant**
  (N plants → N channels). For the identity hero: 4 plants → 4 channels. *Why:* there is a single
  store, and each project draws from it on its own line.
- **Directional flow, rendered in-image.** Each channel carries **bidirectional arrows** (rendered
  by the model, pictorially) showing seeds flowing *out* to the roots and *back* to the box.
  **Outbound seeds are plain; returning seeds glow.** The returning glow *is* the enrichment — the
  store ends up holding visibly more. *Why:* this is the one rule that makes `identity` legible as
  give-and-replenish rather than one-way fan-out (and it is what your critique asked for most
  forcefully).
- **Variety of plants = variety of project kinds.** Use distinct plant *kinds* to show one
  standardized seed growing different *kinds* of project. (The specific four — **seedling, bamboo,
  fruiting tomato, gourd** — are an art-direction crystallization from the identity render; your
  verbatim source gives the *principle* (variety = project kinds) and the sketch's three kinds
  "maturing plant / bamboo / fruit plant" (§0.3) — the exact species are a rendering choice.)
  All plants sit in the **foreground**, spread out — **none in the background.**
  *Why:* the seed looks the same everywhere; the *projects* differ. Foreground spread says every
  project is first-class, none is secondary.
- **Fresh and bright, never washed.** Aim **fresh, not washed/worn**; brighter, clearer color;
  **no still-water reflection** (it muddied the image and read as tired). *Why:* Loam is alive and
  growing; a washed/worn palette reads as decay.
- **Yoshida shin-hanga, per the reference images.** Atmospheric woodblock; include the calm
  **lake / water + soft layered hills** background. Adhere to the local `yoshida_hiroshi/`
  references. Stay inside the Yoshida idiom — do *not* over-saturate into a non-Yoshida brightness,
  and do *not* drift into a flat "textbook" look (structural clarity — the cutaway, the channels —
  is welcome; clip-art flatness is not). *Why:* the mood is the brand; "fresh, not washed" is a
  move *within* shin-hanga, not away from it. (Note the tension: keep the calm lake and soft
  layered hills, but drop the literal mirror-reflection on the water that looked washed.)
- **The seed grows as it feeds (accumulation).** Along a *maturation or accumulation* progression
  — lifecycle's one plant over time, or identity's returning seeds — render the seed (and the
  seed-nodes travelling the channel) **increasing in size and glowing brightness** as they reach
  more mature plants. The seed is not a fixed pellet: it *swells and brightens* the further it has
  travelled. *Why:* the seed = your Claude Code setup, which gets **richer at every project**; a
  seed that visibly grows encodes that accumulation directly (the same enrichment the *returning*
  glow encodes for `identity`). This is the rule that won the lifecycle keeper — your words:
  "I like how the seed's size and glowing brightness increases as the plant evolves; the seed here
  also grows with every project (i.e. plant)." **Do NOT apply to `fan-out`:** its seeds are uniform
  and outward-only; a growing/brightening seed there would imply an enrichment that fan-out must
  never show (accumulation is identity's facet, not fan-out's).

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
2. If Loam itself appears: show the **glass-box store + outward reach + return/accumulation**, with
   **outbound seeds plain and returning seeds glowing.**
3. Distinguish sibling concepts by the **facet each isolates**:
   `identity` = the whole system, out *and* back; `fan-out` = outward only; `lifecycle` = one
   project over time.
4. Prefer the **cutaway / cross-section + root-channel** vocabulary wherever the *seeding mechanic*
   matters (seeds reach the plant at its roots, underground).
5. Reuse the **seedling / bamboo / fruiting tomato / gourd** vocabulary to express multiplicity of
   project *kinds*, all spread across the **foreground**.
6. Keep the **lake + layered hills** background and the **luminous, fresh (never washed)** garden
   palette family for Loam-system scenes.

## 6. Decision Log

> Append new decisions here (newest at the bottom). Each entry: date, the decision, and its source.

### 2026-06-02 — identity hero, art-direction sessions

1. **Reframe.** Identity moves from the ouroboros (self-eating loop = symlink dogfood detail) to the
   **seed-store** model: one store ports the workflow out to many projects and grows richer from
   each. (Plan `2026-06-01-identity-concept-realign-reviewed.md`, decisions table; sketch `IMG_9389.JPG`.)
2. **Render in Phase A**, with the user gating each paid render.
3. **Round-1 critique** (`loam_scratchpad.md` §0.2; keeper c3): remove the water reflection;
   brighter/fresher, not washed/worn; plants spread across the foreground (none in background);
   add arrows + clear seed trajectories; outbound seeds plain, **returning seeds glowing**; add
   labels (seed = Claude workflows/setups/infrastructure; plants = projects); the *variety* of
   plants shows a standardized seed growing **various kinds** of project (harness porting). Chose
   **both tracks** (Track B atmosphere + Track A labels).
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
7. **Overlay refinement** (this session, your live input): each `project` tag must **hover
   precisely over its plant**; **no text may overlap other text**.
8. **Outcome.** Phase A shipped: identity redefined to the seed-store/glass-box cutaway, c3 kept
   (`loam-hero-01-identity-c3-labeled.png`), `loam-identity.drawio` updated with promote-back
   arrows, one generic sentence added to the shipped `design-language.md`, registry header gained
   the 5 Loam design principles. Committed (`7d882800`) and released **v3.6.1** (`63db791c`).
   **Phase B — re-aligning all 15 other concepts' prompts — is NOT yet done.**

### 2026-06-03 — Phase B render loop begins (lifecycle keeper)

1. **Method change.** The autonomous self-critic loop was too strict to ever return "aligned," and
   its auto-rewrites drifted (it added a confusing second glass box to lifecycle). Switched to
   **"critic advises, you keep"**: render 5 once from the authored prompt, an Opus critic ranks +
   diagnoses (no auto-rewrite), and *you* pick the keeper at the per-concept gate. The authored
   prompts are the starting point; they are not edited unless you ask.
2. **New principle — the seed grows as it accumulates** (folded into §3, fidelity row in §7). Your
   first-round preference (c1/c3 over the critic's round-1 pick c4) turned on the seed-nodes visibly swelling and
   brightening as they reach more mature plants — encoding "the seed grows richer with every
   project." Apply on maturation/accumulation concepts only (not fan-out; see §3).
3. **Lifecycle keeper: c5** — re-rolled with the growing-seed rule written into the prompt (the
   2-box auto-drift was reverted first). c5 shows the seed swelling + brightening from a dim
   pinpoint at the box to a large radiant bulb returning at the right. Recorded in
   `loam-hero-prompts.md`.
4. **Context-routing keeper: c2** — user kept a round glass dispatch basin (an accepted deviation
   from the cuboid glass-box vocabulary for this concept); its blank label bands suit its
   `vector-overlay` strategy.
5. **Layer-triage reframed + kept (c3, cropped).** Confirmed against source that layer-triage =
   the **60/30/10 work-split** (deterministic 60% / rule-based 30% / AI 10%;
   `soil/jvc/constraints/06-layer-triage.md:52`), NOT context-attention routing — a Google
   AI-overview had conflated it with ICM Layer-1 routing, which is really concept #3
   (context-routing). At the user's direction this concept **drops the atmospheric lake/hills hero
   for an UP-CLOSE botanical xylem/phloem cross-section**: golden sap apportioned across three
   unequal vessel-clusters (~6/3/1) — large central core (deterministic) / side cluster (rule) / a
   few fine vessels to one small glowing bud (AI). The up-close framing was achieved by forceful
   "fill the frame, no sky/horizon/water" language overriding the byte-locked Yoshida PREAMBLE
   (so: a concept MAY drop the atmosphere when its meaning needs a close-up). **Reproducibility
   caveat:** because the prompt fights the PREAMBLE's wide-banner / blank-margins / water framing,
   layer-triage is NOT cleanly reproducible from `concepts.yaml` alone — the keeper needed a manual
   border crop (kept as `loam-hero-04-layer-triage-c3-cropped.png`), and a future re-render must
   expect to crop the keyline again. A proper fix would be a per-concept PREAMBLE override in the
   engine (out of scope here).
6. **Recurring artifact — reference-print seals (FIXED at the source).** The Yoshida reference
   prints carry signatures + red seals, and the model kept copying them into renders (seen on
   lifecycle, context-routing, layer-triage candidates). Fixed at the source: the clause
   "no seal, stamp, signature, date column, lettering, or ruled border anywhere" was folded into
   the Yoshida **PREAMBLE itself** — both byte-twins (`scripts/render-yoshida.py` and the prose
   copy in `design-language.md`), kept byte-identical — so every concept inherits the guard. The
   redundant per-prompt guard tails were then removed from the four prompts that had them
   (layer-triage, workflow, repo-anatomy, fan-out), keeping `track_b.prompt` positive-framed.
   NOTE: this edits `seed/` (shipped), so the next release needs a tag (Copier resolves from tags).

### 2026-06-03 (later) — Phase B render loop completes (#7–#15)

1. **Phase B done.** #7–#15 rendered (5 candidates each) and kept: fan-out c1, cultivation c4,
   flavors c1, validation c3, soil c3, memory c1, agent-teams c1, toolkit c5, cover-art c5. All 15
   active concepts now carry `status.track_b: keep`.
2. **Diagnosis — subject-prompt density, not the preamble, governs Yoshida craft.** A held-aside A/B
   worktree (the parked Yoshida experiment) showed two renders sharing the *same* preamble could be
   richly atmospheric or flatly "textbook" purely by their *subject-prompt* style: short, scene-led
   prompts let the woodblock craft flourish; long, schema-dense prompts ("arranged like a routing
   diagram", "so it reads clearly") pull toward infographic flatness. The worktree was kept only as a
   visual-fidelity reference; its renders are superseded by the main line.
3. **Tic-trim (repo-local).** Removed the "so it reads clearly / at a glance / read in clear order"
   legibility tics from #7–#15 `track_b.prompt` (reinforces §3 "more Yoshida, less textbook"),
   keeping each composition and its refs intact.
4. **Narrow preamble contrast edit (shipped).** "soft even tonal transitions with a gentle contrast
   range" → "…with a fresh, clear contrast range within the Yoshida idiom", in BOTH byte-twins
   (`scripts/render-yoshida.py`, `design-language.md`). Serves §3 "fresh, not washed". NOTE: edits
   `seed/` → the next release needs a tag.
5. **Brightness push (repo-local).** Per your repeated "colours brighter" direction (§0.2), brightness
   was added at the per-concept prompt opening ("painted in bright, vivid, freshly-printed colour")
   and palette level for #7–#15 — deliberately NOT in the shipped preamble (the A/B proved the
   preamble is not the craft differentiator, and keeping it repo-local avoids imposing loam's
   brightness taste on every bootstrapped project).
6. **fan-out art-direction (your live input on #7).** Three corrections folded into its prompt:
   (a) brighter colour; (b) **varied plant KINDS** — bamboo, oak sapling, mint, fruiting tomato,
   gourd vine — not uniform seedlings (reinforces §3 "variety of plants = variety of project kinds";
   fan-out is the one→many facet, so it shows the most kinds); (c) seed channels kept in clean,
   evenly-spaced, non-overlapping lanes.
7. **Recurring artifact — fake lettering/seals (mitigated by selection).** The seal-guard PREAMBLE
   clause largely held, but fake Japanese lettering still bled into fan-out c4 and memory c5, and a
   garbled-shape artifact into toolkit c2; all three were disqualified at the gate. The kept set is
   clean. Small ≤2-word English margin titles (within `label-light`) are cropped/overlaid at finishing.

### 2026-06-03 (later still) — reserved slot #16 authored as `plan-review`

1. **#16 authored.** The deliberately-reserved #16 slot was authored as a real concept,
   `plan-review` ("Plan-first review (the pruning bench)"), at the user's direction. Facet:
   **adversarial scrutiny BEFORE growth** — Loam plans first and stress-tests the plan
   (the plan-reviewer's checklist + Elegance Gate + the critique team) before any implementation.
2. **Metaphor.** An open-air inspection/pruning bench where gardeners examine a tray of young
   seedlings, prune the weak, mark the strong, and carry only the approved ones to a prepared empty
   bed — all the scrutiny happens *before* anything is planted.
3. **Distinctness held.** Kept clear of `#10 validation` (sieves at the harvest/output gate) and
   `#5 workflow` (the whole 6-stage path): plan-review is input-side selection, before planting. No
   glowing return loop (that is `identity`'s facet only). `track_b: todo` — authored, render pending;
   the render is a separate user-gated paid step. No §1–§5 rule change (a new concept, not a new
   visual rule), so no §7 row.

## 7. Fidelity check — rule ↔ source (so this file matches what you said)

| Rule (§) | Your source | Anchor |
|---|---|---|
| Seed = your Claude Code operation, not botanical (§1) | brief pt. 1–2 | §0.1 |
| Exists to kill manual porting (§1) | brief pt. 3 | §0.1 |
| One standardized seed → varied project kinds = harness porting (§1, §3) | brief pt. 1 + critique | §0.1 / §0.2 |
| Opinionated / best-practice setup (§1) | brief pt. 4 | §0.1 |
| Glass box, not pot/pile (§3) | sketch soft box → Rounds 3–4 | §0.3 / §6.5–6 |
| Cutaway, seeds reach roots underground (§3) | Round-2 critique | §6.4 |
| One source, N channels; 4 plants → 4 channels (§3) | Round-2 critique | §6.4 |
| Bidirectional arrows; **returning seeds glow** = enrichment (§3) | critique | §0.2 / §6.3 |
| Plants spread, all foreground, varied kinds (§3) | critique | §0.2 |
| Fresh & bright, no washed reflection (§3) | critique | §0.2 |
| Yoshida lake + layered hills (§3) | Round-2 critique ("bring back the lake") | §6.4 |
| Labels via overlay/Track A, never the model (§4) | critique ("add labels") + label discipline | §0.2 |
| Tags hover over their plant; no text overlap (§4) | this session, live | §6.7 |
| Seed grows in size + glow as it accumulates (§3) | lifecycle keeper pick, your verbatim words | §6 (2026-06-03) |
| Brighter colour, fresh not washed — pushed per-concept (§3) | your repeated critique | §0.2 / §6 (2026-06-03 later) |
| More Yoshida, less textbook — legibility tics trimmed (§3) | §3 rule + this round | §6 (2026-06-03 later) |
| fan-out = varied plant kinds, outward only (§1, §3) | your live #7 critique | §6 (2026-06-03 later) |

If a future change can't be traced to a row here, add the row (and the source) before folding the
rule into §1–§5 — that keeps the file honest to *your* intent.

## 8. How to use this file

- This is the **taste reference for updating all concept prompts** in `concepts.yaml` (the Phase B
  re-alignment of the other concepts). Read §0–§5 before editing any `track_b.prompt`. Phase B
  re-aligns all 15 non-identity concepts — **including #3 (context-routing) and #4 (layer-triage),
  whose existing renders/prompts go stale** and must be re-authored; follow the plan's Phase B
  section for the per-concept loop.
- When a new art-direction decision lands, **append to §6**, add a **§7 fidelity row**, and update
  the affected rule in §1–§5.
- Keep it consistent with its siblings:
  - [`concepts.yaml`](concepts.yaml) — the actual prompts (source of truth for prompt text).
  - [`loam-hero-prompts.md`](loam-hero-prompts.md) — the render/keeper dashboard.
  - [`../../seed/.claude/skills/diagrams/design-language.md`](../../seed/.claude/skills/diagrams/design-language.md)
    — the **generic, shippable** rendering method (keep project-specific taste *out* of it; it lives here).
