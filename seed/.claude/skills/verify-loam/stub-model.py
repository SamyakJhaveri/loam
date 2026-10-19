#!/usr/bin/env python3
"""Scripted stand-in for the Anthropic Messages API: a real `claude -p` runs its real hooks at $0.

Usage: stub-model.py PORT [LOG]. PORT 0 picks a free port; the first stdout line is the bound port.
Point Claude Code at it with ANTHROPIC_BASE_URL=http://127.0.0.1:<port> and a dummy ANTHROPIC_API_KEY.
A POST to .../responses gets the OpenAI Responses wire instead, for `codex exec` with a custom
model provider whose base_url is http://127.0.0.1:<port>/v1.
Reply rule: a user prompt holding `STUB_BASH: cmd1 ;; cmd2` gets one Bash tool_use (Codex:
exec_command function_call) per command, in order, then the text `STUB DONE`; anything else gets
the text `OK`.
Every request is one JSON line in LOG (default stderr). Content-Length is the only request header
read, and no header is logged, so a credential the client sends is never read or written.
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stderr


def log(**fields):
    LOG.write(json.dumps({"t": time.strftime("%H:%M:%S"), **fields}) + "\n")
    LOG.flush()


def texts(msgs):
    for m in msgs:
        c = m.get("content")
        if isinstance(c, str):
            yield c
        else:
            for b in c or []:
                if b.get("type") == "text":
                    yield b.get("text", "")


def script(user_texts):
    cmds = []
    for t in user_texts:
        if "STUB_BASH:" in t:
            line = t.split("STUB_BASH:", 1)[1].split("\n", 1)[0]
            cmds = [c.strip() for c in line.split(";;") if c.strip()]
    return cmds


def plan(body):
    msgs = body.get("messages", [])
    done = sum(
        1
        for m in msgs
        if isinstance(m.get("content"), list)
        for b in m["content"]
        if b.get("type") == "tool_result"
    )
    cmds = script(texts(m for m in msgs if m.get("role") == "user"))
    has_bash = any(t.get("name") == "Bash" for t in body.get("tools", []))
    if cmds and has_bash and done < len(cmds):
        block = {
            "type": "tool_use",
            "id": f"toolu_stub_{done}",
            "name": "Bash",
            "input": {"command": cmds[done], "description": "stub step"},
        }
        return block, "tool_use"
    return {"type": "text", "text": "STUB DONE" if cmds else "OK"}, "end_turn"


def plan_responses(body):
    items = [i for i in body.get("input", []) if isinstance(i, dict)]
    done = sum(1 for i in items if i.get("type") == "function_call_output")
    cmds = script(
        b.get("text", "")
        for i in items
        if i.get("type") == "message" and i.get("role") == "user"
        for b in i.get("content") or []
        if isinstance(b, dict)
    )
    has_exec = any(t.get("name") == "exec_command" for t in body.get("tools", []))
    if cmds and has_exec and done < len(cmds):
        args = json.dumps({"cmd": cmds[done]})
        return {"type": "function_call", "call_id": f"call_stub_{done}", "name": "exec_command", "arguments": args}
    text = "STUB DONE" if cmds else "OK"
    return {"type": "message", "role": "assistant", "id": "msg_stub", "content": [{"type": "output_text", "text": text}]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        log(method="GET", path=self.path)
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        size = int(self.headers.get("content-length", 0))
        body = json.loads(self.rfile.read(size) or b"{}")
        if "count_tokens" in self.path:
            log(path=self.path, model=body.get("model"))
            return self.reply({"input_tokens": 10})
        if self.path.split("?")[0].endswith("/responses"):
            return self.answer_responses(body)
        block, stop = plan(body)
        log(
            path=self.path,
            model=body.get("model"),
            stream=body.get("stream"),
            tools=len(body.get("tools", [])),
            reply=block.get("input", {}).get("command") or block.get("text"),
        )
        usage = {
            "input_tokens": 1,
            "output_tokens": 1,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        }
        msg = {
            "id": "msg_stub",
            "type": "message",
            "role": "assistant",
            "model": body.get("model"),
            "stop_reason": None,
            "stop_sequence": None,
            "usage": usage,
        }
        if not body.get("stream"):
            return self.reply({**msg, "content": [block], "stop_reason": stop})
        if block["type"] == "tool_use":
            start = dict(block, input={})
            delta = {
                "type": "input_json_delta",
                "partial_json": json.dumps(block["input"]),
            }
        else:
            start = dict(block, text="")
            delta = {"type": "text_delta", "text": block["text"]}
        events = [
            {"type": "message_start", "message": {**msg, "content": []}},
            {"type": "content_block_start", "index": 0, "content_block": start},
            {"type": "content_block_delta", "index": 0, "delta": delta},
            {"type": "content_block_stop", "index": 0},
            {
                "type": "message_delta",
                "delta": {"stop_reason": stop, "stop_sequence": None},
                "usage": {"output_tokens": 5},
            },
            {"type": "message_stop"},
        ]
        self.stream(events)

    def answer_responses(self, body):
        item = plan_responses(body)
        log(
            path=self.path,
            model=body.get("model"),
            stream=body.get("stream"),
            tools=len(body.get("tools", [])),
            reply=json.loads(item.get("arguments", "{}")).get("cmd") or item["content"][0]["text"],
        )
        usage = {
            "input_tokens": 1,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 1,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 2,
        }
        self.stream(
            [
                {"type": "response.created", "response": {"id": "resp_stub"}},
                {"type": "response.output_item.done", "output_index": 0, "item": item},
                {"type": "response.completed", "response": {"id": "resp_stub", "usage": usage}},
            ]
        )

    def stream(self, events):
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        for event in events:
            sse = f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"
            self.wfile.write(sse.encode())
        self.wfile.flush()

    def reply(self, obj):
        raw = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


server = ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Handler)
print(server.server_address[1], flush=True)
server.serve_forever()
