# Claim drift guard for revisions

Run it each time the writer revises a section or fills `\pending{Pn}` placeholders.
It has two parts: the ladder rule, which a reader applies to each revised sentence, and the token check, a script run on the old and new copy of each changed file.
Sections 1 to 2 and the block in section 4 are taken from academic-research-skills (attribution at the end); [H] marks our additions.

## 1. The claim-strength ladder

| Rung | Phrasings (upstream, weakest first) | Same rung, added phrasings [H] |
|---|---|---|
| 1 | is consistent with, may suggest | suggests |
| 2 | is associated with, relates to, correlates with | - |
| 3 | predicts | - |
| 4 | contributes to | - |
| 5 | affects, influences, leads to, shapes | - |
| 6 | causes, determines, demonstrates that, proves | shows that, establishes, guarantees |

- The order of rungs varies by field, so the rule is "no silent move", not one fixed order.
- When unsure whether two phrasings sit on the same rung, treat them as different rungs and keep the old wording.

## 2. What counts as a move

A move (needs the authorization in section 3):

- `associated with` to `leads to`, `reduces`, `drives` or `causes` (up).
- `may support` or `might improve` to `supports` or `improves`: dropping a modal hedge is a move up.
- `predicts` to `is associated with` (down): silent weakening misstates the result as much as strengthening.
- Deleting a design-based causal caveat, a scope hedge ("in this sample"), a status hedge ("preliminary", "exploratory"), or a null or negative result.
- Moving a claim from a cited background source onto this paper's own finding.

Not a move:

- Reordering a sentence that keeps the same verb and hedges.
- Emphasis or positioning prose that leaves the verb's rung unchanged.
- A description swap on the same rung ("narrows the range" and "reduces the range").
- Condensing prose that keeps every hedge and every claim's rung.

The hedges of the draft that a revision keeps unless section 3 authorizes a change [H]: list them once per paper, each with its file and line at a named commit.
Keep the list where the reader of section 3 finds it, for example as a project rule in `paper/tools/contract.md` section 3.
A synthetic example, for a paper on ExampleSys:

- Scope: "on the evaluated jobs and machines" (`paper/sections/introduction.tex:12`).
- Design caveat: "does not prove that the two outputs are equal" (`introduction.tex:12`); "is not a proof of equality" (`discussion.tex:5`).
- Status of a bound: "a 90 percent interval" (`abstract.tex:2`, `evaluation.tex:40`).
- Limit of a control: "it does not show that ExampleSys catches a fault it was never shown" (`evaluation.tex:81`).
- Limit of the sample: "it does not show that the sample jobs represent workloads in general" (`design.tex:40`).

## 3. The rule for each revised sentence

1. Place the claim of the old sentence on the ladder (verb, modal, hedges).
2. Place the claim of the new sentence on the ladder the same way.
3. New rung above old rung, or a hedge from section 2 deleted: a confirmed finding or an owner decision must authorize the strength change, and the same edit must add the new evidence that supports the higher rung.
   New evidence is one of: a `\pending{Pn}` filled from its source in the project's placeholder registry (the file that names, for each placeholder, the claims file and key its value comes from), a new or changed table or figure value from the claims file the registry names for it, or a new `\cite` of a peer-reviewed source that states the claim.
   Without both, restore the old wording.
4. Evidence in an earlier or later edit does not count; it must be in the same diff.
5. New rung below old rung: needs a confirmed finding or an owner decision that authorizes it, but no new evidence; name it and the sentence in the commit message.
6. A reviewer asks for more confidence: strengthen the writing (active voice, result first, shorter sentences), not the claim.
7. Numbers, `\cite` keys, `\ref` and `\label` targets and placeholders are conserved tokens: run section 5 and explain every delta by a confirmed finding or an owner decision; revert the rest.

## 4. Writer prompt block (measured upstream)

Paste this block into the task of a model that revises prose, between the revision plan and the final instruction.
It is the RUN_PLAN.md guard block with its em dashes written "-"; in our workflow a "revision-plan item" is a confirmed finding routed to the writer or an owner decision.
Section 7 gives what it was measured to do.

```
REVISION DISCIPLINE (claim-strength ladder):

Epistemic claims sit on an ordered strength scale:
  is consistent with / may suggest
    < is associated with / relates to / correlates with
      < predicts
        < contributes to
          < affects / influences / leads to / shapes
            < causes / determines / demonstrates that / proves

1. No silent move. Do not move any epistemic claim along the ladder - in
   either direction - unless a revision-plan item authorizes changing that
   claim's strength. Positioning/emphasis prose is fine while the verb's rung
   stays put. Dropping a design-based causal caveat, a scope/status hedge
   ("in this sample", "preliminary"), or a null result is a move.
2. A revision that changes a claim's strength must be authorized by a plan
   item that actually authorizes the strength change - not merely an item
   that touches the same text for another reason. A "clarify wording" item
   does not authorize `associated with` → `causes`.
3. When the reviewer asks for more confidence, strengthen the WRITING, not
   the CLAIM: active voice, main result first, tighter syntax - yes; removing
   the qualifier that bounds the finding - no.
4. Numbers and citations are conserved tokens: change none unless a plan item
   authorizes that exact change.
```

Add this line after the block [H, not measured]:

```
5. A move up the ladder also needs the new evidence (a filled placeholder, a claims-file value, or a new citation) in the same edit.
```

## 5. Token check commands

Run from the project root.
`paper-tool` is the plugin's `bin/paper-tool`; an agent runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_revision_token_conservation.py` with the same arguments.
Keep the `.tex` suffix on the copy: it tells the script to drop `%` comments (a `\%` stays text).

One section, before committing the revision:

```
F=paper/sections/evaluation.tex
git show HEAD:$F > "$TMPDIR/before.tex"
paper-tool check_revision_token_conservation pair --source "$TMPDIR/before.tex" --revision $F --strict
echo "exit=$?"
```

One section, after the revision is committed (`F` set as above):

```
git show HEAD~1:$F > "$TMPDIR/before.tex"
git show HEAD:$F > "$TMPDIR/after.tex"
paper-tool check_revision_token_conservation pair --source "$TMPDIR/before.tex" --revision "$TMPDIR/after.tex" --strict
```

Every section file (here `paper/sections`; use the folder `paper.sections_dir` names in `paper/tools/paper-tools.toml`, relative to the project root):

```
for F in paper/sections/*.tex; do
  git show HEAD:$F > "$TMPDIR/before.tex"
  paper-tool check_revision_token_conservation pair --source "$TMPDIR/before.tex" --revision $F --strict > "$TMPDIR/$(basename $F .tex).drift.json" || echo "delta: $F"
done
```

Built text (optional): copy the built text (`build.text` in the config; `paper-tool paper_config build.text` prints its path) to `$TMPDIR/main_before.txt` before you rebuild the paper and extract its text again, then run `pair` on the two `.txt` files; `[PENDING Pn]` fills are found there too.
A `\pendingcell{Pn}` table cell prints as a bare `Pn` in the built text, so its fill shows there as a number added; check table fills on the `.tex` files.

Authorize the deltas (`--authorize`), before committing:

1. Run the check without `--authorize` and list every delta and fill in its output.
2. Write one row per token the revision may change: token, authority and an optional note, separated by tab characters, with no header; a line starting with `#` is a comment.
   Copy each token as the output prints it, with JSON escapes undone (`\cite{key}`, not `\\cite{key}`).
3. Run the check with the rows.
   With `--authorize` the check is a gate and `--strict` is ignored: exit 0 only when every delta matches a row whose authority holds, a `claims:` row checks every fill, no row fails, and `fill_conflicts` is empty.

Example `$TMPDIR/authorize.tsv` (every token, id, path and key in it is illustrative):

```
# token	authority	note
312	claims:results/claims.json#counts.sample_jobs	P40, sample jobs
six	finding:1a2b3c4d	confirmed finding: the count was wrong
\cite{Beta2022}	decision:D13	owner decision drops this comparison
```

`$RUN` below is the folder of the review round whose adjudicator wrote `adjudication.md`; the `--decisions` file is the one where the project records owner decisions with their ids (`paper/notes/decisions.md` in this example).

```
paper-tool check_revision_token_conservation pair --source "$TMPDIR/before.tex" --revision $F \
  --authorize "$TMPDIR/authorize.tsv" \
  --findings "$RUN/adjudication.md" \
  --decisions paper/notes/decisions.md
echo "exit=$?"
```

The three authority forms:

- `finding:<id>`: the 8 lowercase hex characters that start a confirmed finding's id, as `adjudication.md` writes them; the id must appear as a whole word in a `--findings` file (the option repeats).
- `decision:<id>`: an owner decision id such as `D13`; it must appear as a whole word in a `--decisions` file (the option repeats).
- `claims:<path>#<dotted.json.key>`: only for a fill or an added number, and the only form that authorizes a fill.
  The path is relative to the working directory; the key is read from the left, and in an object each step takes the longest run of dotted parts that names a member, so `models.vendor-model-1.5.score.value` reaches the member `vendor-model-1.5` (in a list, a part is an index); the value there must equal the token once `%` and thousands separators are removed: `2.5%` matches `2.5` and `48,512` matches `48512`, but `20.3%` does not match `0.2034`.
  Point the key at the value the paper prints; an added number that no claims file holds can carry a finding or a decision row instead, a fill cannot.
  For a percent, point the key at the value as the paper prints it (already rounded), not at the raw ratio.

A finding or decision row authorizes its token in every delta and at any count; a `claims:` row authorizes only a fill or an added number with its token.
A row fails when its id is not found, its file or key is missing, or its value differs, and a failing row fails the run even when another row covers its token.

Read the JSON output:

- Exit 0, `"conserved": true`: no number, citation, key, target or placeholder was lost, changed or added, no strong word was added and no hedge dropped, and a passing `claims:` row checked every fill (so without `--authorize` any fill gives exit 1 under `--strict`).
- `fills`: each `{"placeholder": "Pn", "value": "..."}` is a placeholder replaced in place by a digit number; a number word in its place shows as a placeholder removed and a number added.
- `unverified_fills`: the fills that no passing `claims:` row checked; without `--authorize` that is every fill; write a `claims:` row from the registry row's source for each.
- `fill_conflicts`: `{"Pn": [values]}` when one placeholder was filled with two different values; exit 1; fix the wrong value.
- Exit 1 under `--strict`: some delta is non-empty (each entry needs a reason from section 3, step 7), a fill is unverified, or `fill_conflicts` is non-empty.
- `numbers_delta`: digit numbers, and the number words zero to twenty, thirty to ninety by tens, hundred, thousand, dozen, half and twice, lowercased (`twenty percent` is one token); the same count removed and added is a changed number.
- `placeholders_delta.removed` with no fill: a placeholder deleted or replaced by words; drop or update its registry row.
- `placeholders_delta.removed` plus `numbers_delta.added`: often a fill in a moved sentence that the aligner could not pair; check it by hand.
- `latex_keys_delta`: a `\cite{key}` dropped or added, or a `\ref{x}` or `\label{x}` changed.
- `strength_delta.strong_added`: strong words the revision adds (prove, proves, proven, demonstrate(s) that, shows that, causes, determines, guarantee(s), establish(es), confirm(s), always, never, cannot, all, every, first, only); apply section 3 to each sentence.
- `strength_delta.hedges_removed`: hedges the revision drops (suggest(s), may, might, indicate(s), at least, at most, about, approximately); apply section 3 to each sentence.
  A strong word removed or a hedge added is not reported, so a move down still needs the reader.
  A negated strong word counts as added: a new "does not prove equivalence" reports `prove`; authorize it with the finding or decision that asked for the caveat.
- `citations_delta` and `protected_terms_delta`: upstream's Markdown and author-year forms; empty for `.tex` input unless `--protected-terms` is given.
- `authorization` (only with `--authorize`): `authorized` (true exactly when the exit code is 0), `unauthorized` (each delta with no passing row and each fill with no passing `claims:` row: its delta, its side or placeholder, and its token) and `failing_rows` (each failing row with its line number and reason).

Hedges and wrong-but-valid keys still need the reader pass of section 3 and the `research-paper:claim-ref-alignment` seat: the word lists miss a hedge or a rung move written in other words, a `\cite` key can exist and still name a source that does not state the claim, and a `claims:` key can hold the right number for a different quantity.

## 6. Reviewer finding format

- A reviewer who finds a move writes one finding per `paper/tools/contract.md` section 6 (`finding_schema.json`).
- `lens`: `consistency`; `rule`: "CLAIM_DRIFT_GUARD section 3, step N".
- `evidence`: the new sentence quoted with its line; `failing_case`: the old wording, its rung, the new rung, and the missing evidence.
- `not_established`: "This shows the wording moved up the ladder, not that the stronger claim is false."

## 7. What was measured upstream

Source: `evals/heldout/revision_claim_drift/measurement-2026-08-07.json` and `runs/2026-08-07/`, read whole.

- Claim-strength or hedge drift in 7/16 revisions without the section 4 block and 1/16 with it (items: 4/8 to 1/8).
- Setup: 8 synthetic passages in 8 fields (`heldout_set.json` 0.1.0), 2 replicates per item and arm, reviser `claude-fable-5`, one judge (`gpt-5.6-sol`) plus blinded adjudication that could reject but never add flags, so the rates are lower bounds.
- It measures the prompt block given to a model reviser; it does not measure the token check or a human writer.
- The remaining guarded case (rp-03-G-r2) kept "no evidence of the expected operational advantage" and added "transparency showed no relation to how quickly teams delivered": absence of evidence restated as evidence of absence, with every protected phrase still present.
- Token check on the same 32 revisions: unauthorized deltas in 4/16 unguarded and 0/16 guarded; the control rp-07 showed only the authorized 0.17 to 0.21 in all 4 runs.
- 5 of the 8 drifted revisions were token-conserved (rp-02-U-r1, rp-02-U-r2, rp-05-U-r1, rp-06-U-r1, rp-03-G-r2): the token check does not see a rung move, so section 3 needs a reader.

## 8. Upstream scripts not taken

- `scripts/check_revision_claim_drift_suite_v2.py`: not needed; it checks the upstream eval suite's own files (hash-pinned run tree, rubric v2, subject-context and call-plan records) with jsonschema and reads no manuscript.
- `scripts/claim_strength_drift_disposition.py`: not needed; it records an author's authorize, restore or pause decision on drift findings in upstream's sidecar format bound to session-event files, and here a finding goes to `finding_schema.json` and the owner decision batch instead.

## What these checks do not establish

- A conserved token check shows that no number, key, target or placeholder was lost or changed; it does not show that a claim kept its rung, its hedges, its negation or its comparison direction.
- A recorded fill shows which number replaced which placeholder; it does not show that the number is the right value from the claims file.
- The ladder rule shows that a move was authorized by evidence in the same edit; it does not show that the evidence supports the new rung.

---

Attribution.
Taken from https://github.com/imbad0202/academic-research-skills at commit e79085d0d38609984ef8cfe0faf2d254aac9e0a9, license CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu, https://creativecommons.org/licenses/by-nc/4.0/ (non-commercial research use only).

- `shared/references/claim_strength_ladder.md`, lines 19-58: the ladder (L24-31), the "no silent move" rule and the same-rung tie rule (L21-22, L33-36), and the move and not-a-move lists (L40-58).
  Changes: the ladder is a table with an [H] column; the rule and lists are reworded as bullet lines, "roadmap item" becomes the authorization of section 3, and the upstream `→` arrows are written "to"; em dashes removed.
- `evals/heldout/revision_claim_drift/runs/2026-08-07/RUN_PLAN.md`, lines 72-95: the guard block in section 4, verbatim except that its five em dashes are written "-".
- Section 7 reports numbers read from `evals/heldout/revision_claim_drift/measurement-2026-08-07.json` and `runs/2026-08-07/` (deterministic, judge and adjudication records, `anon_map.json`, `RUN_NOTES.md`); no text is taken from them.
- Sections 3, 5, 6, the hedge list in section 2, line 5 after the block, and the [H] column are ours (written for a private research-paper project, 2026-09-29, and made generic for this plugin).
