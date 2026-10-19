from unittest.mock import MagicMock, patch

import pytest
import requests

from fizzbuzz.output import output_speak, output_stdout, output_webhook


def test_output_stdout_prints_each_line(capsys):
    output_stdout(["1", "2", "Fizz"])

    captured = capsys.readouterr()
    assert captured.out == "1\n2\nFizz\n"


def test_output_stdout_empty_list_prints_nothing(capsys):
    output_stdout([])

    captured = capsys.readouterr()
    assert captured.out == ""


# For the speak and webhook tests I'm mocking out the actual pyttsx3 engine
# and requests.post calls - don't want tests that actually talk out loud or
# hit a real network URL every time someone runs the test suite.


@patch("pyttsx3.init")
def test_output_speak_calls_say_for_each_line(mock_init):
    mock_engine = MagicMock()
    mock_init.return_value = mock_engine

    output_speak(["1", "2", "Fizz"])

    assert mock_engine.say.call_count == 3
    mock_engine.say.assert_any_call("Fizz")
    mock_engine.runAndWait.assert_called_once()


@patch("requests.post")
def test_output_webhook_posts_results_as_json(mock_post):
    mock_response = MagicMock()
    mock_post.return_value = mock_response

    output_webhook(["1", "2", "Fizz"], "https://example.com/hook")

    mock_post.assert_called_once_with(
        "https://example.com/hook",
        json={"results": ["1", "2", "Fizz"]},
        timeout=10,
    )
    mock_response.raise_for_status.assert_called_once()


@patch("requests.post")
def test_output_webhook_raises_on_bad_response(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 error")
    mock_post.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        output_webhook(["1"], "https://example.com/hook")
