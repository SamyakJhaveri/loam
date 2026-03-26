---

# ParBench Visualization Design Spec

> Canonical design reference for all pages in `visualizations/`. Reference this in every frontend prompt.
> Aesthetic: "Clean, minimal, academic — like a Nature paper's online appendix."

## Theme

**Light** throughout. No dark backgrounds on public pages. SC26 reviewers and paper readers expect academic styling.

```
Background:    #F5F0EB   (Warm Linen — outfit-derived SC'26 palette)
Surface:       #ffffff   (cards, panels, table rows)
Surface-alt:   #F0E6D0   (Cream Ivory — alternating rows, subtle sections)
Border:        #e5e7eb   (card borders, table dividers)
Border-strong: #B8976A   (Zari Gold — section dividers, tab borders)
Text:          #2D3436   (Charcoal — primary body text)
Text-secondary:#636e72   (Slate — labels, captions)
Text-muted:    #9ca3af   (gray-400 — decorative only; never for meaningful text)
Accent:        #1B6573   (Deep Teal — links, focus rings, active states)
Accent-light:  #D8F0F4   (Lightest Teal — accent backgrounds)
```

## Typography

```
Font UI:   'Inter', system-ui, -apple-system, sans-serif
Font Data: 'JetBrains Mono', 'Fira Code', monospace   ← kernel names, percentages, hashes, code

Google Fonts import:
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Type Scale
```
Page title:    24px / 700 / Inter / line-height 1.2
Section title: 18px / 600 / Inter / line-height 1.3
Card label:    12px / 500 / Inter / 0.06em letter-spacing / uppercase
Primary value: 32px / 700 / JetBrains Mono / tabular-nums
Table data:    13px / 400 / JetBrains Mono
Body:          14px / 400 / Inter / line-height 1.6
Caption:       12px / 400 / Inter / text-muted color
```

## Color Tokens (CSS Custom Properties)

```css
:root {
  /* === SURFACES (Outfit-derived SC'26 palette) === */
  --bg:              #F5F0EB;    /* Warm Linen */
  --surface:         #ffffff;
  --surface-alt:     #F0E6D0;    /* Cream Ivory */
  --border:          #e5e7eb;
  --border-strong:   #B8976A;    /* Zari Gold */

  /* === TEXT === */
  --text:            #2D3436;    /* Charcoal */
  --text-secondary:  #636e72;    /* Slate */
  --text-muted:      #9ca3af;
  --accent:          #1B6573;    /* Deep Teal */
  --accent-light:    #D8F0F4;    /* Lightest Teal */

  /* === STATUS (Outfit-derived SC'26 palette) === */
  --pass-color:      #2E8E9E;   /* Teal */
  --pass-bg:         #D8F0F4;
  --pass-text:       #1B6573;

  --build-fail-color:#C8607A;   /* Rose Pink */
  --build-fail-bg:   #F8E0E5;
  --build-fail-text: #6E3244;

  --run-fail-color:  #D48A35;   /* Saffron Amber */
  --run-fail-bg:     #FBF0DD;
  --run-fail-text:   #75491B;

  --verify-fail-color: #E6A84D; /* Gold */
  --verify-fail-bg:  #FDF5E3;
  --verify-fail-text:#7A5928;

  --neutral-color:   #636e72;   /* Slate */
  --neutral-bg:      #f1f5f9;
  --neutral-text:    #2D3436;   /* Charcoal */

  /* === TEAM MEMBERS (sprint dashboard) === */
  --team-samyak:     #C8607A;   /* Rose Pink */
  --team-erel:       #D48A35;   /* Saffron Amber */
  --team-gal:        #2E8E9E;   /* Teal */
  --team-niranjan:   #E6A84D;   /* Gold */
  --team-claude:     #1B6573;   /* Deep Teal */

  /* === SPACING (8pt grid) === */
  --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px; --sp-4: 16px;
  --sp-5: 20px; --sp-6: 24px; --sp-8: 32px; --sp-10: 40px;
  --sp-12: 48px; --sp-16: 64px;

  /* === RADIUS === */
  --r-xs: 2px; --r-sm: 4px; --r-md: 8px; --r-lg: 12px; --r-full: 9999px;

  /* === SHADOWS (hue-matched, layered — never rgba(0,0,0,...)) === */
  --sh-color: 220deg 40% 15%;
  --shadow-sm:  0 1px 2px hsl(var(--sh-color) / 0.06);
  --shadow-md:  0 1px 3px hsl(var(--sh-color) / 0.07),
                0 4px 12px hsl(var(--sh-color) / 0.07);
  --shadow-lg:  0 2px 4px  hsl(var(--sh-color) / 0.05),
                0 4px 8px  hsl(var(--sh-color) / 0.05),
                0 8px 24px hsl(var(--sh-color) / 0.08);

  /* === CHART COLORS (Outfit-derived SC'26 palette) === */
  --chart-pass:         #2E8E9E;
  --chart-build-fail:   #C8607A;
  --chart-run-fail:     #D48A35;
  --chart-verify-fail:  #E6A84D;
  --chart-neutral:      #636e72;
  --chart-l0:           #1B6573;
  --chart-l1:           #2E8E9E;
  --chart-l2:           #7CC3CE;
  --chart-l3:           #D8F0F4;
  --chart-l4:           #F0E6D0;
}
```

## Chart Library

**Chart.js v4** via CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### Chart Type → Use Case Mapping
| Use Case | Chart Type | Notes |
|----------|-----------|-------|
| Per-kernel pass/fail breakdown | Horizontal stacked 100% bar | PASS left-anchored, then BUILD_FAIL, RUN_FAIL, VERIFY_FAIL |
| Model comparison | Sortable HTML table + horizontal grouped bar | Table is primary; chart is supplementary |
| Model × kernel overview | CSS-grid heatmap (plain JS) | 2×10 cells colored by status; no Chart.js needed |
| Augmentation level trends | Grouped horizontal bar | 5 bars per kernel (L0–L4), sequential blue palette |
| Per-model summary | Doughnut chart | Only for single-model summary widget; ≤4 slices |

### Chart.js Global Defaults
Set these once per page before any chart initialization:
```javascript
Chart.defaults.font.family = "'JetBrains Mono', monospace";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#636e72';
Chart.defaults.borderColor = '#e5e7eb';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = '#2D3436';
Chart.defaults.plugins.tooltip.titleColor = '#F5F0EB';
Chart.defaults.plugins.tooltip.bodyColor = '#B8976A';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 6;
```

## Card Component

```css
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);   /* 12px */
  padding: var(--sp-6);         /* 24px */
  box-shadow: var(--shadow-md);
}
.card:hover {
  box-shadow: var(--shadow-lg);
  transition: box-shadow 150ms ease;
}
```

## Status Badge

```css
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; font-weight: 500; line-height: 20px;
  border-radius: var(--r-full);
  white-space: nowrap;
}
.badge-pass         { background: var(--pass-bg);         color: var(--pass-text); }
.badge-build-fail   { background: var(--build-fail-bg);   color: var(--build-fail-text); }
.badge-run-fail     { background: var(--run-fail-bg);     color: var(--run-fail-text); }
.badge-verify-fail  { background: var(--verify-fail-bg);  color: var(--verify-fail-text); }
.badge-neutral      { background: var(--neutral-bg);      color: var(--neutral-text); }
```

## Navigation

Shared top navigation across all pages. Active page uses `var(--accent)` text and a 2px bottom border.

```html
<nav class="site-nav">
  <a href="overview.html" class="nav-brand">ParBench</a>
  <div class="nav-links">
    <a href="overview.html">Overview</a>
    <a href="benchmark_landscape.html">Benchmarks</a>
    <a href="pipeline.html">Pipeline</a>
    <a href="llm_evaluation.html" class="active">LLM Evaluation</a>
    <a href="sprint_dashboard.html">Sprint</a>
  </div>
</nav>
```

## Print Stylesheet

Every public-facing page must include:
```css
@media print {
  .site-nav, .no-print { display: none !important; }
  body { background: white; color: black; font-size: 11pt; }
  .card { box-shadow: none; border: 1px solid #ccc; }
  canvas { max-width: 100% !important; }
  h1, h2, h3 { page-break-after: avoid; }
  table { page-break-inside: avoid; }
}
```

## File Structure Conventions

```
visualizations/
  DESIGN.md            ← this file (always read before any frontend work)
  theme.css            ← shared CSS custom properties (future: extract from inline)
  eval_results_data.js ← auto-generated by analyze_eval.py — do not edit manually
  results_data.js      ← auto-generated
  build_results_data.js← auto-generated
  *.html               ← one file per page; inline <style> + <script> only
```

## Anti-Patterns (never do these)

- `box-shadow: 2px 2px 5px rgba(0,0,0,0.1)` — use hue-matched layered shadows
- `<div style="width:68%">` for charts — use Chart.js
- Hardcoded dates, model names, or counts in HTML — derive from data files or JS constants
- `innerHTML +=` in a loop — use array + single `innerHTML` assignment
- Mixing 3+ font families — Inter + JetBrains Mono only
- Color-only status indicators — always pair color with text label
- `font-size: 10px` or below — minimum 11px for any visible text

---

*Last updated: 2026-03-26. Update this file whenever design decisions change.*
