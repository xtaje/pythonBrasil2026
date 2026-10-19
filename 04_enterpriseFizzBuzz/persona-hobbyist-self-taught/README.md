# fizzbuzz

My take on FizzBuzz, but I wanted to make it more interesting than just
printing to the terminal, so it can also **say the results out loud**
or **POST them to a webhook url**. Built with `uv` because that seems
to be the way everyone's doing Python projects now, and I wrote some
`pytest` tests for the actual logic parts.

## What it does

Runs FizzBuzz from `--start` to `--end` (default 1 to 100) and sends
the output one of three ways:

- `stdout` (default) - just prints it
- `speak` - reads it out loud using `pyttsx3` (works offline!)
- `webhook` - POSTs a JSON blob like `{"results": [...]}` to a url you give it

## Setup

```
uv sync
```

That installs everything, including `pytest` for the tests.

## Running it

```
uv run fizzbuzz
uv run fizzbuzz --start 1 --end 20
uv run fizzbuzz --output speak --start 1 --end 15
uv run fizzbuzz --output webhook --webhook-url https://webhook.site/your-id-here
```

## Using it as a library

The whole point of setting it up as a package instead of just one script
is so you can also do this in your own code:

```python
from fizzbuzz import fizzbuzz, fizzbuzz_range

fizzbuzz(15)              # "FizzBuzz"
fizzbuzz_range(1, 10)     # ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz"]
```

## Running the tests

```
uv run pytest
```

## Notes to self / things I'm not 100% sure about

- I only actually tested `--output speak` on my Mac. `pyttsx3`'s docs say
  it works on Linux too but needs `espeak` installed as a system package
  first (not something `pip`/`uv` can install for you). Haven't tried it
  on an actual Linux box so ¯\\_(ツ)_/¯.
- Installing `pyttsx3` pulled in a genuinely huge pile of `pyobjc`
  framework packages on my Mac (like, a lot). That surprised me, but it
  seems to be normal for how `pyttsx3` talks to macOS's speech stuff, so
  I'm leaving it.
- I didn't write automated tests for the speak or webhook output
  functions since they actually do something in the real world (make
  noise / hit the network) and I don't really know how to fake that
  stuff in a test yet. I tested those manually by running the CLI and
  checking it worked, and pulled the "build the JSON payload" bit into
  its own function (`build_payload`) so at least that part is covered
  by a real test.
- `uv init --package` set `requires-python = ">=3.14"` automatically
  based on whatever Python it found on my machine - not sure that's
  actually necessary for code this simple, but didn't see a reason to
  fight it.
