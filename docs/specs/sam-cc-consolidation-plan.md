# Sam CC Setup Consolidation Implementation Plan

> **For agentic workers:** Use test-driven development for the repository contract and skill-evaluation development for the two process skills. Keep the work on the `sam-cc-consolidation` branch.

**Goal:** Make `sam-cc-setup` own a complete design-to-plan workflow and retire `sam-superpowers`.

**Architecture:** Move the existing design skill into `sam-cc-setup`, add an adapted self-contained planning skill, and enforce the ownership and handoff chain with repository tests. Preserve upstream license provenance and remove all active marketplace routing to the retired plugin.

**Tech Stack:** Markdown Agent Skills, JSON plugin manifests, Python `unittest`, Bash verification.

## Global Constraints

- `sam-cc-setup` is the only Loam-owned setup plugin after this change.
- `brainstorming` and `writing-plans` live under `cultivation/marketplace/sam-cc-setup/skills/`.
- `writing-plans` contains no required `superpowers:*` execution dependency.
- `sam-cc-setup` is version `0.5.0` in both manifests.
- Preserve the upstream MIT notice verbatim.
- Do not modify `seed/` or perform Clief Notes integration.

---

### Task 1: Define the failing marketplace ownership contract

**Files:**

- Create: `bin/tests/test_marketplace_skill_routes.py`
- Modify: `bin/verify-template.sh`

**Interfaces:**

- Consumes: the repository tree rooted two directories above the test file.
- Produces: `unittest` failures for missing skills, stale plugin ownership, broken references, version drift, and missing license provenance.

- [ ] Write tests that assert the six requirements in the design's verification contract.
- [ ] Change the stage-one discovery pattern from the single rendered-contract test file to `test_*.py` so the new contract is part of the public gate.
- [ ] Run `python3 -m unittest discover -s bin/tests -p 'test_*.py' -v` against the unchanged plugin.
- [ ] Record the expected RED result: failures for the present `sam-superpowers` entry and directory, absent local `writing-plans`, and old version.
- [ ] Commit with `test: define sam cc skill ownership`.

### Task 2: Consolidate and adapt the design workflow

**Files:**

- Move: `cultivation/marketplace/sam-superpowers/skills/brainstorming/` to `cultivation/marketplace/sam-cc-setup/skills/brainstorming/`
- Create: `cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md`
- Create: `cultivation/marketplace/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt`
- Modify: `cultivation/marketplace/sam-cc-setup/skills/tech-selection/SKILL.md`

**Interfaces:**

- Consumes: an approved design document from `brainstorming`.
- Produces: a complete implementation plan at `docs/plans/YYYY-MM-DD-<feature-name>.md` and an available-host execution handoff.

- [ ] Run one fresh-context baseline scenario against the current plugin. Confirm that an approved brainstorming design cannot resolve its required `writing-plans` handoff locally.
- [ ] Move the existing brainstorming tree without dropping its support files.
- [ ] Change its default spec location to `docs/specs/` and keep `writing-plans` as its only terminal handoff.
- [ ] Adapt the historical `writing-plans` skill. Keep exact file paths, runnable checks, expected results, small tasks, and self-review. Replace required `superpowers:*` execution skills with available-host execution choices.
- [ ] Copy the upstream MIT license notice verbatim into the third-party license file.
- [ ] Make `tech-selection` refer to the local `brainstorming` skill without implying a separate plugin.
- [ ] Run fresh-context GREEN scenarios for discovery, the design-to-plan handoff, and a plan produced without missing dependencies.
- [ ] Run the focused unit suite and require all marketplace ownership tests to pass except the manifest-removal and version tests reserved for Task 3.
- [ ] Commit with `feat: consolidate design planning skills`.

### Task 3: Retire the plugin and update active routing

**Files:**

- Delete: `cultivation/marketplace/sam-superpowers/`
- Modify: `cultivation/marketplace/.claude-plugin/marketplace.json`
- Modify: `cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json`
- Modify: `cultivation/marketplace/README.md`
- Modify: `cultivation/marketplace/sam-cc-setup/README.md`
- Modify: `cultivation/marketplace/UPGRADING.md`

**Interfaces:**

- Consumes: the complete local skill chain from Task 2.
- Produces: one installable `sam-cc-setup` plugin at version `0.5.0`.

- [ ] Remove the `sam-superpowers` marketplace entry and directory.
- [ ] Set both `sam-cc-setup` versions to `0.5.0`.
- [ ] Rewrite active plugin inventory and upgrade instructions to name the consolidated workflow and the upstream provenance.
- [ ] Preserve historical context only in clearly historical sections or git history. Remove dead installation commands.
- [ ] Run `python3 -m unittest discover -s bin/tests -p 'test_*.py' -v` and require all tests to pass.
- [ ] Run `bin/verify-template.sh` and require `verify-template: PASSED`.
- [ ] Run `rg -n 'sam-superpowers' cultivation/marketplace README.md CONTRIBUTING.md` and require no active routing match.
- [ ] Commit with `refactor: retire sam superpowers plugin`.

### Task 4: Review the full branch

**Files:**

- Review all changes from `28d08f8` to branch HEAD.

**Interfaces:**

- Consumes: Tasks 1 through 3.
- Produces: a correctness review limited to broken routes, missing files, invalid skill behavior, provenance loss, and verification gaps.

- [ ] Run a fresh-context review of the complete diff.
- [ ] Fix confirmed correctness findings and rerun their focused checks.
- [ ] Run `git diff --check 28d08f8..HEAD`.
- [ ] Run `bin/verify-template.sh` once more and record its exact test summary and final marker.
