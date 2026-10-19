# fizzbuzz

FizzBuzz, but as a real small project: usable as a CLI, importable as a
library, and able to send its output to stdout, your speakers, or a webhook.
Built with [uv](https://docs.astral.sh/uv/) and tested with pytest.

## Install / setup

```bash
uv sync
```

That installs the runtime deps (`requests`, `pyttsx3`) and dev deps (`pytest`)
into a local `.venv`.

**Linux only, for `--output speak`:** pyttsx3 drives `espeak` under the hood
on Linux, and `espeak` is a system package, not a Python one. Install it
separately:

```bash
# Debian/Ubuntu
sudo apt install espeak
```

On macOS, pyttsx3 uses the built-in NSSpeechSynthesizer, so there's nothing
extra to install. `stdout` and `webhook` output have no OS-specific
requirements on either platform.

## CLI usage

```bash
uv run fizzbuzz 15                     # 1..15 to stdout (default)
uv run fizzbuzz 20 --start 10          # 10..20 to stdout
uv run fizzbuzz 15 --output speak      # spoken aloud
uv run fizzbuzz 15 --output webhook --webhook-url https://example.com/hook
uv run fizzbuzz 20 --fizz 2 --buzz 7   # custom divisors, if you're into that
```

Run `uv run fizzbuzz --help` for the full flag list.

## Library usage

The core logic has zero dependencies, so you can use it standalone without
pulling in requests/pyttsx3 at all:

```python
from fizzbuzz import fizzbuzz_value, fizzbuzz_range

fizzbuzz_value(15)            # "FizzBuzz"
list(fizzbuzz_range(1, 20))   # ["1", "2", "Fizz", ..., "FizzBuzz"]
```

`fizzbuzz_range` is a generator, not a list — fine to point it at a huge
range without worrying about memory.

To reuse the output backends directly (e.g. from your own script):

```python
from fizzbuzz.output import output_stdout, output_speak, output_webhook

output_webhook(fizzbuzz_range(1, 100), "https://example.com/hook")
```

## Testing

```bash
uv run pytest
```

Tests are pytest, no fixtures framework beyond what pytest ships with, and
fakes instead of mocking libraries wherever it's easy (see
`tests/test_output.py` for a hand-rolled fake TTS engine and a `MagicMock`
standing in for a `requests.Session` — nothing calls real audio hardware or
the network). `test_cli.py` calls `main()` the way a real invocation would,
because for something this small that catches more real bugs per test than
a pile of argparse-internals unit tests would.

## Notes / known limitations

- Spoken output requires the OS TTS voice to actually be configured/working.
  If `--output speak` hangs or errors on a headless Linux box, that's almost
  certainly a missing `espeak` install or no audio device — not a bug in
  this code. Not covered by CI (no speakers there); the *logic* around it
  (what gets said, in what order) is tested with a fake engine.
- Webhook output is a fire-and-forget POST with a 10s timeout and no
  retries. Fine for a CLI toy; if this becomes a real integration, add
  retry/backoff and probably a signature/auth header before trusting it in
  prod.
- No packaging/publishing setup (no PyPI, no Docker image) — not needed
  yet. `uv run fizzbuzz` and `uv build` cover what we need right now.
