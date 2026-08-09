"""Generate with a trained adapter and check the output against the input.

This is the acceptance check for the line-anchored format: every anchor the
model emits carries a line number and the text of that line, so an anchor can
be compared against the source it claims to describe. An anchor whose text does
not match the input is a hallucination, and this reports the rate.

    uv run python scripts/eval_adapter.py \
        --adapter kaggle_output/'results (1)'/outputs/.../checkpoint-500 \
        --tasks line_comments complexity --samples 3

Runs on CPU. Generation is slow there, so keep --samples small.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from qwen_cpp_review.prompt import TASKS, format_prompt_without_response

SYSTEM_SAMPLES: list[dict[str, Any]] = [
    {
        "name": "digit_sum_loop",
        "code": (
            "int countDigits(int a, int b)\n"
            "{\n"
            "  int sum = a + b;\n"
            "  int count = 0;\n"
            "  while (sum != 0)\n"
            "  {\n"
            "    sum /= 10;\n"
            "    count++;\n"
            "  }\n"
            "  return count;\n"
            "}"
        ),
    },
    {
        "name": "recursive_fib",
        "code": (
            "int fib(int n)\n"
            "{\n"
            "  if (n <= 1)\n"
            "    return n;\n"
            "  return fib(n - 1) + fib(n - 2);\n"
            "}"
        ),
    },
    {
        # Deliberately meaningless names: the same code as digit_sum_loop.
        "name": "digit_sum_loop_obfuscated",
        "code": (
            "int f(int x, int y)\n"
            "{\n"
            "  int a = x + y;\n"
            "  int b = 0;\n"
            "  while (a != 0)\n"
            "  {\n"
            "    a /= 10;\n"
            "    b++;\n"
            "  }\n"
            "  return b;\n"
            "}"
        ),
    },
]


def check_anchors(code: str, anchors: list[dict[str, Any]]) -> tuple[int, int, list[str]]:
    """Return ``(valid, total, problems)`` for one set of anchors."""
    lines = [line.strip() for line in code.split("\n")]
    valid = 0
    problems: list[str] = []
    seen: set[int] = set()
    for anchor in anchors:
        number = anchor.get("line")
        text = anchor.get("code")
        if not isinstance(number, int) or not isinstance(text, str):
            problems.append(f"malformed anchor: {anchor!r}")
            continue
        if number in seen:
            problems.append(f"line {number} annotated twice")
        seen.add(number)
        if not 1 <= number <= len(lines):
            problems.append(f"line {number} is outside the file (1-{len(lines)})")
            continue
        if lines[number - 1] != text.strip():
            problems.append(f"line {number}: claimed {text.strip()!r}, actual {lines[number - 1]!r}")
            continue
        valid += 1
    return valid, len(anchors), problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--tasks", nargs="+", default=["line_comments", "complexity"])
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--base-only", action="store_true", help="Skip the adapter, to compare against it.")
    args = parser.parse_args()

    unknown = [task for task in args.tasks if task not in TASKS]
    if unknown:
        raise SystemExit(f"unknown tasks {unknown}; known: {sorted(TASKS)}")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=torch.float32)
    label = "BASE MODEL (no adapter)"
    if not args.base_only:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, args.adapter)
        label = f"ADAPTER {Path(args.adapter).name}"
    model.eval()
    print(f"=== {label} ===\n")

    anchors_valid = anchors_total = 0
    json_ok = json_total = 0

    for sample in SYSTEM_SAMPLES[: args.samples]:
        for task in args.tasks:
            prompt = format_prompt_without_response(
                sample["code"], [], style="chat", tokenizer=tokenizer, task=task
            )
            inputs = tokenizer(prompt, return_tensors="pt")
            started = time.perf_counter()
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                )
            text = tokenizer.decode(
                generated[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
            )
            elapsed = time.perf_counter() - started
            new_tokens = generated.shape[1] - inputs["input_ids"].shape[1]

            print(f"--- {sample['name']} / {task}  ({new_tokens} tok, {elapsed:.0f}s, "
                  f"{new_tokens / elapsed:.1f} tok/s) ---")
            json_total += 1
            try:
                parsed = json.loads(text)
                json_ok += 1
            except json.JSONDecodeError as exc:
                print(f"  INVALID JSON: {exc}")
                print(f"  raw: {text[:300]}")
                continue

            if task == "line_comments":
                found = parsed.get("line_comments") or []
                valid, total, problems = check_anchors(sample["code"], found)
                anchors_valid += valid
                anchors_total += total
                print(f"  anchors: {valid}/{total} valid")
                for problem in problems[:5]:
                    print(f"    ! {problem}")
                for anchor in found[:4]:
                    print(f"    line {anchor.get('line'):>3}: {str(anchor.get('comment'))[:70]}")
            else:
                print(f"  {json.dumps(parsed, ensure_ascii=False)[:300]}")
            print()

    print("=" * 68)
    print(f"parseable JSON : {json_ok}/{json_total}")
    if anchors_total:
        print(f"anchor validity: {anchors_valid}/{anchors_total} = {anchors_valid / anchors_total:.1%}")
        print("  (Phase A acceptance target is >90%)")


if __name__ == "__main__":
    main()
