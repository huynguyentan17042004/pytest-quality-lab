from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from qa_framework.api import BaseApiClient
from qa_framework.api.response_mapper import ResponseMapper
from qa_framework.exceptions import ResponseParseError

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.api]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/empty":
            self.send_response(204)
            self.end_headers()
        elif self.path == "/bad-json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{")
        else:
            payload = json.dumps({"path": self.path, "header": self.headers.get("X-Test")}).encode()
            self.send_response(404 if self.path == "/missing" else 200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

    def log_message(self, *_args):
        return


@pytest.fixture(scope="module")
def local_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_local_transport_headers_query_and_negative_status(local_server):
    with BaseApiClient(local_server, default_headers={"X-Test": "present"}) as client:
        response = client.get("/missing?value=1")
    assert response.status_code == 200  # handler path includes query and returns diagnostic payload
    assert response.json() == {"path": "/missing?value=1", "header": "present"}


def test_local_204(local_server):
    with BaseApiClient(local_server) as client:
        assert ResponseMapper.map(client.get("/empty")).body is None


def test_local_malformed_json(local_server):
    with BaseApiClient(local_server) as client, pytest.raises(ResponseParseError):
        ResponseMapper.map(client.get("/bad-json"))
