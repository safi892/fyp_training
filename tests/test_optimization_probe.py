"""The probe must score the code, never the prose the model wrote about the code.

The first run of this probe read an unchanged tail-recursion as memoised, because
the model had added the comment ``// cache next node`` and the keyword scan saw
"cache". That is the same failure the scoring guard in `test_hard_scoring.py`
exists for, so it gets the same treatment: a test that fails if a verdict can
again be earned by a word in a comment.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from probe_optimization import (  # noqa: E402
    BEST_PHRASING,
    PHRASINGS,
    RENAME_STRATEGIES,
    SAMPLES,
    classify,
    strip_comments,
)

from qwen_cpp_review.obfuscation import STRATEGIES, obfuscate  # noqa: E402

RECURSIVE = "int fib(int n){ if (n <= 1) return n; return fib(n-1) + fib(n-2); }"


def test_comments_cannot_earn_a_verdict():
    narrated = (
        "int fib(int n){\n"
        "  // memo table would cache each dp result here\n"
        "  if (n <= 1) return n;\n"
        "  return fib(n-1) + fib(n-2);  /* vector<int> dp cache */\n"
        "}"
    )
    verdict, signals = classify(RECURSIVE, narrated)
    assert verdict == "unchanged algorithm", verdict
    assert "stores results" not in signals


def test_real_memoisation_still_scores():
    memoised = (
        "int fib(int n){ static int memo[100] = {0};"
        " if (n <= 1) return n;"
        " if (memo[n]) return memo[n];"
        " return memo[n] = fib(n-1) + fib(n-2); }"
    )
    assert classify(RECURSIVE, memoised)[0].startswith("MEMOISED")


def test_a_plain_loop_scores_iterative():
    looped = "int fib(int n){ int a=0,b=1; for(int i=0;i<n;i++){ int t=a+b; a=b; b=t; } return a; }"
    assert classify(RECURSIVE, looped)[0].startswith("ITERATIVE")


def test_strip_comments_leaves_code_intact():
    assert "fib" in strip_comments("int fib(int n); // fib is recursive")
    assert "recursive" not in strip_comments("int fib(int n); // fib is recursive")


def test_every_sample_has_a_phrasing_and_a_difficulty():
    for sample in SAMPLES:
        assert sample["difficulty"] in {"easy", "medium", "hard"}, sample["name"]
        assert BEST_PHRASING[sample["wants"]] in PHRASINGS, sample["name"]


def test_rename_strategies_exist_and_original_is_the_control():
    assert RENAME_STRATEGIES[0] == "original"
    assert set(RENAME_STRATEGIES) <= set(STRATEGIES)


def test_every_sample_actually_renames():
    """A sample that renames to nothing scores as robust without being tested.

    This is not hypothetical: the pointer-heavy samples all returned unchanged
    until `obfuscation.POINTER_DECL_RE` was added, so the probe was reporting
    survival of a rename that never happened.
    """
    for sample in SAMPLES:
        for strategy in RENAME_STRATEGIES:
            if strategy == "original":
                continue
            renamed = obfuscate(sample["code"], strategy, random.Random(0))
            assert renamed != sample["code"], f"{sample['name']} / {strategy}"


def test_samples_cover_all_three_rewrite_kinds():
    """`kind` is the axis the results separate on, so each value needs samples."""
    kinds = {sample["kind"] for sample in SAMPLES}
    assert kinds == {"table", "accumulator", "stack"}
    for kind in kinds:
        assert sum(1 for s in SAMPLES if s["kind"] == kind) >= 3, kind


def test_failure_picker_ignores_a_sample_some_wording_already_fixed(tmp_path):
    """A sample only needs a harder wording if no wording has ever worked on it.

    One losing phrasing beside a winning one is a result about that phrasing, not
    a wall in the model, and sending it back for another round would report the
    same win twice.
    """
    from probe_wordings import failing_samples

    def record(sample, phrasing, verdict):
        return {"sample": sample, "phrasing": phrasing, "strategy": "original",
                "verdict": verdict}

    probe = tmp_path / "probe.json"
    probe.write_text(json.dumps([
        record("fibonacci", "trained_wording", "unchanged algorithm"),
        record("fibonacci", "explicit_memo", "MEMOISED (top-down)"),
        record("inorder_walk", "trained_wording", "unchanged algorithm"),
        record("inorder_walk", "explicit_loop", "unchanged algorithm"),
    ]), encoding="utf-8")

    assert [s["name"] for s in failing_samples(probe)] == ["inorder_walk"]


def test_failure_picker_ignores_renamed_runs(tmp_path):
    """Phase 2 failures are a robustness result, not evidence the wording lost."""
    from probe_wordings import failing_samples

    probe = tmp_path / "probe.json"
    probe.write_text(json.dumps([
        {"sample": "fibonacci", "strategy": "original", "verdict": "MEMOISED (top-down)"},
        {"sample": "fibonacci", "strategy": "terse", "verdict": "unchanged algorithm"},
    ]), encoding="utf-8")

    assert failing_samples(probe) == []


# The recursion and conversion patterns moved to `qwen_cpp_review.claim_checks`
# so the report and the serving layer share one definition. They are tested in
# `test_checked_response.py`; keeping a second copy here is how the two drifted.
