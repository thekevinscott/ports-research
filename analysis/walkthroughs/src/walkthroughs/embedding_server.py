import json
from urllib.request import urlopen


def embedding_server(url: str, model: str) -> dict:
    """The url, the requested model, and the server's /models entry for it: a llama.cpp router lists each model's --model and --pooling in status.args."""
    with urlopen(f"{url.rstrip('/')}/models", timeout=30) as response:
        entries = json.load(response)["data"]
    server = next((e for e in entries if e["id"] == model), entries[0] if len(entries) == 1 else None)
    return {"url": url, "model": model, "server": server}
