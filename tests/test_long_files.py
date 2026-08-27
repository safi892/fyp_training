"""Concatenating anchored rows must not move the anchors off their lines.

The corpus is single functions at p50 15 lines, and the model's false-statement
rate goes from 1/46 in-distribution to 9/20 on 45-58 line programs - where 2.2%
of the training rows live. These files close that gap, and they are worth having
only if the anchor guarantee survives the join: a long file whose anchors are
wrong teaches the model to invent quotes, which is the one thing the whole
line-anchored design exists to prevent.

The off-by-one is the reason these tests exist. A separator of "\\n\\n" adds one
blank line, not two: its first newline terminates the previous part's last line.
Counting it as two shifted every anchor by one per part, and the first run
emitted nothing at all.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("blf", ROOT / "scripts" / "build_long_files.py")
blf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blf)

FIRST = {
    "code": "int twice(int n)\n{\n  return n * 2;\n}",
    "line_comments": [
        {"line": 1, "code": "int twice(int n)", "comment": "double a number"},
        {"line": 3, "code": "return n * 2;", "comment": "the doubling itself"},
    ],
}
SECOND = {
    "code": "int half(int n)\n{\n  return n / 2;\n}",
    "line_comments": [
        {"line": 3, "code": "return n / 2;", "comment": "integer halving"},
    ],
}


def test_anchors_survive_the_join():
    built = blf.bundle([FIRST, SECOND])
    assert built is not None
    assert blf.anchors_hold(built["code"], built["line_comments"])


def test_the_second_part_is_shifted_by_its_offset_plus_one_blank_line():
    """FIRST is 4 lines, the blank makes 5, so SECOND's line 3 becomes line 8."""
    built = blf.bundle([FIRST, SECOND])
    lines = [a["line"] for a in built["line_comments"]]
    assert lines == [1, 3, 8], lines


def test_a_wrong_offset_is_caught_rather_than_emitted():
    """The guarantee is checked, not assumed - this is what discards a bad bundle."""
    code = "int a;\nint b;"
    assert not blf.anchors_hold(code, [{"line": 2, "code": "int a;", "comment": "x"}])
    assert not blf.anchors_hold(code, [{"line": 9, "code": "int a;", "comment": "x"}])
    assert blf.anchors_hold(code, [{"line": 1, "code": "int a;", "comment": "x"}])


def test_anchors_come_out_in_line_order():
    built = blf.bundle([SECOND, FIRST])
    lines = [a["line"] for a in built["line_comments"]]
    assert lines == sorted(lines)


def test_definitions_are_found_and_keywords_are_not():
    names = blf.defined_names("int solve(int n) { if (n) { for (;;) {} } return 0; }")
    assert names == {"solve"}


def test_a_bundle_defining_the_same_name_twice_is_refused():
    """Two rows both defining `solve` would not compile as one file."""
    import random
    same = dict(FIRST, code="int solve(int n)\n{\n  return n;\n}",
                line_comments=[{"line": 3, "code": "return n;", "comment": "x"}])
    other = dict(same)
    built = list(blf.bundles([same, other], min_lines=4, max_lines=90, rng=random.Random(0)))
    assert built == []


def test_comments_are_carried_through_unchanged():
    built = blf.bundle([FIRST, SECOND])
    assert [a["comment"] for a in built["line_comments"]] == [
        "double a number", "the doubling itself", "integer halving",
    ]
