"""Integration test for SpeechOutputAdapter against a real, installed
text-to-speech engine.

Skipped -- not faked -- on any runner without a supported engine on PATH.
A fake here would only prove we can call `subprocess.run`, which the unit
tests already cover in tests/unit/test_speech_adapter.py; the entire point
of this test is to catch a real invocation failure (wrong CLI flag for the
installed engine version, the engine hanging) that a mock can't see. A
flaky or environment-dependent test that fails on runners that simply don't
have `espeak` installed erodes trust in the suite faster than it's worth --
skip it explicitly instead.
"""

from __future__ import annotations

import shutil

import pytest

from fizzbuzz.adapters.speech_adapter import SpeechOutputAdapter

pytestmark = pytest.mark.integration

_HAS_ENGINE = any(shutil.which(binary) for binary in ("say", "espeak-ng", "espeak", "spd-say"))


@pytest.mark.skipif(not _HAS_ENGINE, reason="no supported text-to-speech engine on PATH")
class TestSpeechIntegration:
    def test_speaks_a_line_without_raising(self) -> None:
        adapter = SpeechOutputAdapter()
        adapter.emit(["test"])
