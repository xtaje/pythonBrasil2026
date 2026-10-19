"""Output backends for FizzBuzz results: stdout, spoken audio, or a webhook POST.

Each backend is just a function that takes an iterable of strings and does
something with them. No base class / plugin registry — there are three of
these and they're not going to grow a hierarchy. If we end up with a fifth
backend and real plugin needs, that's the time to add abstraction, not now.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable

DEFAULT_WEBHOOK_TIMEOUT_SECONDS = 10.0


def output_stdout(lines: Iterable[str], *, stream=None) -> None:
    """Print each value on its own line.

    `stream` defaults to sys.stdout looked up at call time (not as a default
    arg value) so this plays nice with pytest's capsys, which swaps
    sys.stdout out after this module is imported.
    """
    stream = stream if stream is not None else sys.stdout
    for line in lines:
        print(line, file=stream)


def output_speak(lines: Iterable[str], *, rate: int | None = None, engine=None) -> None:
    """Speak each value aloud using the OS's TTS voice via pyttsx3.

    pyttsx3 wraps NSSpeechSynthesizer on macOS and espeak on Linux, so this
    works on both without picking a platform at call time. Known gotcha:
    on Linux, pyttsx3 needs the `espeak` (or `espeak-ng`) binary installed
    on the system (e.g. `apt install espeak`) — it's not pulled in by pip.
    That's a real cross-platform wrinkle, not a bug in this code; documented
    in the README rather than papered over here.

    `engine` is exposed as a parameter purely so tests can inject a fake
    instead of touching real audio hardware / CI having no sound device.
    """
    lines = list(lines)
    if not lines:
        return

    if engine is None:
        try:
            import pyttsx3
        except ImportError as exc:  # pragma: no cover - environment issue, not logic
            raise RuntimeError(
                "Speech output requires pyttsx3. Install it with `uv sync` "
                "(and on Linux, make sure `espeak` is installed via your "
                "system package manager)."
            ) from exc
        engine = pyttsx3.init()

    if rate is not None:
        engine.setProperty("rate", rate)

    for line in lines:
        engine.say(line)
    engine.runAndWait()


def output_webhook(
    lines: Iterable[str],
    url: str,
    *,
    timeout: float = DEFAULT_WEBHOOK_TIMEOUT_SECONDS,
    session=None,
):
    """POST the results to a webhook URL as JSON: {"results": [...]}.

    Raises for non-2xx responses so callers (e.g. the CLI) can surface a
    clear error instead of silently "succeeding" against a broken endpoint.
    """
    import requests

    lines = list(lines)
    http = session or requests
    response = http.post(url, json={"results": lines}, timeout=timeout)
    response.raise_for_status()
    return response


def emit(
    lines: Iterable[str],
    mode: str,
    *,
    webhook_url: str | None = None,
    rate: int | None = None,
) -> None:
    """Dispatch to the right output backend by name. Used by the CLI."""
    if mode == "stdout":
        output_stdout(lines)
    elif mode == "speak":
        output_speak(lines, rate=rate)
    elif mode == "webhook":
        if not webhook_url:
            raise ValueError("webhook_url is required when mode='webhook'")
        output_webhook(lines, webhook_url)
    else:
        raise ValueError(f"Unknown output mode: {mode!r} (expected stdout, speak, or webhook)")
