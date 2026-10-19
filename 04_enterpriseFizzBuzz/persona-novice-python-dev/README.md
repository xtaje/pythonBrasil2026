# fizzbuzz

Classic FizzBuzz. Works as a CLI tool or as a library you can import.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) to manage dependencies.

```
uv sync
```

## CLI usage

```
uv run fizzbuzz --start 1 --end 20
uv run fizzbuzz --start 1 --end 20 --output speak
uv run fizzbuzz --start 1 --end 20 --output webhook --webhook-url https://example.com/hook
```

If you don't pass `--start`/`--end` it defaults to 1-100. `--output` defaults to `stdout`.

## Library usage

```python
from fizzbuzz import fizzbuzz_value, fizzbuzz_range

fizzbuzz_value(15)      # "FizzBuzz"
fizzbuzz_range(1, 5)    # ["1", "2", "Fizz", "4", "Buzz"]
```

## Tests

```
uv run pytest
```

## Notes / things I'm not 100% sure about

- The "speak" output uses `pyttsx3` for text-to-speech since it's supposed to work
  offline on Windows/Mac/Linux without an API key. I tested it on my Mac and it
  works, but on Linux it apparently needs `espeak` (or `espeak-ng`) installed on
  the system first - I haven't been able to actually test that on a Linux box,
  so if it breaks there that's probably why.
- Installing `pyttsx3` pulled in a surprising number of extra packages on macOS
  (a bunch of `pyobjc` stuff for the built-in speech APIs). Didn't expect that,
  but it works, so leaving it as-is for now.
- Webhook errors (bad URL, server down, etc.) just get printed to stderr and
  exit with code 1 - didn't build in retries or anything fancier than that.
