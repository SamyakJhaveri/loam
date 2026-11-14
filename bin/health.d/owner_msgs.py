"""Extract the owner's messages from Claude Code session transcripts, whole, with a stable id each.

Usage: python3 -I extract_user_msgs.py <projects-dir> <out-dir> [host-label] [--since ISO-TIME]

Writes <out-dir>/<host>-messages.jsonl (one JSON object per message, oldest first) and <out-dir>/<host>-<day>.md
(the same messages for a person to read). A message is one of:
- typed: a user record Samyak typed (not a tool result, meta record, compact summary or sidechain);
- command: a slash command he typed with words after it, as "/name words" (one with no words is left out);
- dialog: one answer he gave in a question dialog (AskUserQuestion), with the question it answers.
Fields: id (<host>:<session uuid>:<record uuid>, plus #<n> for the n-th answer of one dialog), host, session, record,
parent (the record it replies to; two typed records with one parent are an edit and its original), file, line (1-based
line of the record in the .jsonl), ts, kind, text (never cut), before (the assistant's last text before it, never cut),
question (dialog only). A record seen in two files (a resumed session copies its history) is written once.
--since keeps only messages with a timestamp after ISO-TIME.
"""
import glob
import json
import os
import re
import sys

argv = sys.argv[1:]
since = ""
if "--since" in argv:
    i = argv.index("--since")
    since = argv[i + 1]
    del argv[i:i + 2]
src, out = argv[0], argv[1]
host = argv[2] if len(argv) > 2 else "mac"
os.makedirs(out, exist_ok=True)
SR = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
NOT_HIS_PREFIX = ("<task-notification>", "<local-command-stdout>", "<local-command-stderr>", "Caveat:",
               "[Request interrupted", "This session is being continued")
CMD = re.compile(r"<command-(?:name|message)>([^<]*)</command-(?:name|message)>(?:.*?<command-args>(.*?)</command-args>)?", re.S)


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


rows, seen = [], set()
for f in sorted(glob.glob(os.path.join(src, "*.jsonl"))):
    last_asst = ""
    try:
        fh = open(f, encoding="utf-8", errors="replace")
    except OSError:
        continue
    with fh:
        for n, line in enumerate(fh, 1):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t, msg = r.get("type"), r.get("message") or {}
            if t == "assistant":
                txt = text_of(msg.get("content")).strip()
                if txt:
                    last_asst = txt
                continue
            if t != "user" or r.get("isMeta") or r.get("isCompactSummary") or r.get("isSidechain"):
                continue
            sid, uid, ts = r.get("sessionId") or os.path.basename(f)[:-6], r.get("uuid", ""), r.get("timestamp", "")
            if (sid, uid) in seen or (since and ts <= since):
                continue
            seen.add((sid, uid))
            base = {"host": host, "session": sid, "record": uid, "parent": r.get("parentUuid"), "file": f,
                    "line": n, "ts": ts, "before": last_asst}
            tur = r.get("toolUseResult")
            answers = tur.get("answers") if isinstance(tur, dict) else None
            if isinstance(answers, dict):
                notes = tur.get("annotations") if isinstance(tur.get("annotations"), dict) else {}
                for i, (q, a) in enumerate(answers.items(), 1):
                    extra = (notes.get(q) or {}).get("notes") if isinstance(notes.get(q), dict) else None
                    rows.append({**base, "id": f"{host}:{sid}:{uid}#{i}", "kind": "dialog", "question": q,
                                 "text": str(a) + (f"\n\nNotes: {extra}" if extra else "")})
                continue
            c = msg.get("content")
            if isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
                continue
            txt = SR.sub("", text_of(c)).strip()
            cmd = CMD.match(txt)
            if cmd:  # a slash command: his words are its arguments; one with none (/exit, /model) says nothing
                if (cmd.group(2) or "").strip():
                    rows.append({**base, "id": f"{host}:{sid}:{uid}", "kind": "command",
                                 "text": f"{cmd.group(1)} {cmd.group(2).strip()}"})
                continue
            if not txt or txt.startswith(NOT_HIS_PREFIX):
                continue
            rows.append({**base, "id": f"{host}:{sid}:{uid}", "kind": "typed", "text": txt})

rows.sort(key=lambda x: (x["ts"], x["id"]))
tmp = os.path.join(out, f".{host}-messages.jsonl.tmp")
with open(tmp, "w") as fh:
    for x in rows:
        fh.write(json.dumps(x, ensure_ascii=False) + "\n")
os.replace(tmp, os.path.join(out, f"{host}-messages.jsonl"))
by_day = {}
for x in rows:
    by_day.setdefault(x["ts"][:10], []).append(x)
for day, items in by_day.items():
    with open(os.path.join(out, f"{host}-{day}.md"), "w") as fh:
        for x in items:
            q = f"Question: {x['question']}\n\n" if x["kind"] == "dialog" else ""
            fh.write(f"\n### {x['ts'][:16]} {x['kind']} {x['id']} ({os.path.basename(x['file'])}:{x['line']})\n"
                     f"Assistant just before: {x['before']}\n\n{q}OWNER: {x['text']}\n")
kinds = [sum(1 for x in rows if x["kind"] == k) for k in ("typed", "command", "dialog")]
print(f"{len(rows)} owner messages over {len(by_day)} days: {kinds[0]} typed, {kinds[1]} commands with words, "
      f"{kinds[2]} dialog answers")
