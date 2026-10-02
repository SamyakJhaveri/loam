# How the toolchain works

Why the plugin is built the way it is: the one fact behind the design, the flow from review seats to the quote gate to the adjudicator, what each piece is for, and the design decisions with the alternatives they rejected.
Commands and the run order are in `../README.md`.

## 1. The one fact behind the design

An AI reviewer is often confidently wrong, so nothing it says counts until a program has checked it.
A seat will claim, for example, that the paper never gives a figure the paper states plainly a few pages later; when the adjudicator checks seat findings against the text, a real share of them are refuted.
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
The scripts exist because a venue's hard rules (page limit, anonymity, a DOI or link per reference, abstract length, no appendix) can cause rejection without review.
`cite_check` fails closed: a network error counts as a defect, never a pass.

### Fixture tests

A fixture is a small made-up input with a known answer.
Each script has one input with a planted defect (it must exit 1) and one clean input (it must exit 0).
They exist because separate verifier agents found real defects in freshly built scripts that the builders' own tests passed, for example a `\cite` split over two lines being skipped.

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

A key is a list of known problems, for example the objections of an earlier review or the issues found in a trial run.
Vaccination means running the seats, seeing which known problems they miss, and adding a named check for each miss to the seat that should have caught it; then the seats run again.

### Routing the result

Confirmed text fixes go to the writer; items that need new analysis become new tasks; held items go to the author one decision at a time (fact, options, risk, recommendation).
The writer never answers an open author decision; it leaves a `% OWNER:` comment in the `.tex` naming the decision.

## 4. Design decisions

| Decision | Chosen | Rejected | Why |
|----|----|----|----|
| Source of tools | Single files and line ranges from upstream repositories, with attribution | Installing whole repositories or plugins | The value was in the prompt text; the repositories' machinery did not fit, and some was broken (one citation checker crashed on any DOI entry) |
| Trust in agents | Quote gate plus adjudicator | Using seat output as is | Seats are confidently wrong at a real rate |
| Script verification | A separate agent attacks each script | The builder's own tests only | The attackers found defects the builders' tests passed |
| Network use | Only DOIs, arXiv ids, URLs, cited titles and topic keywords leave the machine | Services that take manuscript sentences | Manuscript text must not go to an outside service |
| Configuration | One contract and one config file per project, in `paper/tools/` | Venue, field and paths written into each agent and script | One plugin serves any paper; a project fills in two files |
| Agent location | One copy, shipped in the plugin | A hand-made copy in each project | A hand-made copy goes stale |
