from unittest.mock import patch

import pytest

from fizzbuzz.cli import main


def test_cli_default_output_goes_to_stdout(capsys):
    exit_code = main(["--start", "1", "--end", "5"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "1\n2\nFizz\n4\nBuzz\n"


def test_cli_webhook_without_url_errors_out():
    # argparse.error() calls sys.exit(2), so this should raise SystemExit
    # instead of returning a normal exit code.
    with pytest.raises(SystemExit):
        main(["--output", "webhook"])


@patch("fizzbuzz.cli.output_webhook")
def test_cli_webhook_calls_output_webhook_with_url(mock_output_webhook):
    exit_code = main(
        [
            "--start",
            "1",
            "--end",
            "3",
            "--output",
            "webhook",
            "--webhook-url",
            "https://example.com/hook",
        ]
    )

    assert exit_code == 0
    mock_output_webhook.assert_called_once_with(
        ["1", "2", "Fizz"], "https://example.com/hook"
    )


def test_cli_invalid_range_returns_error_code(capsys):
    exit_code = main(["--start", "10", "--end", "1"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
