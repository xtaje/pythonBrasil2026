from fizzbuzz.core import fizzbuzz, fizzbuzz_range


def test_fizzbuzz_basic_cases():
    # just checking the main rules all work right, all in one test
    # since they're all kind of testing the same function
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(2) == "2"
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(6) == "Fizz"
    assert fizzbuzz(10) == "Buzz"
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(30) == "FizzBuzz"


def test_fizzbuzz_range_short():
    assert fizzbuzz_range(1, 5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_range_backwards_still_works():
    # tried this by accident while messing around and it errored out
    # with an empty list, so I added the swap in fizzbuzz_range to fix it
    assert fizzbuzz_range(5, 1) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_range_single_number():
    assert fizzbuzz_range(15, 15) == ["FizzBuzz"]
