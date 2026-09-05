"""Choose the optimization prompt from the recursive shape of the code."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from qwen_cpp_review.claim_checks import recursive_functions, strip_comments

OptimizationTask = Literal["optimize", "iterate"]


@dataclass(frozen=True)
class RecursionProfile:
    """Small structural summary used to route optimization prompts."""

    functions: tuple[str, ...]
    max_self_calls: int
    max_self_calls_in_return: int
    task: OptimizationTask
    reason: str

    @property
    def recursive(self) -> bool:
        return bool(self.functions)


def classify_recursion(code: str) -> RecursionProfile:
    """Classify recursion as DP-shaped or direct-recursive.

    A return expression with two self-calls is the important signal for
    overlapping recursion, for example ``fib(n - 1) + fib(n - 2)``. Multiple
    self-call sites in separate branches, such as recursive binary search, are
    still direct recursion and route to the iteration prompt.
    """
    names = tuple(recursive_functions(code))
    if not names:
        return RecursionProfile((), 0, 0, "optimize", "no self recursion detected")

    counts = _tree_sitter_counts(code, names) or _regex_counts(code, names)
    max_calls = max((calls for calls, _ in counts.values()), default=1)
    max_return_calls = max((returns for _, returns in counts.values()), default=0)

    if max_return_calls >= 2:
        return RecursionProfile(
            names, max_calls, max_return_calls, "optimize", "branching recursive return"
        )
    return RecursionProfile(names, max_calls, max_return_calls, "iterate", "direct recursion")


def select_optimization_task(code: str) -> OptimizationTask:
    """Return the prompt task that should be used for this code."""
    return classify_recursion(code).task


def _parser() -> Any | None:
    try:
        import tree_sitter_cpp
        from tree_sitter import Language, Parser
    except ImportError:  # pragma: no cover - project dependency, fallback exists
        return None
    return Parser(Language(tree_sitter_cpp.language()))


def _walk(node: Any):
    yield node
    for child in node.children:
        yield from _walk(child)


def _text(source: bytes, node: Any) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")


def _function_name(source: bytes, node: Any) -> str | None:
    header = _text(source, node).split("{", 1)[0]
    match = re.search(r"\b(?:~?\w+)\s*\(", header)
    if not match:
        return None
    name = match.group(0).split("(", 1)[0].strip()
    if name in {"if", "for", "while", "switch", "catch"}:
        return None
    return name


def _tree_sitter_counts(code: str, names: tuple[str, ...]) -> dict[str, tuple[int, int]]:
    parser = _parser()
    if parser is None:
        return {}

    source = code.encode("utf-8")
    root = parser.parse(source).root_node
    wanted = set(names)
    counts: dict[str, tuple[int, int]] = {}

    for function in (node for node in _walk(root) if node.type == "function_definition"):
        name = _function_name(source, function)
        if name not in wanted:
            continue
        body = next((child for child in function.children if child.type == "compound_statement"), None)
        if body is None:
            continue
        calls = _self_call_count(source, body, name)
        returns = max(
            (
                _self_call_count(source, node, name)
                for node in _walk(body)
                if node.type == "return_statement"
            ),
            default=0,
        )
        counts[name] = (calls, returns)
    return counts


def _self_call_count(source: bytes, node: Any, name: str) -> int:
    needle = re.compile(rf"\b{re.escape(name)}\s*\(")
    return sum(
        1
        for child in _walk(node)
        if child.type == "call_expression" and needle.match(_text(source, child))
    )


def _regex_counts(code: str, names: tuple[str, ...]) -> dict[str, tuple[int, int]]:
    bare = strip_comments(code)
    return {
        name: (
            len(re.findall(rf"\b{re.escape(name)}\s*\(", bare)) - 1,
            max(
                (
                    len(re.findall(rf"\b{re.escape(name)}\s*\(", line))
                    for line in bare.splitlines()
                    if "return" in line
                ),
                default=0,
            ),
        )
        for name in names
    }
