"""The gate has to reject a rewrite that is wrong, not merely one that looks odd."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from verify_optimization_pairs import check, load_pairs, recursive_functions  # noqa: E402

RECURSIVE = """\
#include <iostream>
long long fact(int n) { if (n <= 1) return 1; return n * fact(n - 1); }
int main() { std::cout << fact(10); return 0; }
"""

ITERATIVE = """\
#include <iostream>
long long fact(int n) { long long r = 1; for (int i = 2; i <= n; i++) r *= i; return r; }
int main() { std::cout << fact(10); return 0; }
"""

#: Same shape, wrong answer - starts the product at 0. Only running it catches this.
WRONG = ITERATIVE.replace("long long r = 1;", "long long r = 0;")


@pytest.fixture
def workdir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def test_finds_self_calls_including_lambdas():
    assert recursive_functions(RECURSIVE) == ["fact"]
    assert recursive_functions(ITERATIVE) == []
    lambda_code = "void f() { function<void(int)> go = [&](int i){ if (i) go(i - 1); }; go(3); }"
    assert "go" in recursive_functions(lambda_code)


def test_accepts_a_pair_that_agrees(workdir):
    assert check(RECURSIVE, ITERATIVE, workdir, timeout=10) is None


def test_rejects_a_rewrite_that_changes_the_answer(workdir):
    problem = check(RECURSIVE, WRONG, workdir, timeout=10)
    assert problem is not None and "different output" in problem


def test_rejects_a_rewrite_that_is_still_recursive(workdir):
    problem = check(RECURSIVE, RECURSIVE, workdir, timeout=10)
    assert problem is not None and "still recurses" in problem


def test_rejects_when_the_first_version_was_never_recursive(workdir):
    problem = check(ITERATIVE, ITERATIVE, workdir, timeout=10)
    assert problem is not None and "nothing to optimise" in problem


def test_rejects_code_that_cannot_be_run(workdir):
    headless = "class Solution { public: int f(int n) { return n ? f(n - 1) : 0; } };"
    problem = check(headless, "class Solution { public: int f(int n) { return 0; } };", workdir, 10)
    assert problem is not None and "no main" in problem


def test_reads_all_three_collected_formats(tmp_path):
    (tmp_path / "seed.jsonl").write_text(
        json.dumps({"code": "s", "improved_code": "t", "stdin": "5\n"}) + "\n", encoding="utf-8"
    )
    (tmp_path / "DATASET.json").write_text('[[{"code": "a"}, {"code": "b"}]]', encoding="utf-8")
    # The broken form: a string with no key, which no JSON parser accepts.
    (tmp_path / "dataset.jsonl").write_text('[\n {"c"},\n {"d"}\n]\n', encoding="utf-8")

    pairs = load_pairs(tmp_path)
    assert [(p["code"], p["improved_code"]) for p in pairs] == [("s", "t"), ("a", "b"), ("c", "d")]
    # Only the seed format records input; the older two have none to record.
    assert [p["stdin"] for p in pairs] == ["5\n", "", ""]


def test_comments_cannot_look_like_recursion():
    """`//S.C : O(26)` scans as a function `O(26){...}` whose body calls `O(n)`.

    Complexity notes are common in submitted code, so without stripping comments
    the corpus miner reported plain loops as recursive.
    """
    annotated = (
        "string repeat(string s) {\n"
        "    vector<int> count(26, 0); //S.C : O(26)\n"
        "    for (char &ch : s) { //T.C : O(n)\n"
        "        count[ch - 'a']++;\n"
        "    }\n"
        "    return s;\n"
        "}"
    )
    assert recursive_functions(annotated) == []


def test_a_comment_naming_the_function_is_not_a_call():
    code = "int walk(int n) {\n    // walk(n - 1) would recurse here\n    return n;\n}"
    assert recursive_functions(code) == []


# --- the verified-dataset builder ------------------------------------------

def test_the_builder_keeps_only_rewrites_that_run_and_agree():
    """The gate is the whole design: generation is untrusted, execution decides.

    Written against the builder rather than the script that produced the seed
    set, because this is the one that will write hundreds of rows unattended.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import judge

    rec = "int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }"
    itr = "int fact(int n){ int r=1; for(int i=2;i<=n;i++) r*=i; return r; }"

    assert judge(rec, itr, 10.0) is None
    assert judge(rec, itr.replace("r=1", "r=0"), 10.0) == "different output"
    assert judge(rec, rec, 10.0) == "still recursive"
    assert judge(rec, "", 10.0) == "empty"


def test_the_builder_reads_the_wording_it_will_be_served_with():
    """A dataset built with one instruction and served with another teaches drift."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import TASK, build_prompt

    from qwen_cpp_review.prompt import TASK_FIELD_HINTS

    for task in ("optimize", "iterate"):
        assert TASK_FIELD_HINTS[task]["improved_code"] in build_prompt("int f();", task)
    assert TASK in TASK_FIELD_HINTS


def test_the_extractor_finds_code_however_the_model_wrapped_it():
    """The base model emits 0/20 usable JSON, so insisting on JSON rejects it all.

    Format compliance is not what a proposer is for. The gate decides whether the
    code is right; this only has to find the code.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import extract_candidate

    assert extract_candidate('{"improved_code": "int f(){return 1;}"}') == "int f(){return 1;}"
    assert "return 2" in extract_candidate('Sure!\n{"improved_code": "int f(){return 2;}"}\nDone.')
    assert "int r=1" in extract_candidate("Here:\n```cpp\nint f(){ int r=1; return r; }\n```")

    # A reply that fences the original before the rewrite: the rewrite is longer.
    both = ("Original:\n```cpp\nint f(){return f();}\n```\n"
            "Rewritten:\n```cpp\nint f(){ int r=0; for(int i=0;i<3;i++) r+=i; return r; }\n```")
    assert "for" in extract_candidate(both)

    assert extract_candidate("I would suggest an explicit stack.") == ""
    assert extract_candidate("") == ""
