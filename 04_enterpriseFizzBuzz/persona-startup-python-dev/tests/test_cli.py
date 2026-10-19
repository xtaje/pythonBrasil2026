"""CLI tests. These are closer to integration tests than unit tests — we
call main() with real argv-style input and check real stdout, the way an
actual user would invoke this. That catches wiring bugs (bad arg names,
wrong defaults) that isolated unit tests on argparse internals wouldn't."""

from unittest.mock import patch

import pytest

from fizzbuzz.cli import main


def test_cli_default_stdout_output(capsys):
    exit_code = main(["15"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.splitlines() == [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]


def test_cli_respects_start_flag(capsys):
    main(["5", "--start", "3"])
    out = capsys.readouterr().out
    assert out.splitlines() == ["Fizz", "4", "Buzz"]


def test_cli_custom_fizz_buzz_divisors(capsys):
    main(["4", "--fizz", "2", "--buzz", "4"])
    out = capsys.readouterr().out
    assert out.splitlines() == ["1", "Fizz", "3", "FizzBuzz"]


def test_cli_webhook_without_url_errors(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["10", "--output", "webhook"])
    assert exc_info.value.code == 2  # argparse's error() exit code
    assert "--webhook-url is required" in capsys.readouterr().err


def test_cli_webhook_posts_results(capsys):
    with patch("fizzbuzz.cli.emit") as fake_emit:
        exit_code = main(["3", "--output", "webhook", "--webhook-url", "https://example.com/hook"])
    assert exit_code == 0
    fake_emit.assert_called_once()
    _, kwargs = fake_emit.call_args
    assert kwargs["webhook_url"] == "https://example.com/hook"


def test_cli_reports_errors_without_traceback(capsys):
    with patch("fizzbuzz.cli.emit", side_effect=RuntimeError("webhook is down")):
        exit_code = main(["5"])
    assert exit_code == 1
    assert "fizzbuzz: error: webhook is down" in capsys.readouterr().err
