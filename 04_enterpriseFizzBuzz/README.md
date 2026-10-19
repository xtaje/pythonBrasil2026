Install the personas as agents in your repo, and ask CLAUDE to use them to generate independent solutions to the prompt in `enterpriseFizzBuzz.md`.

Another test you can try that was not shown in the presentations is comparing multi-turn vs. single-turn prompts (aka sharded vs. non-sharded).

With sharded instructions, you should see that Claude will forget some of the requirements and need to be reminded again.

To run non-sharded, use this prompt:
* "Please read @enterpriseFizzBuzz.md"

To run sharded, just enter the requirements one line at a time into Claude Code in "auto" mode, and accept all suggested tool calls.
