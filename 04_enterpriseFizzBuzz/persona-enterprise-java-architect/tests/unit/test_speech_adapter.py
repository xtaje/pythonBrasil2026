"""Unit tests for SpeechOutputAdapter.

Mocked at the architectural boundary -- `subprocess.run`, `shutil.which`,
and `platform.system` -- rather than at the granularity of "does this
function call that function". This is the seam we own; whatever `say` or
`espeak` actually does with the text is somebody else's problem, and is
covered separately by the integration test that only runs when a real
engine is present (see tests/integration/test_speech_integration.py).
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from fizzbuzz.adapters.speech_adapter import SpeechOutputAdapter
from fizzbuzz.exceptions import SpeechDeliveryError, SpeechEngineNotFoundError


class TestEngineDetection:
    def test_explicit_command_bypasses_platform_detection(self) -> None:
        adapter = SpeechOutputAdapter(command=("/usr/bin/fake-say",))
        assert adapter._command == ("/usr/bin/fake-say",)

    @patch("fizzbuzz.adapters.speech_adapter.shutil.which", return_value="/usr/bin/say")
    @patch("fizzbuzz.adapters.speech_adapter.platform.system", return_value="Darwin")
    def test_detects_say_on_macos(self, mock_system: MagicMock, mock_which: MagicMock) -> None:
        adapter = SpeechOutputAdapter()
        assert adapter._command == ("/usr/bin/say",)

    @patch("fizzbuzz.adapters.speech_adapter.platform.system", return_value="Linux")
    def test_falls_back_to_next_linux_engine_when_first_is_absent(
        self, mock_system: MagicMock
    ) -> None:
        with patch(
            "fizzbuzz.adapters.speech_adapter.shutil.which",
            side_effect=lambda name: "/usr/bin/espeak" if name == "espeak" else None,
        ):
            adapter = SpeechOutputAdapter()
        assert adapter._command == ("/usr/bin/espeak",)

    @patch("fizzbuzz.adapters.speech_adapter.shutil.which", return_value=None)
    @patch("fizzbuzz.adapters.speech_adapter.platform.system", return_value="Linux")
    def test_raises_actionable_error_when_no_engine_on_path(
        self, mock_system: MagicMock, mock_which: MagicMock
    ) -> None:
        with pytest.raises(SpeechEngineNotFoundError, match="No supported"):
            SpeechOutputAdapter()

    @patch("fizzbuzz.adapters.speech_adapter.platform.system", return_value="Windows")
    def test_raises_on_unsupported_platform(self, mock_system: MagicMock) -> None:
        with pytest.raises(SpeechEngineNotFoundError, match="not supported"):
            SpeechOutputAdapter()


class TestEmit:
    def test_invokes_subprocess_once_per_line_with_expected_args(self) -> None:
        adapter = SpeechOutputAdapter(command=("say",))
        with patch("fizzbuzz.adapters.speech_adapter.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            adapter.emit(["Fizz", "Buzz"])

        assert mock_run.call_count == 2
        mock_run.assert_any_call(("say", "Fizz"), check=True, capture_output=True, timeout=10)
        mock_run.assert_any_call(("say", "Buzz"), check=True, capture_output=True, timeout=10)

    def test_nonzero_exit_is_wrapped_in_domain_exception(self) -> None:
        adapter = SpeechOutputAdapter(command=("say",))
        error = subprocess.CalledProcessError(1, ("say", "Fizz"), stderr=b"boom")
        with (
            patch("fizzbuzz.adapters.speech_adapter.subprocess.run", side_effect=error),
            pytest.raises(SpeechDeliveryError, match="boom"),
        ):
            adapter.emit(["Fizz"])

    def test_timeout_is_wrapped_in_domain_exception(self) -> None:
        adapter = SpeechOutputAdapter(command=("say",))
        error = subprocess.TimeoutExpired(("say", "Fizz"), 10)
        with (
            patch("fizzbuzz.adapters.speech_adapter.subprocess.run", side_effect=error),
            pytest.raises(SpeechDeliveryError, match="timed out"),
        ):
            adapter.emit(["Fizz"])

    def test_stops_at_first_failure(self) -> None:
        adapter = SpeechOutputAdapter(command=("say",))
        error = subprocess.CalledProcessError(1, ("say", "Buzz"), stderr=b"boom")
        with (
            patch(
                "fizzbuzz.adapters.speech_adapter.subprocess.run",
                side_effect=[MagicMock(returncode=0), error],
            ) as mock_run,
            pytest.raises(SpeechDeliveryError),
        ):
            adapter.emit(["Fizz", "Buzz", "FizzBuzz"])
        assert mock_run.call_count == 2  # never attempted the third line
