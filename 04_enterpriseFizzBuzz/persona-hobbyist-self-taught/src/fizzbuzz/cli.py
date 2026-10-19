import argparse
import sys

from fizzbuzz.core import fizzbuzz_range
from fizzbuzz.output import output_stdout, output_speak, output_webhook


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Does FizzBuzz, from --start to --end, and lets you "
        "choose how you want to see (or hear) the results."
    )
    parser.add_argument(
        "--start", type=int, default=1, help="number to start at (default: 1)"
    )
    parser.add_argument(
        "--end", type=int, default=100, help="number to end at (default: 100)"
    )
    parser.add_argument(
        "--output",
        choices=["stdout", "speak", "webhook"],
        default="stdout",
        help="where the results go (default: stdout)",
    )
    parser.add_argument(
        "--webhook-url",
        default=None,
        help="url to POST the results to as JSON, only used with --output webhook",
    )

    args = parser.parse_args()

    if args.output == "webhook" and not args.webhook_url:
        parser.error("--webhook-url is required when --output is webhook")

    results = fizzbuzz_range(args.start, args.end)

    if args.output == "stdout":
        output_stdout(results)
    elif args.output == "speak":
        output_speak(results)
    elif args.output == "webhook":
        try:
            output_webhook(results, args.webhook_url)
        except Exception as e:
            # not super graceful but at least it tells you what went wrong
            # instead of just spitting out a giant traceback
            print(f"webhook thing didn't work: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
