"""The output port.

This is the one abstraction the application core and the CLI depend on for
delivering results. New delivery mechanisms (Slack, a message queue, a log
sink) get added by writing a new adapter under `fizzbuzz.adapters` and
wiring it into the CLI's factory -- nothing in `core.py` or in an existing
adapter has to change. That's the entire justification for the extra
indirection here: it's cheap now, and it's exactly the seam that gets asked
for eventually on any project that lives long enough to grow a second output
target, which this one already has three of on day one.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable


class OutputPort(ABC):
    """A destination that a sequence of FizzBuzz lines can be delivered to."""

    @abstractmethod
    def emit(self, lines: Iterable[str]) -> None:
        """Deliver ``lines``, in order.

        Implementations must translate any transport-specific failure into a
        subclass of :class:`fizzbuzz.exceptions.OutputDeliveryError` rather
        than letting it escape the adapter -- callers of this port should
        never need to know or catch `subprocess.CalledProcessError` or
        `requests.RequestException`.
        """
        raise NotImplementedError
