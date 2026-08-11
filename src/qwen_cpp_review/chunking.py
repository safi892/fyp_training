"""Split a C++ file into pieces the model can actually answer about, and put
the answers back together.

The model was trained on function-sized inputs, and a 300-line file is neither
something it has seen nor something that fits the sequence length. Splitting at
syntax boundaries keeps every chunk a complete unit, so a comment is never
written about half a function.

Chunks are line ranges rather than extracted text: every line of the file
belongs to exactly one chunk, and a chunk's first line number is its offset
into the file. That makes the mapping back to file coordinates exact instead of
reconstructed, which is what lets an anchor still be checked against the
original file after stitching.

Follows the split-then-merge shape of cAST (arXiv 2506.15655): split on
structure, then merge neighbours up to a budget so a file of one-line functions
does not become a hundred requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from qwen_cpp_review.line_anchoring import Anchor, repair_anchors

#: Node types that stand on their own and must never be split.
UNIT_TYPES = {
    "function_definition",
    "class_specifier",
    "struct_specifier",
    "namespace_definition",
    "template_declaration",
    "enum_specifier",
    "union_specifier",
}

#: Roughly the ratio the Qwen tokenizer achieves on C++. Only used when no real
#: tokenizer is supplied, to keep this module importable without one.
CHARS_PER_TOKEN = 3.2


@dataclass(frozen=True)
class Chunk:
    """A contiguous run of lines, 1-based and inclusive at both ends."""

    start_line: int
    end_line: int
    text: str
    kind: str
    #: True when a single indivisible unit is already over budget. Splitting it
    #: would break a function in half, so it is passed through whole and the
    #: caller can decide.
    oversized: bool = False

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def _parser() -> Any:
    try:
        import tree_sitter_cpp
        from tree_sitter import Language, Parser
    except ImportError as exc:  # pragma: no cover - depends on the install
        raise RuntimeError(
            "chunking needs tree-sitter; install with `uv pip install tree-sitter tree-sitter-cpp`"
        ) from exc
    return Parser(Language(tree_sitter_cpp.language()))


def _select_units(node: Any, lines: list[str], max_tokens: int, count_tokens: Callable[[str], int]):
    """Yield the outermost units that fit the budget, descending when they do not.

    A class that fits is one unit; a class that does not is descended into so
    its methods become units of their own. That is the ``split`` half of
    split-then-merge, and it is what stops a large class from arriving as a
    single oversized chunk.
    """
    for child in node.children:
        start, end = child.start_point[0] + 1, child.end_point[0] + 1
        if child.type in UNIT_TYPES:
            body = "\n".join(lines[start - 1 : end])
            if count_tokens(body) <= max_tokens:
                yield start, end, child.type
                continue
            inner = list(_select_units(child, lines, max_tokens, count_tokens))
            if inner:
                yield from inner
            else:
                yield start, end, child.type  # indivisible and over budget
        else:
            # Not a unit itself, but may contain them - a class body, a
            # namespace block, a template wrapper.
            yield from _select_units(child, lines, max_tokens, count_tokens)


def unit_boundaries(
    code: str,
    *,
    max_tokens: int = 10**9,
    count_tokens: Callable[[str], int] = estimate_tokens,
) -> list[tuple[int, int, str]]:
    """Line ranges covering the whole file, in order, with no gaps or overlaps.

    Anything between two units - includes, blank lines, stray comments -
    becomes its own ``filler`` range, so the ranges tile the file and nothing is
    silently dropped.
    """
    lines = code.split("\n")
    tree = _parser().parse(code.encode("utf-8"))
    units = sorted(_select_units(tree.root_node, lines, max_tokens, count_tokens))

    ranges: list[tuple[int, int, str]] = []
    cursor = 1
    for start, end, kind in units:
        if start > cursor:
            ranges.append((cursor, start - 1, "filler"))
        start = max(start, cursor)
        if end >= start:
            ranges.append((start, end, kind))
            cursor = end + 1
    if cursor <= len(lines):
        ranges.append((cursor, len(lines), "filler"))
    return ranges


def chunk_code(
    code: str,
    *,
    max_tokens: int = 300,
    merge_below: int | None = None,
    count_tokens: Callable[[str], int] = estimate_tokens,
) -> list[Chunk]:
    """Split ``code`` into chunks on syntax boundaries.

    ``max_tokens`` is the ceiling a chunk may not cross. ``merge_below`` is the
    much lower size under which neighbours are combined, defaulting to a third
    of the ceiling.

    The two thresholds are separate on purpose. Merging everything up to the
    ceiling would hand the model 100-line chunks, when it was trained on
    functions of roughly fifteen lines and answers those best. So a real
    function is left as its own chunk, and merging only rescues the scraps -
    includes, a stray comment, a one-line accessor - from becoming requests of
    their own.
    """
    if merge_below is None:
        merge_below = max(1, max_tokens // 3)
    lines = code.split("\n")

    def text_of(start: int, end: int) -> str:
        return "\n".join(lines[start - 1 : end])

    chunks: list[Chunk] = []
    pending: list[tuple[int, int, str]] = []

    def flush() -> None:
        if not pending:
            return
        start, end = pending[0][0], pending[-1][1]
        kinds = [kind for _, _, kind in pending if kind != "filler"]
        chunks.append(
            Chunk(
                start_line=start,
                end_line=end,
                text=text_of(start, end),
                kind=kinds[0] if len(set(kinds)) == 1 else ("mixed" if kinds else "filler"),
            )
        )
        pending.clear()

    for start, end, kind in unit_boundaries(code, max_tokens=max_tokens, count_tokens=count_tokens):
        body = text_of(start, end)
        size = count_tokens(body)

        if size > max_tokens:
            # Indivisible and over budget: emit alone rather than cut a function.
            flush()
            chunks.append(Chunk(start_line=start, end_line=end, text=body, kind=kind, oversized=True))
            continue

        if pending:
            combined = count_tokens(text_of(pending[0][0], end))
            # Keep accumulating only while the result stays small. A chunk that
            # has already reached a useful size is better left alone.
            if combined > merge_below or combined > max_tokens:
                flush()
        pending.append((start, end, kind))

    flush()
    return [chunk for chunk in chunks if chunk.text.strip()]


def stitch(code: str, results: Iterable[tuple[Chunk, list[dict[str, Any]]]]) -> list[Anchor]:
    """Turn per-chunk model output into anchors in whole-file coordinates.

    Each chunk's anchors are first repaired *within that chunk*, because the
    model's line numbers are unreliable but its quoted code is not, then
    shifted by the chunk's offset. Repairing before shifting matters: a quote
    is searched for in the chunk the model actually saw, not across the file,
    so a line that appears in several functions cannot attract a comment
    written about a different one.

    A line already carrying a comment is not given a second one, so overlapping
    chunks cannot produce duplicates.
    """
    anchors: list[Anchor] = []
    claimed: set[int] = set()
    for chunk, raw in results:
        report = repair_anchors(chunk.text, raw)
        for anchor in report.anchors:
            line = anchor.line + chunk.start_line - 1
            if line in claimed:
                continue
            claimed.add(line)
            anchors.append(Anchor(line=line, code=anchor.code, comment=anchor.comment))
    anchors.sort(key=lambda anchor: anchor.line)
    return validate(code, anchors)


def validate(code: str, anchors: Iterable[Anchor]) -> list[Anchor]:
    """Keep only anchors whose quoted text matches that line of ``code``.

    The last gate before output: whatever survives here is checkable against
    the user's file, which is the guarantee the whole line-anchored format
    exists to provide.
    """
    lines = [line.strip() for line in code.split("\n")]
    return [
        anchor
        for anchor in anchors
        if 1 <= anchor.line <= len(lines) and lines[anchor.line - 1] == anchor.code.strip()
    ]
