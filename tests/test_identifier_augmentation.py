import random

from qwen_cpp_review.identifier_augmentation import apply_mapping_to_row, augment_row


def anchors_still_match(row: dict) -> bool:
    """Every anchor's stored text must equal the line it points at."""
    lines = [line.strip() for line in row["code"].split("\n")]
    return all(
        1 <= anchor["line"] <= len(lines) and lines[anchor["line"] - 1] == anchor["code"]
        for anchor in row["line_comments"]
    )


ROW = {
    "code": "int add(int alpha, int beta)\n{\n  int total = alpha + beta;\n  return total;\n}",
    "language": "cpp",
    "line_comments": [
        {"line": 3, "code": "int total = alpha + beta;", "comment": "sum the operands"},
        {"line": 4, "code": "return total;", "comment": "hand back the sum"},
    ],
    "improved_code": "int add(int alpha, int beta) { return alpha + beta; }",
}


def test_augmented_variants_keep_anchors_valid():
    variants = augment_row(ROW, random.Random(0))

    assert len(variants) == 3
    for variant in variants:
        assert anchors_still_match(variant), variant["augmentation"] if "augmentation" in variant else "original"


def test_improved_code_is_renamed_with_the_same_mapping():
    renamed = apply_mapping_to_row(ROW, {"alpha": "x", "beta": "y", "total": "s"})

    assert "alpha" not in renamed["improved_code"]
    assert "x" in renamed["improved_code"]
    assert renamed["code"].count("x") >= 1


def test_original_row_is_not_mutated():
    original_anchor = dict(ROW["line_comments"][0])

    apply_mapping_to_row(ROW, {"alpha": "q", "beta": "r", "total": "z"})

    assert ROW["line_comments"][0] == original_anchor
    assert "alpha" in ROW["code"]


def test_row_without_line_comments_is_handled():
    row = {"code": "int alpha = 1;", "explanation": "sets alpha"}

    renamed = apply_mapping_to_row(row, {"alpha": "x"})

    assert renamed["code"] == "int x = 1;"
    assert "line_comments" not in renamed


def test_row_without_renameable_identifiers_is_returned_unchanged():
    row = {"code": "return 0;"}

    assert augment_row(row, random.Random(0)) == [row]
