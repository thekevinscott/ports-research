import json
import os
import subprocess
from pathlib import Path

import pytest
from werkzeug.wrappers import Response

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

VECTORS = {
    "a = 1\n": [1.0, 0.0, 0.0],
    "\na = 1\n": [1.0, 0.0, 0.0],
    "b = 2\n": [0.0, 1.0, 0.0],
    "c = 3\n": [2.0, 0.0, 0.0],
    "const t = 1;\n": [0.0, 0.0, 1.0],
}


def embeddings_handler(request):
    body = json.loads(request.data)
    return Response(
        json.dumps({"model": body["model"], "data": [{"embedding": VECTORS[body["input"]]}]}),
        content_type="application/json",
    )


@pytest.fixture
def embeddings_server(httpserver):
    httpserver.expect_request("/v1/embeddings", method="POST").respond_with_handler(embeddings_handler)
    return httpserver


@pytest.fixture
def run_cli(embeddings_server):
    env = {**os.environ, "GENERATE_EMBEDDING_BASE_URL": embeddings_server.url_for("/v1")}

    def run(*args):
        return subprocess.run(
            ["uv", "run", "measure-embedding", *args],
            cwd=PACKAGE_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    return run
