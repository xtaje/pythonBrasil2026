"""Handles getting FizzBuzz results out to the world.

Three ways to "output" the results, per the spec:
- stdout: just print them (the default, and probably what most people want)
- speak: read them out loud using text-to-speech
- webhook: POST them as JSON to a URL

I split these into their own functions so the CLI (and anyone using this as
a library) can call whichever one they need without pulling in the others.
"""

from __future__ import annotations

from typing import Iterable

import requests


def output_stdout(results: Iterable[str]) -> None:
    """Print each result on its own line."""
    for line in results:
        print(line)


def output_speak(results: Iterable[str]) -> None:
    """Speak each result out loud using text-to-speech.

    Uses pyttsx3 because it works offline and (in theory) on Windows, Mac,
    and Linux without needing an API key or internet connection. On Linux
    it needs the espeak engine installed on the system - if that's missing
    this will probably blow up with an error from pyttsx3, not from this
    code. Not 100% sure how well this behaves on every Linux distro, would
    want to actually test on a real machine before relying on this in
    something important.
    """
    # Imported here instead of at the top of the file so that `output_stdout`
    # and `output_webhook` still work even if pyttsx3 isn't installed or
    # fails to initialize on a given machine (e.g. no audio device).
    import pyttsx3

    engine = pyttsx3.init()
    for line in results:
        engine.say(line)
    engine.runAndWait()


def output_webhook(results: Iterable[str], url: str) -> None:
    """POST the results as JSON to the given webhook URL.

    Sends a simple JSON body: {"results": [...]}. If the request fails
    (bad URL, server error, timeout, etc.) this raises requests' own
    exception rather than swallowing it - felt better to let the caller
    know something went wrong instead of silently failing.
    """
    response = requests.post(url, json={"results": list(results)}, timeout=10)
    response.raise_for_status()
