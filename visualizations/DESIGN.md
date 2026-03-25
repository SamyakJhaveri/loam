---

# ParBench Visualization Design Spec

> Canonical design reference for all pages in `visualizations/`. Reference this in every frontend prompt.
> Aesthetic: "Clean, minimal, academic — like a Nature paper's online appendix."

## Theme

**Light** throughout. No dark backgrounds on public pages. SC26 reviewers and paper readers expect academic styling.

```
Background:    #f9fafb   (gray-50 — page background)
Surface:       #ffffff   (cards, panels, table rows)
Surface-alt:   #f3f4f6   (alternating table rows, subtle sections)
Border:        #e5e7eb   (card borders, table dividers)
Border-strong: #d1d5db   (section dividers, tab borders)
Text:          #111827   (gray-900 — primary body text)
Text-secondary:#4b5563   (gray-600 — labels, captions)
Text-muted:    #9ca3af   (gray-400 — decorative only; never for meaningful text)
Accent:        #2563eb   (blue-600 — links, focus rings, active states)
Accent-light:  #eff6ff   (blue-50 — accent backgrounds)
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
  /* === SURFACES === */
  --bg:              #f9fafb;
  --surface:         #ffffff;
  --surface-alt:     #f3f4f6;
  --border:          #e5e7eb;
  --border-strong:   #d1d5db;

  /* === TEXT === */
  --text:            #111827;
  --text-secondary:  #4b5563;
  --text-muted:      #9ca3af;
  --accent:          #2563eb;
  --accent-light:    #eff6ff;

  /* === STATUS (Okabe-Ito colorblind-safe palette) === */
  --pass-color:      #56B4E9;   /* Sky Blue */
  --pass-bg:         #e8f4fb;
  --pass-text:       #0369a1;

  --build-fail-color:#D55E00;   /* Vermillion */
  --build-fail-bg:   #fdf1ec;
  --build-fail-text: #9a3412;

  --run-fail-color:  #E69F00;   /* Orange */
  --run-fail-bg:     #fef9ec;
  --run-fail-text:   #92400e;

  --verify-fail-color: #CC79A7; /* Reddish Purple */
  --verify-fail-bg:  #fdf2f8;
  --verify-fail-text:#86198f;

  --neutral-color:   #94a3b8;
  --neutral-bg:      #f1f5f9;
  --neutral-text:    #475569;

  /* === TEAM MEMBERS (sprint dashboard) === */
  --team-samyak:     #4f46e5;   /* Indigo */
  --team-erel:       #7c3aed;   /* Violet */
  --team-gal:        #db2777;   /* Pink */
  --team-niranjan:   #0891b2;   /* Cyan */
  --team-claude:     #0d9488;   /* Teal */

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

  /* === CHART COLORS (ordered by use frequency) === */
  --chart-pass:         #56B4E9;
  --chart-build-fail:   #D55E00;
  --chart-run-fail:     #E69F00;
  --chart-verify-fail:  #CC79A7;
  --chart-neutral:      #94a3b8;
  --chart-l0:           #2563eb;
  --chart-l1:           #3b82f6;
  --chart-l2:           #60a5fa;
  --chart-l3:           #93c5fd;
  --chart-l4:           #bfdbfe;
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
Chart.defaults.color = '#4b5563';
Chart.defaults.borderColor = '#e5e7eb';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = '#111827';
Chart.defaults.plugins.tooltip.titleColor = '#f9fafb';
Chart.defaults.plugins.tooltip.bodyColor = '#d1d5db';
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

*Last updated: 2026-03-25. Update this file whenever design decisions change.*
