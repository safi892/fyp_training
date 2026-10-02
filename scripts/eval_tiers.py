"""Comments and explanations on easy and medium code, which no harness covered.

`eval_hard.py` runs twenty programs that are 3-11 lines and each hide a trap, so
it measures defect finding. `annotate_seed.py` runs 45-58 line tree and graph
programs, so it measures the out-of-distribution end. Between them sat the case
the product actually serves most of the time: ordinary correct code, in the
length band the corpus is made of (p50 14, p90 37), where the only question is
whether the description is true.

That gap matters for a model comparison. A bigger model can look better on traps
while getting worse at plain description, and nothing here would have seen it.

Scoring reuses the audited pieces rather than adding a ninth way to be wrong:

    repair_anchors      exact / repaired / dropped, reported separately because
                        a post-repair number cannot see the model degrade
    check_claims        prose the source refutes (false recursion, complexity)

On top of those, each sample names the concepts a correct description has to
contain, and **every awarded point ships the phrase that earned it**, so a
human can audit the score. `must_not` is the sample-specific falsehood: a claim
that is not merely missing but wrong, which is worse than saying nothing.

    uv run python scripts/eval_tiers.py --gguf models/gguf/<model>.gguf --port 8090
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qwen_cpp_review.claim_checks import check_claims  # noqa: E402
from qwen_cpp_review.line_anchoring import repair_anchors  # noqa: E402
from qwen_cpp_review.prompt import format_prompt_without_response  # noqa: E402

#: `finds` is what a true description must say; `must_not` is the specific thing
#: it must not say. Neither is a keyword list for its own sake - each entry was
#: written from the code beside it, and the alternatives inside a group are
#: synonyms, not extra chances to score.
#:
#: `gcd` and `fibonacci` are deliberately absent: both appear verbatim in
#: `test_results/distilled.jsonl`, so a sample built on either measures recall
#: of the training data rather than understanding of the input.
EASY: list[dict[str, Any]] = [
    {
        "name": "sum_array",
        "code": "int sumArray(const std::vector<int>& values) {\n"
                "    int total = 0;\n"
                "    for (int value : values) {\n"
                "        total += value;\n"
                "    }\n"
                "    return total;\n"
                "}",
        "finds": [r"sum|total|add(?:s|ing)?|accumulat\w+", r"loop|iterat\w+|each element|every element"],
        "must_not": r"recursiv\w+|calls itself|sorts|multiplies",
    },
    {
        "name": "max_of_three",
        "code": "int maxOfThree(int a, int b, int c) {\n"
                "    int best = a;\n"
                "    if (b > best) best = b;\n"
                "    if (c > best) best = c;\n"
                "    return best;\n"
                "}",
        "finds": [r"max\w*|largest|greatest|biggest|highest", r"compar\w+|greater than|larger than"],
        "must_not": r"recursiv\w+|smallest|minimum|sorts",
    },
    {
        "name": "count_vowels",
        "code": "int countVowels(const std::string& text) {\n"
                "    int count = 0;\n"
                "    for (char c : text) {\n"
                "        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {\n"
                "            ++count;\n"
                "        }\n"
                "    }\n"
                "    return count;\n"
                "}",
        "finds": [r"vowel", r"count\w*|number of|how many|tally"],
        # It only handles lower case; saying it is case-insensitive is wrong.
        "must_not": r"case[- ]insensitiv\w+|upper\s*case|ignores case|both cases",
    },
    {
        "name": "swap_values",
        "code": "void swapValues(int& a, int& b) {\n"
                "    int temp = a;\n"
                "    a = b;\n"
                "    b = temp;\n"
                "}",
        "finds": [r"swap\w*|exchang\w+|interchang\w+", r"temp\w*|third variable|temporary"],
        "must_not": r"recursiv\w+|xor|without a temp|returns",
    },
    {
        "name": "square_all",
        "code": "void squareAll(std::vector<int>& values) {\n"
                "    for (std::size_t i = 0; i < values.size(); ++i) {\n"
                "        values[i] = values[i] * values[i];\n"
                "    }\n"
                "}",
        "finds": [r"squar\w+|multiplied by itself|\* itself", r"in[- ]place|modif\w+|each element"],
        "must_not": r"returns a new|recursiv\w+|copy of the vector|cub\w+",
    },
    {
        "name": "is_divisible",
        "code": "bool isDivisible(int value, int divisor) {\n"
                "    return value % divisor == 0;\n"
                "}",
        "finds": [r"divisib\w+|modulo|remainder|evenly", r"true|false|bool"],
        # No zero check: claiming it is safe is the falsehood worth catching.
        "must_not": r"handles (?:a )?(?:zero|divisor of zero)|checks for zero|safe",
    },
]

MEDIUM: list[dict[str, Any]] = [
    {
        "name": "binary_search",
        "code": "int binarySearch(const std::vector<int>& values, int target) {\n"
                "    int low = 0;\n"
                "    int high = static_cast<int>(values.size()) - 1;\n"
                "    while (low <= high) {\n"
                "        int mid = low + (high - low) / 2;\n"
                "        if (values[mid] == target) {\n"
                "            return mid;\n"
                "        }\n"
                "        if (values[mid] < target) {\n"
                "            low = mid + 1;\n"
                "        } else {\n"
                "            high = mid - 1;\n"
                "        }\n"
                "    }\n"
                "    return -1;\n"
                "}",
        "finds": [r"binary search|halv\w+|half|midpoint|middle", r"(?<!un)sorted|in order|ordered", r"-1|not found|absent"],
        "must_not": r"recursiv\w+|linear search|unsorted|O\(n\)(?! ?log)",
    },
    {
        "name": "bubble_sort",
        "code": "void bubbleSort(std::vector<int>& values) {\n"
                "    for (std::size_t i = 0; i + 1 < values.size(); ++i) {\n"
                "        for (std::size_t j = 0; j + 1 < values.size() - i; ++j) {\n"
                "            if (values[j] > values[j + 1]) {\n"
                "                std::swap(values[j], values[j + 1]);\n"
                "            }\n"
                "        }\n"
                "    }\n"
                "}",
        "finds": [r"sort\w*", r"adjacent|neighbou?r|next element|pair", r"nested|two loops|quadratic|O\(n\^?2\)|O\(n²\)"],
        "must_not": r"recursiv\w+|O\(n ?log ?n\)|merge sort|quick ?sort|descending",
    },
    {
        "name": "is_palindrome",
        "code": "bool isPalindrome(const std::string& text) {\n"
                "    std::size_t left = 0;\n"
                "    std::size_t right = text.size() - 1;\n"
                "    while (left < right) {\n"
                "        if (text[left] != text[right]) {\n"
                "            return false;\n"
                "        }\n"
                "        ++left;\n"
                "        --right;\n"
                "    }\n"
                "    return true;\n"
                "}",
        "finds": [r"palindrome|same (?:forwards?|backwards?)|reads the same",
                  r"both ends|two[- ]pointer|left and right|toward\w* (?:the )?(?:middle|centre|center)"],
        # text.size() - 1 underflows on an empty string; claiming it is handled is wrong.
        "must_not": r"handles (?:the )?empty|empty string is handled|safe for empty",
    },
    {
        "name": "remove_duplicates",
        "code": "std::vector<int> removeDuplicates(const std::vector<int>& values) {\n"
                "    std::vector<int> out;\n"
                "    for (int value : values) {\n"
                "        bool seen = false;\n"
                "        for (int kept : out) {\n"
                "            if (kept == value) {\n"
                "                seen = true;\n"
                "                break;\n"
                "            }\n"
                "        }\n"
                "        if (!seen) {\n"
                "            out.push_back(value);\n"
                "        }\n"
                "    }\n"
                "    return out;\n"
                "}",
        "finds": [r"duplicat\w+|unique|repeat\w+", r"order|first occurrence|preserv\w+|as they appear",
                  r"nested|inner loop|quadratic|O\(n\^?2\)|O\(n²\)|for each"],
        "must_not": r"hash|unordered_set|sorts|O\(n ?log ?n\)|in[- ]place",
    },
    {
        "name": "matrix_row_sums",
        "code": "std::vector<int> rowSums(const std::vector<std::vector<int>>& grid) {\n"
                "    std::vector<int> sums;\n"
                "    for (const std::vector<int>& row : grid) {\n"
                "        int total = 0;\n"
                "        for (int cell : row) {\n"
                "            total += cell;\n"
                "        }\n"
                "        sums.push_back(total);\n"
                "    }\n"
                "    return sums;\n"
                "}",
        "finds": [r"row", r"sum|total|add\w*", r"each row|per row|every row"],
        "must_not": r"column|transpos\w+|recursiv\w+|single (?:int|value|number) is returned",
    },
    {
        "name": "merge_sorted",
        "code": "std::vector<int> mergeSorted(const std::vector<int>& a, const std::vector<int>& b) {\n"
                "    std::vector<int> out;\n"
                "    std::size_t i = 0;\n"
                "    std::size_t j = 0;\n"
                "    while (i < a.size() && j < b.size()) {\n"
                "        if (a[i] <= b[j]) {\n"
                "            out.push_back(a[i++]);\n"
                "        } else {\n"
                "            out.push_back(b[j++]);\n"
                "        }\n"
                "    }\n"
                "    while (i < a.size()) out.push_back(a[i++]);\n"
                "    while (j < b.size()) out.push_back(b[j++]);\n"
                "    return out;\n"
                "}",
        "finds": [r"merg\w+|combin\w+", r"(?<!un)sorted|in order|ordered", r"remain\w+|leftover|rest of|tail|trailing"],
        "must_not": r"recursiv\w+|sorts the (?:result|output)|removes duplicates|in[- ]place",
    },
]

TIERS = {"easy": EASY, "medium": MEDIUM}


def wait_for_server(port: int, timeout: float = 300.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
                if json.load(response).get("status") == "ok":
                    return
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
            pass
        time.sleep(2)
    raise RuntimeError("llama-server did not become ready")


def complete(port: int, prompt: str, n_predict: int) -> str:
    payload = json.dumps(
        {"prompt": prompt, "n_predict": n_predict, "temperature": 0, "cache_prompt": False}
    ).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=1800) as response:
        body = json.load(response)
    return body["content"], bool(body.get("stopped_limit"))


def parse(text: str) -> tuple[dict[str, Any] | None, str]:
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def score_sample(sample: dict[str, Any], comment_json: dict | None,
                 explanation_json: dict | None, prose: str) -> dict[str, Any]:
    """What the two answers said, with the phrase behind every point."""
    lowered = prose.lower()
    matches = [re.search(group, lowered, re.I) for group in sample["finds"]]
    wrong = re.search(sample["must_not"], lowered, re.I)

    anchors = (comment_json or {}).get("line_comments") or []
    report = repair_anchors(sample["code"], anchors) if anchors else None
    claims = check_claims(sample["code"], prose)

    return {
        "found": sum(1 for m in matches if m),
        "of": len(matches),
        "missed": [g for g, m in zip(sample["finds"], matches) if not m],
        # Every point ships the sentence that earned it: three times a common
        # word has scored where nothing had been understood.
        "evidence": [lowered[max(0, m.start() - 55): m.end() + 45].replace("\n", " ")
                     for m in matches if m],
        "said_something_false": bool(wrong),
        "false_phrase": lowered[max(0, wrong.start() - 55): wrong.end() + 45].replace("\n", " ") if wrong else None,
        "anchors_total": len(anchors),
        "anchors_exact": report.exact if report else 0,
        "anchors_repaired": report.repaired if report else 0,
        "anchors_dropped": report.dropped if report else 0,
        "claim_objections": [c.sentence for c in claims.contradictions],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-v3-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--n-predict", type=int, default=600)
    parser.add_argument("--tokenizer", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--label", default="model")
    parser.add_argument("--output", default="test_results/tiers")
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port),
         "-c", "4096", "-t", str(args.threads), "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records: list[dict[str, Any]] = []
    try:
        wait_for_server(args.port)
        for tier, samples in TIERS.items():
            print(f"\n{'=' * 70}\n{tier.upper()}\n{'=' * 70}", flush=True)
            for sample in samples:
                raw: dict[str, str] = {}
                truncated = False
                for task in ("line_comments", "explanation"):
                    prompt = format_prompt_without_response(
                        sample["code"], [], style="chat", tokenizer=tokenizer, task=task
                    )
                    text, cut = complete(args.port, prompt, args.n_predict)
                    raw[task] = text
                    truncated = truncated or cut
                comment_json, _ = parse(raw["line_comments"])
                explanation_json, _ = parse(raw["explanation"])
                prose = " ".join(
                    [str((explanation_json or {}).get("explanation") or raw["explanation"])]
                    + [str(a.get("comment") or "") for a in
                       ((comment_json or {}).get("line_comments") or [])]
                )
                result = score_sample(sample, comment_json, explanation_json, prose)
                json_ok = (comment_json is not None) + (explanation_json is not None)
                records.append({
                    "tier": tier, "name": sample["name"], "model": args.label,
                    "json_ok": json_ok, "truncated": truncated, **result, "raw": raw,
                })
                flag = "  <- SAID SOMETHING FALSE" if result["said_something_false"] else ""
                print(f"  {sample['name']:<20} said {result['found']}/{result['of']}"
                      f"  json {json_ok}/2  anchors {result['anchors_exact']}exact/"
                      f"{result['anchors_total']}{flag}", flush=True)
    finally:
        process.terminate()
        process.wait(timeout=30)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"\n{'=' * 70}\n{args.label}\n{'=' * 70}")
    for tier in TIERS:
        rows = [r for r in records if r["tier"] == tier]
        total = sum(r["of"] for r in rows)
        exact = sum(r["anchors_exact"] for r in rows)
        anchors = sum(r["anchors_total"] for r in rows)
        print(f"  {tier:<8} described {sum(r['found'] for r in rows)}/{total}"
              f"   said something false {sum(1 for r in rows if r['said_something_false'])}/{len(rows)}"
              f"   valid JSON {sum(r['json_ok'] for r in rows)}/{2 * len(rows)}"
              f"   anchors on the right line unaided {exact}/{anchors}")
    print(f"\nwrote {out.with_suffix('.json')}")


if __name__ == "__main__":
    main()
