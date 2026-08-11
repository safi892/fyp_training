"""Repairing line numbers the model got wrong.

The cases here are the real output of checkpoint-500 on `digit_sum_loop`: the
quoted code was right every time and only the number drifted, because the model
did not count the brace-only line.
"""

from qwen_cpp_review.line_anchoring import repair_anchors

CODE = "\n".join(
    [
        "int countDigits(int a, int b)",  # 1
        "{",  # 2
        "  int sum = a + b;",  # 3
        "  int count = 0;",  # 4
        "  while (sum != 0)",  # 5
        "  {",  # 6
        "    sum /= 10;",  # 7
        "    count++;",  # 8
        "  }",  # 9
        "  return count;",  # 10
        "}",  # 11
    ]
)

#: Verbatim from the checkpoint-500 run.
MODEL_OUTPUT = [
    {"line": 3, "code": "int sum = a + b;", "comment": "Compute the sum"},
    {"line": 4, "code": "int count = 0;", "comment": "Initialize digit counter to zero."},
    {"line": 5, "code": "while (sum != 0)", "comment": "Loop until all digits processed."},
    {"line": 6, "code": "sum /= 10;", "comment": "Remove the least significant digit."},
    {"line": 7, "code": "count++;", "comment": "Count the digit."},
    {"line": 9, "code": "return count;", "comment": "Return the digit count."},
]


def test_off_by_one_anchors_are_relocated_not_discarded():
    report = repair_anchors(CODE, MODEL_OUTPUT)

    assert report.total == 6
    assert report.dropped == 0
    assert report.exact == 3
    assert report.repaired == 3
    assert [(a.line, a.code) for a in report.anchors] == [
        (3, "int sum = a + b;"),
        (4, "int count = 0;"),
        (5, "while (sum != 0)"),
        (7, "sum /= 10;"),
        (8, "count++;"),
        (10, "return count;"),
    ]


def test_every_repaired_anchor_matches_its_new_line():
    lines = [line.strip() for line in CODE.split("\n")]

    for anchor in repair_anchors(CODE, MODEL_OUTPUT).anchors:
        assert lines[anchor.line - 1] == anchor.code


def test_quote_absent_from_the_file_is_dropped():
    report = repair_anchors(CODE, [{"line": 3, "code": "delete[] buffer;", "comment": "invented"}])

    assert report.anchors == []
    assert report.dropped == 1


def test_repeated_line_resolves_to_the_nearest_occurrence():
    code = "if (a)\n  return 0;\nif (b)\n  return 0;\nreturn 1;"
    report = repair_anchors(code, [{"line": 5, "code": "return 0;", "comment": "second branch"}])

    assert [a.line for a in report.anchors] == [4]


def test_correct_anchors_are_left_alone():
    report = repair_anchors(CODE, [{"line": 3, "code": "int sum = a + b;", "comment": "sum"}])

    assert report.exact == 1
    assert report.repaired == 0


def test_malformed_anchor_is_dropped_without_raising():
    report = repair_anchors(CODE, [{"line": 3}, {"code": "int sum = a + b;"}, {}])

    assert report.anchors == []
    assert report.dropped == 3


def test_output_is_sorted_by_line():
    shuffled = list(reversed(MODEL_OUTPUT))

    lines = [a.line for a in repair_anchors(CODE, shuffled).anchors]

    assert lines == sorted(lines)
