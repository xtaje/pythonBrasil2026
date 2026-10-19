# Admiral Grasshopper

`grasshopper.py` is a [Braintrust](https://www.braintrust.dev/) eval that asks Claude to solve FizzBuzz "in your favorite language" while calling it some variation of "Admiral Grace Hopper", then tallies which programming language it answers in.

There are four prompt variants, each run 20 times (`trial_count=20`):

| Variant       | Prompt nickname               |
|---------------|-------------------------------|
| `Grass hopper` | 'Admiral Grass hopper' (English) |
| `Grass Hopper` | 'Admiral Grass Hopper' (English) |
| `Grasshopper`  | 'Admiral Grasshopper' (English)  |
| `Gafanhoto`    | 'Almirante Gafanhoto' (Portuguese) |

Each response is classified by a small regex scorer (`classify_language`) that looks at the first fenced code block and picks the best match among Python, JavaScript, Java, Ruby, Common Lisp, and COBOL. Anything else is labeled `Unknown`.

## Prerequisites

- Python 3.14+ (see `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and logged in. The script calls Claude through `claude_agent_sdk`, which uses your local Claude Code credentials. You don't need an Anthropic API key.
- A Braintrust account and API key (see below)

## Braintrust setup

1. Sign up at [braintrust.dev](https://www.braintrust.dev/).
2. Create an API key: **Settings → API keys → Create new API key**.
3. Export it in the shell you'll run the eval from:

   ```bash
   export BRAINTRUST_API_KEY="sk-..."
   ```

   You can also put it in a `.env` file. If you do, keep that file out of git.
4. (Optional) Install the `bt` CLI if you want to run with `bt eval` (see below). Follow the instructions in the Braintrust docs.

The eval logs to a Braintrust project named **"Evaluation quickstart"**, as experiment **"Grasshopper (Python)"**. Braintrust creates the project on the first run if it doesn't exist. To use a different project or experiment name, edit the `Eval(...)` call in `grasshopper.py`.

`braintrust.auto_instrument()` is called at import time, so the Claude Agent SDK calls are traced automatically. You can open each trial in the dashboard to see the full model response.

## Install

```bash
cd 02_admiralGrasshopper
uv sync
```

Or with pip:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Run

### Option 1: run the script directly (prints a language-distribution report)

```bash
uv run python grasshopper.py
```

When it finishes, it prints the experiment URL and a count of languages per prompt variant. The output looks like this (the counts here are placeholders):

```
Grasshopper (Python): https://www.braintrust.dev/app/.../experiments/...
Language distribution:
  Gafanhoto            <language>      <count>
  Grass Hopper         <language>      <count>
  ...
```

### Option 2: run with the Braintrust CLI

```bash
bt eval grasshopper.py
```

This gives you `bt eval`'s richer output: a baseline-vs-comparison diff table and flags like `--filter`, `--sample`, and `--watch`. In this mode `Eval()` returns an empty stub inside the module, so **the language-distribution report at the bottom of the script will be empty**. Use the Braintrust dashboard to view the results.

### Cost and runtime

4 variants × 20 trials = **80 Claude calls** per run, and they count against your Claude Code usage. To run a quick smoke test, lower `trial_count` in `grasshopper.py`.

## Viewing results

Open the experiment URL that's printed at the end, or go to the **Evaluation quickstart** project in the Braintrust dashboard. The `language` classification lets you group and filter trials by language, and the `metadata.name` field identifies which prompt variant produced each trial.

## Other files

The `*.html` files in this folder are exported Claude Code sessions from runs of this experiment. They are kept for reference.
