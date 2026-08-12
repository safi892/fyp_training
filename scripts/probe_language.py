"""Ask whether the checkpoint can answer in Roman Urdu before anything is built.

Adding a language looks like a training question and may not be one. The same
question was asked twice before in this project - once about optimisation,
where the capability turned out to be present and only badly requested, and
once about defect awareness, where it was genuinely absent. Both answers came
from a probe that cost under a day, and both changed the plan.

Three things are worth knowing before choosing an architecture:

- can the model answer a **code** question in Roman Urdu when asked plainly?
- does an example of the target style help?
- can it translate at all, with the code task removed entirely?

The third matters most. If the model cannot translate a sentence it wrote
itself, no amount of prompt work on the code task will help, and the language
belongs in a separate stage rather than in this model.

    uv run python scripts/probe_language.py

Reuses a llama-server already listening on ``--port``; starts one otherwise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_hard import already_serving, complete, wait_for_server  # noqa: E402

SYSTEM = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)

CODE = """int howMany(int first, int second)
{
  int total = first + second;
  int tally = 0;
  while (total != 0)
  {
    total /= 10;
    tally++;
  }
  return tally;
}"""

#: Asked as the product asks, with only the language requirement added, so a
#: failure here is about the language and not about a rewritten instruction.
CODE_TASKS: dict[str, str] = {
    "roman_urdu_plain": (
        "Generate:\n- Explanation (write the explanation in Roman Urdu, that is "
        "Urdu written using English letters)"
    ),
    "roman_urdu_with_example": (
        "Generate:\n- Explanation (Roman Urdu mein likhein, misal ke taur par: "
        '"Ye function do numbers ko add karta hai")'
    ),
    "urdu_script": "Generate:\n- Explanation (write the explanation in Urdu)",
}

ENGLISH = "This function counts how many decimal digits are in the sum of two integers."

#: The code task removed, so the only thing being measured is whether the
#: language exists in the model at all.
TRANSLATION_TASKS: dict[str, tuple[str, str]] = {
    "translate_plain": (
        "You are a helpful translator.",
        f"Translate into Roman Urdu (Urdu written in English letters):\n\n{ENGLISH}",
    ),
    "translate_few_shot": (
        "You are a helpful translator.",
        "Translate English into Roman Urdu.\n\n"
        "English: This function adds two numbers.\n"
        "Roman Urdu: Ye function do numbers ko add karta hai.\n\n"
        f"English: {ENGLISH}\nRoman Urdu:",
    ),
}

#: Urdu is written in a Perso-Arabic script, so a reply can be in the right
#: script and the wrong language. Persian markers are checked separately
#: because that is the failure this model actually produced.
ARABIC_RANGE = range(0x0600, 0x0700)
PERSIAN_MARKERS = ("این", "می‌کند", "است", "را ")
ROMAN_URDU_MARKERS = ("karta", "karti", "hai", "ye ", "ka ", "ki ", "mein", "ko ")


def classify(text: str) -> str:
    """Say what came back, in terms that can be checked rather than eyeballed."""
    lowered = text.lower()
    arabic = sum(1 for character in text if ord(character) in ARABIC_RANGE)
    roman_hits = sum(1 for marker in ROMAN_URDU_MARKERS if marker in lowered)

    words = text.split()
    looping = len(words) > 20 and len(set(words)) < len(words) / 3

    if arabic > 10:
        script = "PERSIAN" if any(m in text for m in PERSIAN_MARKERS) else "ARABIC-SCRIPT"
        return f"{script}{' + LOOPING' if looping else ''}"
    if roman_hits >= 2:
        return "ROMAN URDU"
    if looping:
        return "LOOPING"
    return "ENGLISH"


def build(system: str, user: str) -> str:
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--n-predict", type=int, default=260)
    parser.add_argument("--output", default="test_results/language_probe.json")
    args = parser.parse_args()

    process = None
    if already_serving(args.port):
        print(f"using the llama-server already on port {args.port}")
    else:
        process = subprocess.Popen(
            ["llama-server", "-m", args.gguf, "--port", str(args.port),
             "-c", "4096", "-t", "8", "--no-warmup"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        wait_for_server(args.port)

    records: list[dict[str, Any]] = []
    try:
        print("\nCODE TASK - the product's own prompt, plus a language requirement")
        for name, block in CODE_TASKS.items():
            instruction = (
                "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
                f"{block}\n\nReturn a single JSON object using the requested field names."
            )
            user = f"{instruction}\n\n### Code\n\n```cpp\n{CODE}\n```"
            text = complete(args.port, build(SYSTEM, user), args.n_predict)
            try:
                answer = str((json.loads(text) or {}).get("explanation") or text)
            except json.JSONDecodeError:
                answer = text
            verdict = classify(answer)
            print(f"  {name:<26} -> {verdict}")
            records.append({"probe": name, "kind": "code", "verdict": verdict, "text": answer})

        print("\nTRANSLATION ONLY - no code, so only the language is under test")
        for name, (system, user) in TRANSLATION_TASKS.items():
            text = complete(args.port, build(system, user), args.n_predict)
            verdict = classify(text)
            print(f"  {name:<26} -> {verdict}")
            records.append({"probe": name, "kind": "translation", "verdict": verdict, "text": text})
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=30)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    produced = [r for r in records if r["verdict"] == "ROMAN URDU"]
    print(f"\n{'=' * 72}")
    print(f"replies that were actually Roman Urdu: {len(produced)}/{len(records)}")
    print("\nIf none, the language is not in this model and prompting cannot add it.")
    print("A translation stage after generation is then the architecture, not a")
    print("second code model.")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
