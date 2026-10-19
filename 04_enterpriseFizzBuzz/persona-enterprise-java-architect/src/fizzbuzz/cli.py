"""Command-line entry point and composition root.

This is the only module in the package that's allowed to know about all
three adapters at once and wire one of them up based on user input. Business
logic (`core.py`) and each adapter stay ignorant of each other and of
argparse -- keeping that wiring in exactly one place is what makes it
possible to add a fourth output target later by touching only this file and
a new adapter module.

argparse over click/typer: it's in the standard library, it has been stable
for over a decade, and this CLI's surface (a handful of flags) doesn't need
what a third-party framework buys you. Pull in a dependency when the
built-in tool stops being enough, not before.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from fizzbuzz.core import fizzbuzz_range
from fizzbuzz.exceptions import FizzBuzzError
from fizzbuzz.ports import OutputPort

logger = logging.getLogger("fizzbuzz")

_OUTPUT_CHOICES = ("stdout", "speech", "webhook")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fizzbuzz",
        description=(
            "Classic FizzBuzz over an inclusive integer range, "
            "delivered to stdout, spoken aloud, or POSTed to a webhook."
        ),
    )
    parser.add_argument(
        "--start", type=int, default=1, metavar="N", help="First number in the range (default: 1)."
    )
    parser.add_argument(
        "--end",
        type=int,
        default=100,
        metavar="N",
        help="Last number in the range, inclusive (default: 100).",
    )
    parser.add_argument(
        "--output",
        choices=_OUTPUT_CHOICES,
        default="stdout",
        help="Where to deliver the output (default: stdout).",
    )
    parser.add_argument(
        "--webhook-url",
        default=None,
        metavar="URL",
        help="Target URL for --output=webhook. Required when --output=webhook.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging to stderr.",
    )
    return parser


def _build_output_adapter(args: argparse.Namespace) -> OutputPort:
    # Imported lazily, inside the branch that needs them, rather than at
    # module top: a pure `--output stdout` invocation then never imports
    # `requests` or shells out to detect a speech engine, so it can't fail
    # for reasons unrelated to what the user actually asked for.
    if args.output == "stdout":
        from fizzbuzz.adapters.stdout_adapter import StdoutOutputAdapter

        return StdoutOutputAdapter()

    if args.output == "speech":
        from fizzbuzz.adapters.speech_adapter import SpeechOutputAdapter

        return SpeechOutputAdapter()

    if args.output == "webhook":
        from fizzbuzz.adapters.webhook_adapter import WebhookOutputAdapter

        return WebhookOutputAdapter(url=args.webhook_url)

    # Unreachable: argparse `choices=` already restricts this. Kept as an
    # explicit guard rather than trusting that invariant silently -- the
    # cost of one branch is nothing next to a `None` adapter escaping to the
    # caller if _OUTPUT_CHOICES and this function ever drift apart.
    raise AssertionError(f"unhandled --output value: {args.output!r}")  # pragma: no cover


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run FizzBuzz, deliver the output. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    if args.output == "webhook" and not args.webhook_url:
        parser.error("--webhook-url is required when --output=webhook")

    try:
        adapter = _build_output_adapter(args)
        lines = fizzbuzz_range(args.start, args.end)
    except ValueError as exc:
        # A bad --start/--end combination is a usage error, not a runtime
        # failure -- report it the same way argparse reports every other
        # bad argument (usage text, exit code 2), not as a stack trace.
        # No `return` after this: argparse.ArgumentParser.error() is typed
        # `-> NoReturn` (it calls sys.exit()), and mypy --strict's
        # warn_unreachable correctly flags any code placed after it as
        # dead -- trust the stub instead of adding a defensive return.
        parser.error(str(exc))

    try:
        adapter.emit(lines)
    except FizzBuzzError as exc:
        logger.error("%s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


def run() -> None:
    """Console-script entry point; see [project.scripts] in pyproject.toml."""
    raise SystemExit(main())


if __name__ == "__main__":
    run()
