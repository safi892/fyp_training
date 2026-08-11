"""Ask whether the model can already notice a defect when told not to assume one away.

`eval_hard.py` measured what the product asks for today: the model described
eight broken programs as though they worked, asserting something false about
four of them. That is a result about the *instruction* as much as the weights.
The trained wording asks what the code does on the assumption it does something
sensible, and on every row of the corpus that assumption held.

The same question was worth asking before building an optimisation dataset, and
the answer there was that the capability was present and the instruction was the
problem — `probe_optimization.py`, trained wording 0/3, explicit wording 3/3.
Building a verified buggy-code corpus is roughly ten days of work, so it is
worth half a day to find out whether a sentence does it instead.

Three things are measured for every phrasing, because a phrasing that finds
defects and wrecks the rest is not usable:

- **buggy code**  — problems named, and false claims made
- **correct code** — defects invented, which is the failure mode that would
  make the product worse, since correct code is its normal input
- **anchors**      — validity against the submitted source, which everything
  downstream of the model depends on

    uv run python scripts/probe_defects.py

Reuses a llama-server already listening on ``--port``; starts one otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from eval_hard import (  # noqa: E402  (path set above)
    SAMPLES,
    already_serving,
    complete,
    score,
    wait_for_server,
)

from qwen_cpp_review.line_anchoring import repair_anchors  # noqa: E402
from qwen_cpp_review.prompt import format_prompt_without_response  # noqa: E402

#: Correct, conventional functions - the product's normal input. A phrasing
#: that makes the model report defects here has moved the problem rather than
#: solved it, and these are deliberately the same shapes the broken samples
#: imitate, so a lazy "mentions a bug whenever the code looks like a sort"
#: heuristic is caught.
CLEAN_SAMPLES: list[dict[str, str]] = [
    {
        "name": "correct_swap",
        "code": """void sortValues(int data[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (data[j] > data[j + 1]) {
                int spare = data[j];
                data[j] = data[j + 1];
                data[j + 1] = spare;
            }
        }
    }
}""",
    },
    {
        "name": "correct_binary_search",
        "code": """int findValue(int arr[], int size, int target) {
    int low = 0, high = size - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}""",
    },
    {
        "name": "correct_erase",
        "code": """void removeNegatives(std::vector<int>& values) {
    for (auto it = values.begin(); it != values.end(); ) {
        if (*it < 0)
            it = values.erase(it);
        else
            ++it;
    }
}""",
    },
    {
        "name": "correct_counter",
        "code": """int countMatches(const std::vector<int>& items, int wanted) {
    int found = 0;
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (items[i] == wanted)
            found = found + 1;
    }
    return found;
}""",
    },
]

#: Extra sentences appended to the trained instruction. ``trained_wording`` is
#: the control and must stay exactly what the product sends, or the comparison
#: measures two changes at once.
PHRASINGS: dict[str, str] = {
    "trained_wording": "",
    "describe_effect": (
        "Describe what each line actually does when executed. Do not describe "
        "what the function appears intended to do."
    ),
    "assume_nothing": (
        "This code may contain defects. Do not assume it is correct. Describe "
        "what each line actually does when executed, and where a line's effect "
        "differs from what the surrounding code appears intended to achieve, "
        "say so plainly."
    ),
}

#: Words that only appear when the model is alleging something is wrong. Used
#: on correct code, where any hit is a false positive.
_ALLEGATION = re.compile(
    r"\b(bug|buggy|incorrect|wrong|defect|error|broken|flaw|mistake|fails?|failing"
    r"|undefined behavi|overwrit|lost|loses|clobber|invalid|does not (work|sort|match)"
    r"|never (work|return|increment)|should be|instead of)\b",
    re.I,
)


def build_prompt(code: str, task: str, extra: str, tokenizer: Any) -> str:
    """Render the product's prompt for ``task``, with ``extra`` appended.

    The trained instruction is produced by the package rather than retyped, so
    the control arm is genuinely what the service sends. Additional wording is
    appended to the same user message rather than replacing it, which keeps the
    requested JSON field names intact — a phrasing that changed them would be
    measuring the parser, not the model.
    """
    base = format_prompt_without_response(
        code, [], style="chat", tokenizer=tokenizer, task=task
    )
    if not extra:
        return base
    marker = "\n\n### Code\n\n"
    head, _, tail = base.partition(marker)
    return f"{head}\n\n{extra}{marker}{tail}"


def read_fields(comments_raw: str, explanation_raw: str) -> tuple[list[dict], str, int]:
    """Pull the two answers apart, tolerating a malformed one."""
    anchors: list[dict] = []
    parsed = 0
    try:
        payload = json.loads(comments_raw) or {}
        anchors = [a for a in (payload.get("line_comments") or []) if isinstance(a, dict)]
        parsed += 1
    except (json.JSONDecodeError, AttributeError):
        pass
    explanation = explanation_raw
    try:
        explanation = str((json.loads(explanation_raw) or {}).get("explanation") or "")
        parsed += 1
    except (json.JSONDecodeError, AttributeError):
        pass
    return anchors, explanation, parsed


def run_one(port: int, code: str, extra: str, n_predict: int, tokenizer: Any) -> dict[str, Any]:
    """Generate both fields for one sample under one phrasing."""
    raw = {
        task: complete(port, build_prompt(code, task, extra, tokenizer), n_predict)
        for task in ("line_comments", "explanation")
    }
    anchors, explanation, parsed = read_fields(raw["line_comments"], raw["explanation"])
    report = repair_anchors(code, anchors)
    text = "\n".join([*(str(a.get("comment") or "") for a in anchors), explanation])
    return {
        "text": text,
        "json_ok": parsed == 2,
        "anchors_proposed": len(anchors),
        "anchors_kept": len(report.anchors),
        "raw": raw,
    }


def write_report(rows: list[dict[str, Any]], totals: dict[str, Any], path: Path) -> None:
    lines = [
        "# Defect-awareness probe",
        "",
        "Does explicit wording get the model to report what a line *does* rather than",
        "what the function looks like it was meant to do? The trained wording is the",
        "control: it is exactly what `/analyze` sends today.",
        "",
        "A phrasing only helps if it moves the first two columns without moving the",
        "third — correct code is the product's normal input, and inventing defects in",
        "it would be a worse failure than missing real ones.",
        "",
        "| phrasing | problems named | false claims (of 8) | defects invented on correct code (of 4) | anchor validity |",
        "| --- | :---: | :---: | :---: | :---: |",
    ]
    for name in PHRASINGS:
        t = totals[name]
        lines.append(
            f"| `{name}` | {t['found']}/{t['of']} | {t['false_claims']} | "
            f"{t['invented']} | {t['anchors_kept']}/{t['anchors_proposed']} |"
        )
    lines += ["", "---", ""]

    for name in PHRASINGS:
        lines += [f"## {name}", ""]
        if PHRASINGS[name]:
            lines += ["> " + PHRASINGS[name], ""]
        else:
            lines += ["> *(the trained instruction, unchanged)*", ""]
        for row in rows:
            if row["phrasing"] != name:
                continue
            if row["kind"] == "buggy":
                verdict = f"found {row['found']}/{row['of']}"
                if row["false_claim"]:
                    verdict += ", **asserted something false**"
            else:
                verdict = "**invented a defect**" if row["invented"] else "clean, as it should be"
            lines += [
                f"### {row['sample']} — {verdict}",
                "",
                "```",
                row["text"].strip() or "(empty)",
                "```",
                "",
            ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--n-predict", type=int, default=700)
    parser.add_argument("--tokenizer", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--output", default="test_results/defect_probe")
    parser.add_argument(
        "--rescore", default=None,
        help="Re-apply scoring to a saved results JSON instead of generating again.",
    )
    args = parser.parse_args()

    # Scoring rules need tuning against real output, and regenerating to test a
    # rule change both costs half an hour and lets the goalposts move unnoticed.
    # Replaying fixes the text while the judgement is revised.
    if args.rescore:
        saved = json.loads(Path(args.rescore).read_text(encoding="utf-8"))
        by_name = {s["name"]: s for s in SAMPLES}
        rows, totals = [], {}
        for row in saved["rows"]:
            if row["kind"] == "buggy":
                row = {**row, **score(row["text"], by_name[row["sample"]])}
            else:
                row = {**row, "invented": bool(_ALLEGATION.search(row["text"]))}
            rows.append(row)
        for phrasing in PHRASINGS:
            mine = [r for r in rows if r["phrasing"] == phrasing]
            buggy = [r for r in mine if r["kind"] == "buggy"]
            totals[phrasing] = {
                "found": sum(r["found"] for r in buggy),
                "of": sum(r["of"] for r in buggy),
                "false_claims": sum(int(r["false_claim"]) for r in buggy),
                "invented": sum(int(r["invented"]) for r in mine if r["kind"] == "clean"),
                "anchors_proposed": sum(r["anchors_proposed"] for r in mine),
                "anchors_kept": sum(r["anchors_kept"] for r in mine),
            }
        out = Path(args.output)
        out.with_suffix(".json").write_text(
            json.dumps({"rows": rows, "totals": totals}, indent=2), encoding="utf-8"
        )
        write_report(rows, totals, out.with_suffix(".md"))
        print(f"rescored {len(rows)} saved generations\n")
        print(f"{'phrasing':<18} {'named':>8} {'false':>7} {'invented':>9} {'anchors':>10}")
        for name in PHRASINGS:
            t = totals[name]
            print(
                f"{name:<18} {t['found']:>3}/{t['of']:<4} {t['false_claims']:>7} "
                f"{t['invented']:>9} {t['anchors_kept']:>4}/{t['anchors_proposed']:<5}"
            )
        return

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    process = None
    if already_serving(args.port):
        print(f"using the llama-server already on port {args.port}")
    else:
        print(f"starting llama-server on port {args.port}")
        process = subprocess.Popen(
            ["llama-server", "-m", args.gguf, "--port", str(args.port),
             "-c", "4096", "-t", "8", "--no-warmup"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        wait_for_server(args.port)

    rows: list[dict[str, Any]] = []
    totals: dict[str, Any] = {}
    try:
        for phrasing, extra in PHRASINGS.items():
            print(f"\n{'=' * 72}\n{phrasing}\n{'=' * 72}")
            tally = {
                "found": 0, "of": 0, "false_claims": 0, "invented": 0,
                "anchors_proposed": 0, "anchors_kept": 0,
            }

            for sample in SAMPLES:
                result = run_one(args.port, sample["code"], extra, args.n_predict, tokenizer)
                marks = score(result["text"], sample)
                tally["found"] += marks["found"]
                tally["of"] += marks["of"]
                tally["false_claims"] += int(marks["false_claim"])
                tally["anchors_proposed"] += result["anchors_proposed"]
                tally["anchors_kept"] += result["anchors_kept"]
                flag = "  <- FALSE" if marks["false_claim"] else ""
                print(f"  {sample['name']:<28} {marks['found']}/{marks['of']}{flag}")
                rows.append({
                    "phrasing": phrasing, "kind": "buggy", "sample": sample["name"],
                    **marks, **result,
                })

            for sample in CLEAN_SAMPLES:
                result = run_one(args.port, sample["code"], extra, args.n_predict, tokenizer)
                invented = bool(_ALLEGATION.search(result["text"]))
                tally["invented"] += int(invented)
                tally["anchors_proposed"] += result["anchors_proposed"]
                tally["anchors_kept"] += result["anchors_kept"]
                print(f"  {sample['name']:<28} {'INVENTED A DEFECT' if invented else 'clean'}")
                rows.append({
                    "phrasing": phrasing, "kind": "clean", "sample": sample["name"],
                    "invented": invented, **result,
                })

            totals[phrasing] = tally
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=30)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(
        json.dumps({"rows": rows, "totals": totals}, indent=2), encoding="utf-8"
    )
    write_report(rows, totals, out.with_suffix(".md"))

    print(f"\n{'=' * 72}")
    header = f"{'phrasing':<18} {'named':>8} {'false':>7} {'invented':>9} {'anchors':>10}"
    print(header)
    for name in PHRASINGS:
        t = totals[name]
        print(
            f"{name:<18} {t['found']:>3}/{t['of']:<4} {t['false_claims']:>7} "
            f"{t['invented']:>9} {t['anchors_kept']:>4}/{t['anchors_proposed']:<5}"
        )
    print("\nA phrasing wins by cutting `false` without raising `invented`.")
    print("If none does, the capability is not there and the dataset is the answer.")
    print(f"\nwrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
