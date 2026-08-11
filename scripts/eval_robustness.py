"""Measure how much the model's output depends on identifier names.

Runs the same held-out C++ through six namings and reports what changes. The
number to read is the delta against `original`: it separates understanding of
the code from reading of the names, which is the distinction *When Names
Disappear* (arXiv 2510.03178) showed most models fail.

    uv run python scripts/eval_robustness.py \
        --base-model models/Qwen2.5-Coder-1.5B-Instruct \
        --adapter path/to/best_adapter

Generation on CPU is slow, so start with --samples 2 to see the shape of the
output before running the whole set.

Metrics per variant
  json          share of responses that parse
  anchors       share of emitted anchors whose quoted line exists, after
                relocating by that quote (what a user actually receives)
  raw anchors   the same before relocation, which is the model's own counting
  concepts      share of concept groups the explanation names; the primary
                signal, since it is scored against words that never appear as
                identifiers and so cannot be echoed back
  agreement     word overlap between this variant's explanation and the
                explanation for `original`, on the same sample
"""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from qwen_cpp_review.line_anchoring import repair_anchors
from qwen_cpp_review.obfuscation import STRATEGIES, mixed, obfuscate
from qwen_cpp_review.prompt import format_prompt_without_response
from qwen_cpp_review.robustness_samples import SAMPLES

VARIANTS = ["original", "clear", "terse", "noise", "misleading", "mixed"]
WORD_RE = re.compile(r"[a-z]+")
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "is", "are", "it", "its", "in",
    "on", "for", "with", "that", "this", "which", "as", "by", "be", "from",
    "at", "if", "then", "else", "not", "into", "each", "all", "we", "you",
    "function", "code", "value", "values", "int", "return", "returns",
}


def resolve_adapter(adapter: str) -> str:
    """Fail clearly when the adapter path is wrong.

    PEFT falls back to treating an unknown path as a Hub repo id, so a typo or
    a copied placeholder surfaces as an opaque HFValidationError about repo
    naming rules rather than "that folder is not here".
    """
    path = Path(adapter)
    if path.exists():
        if (path / "adapter_config.json").exists():
            return str(path)
        raise SystemExit(
            f"{path} has no adapter_config.json, so it is not a LoRA adapter.\n"
            f"It contains: {', '.join(sorted(p.name for p in path.iterdir())[:10]) or '(empty)'}"
        )
    if "/" in adapter and not adapter.replace("/", "").replace("-", "").replace("_", "").isalnum():
        raise SystemExit(
            f"No such directory: {adapter}\n"
            f"That looks like a local path rather than a Hub model id. Did you paste an "
            f"abbreviated example such as '.../best_adapter'? Use the full path, e.g.\n"
            f"  kaggle_output/'results(4)'/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter"
        )
    return adapter


def make_variant(code: str, variant: str, rng: random.Random) -> str:
    return mixed(code, rng) if variant == "mixed" else obfuscate(code, variant, rng)


def content_words(text: str) -> set[str]:
    return {w for w in WORD_RE.findall(text.lower()) if len(w) > 2 and w not in STOPWORDS}


def concept_score(text: str, concepts: list[list[str]]) -> tuple[int, int]:
    lowered = text.lower()
    hit = sum(1 for group in concepts if any(word.lower() in lowered for word in group))
    return hit, len(concepts)


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def generate(model, tokenizer, code: str, task: str, max_new_tokens: int) -> tuple[str, float]:
    prompt = format_prompt_without_response(code, [], style="chat", tokenizer=tokenizer, task=task)
    inputs = tokenizer(prompt, return_tensors="pt")
    started = time.perf_counter()
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    text = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return text, time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--adapter", default=None, help="Omit to evaluate the base model.")
    parser.add_argument("--base-model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--samples", type=int, default=len(SAMPLES))
    parser.add_argument("--variants", nargs="+", default=VARIANTS)
    parser.add_argument("--max-new-tokens", type=int, default=400)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="test_results/robustness.jsonl")
    args = parser.parse_args()

    unknown = [v for v in args.variants if v not in STRATEGIES and v != "mixed"]
    if unknown:
        raise SystemExit(f"unknown variants {unknown}; known: {sorted(STRATEGIES) + ['mixed']}")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=torch.float32)
    label = "base model"
    if args.adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, resolve_adapter(args.adapter))
        label = Path(args.adapter).name
    model.eval()

    samples = SAMPLES[: args.samples]
    print(f"model    : {label}")
    print(f"samples  : {len(samples)}   variants: {len(args.variants)}   "
          f"generations: {len(samples) * len(args.variants) * 2}\n")

    records: list[dict[str, Any]] = []
    baseline_words: dict[str, set[str]] = {}

    # Written as each generation completes rather than at the end: the whole run
    # takes tens of minutes on CPU, and a partial file is reviewable while a
    # lost one is not.
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    handle = output_path.open("w", encoding="utf-8")

    for sample in samples:
        for variant in args.variants:
            rng = random.Random(f"{args.seed}-{sample['name']}-{variant}".__hash__() & 0xFFFF)
            code = make_variant(sample["code"], variant, rng)
            record: dict[str, Any] = {"sample": sample["name"], "variant": variant, "code": code}

            comment_text, seconds = generate(model, tokenizer, code, "line_comments", args.max_new_tokens)
            record["line_comments_raw"] = comment_text
            record["seconds_line_comments"] = round(seconds, 1)
            try:
                anchors = (json.loads(comment_text) or {}).get("line_comments") or []
                record["line_comments_json_ok"] = True
            except json.JSONDecodeError:
                anchors = []
                record["line_comments_json_ok"] = False
            report = repair_anchors(code, anchors)
            lines = [line.strip() for line in code.split("\n")]
            record["anchors_total"] = report.total
            record["anchors_kept"] = report.exact + report.repaired
            record["anchors_exact"] = report.exact
            record["anchors_dropped"] = report.dropped
            record["anchor_comments"] = [a.comment for a in report.anchors]
            record["coverage"] = round(
                len({a.line for a in report.anchors}) / max(1, sum(1 for line in lines if line not in ("", "{", "}"))),
                3,
            )

            explanation_text, seconds = generate(model, tokenizer, code, "explanation", args.max_new_tokens)
            record["seconds_explanation"] = round(seconds, 1)
            try:
                explanation = (json.loads(explanation_text) or {}).get("explanation") or ""
                record["explanation_json_ok"] = True
            except json.JSONDecodeError:
                explanation = explanation_text
                record["explanation_json_ok"] = False
            record["explanation"] = explanation

            # Concepts are scored over both outputs: an idea named in the
            # line comments counts as understood just as much as one in prose.
            combined = explanation + " " + " ".join(record["anchor_comments"])
            hit, total = concept_score(combined, sample["concepts"])
            record["concepts_hit"] = hit
            record["concepts_total"] = total

            words = content_words(combined)
            if variant == "original":
                baseline_words[sample["name"]] = words
            record["agreement"] = round(jaccard(words, baseline_words.get(sample["name"], set())), 3)

            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"  {sample['name']:<18}{variant:<12}"
                  f"concepts {hit}/{total}  anchors {record['anchors_kept']}/{report.total}  "
                  f"agree {record['agreement']:.2f}  "
                  f"({record['seconds_line_comments'] + record['seconds_explanation']:.0f}s)",
                  flush=True)

    handle.close()

    print("\n" + "=" * 78)
    print(f"{'variant':<14}{'json':>8}{'raw anch':>10}{'anchors':>9}{'concepts':>10}{'agreement':>11}")
    baseline_concepts = None
    for variant in args.variants:
        rows = [r for r in records if r["variant"] == variant]
        if not rows:
            continue
        json_ok = sum(r["line_comments_json_ok"] + r["explanation_json_ok"] for r in rows) / (2 * len(rows))
        kept = sum(r["anchors_kept"] for r in rows)
        exact = sum(r["anchors_exact"] for r in rows)
        total = sum(r["anchors_total"] for r in rows)
        concepts = sum(r["concepts_hit"] for r in rows) / max(1, sum(r["concepts_total"] for r in rows))
        agreement = sum(r["agreement"] for r in rows) / len(rows)
        if variant == "original":
            baseline_concepts = concepts
        delta = "" if baseline_concepts is None else f"  ({concepts - baseline_concepts:+.1%})"
        print(f"{variant:<14}{json_ok:>7.0%}{exact / max(1, total):>10.0%}{kept / max(1, total):>9.0%}"
              f"{concepts:>9.0%}{agreement:>11.2f}{delta}")

    print("\nconcepts is the headline: the share of ideas named whatever the")
    print("identifiers are called. A large drop from `original` means the model")
    print("was reading names rather than code.")
    print(f"\nwrote {output_path}")


if __name__ == "__main__":
    main()
