# seed-skills marketplace

Install-on-demand plugin bundles for Loam-adjacent projects.
Nothing here ships to bootstrapped projects by default; installs are explicit.
Slimmed 2026-08-29 in the rebuild.
Slimmed again in v3.0.0: `sam-cc-setup` kept 3 skills and ships no hooks; everything else moved to `cultivation/parked/` (design law 7, burden of proof is on keeping).

## Install

```bash
claude plugin marketplace add /path/to/loam/cultivation/marketplace
/plugin install sam-cc-setup
```

## Bundles

| Bundle | Contents | Notes |
|--------|----------|-------|
| `sam-cc-setup` | The Loam-owned skills and agents, listed in `sam-cc-setup/README.md` | No hooks, no workflows |
| `research-paper` | Review seats and an adjudicator behind a quote gate, two citation agents, a blind-reader agent, gate scripts (citations, page limits, anonymity, acronyms, consistency, figures, claim drift), the `section-from-exemplars` skill, two review-round workflows, writing guides and project templates for `paper/tools/` | Ships `defaultEnabled:false`; enable per project. Mixed licence: Loam's MIT plus third-party MIT, Apache-2.0, unlicensed-upstream and CC BY-NC 4.0 (non-commercial) parts, listed in its README |
| `web-frontend-*`, `deer-flow-public` | External skills, SHA-pinned via `git-subdir` | Ship `defaultEnabled:false`; enable to trial. Licenses per entry in `marketplace.json`; a `LICENSE.upstream` file in a vendored bundle is authoritative |

Parked in v3.0.0 (moved to `cultivation/parked/`, not installed): 23 `sam-cc-setup` skills, 5 unused agents, the plugin `hooks/` directory, the `plan-review-fanout` workflow, the upstream MIT notice that covered the parked design skills, and the whole `impeccable` plugin.
Removed 2026-08-29: `meta-improvement`, `helpers`, `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
