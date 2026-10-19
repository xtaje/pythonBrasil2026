"""Unit tests for WebhookOutputAdapter, mocked at the requests.Session
boundary (the port/adapter seam) rather than patching individual internal
calls. The real-wire-format cases (correct JSON, actual HTTP status
handling) live in tests/integration/test_webhook_integration.py against a
real local server -- a mock can't catch "we sent the wrong content-type"
because a mock will happily accept whatever we hand it.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from fizzbuzz.adapters.webhook_adapter import WebhookOutputAdapter
from fizzbuzz.exceptions import WebhookDeliveryError


def _response(status_code: int, ok: bool, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.ok = ok
    response.text = text
    return response


class TestConstruction:
    def test_rejects_empty_url(self) -> None:
        with pytest.raises(ValueError, match="url"):
            WebhookOutputAdapter(url="")


class TestEmit:
    def test_posts_json_payload_per_line_with_incrementing_sequence(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.return_value = _response(200, ok=True)
        adapter = WebhookOutputAdapter(url="https://example.test/hook", session=session)

        adapter.emit(["Fizz", "Buzz"])

        assert session.post.call_count == 2
        first_args, first_kwargs = session.post.call_args_list[0]
        assert first_args == ("https://example.test/hook",)
        assert first_kwargs["json"] == {"sequence": 0, "value": "Fizz"}
        _, second_kwargs = session.post.call_args_list[1]
        assert second_kwargs["json"] == {"sequence": 1, "value": "Buzz"}

    def test_passes_configured_timeout(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.return_value = _response(200, ok=True)
        adapter = WebhookOutputAdapter(
            url="https://example.test/hook", timeout_seconds=1.5, session=session
        )

        adapter.emit(["Fizz"])

        assert session.post.call_args.kwargs["timeout"] == 1.5

    def test_non_ok_response_raises_domain_error(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.return_value = _response(500, ok=False, text="server exploded")
        adapter = WebhookOutputAdapter(url="https://example.test/hook", session=session)

        with pytest.raises(WebhookDeliveryError, match="500"):
            adapter.emit(["Fizz"])

    def test_network_failure_raises_domain_error(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.side_effect = requests.ConnectionError("dns lookup failed")
        adapter = WebhookOutputAdapter(url="https://example.test/hook", session=session)

        with pytest.raises(WebhookDeliveryError, match="dns lookup failed"):
            adapter.emit(["Fizz"])

    def test_stops_at_first_failure_rather_than_swallowing_it(self) -> None:
        session = MagicMock(spec=requests.Session)
        session.post.side_effect = [_response(200, ok=True), requests.ConnectionError("boom")]
        adapter = WebhookOutputAdapter(url="https://example.test/hook", session=session)

        with pytest.raises(WebhookDeliveryError):
            adapter.emit(["Fizz", "Buzz", "FizzBuzz"])

        assert session.post.call_count == 2  # third line never attempted
