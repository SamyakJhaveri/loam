# Artifact format

A self-contained `.html` file. Not styling advice — three structural rules, each of which
Markdown cannot satisfy.

## 1. The prompt sits at the top, the output below it

The artifact is a prompt/output pair, so it is self-documenting and re-runnable. Thariq's
index says it plainly: *"Each page shows the exact prompt at the top and the artifact Claude
produced below it: paste the prompt, get something like the page."*

Anyone opening it six weeks later can see what was asked, not just what was produced.

## 2. It ends by writing the reader's reply for them

This is the reusable idea, and the easiest one to miss. Across Thariq's eleven artifacts the
recurring device is not the visuals — it is that reacting to the artifact *produces a
pasteable message*:

- **steal/skip chips** on each design direction
- **resonate checkboxes** on each brainstormed intervention
- a **self-filling reply template** under the mock
- a decisions table plus a **ready-to-paste implementation prompt** after the interview

The reader's job is to react. Composing the response is the artifact's job. If the reader
still has to write a paragraph explaining which option they picked, the artifact is
unfinished.

## 3. Structure carries meaning that prose cannot

Use the layout to say something: a 2x2 rendered as a grid rather than four bullets; filter
pills with live counts; a card grid where the filename is the affordance; ordering by blast
radius or by likelihood-of-change rather than by execution order; a quiz whose wrong answers
link back to the exact section that was skimmed.

## Practical constraints

- **Self-contained.** Inline the CSS and JS, embed images as data URIs. No CDN, no external
  fonts. It must open from `file://` with no network.
- **Both themes.** Support `prefers-color-scheme` — these get read at night.
- **Wide content scrolls inside its own container**, never the page body.
- **Write it where the work is.** Local file for anything touching unpublished research;
  publish only what is meant to leave the project.

## When NOT to use one

A one-line answer, a diff, or a command. The artifact earns its cost when the reader has to
*choose between options*, *absorb structure*, or *verify they understood something*. Building
one to deliver a fact is the same over-production the skill warns about elsewhere.
