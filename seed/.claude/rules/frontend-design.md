---
paths:
  - "frontend/**"
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---

# Frontend Theme & Design Standards

> Loads when working on frontend/visualization code.
> Fill in your project's design system below.

## Aesthetic Direction

<!-- Define the visual direction for your project -->
"Clean, minimal, professional."

## Design Decisions

- **Theme:** Light — `#f9fafb` background, `#ffffff` card surfaces
- **Fonts:** System fonts or Inter (UI) + monospace for code/data
- **Spacing:** 8pt grid — all padding/margin/gap are multiples of 4 or 8
- **Charts:** Use a proper charting library (Chart.js, D3, etc.) — no fake HTML bars

## Frontend Generation Rules

When writing or editing HTML/CSS/JS:

1. **Use design tokens** — define colors/fonts in CSS custom properties (`var(--color-*)`)
2. **Real charts only** — use proper charting libraries with axes, tooltips, and legends
3. **Typography matters** — use appropriate font weights. Data values use monospace.
4. **Section comments** — wrap major sections in `<!-- === SECTION: Name === -->` for targeted editing
5. **No Tailwind CDN** — plain CSS with custom properties for single-file HTML pages
6. **Accessibility** — ARIA roles on interactive elements. No color-only status indication.
7. **Error handling** — if a page depends on external data, show a visible fallback on failure

## Verifying visual changes

For any change to a rendered page, close the loop with a visual check rather than asserting "looks done" (best-practices ["verify UI changes visually"](https://code.claude.com/docs/en/best-practices)):

1. **Screenshot-vs-design** — capture the rendered result (the `impeccable` skill's browser screenshotting, or a manual screenshot from a local preview) and compare it against the target design/mock; list the differences and fix them.
2. **Layout assertions** — run your project's layout/structure tests for deterministic checks.
3. **Show the evidence** — paste the before/after (or the diff), not just a "done."
