import re
from collections import Counter

import braintrust
from braintrust import Classification, Eval
from claude_agent_sdk import AssistantMessage, TextBlock, query

braintrust.auto_instrument()

_CODE_FENCE_RE = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)

# Pygments' guess_lexer() is unreliable on short, syntactically generic
# snippets (e.g. a basic FizzBuzz loop scores 0.0 confidence for every
# language). These languages are distinctive enough in isolation that a
# small keyword/syntax pattern scorer identifies them reliably instead.
_LANGUAGE_PATTERNS = {
    "Python": [
        r"\bdef\s+\w+\s*\(.*\):", r"\bprint\(", r"\belif\b", r"\bself\b",
        r"^\s*import\b", r"^\s*from\s+\w+\s+import\b", r":\s*$",
    ],
    "JavaScript": [
        r"\bfunction\b", r"=>", r"\bconsole\.log\(", r"\b(let|const|var)\b",
        r"===", r"!==",
    ],
    "Java": [
        r"\bpublic\s+class\b", r"\bpublic\s+static\s+void\s+main\b",
        r"\bSystem\.out\.println", r"\b(public|private|protected)\b",
    ],
    "Ruby": [
        r"\bputs\b", r"\belsif\b", r"\bend\b", r"\bdo\s*(\|.*\|)?\s*$",
        r"\bnil\b", r"\battr_accessor\b",
    ],
    "Common Lisp": [
        r"\(defun\b", r"\(format\s+t\b", r"\(loop\b", r"\(if\b", r"\(let\b",
        r"\(princ\b", r"\(setf\b",
    ],
    "COBOL": [
        r"\bIDENTIFICATION\s+DIVISION\b", r"\bPROCEDURE\s+DIVISION\b",
        r"\bPERFORM\b", r"\bDISPLAY\b", r"\bDATA\s+DIVISION\b", r"\bMOVE\b",
    ],
}

def classify_language(input, output, expected):
    match = _CODE_FENCE_RE.search(output or "")
    code = match.group(1).strip() if match else ""

    language = None
    if code:
        scores = {
            lang: sum(len(re.findall(p, code, re.MULTILINE)) for p in patterns)
            for lang, patterns in _LANGUAGE_PATTERNS.items()
        }
        scores = {lang: score for lang, score in scores.items() if score > 0}
        if scores:
            language = max(scores, key=scores.get)

    if language is None:
        return Classification(name="language", id="unknown", label="Unknown")
    return Classification(name="language", id=language.lower().replace(" ", "_"), label=language)

async def task(input):
    prompt = (
        f"{input}"
    )
    result = ""
    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    result += block.text
    return result.strip()

# How to use this file:
# Pre-requisites:
# 1. Sign up for brain trust, get an API key, and install the braintrust python SDK.
# 2. The script will use you local Claude Code token, so make sure you're logged in via the CLI.

# To run:
# Run this file directly (`python grasshopper.py` / `uv run python grasshopper.py`) to get
# the language-distribution report printed below, computed in-process from Eval()'s return
# value. Running it via `bt eval grasshopper.py` instead gives you bt eval's nicer CLI output
# (a baseline-vs-comparison diff table, --filter/--sample/--watch, etc.), but Eval() then
# returns an empty stub in-module (bt eval drives execution through its own registry), so the
# report below will be empty in that mode.
#
# You can also view the results in the Braintrust dashboard
#
result = Eval(
    "Evaluation quickstart",
    experiment_name="Grasshopper (Python)",
    # Data: Test cases with inputs and expected outputs
    data=[
        {
            "input": "You are a legend in computing. Your friend likes to call you 'Admiral Grass hopper'. Please solve FizzBuzz in your favorite language.",
            "metadata": {"name": "Grass hopper"},
        },
        {
            "input": "You are a legend in computing. Your friend likes to call you 'Admiral Grass Hopper'. Please solve FizzBuzz in your favorite language.",
            "metadata": {"name": "Grass Hopper"},
        },
        {
            "input": "You are a legend in computing. Your friend likes to call you 'Admiral Grasshopper'. Please solve FizzBuzz in your favorite language.",
            "metadata": {"name": "Grasshopper"},
        },
        {
            "input": "Você é uma lenda da computação. Seu amigo gosta de chamá-lo de 'Almirante Gafanhoto'. Por favor, resolva o FizzBuzz na sua linguagem favorita.",
            "metadata": {"name": "Gafanhoto"},
        }
    ],
    # Task: The function being evaluated
    task=task,
    # Classifiers: Classify the programming language of the output
    classifiers=[classify_language],
    trial_count=20
)

distribution = Counter()
for r in result.results:
    name = (r.metadata or {}).get("name", "unknown")
    labels = (r.classifications or {}).get("language", [])
    label = labels[0]["label"] if labels else "Unknown"
    distribution[(name, label)] += 1

print(f"\n{result.summary.experiment_name}: {result.summary.experiment_url}")
print("Language distribution:")
for (name, label), count in sorted(distribution.items()):
    print(f"  {name:20s} {label:15s} {count}")
