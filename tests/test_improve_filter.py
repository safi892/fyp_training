"""The improve task drops rewrites that only changed the spelling.

Measured over the 13,087 improve-eligible rows: 61.8% leave every control-flow
token count identical and only 6.3% introduce a dp/memo/cache, while the task
carries 37% of the supervised tokens. These tests pin the distinction, because
the filter is crude by design and a well-meaning "improvement" to it would
quietly start admitting `const`-sprinkling again.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_task_mixture import changed_structure, emit_tasks  # noqa: E402

RECURSIVE = "int f(int n){ if(n<2) return n; return f(n-1)+f(n-2); }"
ITERATIVE = "int f(int n){ int a=0,b=1; for(int i=0;i<n;i++){int t=a+b;a=b;b=t;} return a; }"


def test_const_sprinkling_is_not_a_structural_change():
    assert not changed_structure(RECURSIVE, "int f(const int n){ if(n<2) return n; return f(n-1)+f(n-2); }")


def test_added_include_is_not_a_structural_change():
    assert not changed_structure(RECURSIVE, "#include <vector>\n" + RECURSIVE)


def test_comment_only_diff_is_not_a_structural_change():
    assert not changed_structure(RECURSIVE, RECURSIVE + "  // now with a comment")


def test_recursion_to_loop_is_a_structural_change():
    assert changed_structure(RECURSIVE, ITERATIVE)


def test_added_guard_is_a_structural_change():
    assert changed_structure(RECURSIVE, "int f(int n){ if(n<0) return 0; if(n<2) return n; return f(n-1)+f(n-2); }")


def test_flow_tokens_inside_comments_do_not_count():
    """A rewrite that only *mentions* a loop in prose has not written one."""
    assert not changed_structure(RECURSIVE, RECURSIVE + "  // a for loop would be faster here")


def _improve_rows(row, **kwargs):
    return [r for r in emit_tasks(row, min_anchors=1, **kwargs) if r["task"] == "improve"]


def test_emit_tasks_drops_a_cosmetic_improve_by_default():
    row = {"code": RECURSIVE, "improved_code": "int f(const int n){ if(n<2) return n; return f(n-1)+f(n-2); }"}
    assert _improve_rows(row) == []


def test_emit_tasks_keeps_a_structural_improve():
    row = {"code": RECURSIVE, "improved_code": ITERATIVE}
    assert len(_improve_rows(row)) == 1


def test_keep_cosmetic_flag_restores_the_old_behaviour():
    """The old mixture must stay reproducible, or before/after is not comparable."""
    row = {"code": RECURSIVE, "improved_code": "int f(const int n){ if(n<2) return n; return f(n-1)+f(n-2); }"}
    assert len(_improve_rows(row, structural_only=False)) == 1
