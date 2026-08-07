from __future__ import annotations

import json
from typing import Any, Protocol


SYSTEM_PROMPT = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)


FIELD_TITLES = {
    "line_comments": "Line-by-line comments",
    "comments": "Commented code",
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

#: Extra guidance appended to a field's line in the instruction block. Only
#: fields whose output shape is not obvious from the title need an entry.
FIELD_HINTS = {
    "line_comments": (
        'array of {"line", "code", "comment"} objects, where "line" is the '
        '1-based line number and "code" is that line copied verbatim from the '
        "input. Never reformat or rewrite the code, and only comment lines that "
        "carry meaning"
    ),
    "complexity_analysis": 'object with "time" and "space"',
}

#: Which output fields each task asks for. A dataset row names its task in a
#: ``task`` key; rows without one fall back to the configured output fields, so
#: existing single-task configs keep working unchanged.
TASKS = {
    "line_comments": ["line_comments"],
    "explanation": ["explanation"],
    "complexity": ["complexity_analysis"],
    "improve": ["improved_code"],
    "review": ["line_comments", "explanation", "improved_code", "complexity_analysis"],
}


class ChatTemplateTokenizer(Protocol):
    def apply_chat_template(
        self,
        conversation: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
    ) -> str: ...


def field_label(field: str) -> str:
    return FIELD_TITLES.get(field, field.replace("_", " ").title())


def has_field(example: dict[str, Any], field: str) -> bool:
    """Whether ``example`` actually supplies ``field``.

    ``datasets`` unifies the schema across a mixed-task JSONL file, so a row
    that never had ``line_comments`` still carries the key with a ``None``
    value. Treating that as present would ask every explanation row to emit
    ``"line_comments": null``.
    """
    return example.get(field) is not None


def resolve_output_fields(example: dict[str, Any], output_fields: list[str]) -> list[str]:
    """Pick the fields this example asks for.

    A row carrying a ``task`` key uses that task's field list; anything else
    uses the configured default. Task fields absent from the row are dropped so
    the instruction never asks for something the target cannot supply.
    """
    task = example.get("task")
    if not task:
        return [field for field in output_fields if has_field(example, field)] or output_fields
    if task not in TASKS:
        raise ValueError(f"Unknown task {task!r}. Known tasks: {sorted(TASKS)}")
    declared = TASKS[task]
    present = [field for field in declared if has_field(example, field)]
    return present or declared


def build_instruction(example: dict[str, Any], output_fields: list[str]) -> str:
    language = example.get("language") or "cpp"
    lines = []
    for field in output_fields:
        hint = FIELD_HINTS.get(field)
        lines.append(f"- {field_label(field)}" + (f" ({hint})" if hint else ""))
    requested = "\n".join(lines)
    return (
        "Analyze the following C++ code.\n\n"
        f"Language: {language}\n\n"
        "Generate:\n"
        f"{requested}\n\n"
        "Return a single JSON object using the requested field names."
    )


def build_response(example: dict[str, Any], output_fields: list[str], *, indent: int | None = 2) -> str:
    """Render the target JSON.

    ``indent`` is configurable, but the default is pretty-printed: measured
    against the Qwen tokenizer, compact JSON saves only ~15% on the largest
    task (``line_comments`` p99 1257 -> 1051 tokens) because runs of
    indentation tokenize cheaply. Readability wins at that price.
    """
    response = {field: example[field] for field in output_fields if has_field(example, field)}
    separators = None if indent is not None else (",", ":")
    return json.dumps(response, ensure_ascii=False, indent=indent, separators=separators)


def build_messages(
    example: dict[str, Any],
    output_fields: list[str],
    *,
    indent: int | None = 2,
) -> list[dict[str, str]]:
    fields = resolve_output_fields(example, output_fields)
    instruction = build_instruction(example, fields)
    code = example.get("code", "")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
        {"role": "assistant", "content": build_response(example, fields, indent=indent)},
    ]


def format_instruction_template(
    example: dict[str, Any],
    output_fields: list[str],
    *,
    indent: int | None = 2,
) -> str:
    fields = resolve_output_fields(example, output_fields)
    instruction = build_instruction(example, fields)
    response = build_response(example, fields, indent=indent)
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
    indent: int | None = 2,
) -> str:
    if style == "instruction":
        return format_instruction_template(example, output_fields, indent=indent)
    if style != "chat":
        raise ValueError(f"Unsupported prompt style: {style}")
    if tokenizer is None:
        raise ValueError("A tokenizer is required for chat prompt formatting.")
    return tokenizer.apply_chat_template(
        build_messages(example, output_fields, indent=indent),
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
    task: str | None = None,
) -> str:
    """Render an inference prompt.

    Passing ``task`` asks for exactly that task's fields; omitting it keeps the
    configured ``output_fields``, which is what existing callers do.
    """
    example: dict[str, Any] = {"code": code, "language": language}
    if task is not None:
        example["task"] = task
    fields = resolve_output_fields(example, output_fields)
    instruction = build_instruction(example, fields)
    if style == "instruction":
        return f"### Instruction\n\n{instruction}\n\n### Code\n\n{code}\n\n### Response\n\n"
    if tokenizer is None:
        raise ValueError("A tokenizer is required for chat prompt formatting.")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

