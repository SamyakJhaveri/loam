# Review round workflows

Two Workflow scripts in `workflows/` run one review round of the paper with the plugin's review seats.
`attack_round_full.js` runs the whole round; `attack_round_seats.js` runs only the seats and leaves the gate and the adjudicator to you.
Workflow agents cannot be messaged once they finish, so a seat that fails the quote gate is repaired by a fresh agent of the same type.

## Before you run

- Start the session at the project root: every path the workflows use is relative to it.
- Fill `paper/tools/contract.md` from `templates/contract.md`; the seats and the critics take the venue, its review criteria and its aspects from section 2.
- Build the PDF (`build.command` in `paper/tools/paper-tools.toml`), then extract its text without `-layout`, for example `pdftotext paper/build/main.pdf paper/build/main.txt`; layout text makes the quote gate reject real quotes.
- Define two user-level agent types the plugin does not ship: `worker` (an execution agent; it runs the quote gate) and `escalate` (a critic on the strongest model you have; it runs the critic, taste and completeness seats).
  The type names sit in the constant block at the top of each script; change them there if yours differ.

## The seats

Both workflows launch the same 10 seats in parallel, each on the built paper text:

- the plugin agents `reviewer-methods`, `reviewer-domain`, `reviewer-generalist`, `reviewer-devils-advocate`, `lean-critic-forensic`, `claim-ref-alignment`, `reader-first-intro` and `citation-finder` (addressed as `research-paper:<name>`);
- `critic`, an `escalate` agent that judges the paper on the criteria and aspects of contract section 2;
- `taste`, an `escalate` agent that judges six writing moves: argument chain, gap-to-answer mapping, claim headings, what Fig. 1 shows, numbers in the claiming sentence, and machine-sounding prose.

Each seat writes `<seat>.findings.json` and `<seat>.review.md`; every seat but `reviewer-devils-advocate`, which only challenges, also writes `<seat>.scores.md` (a score from 1 to 5 per criterion and aspect, weakest first).
In this round `claim-ref-alignment` skips its uncited-assertion step, because `citation-finder` covers those sentences.

## What each workflow does

`attack-round-full`:

1. Seats: the 10 seats above.
2. Gate: as each seat finishes, a `worker` runs `paper-tool validate_findings <file>` and `paper-tool validate_findings --check-quotes --require-quotes <file> --root <ROOT>`, and copies the seat's files into `findings/` when both exit 0.
   On failure, one fresh agent of the seat's own type gets the seat's findings file and the rejection list, fixes only those findings, and the gate runs once more.
   At most 8 repairs run in one round; a seat that still fails stays out of `findings/` and is named in the result.
3. Adjudicate: `research-paper:adjudicate-review` verifies, merges and tiers the findings of the seats that passed, adds a "Scores" table, and, when given, uses the decisions file, the known-issue keys and the prior round.
4. Completeness: an `escalate` critic reads contract section 2, the paper and the adjudicated findings, and lists what stays uncovered once the confirmed findings are fixed.

`attack-round-seats` runs step 1 only.
Then, from the project root, for each seat:

```
paper-tool validate_findings <out>/seats/<seat>/<seat>.findings.json
paper-tool validate_findings --check-quotes --require-quotes <out>/seats/<seat>/<seat>.findings.json --root .
```

Copy the files of each seat that passes both into `<out>/findings/`, then launch `research-paper:adjudicate-review` with `FINDINGS_DIR`, `PAPER`, `ROOT`, `OUT = <out>/adjudicated` and any of `DECISIONS`, `KEYS` and `PRIOR`.
The workflow returns these steps with the round's paths filled in.

## Agent count

State the count before launch.

| Workflow | Seats | Gate checks | Repairs and re-checks | Adjudicator | Completeness | Total |
|---|---|---|---|---|---|---|
| `attack-round-full` | 10 | 10 | 0 to 8, plus 0 to 8 | 1 | 1 | 22 to 38 |
| `attack-round-seats` | 10 | 0 | 0 | 0 | 0 | 10 |

## Inputs

Pass a JSON object as the workflow's `args`; every key is optional.

| Key | Default | Meaning |
|---|---|---|
| `paper` | `paper/build/main.txt` | the built paper text the seats read |
| `out` | `paper/review/round-1` | the output folder of this round |
| `keys` | none | one or more JSON files of known issues (adjudicator only) |
| `decisions` | none | one or more files of decisions already made (adjudicator only) |
| `prior` | none | the previous round's `adjudicated.findings.json` (adjudicator only) |

Use a new `out` for each round, so a second round does not overwrite the first.

## Outputs

```
<out>/seats/<seat>/      each seat's findings, review and scores (no scores from reviewer-devils-advocate)
<out>/findings/          copies from the seats that passed the quote gate
<out>/adjudicated/       adjudicated.findings.json and adjudication.md
<out>/completeness/      completeness.md
```

`attack-round-seats` writes only `seats/`.

## How to run

Invoke `/research-paper:attack-round-full` or `/research-paper:attack-round-seats` and give the inputs, for example:

```json
{"paper": "paper/build/main.txt", "out": "paper/review/round-2", "prior": "paper/review/round-1/adjudicated/adjudicated.findings.json"}
```

The workflow logs the inputs it resolved before the first seat starts and returns a summary per seat.
