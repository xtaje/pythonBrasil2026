"""Domain logic for FizzBuzz.

This module has zero knowledge of the CLI, stdout, speech, or HTTP -- it is
the one piece of this project with an actual business rule in it, and it is
kept free of I/O on purpose so it can be unit tested exhaustively and reused
by any caller (CLI, another service, a REPL) without dragging in argparse,
subprocess, or requests.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """A single substitution rule: multiples of ``divisor`` become ``word``.

    Frozen and validated at construction so an invalid Rule can never exist
    half-built somewhere in a collection -- fail at the point of creation,
    not three function calls later when someone tries to use it.
    """

    divisor: int
    word: str

    def __post_init__(self) -> None:
        if self.divisor <= 0:
            raise ValueError(f"divisor must be a positive integer, got {self.divisor!r}")
        if not self.word:
            raise ValueError("word must be a non-empty string")


# The classic rules. Exposed as a tuple (immutable) rather than a list so
# nothing downstream can accidentally mutate the shared default -- a mutable
# default here would be the kind of bug that only shows up once, in
# production, after some caller does `DEFAULT_RULES.append(...)` thinking
# they're working with their own copy.
DEFAULT_RULES: tuple[Rule, ...] = (Rule(3, "Fizz"), Rule(5, "Buzz"))


def fizzbuzz(n: int, rules: Sequence[Rule] = DEFAULT_RULES) -> str:
    """Return the FizzBuzz value for a single positive integer ``n``.

    Rules are evaluated in the order given and their words concatenated, so
    the classic case (n=15) yields "Fizz" + "Buzz" = "FizzBuzz". If no rule
    matches, the number itself is returned as a string.
    """
    if n <= 0:
        raise ValueError(f"n must be a positive integer, got {n!r}")

    matched = "".join(rule.word for rule in rules if n % rule.divisor == 0)
    return matched if matched else str(n)


def fizzbuzz_range(start: int, end: int, rules: Sequence[Rule] = DEFAULT_RULES) -> Iterator[str]:
    """Return a lazy iterator of FizzBuzz values for the inclusive range [start, end].

    Deliberately NOT implemented as a generator function (no ``yield`` in
    this body). A generator function defers *all* of its code, guard clauses
    included, until the caller starts iterating -- which means a naive
    version of this function would let `fizzbuzz_range(10, 1)` be called
    without error and only blow up later, deep inside whatever loop first
    calls `next()`, far from the actual mistake. Returning a generator
    *expression* from a plain function keeps the validation eager (it runs
    when you call this function) while keeping the iteration itself lazy
    (no need to materialize a list for a range of a million numbers).
    """
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    return (fizzbuzz(n, rules) for n in range(start, end + 1))
