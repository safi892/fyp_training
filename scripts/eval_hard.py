"""Test the model on code where the plausible answer is the wrong one.

Every earlier evaluation used code the model handles well: short, correct,
conventional functions of the kind the corpus is made of. Passing those shows
the output format holds. It does not show the model read the code, because on
correct conventional code, describing what the function is *named after* and
describing what it *does* give the same answer.

These samples separate the two. Each one looks like a familiar algorithm and
isn't: a bubble sort whose swap loses data, a binary search that overflows, a
loop that erases while iterating. A model matching patterns will produce a
confident, fluent, wrong description. A model reading the code will notice.

Scoring has two axes, and the second matters more:

- ``finds``      — did it name the real problem?
- ``claims``     — did it assert something false about the code?

A vague answer is survivable; a confidently wrong one is what reaches a user
and gets believed. Concepts are scored on words that never appear as
identifiers in the sample, so a point cannot be earned by echoing a name.

    uv run python scripts/eval_hard.py

Reuses a llama-server already listening on ``--port``; starts one otherwise.
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

#: Each sample pairs code with what a correct reading finds, and with the
#: specific false statement the code is designed to bait. ``finds`` groups are
#: alternatives - any one spelling counts, because the wording is the model's
#: choice and only the concept is being scored. ``false_claim`` fires only when
#: the model asserts the wrong thing *without* also naming the defect, so
#: "attempts to swap but loses a value" is not counted against it.
SAMPLES: list[dict[str, Any]] = [
    {
        "name": "broken_swap",
        "trap": "looks exactly like bubble sort; the swap has no temporary and destroys data",
        "code": """void sortValues(int data[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (data[j] > data[j + 1]) {
                data[j] = data[j + 1];
                data[j + 1] = data[j];
            }
        }
    }
}""",
        "finds": [
            r"overwrit|destroy|lose|lost|clobber|duplicat",
            r"no temporar|without a temporar|missing temporar|third variable",
            r"\bbug|incorrect|wrong|broken|does not (work|sort)|fails",
        ],
        "false_claim": r"\bswaps?\b|\bswapping\b|exchanges",
    },
    {
        "name": "overflow_mid",
        "trap": "textbook binary search, but (low + high) overflows on large inputs",
        "code": """int findValue(int arr[], int size, int target) {
    int low = 0, high = size - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}""",
        "finds": [r"overflow"],
        "false_claim": r"(avoid|prevent|safe|without|no risk of)\w*[^.]{0,30}overflow",
    },
    {
        "name": "erase_while_iterating",
        "trap": "erase() invalidates the iterator; the loop is undefined behaviour",
        "code": """void removeNegatives(std::vector<int>& values) {
    for (auto it = values.begin(); it != values.end(); ++it) {
        if (*it < 0)
            values.erase(it);
    }
}""",
        "finds": [
            r"invalidat",
            r"undefined behavi|\bUB\b",
            r"skip|miss|consecutive|adjacent",
        ],
        "false_claim": r"remove[s]? all|correctly remove|erases all",
    },
    {
        "name": "dangling_reference",
        "trap": "returns a reference to a local that dies at the closing brace",
        "code": """const std::string& describe(int code) {
    std::string result = "code: " + std::to_string(code);
    return result;
}""",
        "finds": [
            r"dangl",
            r"local|out of scope|goes out of|lifetime|destroy",
            r"undefined behavi|\bUB\b",
        ],
        "false_claim": r"returns? (a|the) reference to the (formatted|resulting|constructed|string)",
    },
    {
        "name": "self_shadowing_counter",
        "trap": "the inner declaration shadows the counter and reads itself uninitialised",
        "code": """int countMatches(const std::vector<int>& items, int wanted) {
    int found = 0;
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (items[i] == wanted) {
            int found = found + 1;
        }
    }
    return found;
}""",
        "finds": [
            r"shadow",
            r"uninitiali[sz]ed|indeterminate|itself",
            r"always (return|be|yield)|never (increment|updat|chang)|discarded|inner",
        ],
        "false_claim": r"count(s|ing)? (the )?(number of )?(match|occurrence|element)",
    },
    {
        "name": "unsigned_wraparound",
        "trap": "size() - 1 on an empty vector wraps to a huge value and reads out of bounds",
        "code": """bool isAscending(const std::vector<int>& series) {
    for (std::size_t i = 0; i < series.size() - 1; ++i) {
        if (series[i] > series[i + 1])
            return false;
    }
    return true;
}""",
        "finds": [
            r"empty",
            r"wrap|underflow|overflow|huge|enormous|SIZE_MAX|maximum value",
            r"out of (bounds|range)|out-of-bounds|past the end",
            r"unsigned",
        ],
        "false_claim": r"(handles|works|returns true).{0,25}empty",
    },
    {
        "name": "shallow_copy_double_free",
        "trap": "the copy constructor copies the pointer, so both objects delete it",
        "code": """class Buffer {
    int* data;
    std::size_t len;
public:
    Buffer(std::size_t n) : data(new int[n]), len(n) {}
    ~Buffer() { delete[] data; }
    Buffer(const Buffer& other) : data(other.data), len(other.len) {}
};""",
        "finds": [
            r"shallow",
            r"double (free|delete)|twice|same (memory|pointer|buffer|array)",
            r"deep copy|rule of (three|3|five|5)",
        ],
        "false_claim": r"cop(y|ies) (the )?(contents|elements|buffer|data) (of|from)",
    },
    {
        "name": "misleading_function_name",
        "trap": "named bubbleSort; actually sums the primes up to a limit",
        "code": """int bubbleSort(int limit) {
    int total = 0;
    for (int i = 2; i <= limit; i++) {
        bool flag = true;
        for (int j = 2; j * j <= i; j++)
            if (i % j == 0) { flag = false; break; }
        if (flag) total += i;
    }
    return total;
}""",
        "finds": [
            r"prime",
            r"\bsum|accumulat|adds up|running total",
            r"divisor|divisib|factor|modul",
        ],
        "false_claim": r"\bsort|\bbubble|ascending order|reorder",
    },
]

def harvest_text(comments_raw: str, explanation_raw: str) -> tuple[str, int]:
    """Flatten both answers into one string to score, however they parsed.

    A malformed answer is still scored on its text: refusing to score it would
    reward the failure mode of emitting prose instead of JSON.
    """
    parts: list[str] = []
    parsed = 0

    try:
        anchors = (json.loads(comments_raw) or {}).get("line_comments") or []
        parsed += 1
        parts += [
            str(a.get("comment") or "") for a in anchors if isinstance(a, dict)
        ]
    except (json.JSONDecodeError, AttributeError):
        parts.append(comments_raw)

    try:
        parts.append(str((json.loads(explanation_raw) or {}).get("explanation") or ""))
        parsed += 1
    except (json.JSONDecodeError, AttributeError):
        parts.append(explanation_raw)

    return "\n".join(parts), parsed


def score(text: str, sample: dict[str, Any]) -> dict[str, Any]:
    """Count concepts named, and whether a false assertion was made."""
    lowered = text.lower()
    hits = [bool(re.search(group, lowered, re.I)) for group in sample["finds"]]
    asserted = bool(re.search(sample["false_claim"], lowered, re.I))
    # A claim only counts as false when the defect went unmentioned: naming the
    # bug and then describing the intent is accurate, not misleading.
    return {
        "found": sum(hits),
        "of": len(hits),
        "missed": [g for g, hit in zip(sample["finds"], hits) if not hit],
        "false_claim": asserted and not any(hits),
    }


def already_serving(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
            return bool(json.load(response).get("status"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return False


def wait_for_server(port: int, timeout: float = 300.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if already_serving(port):
            return
        time.sleep(2)
    raise RuntimeError("llama-server did not become ready")


def complete(port: int, prompt: str, n_predict: int) -> str:
    payload = json.dumps(
        {"prompt": prompt, "n_predict": n_predict, "temperature": 0, "cache_prompt": False}
    ).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.load(response)["content"]


def write_report(records: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Hard-example evaluation",
        "",
        "Code where the plausible answer is the wrong one. Each sample resembles a",
        "familiar algorithm and behaves differently. **finds** is how many of the real",
        "problems were named; **false claim** means the model asserted the code does",
        "something it does not, without naming the defect.",
        "",
        "| sample | the trap | JSON | finds | false claim |",
        "| --- | --- | :---: | :---: | :---: |",
    ]
    for record in records:
        verdict = "**yes**" if record["false_claim"] else "no"
        lines.append(
            f"| `{record['name']}` | {record['trap']} | "
            f"{'ok' if record['json_ok'] else 'BAD'} | "
            f"{record['found']}/{record['of']} | {verdict} |"
        )

    found = sum(r["found"] for r in records)
    total = sum(r["of"] for r in records)
    claims = sum(1 for r in records if r["false_claim"])
    lines += [
        "",
        f"**{found}/{total} problems named** · "
        f"**{claims}/{len(records)} samples drew a confidently false description**",
        "",
        "---",
        "",
    ]
    for record in records:
        lines += [
            f"## {record['name']}",
            "",
            f"*{record['trap']}*",
            "",
            "```cpp",
            record["code"],
            "```",
            "",
            f"**Model output** — found {record['found']}/{record['of']}"
            + (", **asserted something false**" if record["false_claim"] else ""),
            "",
            "```",
            record["text"].strip() or "(empty)",
            "```",
            "",
        ]
        if record["missed"]:
            lines += ["Concepts not named: " + ", ".join(f"`{m}`" for m in record["missed"]), ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--n-predict", type=int, default=700)
    parser.add_argument("--tokenizer", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--output", default="test_results/hard_examples")
    parser.add_argument(
        "--rescore", default=None,
        help="Re-apply scoring to a saved results JSON instead of generating again.",
    )
    args = parser.parse_args()

    # Scoring regexes need tuning against real output, and re-running the model
    # to test a regex change would be both slow and a way to quietly move the
    # goalposts. Rescoring replays the saved generations instead, so the text
    # being judged is fixed while the judgement is revised.
    if args.rescore:
        saved = json.loads(Path(args.rescore).read_text(encoding="utf-8"))
        by_name = {s["name"]: s for s in SAMPLES}
        records = [{**r, **score(r["text"], by_name[r["name"]])} for r in saved]
        out = Path(args.output)
        out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")
        write_report(records, out.with_suffix(".md"))
        found = sum(r["found"] for r in records)
        total = sum(r["of"] for r in records)
        claims = sum(1 for r in records if r["false_claim"])
        print(f"rescored {len(records)} saved generations")
        print(f"problems named            : {found}/{total}")
        print(f"confidently false answers : {claims}/{len(records)}")
        return

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

    # One task per request, exactly as the mixture was trained and as
    # `compare_quantizations.py` measures. Asking for both fields at once is
    # off-distribution and collapses the JSON, which would be measuring the
    # prompt rather than the model.
    from transformers import AutoTokenizer

    from qwen_cpp_review.prompt import format_prompt_without_response

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    records = []
    try:
        for sample in SAMPLES:
            print(f"\n=== {sample['name']} ===")
            print(f"    trap: {sample['trap']}")
            outputs = {}
            for task in ("line_comments", "explanation"):
                prompt = format_prompt_without_response(
                    sample["code"], [], style="chat", tokenizer=tokenizer, task=task
                )
                outputs[task] = complete(args.port, prompt, args.n_predict)
            text, parsed = harvest_text(outputs["line_comments"], outputs["explanation"])
            result = score(text, sample)
            flag = "  <- ASSERTED SOMETHING FALSE" if result["false_claim"] else ""
            print(f"    found {result['found']}/{result['of']}"
                  f"{'' if parsed == 2 else f'  (JSON ok on {parsed}/2)'}{flag}")
            records.append(
                {**sample, **result, "text": text, "json_ok": parsed == 2,
                 "raw": outputs}
            )
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=30)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_report(records, out.with_suffix(".md"))

    found = sum(r["found"] for r in records)
    total = sum(r["of"] for r in records)
    claims = sum(1 for r in records if r["false_claim"])
    print(f"\n{'=' * 72}")
    print(f"problems named            : {found}/{total}")
    print(f"confidently false answers : {claims}/{len(records)}")
    print(f"\nwrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
