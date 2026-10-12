import json
import os
import subprocess
import threading
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FAKE_CLAUDE = Path(__file__).resolve().parent / "fake_claude.py"
WALKTHROUGH = {
    "entry_points": [
        {
            "name": "parse_grammar",
            "happy_path": ["split the grammar into rules", "build the graph of rules", "return the parser"],
            "error_paths": ["raise when the root rule is missing"],
            "invariants": ["rules are keyed by name"],
        }
    ]
}


@pytest.fixture
def calls(tmp_path):
    """Every call the fake claude received: argv, cwd, whether it saw an API key, and its prompt."""
    log = tmp_path / "calls.jsonl"

    def read():
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    read.log = log
    return read


@pytest.fixture
def run_cli(tmp_path, calls):
    bin_directory = tmp_path / "bin"
    bin_directory.mkdir()
    (bin_directory / "claude").symlink_to(FAKE_CLAUDE)

    def run(*args, walkthrough=WALKTHROUGH):
        env = {
            **os.environ,
            "PATH": f"{bin_directory}{os.pathsep}{os.environ['PATH']}",
            "ANTHROPIC_API_KEY": "sk-must-not-reach-claude",
            "FAKE_CLAUDE_LOG": str(calls.log),
            "FAKE_CLAUDE_WALKTHROUGH": json.dumps(walkthrough),
        }
        return subprocess.run(["uv", "run", "walkthroughs", *[str(a) for a in args]], cwd=PACKAGE_ROOT, capture_output=True, text=True, env=env)

    return run


@pytest.fixture
def embeddings_url():
    """A local OpenAI-compatible /v1/embeddings server: each word of the input hashed into one of 64 dimensions."""
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(body)
            vector = [0.0] * 64
            for word in body["input"].lower().split():
                vector[int(sha256(word.encode()).hexdigest(), 16) % 64] += 1.0
            payload = json.dumps({"model": body["model"], "data": [{"embedding": vector}]}).encode()
            self.send_response(200 if self.path == "/v1/embeddings" else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/v1"
    yield type("Server", (str,), {"requests": requests})(url)
    server.shutdown()


@pytest.fixture
def make_walkthrough(tmp_path):
    def make(name, entry_points):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps({"walkthrough": {"entry_points": entry_points}}))
        return path

    return make
