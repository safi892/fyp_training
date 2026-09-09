"""The control the first run needed.

`total`, `best`, `out`, `hits` all announce their own purpose. A comment saying
"accumulator for the sum" may be reading the identifier, not the lines below it.
So: strip the names to single letters, and then make them actively misleading -
a variable called `count` that holds a sum, one called `sum` that holds a count.
If the comment follows the name it is now wrong, and wrong in a way that is
checkable rather than arguable.
"""
from __future__ import annotations
import json, re, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from transformers import AutoTokenizer
from qwen_cpp_review.prompt import format_prompt_without_response

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
ADAPTER = ("models/27aug01/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter")
TOK = AutoTokenizer.from_pretrained(ADAPTER, trust_remote_code=True)

CASES = [
    # ---- names stripped to single letters: no help from the identifier ----
    ("A_neutral_name",
     "int f(const std::vector<int>& v) {\n"
     "    int q = 0;\n"
     "    for (int x : v) {\n"
     "        if (x % 2 == 0) {\n"
     "            q += x;\n"
     "        }\n"
     "    }\n"
     "    return q;\n"
     "}", "int q = 0;", "sums even values"),

    ("B_neutral_name_max",
     "int g(const std::vector<int>& v) {\n"
     "    int z = v[0];\n"
     "    for (std::size_t i = 1; i < v.size(); ++i) {\n"
     "        if (v[i] > z) {\n"
     "            z = v[i];\n"
     "        }\n"
     "    }\n"
     "    return z;\n"
     "}", "int z = v[0];", "holds the running maximum"),

    # ---- the name says COUNT, the code computes a SUM ----
    ("C_misleading_count_is_sum",
     "int process(const std::vector<int>& v) {\n"
     "    int count = 0;\n"
     "    for (int x : v) {\n"
     "        count += x;\n"
     "    }\n"
     "    return count;\n"
     "}", "int count = 0;", "adds values - it is a SUM, not a count"),

    # ---- the name says SUM, the code computes a COUNT ----
    ("D_misleading_sum_is_count",
     "int process(const std::vector<int>& v) {\n"
     "    int sum = 0;\n"
     "    for (int x : v) {\n"
     "        if (x > 10) {\n"
     "            sum += 1;\n"
     "        }\n"
     "    }\n"
     "    return sum;\n"
     "}", "int sum = 0;", "counts elements > 10 - it is a COUNT, not a sum"),

    # ---- declared far from use, and NOT the return value ----
    ("E_scratch_not_result",
     "int firstGap(const std::vector<int>& v) {\n"
     "    int prev = v[0];\n"
     "    int answer = -1;\n"
     "    for (std::size_t i = 1; i < v.size(); ++i) {\n"
     "        if (v[i] - prev > 1 && answer == -1) {\n"
     "            answer = prev + 1;\n"
     "        }\n"
     "        prev = v[i];\n"
     "    }\n"
     "    return answer;\n"
     "}", "int answer = -1;", "sentinel: -1 means 'no gap found'"),
]

SAYS_SUM   = re.compile(r"\b(sum|total|add(?:ing|s|ition)?|accumulat\w*)\b", re.I)
SAYS_COUNT = re.compile(r"\b(count\w*|number of|how many|tally|increment\w*)\b", re.I)

def ask(code):
    prompt = format_prompt_without_response(
        code, ["line_comments"], style="chat", tokenizer=TOK, task="line_comments")
    body = json.dumps({"prompt": prompt, "n_predict": 700,
                       "temperature": 0, "cache_prompt": False}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        text = json.load(r)["content"]
    try: return json.loads(text)
    except json.JSONDecodeError: return None

out = []
for name, code, target, truth in CASES:
    parsed = ask(code)
    anchors = (parsed or {}).get("line_comments") or []
    hit = next((a for a in anchors if (a.get("code") or "").strip() == target), None)
    c = (hit or {}).get("comment")
    print(f"\n--- {name}   ({'json ok' if parsed else 'JSON FAILED'}, {len(anchors)} anchors)")
    print(f"    line     : {target}")
    print(f"    truth    : {truth}")
    print(f"    comment  : {c!r}")
    if name.startswith("C"):
        print(f"    -> says sum {bool(c and SAYS_SUM.search(c))}   "
              f"says count {bool(c and SAYS_COUNT.search(c))}   (correct = sum)")
    if name.startswith("D"):
        print(f"    -> says sum {bool(c and SAYS_SUM.search(c))}   "
              f"says count {bool(c and SAYS_COUNT.search(c))}   (correct = count)")
    for a in anchors:
        if (a.get("code") or "").strip() != target:
            print(f"      other  : {(a.get('code') or '').strip()[:40]:<40} -> {a.get('comment')}")
    out.append({"name": name, "target": target, "truth": truth, "comment": c,
                "anchors": [{"code": (a.get('code') or '').strip(),
                             "comment": a.get('comment')} for a in anchors]})
Path("/tmp/claude-1000/-home-usama-Downloads-saffi-fyp-fyp-training/"
     "35610843-d5fd-4636-a739-e08b0471bd46/scratchpad/control_probe.json"
     ).write_text(json.dumps(out, indent=2), encoding="utf-8")
