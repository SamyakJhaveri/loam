# Merged ideas: <the question in one line>

<!-- Copy to <run>/merged.md and fill every <...>. Read only <run>/proposals/*.md, <run>/owner-ideas.md and <run>/seats.tsv; no earlier merge and no owner notes, which carry the owner's conclusions. Re-check nothing: every number and quote is as the named seat wrote it, under its own Verified or Inferred mark. Keep the section order; write "none" in an empty section rather than dropping it. -->

Run `<date>-<slug>`, step 2 of the research-gap skill, <date>.
Inputs: `proposals/<seat>.md` for <the seats that returned>, `owner-ideas.md` and `seats.tsv` in this folder.

## 0. How to read this

| Seat | Lens | Model and effort | Seeds |
| --- | --- | --- | --- |
| <seat id> | <lens> | <as seats.tsv says> | <as seats.tsv says> |

- N = <seats with a proposal file>; <name any seat that did not return, and why>.
- Locator: `<seat>#<n>` is the idea headed `### <n>.` in `proposals/<seat>.md`.
  `<seat>#0` is the text above a seat's first `###` idea; it can be cited but is not an idea.
- Support k/N: k seats proposed the idea as one of their `###` ideas.
- "+k cite": k more seats raise the same gap inside an idea mapped to another id, by quoting the same passage ("quote") or reporting the same evidence ("evidence"); they are named.
- "owner" marks an idea from `owner-ideas.md`.
  "owner; briefed" is an owner idea the brief itself states: every seat saw it, so no seat can support it independently, and the seats whose ideas take up a part of it are listed as cites, including a seat idea that maps onto it whole.
  An owner idea kept out of the briefs gets k/N like any other, and 0/N is a real count.
- Support counts independent proposers; it is not a score, since models can share a blind spot.
- Cost words, as the seats use them: FREE (data in hand), SMALL (one analysis or one logged field), NEW ARM (new runs).

## 1. At a glance

| Id | Idea in plain words | Support | Against or qualifying | Cost | Shortlist |
| --- | --- | --- | --- | --- | --- |
| M1 | <one or two sentences> | <k/N +k cite, or owner; briefed +k cite> | <seats that argue against it, or none> | <FREE, SMALL or NEW ARM> | <yes, owner / yes / yes, cheapest kill / no> |

## 2. Map from every seat idea

Every `###` idea of every proposal file has one row.

| Seat idea | The seat's idea, short | Merged id |
| --- | --- | --- |
| `<seat>#<n>` | <a few words> | <M id; "other half: M id" when it spans two, counted as a cite there> |

## 3. Merged ideas

### M1 (<owner, if it is one>). <short title>

- **Plain words.** <the question; an owner idea quotes `owner-ideas.md`>
- **Support.** <k/N or owner; briefed: which seats, and the +k cites with what each quotes or reports>
- **Gap.** <the strongest quote a seat gives, with its locator and mark>
- **Evidence the seats report.** <numbers and records, each with its seat and mark>
- **Closest work.** <papers seats named as closest, each with the seat that named it; an id or title the merge added from memory is marked "(added in merge)">
- **Data and cost.** <what would answer it and its cost word>
- **Kill result.** <the finding that would show it wrong or already done, per seat>
- **Numbers stated differently.** <pointer to section 5, or none>

## 4. Where the seats disagree, and why

| # | Topic | Positions | Why they differ | What step 3 or 6 should settle |
| --- | --- | --- | --- | --- |
| D1 | <topic (M ids)> | <each seat's position, quoted or close> | <the different reading, source or definition> | <the record, search or check that would settle it> |

## 5. Numbers stated differently

Recorded as each seat states them; this merge does not pick one.

- **N1. <quantity>.**
  <seat>: <number>, <its definition and source>.
  <seat>: <number>, <its definition and source>.

## 6. Shortlist

Rule: every owner idea, every idea with support 2 or more, and at most three single-seat ideas with the cheapest kill.
Cheapest means first in this order: (1) a read or analysis of data already collected, with no hardware time and no money; (2) hardware time with no model spend; (3) runs already planned; (4) a new arm, new runs that spend money.
In the small mode only the owner's ideas go to step 3.
On a tie among single-seat ideas the merge picks one and says why.
An owner idea that is both a gap claim and a data question goes to step 3 and is also listed under the step-6 questions.
In the small mode a shortlisted seat claim stays here, unchecked, for a later run.

### Gap claims for step 3

| Id | Support | Reason |
| --- | --- | --- |
| M1 | <support> | <one line> |

For each gap claim:

**M1.**
Facets (a prior paper closes the gap only if it matches all of them): (1) <...>; (2) <...>; (3) <...>.
Closest, named by seats: <id, title (seat)>.
Named in `owner-ideas.md`: <id, title, or none>.

### Questions about the project's own data, for step 6

| Id | Support | Cheapest check and its cost |
| --- | --- | --- |
| M<n> | <support> | <the check, its cost word and its place in the cost order> |

### Not shortlisted

- M<n> (<support>): <why, with its kill's place in the cost order>.

## 7. Follow-ups found during the merge (not edited)

- <stale rows in `seats.tsv`, contradictions inside a proposal, records a seat flagged, or none>

## 8. Risks

- <grouping calls (ideas mapped to their main half), titles added from memory, any count that rests on a judgement>
