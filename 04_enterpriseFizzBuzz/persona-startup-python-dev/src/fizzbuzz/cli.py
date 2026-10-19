"""Command-line entry point for fizzbuzz.

Plain argparse, no click/typer — this CLI has four flags, argparse in the
stdlib does the job with zero added dependencies.
"""

from __future__ import annotations

import argparse
import sys

from .core import fizzbuzz_range
from .output import emit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fizzbuzz",
        description="Classic FizzBuzz, with a choice of where the output goes.",
    )
    parser.add_argument(
        "end",
        type=int,
        help="Print/speak/send FizzBuzz for 1..END (or START..END if --start is given).",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start of the range (default: 1).",
    )
    parser.add_argument(
        "--output",
        choices=["stdout", "speak", "webhook"],
        default="stdout",
        help="Where to send the output (default: stdout).",
    )
    parser.add_argument(
        "--webhook-url",
        default=None,
        help="Webhook URL to POST results to. Required when --output=webhook.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=None,
        help="Words-per-minute for --output=speak (defaults to the system voice's rate).",
    )
    parser.add_argument(
        "--fizz",
        type=int,
        default=3,
        help="Divisor for 'Fizz' (default: 3).",
    )
    parser.add_argument(
        "--buzz",
        type=int,
        default=5,
        help="Divisor for 'Buzz' (default: 5).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output == "webhook" and not args.webhook_url:
        parser.error("--webhook-url is required when --output=webhook")

    try:
        values = fizzbuzz_range(args.start, args.end, fizz=args.fizz, buzz=args.buzz)
        emit(values, args.output, webhook_url=args.webhook_url, rate=args.rate)
    except Exception as exc:  # noqa: BLE001 - CLI boundary: turn errors into a message + exit code
        print(f"fizzbuzz: error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
