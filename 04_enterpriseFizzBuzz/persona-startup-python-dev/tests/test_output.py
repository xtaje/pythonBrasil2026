"""Output backends. We don't hit real audio hardware or the network here —
a fake TTS engine and a fake requests session stand in. That's enough to
catch "did we call the right thing with the right args" without making the
suite slow or flaky in CI."""

from unittest.mock import MagicMock

import pytest

from fizzbuzz.output import emit, output_speak, output_stdout, output_webhook


def test_output_stdout_prints_each_line(capsys):
    output_stdout(["1", "2", "Fizz"])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\nFizz\n"


def test_output_stdout_handles_empty_input(capsys):
    output_stdout([])
    assert capsys.readouterr().out == ""


class FakeTTSEngine:
    """Stand-in for pyttsx3.Engine — records calls instead of speaking."""

    def __init__(self):
        self.said = []
        self.properties = {}
        self.ran = False

    def say(self, text):
        self.said.append(text)

    def setProperty(self, name, value):
        self.properties[name] = value

    def runAndWait(self):
        self.ran = True


def test_output_speak_says_each_line_and_runs():
    engine = FakeTTSEngine()
    output_speak(["1", "Fizz", "Buzz"], engine=engine)
    assert engine.said == ["1", "Fizz", "Buzz"]
    assert engine.ran is True


def test_output_speak_sets_rate_when_given():
    engine = FakeTTSEngine()
    output_speak(["Fizz"], rate=150, engine=engine)
    assert engine.properties["rate"] == 150


def test_output_speak_skips_engine_setup_when_no_lines():
    # No engine passed AND nothing to say -> must not try to init a real
    # pyttsx3 engine (which would blow up in a headless CI box).
    output_speak([], engine=None)


def test_output_webhook_posts_json_payload():
    fake_session = MagicMock()
    fake_response = MagicMock()
    fake_session.post.return_value = fake_response

    output_webhook(["1", "2", "Fizz"], "https://example.com/hook", session=fake_session)

    fake_session.post.assert_called_once_with(
        "https://example.com/hook",
        json={"results": ["1", "2", "Fizz"]},
        timeout=10.0,
    )
    fake_response.raise_for_status.assert_called_once()


def test_output_webhook_raises_on_http_error():
    fake_session = MagicMock()
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = RuntimeError("500 boom")
    fake_session.post.return_value = fake_response

    with pytest.raises(RuntimeError):
        output_webhook(["Fizz"], "https://example.com/hook", session=fake_session)


def test_emit_dispatches_to_stdout(capsys):
    emit(["Fizz"], "stdout")
    assert capsys.readouterr().out == "Fizz\n"


def test_emit_webhook_requires_url():
    with pytest.raises(ValueError):
        emit(["Fizz"], "webhook", webhook_url=None)


def test_emit_rejects_unknown_mode():
    with pytest.raises(ValueError):
        emit(["Fizz"], "carrier-pigeon")
