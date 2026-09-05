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


def test_verified_rows_are_labeled_with_the_routed_task(tmp_path, workdir):
    from verify_optimization_pairs import main

    (tmp_path / "DATASET.json").write_text(
        json.dumps(
            [[
                {"code": "int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }"},
                {"code": "int fact(int n){ int r=1; for(int i=2;i<=n;i++) r*=i; return r; }"},
            ]]
        ),
        encoding="utf-8",
    )

    old_argv = sys.argv
    try:
        sys.argv = ["verify_optimization_pairs.py", str(tmp_path), "--timeout", "10"]
        main()
    finally:
        sys.argv = old_argv

    row = json.loads((tmp_path / "pairs.jsonl").read_text(encoding="utf-8"))
    assert row["task"] == "iterate"


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


def test_the_builder_can_route_recursion_shapes_automatically():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import task_for_code

    direct = "int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }"
    branching = "int fib(int n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }"

    assert task_for_code(direct, "auto") == "iterate"
    assert task_for_code(branching, "auto") == "optimize"


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


def test_api_config_reader_ignores_trailing_env_notes(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import load_provider_config

    env = tmp_path / ".env"
    env.write_text(
        '{"providers":{"demo":{"baseUrl":"https://example.test","apiKey":"secret"}}}\n'
        "EXTRA_NOT_JSON=1\n",
        encoding="utf-8",
    )

    assert load_provider_config(env, "demo") == {
        "baseUrl": "https://example.test",
        "apiKey": "secret",
    }


def test_api_generator_prefers_provider_model_override(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import APIGenerator

    env = tmp_path / ".env"
    env.write_text(
        json.dumps(
            {
                "providers": {
                    "demo": {
                        "baseUrl": "https://example.test",
                        "apiKey": "secret",
                        "model": "provider-model",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    generator = APIGenerator(env, "demo", "cli-model", 10, "optimize")

    assert generator.model == "provider-model"


def test_api_provider_list_preserves_order_and_old_default():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_optimize_dataset import provider_names

    assert provider_names("gemini", None) == ["gemini"]
    assert provider_names("gemini", ["gemini", "gemini2", "gemini"]) == [
        "gemini",
        "gemini2",
    ]


def test_multi_provider_run_does_not_fall_back_to_llama(tmp_path, monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import build_optimize_dataset

    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text(
        json.dumps({"code": "int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }"})
        + "\n",
        encoding="utf-8",
    )
    env = tmp_path / ".env"
    env.write_text(
        json.dumps({
            "providers": {
                "gemini": {"baseUrl": "https://example.test", "apiKey": "a"},
                "gemini2": {"baseUrl": "https://example.test", "apiKey": "b"},
            }
        }),
        encoding="utf-8",
    )

    monkeypatch.setattr(build_optimize_dataset.APIGenerator, "_one", lambda *args: "")
    monkeypatch.setattr(
        build_optimize_dataset,
        "complete",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("called llama")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_optimize_dataset.py",
            "--corpus", str(corpus),
            "--out", str(tmp_path / "out.jsonl"),
            "--task", "auto",
            "--limit", "1",
            "--samples", "1",
            "--backend", "api",
            "--providers", "gemini", "gemini2",
            "--env", str(env),
        ],
    )

    build_optimize_dataset.main()


def test_retry_failed_reattempts_attempted_but_unverified_rows(tmp_path, monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import build_optimize_dataset

    code = "int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }"
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text(json.dumps({"code": code}) + "\n", encoding="utf-8")
    out = tmp_path / "out.jsonl"
    out.with_suffix(".attempted.json").write_text(json.dumps([code]), encoding="utf-8")

    calls = []
    monkeypatch.setattr(build_optimize_dataset, "complete", lambda *args, **kwargs: calls.append(args) or "")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_optimize_dataset.py",
            "--corpus", str(corpus),
            "--out", str(out),
            "--task", "auto",
            "--limit", "1",
            "--samples", "1",
            "--backend", "llama",
            "--retry-failed",
        ],
    )
    monkeypatch.setattr(build_optimize_dataset, "wait_for_server", lambda *args, **kwargs: None)

    class Process:
        def terminate(self):
            pass

        def wait(self, timeout):
            pass

    monkeypatch.setattr(build_optimize_dataset.subprocess, "Popen", lambda *args, **kwargs: Process())

    build_optimize_dataset.main()

    assert calls
    assert (tmp_path / "out.failures.jsonl").exists()
