"""fizzbuzz: FizzBuzz as a small, deliberately boring reusable library.

Public API surface -- anything not exported here is an implementation detail
and may change without a version bump.

Output adapters (`fizzbuzz.adapters.*`) are intentionally NOT re-exported
here: importing them pulls in extra dependencies (`requests`) or touches the
filesystem/PATH (speech engine detection) that a caller who only wants
`fizzbuzz()` as pure logic shouldn't have to pay for. Import the adapter
module you need directly, e.g. `from fizzbuzz.adapters.stdout_adapter
import StdoutOutputAdapter`.
"""

from __future__ import annotations

from fizzbuzz.core import DEFAULT_RULES, Rule, fizzbuzz, fizzbuzz_range
from fizzbuzz.exceptions import (
    FizzBuzzError,
    OutputDeliveryError,
    SpeechDeliveryError,
    SpeechEngineNotFoundError,
    WebhookDeliveryError,
)
from fizzbuzz.ports import OutputPort

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_RULES",
    "FizzBuzzError",
    "OutputDeliveryError",
    "OutputPort",
    "Rule",
    "SpeechDeliveryError",
    "SpeechEngineNotFoundError",
    "WebhookDeliveryError",
    "__version__",
    "fizzbuzz",
    "fizzbuzz_range",
]
