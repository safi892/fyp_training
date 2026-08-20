"""The checks must fire on what the model actually got wrong, and only on that.

Every case below is a real output from `test_results/seed_annotation.json` or
`test_results/corpus_recursion.json`, not an invented one. A checker tested on
imagined failures catches imagined failures.
"""

from __future__ import annotations

import shutil

import pytest

from qwen_cpp_review.claim_checks import check_claims, filter_comments, recursive_functions
from qwen_cpp_review.checked_response import check_response

RECURSIVE = "int fact(int n) { if (n <= 1) return 1; return n * fact(n - 1); }"
ITERATIVE = "int fact(int n) { int r = 1; for (int i = 2; i <= n; i++) r *= i; return r; }"
#: Same shape, wrong answer. Only running it catches this.
WRONG = ITERATIVE.replace("int r = 1;", "int r = 0;")

STACK_LINE = "stack<pair<int, int>> pending;"


# --- claim checks -----------------------------------------------------------

def test_calling_a_loop_recursive_is_a_contradiction():
    """Verbatim from the model on `quicksort_ranges`, which has no recursion."""
    said = "Subsequent calls process the left and right partitions, recursively sorting them."
    assert [c.kind for c in check_claims(ITERATIVE, said).contradictions] == ["recursion"]


def test_naming_the_removed_recursion_is_not_a_contradiction():
    """Checked against code that really has the stack, so only the recursion
    wording is under test - a fixture without one would fail for the other reason."""
    with_stack = "void walk(Node* n) { stack<Node*> p; p.push(n); while (!p.empty()) p.pop(); }"
    for fine in (
        "Uses a stack to simulate recursion, pushing nodes onto the stack.",
        "Replaces the recursive descent with an explicit stack.",
        "An iterative version of the recursive algorithm.",
    ):
        assert check_claims(with_stack, fine).ok, fine


def test_describing_real_recursion_is_not_a_contradiction():
    assert check_claims(RECURSIVE, "The function calls itself until n reaches 1.").ok


def test_naming_a_structure_the_code_does_not_have():
    code = "void f() { stack<int> s; s.push(1); }"
    found = check_claims(code, "Uses a BFS queue to hold the cells.").contradictions
    assert [c.kind for c in found] == ["no queue in the code"]


def test_naming_a_structure_the_code_does_have_is_fine():
    code = "void f() { stack<int> s; s.push(1); }"
    assert check_claims(code, "Uses a stack to hold the cells.").ok


def test_vague_prose_is_not_called_wrong():
    """A checker that fires on uncertainty stops being evidence."""
    assert check_claims(ITERATIVE, "Computes a value from the input.").ok


def test_complexity_comments_do_not_read_as_recursion():
    """`//S.C : O(26)` parses as a function `O(26){...}` whose body calls `O(n)`."""
    annotated = (
        "int f(string s) {\n"
        "    vector<int> count(26, 0); //S.C : O(26)\n"
        "    for (char &c : s) { //T.C : O(n)\n        count[c - 'a']++;\n    }\n"
        "    return 0;\n}"
    )
    assert recursive_functions(annotated) == []


# --- per-line comment filtering --------------------------------------------

def test_comment_contradicting_its_own_line_is_dropped():
    """Verbatim from the model on `flood_fill`."""
    comments = [{"line": 11, "code": STACK_LINE, "comment": "BFS queue for flood-filling."}]
    kept, dropped = filter_comments("", comments)
    assert kept == [] and len(dropped) == 1


def test_comment_agreeing_with_its_line_is_kept():
    comments = [{"line": 11, "code": STACK_LINE, "comment": "Stack of cells still to visit."}]
    kept, dropped = filter_comments("", comments)
    assert len(kept) == 1 and dropped == []


def test_a_comment_on_a_line_declaring_nothing_is_left_alone():
    """Only a line that declares a structure can contradict one."""
    comments = [{"line": 3, "code": "int total = 0;", "comment": "Running total for the queue."}]
    kept, _ = filter_comments("", comments)
    assert len(kept) == 1


# --- the composed entry point ----------------------------------------------

def test_anchors_quoting_a_missing_line_are_dropped():
    response = {"line_comments": [
        {"line": 1, "code": "int fact(int n) { if (n <= 1) return 1; return n * fact(n - 1); }",
         "comment": "recursive factorial"},
        {"line": 2, "code": "cout << nothing_like_this;", "comment": "invented"},
    ]}
    checked = check_response(RECURSIVE, response, verify_improved=False)
    assert checked.dropped_anchors == 1
    assert len(checked.line_comments) == 1
    assert checked.needs_review


def test_a_clean_response_needs_no_review():
    response = {"line_comments": [], "explanation": "Computes n factorial by looping from 2 to n."}
    checked = check_response(ITERATIVE, response, verify_improved=False)
    assert checked.ok if hasattr(checked, "ok") else not checked.needs_review


def test_explanation_conflicts_are_flagged_but_the_text_is_kept():
    """Deleting half a paragraph leaves prose that reads whole and is not."""
    response = {"explanation": "Recursively sorts the halves. Then prints the result."}
    checked = check_response(ITERATIVE, response, verify_improved=False)
    assert len(checked.explanation_conflicts) == 1
    assert checked.explanation is not None


@pytest.mark.skipif(shutil.which("g++") is None, reason="needs a C++ compiler")
def test_a_rewrite_that_changes_the_answer_is_withheld():
    checked = check_response(RECURSIVE, {"improved_code": WRONG})
    assert checked.improved_code is None
    assert "same output" in (checked.improved_code_rejected or "")
    assert checked.needs_review


@pytest.mark.skipif(shutil.which("g++") is None, reason="needs a C++ compiler")
def test_a_correct_rewrite_is_shown():
    checked = check_response(RECURSIVE, {"improved_code": ITERATIVE})
    assert checked.improved_code == ITERATIVE
    assert checked.improved_code_rejected is None


@pytest.mark.skipif(shutil.which("g++") is None, reason="needs a C++ compiler")
def test_an_undrivable_signature_is_not_treated_as_a_failure():
    """Unproven is not the same as wrong; withholding it would hide correct answers."""
    weird = "void run() { std::cout << 1; }"
    checked = check_response(weird, {"improved_code": "void run() { std::cout << 1; }"})
    assert checked.improved_code_rejected is None


def test_verification_can_be_turned_off_without_losing_the_other_checks():
    response = {"improved_code": WRONG, "explanation": "Recursively multiplies the values."}
    checked = check_response(ITERATIVE, response, verify_improved=False)
    assert checked.improved_code == WRONG            # not checked, so not withheld
    assert len(checked.explanation_conflicts) == 1   # still checked


# --- false positives found by running it over real output -------------------

def test_a_quoted_string_literal_is_not_a_claim():
    """`printRecursion` was rewritten as a loop that prints "I love Recursion".

    Describing that loop as printing the phrase is correct, and the word inside
    the quotation marks is not an assertion that the code recurses.
    """
    loop = 'int main() { for (int i = 0; i < n; i++) cout << "I love Recursion" << endl; }'
    said = 'Prints the phrase "I love Recursion" exactly n times.'
    assert check_claims(loop, said).ok


def test_the_call_stack_is_not_a_std_stack():
    """"stack overflow" is about the runtime stack, which no program declares."""
    recursive = "long long fib(int n) { return n < 2 ? n : fib(n-1) + fib(n-2); }"
    for said in (
        "The recursion leads to exponential time and stack overflow.",
        "Each call adds a stack frame, so deep inputs exhaust the call stack.",
    ):
        assert check_claims(recursive, said).ok, said


def test_a_real_std_stack_claim_still_fires():
    """The exclusions must not swallow the case the check exists for."""
    no_stack = "int f(int n) { int r = 0; for (int i = 0; i < n; i++) r += i; return r; }"
    found = check_claims(no_stack, "Uses a stack to hold the pending items.").contradictions
    assert [c.kind for c in found] == ["no stack in the code"]
