"""FizzBuzz - usable as a CLI tool or imported as a library.

Library usage:
    from fizzbuzz import fizzbuzz_value, fizzbuzz_range

    fizzbuzz_value(15)        # "FizzBuzz"
    fizzbuzz_range(1, 20)     # ["1", "2", "Fizz", "4", "Buzz", ...]

CLI usage: see cli.py, or run `fizzbuzz --help`.
"""

from .core import fizzbuzz_range, fizzbuzz_value
from .cli import main

__all__ = ["fizzbuzz_value", "fizzbuzz_range", "main"]
