"""Core FizzBuzz logic.

This is the "library" part of the project - just plain functions with no
printing or I/O in them, so other code (or other projects) can import and
reuse them without getting stdout/webhook/etc. stuff along for the ride.
"""

from __future__ import annotations


def fizzbuzz_value(n: int) -> str:
    """Return the FizzBuzz string for a single number.

    Rules:
    - multiples of 3 -> "Fizz"
    - multiples of 5 -> "Buzz"
    - multiples of both 3 and 5 -> "FizzBuzz"
    - anything else -> the number itself, as a string
    """
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def fizzbuzz_range(start: int, end: int) -> list[str]:
    """Return FizzBuzz results for every number from start to end, inclusive.

    Raises ValueError if start > end, since that's almost always a mistake
    on the caller's part (e.g. args swapped).
    """
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    return [fizzbuzz_value(n) for n in range(start, end + 1)]
