from qwen_cpp_review.line_anchoring import (
    anchor_comments,
    normalize,
    parse_annotated,
    split_line,
    strip_code_fence,
)


def test_split_line_separates_trailing_comment():
    code, comment, in_block = split_line("int x = 1; // set x", False)

    assert code == "int x = 1;"
    assert comment == "set x"
    assert in_block is False


def test_split_line_ignores_slashes_inside_string_literal():
    code, comment, _ = split_line('cout << "http://a.b"; // print', False)

    assert code == 'cout << "http://a.b";'
    assert comment == "print"


def test_split_line_tracks_block_comment_across_lines():
    _, _, in_block = split_line("int x = 1; /* open", False)
    assert in_block is True

    code, comment, in_block = split_line("still comment */ int y = 2;", True)
    assert code == " int y = 2;".rstrip()
    assert comment == "still comment"
    assert in_block is False


def test_strip_code_fence_removes_language_fence():
    assert strip_code_fence("```cpp\nint x;\n```") == "int x;"


def test_strip_code_fence_keeps_unfenced_text():
    assert strip_code_fence("int x;") == "int x;"


def test_standalone_comment_attaches_to_following_line():
    parsed = parse_annotated("// describes next\nint x = 1;")

    assert len(parsed) == 1
    assert parsed[0].comment == "describes next"


def test_anchors_use_original_line_numbers_and_text():
    code = "int add(int a, int b)\n{\n  int s = a + b;\n  return s;\n}"
    comments = (
        "```cpp\nint add(int a, int b)\n{\n"
        "  int s = a + b; // add the operands\n"
        "  return s; // hand back the total\n}\n```"
    )

    result = anchor_comments(code, comments)

    assert [anchor.line for anchor in result.anchors] == [3, 4]
    assert result.anchors[0].code == "int s = a + b;"
    assert result.anchors[0].comment == "add the operands"
    assert result.match_ratio == 1.0
    assert result.dropped == 0


def test_reindented_annotation_still_anchors():
    code = "int f()\n{\nreturn 1;\n}"
    comments = "int f()\n{\n        return 1;   // constant\n}"

    result = anchor_comments(code, comments)

    assert [anchor.line for anchor in result.anchors] == [3]
    assert result.match_ratio == 1.0


def test_comment_on_invented_line_is_dropped():
    code = "int s = a + b;\nreturn s;"
    comments = "#include <iostream> // added by annotator\nint s = a + b; // real\nreturn s;"

    result = anchor_comments(code, comments)

    assert [anchor.line for anchor in result.anchors] == [1]
    assert result.dropped == 1
    assert result.match_ratio < 1.0


def test_rewritten_statement_does_not_anchor():
    code = "count = count + 1;"
    comments = "count += 1; // bump the counter"

    result = anchor_comments(code, comments)

    assert result.anchors == []
    assert result.match_ratio == 0.0


def test_header_only_comment_yields_no_anchors():
    code = "int main() { return 0; }"
    comments = "// This program does nothing.\n// It returns zero."

    result = anchor_comments(code, comments)

    assert result.anchors == []
    assert result.anchored == 0


def test_empty_inputs_are_safe():
    assert anchor_comments("", "// something").anchors == []
    assert anchor_comments("int x;", "").anchors == []


def test_coverage_counts_commented_original_lines():
    code = "int a = 1;\nint b = 2;\nint c = 3;"
    comments = "int a = 1; // one\nint b = 2;\nint c = 3; // three"

    result = anchor_comments(code, comments)

    assert result.coverage == 2 / 3


def test_normalize_collapses_whitespace():
    assert normalize("  int    x  =  1;  ") == "int x = 1;"
