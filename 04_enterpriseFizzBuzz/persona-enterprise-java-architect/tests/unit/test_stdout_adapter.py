from __future__ import annotations

import io

from fizzbuzz.adapters.stdout_adapter import StdoutOutputAdapter


def test_emits_each_line_newline_terminated_in_order() -> None:
    buffer = io.StringIO()
    adapter = StdoutOutputAdapter(stream=buffer)

    adapter.emit(["1", "2", "Fizz"])

    assert buffer.getvalue() == "1\n2\nFizz\n"


def test_emit_with_no_lines_writes_nothing() -> None:
    buffer = io.StringIO()
    adapter = StdoutOutputAdapter(stream=buffer)

    adapter.emit([])

    assert buffer.getvalue() == ""


def test_emit_accepts_any_iterable_not_just_a_list() -> None:
    buffer = io.StringIO()
    adapter = StdoutOutputAdapter(stream=buffer)

    adapter.emit(str(n) for n in range(3))

    assert buffer.getvalue() == "0\n1\n2\n"
