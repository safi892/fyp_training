"""Route recursive optimization attempts to the right prompt."""

from __future__ import annotations

import sys
from pathlib import Path

from qwen_cpp_review.optimization_routing import classify_recursion, select_optimization_task

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_optimize_dataset import build_prompt, task_for_code  # noqa: E402


FACTORIAL = """\
long long fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}
"""

FIBONACCI = """\
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
"""

BINARY_SEARCH = """\
int binarySearch(int arr[], int low, int high, int x) {
    if (low > high) return -1;
    int mid = low + (high - low) / 2;
    if (arr[mid] == x) return mid;
    if (arr[mid] > x) return binarySearch(arr, low, mid - 1, x);
    return binarySearch(arr, mid + 1, high, x);
}
"""


def test_direct_recursion_routes_to_iteration_prompt():
    profile = classify_recursion(FACTORIAL)

    assert profile.functions == ("fact",)
    assert profile.task == "iterate"
    assert profile.max_self_calls == 1


def test_branching_return_recursion_routes_to_dp_prompt():
    profile = classify_recursion(FIBONACCI)

    assert profile.functions == ("fib",)
    assert profile.task == "optimize"
    assert profile.max_self_calls_in_return == 2


def test_multiple_branches_are_not_misread_as_overlapping_recursion():
    profile = classify_recursion(BINARY_SEARCH)

    assert profile.functions == ("binarySearch",)
    assert profile.task == "iterate"
    assert profile.max_self_calls == 2
    assert profile.max_self_calls_in_return == 1


def test_comments_do_not_trigger_the_iteration_route():
    code = "int score(int n) { // score(n - 1) would recurse\n    return n + 1;\n}"

    assert select_optimization_task(code) == "optimize"
    assert not classify_recursion(code).recursive


def test_builder_auto_uses_the_selected_prompt_wording():
    assert task_for_code(FACTORIAL, "auto") == "iterate"
    assert task_for_code(FIBONACCI, "auto") == "optimize"
    assert "update the arguments in a while loop" in build_prompt(
        FACTORIAL, task_for_code(FACTORIAL, "auto")
    )
    assert "memoisation or a dynamic-programming table" in build_prompt(
        FIBONACCI, task_for_code(FIBONACCI, "auto")
    )


def test_explicit_task_still_wins_over_auto_routing():
    assert task_for_code(FACTORIAL, "optimize") == "optimize"
    assert task_for_code(FIBONACCI, "iterate") == "iterate"
