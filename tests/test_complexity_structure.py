"""A suspect complexity label is contradicted by structure, not by its name.

The flag used to fire on the label alone, and `build_task_mixture` blocks on it,
so every `O(n³)` row left the mixture and the adapter could not emit the label
even where it was right. These tests pin the replacement: the label is only
distrusted when the written code cannot produce it.
"""

from __future__ import annotations

from qwen_cpp_review.claim_checks import complexity_contradicted, max_loop_depth

TRIPLE = "void f(int n){for(int i=0;i<n;i++)for(int j=0;j<n;j++)for(int k=0;k<n;k++){}}"
DOUBLE = "void f(int n){for(int i=0;i<n;i++)for(int j=0;j<n;j++){}}"
FLAT = "void f(int n){for(int i=0;i<n;i++){}}"
RECURSIVE = "int f(int n){ if(n<2) return n; return f(n-1)+f(n-2); }"


def test_max_loop_depth_counts_nesting():
    assert max_loop_depth(TRIPLE) == 3
    assert max_loop_depth(DOUBLE) == 2
    assert max_loop_depth(FLAT) == 1
    assert max_loop_depth("int x = 1;") == 0


def test_max_loop_depth_counts_while_and_range_for():
    assert max_loop_depth("void f(){ while(1){ for(int i=0;i<3;i++){} } }") == 2
    assert max_loop_depth("void f(std::vector<int>& v){ for(auto& x : v){ while(x){} } }") == 2


def test_cubic_label_stands_when_three_loops_are_written():
    assert not complexity_contradicted(TRIPLE, "O(n³)")


def test_cubic_label_is_contradicted_by_two_loops():
    assert complexity_contradicted(DOUBLE, "O(n³)")


def test_recursion_makes_the_label_unprovable_rather_than_wrong():
    """Recursion can be cubic with no nesting at all, so it is not contradicted."""
    assert not complexity_contradicted(RECURSIVE, "O(n³)")


def test_labels_that_nesting_cannot_speak_to_are_left_alone():
    """`O(n log n)` comes from an algorithm, not from loop depth."""
    assert not complexity_contradicted(FLAT, "O(n log n)")
    assert not complexity_contradicted(FLAT, "O(1)")
    assert not complexity_contradicted(FLAT, None)


def test_ascii_and_unicode_spellings_are_both_checked():
    assert complexity_contradicted(DOUBLE, "O(n^3)")
    assert complexity_contradicted(DOUBLE, "O(n³)")


def test_unparseable_code_is_not_reported_as_contradicted_by_depth_alone():
    """Garbage parses to depth 0, but if it recurses we still must not accuse it."""
    assert complexity_contradicted("}{ not c++ at all", "O(n³)")


def test_corroboration_requires_the_nesting_the_label_needs():
    from qwen_cpp_review.claim_checks import complexity_corroborated

    assert complexity_corroborated(DOUBLE, "O(n²)")
    assert not complexity_corroborated(FLAT, "O(n²)")
    assert complexity_corroborated(TRIPLE, "O(n³)")
    assert not complexity_corroborated(DOUBLE, "O(n³)")


def test_corroboration_stays_silent_on_labels_nesting_cannot_explain():
    """Low annotator confidence must survive where the code cannot corroborate."""
    from qwen_cpp_review.claim_checks import complexity_corroborated

    assert not complexity_corroborated(DOUBLE, "O(n log n)")
    assert not complexity_corroborated(DOUBLE, "O(1)")
    assert not complexity_corroborated(DOUBLE, None)
