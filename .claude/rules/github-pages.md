---
paths:
  - "visualizations/**"
  - ".github/workflows/**"
---

# GitHub Pages Rules

> Auto-loaded when working on `visualizations/` files.

## Deployment

- **URL:** https://samyakjhaveri.github.io/parbench_sam/
- **Source:** `visualizations/` directory (7 HTML + 2 JS data files)
- **Workflow:** `.github/workflows/deploy-pages.yml`
- **Triggers:** push to `main` touching `visualizations/**`, or manual `workflow_dispatch`
- **Entry point:** `visualizations/index.html` redirects to `overview.html`

## Privacy

- Password-protected via `staticrypt` (AES-256 browser encryption)
- Password stored as GitHub secret `PAGES_PASSWORD`
- Setup instructions: `.github/PAGES_SETUP.md`
- True private Pages (GitHub SSO) requires Enterprise Cloud — not available on Pro

## Data Refresh

```bash
python3 scripts/generate_viz_data.py
# Regenerates results_data.js and build_results_data.js
# from source JSON in results/augmentation/
# Then commit and push to redeploy
```

## Adding a New Dashboard

1. Create `visualizations/<name>.html` (copy nav structure from any existing page)
2. Add a nav link in ALL existing HTML files' nav bars
3. Add it to the dashboard list in `README.md`
4. Push to `main` — workflow auto-deploys

## After Repo Transfer

Re-enable: Settings → Pages → Source = "GitHub Actions"
