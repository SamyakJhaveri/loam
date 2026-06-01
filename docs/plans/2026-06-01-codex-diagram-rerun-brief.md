# Codex brief: re-run Loam diagram design language

Date: 2026-06-01

## Mission

Re-run Loam's diagram-design-language work as an independent Codex pass. The prior attempt
created useful rails, but the rendered concepts did not reliably explain Loam. This pass
should apply the reusable quality gate, improve the active prompt sources, and re-render only
after the concept contract is clear.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/rules/workflow.md`
- `.claude/rules/known-issues.md`
- `.claude/rules/layer-triage.md`
- `seed/.claude/skills/diagrams/design-language.md`
- `seed/.claude/skills/diagrams/quality-gate.md`
- `seed/.claude/skills/diagrams/scripts/render-yoshida.py`
- `docs/diagrams/concepts.yaml`
- `docs/diagrams/loam-hero-prompts.md`

Codex caveat: the drawio, excalidraw, and tldraw MCP servers described in the Claude-facing
docs are claude.ai-hosted and authenticated through Claude. In Codex, use direct file/script
paths. Track B is driven by `seed/.claude/skills/diagrams/scripts/render-yoshida.py`, which
requires `GEMINI_API_KEY` and network access.

## Execute

1. Understand Loam before editing prompts: it is both a Copier template and a Claude Code
   project dogfooding `seed/.claude/` through `.claude -> seed/.claude`; only `seed/` ships.
2. Use `seed/.claude/skills/diagrams/quality-gate.md` as the canonical pass/fail contract.
   Do not duplicate the rubric into new places.
3. Treat `docs/diagrams/concepts.yaml` as the per-concept source of truth. Each concept's
   `viewer_should_understand`, `must_show`, and `label_strategy` fields define what a keeper
   must prove.
4. Fix concept #3, `context-routing`, first. A keeper must show routing: paths, dispatch,
   gates, directional flow, or movement into L0/L1/L2 destinations. A static soil cross-section
   fails.
5. Route labels deterministically. Use Track A or a vector overlay for exact labels; keep Track B
   label-light or label-free.
6. Keep Track B bright, inviting, and luminous. Preserve positive framing in active prompts.
7. Render candidates only after the registry contract and prompt are clear. For each generated
   candidate, use the `.qa.yaml` manifest and quality gate before marking `Keep?`.

## Scope Guard

Keep the original hard constraints:

- `render-yoshida.py` stays glue-only: registry -> prompt assembly -> refs -> Gemini call -> PNGs
  plus a small QA manifest.
- Gemini references remain capped at six, with hard-fail above the cap.
- Do not vendor Yoshida scans, PaperBanana, or external renderer source.
- Do not commit `yoshida_hiroshi/`, `docs/diagrams/loam-hero-*.png`, or
  `docs/diagrams/loam-hero-*.qa.yaml`.
- Reusable diagram machinery belongs in `seed/.claude/skills/diagrams/`.
- Loam-specific diagram content belongs in root `docs/diagrams/`, not in `seed/`.
- Commit directly to `main`; do not create a branch unless the user asks.
- Run `bin/verify-template.sh` before any commit and expect `ALL OK`.

## Verification

```bash
python3 -m py_compile seed/.claude/skills/diagrams/scripts/render-yoshida.py
python3 -c "import yaml; d=yaml.safe_load(open('docs/diagrams/concepts.yaml')); assert isinstance(d, list); assert len(d) == 16; assert all('viewer_should_understand' in c and 'must_show' in c and 'label_strategy' in c for c in d); print('concepts ok')"
! grep -rni "vintage botanical scientific plate\\|old biology textbook\\|no harsh contrast" seed/.claude/skills/diagrams docs/diagrams
bin/verify-template.sh
```

With `GEMINI_API_KEY` exported and network enabled:

```bash
uv run seed/.claude/skills/diagrams/scripts/render-yoshida.py --concept identity --candidates 2
uv run seed/.claude/skills/diagrams/scripts/render-yoshida.py --concept context-routing --candidates 2
```

Then review the generated PNGs and `.qa.yaml` manifests against
`seed/.claude/skills/diagrams/quality-gate.md`, updating `docs/diagrams/loam-hero-prompts.md`
with concise keep/reject notes.
