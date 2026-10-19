"""Core FizzBuzz logic.

Kept dependency-free on purpose: this is the one part of the project that's
actually "business logic" (such as it is for FizzBuzz), and it's the part
most likely to get reused or embedded elsewhere. Everything else (CLI,
output backends) builds on top of this.
"""

from __future__ import annotations

from collections.abc import Iterator


def fizzbuzz_value(
    n: int,
    *,
    fizz: int = 3,
    buzz: int = 5,
    fizz_word: str = "Fizz",
    buzz_word: str = "Buzz",
) -> str:
    """Return the FizzBuzz string for a single number.

    Divisible by both `fizz` and `buzz` -> "{fizz_word}{buzz_word}"
    Divisible by `fizz` only -> fizz_word
    Divisible by `buzz` only -> buzz_word
    Otherwise -> str(n)
    """
    if fizz == 0 or buzz == 0:
        raise ValueError("fizz and buzz divisors must be non-zero")

    hits = ""
    if n % fizz == 0:
        hits += fizz_word
    if n % buzz == 0:
        hits += buzz_word
    return hits or str(n)


def fizzbuzz_range(
    start: int,
    end: int,
    *,
    fizz: int = 3,
    buzz: int = 5,
    fizz_word: str = "Fizz",
    buzz_word: str = "Buzz",
) -> Iterator[str]:
    """Yield FizzBuzz values for the inclusive range [start, end].

    A generator rather than a list so callers doing something like piping
    to stdout don't have to materialize huge ranges in memory. Callers that
    want a list can just wrap it: list(fizzbuzz_range(1, 100)).
    """
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    for n in range(start, end + 1):
        yield fizzbuzz_value(n, fizz=fizz, buzz=buzz, fizz_word=fizz_word, buzz_word=buzz_word)
