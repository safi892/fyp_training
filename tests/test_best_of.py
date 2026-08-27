"""Sampling several answers and letting the checks pick which one is served.

The hazard this has to avoid is that "fewest objections" is optimised by saying
nothing: a response with one comment and no explanation objects to nothing and
would win every time, so best-of-N would make the product worse the more
samples it was given. These tests pin the degenerate direction closed.
"""

from __future__ import annotations

from qwen_cpp_review.checked_response import best_of, content_size, objection_count

CODE = (
    "int total(const int values[], int n) {\n"
    "  int sum = 0;\n"
    "  for (int i = 0; i < n; ++i)\n"
    "    sum += values[i];\n"
    "  return sum;\n"
    "}"
)

FULL_AND_CLEAN = {
    "line_comments": [
        {"line": 2, "code": "int sum = 0;", "comment": "running total starts empty"},
        {"line": 3, "code": "for (int i = 0; i < n; ++i)", "comment": "visit every element once"},
        {"line": 5, "code": "return sum;", "comment": "hand back the accumulated total"},
    ],
    "explanation": "Adds every element of the array. Returns the total.",
}

THIN_AND_CLEAN = {
    "line_comments": [
        {"line": 2, "code": "int sum = 0;", "comment": "running total starts empty"},
    ],
    "explanation": "Adds the elements.",
}

FULL_BUT_FLAWED = {
    "line_comments": [
        {"line": 2, "code": "int sum = 0;", "comment": "running total starts empty"},
        {"line": 9, "code": "delete[] values;", "comment": "invented - not in the source"},
        {"line": 3, "code": "for (int i = 0; i < n; ++i)", "comment": "visit every element"},
    ],
    "explanation": "Adds every element. Recursively sums the sub-arrays.",
}

EMPTY = {"line_comments": [], "explanation": ""}


def test_a_clean_answer_beats_a_flawed_one():
    _, index = best_of(CODE, [FULL_BUT_FLAWED, FULL_AND_CLEAN], verify_improved=False)
    assert index == 1


def test_among_clean_answers_the_fuller_one_wins():
    _, index = best_of(CODE, [THIN_AND_CLEAN, FULL_AND_CLEAN], verify_improved=False)
    assert index == 1


def test_saying_nothing_does_not_win():
    """The whole hazard: an empty answer objects to nothing."""
    _, index = best_of(CODE, [EMPTY, FULL_AND_CLEAN], verify_improved=False)
    assert index == 1


def test_saying_nothing_does_not_win_even_against_a_flawed_answer():
    """A flawed answer that says something is served over an empty clean one."""
    checked, index = best_of(CODE, [EMPTY, FULL_BUT_FLAWED], verify_improved=False)
    assert index == 1, f"served the empty answer; objections={objection_count(checked)}"


def test_ties_go_to_the_earliest_sample():
    _, index = best_of(CODE, [FULL_AND_CLEAN, dict(FULL_AND_CLEAN)], verify_improved=False)
    assert index == 0


def test_no_responses_is_not_an_error():
    checked, index = best_of(CODE, [], verify_improved=False)
    assert index == -1 and not checked.needs_review


def test_a_single_response_is_returned_unchanged():
    checked, index = best_of(CODE, [FULL_AND_CLEAN], verify_improved=False)
    assert index == 0 and len(checked.line_comments) == 3


def test_objection_count_and_content_size_move_in_the_right_directions():
    from qwen_cpp_review.checked_response import check_response

    flawed = check_response(CODE, FULL_BUT_FLAWED, verify_improved=False)
    clean = check_response(CODE, FULL_AND_CLEAN, verify_improved=False)
    assert objection_count(flawed) > objection_count(clean) == 0
    assert content_size(clean) > content_size(check_response(CODE, THIN_AND_CLEAN, verify_improved=False))
