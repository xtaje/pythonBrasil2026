"""The stdout adapter: the simplest OutputPort, and the reference every
other adapter's tests get compared against because it has essentially no
external failure modes worth simulating.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING

from fizzbuzz.ports import OutputPort

if TYPE_CHECKING:
    from typing import TextIO


class StdoutOutputAdapter(OutputPort):
    """Writes each line to a text stream (stdout by default), one per line."""

    def __init__(self, stream: TextIO | None = None) -> None:
        # NOT `stream: TextIO = sys.stdout` in the signature: a default
        # argument value is evaluated exactly once, at function-definition
        # time (i.e. at module import), so it would bind to whatever
        # `sys.stdout` happened to be at import time. That's invisible in
        # normal use but breaks the moment something reassigns
        # `sys.stdout` after import -- which is precisely what pytest's
        # `capsys` fixture does. Resolving it here, at call time, is the
        # only version of "default to stdout" that's actually correct.
        self._stream = stream if stream is not None else sys.stdout

    def emit(self, lines: Iterable[str]) -> None:
        for line in lines:
            print(line, file=self._stream)
