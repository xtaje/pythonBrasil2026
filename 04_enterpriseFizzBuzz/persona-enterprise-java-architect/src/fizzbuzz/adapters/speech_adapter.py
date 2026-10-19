"""The speech adapter: reads each line aloud via an OS-native command-line
text-to-speech engine.

We shell out to a native binary instead of depending on a Python TTS
package (pyttsx3 and friends). Those wrap the exact same OS engines while
adding a dependency with its own release cadence and, on Linux, a native
library they link against that may or may not be present on a given box --
in past projects that's been the first thing to break in a fresh
environment, and it breaks in a way that's hard to diagnose from a Python
traceback alone. subprocess plus a well-known, separately-installed binary
is one more moving part we don't control the packaging of, but it's a
boring and inspectable one: you can reproduce a failure by running the exact
same command by hand on a terminal.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from collections.abc import Iterable, Sequence

from fizzbuzz.exceptions import SpeechDeliveryError, SpeechEngineNotFoundError
from fizzbuzz.ports import OutputPort

# Ordered by preference within each OS family. First one found on PATH wins.
_LINUX_ENGINES: Sequence[Sequence[str]] = (
    ("espeak-ng",),
    ("espeak",),
    ("spd-say",),
)
_DARWIN_ENGINES: Sequence[Sequence[str]] = (("say",),)

_SUBPROCESS_TIMEOUT_SECONDS = 10


class SpeechOutputAdapter(OutputPort):
    """Speaks each line aloud using whatever native TTS engine is on PATH.

    Engine detection happens once, at construction, and fails fast with an
    actionable message if nothing suitable is found -- better to fail before
    doing any work than partway through emitting a batch of lines, with the
    caller unable to tell which lines were actually spoken.
    """

    def __init__(self, command: Sequence[str] | None = None) -> None:
        self._command: Sequence[str] = (
            tuple(command) if command is not None else self._detect_engine()
        )

    @staticmethod
    def _candidate_commands() -> Sequence[Sequence[str]]:
        system = platform.system()
        if system == "Darwin":
            return _DARWIN_ENGINES
        if system == "Linux":
            return _LINUX_ENGINES
        raise SpeechEngineNotFoundError(
            f"Speech output is not supported on platform {system!r}; "
            "supported platforms are Darwin (macOS) and Linux."
        )

    @classmethod
    def _detect_engine(cls) -> Sequence[str]:
        for candidate in cls._candidate_commands():
            resolved = shutil.which(candidate[0])
            if resolved is not None:
                return (resolved, *candidate[1:])
        raise SpeechEngineNotFoundError(
            "No supported text-to-speech engine found on PATH. On Linux, "
            "install 'espeak-ng' (preferred), 'espeak', or 'speech-dispatcher' "
            "(spd-say); on macOS the built-in 'say' command is used automatically."
        )

    def emit(self, lines: Iterable[str]) -> None:
        for line in lines:
            self._speak(line)

    def _speak(self, text: str) -> None:
        command = (*self._command, text)
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                timeout=_SUBPROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise SpeechDeliveryError(
                f"Speech engine {self._command[0]!r} timed out after "
                f"{_SUBPROCESS_TIMEOUT_SECONDS}s speaking {text!r}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = (
                exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
            )
            raise SpeechDeliveryError(
                f"Speech engine {self._command[0]!r} exited with status "
                f"{exc.returncode} for input {text!r}: {stderr!r}"
            ) from exc
