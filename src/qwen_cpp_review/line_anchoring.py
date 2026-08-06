"""Convert free-form annotated code into line-anchored comments.

The ``comments`` field in the raw dataset holds a *rewritten* copy of the source
with inline comments attached. That copy frequently drifts from the input: it
adds includes, reformats statements, and rewrites expressions. A model trained
on it learns to silently edit the user's file while claiming to explain it.

This module realigns those comments onto the original source lines. Every
anchor it emits carries the line number and the *original* line text, so a
downstream consumer can verify an anchor against the input instead of trusting
the model to reproduce the file.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from typing import Any, Iterator

FENCE_RE = re.compile(r"^\s*```[A-Za-z+#]*\s*$")
WHITESPACE_RE = re.compile(r"\s+")

#: Lines that carry no meaning on their own. They still take part in the
#: alignment so surrounding context lines up, but they are not counted when
#: scoring how well the annotated copy matches the original.
TRIVIAL_LINES = {"", "{", "}", "};", "{}", "(", ")", "else", "else {", "} else {"}


@dataclass(frozen=True)
class Anchor:
    """A comment bound to one line of the original source."""

    line: int
    code: str
    comment: str

    def to_dict(self) -> dict[str, Any]:
        return {"line": self.line, "code": self.code, "comment": self.comment}


@dataclass
class AnchorResult:
    """Anchors plus the evidence needed to decide whether to keep the row."""

    anchors: list[Anchor] = field(default_factory=list)
    #: Substantive annotated lines that matched an original line, over all
    #: substantive annotated lines. Low values mean the annotated copy is a
    #: rewrite rather than the input.
    match_ratio: float = 0.0
    #: Substantive original lines that received a comment, over all substantive
    #: original lines.
    coverage: float = 0.0
    #: Comments discarded because they sat on a line that is not in the input.
    dropped: int = 0

    @property
    def anchored(self) -> int:
        return len(self.anchors)


@dataclass
class _AnnotatedLine:
    """One line of the annotated copy, split into code and comment."""

    code: str
    normalized: str
    comment: str


def strip_code_fence(text: str) -> str:
    """Drop a leading/trailing markdown fence, keeping the body intact."""
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and FENCE_RE.match(lines[0]):
        lines.pop(0)
        if lines and FENCE_RE.match(lines[-1]):
            lines.pop()
    return "\n".join(lines)


def split_line(line: str, in_block: bool) -> tuple[str, str, bool]:
    """Split one C++ line into ``(code, comment, still_in_block_comment)``.

    String and character literals are tracked so that a ``//`` inside
    ``"http://..."`` is not mistaken for a comment.
    """
    code: list[str] = []
    comment: list[str] = []
    index = 0
    length = len(line)
    in_string = False
    in_char = False

    while index < length:
        char = line[index]
        pair = line[index : index + 2]

        if in_block:
            if pair == "*/":
                in_block = False
                index += 2
                continue
            comment.append(char)
            index += 1
            continue

        if in_string or in_char:
            code.append(char)
            if char == "\\" and index + 1 < length:
                code.append(line[index + 1])
                index += 2
                continue
            if in_string and char == '"':
                in_string = False
            elif in_char and char == "'":
                in_char = False
            index += 1
            continue

        if char == '"':
            in_string = True
            code.append(char)
            index += 1
            continue
        if char == "'":
            in_char = True
            code.append(char)
            index += 1
            continue
        if pair == "//":
            comment.append(line[index + 2 :])
            index = length
            continue
        if pair == "/*":
            in_block = True
            index += 2
            continue

        code.append(char)
        index += 1

    return "".join(code).rstrip(), "".join(comment).strip(), in_block


def normalize(line: str) -> str:
    """Collapse formatting differences that do not change meaning."""
    return WHITESPACE_RE.sub(" ", line).strip()


def is_substantive(normalized: str) -> bool:
    return normalized not in TRIVIAL_LINES


def parse_annotated(comments: str) -> list[_AnnotatedLine]:
    """Parse the annotated copy, folding standalone comments onto the next line.

    A comment on its own line describes the statement that follows it, so it is
    held back and attached to the next line that carries code.
    """
    parsed: list[_AnnotatedLine] = []
    pending: list[str] = []
    in_block = False

    for raw in strip_code_fence(comments).split("\n"):
        code, comment, in_block = split_line(raw, in_block)
        if not code.strip():
            if comment:
                pending.append(comment)
            continue
        merged = " ".join([*pending, comment]) if pending else comment
        pending.clear()
        parsed.append(_AnnotatedLine(code=code, normalized=normalize(code), comment=merged.strip()))

    return parsed


def _original_lines(code: str) -> list[tuple[int, str, str]]:
    """Yield ``(line_number, raw_text, normalized)`` for the input source."""
    result = []
    in_block = False
    for number, raw in enumerate(code.split("\n"), start=1):
        stripped, _, in_block = split_line(raw, in_block)
        result.append((number, raw.strip(), normalize(stripped)))
    return result


def _matched_pairs(
    original: list[tuple[int, str, str]],
    annotated: list[_AnnotatedLine],
) -> Iterator[tuple[int, int]]:
    """Align the two line sequences, yielding ``(original_idx, annotated_idx)``."""
    matcher = difflib.SequenceMatcher(
        a=[item[2] for item in original],
        b=[item.normalized for item in annotated],
        autojunk=False,
    )
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            yield block.a + offset, block.b + offset


def anchor_comments(code: str, comments: str) -> AnchorResult:
    """Bind each comment in ``comments`` to a line of ``code``.

    Comments attached to lines the annotator invented are dropped, and reported
    through :attr:`AnchorResult.dropped`.
    """
    if not code.strip() or not comments.strip():
        return AnchorResult()

    original = _original_lines(code)
    annotated = parse_annotated(comments)
    if not annotated:
        return AnchorResult()

    substantive_annotated = sum(1 for item in annotated if is_substantive(item.normalized))
    substantive_original = sum(1 for _, _, norm in original if is_substantive(norm))

    matched_annotated: set[int] = set()
    anchors: list[Anchor] = []
    for original_index, annotated_index in _matched_pairs(original, annotated):
        entry = annotated[annotated_index]
        if is_substantive(entry.normalized):
            matched_annotated.add(annotated_index)
        if not entry.comment:
            continue
        number, raw, _ = original[original_index]
        anchors.append(Anchor(line=number, code=raw, comment=entry.comment))

    dropped = sum(
        1
        for index, entry in enumerate(annotated)
        if entry.comment and index not in matched_annotated and is_substantive(entry.normalized)
    )

    anchored_lines = {anchor.line for anchor in anchors}
    return AnchorResult(
        anchors=anchors,
        match_ratio=len(matched_annotated) / substantive_annotated if substantive_annotated else 0.0,
        coverage=len(anchored_lines) / substantive_original if substantive_original else 0.0,
        dropped=dropped,
    )
