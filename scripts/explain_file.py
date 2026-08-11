"""Annotate a whole C++ file, line by line.

The model answers about one function at a time, because that is the shape it
was trained on and a long file does not fit its sequence length. This splits
the file on syntax boundaries, asks about each piece, and puts the answers back
in file coordinates.

    uv run python scripts/explain_file.py --adapter path/to/best_adapter \\
        --file examples/inventory.cpp --output notes.md

Every comment that survives is checked against the line it claims, so the
output can be trusted against the original file rather than believed.
Generation is slow on CPU - budget a minute or two per chunk.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from qwen_cpp_review.chunking import Chunk, chunk_code, stitch
from qwen_cpp_review.prompt import format_prompt_without_response


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


def annotate(model, tokenizer, chunk: Chunk, max_new_tokens: int) -> tuple[list[dict], str]:
    """Return ``(anchors, status)`` for one chunk."""
    prompt = format_prompt_without_response(
        chunk.text, [], style="chat", tokenizer=tokenizer, task="line_comments"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    produced = output.shape[1] - inputs["input_ids"].shape[1]
    text = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    try:
        return (json.loads(text) or {}).get("line_comments") or [], "ok"
    except json.JSONDecodeError:
        return [], "truncated" if produced >= max_new_tokens else "unparseable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", required=True)
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--base-model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--max-tokens", type=int, default=300, help="Chunk size budget.")
    parser.add_argument("--max-new-tokens", type=int, default=700, help="Answer budget per chunk.")
    parser.add_argument("--output", default=None, help="Write markdown here as well as stdout.")
    args = parser.parse_args()

    source = Path(args.file)
    code = source.read_text(encoding="utf-8").rstrip("\n")
    lines = code.split("\n")
    chunks = chunk_code(code, max_tokens=args.max_tokens)

    print(f"file   : {source}  ({len(lines)} lines)")
    print(f"chunks : {len(chunks)}")
    for chunk in chunks:
        flag = "  OVERSIZED" if chunk.oversized else ""
        print(f"   {chunk.start_line:>4}-{chunk.end_line:<4} {chunk.kind}{flag}")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=torch.float32)
    label = "base model"
    if args.adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, resolve_adapter(args.adapter))
        label = Path(args.adapter).name
    model.eval()
    print(f"model  : {label}\n")

    results: list[tuple[Chunk, list[dict]]] = []
    statuses: list[str] = []
    started = time.perf_counter()
    for index, chunk in enumerate(chunks, start=1):
        chunk_started = time.perf_counter()
        raw, status = annotate(model, tokenizer, chunk, args.max_new_tokens)
        results.append((chunk, raw))
        statuses.append(status)
        print(
            f"  [{index}/{len(chunks)}] lines {chunk.start_line}-{chunk.end_line}  "
            f"{len(raw)} anchors  {status}  ({time.perf_counter() - chunk_started:.0f}s)",
            flush=True,
        )

    anchors = stitch(code, results)
    by_line = {anchor.line: anchor.comment for anchor in anchors}
    proposed = sum(len(raw) for _, raw in results)
    substantive = sum(1 for line in lines if line.strip() and line.strip() not in ("{", "}", "};"))

    print(f"\n{'=' * 72}")
    print(f"anchors proposed by the model : {proposed}")
    print(f"anchors that match the file   : {len(anchors)}"
          f"  ({len(anchors) / proposed:.0%})" if proposed else "")
    print(f"lines covered                 : {len(anchors)}/{substantive} substantive "
          f"({len(anchors) / max(1, substantive):.0%})")
    failed = [s for s in statuses if s != "ok"]
    if failed:
        print(f"chunks with no usable answer  : {len(failed)} ({', '.join(sorted(set(failed)))})")
        if "truncated" in failed:
            print("  raise --max-new-tokens; the answer was cut off mid-JSON")
    print(f"elapsed                       : {time.perf_counter() - started:.0f}s")

    width = max(len(line) for line in lines)
    rendered = [
        f"{number:>4}  {line:<{width}}" + (f"   // {by_line[number]}" if number in by_line else "")
        for number, line in enumerate(lines, start=1)
    ]
    print(f"\n{'=' * 72}\nANNOTATED\n{'=' * 72}")
    print("\n".join(rendered))

    if args.output:
        report = [
            f"# {source.name} — line-by-line",
            "",
            f"`{label}` · {len(lines)} lines · {len(chunks)} chunks · "
            f"{len(anchors)}/{proposed} anchors verified against the file",
            "",
            "Every comment below was checked against the line it points at. "
            "Anything the model invented was dropped rather than shown.",
            "",
            "```cpp",
            *rendered,
            "```",
        ]
        Path(args.output).write_text("\n".join(report), encoding="utf-8")
        print(f"\nwrote {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
