---
paths:
  - "visualizations/**"
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
