"""Does the comment survive when every name is `a`, `x`, `n`?

Six programs whose behaviour is not in dispute, each shown three ways:

    original     the names their author would write
    terse        every identifier and the function name replaced by a, b, x, n...
    noise        replaced by unrelated words

Only identifiers change; the structure is byte-for-byte the same. So any drop is
name-reading, not difficulty. Each program declares what a correct comment has
to say, and the sentence that scored is printed beside the score.
"""
from __future__ import annotations
import json
import random
import re
import sys
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from transformers import AutoTokenizer
from qwen_cpp_review.prompt import format_prompt_without_response
from qwen_cpp_review.obfuscation import obfuscate

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
ADAPTER = "models/27aug01/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter"
TOK = AutoTokenizer.from_pretrained(ADAPTER, trust_remote_code=True)

PROGRAMS = [
    ("sum_even",
     "int sumEven(const std::vector<int>& values) {\n"
     "    int total = 0;\n"
     "    for (int value : values) {\n"
     "        if (value % 2 == 0) {\n"
     "            total += value;\n"
     "        }\n"
     "    }\n"
     "    return total;\n"
     "}",
     re.compile(r"\b(sum|total|add\w*|accumulat\w*)\b", re.I),
     re.compile(r"\beven\b", re.I),
     "adds up the even elements"),

    ("largest",
     "int largest(const std::vector<int>& values) {\n"
     "    int best = values[0];\n"
     "    for (std::size_t i = 1; i < values.size(); ++i) {\n"
     "        if (values[i] > best) {\n"
     "            best = values[i];\n"
     "        }\n"
     "    }\n"
     "    return best;\n"
     "}",
     re.compile(r"\b(max\w*|largest|greatest|biggest|highest)\b", re.I),
     re.compile(r"\b(loop|iterat\w*|scan\w*|travers\w*)\b", re.I),
     "returns the maximum"),

    ("count_positive",
     "int countPositive(const std::vector<int>& values) {\n"
     "    int hits = 0;\n"
     "    for (int value : values) {\n"
     "        if (value > 0) {\n"
     "            ++hits;\n"
     "        }\n"
     "    }\n"
     "    return hits;\n"
     "}",
     re.compile(r"\b(count\w*|number of|how many|tally)\b", re.I),
     re.compile(r"\b(positive|greater than (?:0|zero)|> ?0)\b", re.I),
     "counts elements greater than zero"),

    ("reverse_string",
     "void reverseString(std::string& text) {\n"
     "    std::size_t left = 0;\n"
     "    std::size_t right = text.size() - 1;\n"
     "    while (left < right) {\n"
     "        std::swap(text[left], text[right]);\n"
     "        ++left;\n"
     "        --right;\n"
     "    }\n"
     "}",
     re.compile(r"\b(revers\w*|swap\w*)\b", re.I),
     re.compile(r"\b(two[- ]pointer|from both ends|opposite ends|left and right|"
                r"toward\w* (?:the )?(?:middle|centre|center)|meet)\b", re.I),
     "reverses in place with two pointers"),

    ("binary_search",
     "int binarySearch(const std::vector<int>& values, int target) {\n"
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
     re.compile(r"\b(binary search|halv\w*|half|midpoint|middle)\b", re.I),
     re.compile(r"\b(sorted|order\w*)\b", re.I),
     "binary search; requires sorted input"),

    ("factorial",
     "long factorial(int number) {\n"
     "    if (number <= 1) {\n"
     "        return 1;\n"
     "    }\n"
     "    return number * factorial(number - 1);\n"
     "}",
     re.compile(r"\b(factorial|recurs\w*)\b", re.I),
     re.compile(r"\b(base case|terminat\w*|stop\w*)\b", re.I),
     "recursive factorial with a base case"),
]

def ask(code):
    prompt = format_prompt_without_response(
        code, ["line_comments"], style="chat", tokenizer=TOK, task="line_comments")
    body = json.dumps({"prompt": prompt, "n_predict": 800,
                       "temperature": 0, "cache_prompt": False}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        text = json.load(r)["content"]
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text

rows = []
for strategy in ("original", "terse", "noise"):
    print(f"\n{'#'*78}\n# {strategy}\n{'#'*78}", flush=True)
    for name, code, core_re, detail_re, truth in PROGRAMS:
        shown = code if strategy == "original" else obfuscate(code, strategy, random.Random(7))
        parsed, raw = ask(shown)
        anchors = (parsed or {}).get("line_comments") or []
        blob = " ".join((a.get("comment") or "") for a in anchors)
        core = bool(core_re.search(blob))
        detail = bool(detail_re.search(blob))
        # every anchor must quote a line that is actually in the file
        lines = {line.strip() for line in shown.split("\n")}
        bad = [a for a in anchors if (a.get("code") or "").strip() not in lines]
        rows.append({"program": name, "strategy": strategy, "json_ok": parsed is not None,
                     "core": core, "detail": detail, "anchors": len(anchors),
                     "unquotable": len(bad), "truth": truth,
                     "code_shown": shown,
                     "comments": [{"code": (a.get('code') or '').strip(),
                                   "comment": a.get('comment')} for a in anchors]})
        flag = "ok " if (core and detail) else ("PART" if core else "MISS")
        print(f"\n  [{flag}] {name:<16} json {'y' if parsed else 'N'}  "
              f"anchors {len(anchors)}  bad-quote {len(bad)}   truth: {truth}")
        if strategy != "original":
            print(f"        shown as: {shown.splitlines()[0]}")
        for a in anchors[:9]:
            print(f"          {(a.get('code') or '').strip()[:36]:<36} -> {a.get('comment')}")

print(f"\n{'='*78}\nSCORES  (n=6 programs per row)\n{'='*78}")
print(f"{'naming':<10} {'names the operation':>20} {'+ the detail':>14} "
      f"{'json':>6} {'anchors':>8} {'un-quotable':>12}")
for s in ("original", "terse", "noise"):
    r = [x for x in rows if x["strategy"] == s]
    print(f"{s:<10} {sum(x['core'] for x in r):>17}/6 {sum(x['detail'] for x in r):>11}/6 "
          f"{sum(x['json_ok'] for x in r):>4}/6 {sum(x['anchors'] for x in r):>8} "
          f"{sum(x['unquotable'] for x in r):>12}")
Path("/tmp/claude-1000/-home-usama-Downloads-saffi-fyp-fyp-training/"
     "35610843-d5fd-4636-a739-e08b0471bd46/scratchpad/name_probe.json"
     ).write_text(json.dumps(rows, indent=2), encoding="utf-8")
