"""Run the model over your own C++ and print what it says.

The quickest way to judge the model: hand it a file and read the output.

    uv run python scripts/try_model.py --adapter path/to/best_adapter --code-file mine.cpp
    uv run python scripts/try_model.py --adapter path/to/best_adapter --code-file mine.cpp \\
        --tasks improve --obfuscate misleading

Anchors are checked against the file, so a comment claiming a line that is not
there is reported rather than shown as fact. Generation on CPU is slow; a long
file will take minutes, and --max-new-tokens must be large enough to finish the
answer or the JSON arrives truncated.
"""

from __future__ import annotations

import argparse
import difflib
import json
import random
import re
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from qwen_cpp_review.line_anchoring import repair_anchors
from qwen_cpp_review.obfuscation import STRATEGIES, collect_function_names, mixed, obfuscate
from qwen_cpp_review.prompt import TASKS, format_prompt_without_response

DEFAULT_CODE = """int factorial(int n)
{
  if (n <= 1)
    return 1;
  return n * factorial(n - 1);
}"""


def show_line_comments(code: str, parsed: dict) -> None:
    report = repair_anchors(code, parsed.get("line_comments") or [])
    lines = code.split("\n")
    by_line: dict[int, list[str]] = {}
    for anchor in report.anchors:
        by_line.setdefault(anchor.line, []).append(anchor.comment)

    width = max((len(line) for line in lines), default = 0)
    for number, line in enumerate(lines, start=1):
        comments = by_line.get(number)
        note = f"   // {'; '.join(comments)}" if comments else ""
        print(f"  {number:>3}  {line:<{width}}{note}")

    print(
        f"\n  anchors: {report.exact + report.repaired}/{report.total} usable "
        f"({report.exact} already on the right line, {report.repaired} relocated by their quoted "
        f"code, {report.dropped} quoting text absent from the file)"
    )
    if report.dropped:
        print("  ! dropped anchors are hallucinations - the model quoted a line you did not write")


def show_improved(code: str, parsed: dict) -> None:
    improved = parsed.get("improved_code") or ""
    print(improved)
    diff = list(
        difflib.unified_diff(
            code.split("\n"), improved.split("\n"), fromfile="yours", tofile="model", lineterm=""
        )
    )
    if diff:
        print("\n  --- what changed ---")
        for line in diff:
            print(f"  {line}")
    else:
        print("\n  (identical to the input)")
    hints = []
    if re.search(r"\b(for|while)\s*\(", improved):
        hints.append("uses a loop")
    names = collect_function_names(code)
    if names and improved.count(names[0]) > 1:
        hints.append(f"still calls {names[0]} inside itself, so the recursion remains")
    elif names and re.search(r"\b(for|while)\s*\(", improved) and not re.search(r"\b(for|while)\s*\(", code):
        hints.append("recursion appears to have become iteration")
    if hints:
        print(f"\n  note: {'; '.join(hints)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--adapter", default=None, help="Omit to see what the base model does.")
    parser.add_argument("--base-model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--code-file", default=None, help="A .cpp file. Defaults to a recursive factorial.")
    parser.add_argument("--code", default=None, help="C++ passed directly instead of a file.")
    parser.add_argument("--tasks", nargs="+", default=["line_comments", "explanation"])
    parser.add_argument(
        "--obfuscate",
        default=None,
        choices=sorted(STRATEGIES) + ["mixed"],
        help="Rename the identifiers first, to see whether the answer depends on them.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=900)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    unknown = [task for task in args.tasks if task not in TASKS]
    if unknown:
        raise SystemExit(f"unknown tasks {unknown}; known: {sorted(TASKS)}")

    if args.code:
        code = args.code
    elif args.code_file:
        code = Path(args.code_file).read_text(encoding="utf-8").rstrip("\n")
    else:
        code = DEFAULT_CODE

    if args.obfuscate:
        rng = random.Random(args.seed)
        code = mixed(code, rng) if args.obfuscate == "mixed" else obfuscate(code, args.obfuscate, rng)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=torch.float32)
    label = "base model, no adapter"
    if args.adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, args.adapter)
        label = Path(args.adapter).name
    model.eval()

    print(f"model : {label}")
    if args.obfuscate:
        print(f"names : renamed with `{args.obfuscate}`")
    print(f"lines : {len(code.split(chr(10)))}\n")
    print("INPUT")
    for number, line in enumerate(code.split("\n"), start=1):
        print(f"  {number:>3}  {line}")

    failures = 0
    for task in args.tasks:
        prompt = format_prompt_without_response(code, [], style="chat", tokenizer=tokenizer, task=task)
        inputs = tokenizer(prompt, return_tensors="pt")
        started = time.perf_counter()
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )
        produced = output.shape[1] - inputs["input_ids"].shape[1]
        text = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        elapsed = time.perf_counter() - started

        print(f"\n{'=' * 72}\n{task.upper()}   ({produced} tokens, {elapsed:.0f}s, "
              f"{produced / max(elapsed, 1e-6):.1f} tok/s)\n{'=' * 72}")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            failures += 1
            print(f"  INVALID JSON: {exc}")
            if produced >= args.max_new_tokens:
                print(f"  The answer hit the {args.max_new_tokens}-token limit and was cut off. "
                      f"Raise --max-new-tokens.")
            print(f"  raw:\n{text}")
            continue

        if task == "line_comments":
            show_line_comments(code, parsed)
        elif task == "improve":
            show_improved(code, parsed)
        else:
            for key, value in parsed.items():
                print(f"{value}" if isinstance(value, str) else f"{key}: {json.dumps(value, indent=2)}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
