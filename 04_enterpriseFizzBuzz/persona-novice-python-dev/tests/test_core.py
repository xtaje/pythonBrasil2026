import pytest

from fizzbuzz.core import fizzbuzz_range, fizzbuzz_value


def test_fizzbuzz_value_multiple_of_three():
    assert fizzbuzz_value(3) == "Fizz"


def test_fizzbuzz_value_multiple_of_five():
    assert fizzbuzz_value(5) == "Buzz"


def test_fizzbuzz_value_multiple_of_both():
    assert fizzbuzz_value(15) == "FizzBuzz"


def test_fizzbuzz_value_regular_number():
    assert fizzbuzz_value(7) == "7"


# Parametrize is nice here so I don't have to write a separate test
# function for every single number I want to check.
@pytest.mark.parametrize(
    "n, expected",
    [
        (1, "1"),
        (3, "Fizz"),
        (5, "Buzz"),
        (9, "Fizz"),
        (10, "Buzz"),
        (15, "FizzBuzz"),
        (30, "FizzBuzz"),
        (45, "FizzBuzz"),
    ],
)
def test_fizzbuzz_value_parametrized(n, expected):
    assert fizzbuzz_value(n) == expected


def test_fizzbuzz_range_basic():
    assert fizzbuzz_range(1, 15) == [
        "1",
        "2",
        "Fizz",
        "4",
        "Buzz",
        "Fizz",
        "7",
        "8",
        "Fizz",
        "Buzz",
        "11",
        "Fizz",
        "13",
        "14",
        "FizzBuzz",
    ]


def test_fizzbuzz_range_single_number():
    # start and end the same should just give back that one value
    assert fizzbuzz_range(5, 5) == ["Buzz"]


def test_fizzbuzz_range_start_greater_than_end_raises():
    with pytest.raises(ValueError):
        fizzbuzz_range(10, 1)


def test_fizzbuzz_value_negative_number():
    # Not sure this was in the original spec, but negative numbers are
    # still divisible by 3/5 so this should behave the same way.
    assert fizzbuzz_value(-15) == "FizzBuzz"
