"""Unit tests for the CLI / composition root.

Adapters are constructed by lazy, in-function imports inside
`fizzbuzz.cli._build_output_adapter` (see the comment there for why: pure
`--output stdout` runs shouldn't import `requests` or probe PATH for a TTS
engine). That means patching has to target the adapter class at its
*origin* module (`fizzbuzz.adapters.webhook_adapter.WebhookOutputAdapter`),
not at `fizzbuzz.cli.WebhookOutputAdapter` -- the latter is never bound at
module scope, so a patch there would silently no-op.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fizzbuzz.cli import main
from fizzbuzz.exceptions import WebhookDeliveryError


def test_stdout_output_writes_expected_lines(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--start", "1", "--end", "5", "--output", "stdout"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "1\n2\nFizz\n4\nBuzz\n"


def test_defaults_are_1_to_100_on_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert exit_code == 0
    assert len(lines) == 100
    assert lines[-1] == "Buzz"  # fizzbuzz(100) == "Buzz"


def test_webhook_without_url_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--output", "webhook"])
    assert exc_info.value.code == 2


def test_invalid_range_is_a_usage_error_not_a_traceback() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--start", "10", "--end", "1"])
    assert exc_info.value.code == 2


def test_webhook_output_delegates_to_adapter_with_expected_lines() -> None:
    with patch("fizzbuzz.adapters.webhook_adapter.WebhookOutputAdapter") as mock_adapter_cls:
        mock_adapter = MagicMock()
        mock_adapter_cls.return_value = mock_adapter

        exit_code = main(
            [
                "--start",
                "1",
                "--end",
                "3",
                "--output",
                "webhook",
                "--webhook-url",
                "https://example.test/hook",
            ]
        )

        assert exit_code == 0
        mock_adapter_cls.assert_called_once_with(url="https://example.test/hook")
        mock_adapter.emit.assert_called_once()
        (emitted_arg,), _kwargs = mock_adapter.emit.call_args
        assert list(emitted_arg) == ["1", "2", "Fizz"]


def test_output_delivery_failure_yields_exit_code_one_and_stderr_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("fizzbuzz.adapters.webhook_adapter.WebhookOutputAdapter") as mock_adapter_cls:
        mock_adapter = MagicMock()
        mock_adapter.emit.side_effect = WebhookDeliveryError("webhook unreachable")
        mock_adapter_cls.return_value = mock_adapter

        exit_code = main(["--output", "webhook", "--webhook-url", "https://example.test/hook"])

        captured = capsys.readouterr()
        assert exit_code == 1
        assert "webhook unreachable" in captured.err
