"""Domain exceptions.

Every output adapter translates whatever it fails with (a subprocess error,
a requests.RequestException, ...) into one of these. Callers of the library
-- the CLI included -- should only ever need to catch FizzBuzzError; they
should never need to know that the speech adapter happens to be implemented
with subprocess, or that the webhook adapter happens to be implemented with
requests. That's the whole point of having a port: the implementation detail
of *how* an adapter fails shouldn't leak past its boundary.
"""

from __future__ import annotations


class FizzBuzzError(Exception):
    """Base class for every error this package raises deliberately."""


class OutputDeliveryError(FizzBuzzError):
    """An output adapter could not deliver its payload."""


class SpeechEngineNotFoundError(OutputDeliveryError):
    """No supported text-to-speech engine is available on this platform."""


class SpeechDeliveryError(OutputDeliveryError):
    """A text-to-speech engine was found but failed while speaking a line."""


class WebhookDeliveryError(OutputDeliveryError):
    """A webhook POST failed: network error, timeout, or non-2xx response."""
