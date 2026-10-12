import json
from pathlib import Path


def read_transcript(run: Path) -> dict:
    """A run's transcript as its turns' usage and its tool calls in order.

    Every `*.jsonl` under `<run>/transcript/` is read, subagents' included, and
    their records merged by timestamp. A turn is one assistant message: records
    sharing a `message.id` are one turn, numbered from 1, and its usage is read
    once. Each tool call carries its turn, name, input, the cwd recorded with
    it, and the text of its result.
    """
    paths = sorted(run.glob("transcript/**/*.jsonl"))
    if not paths:
        raise FileNotFoundError(f"no transcript under {run / 'transcript'}")
    records = []
    for path in paths:
        for line in path.read_text().splitlines():
            try:
                records.append(json.loads(line))
            except ValueError:
                continue
    records.sort(key=lambda r: r.get("timestamp") or "")
    turns, usage, calls, results = {}, [], [], {}
    for record in records:
        message = record.get("message") or {}
        content = message.get("content")
        if record.get("type") == "assistant":
            if message.get("id") not in turns:
                turns[message.get("id")] = len(turns) + 1
                usage.append(message.get("usage") or {})
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_use":
                    calls.append({
                        "id": block.get("id"),
                        "turn": turns[message.get("id")],
                        "name": block.get("name"),
                        "input": block.get("input") or {},
                        "cwd": record.get("cwd") or "/target",
                    })
        elif record.get("type") == "user" and isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_result":
                    text = block.get("content")
                    if isinstance(text, list):
                        text = "\n".join(part.get("text", "") for part in text if isinstance(part, dict))
                    results[block.get("tool_use_id")] = text or ""
    for call in calls:
        call["result"] = results.get(call.pop("id"), "")
    return {"usage": usage, "calls": calls}
