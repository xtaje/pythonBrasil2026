# fizzbuzz

FizzBuzz, built as a small reusable library first and a CLI second. The
point of this project isn't the algorithm -- it's the shape: a pure domain
core, an explicit port for "how results get delivered", and three adapters
behind it (stdout, speech, webhook) that the CLI wires up at the composition
root. That structure is more than a five-line function strictly needs, but
it's what lets "also support speech and webhooks" be three isolated
adapters instead of three `if` branches tangled through the algorithm.

## Layout

```
src/fizzbuzz/
    core.py            domain logic: Rule, fizzbuzz(), fizzbuzz_range() -- no I/O
    ports.py            OutputPort: the abstraction adapters implement and the CLI depends on
    exceptions.py        FizzBuzzError and subclasses -- the only exceptions callers need to know about
    cli.py               argparse entry point / composition root (the only module that knows all adapters)
    adapters/
        stdout_adapter.py    prints to a stream
        speech_adapter.py    shells out to `say` (macOS) / `espeak(-ng)` / `spd-say` (Linux)
        webhook_adapter.py   POSTs {"sequence": int, "value": str} per line via requests
tests/
    unit/                 fast, isolated; mocks at the adapter boundary (subprocess, requests.Session)
    integration/           real seams: an in-process HTTP server, an actual installed TTS engine (skipped if absent)
```

## Using it as a library

```python
from fizzbuzz import fizzbuzz, fizzbuzz_range, Rule

fizzbuzz(15)  # "FizzBuzz"
list(fizzbuzz_range(1, 5))  # ["1", "2", "Fizz", "4", "Buzz"]

# Custom rules replace the defaults entirely, in the order given:
list(fizzbuzz_range(1, 6, rules=(Rule(2, "Even"),)))  # ["1", "Even", "3", "Even", "5", "Even"]
```

Delivering output through an adapter is the same shape regardless of
target -- all three implement `OutputPort.emit(lines: Iterable[str]) -> None`
and raise a subclass of `fizzbuzz.FizzBuzzError` on failure:

```python
from fizzbuzz import fizzbuzz_range
from fizzbuzz.adapters.webhook_adapter import WebhookOutputAdapter

WebhookOutputAdapter(url="https://example.com/hook").emit(fizzbuzz_range(1, 100))
```

Adapter modules are intentionally not re-exported from the top-level
`fizzbuzz` package -- importing `fizzbuzz` alone never pulls in `requests`
or touches `PATH`/subprocess. Import the specific adapter you need.

## Using it as a CLI

```console
$ uv run fizzbuzz --start 1 --end 15
1
2
Fizz
4
Buzz
...
FizzBuzz

$ uv run fizzbuzz --output speech --start 1 --end 3        # macOS `say` / Linux espeak(-ng)/spd-say
$ uv run fizzbuzz --output webhook --webhook-url https://example.com/hook
```

Run `uv run fizzbuzz --help` for the full flag list. A bad range
(`--start` > `--end`) or a missing `--webhook-url` is reported as a usage
error (exit code 2); a delivery failure at runtime (webhook unreachable, no
TTS engine installed) is reported on stderr with exit code 1.

## Development

Requires [`uv`](https://docs.astral.sh/uv/).

```console
uv sync                     # install runtime + dev dependencies into .venv
make test                   # full suite (unit + integration)
make test-unit              # unit tests only -- fast, no network/subprocess, for the inner loop
make lint                   # ruff check
make typecheck               # mypy --strict
make check                   # lint + typecheck + full test suite (what CI should run)
```

Without `make`, the underlying commands are `uv run pytest`, `uv run pytest
-m "not integration"`, `uv run ruff check .`, and `uv run mypy`.

### Notes on the platform-dependent bits

- Speech output shells out to a native OS binary (`say` on macOS;
  `espeak-ng`, `espeak`, or `spd-say` on Linux, in that preference order)
  rather than depending on a Python TTS wrapper package. It fails fast with
  an actionable error at construction time if none of those are on `PATH`.
- The speech integration test is skipped (not faked, not xfailed) on any
  machine without one of those engines installed -- most CI containers
  won't have one, and that's fine; the unit tests cover the adapter's own
  logic exhaustively via mocked `subprocess.run`.
- Windows is not supported for speech output (no engine is wired up for
  it); the domain requested "linux or mac", and that's what's built and
  tested here.
