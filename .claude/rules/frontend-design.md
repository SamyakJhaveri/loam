---
paths:
  - "visualizations/**"
---

# Frontend Theme & Design Standards

> Full spec in `visualizations/DESIGN.md`. Reference it on every frontend task.

## Aesthetic Direction
"Clean, minimal, academic — like a Nature paper's online appendix."
Light theme throughout. Data-dense but not cluttered. Professional enough for SC26 reviewers.

## Design Decisions (locked)
- **Theme:** Light — `#f9fafb` background, `#ffffff` card surfaces
- **Fonts:** Inter (UI/labels) + JetBrains Mono (data values, code, hashes)
- **Charts:** Chart.js v4 (CDN, no build step) — never fake HTML div-width bars
- **Colors (charts):** Okabe-Ito colorblind-safe palette — see DESIGN.md for hex values
- **Spacing:** 8pt grid — all padding/margin/gap are multiples of 4 or 8
- **Mobile:** Desktop-only (research dashboard)
- **Print:** @media print stylesheet on all public pages (for paper figures)

## Frontend Generation Rules (anti-"AI slop")
When writing or editing any HTML/CSS/JS in visualizations/:

1. **Commit to the aesthetic** — dark backgrounds and purple gradients are banned. Use the DESIGN.md token values exactly.
2. **Use design tokens** — never hardcode hex values in components; always use `var(--color-*)` tokens defined in the `:root` block.
3. **Real charts only** — no `<div style="width:68%">` fake bars. Use Chart.js with proper axes, tooltips, and legends.
4. **Typography matters** — use Inter with appropriate weights (400/500/600/700). Data values and kernel names use JetBrains Mono. Max 4 font sizes per page.
5. **One shadow rule** — `box-shadow: 0 1px 3px hsl(220deg 40% 15% / 0.08), 0 4px 12px hsl(220deg 40% 15% / 0.08)` — layered, hue-matched, never `rgba(0,0,0,0.1)`.
6. **Section comments** — wrap every major section in `<!-- === SECTION: Name === -->` / `<!-- === END SECTION === -->` for targeted editing.
7. **Print stylesheet** — every public page must include `@media print { ... }` that hides nav, sets white bg, adjusts fonts for publication quality.
8. **No Tailwind CDN** — plain CSS with custom properties is the correct choice for single-file HTML pages.
9. **Accessibility** — ARIA roles on tabs (`role="tablist"`, `role="tab"`, `aria-selected`). No color-only status indication; add text labels.
10. **Error handling** — if a page depends on an external .js data file, show a visible fallback message if it fails to load; never silently show empty tables.
