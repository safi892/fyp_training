import json

import pytest

from qwen_cpp_review.prompt import (
    TASKS,
    build_messages,
    build_response,
    format_instruction_template,
    format_prompt_without_response,
    resolve_output_fields,
)

ANCHORS = [
    {"line": 3, "code": "int s = a + b;", "comment": "add the operands"},
    {"line": 4, "code": "return s;", "comment": "hand back the total"},
]


def test_row_without_task_keeps_configured_fields():
    example = {"code": "int x;", "comments": "c"}

    assert resolve_output_fields(example, ["comments"]) == ["comments"]


def test_task_overrides_configured_fields():
    example = {"code": "int x;", "task": "line_comments", "line_comments": ANCHORS}

    assert resolve_output_fields(example, ["explanation"]) == ["line_comments"]


def test_task_fields_absent_from_row_are_not_requested():
    example = {"code": "int x;", "task": "review", "explanation": "e"}

    assert resolve_output_fields(example, []) == ["explanation"]


def test_inference_task_keeps_declared_fields_with_no_targets_present():
    example = {"code": "int x;", "task": "review"}

    assert resolve_output_fields(example, []) == TASKS["review"]


def test_unknown_task_is_rejected():
    with pytest.raises(ValueError, match="Unknown task"):
        resolve_output_fields({"task": "nope"}, [])


def test_line_comments_target_round_trips_as_json():
    example = {"code": "int x;", "task": "line_comments", "line_comments": ANCHORS}

    messages = build_messages(example, [])

    assert json.loads(messages[-1]["content"]) == {"line_comments": ANCHORS}


def test_instruction_explains_the_anchor_format():
    example = {"code": "int x;", "task": "line_comments", "line_comments": ANCHORS}

    text = format_instruction_template(example, [])

    assert "Line-by-line comments" in text
    assert "1-based line number" in text
    assert "verbatim" in text


def test_instruction_only_lists_the_task_fields():
    example = {
        "code": "int x;",
        "task": "complexity",
        "complexity_analysis": {"time": "O(1)", "space": "O(1)"},
        "explanation": "not requested",
    }

    text = format_instruction_template(example, [])

    assert "Complexity analysis" in text
    assert "Explanation" not in text
    assert "not requested" not in text


def test_compact_indent_drops_whitespace():
    example = {"code": "int x;", "task": "line_comments", "line_comments": ANCHORS}

    pretty = build_response(example, ["line_comments"], indent=2)
    compact = build_response(example, ["line_comments"], indent=None)

    assert json.loads(pretty) == json.loads(compact)
    assert len(compact) < len(pretty)
    assert "\n" not in compact


def test_inference_prompt_accepts_a_task():
    text = format_prompt_without_response("int x;", ["explanation"], style="instruction", task="complexity")

    assert "Complexity analysis" in text
    assert "Explanation" not in text
    assert text.rstrip().endswith("### Response")


def test_none_valued_fields_from_schema_unification_are_ignored():
    """`datasets` fills absent keys with None when tasks share one JSONL file."""
    example = {
        "code": "int x;",
        "task": "explanation",
        "explanation": "does nothing",
        "line_comments": None,
        "complexity_analysis": None,
        "improved_code": None,
    }

    assert resolve_output_fields(example, []) == ["explanation"]
    assert json.loads(build_response(example, ["explanation", "line_comments"])) == {"explanation": "does nothing"}


def test_none_valued_fields_are_ignored_without_a_task():
    example = {"code": "int x;", "comments": "c", "explanation": None}

    assert resolve_output_fields(example, ["comments", "explanation"]) == ["comments"]


def test_inference_row_with_no_targets_still_requests_configured_fields():
    example = {"code": "int x;", "explanation": None}

    assert resolve_output_fields(example, ["explanation"]) == ["explanation"]


def test_every_task_maps_to_known_fields():
    from qwen_cpp_review.prompt import FIELD_TITLES

    for task, fields in TASKS.items():
        assert fields, f"task {task} declares no fields"
        for name in fields:
            assert name in FIELD_TITLES, f"task {task} uses unregistered field {name}"
