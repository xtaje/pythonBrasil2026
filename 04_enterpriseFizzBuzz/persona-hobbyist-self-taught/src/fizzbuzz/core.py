# the actual fizzbuzz logic lives here, separate from the CLI stuff
# so other people (or future me) can just `import fizzbuzz` and use
# these functions without dealing with argparse or any of that


def fizzbuzz(n: int) -> str:
    """Classic fizzbuzz for a single number.

    - multiples of 3 -> "Fizz"
    - multiples of 5 -> "Buzz"
    - multiples of both -> "FizzBuzz"
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
    """Runs fizzbuzz() over a range of numbers, start and end inclusive.

    So fizzbuzz_range(1, 5) gives you ['1', '2', 'Fizz', '4', 'Buzz'].
    """
    if start > end:
        # not gonna overthink this, just swap them so it still works
        # if someone passes them backwards
        start, end = end, start
    return [fizzbuzz(n) for n in range(start, end + 1)]
