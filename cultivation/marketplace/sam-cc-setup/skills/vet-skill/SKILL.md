---
name: vet-skill
description: "Security-scan an external skill or bundle before installing it. Use whenever adopting a skill, plugin, or agent from a third-party GitHub repo or marketplace, before enabling it or copying it into the project. Wraps NVIDIA SkillSpector for a static scan and applies a pass/review/reject threshold. NOT for scanning your own authored skills as a quality check (use /code-review), and NOT a runtime sandbox - it inspects, it does not contain."
disable-model-invocation: true
allowed-tools: Bash, Read
---

# vet-skill

Treat installing any external skill as a trust decision. A skill body loads into
the agent's context and can carry injected instructions; some skills ship scripts
that run. Scan first.

## Tool

[NVIDIA SkillSpector](https://github.com/nvidia/skillspector), a static scanner for
agent skills. Install once, keep current:

```
uv tool install skillspector      # first time
uv tool upgrade skillspector      # keep current before a vetting session
```

If the Loam repo (or a Loam-bootstrapped project) is present, prefer its wrapper,
which applies the threshold and exit codes for you:

```
bin/vet-skill.sh <path-to-skill-dir>
bin/vet-skill.sh https://github.com/owner/repo      # cloned read-only first
```

## Procedure

1. Never install first. Clone read-only to a scratch dir, or point the wrapper at
   the URL (it clones shallow, read-only, and cleans up). Never run the skill's own
   scripts during vetting.
2. Scan: `skillspector scan <dir> --recursive --no-llm --format json`. The static
   scan needs no API key and no network beyond the clone.
3. Read `risk_assessment.severity` (worst finding wins across a multi-skill repo):
   - `NONE` / `LOW` -> adopt.
   - `MEDIUM` -> read every issue and decide deliberately; record why if you adopt.
   - `HIGH` / `CRITICAL` -> reject.
4. Confirm it is actually a Claude skill: it must contain at least one `SKILL.md`.
   A research framework or app with no `SKILL.md` is not installable as a skill.
5. Record the verdict (repo, date, severity, decision) wherever the project tracks
   adopted assets, so the next person does not re-vet blind.

## Notes

- Static scanning finds known-risky patterns, not every possible harm. For a MEDIUM
  result, human reading of the flagged lines is the gate, not the score alone.
- SkillSpector also has an LLM-assisted mode (drop `--no-llm` with a provider key)
  for deeper analysis; the static mode is the deterministic default for a quick gate.
