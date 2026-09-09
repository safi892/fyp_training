"""Two questions about what the line comments actually say.

Q1  On a function whose whole body is `return a + b;`, does the comment explain
    the logic, or restate the signature?

Q2  On a variable declared early and used later to hold the result, does the
    comment on the *declaration line* mention that later role, or only the
    local fact that something was set to zero?

Q2 is the interesting one: it asks whether the comment is written with
knowledge of lines that come after it, which is dataflow, not description.
Both are scored on the declaration/return line only, and every comment is
printed so the score can be checked against the sentence that earned it.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from transformers import AutoTokenizer
from qwen_cpp_review.prompt import format_prompt_without_response

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8085

# ---- Q1: is the comment about the logic, or about the name? -----------------
Q1 = [
    ("add_plain", "int add(int a, int b) {\n    return a + b;\n}", 2),
    ("average_overflow_safe",
     "int average(int a, int b) {\n    return a + (b - a) / 2;\n}", 2),
    ("sum_of_squares",
     "int sumOfSquares(int a, int b) {\n    return a * a + b * b;\n}", 2),
    ("weighted",
     "double weighted(double a, double b) {\n    return 0.7 * a + 0.3 * b;\n}", 2),
]

# ---- Q2: declaration line, used for the result much later ------------------
Q2 = [
    ("accumulate_total",
     "int sumEven(const std::vector<int>& v) {\n"
     "    int total = 0;\n"
     "    for (int x : v) {\n"
     "        if (x % 2 == 0) {\n"
     "            total += x;\n"
     "        }\n"
     "    }\n"
     "    return total;\n"
     "}", 2),
    ("running_max",
     "int largest(const std::vector<int>& v) {\n"
     "    int best = v[0];\n"
     "    for (std::size_t i = 1; i < v.size(); ++i) {\n"
     "        if (v[i] > best) {\n"
     "            best = v[i];\n"
     "        }\n"
     "    }\n"
     "    return best;\n"
     "}", 2),
    ("build_string",
     "std::string join(const std::vector<std::string>& parts) {\n"
     "    std::string out;\n"
     "    for (const std::string& p : parts) {\n"
     "        out += p;\n"
     "        out += \",\";\n"
     "    }\n"
     "    return out;\n"
     "}", 2),
    ("count_matches",
     "int countPositive(const std::vector<int>& v) {\n"
     "    int hits = 0;\n"
     "    for (int x : v) {\n"
     "        if (x > 0) {\n"
     "            ++hits;\n"
     "        }\n"
     "    }\n"
     "    return hits;\n"
     "}", 2),
]

# A comment is forward-looking if it says what the variable is FOR, which can
# only come from lines below it. Words that merely restate the statement
# ("initialize", "declare", "set to zero") are not evidence of that.
FORWARD = re.compile(
    r"\b(accumulat\w*|running|store\w*|storing|hold\w*|track\w*|keep\w*|"
    r"result|total(?:s)?|sum|count(?:er)?|maximum|largest|final|"
    r"will be|to be returned|returned)\b", re.I)
LOCAL_ONLY = re.compile(
    r"\b(initiali[sz]\w*|declar\w*|defin\w*|set\w*\s+to|assign\w*)\b", re.I)
# Q1: does the comment name the operation performed, or only the function's job?
LOGIC = re.compile(r"[-+*/]|\bplus\b|\bmultipl\w*|\bsquar\w*|\bdivid\w*|"
                   r"\bmidpoint\b|\boverflow\b|\bweight\w*|\baverage\b|\bmean\b", re.I)


def ask(code: str) -> tuple[dict | None, str]:
    tok = AutoTokenizer.from_pretrained("models/27aug01/outputs/"
        "qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter", trust_remote_code=True)
    prompt = format_prompt_without_response(
        code, ["line_comments"], style="chat", tokenizer=tok, task="line_comments")
    body = json.dumps({"prompt": prompt, "n_predict": 700,
                       "temperature": 0, "cache_prompt": False}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        text = json.load(r)["content"]
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def run(cases, label, target_line):
    out = []
    print(f"\n{'='*78}\n{label}\n{'='*78}")
    for name, code, line in cases:
        parsed, raw = ask(code)
        anchors = (parsed or {}).get("line_comments") or []
        lines = code.split("\n")
        want = lines[line-1].strip()
        # match by the quoted text, not the line number - line numbers are wrong
        # ~75% of the time in this model and the quote is right ~100%
        hit = next((a for a in anchors
                    if (a.get("code") or "").strip() == want), None)
        rec = {"name": name, "json_ok": parsed is not None,
               "target": want, "comment": (hit or {}).get("comment"),
               "anchors": len(anchors),
               "all": [{"code": (a.get('code') or '').strip(),
                        "comment": a.get('comment')} for a in anchors]}
        out.append(rec)
        print(f"\n--- {name}   (json {'ok' if parsed else 'FAILED'}, {len(anchors)} anchors)")
        print(f"    line   : {want}")
        print(f"    comment: {rec['comment']!r}")
        for a in rec["all"]:
            if a["code"] != want:
                print(f"      other : {a['code'][:44]:<44} -> {a['comment']}")
    return out

q1 = run(Q1, "Q1  a function that just returns a + b", 2)
q2 = run(Q2, "Q2  a variable declared early, used for the result later", 2)

print(f"\n{'='*78}\nSCORES\n{'='*78}")
n = sum(1 for r in q1 if r["comment"] and LOGIC.search(r["comment"]))
print(f"Q1  comment names the actual operation : {n}/{len(q1)}")
forward = sum(1 for r in q2 if r["comment"] and FORWARD.search(r["comment"]))
local = sum(1 for r in q2 if r["comment"] and LOCAL_ONLY.search(r["comment"]))
both = sum(1 for r in q2 if r["comment"] and FORWARD.search(r["comment"])
                                          and LOCAL_ONLY.search(r["comment"]))
print(f"Q2  declaration comment says what it is FOR : {forward}/{len(q2)}")
print(f"Q2  declaration comment restates the statement : {local}/{len(q2)}")
print(f"Q2  says both (initialises X, to hold Y)       : {both}/{len(q2)}")
Path("/tmp/claude-1000/-home-usama-Downloads-saffi-fyp-fyp-training/"
     "35610843-d5fd-4636-a739-e08b0471bd46/scratchpad/comment_probe.json"
     ).write_text(json.dumps({"q1": q1, "q2": q2}, indent=2), encoding="utf-8")
