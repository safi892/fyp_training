"""Does sampling several answers and letting the checks pick actually help?

`best_of` is only worth its inference cost if a second sample of the same
question is measurably cleaner than the first. That is an empirical question
about this model on this code, not something the design can settle, so it is
measured here against what a single-sample deployment would have served.

Sample 0 is drawn at temperature 0 - exactly what serving does today - and the
rest at `--temperature`, so the comparison is against the real baseline rather
than against another sample of the same distribution.

    uv run python scripts/measure_best_of.py --gguf models/gguf/<model>.gguf
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from probe_optimization import wait_for_server  # noqa: E402

from qwen_cpp_review.checked_response import best_of, check_response, objection_count  # noqa: E402
from qwen_cpp_review.prompt import format_prompt_without_response  # noqa: E402


def sample(port: int, prompt: str, n_predict: int, temperature: float, seed: int) -> str:
    payload = json.dumps({
        "prompt": prompt, "n_predict": n_predict,
        "temperature": temperature, "seed": seed, "cache_prompt": False,
    }).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["content"]


def parse(raw: str, field: str) -> object:
    try:
        return (json.loads(raw) or {}).get(field)
    except (json.JSONDecodeError, AttributeError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-v3-q4_k_m.gguf")
    parser.add_argument("--tokenizer", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--seed-dir", type=Path, default=Path("my_data_annotation/recursion_optimization"))
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--n-predict", type=int, default=1200)
    parser.add_argument("--port", type=int, default=8121)
    parser.add_argument("--output", type=Path, default=Path("model_improvement/best_of/measurement.json"))
    args = parser.parse_args()

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    pairs = [
        json.loads(line)
        for line in (args.seed_dir / "seed.jsonl").read_text().splitlines()
        if line.strip()
    ]
    programs = []
    for pair in pairs:
        programs.append((f"{pair['name']} recursive", pair["code"]))
        programs.append((f"{pair['name']} iterative", pair["improved_code"]))

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
         "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for_server(args.port)
        for name, code in programs:
            responses = []
            for index in range(args.samples):
                response = {}
                for task, field in (("line_comments", "line_comments"), ("explanation", "explanation")):
                    prompt = format_prompt_without_response(
                        code, [], style="chat", tokenizer=tokenizer, task=task
                    )
                    # Sample 0 is the deployed setting; the rest explore.
                    raw = sample(
                        args.port, prompt, args.n_predict,
                        0.0 if index == 0 else args.temperature, index,
                    )
                    response[field] = parse(raw, field)
                responses.append(response)

            first = check_response(code, responses[0], verify_improved=False)
            picked, index = best_of(code, responses, verify_improved=False)
            records.append({
                "name": name,
                "first_objections": objection_count(first),
                "best_objections": objection_count(picked),
                "chose": index,
                "per_sample": [
                    objection_count(check_response(code, r, verify_improved=False))
                    for r in responses
                ],
            })
            print(f"  {name:28} first={records[-1]['first_objections']:>2} "
                  f"best={records[-1]['best_objections']:>2} (sample {index})", flush=True)
    finally:
        process.terminate()
        process.wait(timeout=30)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    first_total = sum(r["first_objections"] for r in records)
    best_total = sum(r["best_objections"] for r in records)
    clean_first = sum(1 for r in records if r["first_objections"] == 0)
    clean_best = sum(1 for r in records if r["best_objections"] == 0)
    print(f"\n{'=' * 68}")
    print(f"objections, single sample : {first_total}")
    print(f"objections, best of {args.samples:<5} : {best_total}")
    print(f"clean answers  {clean_first}/{len(records)} -> {clean_best}/{len(records)}")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
