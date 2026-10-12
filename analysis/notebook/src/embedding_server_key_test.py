import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from src.embedding_server_key import embedding_server_key

ROUTER = [
    {"id": "other", "status": {"args": ["--model", "/models/other.gguf", "--pooling", "mean"]}},
    {"id": "m", "status": {"args": ["--embeddings", "--pooling", "last", "--model", "/models/m-q8_0.gguf"]}},
]


@pytest.fixture
def serve():
    """A /v1 server whose GET /v1/models lists the given entries."""
    servers = []

    def start(entries: list[dict]) -> str:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = json.dumps({"data": entries}).encode()
                self.send_response(200 if self.path == "/v1/models" else 404)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        return f"http://127.0.0.1:{server.server_port}/v1"

    yield start
    for server in servers:
        server.shutdown()


def describe_embedding_server_key():
    def it_names_the_model_file_and_pooling_the_server_runs_the_model_with(serve):
        assert embedding_server_key(serve(ROUTER) + "/", "m") == "m-q8_0-pooling-last"

    def it_refuses_a_server_that_does_not_report_pooling(serve):
        with pytest.raises(RuntimeError, match="pooling"):
            embedding_server_key(serve([{"id": "/models/m-q8_0.gguf", "meta": {}}]), "m")

    def it_refuses_a_server_that_does_not_list_the_model(serve):
        with pytest.raises(RuntimeError, match="absent"):
            embedding_server_key(serve(ROUTER), "absent")
