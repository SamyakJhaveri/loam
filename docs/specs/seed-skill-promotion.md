# Seed skill promotion

**Decision D2 (2026-08-31, refined 2026-09-01):** grow `cultivation/marketplace/sam-cc-setup/` toward ~27 curated skills.
The seed stays lean (catchup only); the README advertises "1 core skill + a 27-skill plugin" honestly.
This keeps the asset-layer rule: seed/ ships always-on generic behavior, optional workflows live in the plugin.
Candidate sources include the skills grown in Samyak's other projects: job_search, distbench, parbench, instagram_organizer.
**Evidence constraint:** skills earn their place as ON-DEMAND procedures, never as always-loaded prose.
Skills gave Opus 4.8 +28.2 instruction-following points when they encode procedure and constraint (arXiv 2606.17819); repository-description prose adds cost without benefit (arXiv 2602.11988).
Full verdicts: `docs/specs/rebuild-research/clief-claims-verdicts.md`.

## Source pools, in preference order

1. `cultivation/marketplace/sam-cc-setup/skills/` (16 skills, Samyak-authored or adapted with license notices).
2. The SkillSpector-vetted parked bundles in the marketplace manifest (enable-and-adapt, keep SHA pins and licenses).
3. New skills, only after the trigger that justifies them fires twice.

## Per-skill promotion gate

A skill enters `seed/.agents/skills/` only when every box passes:

1. **Procedure, not description.** The body tells the agent HOW to do something or WHAT constraint binds it. A skill that describes the repository or restates general competence is rejected.
2. **Generic.** Useful to every bootstrapped project, not only to Loam. Loam-specific skills stay in the plugin.
3. **Description quality.** The frontmatter description states the trigger, the non-trigger ("NOT for ..."), and stays well under the 1,536-character listing cap.
4. **Invocation control.** Specialized or destructive skills set `disable-model-invocation: true`. `auto-activate` is not a field; never write it.
5. **Trigger eval.** At least three should-trigger and three should-not-trigger cases pass (skill-creator evals; evaluation E5). A skill that misses required invocations is demoted or inlined, not shipped.
6. **Validation.** `claude plugin validate --strict` green on the PLUGIN ROOT (the CLI refuses bare skill directories, and it checks manifests only, not skill frontmatter). Frontmatter `name:` is enforced separately by verify-template stage 6.
7. **License.** Third-party origin keeps its upstream license notice, following the brainstorming/writing-plans precedent.

## Batch process

- One batch per session, on a branch, PR to main (seed behavior).
- After each batch: committed-HEAD Copier render, `bin/verify-template.sh` green (stages 1-7), `git diff --check` clean.
- Update the `.claude/skills/` symlink bridge for each promoted skill, mirroring catchup's pattern.
- Never restate a promoted skill's content in AGENTS.md.jinja; the listing carries discovery.
- If prose ever states a skill count, `seed/.claude/stale-counts.json` already checks it; keep counts out of prose where possible.

## Watch items

- The skill listing budget is 1% of the context window; at ~27 skills the least-invoked descriptions get truncated first. Check `/doctor`'s listing-cost estimate after each batch.
- Session-decay evidence says more prose does not fix adherence; if a promoted skill is ignored mid-session, the fix is the re-anchor pilot (E2), not a longer skill body.
