# shellcheck shell=bash
# bin/factory.d/review.sh - the verifier and the learn step, sourced by bin/factory from its frozen copy
# (docs/research/2026-11-12-distbench-priming/design-pick.md, unit U4; requirements (d) and (h)). It uses bin/factory's own
# helpers (call_start, call_end, charged, record, assert_caps, log, scrub, alert, codex_*), so it runs only sourced into it.
#
#   verify_round ROUND  after the reviewer and the Codex review: one Opus call reproduces each blocking finding at
#                       GRADED_SHA; CONFIRMED and PARTLY go to round-N.fixes (each source blocks once per ticket),
#                       REJECTED to round-N.rejected. Returns 1 when it queued a fix, else 0.
#   learn_run [STATUS MESSAGE]
#                       from any terminal path: writes $RUN/followups.md and, when it has a line, drafts one ticket
#                       into $RUN/learn/ with two read-only reviews and the verifier on them. Always returns 0, never
#                       calls finish, and runs once per run directory.
#
# Ledger roles: verifier, learn-writer, learn-review. Files: round-N.findings.json, round-N.verify.json,
# round-N.rejected, followups.md, learn/ (draft.md, draft.json, review-fable.json, review-codex.md, findings.json,
# verify.json). The prompts and schemas are this file's siblings: verify.md, verify.schema.json, learn.md, learn.schema.json.

REVIEW_D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# Step 4 of the audit skill is the method the verifier follows; it reads the file by path.
AUDIT_DIR="$ROOT/cultivation/marketplace/sam-cc-setup/skills/audit"

# Blocking: a reviewer high or medium, a Codex critical or high (the rule run_review and run_codex_review apply).
FINDING_BLOCKS='(.source == "reviewer" and (.severity == "high" or .severity == "medium"))
  or (.source == "codex" and (.severity == "critical" or .severity == "high"))'
# The line a finding gets in round-N.fixes: the reviewer's and the Codex review's lines as they were before the verifier.
FINDING_LINE='def fixline: "- \(.file):\(.line) " + (if .source == "codex" then "[\(.severity)] " else "" end) + .claim;'

# Both reviews of a round as one list, each finding with its id; an unparseable review contributes nothing, since
# its fallback finding is not a defect anyone can reproduce (it drafts the PR, as before).
review_findings() { # round -> JSON array on stdout
  { jq -c 'if .unparseable == true then [] else [(.findings // []) | to_entries[] | {id: "reviewer-\(.key)", source: "reviewer",
      severity: .value.severity, file: (.value.file // "?"), line: (.value.line // 0),
      claim: ((.value.defect // "?") + " Fix: " + (.value.fix // "-"))}] end' "$RUN/round-$1.review.json" 2> /dev/null || echo '[]'
    if [ "$CODEX_REVIEW" = yes ]; then
      jq -c 'if .unparseable == true then [] else [(.findings // []) | to_entries[] | {id: "codex-\(.key)", source: "codex",
        severity: .value.severity, file: (.value.file // "?"), line: (.value.line_start // 0),
        claim: ((.value.title // "?") + ": " + (.value.body // "") + " Fix: " + (.value.recommendation // "-"))}] end' \
        "$RUN/round-$1.codex-review.json" 2> /dev/null || echo '[]'
    fi
  } | jq -cs 'add // []'
}

# One read-only or verifier Claude call as call_json makes it: the run's private config dir, the frozen role settings,
# --setting-sources '', and a ledger row. The verifier gets Bash in auto mode; every other role gets Read, Grep, Glob.
# A stuck call stops the run unless REVIEW_NO_FINISH is set (learn_run, which a terminal path may call).
review_claude() { # round role model effort dir prompt schema-text out [add-dir...] -> 0 when out holds the reply object
  local round="$1" role="$2" model="$3" effort="$4" dir="$5" pf="$6" schema="$7" out="$8" raw tools=Read,Grep,Glob
  local mode=() adds=() d
  shift 8
  for d in "$@"; do adds+=(--add-dir "$d"); done
  [ "$role" = verifier ] && { tools=Bash,Read,Grep,Glob; mode=(--permission-mode auto); }
  raw="${out%.json}.raw.json"
  rm -f "$out" "$raw"
  mkdir -p -m 700 "$RUN/grader-config" && chmod 700 "$RUN/grader-config" || { log "could not make $RUN/grader-config"; return 1; }
  while :; do
    CALL_ACCOUNT=$(active_account)
    log "$role call: model=$model effort=$effort dir=$dir"
    call_start "$dir" ${TIMEOUT_G[@]+"${TIMEOUT_G[@]}"} "$ROOT/bin/claude-account" exec env CLAUDE_CONFIG_DIR="$RUN/grader-config" \
        claude -p --model "$model" --effort "$effort" --tools "$tools" ${mode[@]+"${mode[@]}"} ${adds[@]+"${adds[@]}"} \
        --strict-mcp-config --disable-slash-commands --no-session-persistence --json-schema "$schema" \
        --max-budget-usd "$GRADER_BUDGET_USD" --setting-sources '' --settings "$RUN/frozen/role-settings.json" \
        --output-format json < "$pf" > "$raw" 2>> "$LOG"
    call_end "$role" || log "$role exited non-zero"
    if [ -z "$CALL_STUCK" ] && limit_wait "$raw"; then continue; fi
    break
  done
  record "$round" "$role" "$model" "$(charged "$raw" "$GRADER_BUDGET_USD")"
  if [ -n "$CALL_STUCK" ]; then
    [ -n "${REVIEW_NO_FINISH:-}" ] || finish stopped-environment "$CALL_STUCK"
    return 1
  fi
  grader_reply "$raw" | jq -e 'if type == "object" then . else error end' > "$out" 2> /dev/null && return 0
  rm -f "$out"
  log "$role reply absent or not one JSON object; see $raw"
  return 1
}

# A needs-you alert that also reaches a file ticket, which notify skips; the text passes scrub first.
review_alert() { # message
  log "[needs-you] $1"
  printf '%s' "$1" | scrub | { alert --level needs-you --source factory --project "$(printf '%s' "${REPO#*/}" | tr 'A-Z' 'a-z')" \
    --run "${ISSUE:+issue $ISSUE}${ISSUE:-$KEY}" "$(cat)"; } >> "$LOG" 2>&1 || log "the needs-you alert failed; see bin/alert's line above"
}

# The verifier on the blocking findings of a findings file, in a detached worktree of repo at sha. Writes out as
# {sha, findings: [{id, verdict, cmd, output, note}]} with exactly the blocking ids. A finding the verifier did not
# settle is UNVERIFIED, never CONFIRMED: a failed call, an id it left out, or a REJECTED without cmd and output
# (audit step 4: a finding is not dismissed with a defense nobody located and read).
verify_findings() { # findings.json out.json repo sha round scope-line [add-dir...] -> 0 when no finding is UNVERIFIED
  local fj="$1" out="$2" repo="$3" sha="$4" round="$5" scope="$6" wt="${WORKTREE:-$RUN/wt}-verify" pf reply blocking why=""
  local schema
  shift 6
  pf="${out%.json}.prompt.md"; reply="${out%.json}.reply.json"; schema="${out%.json}.schema.json"
  blocking=$(jq -c "[.[] | select($FINDING_BLOCKS) | {id, severity, file, line, claim}]" "$fj")
  rm -f "$reply"
  if [ "$(jq length <<< "$blocking")" -gt 0 ]; then
    git -C "$repo" worktree remove --force "$wt" > /dev/null 2>&1
    git -C "$repo" worktree prune > /dev/null 2>&1
    if ! git -C "$repo" worktree add --detach "$wt" "$sha" > /dev/null 2>&1; then
      why="could not add the verifier worktree $wt at ${sha:0:8}"
    else
      { sed -e "s|<sha>|$sha|g" -e "s|<audit>|$AUDIT_DIR|g" -e "s|<scope>|$scope|g" "$REVIEW_D/verify.md"
        printf '\n## Findings\n\n%s\n' "$FENCE"; jq '.' <<< "$blocking"; printf '%s\n' "$FENCE"; } > "$pf"
      # The model's schema leaves out UNVERIFIED: only the supervisor writes it.
      jq '.properties.findings.items.properties.verdict.enum -= ["UNVERIFIED"]' "$REVIEW_D/verify.schema.json" > "$schema"
      review_claude "$round" verifier "$GRADER_MODEL" high "$wt" "$pf" "$(cat "$schema")" "$reply" "$AUDIT_DIR" "$@" \
        || why="the verifier call failed or gave no reply object"
      git -C "$repo" worktree remove --force "$wt" > /dev/null 2>&1
    fi
  fi
  [ -s "$reply" ] || echo '{}' > "$reply"
  jq -n --arg sha "$sha" --argjson b "$blocking" --arg why "$why" --slurpfile r "$reply" '
    ((($r[0].findings // []) | map({(.id): .}) | add) // {}) as $by
    | def unverified($n): {verdict: "UNVERIFIED", cmd: "", output: "", note: $n};
    {sha: $sha, findings: [$b[] | .id as $id | $by[$id] as $e | {id: $id} + (
      if $why != "" then unverified($why + "; nothing reproduced it")
      elif $e == null then unverified("the verifier gave no verdict for this id")
      elif ($e.verdict | IN("CONFIRMED", "PARTLY")) then {verdict: $e.verdict, cmd: ($e.cmd // ""), output: ($e.output // ""), note: ($e.note // "")}
      elif $e.verdict == "REJECTED" and ($e.cmd // "") != "" and ($e.output // "") != "" then {verdict: "REJECTED", cmd: $e.cmd, output: $e.output, note: ($e.note // "")}
      else unverified("the verifier rejected it without cmd and output: " + ($e.note // "")) end)]}' > "$out"
  [ -z "$why" ] || log "verifier: $why"
  ! jq -e 'any(.findings[]; .verdict == "UNVERIFIED")' "$out" > /dev/null
}

verify_round() { # round -> 1 when it queued a fix
  local round="$1" fj="$RUN/round-$1.findings.json" vj="$RUN/round-$1.verify.json" rej="$RUN/round-$1.rejected" src lines queued=0 n
  rm -f "$vj" "$rej"
  review_findings "$round" > "$fj"
  n=$(jq "[.[] | select($FINDING_BLOCKS)] | length" "$fj")
  if [ "$n" -eq 0 ]; then
    jq -n --arg sha "$GRADED_SHA" '{sha: $sha, findings: []}' > "$vj"
    log "verifier: no blocking finding in round $round; no call"
    return 0
  fi
  assert_caps
  stop_requested && finish stopped "FACTORY_STOP before the verifier call"
  verify_findings "$fj" "$vj" "$WORKTREE" "$GRADED_SHA" "$round" \
    "it holds the ticket's change, the commits $(cat "$RUN/base.sha" 2> /dev/null | cut -c1-12)...$GRADED_SHA." \
    || review_alert "$(ticket_name): the verifier did not settle every blocking finding of round $round; they go to the worker marked UNVERIFIED. Read $vj"
  log "verifier round $round: $(jq -r '[.findings[].verdict] | group_by(.) | map("\(.[0])=\(length)") | join(" ")' "$vj")"
  # Each finding joined with its verdict, one JSON object per line.
  lines=$(jq -c --slurpfile v "$vj" "([\$v[0].findings[] | {(.id): .}] | add // {}) as \$by
    | .[] | select(\$by[.id] != null) | . + {v: \$by[.id]}" "$fj")
  jq -r "$FINDING_LINE"' select(.v.verdict == "REJECTED") | fixline + " REJECTED: " + .v.note | gsub("\\s*\n\\s*"; " ")' <<< "$lines" > "$rej"
  [ -s "$rej" ] || rm -f "$rej"
  jq -r 'select(.v.verdict == "REJECTED" and (.severity == "high" or .severity == "critical"))
    | "\(.source) [\(.severity)] \(.file):\(.line)"' <<< "$lines" | while IFS= read -r n; do
    review_alert "$(ticket_name): the verifier rejected the $n finding in round $round; read its cmd and output in $vj"
  done
  for src in reviewer codex; do
    # Highs before mediums for the reviewer, as run_review queued them; critical before high for Codex.
    n=$(jq -r --arg s "$src" "$FINDING_LINE"' select(.source == $s and (.v.verdict | IN("CONFIRMED", "PARTLY", "UNVERIFIED")))
      | [(if .severity == "critical" or .severity == "high" then 0 else 1 end), (fixline
         + (if .v.verdict == "PARTLY" then " (verifier: PARTLY: " + .v.note + ")"
            elif .v.verdict == "UNVERIFIED" then " (UNVERIFIED: " + .v.note + ")" else "" end))] | @json' <<< "$lines" \
      | jq -rs 'sort_by(.[0]) | .[][1]')
    [ -n "$n" ] || continue
    if { [ "$src" = reviewer ] && [ "$REVIEW_BLOCKED" = 1 ]; } || { [ "$src" = codex ] && [ "$CODEX_REVIEW_BLOCKED" = 1 ]; }; then
      log "the $src already blocked once on this ticket; its verified blocking findings make the PR a draft and are filed as issues"
      continue
    fi
    if [ "$src" = reviewer ]; then REVIEW_BLOCKED=1; else CODEX_REVIEW_BLOCKED=1; fi
    printf '%s\n' "$n" >> "$RUN/round-$round.fixes"
    queued=1
  done
  [ "$queued" = 0 ]
}

# ---- learn ------------------------------------------------------------------

# The run's follow-ups, one `- <source> [<severity>] <file>:<line> <text>` line each: a failed run's own exit (factory),
# the last round's judge backlog, its blocking findings no verifier rejected, its mutation survivors, and every
# round's rejected findings.
followups() { # [status message] -> lines on stdout
  local k checks="$RUN/round-$ROUND.checks" fails
  {
    if [ -n "${1:-}" ] && [ "$1" != pr-opened ]; then
      fails=$([ -f "$checks" ] && fail_names "$checks" | paste -sd, - | sed 's/,/, /g')
      printf -- '- factory [%s] -:0 %s%s\n' "$1" "${2:-}" "${fails:+; failing checks in round $ROUND: $fails}"
    fi
    jq -r '.backlog[]? | "- judge-backlog [-] -:0 " + .' "$RUN/round-$ROUND.judge.json" 2> /dev/null
    review_findings "$ROUND" | jq -r --slurpfile v <(cat "$RUN/round-$ROUND.verify.json" 2> /dev/null || echo '{}') \
      "([\$v[0].findings[]? | {(.id): .verdict}] | add // {}) as \$by
      | .[] | select(($FINDING_BLOCKS) and \$by[.id] != \"REJECTED\") | \"- \(.source) [\(.severity)] \(.file):\(.line) \(.claim)\""
    jq -r '.mutants[]? | select(.result == "survived")
      | "- mutation [survived] \(.path):\(.line) \(.operator): \(.after) (was \(.before))"' "$RUN/round-$ROUND.mutation.json" 2> /dev/null
    for k in $(seq 1 "$ROUND"); do
      [ -f "$RUN/round-$k.verify.json" ] && [ -f "$RUN/round-$k.findings.json" ] || continue
      jq -r --slurpfile v "$RUN/round-$k.verify.json" '([$v[0].findings[] | {(.id): .}] | add // {}) as $by
        | .[] | select($by[.id].verdict == "REJECTED")
        | "- rejected [\(.severity)] \(.file):\(.line) \(.claim) REJECTED: \($by[.id].note)"' "$RUN/round-$k.findings.json"
    done
  } | sed 's/[[:space:]]*$//' | tr -s '\n' | awk 'NF && !seen[$0]++'
}

# Room for one more learn call under the daily budget, which bin/factory's assert_caps would otherwise enforce by
# stopping the run; learn only stops itself.
learn_room() { # role
  if jq -en --argjson a "$(daily_spent)" --argjson b "$GRADER_BUDGET_USD" --argjson c "$DAILY_BUDGET_USD" '($a + $b) > $c' > /dev/null; then
    log "learn: the $1 call could pass the daily budget of $DAILY_BUDGET_USD usd ($(daily_spent) spent today); learn stops here"
    return 1
  fi
  if stop_requested; then log "learn: FACTORY_STOP before the $1 call; learn stops here"; return 1; fi
}

learn_brief() { # section target-dir draft-dir -> the filled learn.md section on stdout
  awk -v want="## $1" '$0 == want {inb=1; next} /^## /{inb=0} inb {print}' "$REVIEW_D/learn.md" \
    | sed -e "s|<target>|$2|g" -e "s|<target-name>|$(printf '%s' "${REPO#*/}" | tr 'A-Z' 'a-z')|g" \
          -e "s|<root>|$ROOT|g" -e "s|<draft>|$3/draft.md|g" -e "s|<draft-json>|$3/draft.json|g"
}

# The draft's own lint: bin/factory lint for a Loam ticket, the target's check_factory for a distbench one.
learn_lint() { # repo dir draft -> the lint output on stdout
  if [ "$1" = loam ]; then
    "$ROOT/bin/factory" lint "$3" 2>&1 && echo "lint: OK"
  elif [ -f "$2/bin/check_tickets.py" ]; then
    python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1] + "/bin"); import check_tickets as c
p = c.check_factory(open(sys.argv[2]).read()); print("\n".join(p) or "check_factory: OK"); sys.exit(bool(p))' "$2" "$3" 2>&1
  else
    echo "no ticket lint for $1"
  fi
}

# Codex's read-only review of the draft, as run_codex_review calls Codex; its findings are the reply's lines of the
# form `- [severity] file:line claim`.
learn_codex() { # dir prompt out -> 0 when out has text
  local ch trust skills_off mcp_off start rc jsonl="${3%.md}.jsonl" res="${3%.md}.result.json"
  ch=$(codex_home) && trust=$(codex_trust "$1") && skills_off=$(codex_skills_off) && mcp_off=$(codex_mcp_off "$1" "$ch" -c "$trust") \
    || { log "learn: no Codex review (no factory login, or its settings could not be read)"; return 1; }
  rm -f "$3"
  start=$SECONDS
  call_start "$1" ${TIMEOUT_G[@]+"${TIMEOUT_G[@]}"} env "${CODEX_UNSET[@]}" PATH="$CODEX_PATH:$PATH" CODEX_HOME="$ch" codex exec "${CODEX_OFF[@]}" --json -m "$CODEX_MODEL" -c model_reasoning_effort="$GRADER_EFFORT" -c "$trust" -c "$skills_off" -c skills.include_instructions=false -c "$mcp_off" -o "$3" -s read-only "$2" > "$jsonl" < /dev/null
  call_end "learn Codex review"; rc=$?
  [ "$rc" -eq 0 ] || log "learn: the Codex review exited $rc"
  codex_result "$jsonl" "$rc" "$(( (SECONDS - start) * 1000 ))" > "$res"
  record "$ROUND" learn-review "$CODEX_MODEL" "$res" 0 0 0 0 1
  [ -s "$3" ]
}

learn_run() { # [status message] -> 0; drafts at most one ticket per run directory
  local d="$RUN/learn" f="$RUN/followups.md" dir repo rdir sha model effort prompt n REVIEW_NO_FINISH=1
  [ -e "$d/ran" ] && { log "learn: already ran for this run directory"; return 0; }
  mkdir -p "$d" || { log "learn: could not make $d"; return 0; }
  followups "$@" > "$f"
  if ! grep -q . "$f"; then log "learn: no follow-ups; no draft"; return 0; fi
  log "learn: $(grep -c . "$f") follow-up(s) in $f"
  dir=${WORKTREE:-}; [ -d "$dir" ] || dir=$TARGET
  # Marked only once the writer may run, so a launch stopped at the daily cap leaves the draft to the next launch.
  learn_room learn-writer && : > "$d/ran" || return 0
  { learn_brief Writer "$dir" "$d"; printf '\n## Follow-ups\n\n%s\n' "$FENCE"; cat "$f"; printf '%s\n' "$FENCE"
    printf '\n## Ticket\n\n%s\n' "$FENCE"; cat "$RUN/frozen/issue.md" 2> /dev/null; printf '\n%s\n' "$FENCE"; } > "$d/writer.prompt.md"
  review_claude "$ROUND" learn-writer "$GRADER_MODEL" high "$dir" "$d/writer.prompt.md" "$(cat "$REVIEW_D/learn.schema.json")" \
    "$d/writer.json" "$ROOT" || { log "learn: the writer gave no draft"; return 0; }
  jq '{repo, title, source_line}' "$d/writer.json" > "$d/draft.json"
  jq -r '.body' "$d/writer.json" > "$d/draft.md"
  repo=$(jq -r .repo "$d/draft.json")
  if [ "$repo" = loam ]; then rdir=$ROOT; else rdir=$dir; fi
  sha=$(git -C "$rdir" rev-parse HEAD 2> /dev/null)
  learn_lint "$repo" "$rdir" "$d/draft.md" > "$d/lint.txt"
  prompt=$(learn_brief Review "$dir" "$d")
  model=$(grader_model reviewer); effort=$(grader_effort reviewer)
  learn_room learn-review || return 0
  printf '%s\n' "$prompt" > "$d/review.prompt.md"
  review_claude "$ROUND" learn-review "$model" "$effort" "$rdir" "$d/review.prompt.md" "$(cat "$RUN/frozen/reviewer.schema.json")" \
    "$d/review-fable.json" "$d" "$ROOT" || log "learn: no reply from the $model review"
  stop_requested || learn_codex "$rdir" "$prompt
Reply in Markdown. Put each finding on one line of exactly this form, and nothing else on a line that starts with '- [':
- [critical|high|medium|low] <file>:<line> <the failure it causes, and the check that reproduces it>" "$d/review-codex.md" || log "learn: no Codex review"
  { jq -c '[(.findings // []) | to_entries[] | {id: "reviewer-\(.key)", source: "reviewer", severity: .value.severity,
      file: (.value.file // "?"), line: (.value.line // 0), claim: ((.value.defect // "?") + " Fix: " + (.value.fix // "-"))}]' \
      "$d/review-fable.json" 2> /dev/null || echo '[]'
    sed -nE 's/^- \[(critical|high|medium|low)\] ([^ ]+):([0-9]+) (.+)$/\1\t\2\t\3\t\4/p' "$d/review-codex.md" 2> /dev/null \
      | jq -cRs '[split("\n")[] | select(. != "") | split("\t")] | to_entries
          | map({id: "codex-\(.key)", source: "codex", severity: .value[0], file: .value[1], line: (.value[2] | tonumber), claim: .value[3]})'
  } | jq -s 'add // []' > "$d/findings.json"
  n=$(jq "[.[] | select($FINDING_BLOCKS)] | length" "$d/findings.json")
  if [ "$n" -gt 0 ] && learn_room verifier; then
    verify_findings "$d/findings.json" "$d/verify.json" "$rdir" "$sha" "$ROUND" \
      "the drafted ticket under review is $d/draft.md; the findings are about that draft." "$d" || :
  elif [ "$n" -eq 0 ]; then
    jq -n --arg sha "$sha" '{sha: $sha, findings: []}' > "$d/verify.json"
  fi
  review_alert "$(ticket_name): learn drafted a $repo ticket, \"$(jq -r .title "$d/draft.json")\", from $(grep -c . "$f") follow-up(s); \
$(tail -n 1 "$d/lint.txt"); $n blocking review finding(s), verifier: $(jq -r '[.findings[]?.verdict] | group_by(.) | map("\(.[0])=\(length)") | join(" ") | if . == "" then "none" else . end' "$d/verify.json" 2> /dev/null || echo "not run"). Read $d/draft.md"
  return 0
}
