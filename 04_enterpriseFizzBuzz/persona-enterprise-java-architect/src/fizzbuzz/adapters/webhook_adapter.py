"""The webhook adapter: POSTs each line as a small JSON payload to a
configured URL.

One HTTP request per line, rather than a single batched request: it keeps
the payload shape trivial and predictable for whatever sits on the
receiving end (a test endpoint, a logging sink, a Slack-style incoming
webhook), at the cost of N round trips for N lines. For the volumes this
program produces that trade is the right one. If this were ever driving
thousands of lines a batched or streaming endpoint would be worth
revisiting -- but that's a real requirement to design around when it shows
up, not something to guess at now.

Fails loudly on the first error: a non-2xx response or a network failure
raises immediately rather than silently dropping lines and moving on. "The
webhook silently ate half the output" is exactly the kind of bug that stays
invisible until someone downstream asks where their data went.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

import requests

from fizzbuzz.exceptions import WebhookDeliveryError
from fizzbuzz.ports import OutputPort

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SECONDS = 5.0


class WebhookOutputAdapter(OutputPort):
    """POSTs ``{"sequence": <int>, "value": <str>}`` per line to ``url``."""

    def __init__(
        self,
        url: str,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
    ) -> None:
        if not url:
            raise ValueError("url must be a non-empty string")
        self._url = url
        self._timeout_seconds = timeout_seconds
        # A caller-supplied session is the seam integration/unit tests use
        # to point this at a fake or local server without monkeypatching
        # module-level requests calls.
        self._session = session if session is not None else requests.Session()

    def emit(self, lines: Iterable[str]) -> None:
        for sequence, line in enumerate(lines):
            self._post(sequence, line)

    def _post(self, sequence: int, line: str) -> None:
        payload = {"sequence": sequence, "value": line}
        try:
            response = self._session.post(self._url, json=payload, timeout=self._timeout_seconds)
        except requests.RequestException as exc:
            raise WebhookDeliveryError(f"Failed to POST {payload!r} to {self._url}: {exc}") from exc

        if not response.ok:
            raise WebhookDeliveryError(
                f"Webhook at {self._url} rejected {payload!r} with status "
                f"{response.status_code}: {response.text[:200]!r}"
            )

        logger.debug(
            "delivered sequence=%d value=%r to %s (status=%s)",
            sequence,
            line,
            self._url,
            response.status_code,
        )
