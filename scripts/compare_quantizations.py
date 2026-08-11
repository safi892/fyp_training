"""Check what quantisation costs before trusting it.

Quantising is only worth doing if the answers survive it, and "it looked fine"
is not a measurement. This runs the identical prompts through each GGUF and
scores them the same way the fp32 evaluation does, so the speed gain and the
accuracy cost are read off the same table.

    uv run python scripts/compare_quantizations.py \\
        --models models/gguf/*.gguf --reference test_results/robustness.jsonl

Each model is served in turn by llama-server, which loads the weights once
instead of per prompt. The reference file is the fp32 run, used to report how
often a quantised model gives the same answer as the original.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from qwen_cpp_review.line_anchoring import repair_anchors
from qwen_cpp_review.robustness_samples import SAMPLES

WORD_RE = re.compile(r"[a-z]+")


def wait_for_server(port: int, timeout: float = 300.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
                if json.load(response).get("status") == "ok":
                    return
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError(f"llama-server on port {port} did not become ready")


def complete(port: int, prompt: str, n_predict: int) -> tuple[str, float]:
    payload = json.dumps(
        {"prompt": prompt, "n_predict": n_predict, "temperature": 0, "cache_prompt": False}
    ).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        body = json.load(response)
    return body["content"], body.get("timings", {}).get("predicted_per_second", 0.0)


def concept_hits(text: str, concepts: list[list[str]]) -> int:
    lowered = text.lower()
    return sum(1 for group in concepts if any(word.lower() in lowered for word in group))


def score_sample(sample: dict[str, Any], comments_raw: str, explanation_raw: str) -> dict[str, Any]:
    code = sample["code"]
    try:
        anchors = (json.loads(comments_raw) or {}).get("line_comments") or []
        comments_ok = True
    except json.JSONDecodeError:
        anchors, comments_ok = [], False
    report = repair_anchors(code, anchors)

    try:
        explanation = (json.loads(explanation_raw) or {}).get("explanation") or ""
        explanation_ok = True
    except json.JSONDecodeError:
        explanation, explanation_ok = explanation_raw, False

    combined = explanation + " " + " ".join(a.comment for a in report.anchors)
    return {
        "json_ok": int(comments_ok) + int(explanation_ok),
        "anchors_total": report.total,
        "anchors_kept": report.exact + report.repaired,
        "anchors_dropped": report.dropped,
        "concepts_hit": concept_hits(combined, sample["concepts"]),
        "concepts_total": len(sample["concepts"]),
        "explanation": explanation,
        "line_comments_raw": comments_raw,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", required=True, help="GGUF files to compare.")
    parser.add_argument("--base-model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--reference", default=None, help="fp32 robustness.jsonl to compare against.")
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--n-predict", type=int, default=500)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--output", default="test_results/quantization.json")
    args = parser.parse_args()

    from transformers import AutoTokenizer

    from qwen_cpp_review.prompt import format_prompt_without_response

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    samples = SAMPLES[: args.samples]

    reference: dict[str, str] = {}
    if args.reference and Path(args.reference).exists():
        for line in Path(args.reference).read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("variant") == "original":
                reference[record["sample"]] = (record.get("explanation") or "").strip()
        print(f"reference: {len(reference)} fp32 explanations from {args.reference}\n")

    results: dict[str, Any] = {}
    for model_path in args.models:
        name = Path(model_path).stem
        size_gb = Path(model_path).stat().st_size / 1024**3
        print(f"--- {name}  ({size_gb:.2f} GB) ---", flush=True)

        process = subprocess.Popen(
            ["llama-server", "-m", model_path, "--port", str(args.port),
             "-c", "4096", "-t", str(args.threads), "--no-warmup"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_for_server(args.port)
            scored: list[dict[str, Any]] = []
            speeds: list[float] = []
            for sample in samples:
                outputs = {}
                for task in ("line_comments", "explanation"):
                    prompt = format_prompt_without_response(
                        sample["code"], [], style="chat", tokenizer=tokenizer, task=task
                    )
                    text, speed = complete(args.port, prompt, args.n_predict)
                    outputs[task] = text
                    speeds.append(speed)
                row = score_sample(sample, outputs["line_comments"], outputs["explanation"])
                row["sample"] = sample["name"]
                scored.append(row)
                print(f"  {sample['name']:<18}concepts {row['concepts_hit']}/{row['concepts_total']}  "
                      f"anchors {row['anchors_kept']}/{row['anchors_total']}", flush=True)
        finally:
            process.terminate()
            process.wait(timeout=30)

        total_anchors = sum(r["anchors_total"] for r in scored)
        agreement = None
        if reference:
            matches = [
                _similarity(r["explanation"], reference.get(r["sample"], ""))
                for r in scored
                if reference.get(r["sample"])
            ]
            agreement = sum(matches) / len(matches) if matches else None

        results[name] = {
            "size_gb": round(size_gb, 2),
            "tokens_per_second": round(sum(speeds) / len(speeds), 1),
            "json_ok": sum(r["json_ok"] for r in scored) / (2 * len(scored)),
            "anchors_kept": sum(r["anchors_kept"] for r in scored),
            "anchors_total": total_anchors,
            "anchor_validity": (sum(r["anchors_kept"] for r in scored) / total_anchors) if total_anchors else 0.0,
            "concepts": sum(r["concepts_hit"] for r in scored) / sum(r["concepts_total"] for r in scored),
            "agreement_with_fp32": round(agreement, 3) if agreement is not None else None,
            "per_sample": scored,
        }
        print()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("=" * 86)
    header = f"{'model':<28}{'GB':>6}{'tok/s':>8}{'JSON':>7}{'anchors':>9}{'concepts':>10}{'vs fp32':>10}"
    print(header)
    for name, row in results.items():
        agree = f"{row['agreement_with_fp32']:.2f}" if row["agreement_with_fp32"] is not None else "-"
        print(f"{name:<28}{row['size_gb']:>6.2f}{row['tokens_per_second']:>8.1f}{row['json_ok']:>7.0%}"
              f"{row['anchor_validity']:>9.0%}{row['concepts']:>10.0%}{agree:>10}")
    print("\nconcepts and anchors are the accuracy figures; a drop here is a real")
    print("cost. vs fp32 is word overlap with the unquantised explanation.")
    print(f"\nwrote {args.output}")


def _similarity(left: str, right: str) -> float:
    a = set(WORD_RE.findall(left.lower()))
    b = set(WORD_RE.findall(right.lower()))
    return len(a & b) / len(a | b) if a and b else 0.0


if __name__ == "__main__":
    main()
