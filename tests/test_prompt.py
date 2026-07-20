import json

from qwen_cpp_review.prompt import build_messages, format_instruction_template


def test_instruction_template_contains_configured_fields():
    example = {
        "code": "int main(){return 0;}",
        "language": "cpp",
        "comments": "// returns zero",
        "explanation": "A minimal program.",
        "improved_code": "int main() { return 0; }",
        "complexity_analysis": {"time": "O(1)", "space": "O(1)"},
    }

    text = format_instruction_template(example, ["comments", "complexity_analysis"])

    assert "### Instruction" in text
    assert "### Code" in text
    assert "### Response" in text
    assert '"comments"' in text
    assert '"complexity_analysis"' in text
    assert '"improved_code"' not in text


def test_chat_messages_response_is_json():
    example = {"code": "int x;", "comments": "comment"}
    messages = build_messages(example, ["comments"])

    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "assistant"
    assert json.loads(messages[-1]["content"]) == {"comments": "comment"}

