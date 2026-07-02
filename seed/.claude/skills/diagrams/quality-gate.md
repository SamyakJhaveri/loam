# Diagram quality gate

> Reusable gate for diagram concepts and rendered candidates. Use this before writing prompts,
> before accepting generated images, and before marking dashboard rows as keep.

## Concept contract

Every non-stub concept should carry explicit acceptance criteria in its registry entry:

```yaml
viewer_should_understand: "A viewer who sees this image should understand the core idea."
must_show:
  - "one visible requirement"
  - "another visible requirement"
label_strategy: "track-a | vector-overlay | label-light | label-free"
```

- `viewer_should_understand` is the plain-language pass/fail sentence.
- `must_show` lists concrete visual evidence the render must contain.
- `label_strategy` routes exact text to the right layer:
  - `track-a` for labeled academic figures, charts, and exact percentages.
  - `vector-overlay` for deterministic labels/callouts over generated art.
  - `label-light` for Track B art with at most two short words.
  - `label-free` for Track B art that communicates by composition alone.

If the prompt cannot make the viewer sentence true, rewrite the concept before rendering.

## Candidate critique

After each render, judge the PNG against this rubric before marking it as keep:

1. **Concept clarity.** The image visibly communicates `viewer_should_understand`.
2. **Required evidence.** Each `must_show` item is visible enough to point at.
3. **Taste and coherence.** The image feels like one intentional composition.
4. **Palette.** The image is bright, inviting, luminous, and visually clear.
5. **Label strategy.** Exact labels are deterministic when they matter.

Re-roll failed candidates up to the session's candidate budget. Do not mark a candidate as keep
just because a render file exists.

## Track B text rule

Gemini should not be responsible for exact labels. Track B text is optional and decorative at
most; exact labels belong in Track A or a deterministic vector overlay. This follows layer
triage: deterministic text belongs in a deterministic layer, while the image model supplies
atmosphere and visual metaphor.

## Project-specific checks

Project-specific acceptance rules belong in that project's concept registry. Put them in
`viewer_should_understand` and `must_show`, then judge candidates against those fields.
