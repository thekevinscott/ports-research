import json
from pathlib import Path

LIMIT = 2000


def transcript_item(files: list[Path]) -> str:
    """The assistant's text blocks and tool calls, in order and numbered; tool results dropped."""

    def cut(value):
        if isinstance(value, str) and len(value) > LIMIT:
            return f"{value[:LIMIT]}[{len(value) - LIMIT} more characters cut]"
        if isinstance(value, dict):
            return {key: cut(v) for key, v in value.items()}
        if isinstance(value, list):
            return [cut(v) for v in value]
        return value

    steps = []
    for path in files:
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if record.get("type") != "assistant":
                continue
            for block in record["message"]["content"]:
                if block["type"] == "text":
                    steps.append(f"text: {block['text']}")
                elif block["type"] == "tool_use":
                    steps.append(f"{block['name']}: {json.dumps(cut(block['input']), ensure_ascii=False)}")
    return "".join(f"[{n}] {step}\n" for n, step in enumerate(steps, 1))
