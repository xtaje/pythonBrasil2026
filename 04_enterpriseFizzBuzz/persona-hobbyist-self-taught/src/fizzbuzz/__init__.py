# makes it so you can do `from fizzbuzz import fizzbuzz, fizzbuzz_range`
# without having to know it actually lives in core.py
from fizzbuzz.core import fizzbuzz, fizzbuzz_range
from fizzbuzz.output import output_stdout, output_speak, output_webhook

__all__ = [
    "fizzbuzz",
    "fizzbuzz_range",
    "output_stdout",
    "output_speak",
    "output_webhook",
]
