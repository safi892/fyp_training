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

#: Per-task overrides for the hints above, for when two tasks want the same
#: field to mean different things.
#:
#: `improve` and `optimize` both produce ``improved_code``, but they are not the
#: same request. The training targets for ``improved_code`` were written without
#: being executed, so the model learned tidying - const references, formatting,
#: an added main. Probing showed the wording is what limits it: the trained
#: phrasing changed the algorithm on none of three recursive samples, while
#: naming memoisation explicitly changed it on all three. The instruction below
#: is that wording.
TASK_FIELD_HINTS = {
    "optimize": {
        "improved_code": (
            "if this function recomputes the same subproblems, rewrite it so each is solved "
            "once, using memoisation or a dynamic-programming table. Keep the signature and the "
            "results identical, and size any table from the arguments rather than a fixed "
            "constant. If there are no overlapping subproblems, return the code unchanged"
        ),
    },
    #: Removing recursion is a different request from removing recomputation, and
    #: the wording that wins is different too. Measured on 60 real submissions from
    #: the corpus, with their authors' own identifiers:
    #:
    #:     the trained wording            3/60   (and all three were the same gcd)
    #:     naming the container          10/60
    #:     a worked before/after example  6/60
    #:
    #: This is the middle line verbatim. It is not a large number - see
    #: `docs/DETECTABILITY.md` for why the answer to that is checking the output
    #: rather than asking harder - but it is three times the wording that ships.
    "iterate": {
        "improved_code": (
            "replace direct self-recursion with an iterative loop. For tail recursion or "
            "single-branch recursion, update the arguments in a while loop; use an explicit "
            "std::stack or std::queue only when traversal state really needs it. Keep the "
            "signature and results identical, and do not leave any self-calls"
        ),
    },
}

#: Which output fields each task asks for. A dataset row names its task in a
#: ``task`` key; rows without one fall back to the configured output fields, so
#: existing single-task configs keep working unchanged.
TASKS = {
    "line_comments": ["line_comments"],
    "explanation": ["explanation"],
    "complexity": ["complexity_analysis"],
    "improve": ["improved_code"],
    "optimize": ["improved_code"],
    "iterate": ["improved_code"],
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
    overrides = TASK_FIELD_HINTS.get(example.get("task") or "", {})
    lines = []
    for field in output_fields:
        hint = overrides.get(field, FIELD_HINTS.get(field))
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


def build_prompt_completion(
    example: dict[str, Any],
    output_fields: list[str],
    *,
    style: str,
    tokenizer: ChatTemplateTokenizer | None = None,
    indent: int | None = 2,
) -> tuple[str, str]:
    """Split one example into ``(prompt, completion)``.

    TRL computes completion-only loss for prompt-completion datasets and
    full-sequence loss for language-modeling ones, so this split is what makes
    the instruction and the input code unsupervised. The prompt ends where
    generation begins, and the completion is the target alone.
    """
    fields = resolve_output_fields(example, output_fields)
    code = example.get("code", "")
    language = example.get("language") or "cpp"
    completion = build_response(example, fields, indent=indent)

    if style == "instruction":
        instruction = build_instruction(example, fields)
        return (
            f"### Instruction\n\n{instruction}\n\n### Code\n\n{code}\n\n### Response\n\n",
            completion,
        )
    if style != "chat":
        raise ValueError(f"Unsupported prompt style: {style}")
    prompt = format_prompt_without_response(
        code,
        fields,
        style=style,
        tokenizer=tokenizer,
        language=language,
    )
    return prompt, completion


#: Appended to the instruction at inference, for the describing tasks only.
#:
#: The trained instruction asks the model to *describe* the code, and 99.97% of
#: the explanation targets follow a fixed Purpose/Input/Output/Algorithm form
#: with no slot for "this is broken" - so the model reliably never says it.
#: These sentences give it one.
#:
#: Measured on the phase-2 checkpoint over the same 24 programs, against the
#: trained wording as control (`model_improvement/step3_prompt/`):
#:
#:     problems named                  8/55 -> 16/55
#:     defects invented in correct code    1 -> 0
#:     anchors kept                    95/95 -> 100/100
#:
#: Better on 5 samples and worse on none, McNemar p = 0.0625. The middle row is
#: the one that licenses the change: correct code is the product's normal input,
#: so a phrasing that finds more defects by imagining them everywhere would be
#: worse than none. This one finds more and invents fewer.
DEFECT_AWARE_SUFFIX = (
    "This code may contain defects. Do not assume it is correct. Describe what "
    "each line actually does when executed, and where a line's effect differs "
    "from what the surrounding code appears intended to achieve, say so plainly."
)

#: Only the tasks the probe actually measured. `complexity` and `optimize` ask
#: for a different kind of answer and were never tested with this wording, so
#: they keep the trained instruction until they are.
DEFECT_AWARE_TASKS = frozenset({"line_comments", "explanation", "review"})


def format_prompt_without_response(
    code: str,
    output_fields: list[str],
    *,
    style: str,
    tokenizer: ChatTemplateTokenizer | None = None,
    language: str = "cpp",
    task: str | None = None,
    defect_aware: bool = True,
) -> str:
    """Render an inference prompt.

    Passing ``task`` asks for exactly that task's fields; omitting it keeps the
    configured ``output_fields``, which is what existing callers do.

    ``defect_aware`` appends :data:`DEFECT_AWARE_SUFFIX` for the describing
    tasks. It is inference-only and deliberately not part of the training
    render: the measurement above is of this wording given to a model trained
    *without* it. Pass ``defect_aware=False`` to reproduce the older prompt,
    which is what the control arm of any comparison needs.
    """
    example: dict[str, Any] = {"code": code, "language": language}
    if task is not None:
        example["task"] = task
    fields = resolve_output_fields(example, output_fields)
    instruction = build_instruction(example, fields)
    # Named tasks only. A caller that passes no task is asking for the
    # configured field list, which no arm of the probe covered, and silently
    # changing that would alter every existing caller on an untested basis.
    if defect_aware and task in DEFECT_AWARE_TASKS:
        instruction = f"{instruction}\n\n{DEFECT_AWARE_SUFFIX}"
    if style == "instruction":
        return f"### Instruction\n\n{instruction}\n\n### Code\n\n{code}\n\n### Response\n\n"
    if tokenizer is None:
        raise ValueError("A tokenizer is required for chat prompt formatting.")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
