from __future__ import annotations

import json
from typing import Any, Protocol


SYSTEM_PROMPT = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)


FIELD_TITLES = {
    "comments": "Line-by-line comments",
    "explanation": "Explanation",
    "improved_code": "Improved code",
    "complexity_analysis": "Complexity analysis",
    "issues": "Issues",
    "security_review": "Security review",
    "best_practices": "Best practices",
    "refactoring": "Refactoring",
    "code_smells": "Code smells",
    "confidence": "Confidence",
    "roman_urdu_explanation": "Roman Urdu explanation",
}


class ChatTemplateTokenizer(Protocol):
    def apply_chat_template(
        self,
        conversation: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
    ) -> str: ...


def build_instruction(example: dict[str, Any], output_fields: list[str]) -> str:
    language = example.get("language") or "cpp"
    requested = "\n".join(f"- {FIELD_TITLES.get(field, field.replace('_', ' ').title())}" for field in output_fields)
    return (
        "Analyze the following C++ code.\n\n"
        f"Language: {language}\n\n"
        "Generate:\n"
        f"{requested}\n\n"
        "Return a single JSON object using the requested field names."
    )


def build_response(example: dict[str, Any], output_fields: list[str]) -> str:
    response = {field: example[field] for field in output_fields if field in example}
    return json.dumps(response, ensure_ascii=False, indent=2)


def build_messages(example: dict[str, Any], output_fields: list[str]) -> list[dict[str, str]]:
    instruction = build_instruction(example, output_fields)
    code = example.get("code", "")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
        {"role": "assistant", "content": build_response(example, output_fields)},
    ]


def format_instruction_template(example: dict[str, Any], output_fields: list[str]) -> str:
    instruction = build_instruction(example, output_fields)
    response = build_response(example, output_fields)
    code = example.get("code", "")
    return (
        "### Instruction\n\n"
        f"{instruction}\n\n"
        "### Code\n\n"
        f"{code}\n\n"
        "### Response\n\n"
        f"{response}"
    )


def format_prompt(
    example: dict[str, Any],
    output_fields: list[str],
    *,
    style: str,
    tokenizer: ChatTemplateTokenizer | None = None,
) -> str:
    if style == "instruction":
        return format_instruction_template(example, output_fields)
    if style != "chat":
        raise ValueError(f"Unsupported prompt style: {style}")
    if tokenizer is None:
        raise ValueError("A tokenizer is required for chat prompt formatting.")
    return tokenizer.apply_chat_template(
        build_messages(example, output_fields),
        tokenize=False,
        add_generation_prompt=False,
    )


def format_prompt_without_response(
    code: str,
    output_fields: list[str],
    *,
    style: str,
    tokenizer: ChatTemplateTokenizer | None = None,
    language: str = "cpp",
) -> str:
    example = {"code": code, "language": language}
    instruction = build_instruction(example, output_fields)
    if style == "instruction":
        return f"### Instruction\n\n{instruction}\n\n### Code\n\n{code}\n\n### Response\n\n"
    if tokenizer is None:
        raise ValueError("A tokenizer is required for chat prompt formatting.")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

