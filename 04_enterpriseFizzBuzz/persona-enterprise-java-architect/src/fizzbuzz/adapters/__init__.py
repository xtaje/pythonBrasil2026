"""Concrete OutputPort adapters.

Deliberately not re-exported from `fizzbuzz/__init__.py`: importing
`fizzbuzz.adapters.webhook_adapter` pulls in `requests`, and a caller who
only wants the pure `fizzbuzz()` / `fizzbuzz_range()` functions as a library
shouldn't pay for a dependency they never use. Import the specific adapter
module you need.
"""
