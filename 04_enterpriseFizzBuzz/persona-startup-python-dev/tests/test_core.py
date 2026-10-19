"""Core FizzBuzz logic. This is the one part of this project that's actually
"business logic" — worth real coverage, unlike the plumbing around it."""

import pytest

from fizzbuzz.core import fizzbuzz_range, fizzbuzz_value


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, "1"),
        (2, "2"),
        (3, "Fizz"),
        (5, "Buzz"),
        (6, "Fizz"),
        (9, "Fizz"),
        (10, "Buzz"),
        (15, "FizzBuzz"),
        (30, "FizzBuzz"),
        (100, "Buzz"),
    ],
)
def test_fizzbuzz_value_classic_cases(n, expected):
    assert fizzbuzz_value(n) == expected


def test_fizzbuzz_value_custom_words_and_divisors():
    # e.g. a "Buzzfizz at 7/4" variant someone asked for once
    assert fizzbuzz_value(28, fizz=4, buzz=7, fizz_word="Boo", buzz_word="Baz") == "BooBaz"
    assert fizzbuzz_value(4, fizz=4, buzz=7) == "Fizz"


def test_fizzbuzz_value_rejects_zero_divisor():
    with pytest.raises(ValueError):
        fizzbuzz_value(10, fizz=0)


def test_fizzbuzz_range_matches_expected_sequence():
    assert list(fizzbuzz_range(1, 15)) == [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]


def test_fizzbuzz_range_is_inclusive_of_both_ends():
    result = list(fizzbuzz_range(3, 5))
    assert result == ["Fizz", "4", "Buzz"]


def test_fizzbuzz_range_single_value():
    assert list(fizzbuzz_range(15, 15)) == ["FizzBuzz"]


def test_fizzbuzz_range_rejects_start_after_end():
    with pytest.raises(ValueError):
        list(fizzbuzz_range(10, 1))


def test_fizzbuzz_range_is_lazy():
    """It's a generator, not a list — shouldn't do work until iterated."""
    gen = fizzbuzz_range(1, 10**9)  # would be way too slow/expensive if eager
    assert next(gen) == "1"
