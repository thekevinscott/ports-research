import json
from pathlib import Path
from urllib.request import urlopen


def embedding_server_key(url: str, model: str) -> str:
    """`<model file>-pooling-<pooling>` from the server's /models entry for model: a llama.cpp router lists both in status.args."""
    with urlopen(f"{url.rstrip('/')}/models", timeout=30) as response:
        entries = json.load(response)["data"]
    # A single-model server lists its one model under the file path, whatever the request names.
    entry = next((e for e in entries if e["id"] == model), entries[0] if len(entries) == 1 else None)
    if entry is None:
        raise RuntimeError(f"{url} does not list {model}")
    args = entry.get("status", {}).get("args", [])
    if "--model" not in args or "--pooling" not in args:
        raise RuntimeError(f"{url} does not report the model file and pooling for {model}; the embedding cache is keyed on both")
    return f"{Path(args[args.index('--model') + 1]).stem}-pooling-{args[args.index('--pooling') + 1]}"
