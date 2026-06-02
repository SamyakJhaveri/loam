# Loam diagram design language

> On-demand reference for the `diagrams` skill. Documents Loam's two-track diagram design
> language: how to produce research-grade figures (Track A) and atmospheric hero art
> (Track B), with the canonical Yoshida preamble, label discipline, naming, and recipes.

## The two tracks (when to use each)

Loam splits diagram work into two tracks with different optimization targets and different
operating modes. Pick the track by what the artifact must do.

| | Track A — research-grade | Track B — Yoshida shin-hanga |
|---|---|---|
| Optimizes for | Legibility — labeled, academic figures | Atmosphere — luminous hero art |
| Tool | Self-hosted PaperBanana, pipeline mode via the browser Streamlit `demo.py` | Direct Gemini Image API (`gemini-3-pro-image`) |
| Mode | Manual, human-in-browser | Automated via `scripts/render-yoshida.py` |
| Use for | Figures that must carry exact labels, percentages, structure | Section banners, hero images, mood-setting plates |

- **Track A — research-grade.** Self-hosted PaperBanana, run in *pipeline mode through the
  browser Streamlit `demo.py`*. It optimizes for legibility: labeled, academic figures with
  text the figure must carry exactly. Track A is manual and human-in-browser. There is one
  supported render path (the browser), driven by a person reviewing each render.
- **Track B — Yoshida shin-hanga.** Direct Gemini Image API (`gemini-3-pro-image`) for
  atmospheric hero art in Hiroshi Yoshida's woodblock style. This track is automated through
  the [`scripts/render-yoshida.py`](scripts/render-yoshida.py) engine, which reads the concept
  registry, assembles the prompt, attaches local references, and writes PNG candidates.

The full prompt the engine sends is assembled as: this preamble + the concept's
`track_b.prompt` + `" Palette: " + palette + "."`. The `palette` field is **required** — the
engine hard-exits on a concept that lacks `track_b` or `palette` (it treats it as an
unauthored stub).

## The Yoshida preamble (canonical copy)

The prose preamble below is the canonical human-readable copy of the Track B style preamble.

> **Two copies of one string.** This is the canonical human-readable copy. The machine copy is
> the `PREAMBLE` constant in [`scripts/render-yoshida.py`](scripts/render-yoshida.py). The two
> must stay byte-identical — if you edit one, edit the other in the same commit. No automated
> test enforces this; it is manual discipline.

```
Japanese shin-hanga woodblock print: atmospheric and luminous, built from many layered transparent color impressions; a single harmonious tonal key per image; soft graded skies (bokashi) suggesting dawn, dusk, or mist; fine hand-carved directional linework; calm, centered, contemplative composition, often with a still-water reflection; matte, slightly grainy printed texture on fine paper; fresh, bright, inviting color; clear luminous daylight; soft even tonal transitions with a gentle contrast range. Wide 16:9 landscape banner. Use clean blank paper margins and let the composition communicate pictorially. Subject:
```

## Style principles

State these as positive descriptions — describe what to depict.

- **Single tonal key.** One harmonious tonal key carries the whole image.
- **Bokashi graded skies.** Soft graded skies suggesting dawn, dusk, or mist.
- **Layered transparent color.** Built from many layered transparent color impressions.
- **Fine carved linework.** Fine hand-carved directional linework.
- **Calm centered composition.** Calm, centered, contemplative framing, often with a
  still-water reflection.
- **Matte grainy print texture.** Matte, slightly grainy printed texture on fine paper.
- **Soft, even tonal transitions.** Soft, even tonal transitions held within a gentle
  contrast range.

## Label discipline

Yoshida prints carry almost no text. Track B keeps on-image text to at most two short words,
or none at all — quoted in the prompt, and cleanly lettered in a named simple serif (for
example, a quiet serif such as "EB Garamond" or "Spectral").

Label-heavy concepts get their labels from **Track A** (PaperBanana, which renders text
legibly) or from a vector overlay (`/diagrams drawio` or `/diagrams excalidraw`), never from
the stochastic image model. This follows the layer-triage principle: deterministic text
belongs in a deterministic layer, not the probabilistic image model. The image model is for
atmosphere; exact labels are a deterministic concern. See
[`.claude/rules/layer-triage.md`](../../rules/layer-triage.md) for the 60/30/10 framework that
makes this a routing rule rather than a preference.

## Quality gate

Every authored concept should define what a viewer must understand, what the image must show,
and how labels are routed. Use [`quality-gate.md`](quality-gate.md) as the reusable pass/fail
contract before writing prompts and before marking candidates as keep.

Every concept's prompt should depict the project's value proposition, not an incidental implementation detail; distinguish sibling concepts by the facet each isolates.

The concept registry fields are:

- `viewer_should_understand` — one plain-language sentence describing the intended takeaway.
- `must_show` — concrete visual evidence required in the render.
- `label_strategy` — one of `track-a`, `vector-overlay`, `label-light`, or `label-free`.

`render-yoshida.py` appends label-strategy-specific guidance to the prompt. `label-free` asks for
blank margins and pictorial communication, `label-light` allows one small decorative title,
`vector-overlay` reserves calm space for deterministic callouts, and `track-a` keeps the hero
image pictorial because exact labels belong in the separate Track A figure.

## Drop, don't adopt

Adopt only Yoshida's *pictorial* language. Drop the literal textual marginalia:

- **Drop** literal Japanese marginalia.
- **Drop** columnar date text.
- **Drop** the red `hanko` seal.

Reason: the image model renders literal glyphs as garbled, fake characters. Keep the
woodblock light, palette, composition, and texture; leave the writing to a deterministic
layer.

The live render prompt names the concrete shin-hanga traits instead of naming the artist.
Local reference images carry the Yoshida style signal; direct artist-name prompting made the
model more likely to copy signatures and seals into otherwise strong candidates.

## Positive-framing lint note

All prompts describe the desired result directly. Phrase every instruction as a positive
description of what to depict — say what is present, in plain affirmative language. The
concept registry's `track_b.prompt` field and this skill's `PREAMBLE` both follow this rule,
and these prompts are kept positively framed by manual discipline (no automated lint enforces it).

## Reference-image guidance

List at most six references per concept — that is the `gemini-3-pro-image` style-reference
ceiling, and [`scripts/render-yoshida.py`](scripts/render-yoshida.py) hard-fails rather than
silently truncate a longer list. The prose prompt ships in the registry and carries the style
on its own; local reference images (gitignored, for example under `yoshida_hiroshi/`) boost
fidelity when present and are skipped with a warning when absent.

## Track A recipe — the PaperBanana 3-field mapping

A PaperBanana pipeline-mode render takes three fields. Map your concept onto them:

- **Source Context** — the structure plus ALL text labels the figure must carry.
- **Figure Caption** — one sentence.
- **Visual Intent** — academic figure style; on-figure labels kept to ≤2-3 words each.

### Worked example — concept #4 (Layer triage 60/30/10)

- **Source Context** — A proportion split of deterministic 60% / rule-based 30% /
  probabilistic 10%, carrying those three labels with their percentages.
- **Figure Caption** — "The 60/30/10 budget heuristic: most work routes to deterministic
  tools, less to rule-based systems, and a small share to probabilistic reasoning."
- **Visual Intent** — A clean academic proportion or stacked-bar chart, matplotlib-style,
  with on-figure labels kept to ≤2-3 words each.

### Self-host steps

1. Clone PaperBanana **outside** this repo (keep the template clean).
2. `uv pip install -r requirements.txt`
3. Copy the model-config template the repo ships (path per its README) to a live config, and
   set the provider API key(s) it asks for (Gemini and/or OpenRouter).
4. `streamlit run demo.py`
5. Render via the browser, reviewing each result.
6. Save the PNG into `docs/diagrams/`.

## Ecosystem pointers

`dnvriend/gemini-nano-banana-tool` (Python) and `kingbootoshi/nano-banana-2-skill` (Bun/TS)
are alternatives a downstream project may prefer; Loam keeps its bespoke glue
([`scripts/render-yoshida.py`](scripts/render-yoshida.py)).

## Naming + output conventions

- Renders are named `loam-hero-<NN>-<slug>-c<idx>.png`, where `NN` is the zero-padded concept
  id and `idx` is the candidate index.
- All outputs go to `docs/diagrams/`.
- The concept registry is `docs/diagrams/concepts.yaml` (root = a YAML list).
- The copy-and-fill template is [`concepts.template.yaml`](concepts.template.yaml), beside
  this file.
