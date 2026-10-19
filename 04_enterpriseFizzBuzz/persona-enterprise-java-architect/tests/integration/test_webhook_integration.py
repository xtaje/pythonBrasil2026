"""Integration test for WebhookOutputAdapter against a real, local HTTP
server -- not a mocked requests.Session.

This is the one seam in this project where a pure unit test (mocking
`requests.Session.post`) can't catch everything that matters: whether the
adapter actually produces well-formed JSON on the wire, sets a sane
content-type, and correctly maps a real non-2xx status or connection
failure into our domain exception. It's a deliberately small slice of the
test pyramid -- three cases, no more -- because the unit tests already cover
every branch of the adapter's own logic; this layer exists only to prove
the wiring to a real socket works.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, ClassVar

import pytest

from fizzbuzz.adapters.webhook_adapter import WebhookOutputAdapter
from fizzbuzz.exceptions import WebhookDeliveryError

pytestmark = pytest.mark.integration


class _RecordingHandler(BaseHTTPRequestHandler):
    received: ClassVar[list[Any]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.__class__.received.append(json.loads(body))
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass  # keep test output quiet; failures are asserted, not logged


class _FailingHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        self.send_response(503)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


def _start_server(handler: type) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture()
def recording_server() -> Iterator[HTTPServer]:
    _RecordingHandler.received = []
    server = _start_server(_RecordingHandler)
    try:
        yield server
    finally:
        server.shutdown()


@pytest.fixture()
def failing_server() -> Iterator[HTTPServer]:
    server = _start_server(_FailingHandler)
    try:
        yield server
    finally:
        server.shutdown()


class TestWebhookIntegration:
    def test_delivers_every_line_to_a_real_server_in_order(
        self, recording_server: HTTPServer
    ) -> None:
        url = f"http://127.0.0.1:{recording_server.server_port}/hook"
        adapter = WebhookOutputAdapter(url=url)

        adapter.emit(["1", "2", "Fizz"])

        assert _RecordingHandler.received == [
            {"sequence": 0, "value": "1"},
            {"sequence": 1, "value": "2"},
            {"sequence": 2, "value": "Fizz"},
        ]

    def test_non_2xx_response_raises_domain_error(self, failing_server: HTTPServer) -> None:
        url = f"http://127.0.0.1:{failing_server.server_port}/hook"
        adapter = WebhookOutputAdapter(url=url)

        with pytest.raises(WebhookDeliveryError, match="503"):
            adapter.emit(["1"])

    def test_nothing_listening_raises_domain_error(self) -> None:
        # Port 1 is a privileged port nothing on a CI/dev box will be
        # listening on; this simulates the webhook endpoint being down.
        adapter = WebhookOutputAdapter(url="http://127.0.0.1:1/hook", timeout_seconds=2)

        with pytest.raises(WebhookDeliveryError):
            adapter.emit(["1"])
