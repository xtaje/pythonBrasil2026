"""Command-line interface for the FizzBuzz tool.

Example usage:
    fizzbuzz --start 1 --end 20
    fizzbuzz --start 1 --end 100 --output speak
    fizzbuzz --start 1 --end 15 --output webhook --webhook-url https://example.com/hook
"""

from __future__ import annotations

import argparse
import sys

from .core import fizzbuzz_range
from .output import output_speak, output_stdout, output_webhook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fizzbuzz",
        description="Classic FizzBuzz, with a few output options.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="First number in the range (default: 1)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=100,
        help="Last number in the range, inclusive (default: 100)",
    )
    parser.add_argument(
        "--output",
        choices=["stdout", "speak", "webhook"],
        default="stdout",
        help="Where to send the results (default: stdout)",
    )
    parser.add_argument(
        "--webhook-url",
        help="URL to POST results to. Required when --output webhook is used.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output == "webhook" and not args.webhook_url:
        parser.error("--webhook-url is required when --output is 'webhook'")

    try:
        results = fizzbuzz_range(args.start, args.end)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output == "stdout":
        output_stdout(results)
    elif args.output == "speak":
        output_speak(results)
    elif args.output == "webhook":
        try:
            output_webhook(results, args.webhook_url)
        except Exception as exc:
            # Catching the general Exception here on purpose - could be a
            # connection error, a timeout, a bad status code from requests,
            # etc. and I just want to show the user something useful
            # instead of a raw traceback. Might be worth catching more
            # specific requests exceptions later, but this works for now.
            print(f"Error sending results to webhook: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
