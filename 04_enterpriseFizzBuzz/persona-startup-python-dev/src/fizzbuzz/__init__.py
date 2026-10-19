"""fizzbuzz: FizzBuzz as a reusable library and a CLI.

Library usage:

    from fizzbuzz import fizzbuzz_value, fizzbuzz_range

    fizzbuzz_value(15)          # "FizzBuzz"
    list(fizzbuzz_range(1, 20)) # ["1", "2", "Fizz", ...]

For custom output (spoken, webhook), see fizzbuzz.output.
"""

from .core import fizzbuzz_range, fizzbuzz_value

__all__ = ["fizzbuzz_value", "fizzbuzz_range"]
__version__ = "0.1.0"
