from pathlib import Path

import pytest

from qwen_cpp_review.chunking import Chunk, chunk_code, estimate_tokens, stitch, validate
from qwen_cpp_review.line_anchoring import Anchor

pytest.importorskip("tree_sitter_cpp", reason="chunking needs the C++ grammar")

FILE = Path(__file__).resolve().parents[1] / "examples" / "inventory.cpp"

SMALL = """#include <vector>

int add(int a, int b)
{
  return a + b;
}

int mul(int a, int b)
{
  return a * b;
}
"""


def covered_lines(chunks: list[Chunk]) -> set[int]:
    return {n for chunk in chunks for n in range(chunk.start_line, chunk.end_line + 1)}


# --- coverage invariants ----------------------------------------------------- #


@pytest.mark.parametrize("budget", [150, 200, 300, 400, 800])
def test_every_meaningful_line_lands_in_exactly_one_chunk(budget):
    code = FILE.read_text()
    lines = code.split("\n")

    chunks = chunk_code(code, max_tokens=budget)
    covered = covered_lines(chunks)

    missing = [n for n in range(1, len(lines) + 1) if n not in covered and lines[n - 1].strip()]
    assert not missing, f"non-blank lines dropped at budget {budget}: {missing}"

    seen: set[int] = set()
    for chunk in chunks:
        span = set(range(chunk.start_line, chunk.end_line + 1))
        assert not (span & seen), f"chunk {chunk.start_line}-{chunk.end_line} overlaps another"
        seen |= span


def test_chunk_text_matches_the_lines_it_claims():
    code = FILE.read_text()
    lines = code.split("\n")

    for chunk in chunk_code(code):
        expected = "\n".join(lines[chunk.start_line - 1 : chunk.end_line])
        assert chunk.text == expected, f"chunk {chunk.start_line}-{chunk.end_line} text drifted"


def test_chunks_are_ordered_and_do_not_run_backwards():
    chunks = chunk_code(FILE.read_text())

    assert chunks == sorted(chunks, key=lambda c: c.start_line)
    for chunk in chunks:
        assert chunk.start_line <= chunk.end_line


# --- splitting behaviour ------------------------------------------------------ #


def test_a_class_is_split_into_methods_when_it_does_not_fit():
    chunks = chunk_code(FILE.read_text(), max_tokens=300)

    kinds = [c.kind for c in chunks]
    assert kinds.count("function_definition") >= 6, (
        f"expected the class to break into methods, got {kinds}"
    )
    assert "class_specifier" not in kinds


def test_a_class_stays_whole_when_it_fits():
    chunks = chunk_code(FILE.read_text(), max_tokens=800)

    assert any(c.kind == "class_specifier" for c in chunks)


def test_no_chunk_exceeds_the_budget_unless_it_is_indivisible():
    for chunk in chunk_code(FILE.read_text(), max_tokens=300):
        if not chunk.oversized:
            assert estimate_tokens(chunk.text) <= 300


def test_tiny_neighbours_are_merged_rather_than_sent_one_by_one():
    chunks = chunk_code(SMALL, max_tokens=400)

    assert len(chunks) == 1, [(c.start_line, c.end_line, c.kind) for c in chunks]


def test_empty_input_produces_no_chunks():
    assert chunk_code("") == []
    assert chunk_code("\n\n\n") == []


# --- stitching ---------------------------------------------------------------- #


def test_chunk_local_anchors_become_file_line_numbers():
    code = SMALL
    chunk = Chunk(start_line=3, end_line=6, text="\n".join(code.split("\n")[2:6]), kind="function_definition")
    # "return a + b;" is line 3 of the chunk, line 5 of the file.
    raw = [{"line": 3, "code": "return a + b;", "comment": "adds them"}]

    anchors = stitch(code, [(chunk, raw)])

    assert [(a.line, a.comment) for a in anchors] == [(5, "adds them")]


def test_a_miscounted_anchor_is_relocated_within_its_own_chunk():
    code = SMALL
    chunk = Chunk(start_line=3, end_line=6, text="\n".join(code.split("\n")[2:6]), kind="function_definition")
    # The model says line 2, but quotes the line that is really chunk line 3.
    raw = [{"line": 2, "code": "return a + b;", "comment": "adds them"}]

    anchors = stitch(code, [(chunk, raw)])

    assert [a.line for a in anchors] == [5]


def test_an_invented_line_is_dropped_not_guessed():
    code = SMALL
    chunk = Chunk(start_line=3, end_line=6, text="\n".join(code.split("\n")[2:6]), kind="function_definition")
    raw = [{"line": 3, "code": "launch_missiles();", "comment": "not in the file"}]

    assert stitch(code, [(chunk, raw)]) == []


def test_a_line_is_never_annotated_twice():
    code = SMALL
    chunk = Chunk(start_line=3, end_line=6, text="\n".join(code.split("\n")[2:6]), kind="function_definition")
    raw = [
        {"line": 3, "code": "return a + b;", "comment": "first"},
        {"line": 3, "code": "return a + b;", "comment": "second"},
    ]

    anchors = stitch(code, [(chunk, raw)])

    assert len(anchors) == 1
    assert anchors[0].comment == "first"


def test_identical_lines_in_different_chunks_keep_their_own_comments():
    """`return a + b;` style repeats must not collapse onto one line."""
    code = "int f()\n{\n  return 0;\n}\n\nint g()\n{\n  return 0;\n}\n"
    first = Chunk(start_line=1, end_line=4, text="int f()\n{\n  return 0;\n}", kind="function_definition")
    second = Chunk(start_line=6, end_line=9, text="int g()\n{\n  return 0;\n}", kind="function_definition")

    anchors = stitch(
        code,
        [
            (first, [{"line": 3, "code": "return 0;", "comment": "from f"}]),
            (second, [{"line": 3, "code": "return 0;", "comment": "from g"}]),
        ],
    )

    assert [(a.line, a.comment) for a in anchors] == [(3, "from f"), (8, "from g")]


# --- validation --------------------------------------------------------------- #


def test_validate_rejects_anchors_that_do_not_match_the_file():
    code = "int a = 1;\nint b = 2;\n"
    good = Anchor(line=1, code="int a = 1;", comment="ok")
    wrong_text = Anchor(line=2, code="int a = 1;", comment="mismatched")
    off_file = Anchor(line=99, code="int a = 1;", comment="past the end")

    assert validate(code, [good, wrong_text, off_file]) == [good]
