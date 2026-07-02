# Future Work — Loam v3.x

Items identified during v3.0 implementation. Address as we go.

---

## Depth-on-Demand for Dissolved Skills

**Context:** v3.0 dissolved 4 skills (karpathy-guidelines, model-route, security, scalability) into AGENTS.md persistent context. This gains always-available guidance but loses depth.

**The tradeoff:** AGENTS.md has ~500-token summaries of security and scalability. The original skills had 4 reference files each (~15KB total). For dedicated security reviews or scalability audits, the condensed version may be insufficient.

**Potential solutions:**
1. Keep the detailed reference files in `cultivation/retired/` and document how to pull them in for deep reviews
2. Create a `/deep-review security` mode that loads the full reference files on demand
3. Use path-scoped rules to load detailed patterns when editing security-sensitive code paths (auth handlers, API endpoints, database queries)

**Design principle at stake:** Availability x Depth = roughly constant. The question is whether we can break this constraint with smart demand-paging — load summaries always, details on trigger.

---

## Skill Composition / Middleware Pattern

**Context:** The original 24-skill Unix-philosophy design (v2.0) had composition overhead in an LLM context. Skills can't pipe into each other like Unix tools because each load costs tokens.

**Future exploration:** If Claude Code adds skill composition (skill-within-skill loading), revisit whether some AGENTS.md sections should become composable micro-skills again. Monitor Claude Code release notes for this feature.
