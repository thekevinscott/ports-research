import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from walkthroughs.embedding_server import embedding_server

ROUTER = [
    {"id": "other", "status": {"args": ["--model", "/models/other.gguf"]}},
    {"id": "m", "status": {"args": ["--embeddings", "--pooling", "last", "--model", "/models/m.gguf"]}},
]


@pytest.fixture
def serve():
    """A /v1 server whose GET /v1/models lists the given entries."""
    servers = []

    def start(entries: list[dict]) -> str:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = json.dumps({"data": entries}).encode() if self.path == "/v1/models" else b""
                self.send_response(200 if body else 404)
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


def describe_embedding_server():
    def it_records_the_url_the_requested_model_and_the_servers_entry_for_it(serve):
        url = serve(ROUTER)
        assert embedding_server(url, "m") == {"url": url, "model": "m", "server": ROUTER[1]}

    def it_takes_a_single_model_servers_only_entry_whatever_its_id(serve):
        url = serve([{"id": "/models/m.gguf", "meta": {"n_params": 1}}])
        assert embedding_server(url + "/", "m")["server"] == {"id": "/models/m.gguf", "meta": {"n_params": 1}}

    def it_records_no_entry_when_a_router_does_not_list_the_model(serve):
        assert embedding_server(serve(ROUTER), "absent")["server"] is None
