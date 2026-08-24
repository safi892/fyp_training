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

Twenty samples, written for this evaluation rather than collected. Synthetic is
the right trade here: the ground truth is known exactly, because the defect was
placed deliberately, and the scoring can therefore be checked rather than
argued about. The cost is that these are not a sample of anything - they say
what the model does on twenty specific defects, not what it does on the defects
real submissions contain. Mined wrong-answer submissions would answer the
second question and cannot answer the first.

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
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qwen_cpp_review.line_anchoring import repair_anchors  # noqa: E402

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
            # "wrong" is deliberately absent: "swap them if they are in the
            # wrong order" is how a *correct* comparison is described, and
            # scoring it as a defect report credits the model for the phrase it
            # produces when it has noticed nothing.
            r"\bbug|incorrect|broken|does not (work|sort)|fails to|is not a( real)? swap",
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
            # Not a bare "skip": "erase the iterator position to skip it" means
            # "remove it", which is what the code intends, not the bug where
            # adjacent negatives are stepped over.
            r"skips? (over |an? )?(element|item|value|entry|negative)"
            r"|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent",
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
    {
        "name": "loop_bound_off_by_one",
        "trap": "<= size() reads one element past the end of the vector",
        "code": """int sumAll(const std::vector<int>& values) {
    int total = 0;
    for (std::size_t i = 0; i <= values.size(); ++i)
        total += values[i];
    return total;
}""",
        "finds": [
            r"out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)",
            r"off.?by.?one|one (too many|extra|past)",
            r"undefined behavi|\bUB\b|crash",
        ],
        "false_claim": r"sums? (all|every|each|the) (element|value|item)",
    },
    {
        "name": "assignment_in_condition",
        "trap": "= instead of ==; assigns, then tests the assigned value",
        "code": """bool isTarget(int value, int target) {
    if (value = target)
        return true;
    return false;
}""",
        "finds": [
            r"assign(s|ment|ing|ed)?\b",
            r"always (true|returns true|be true)|never (returns? )?false",
            r"modif|overwrit|changes the",
        ],
        "false_claim": r"compares?|checks? (whether|if|that)|returns? true (if|when)",
    },
    {
        "name": "switch_fallthrough",
        "trap": "no break statements, so every case falls into default",
        "code": """int scoreOf(char grade) {
    int points = 0;
    switch (grade) {
        case 'A': points = 4;
        case 'B': points = 3;
        case 'C': points = 2;
        default: points = 0;
    }
    return points;
}""",
        "finds": [
            r"fall(s|ing)?[ -]?through|fallthrough",
            r"\bbreak\b",
            r"always (return|be|yield|give)s?.{0,12}(0|zero)",
        ],
        "false_claim": r"(returns?|maps?|converts?|gives?) .{0,25}(grade|letter)",
    },
    {
        "name": "accumulated_float_equality",
        "trap": "compares an accumulated double for exact equality",
        "code": """bool reachesOne(double step, int steps) {
    double running = 0.0;
    for (int i = 0; i < steps; ++i)
        running += step;
    return running == 1.0;
}""",
        "finds": [
            r"floating.?point|rounding|precision|epsilon",
            # Not a bare "exactly": "eventually reaches exactly 1.0" is how the
            # model describes the code working, so the word marks the claim it
            # is making rather than a doubt about it.
            r"never (be )?(exactly )?equal|will not be exact|rarely|almost never|cannot be represented",
            r"toleran|approximat",
        ],
        "false_claim": r"returns? true (if|when|once) .{0,30}(reach|equal|sum|total)",
    },
    {
        "name": "sizeof_on_decayed_array",
        "trap": "an array parameter is a pointer, so sizeof measures the pointer",
        "code": """int countItems(int arr[]) {
    return sizeof(arr) / sizeof(arr[0]);
}""",
        "finds": [
            # "decay" is the concept; a bare "pointer" is not. The model wrote
            # "the size of the pointer itself is multiplied by the element
            # size" and concluded the function returns the element count - the
            # word was present and the understanding was not.
            r"decay",
            r"always (return|be|give)s?.{0,10}(2|the same)|not the (number|count|length)",
            r"(size|length) is (lost|not known|unavailable)|cannot (determine|know)",
        ],
        "false_claim": r"(returns?|counts?|computes?|calculates?) the (number|count|size|length)",
    },
    {
        "name": "leak_on_early_return",
        "trap": "the early return skips the delete[]",
        "code": """int totalUnder(const std::vector<int>& values, int limit) {
    int* seen = new int[values.size()]();
    int sum = 0;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (values[i] > limit)
            return -1;
        sum += values[i];
    }
    delete[] seen;
    return sum;
}""",
        "finds": [
            r"leak",
            # Not a bare "delete": the code contains `delete[] seen;`, so a
            # model echoing the line it is describing would score a point for
            # noticing nothing.
            r"early return|returns? early|not reached|never (deleted|freed|reached)|skips? the",
        ],
        "false_claim": r"(cleans? up|releases?|frees?|deallocates?|deletes?) the (memory|allocation|buffer|array)",
    },
    {
        "name": "recursion_without_base_case",
        "trap": "nothing stops the recursion; it runs until the stack is exhausted",
        "code": """int countDown(int n) {
    return n + countDown(n - 1);
}""",
        "finds": [
            r"base case|termination|terminat|stop(ping)? condition",
            r"infinite|never (end|stop)|forever|unbounded",
            r"stack overflow|exhaust|crash",
        ],
        "false_claim": r"(sums?|adds?|returns? the sum of) .{0,25}(integer|number|value|from|down)",
    },
    {
        "name": "grow_during_range_for",
        "trap": "push_back inside a range-for invalidates the iterators it is using",
        "code": """void duplicate(std::vector<int>& values) {
    for (int value : values)
        values.push_back(value);
}""",
        "finds": [
            r"invalidat",
            r"undefined behavi|\bUB\b",
            r"infinite|grow(s|ing)? (forever|without)|reallocat|never (end|terminat)",
        ],
        "false_claim": r"(duplicates?|doubles?|appends?|copies) (each|every|the|a copy)",
    },
    {
        "name": "integer_division_before_widening",
        "trap": "both operands are int, so the fraction is gone before the double is made",
        "code": """double meanOf(int total, int count) {
    return total / count;
}""",
        "finds": [
            r"integer division|truncat|discard|drops? the (fraction|decimal|remainder)",
            r"cast|static_cast|convert|widen",
        ],
        "false_claim": r"(returns?|computes?|calculates?|gives?) the (mean|average|ratio)",
    },
    {
        "name": "operator_precedence",
        "trap": "== binds tighter than &, so the mask is compared, not applied",
        "code": """bool hasFlag(int flags, int mask) {
    return flags & mask == mask;
}""",
        "finds": [
            r"precedence|parenthes|binds? (more )?tight|evaluat.{0,25}(first|before)",
            r"(lowest|first|least significant) bit|always|\b& 1\b",
        ],
        "false_claim": r"(tests?|checks?|returns? (true )?(if|whether)) .{0,30}(flag|bit|mask)",
    },
    {
        "name": "xor_swap_same_index",
        "trap": "an xor swap zeroes the element when both indices are the same",
        "code": """void swapAt(int data[], int i, int j) {
    data[i] ^= data[j];
    data[j] ^= data[i];
    data[i] ^= data[j];
}""",
        "finds": [
            r"same (index|position|element)|identical indices|\bi == j\b|self",
            r"zero(ed|es|s)?|destroy|lose|lost|wipe",
            r"guard|check|special case",
        ],
        "false_claim": r"swaps? (the )?(two )?(element|value|item|entr)",
    },
    {
        "name": "index_past_last_character",
        "trap": "index size() is the terminator; the last character is at size() - 1",
        "code": """char lastChar(const std::string& text) {
    return text[text.size()];
}""",
        "finds": [
            r"null|terminator|'\\\\0'",
            r"size\(\) ?- ?1|one past|off.?by.?one|last .{0,15}is at",
        ],
        "false_claim": r"returns? the last (character|char|letter)",
    },
]

def count_anchor_repairs(code: str, comments_raw: str) -> dict[str, int]:
    """Split anchor validity into what the model got right and what was rescued.

    ``repair_anchors`` relocates an anchor by its quoted text, so anchor validity
    measured after it runs is ~100% whatever the model's line numbers do. That
    total is the right number to serve, and the wrong number to track a model
    with: phase 1 placed 26 of 77 anchors unaided and phase 2 only 6 of 72, a 4x
    regression that never moved the reported figure. Keeping ``exact`` separate
    is what makes that visible.
    """
    try:
        anchors = (json.loads(comments_raw) or {}).get("line_comments") or []
    except (json.JSONDecodeError, AttributeError):
        return {"anchors_exact": 0, "anchors_repaired": 0, "anchors_dropped": 0}

    report = repair_anchors(code, [a for a in anchors if isinstance(a, dict)])
    return {
        "anchors_exact": report.exact,
        "anchors_repaired": report.repaired,
        "anchors_dropped": report.dropped,
    }


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


#: Typographic characters the model emits where a keyboard would give ASCII.
#: It writes "fall‑through" with a non-breaking hyphen, "in‑place" likewise, and
#: uses a non-breaking space before units. Left alone, a pattern written the
#: obvious way silently fails to match, and the model loses a point it earned -
#: the same class of error as the flattering matches, pointing the other way.
_TYPOGRAPHY = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
    "―": "-", "−": "-", " ": " ", "’": "'", "“": '"',
    "”": '"',
})


def normalise(text: str) -> str:
    """Fold typographic punctuation to ASCII so patterns match what was meant."""
    return text.translate(_TYPOGRAPHY)


#: Phrases that say the named problem does *not* happen here. The model reaches
#: for them constantly: "compute midpoint to avoid overflow" on an unguarded
#: `(low + high) / 2`, "the extra element is intentionally ignored to avoid
#: out-of-bounds access" on a loop that runs off the end. Both name the defect
#: and deny it in one breath, and a plain keyword search reads the naming and
#: misses the denial.
#:
#: Deliberately narrow. "does not check for overflow" is a real catch and
#: contains "not", so bare negations are excluded and only phrases meaning
#: "this is handled" are listed.
_DENIAL = re.compile(
    r"(avoid|prevent|guard(s|ing)? against|protect(s|ing)? against|no risk of"
    r"|safe from|is safe|correctly handles?|properly handles?|intentionally"
    r"|ensures? no|without any)\W*$",
    re.I,
)


def _find_outside_a_denial(pattern: str, text: str) -> re.Match[str] | None:
    """Find ``pattern``, ignoring occurrences that sit inside a denial.

    Naming a problem while asserting it does not arise is not noticing it. The
    search continues past such a match rather than stopping, so a later honest
    mention still scores.
    """
    for match in re.finditer(pattern, text, re.I):
        preceding = text[max(0, match.start() - 30) : match.start()]
        if not _DENIAL.search(preceding):
            return match
    return None


def score(text: str, sample: dict[str, Any]) -> dict[str, Any]:
    """Count concepts named, and whether a false assertion was made.

    False assertions are located first and cut out of the text before concepts
    are counted. Without that, a concept word sitting *inside* the falsehood
    scores as if the model had found the problem: told that ``(low + high) / 2``
    is a binary search, the model wrote "compute midpoint to avoid overflow",
    which contains the word this sample scores on and asserts the opposite of
    the truth. Cutting the span first means a concept only counts when it is
    named somewhere the model was not busy being wrong — and a genuine "attempts
    to swap, but the value is lost" still counts, because the concept survives
    outside the excised phrase.
    """
    lowered = normalise(text).lower()
    asserted = bool(re.search(sample["false_claim"], lowered, re.I))
    remainder = re.sub(sample["false_claim"], " ", lowered, flags=re.I)

    matches = [_find_outside_a_denial(group, remainder) for group in sample["finds"]]
    hits = [match is not None for match in matches]
    # Every awarded point carries the phrase that earned it. Three times now a
    # single common word has scored where the model had understood nothing -
    # "overflow" inside "to avoid overflow", "exactly" inside "reaches exactly
    # 1.0", "pointer" inside a confident description of the wrong computation.
    # A score that cannot be audited gets believed, so the evidence ships with it.
    return {
        "found": sum(hits),
        "of": len(hits),
        "missed": [g for g, hit in zip(sample["finds"], hits) if not hit],
        "evidence": [
            remainder[max(0, m.start() - 60) : m.end() + 40].strip().replace("\n", " ")
            for m in matches
            if m is not None
        ],
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
        if record.get("evidence"):
            lines += ["Scored on:", ""]
            lines += [f"- …{phrase}…" for phrase in record["evidence"]]
            lines += [""]
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
            anchor_counts = count_anchor_repairs(sample["code"], outputs["line_comments"])
            result = score(text, sample)
            flag = "  <- ASSERTED SOMETHING FALSE" if result["false_claim"] else ""
            print(f"    found {result['found']}/{result['of']}"
                  f"{'' if parsed == 2 else f'  (JSON ok on {parsed}/2)'}{flag}")
            records.append(
                {**sample, **result, "text": text, "json_ok": parsed == 2,
                 **anchor_counts, "raw": outputs}
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
    exact = sum(r["anchors_exact"] for r in records)
    repaired = sum(r["anchors_repaired"] for r in records)
    dropped = sum(r["anchors_dropped"] for r in records)
    print(f"\n{'=' * 72}")
    print(f"problems named            : {found}/{total}")
    print(f"confidently false answers : {claims}/{len(records)}")
    # Reported apart from the post-repair total on purpose. Anchor validity is
    # measured after repair_anchors relocates by quoted text, so a model whose
    # line numbers are all wrong still scores 100% - which hid a 4x regression
    # between phase 1 (26/77 exact) and phase 2 (6/72). See
    # docs/PHASE2_INVESTIGATION.md, issue 1.
    print(f"anchors exact / repaired  : {exact}/{exact + repaired}"
          f" ({exact / max(exact + repaired, 1):.0%} landed on the right line unaided)")
    print(f"anchors dropped           : {dropped}")
    print(f"\nwrote {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
