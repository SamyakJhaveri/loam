# How the toolchain works

Why the plugin is built the way it is: the one fact behind the design, the flow from review seats to the quote gate to the adjudicator, what each piece is for, and the design decisions with the alternatives they rejected.
Commands and the run order are in `../README.md`.

## 1. The one fact behind the design

An AI reviewer can be wrong while sounding certain, so nothing it says counts until it has been checked against the paper.
A seat can quote a sentence the paper does not contain, which the quote gate rejects, or call something missing that another section states, which carries no quote and is left to the adjudicator to check.
So every tool either produces something checkable, or checks another tool's output.
Checkable means an exit code (0 is pass, 1 is a problem found) or a quote that must exist at a named line of the paper.

## 2. The flow

```
            +-------------------- WHILE DRAFTING ---------------------+
            |  docs/writing-rules.md, docs/section-loop.md            |
 edit a    -+-> check_revision_token_conservation (before vs after)   |
 section    |        numbers, \cite keys, \ref targets kept?          |
            |        v                                                |
            |  CLAIM_DRIFT_GUARD.md: did any claim get stronger?      |
            +---------------------------------------------------------+
                                  |
            +------------- BEFORE EACH FULL REVIEW -------------------+
 build,     |  cite_check  paper_limits  anonymity_scan               |
 pdftotext  |  check_consistency  check_acronyms  check_tikz          |
            |  FIGURE_CHECKLIST.md          (exit 1 = fix first)      |
            |          v                                              |
            |  seats in parallel, each writes <seat>.findings.json    |
            |  methods | domain | generalist | devils-advocate |      |
            |  lean-critic-forensic | claim-ref-alignment | critic    |
            |          v                                              |
            |  validate_findings --check-quotes   (the quote gate)    |
            |          v                                              |
            |  adjudicate-review: confirmed / refuted / downgraded /  |
            |  held, tiers, known-issue coverage (KEYS)               |
            |          v                                              |
            |  adjudication.md -> writer | new task | author decision |
            +---------------------------------------------------------+
                                  |
             reader-first-intro -> humanizer audit -> rigor pass
```

## 3. Each piece and why it exists

### Scripts

A deterministic check gives the same answer every run and involves no model.
The scripts exist because a venue's hard rules (page limit, anonymity, reference format, abstract length) can cause rejection without review.
`cite_check` fails closed: a network error counts as a defect, never a pass.

### Fixture tests

A fixture is a small made-up input with a known answer.
Each gate script is tested on input with a defect, which it must report, and on clean input, which it must pass: the tests in `tests/`, `tests/run_selftest.sh` for the quote gate, and `style_lint --test` for the style rules.
A check that has never failed on a known defect gives no evidence that it would catch one.

### Review seats

A seat is a subagent with its own instructions file that reviews the paper from one angle, like one program committee member.
Each writes findings in the shape of `finding_schema.json`, each with a verbatim quote and a line number.
The seats differ in lens because different settings catch different problems; the adjudicator gets their union.
`claim-ref-alignment` fetches each cited source by its identifier and checks that it supports the citing sentence; it sends only identifiers, URLs and cited titles, never the paper's text.

### The quote gate

`validate_findings --check-quotes --require-quotes <findings.json> --root <dir>` opens the paper at each finding's line and confirms the quote is there.
A finding whose quote is not there is rejected.
Feed it plain `pdftotext` output, not `-layout`: two-column layout text makes real quotes fail (note D1 in the script).

### The adjudicator

`adjudicate-review` verifies every finding against the paper, merges duplicates, and gives each a verdict (confirmed, refuted, downgraded, held) and a tier (must-fix, should-fix, optional).
It never adds a blocker no seat raised.
With `KEYS` it adds a known-issue coverage section: the known problems that still apply and that no confirmed finding raised; the keys never change a verdict.

### Keys and vaccination

A key is a JSON list of problems the paper is already known to have (the `KEYS` input of `adjudicate-review`, which names its fields).
Vaccination means running the seats, seeing which known problems they miss, and adding a named check for each miss to the seat that should have caught it; then the seats run again.

### Routing the result

Confirmed text fixes go to the writer; items that need new analysis become new tasks; held items go to the author one decision at a time (fact, options, risk, recommendation).
The writer never answers an open author decision; it leaves a `% OWNER:` comment in the `.tex` naming the decision.

## 4. Design decisions

| Decision | Chosen | Rejected | Why |
|----|----|----|----|
| Source of tools | Single files and line ranges from upstream repositories, with attribution | Installing whole repositories or plugins | A single file can be read whole, credited and changed under its own licence; the licence table in `../README.md` names each one |
| Trust in agents | Quote gate plus adjudicator | Using seat output as is | A finding can rest on a quote or an absence that the paper does not bear out (section 1) |
| Network use | Only DOIs, arXiv ids, URLs, cited titles and topic keywords leave the machine | Services that take manuscript sentences | Manuscript text must not go to an outside service |
| Configuration | One contract and one config file per project, in `paper/tools/` | Venue, field and paths written into each agent and script | One plugin serves any paper; a project fills in two files |
| Agent location | One copy, shipped in the plugin | A hand-made copy in each project | A hand-made copy goes stale |
