"""Reject prose that contradicts the code it is describing.

The anchoring design already makes one kind of invented output detectable: a
comment quoting a line that is not in the file is dropped, because the quote can
be checked. This is the same move applied to the prose itself.

It cannot check whether an explanation is *good*. It checks a small set of
claims that the code answers directly, and it only ever fires when the code and
the prose disagree:

    "recursively sorts the sub-arrays"     over a function that never calls itself
    "BFS queue for flood-filling"          over a `std::stack` declaration
    "uses a hash map"                      over code containing no map

Every one of those was produced by the model on real input. None of them is a
matter of taste, and none needs a human to adjudicate.

What it deliberately does not do is guess. A claim only counts as false when the
opposite is established from the source - a description that is merely vague,
incomplete or badly written passes, because there is no way to be sure it is
wrong, and a checker that fires on uncertainty stops being evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

#: Comments are stripped before the code is read, or a complexity note like
#: `//S.C : O(26)` parses as a function `O(26){...}` whose body calls `O(n)`,
#: and a file with no recursion in it is read as recursive.
_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)

_FUNCTION = re.compile(r"(\w+)\s*\(([^;{}]*)\)\s*(?:const\s*)?\{")
_LAMBDA = re.compile(r"\b(\w+)\s*=\s*\[[^\]]*\]")

#: Words that open a block but are not calls.
_NOT_CALLS = frozenset({"if", "for", "while", "switch", "catch", "return", "sizeof", "main"})

#: A claim that this code calls itself. `recursi\w*` rather than `recursiv\w*`
#: because the noun is "recursion"; `call(s|ing)? itself` because the participle
#: is as common as the verb. A closed list of verbs reports whatever it forgot as
#: a pass, which is the direction this project's scoring has been wrong before.
MENTIONS_RECURSION = re.compile(r"\b(?:call(?:s|ing)? itself|recursi\w*)\b", re.I)

#: Wording that turns a mention of recursion into a description of what was
#: replaced. "Uses a stack instead of recursion" is correct prose about a loop.
DESCRIBES_REMOVAL = re.compile(
    r"\b(?:instead of|rather than|replac\w+|convert\w+|no longer|avoid\w*|without|"
    r"eliminat\w+|remov\w+|simulat\w+|mimic\w+|emulat\w+|iterativ\w*)\b",
    re.I,
)

#: Structures whose presence in the source is unambiguous, paired with the word
#: the prose uses for them. The declaration needs the angle bracket - `stack<T>` -
#: while the prose never has one, so the two spellings cannot share a pattern.
STRUCTURES = {
    "stack": (re.compile(r"\bstack\s*<"), re.compile(r"\bstacks?\b", re.I)),
    "queue": (re.compile(r"\bqueue\s*<"), re.compile(r"\bqueues?\b", re.I)),
    "hash map": (
        re.compile(r"\b(?:unordered_map|unordered_set)\s*<"),
        re.compile(r"\bhash (?:map|table|set)\b", re.I),
    ),
}

#: `recursion` as a bare concept is excluded from the structure list on purpose:
#: the call stack is not declared, so its absence cannot be read off the source
#: the way a `std::stack` can.

#: "stack overflow", "call stack", "stack frame" - the runtime stack, which no
#: program declares. Firing on these rejected a correct sentence about a
#: recursive function's memory cost.
_CALL_STACK = re.compile(
    r"\b(?:call|runtime|system|program)\s+stack\b|\bstack\s+(?:overflow|frame|depth|space|usage|memory)\b",
    re.I,
)

#: Text the model is quoting rather than asserting. A program that prints
#: "I love Recursion" makes `Prints the phrase "I love Recursion" n times` a
#: correct description of a loop, and the word inside the quotes is not a claim.
_QUOTED = re.compile(r"\"[^\"]*\"|\u201c[^\u201d]*\u201d|'[^']{2,}'|`[^`]*`")

#: A claim that the code tests one number against another.
#:
#: Every word here had to survive the corpus rather than only look right.
#: `divide` is excluded because "divide the array into two halves" is about
#: partitioning; `multiple of` needs a digit after it so "a multiple of the base
#: case" passes; and **`remainder` was removed after firing on "recursively
#: reverses the remainder"** - the rest of a stack, not a modulo. That is the
#: same two-meanings mistake as reading "stack overflow" as a `std::stack`, and
#: it was a correct sentence about correct code.
CLAIMS_DIVISIBILITY = re.compile(
    # `\d+` rather than `\d`: the trailing word boundary after a single digit
    # falls inside "10" and the whole alternative silently never matches.
    r"\b(?:divisib\w+|modulo|multiple of\s+\d+|"
    r"(?:even|odd)\s+(?:number|value|element|count)s?)\b",
    re.I,
)

#: The operators that can decide divisibility. `& 1` is the idiomatic parity
#: test and is not spelled with a percent sign, so looking only for `%` would
#: report correct prose about `if (n & 1)` as false.
_TESTS_DIVISIBILITY = re.compile(r"%|&\s*1\b")


@dataclass
class Claim:
    """One disagreement between the prose and the code, with the sentence."""

    kind: str
    sentence: str


@dataclass
class ClaimReport:
    contradictions: list[Claim] = field(default_factory=list)
    #: Structures the source declares, for a caller that wants to say what was checked.
    structures: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.contradictions


def strip_comments(code: str) -> str:
    return _COMMENT.sub(" ", code)


def _block(text: str, start: int) -> str:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    return text[start:]


def recursive_functions(code: str) -> list[str]:
    """Names of functions in ``code`` that call themselves, lambdas included."""
    code = strip_comments(code)
    found = []
    for match in _FUNCTION.finditer(code):
        name = match.group(1)
        if name in _NOT_CALLS:
            continue
        if re.search(rf"\b{re.escape(name)}\s*\(", _block(code, match.end() - 1)):
            found.append(name)
    for match in _LAMBDA.finditer(code):
        name = match.group(1)
        brace = code.find("{", match.end())
        if brace != -1 and re.search(rf"\b{re.escape(name)}\s*\(", _block(code, brace)):
            found.append(name)
    return sorted(set(found))


def _unquoted(sentence: str) -> str:
    """The sentence with quoted spans blanked, so a quotation is not read as a claim."""
    return _QUOTED.sub(" ", sentence)


def sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n", text) if part.strip()]


def check_claims(code: str, prose: str) -> ClaimReport:
    """Every sentence of ``prose`` the source contradicts."""
    report = ClaimReport()
    if not code.strip() or not prose.strip():
        return report

    bare = strip_comments(code)
    report.structures = sorted(
        name for name, (in_code, _) in STRUCTURES.items() if in_code.search(bare)
    )

    recurses = bool(recursive_functions(code))
    # One `%` anywhere in the file is enough to let every divisibility claim
    # pass. That is deliberate: the check exists to catch a purpose invented out
    # of nothing - `sum_digits_tree` accumulating `carried * 10 + value` and
    # being described as counting paths "divisible by 10" - not to police which
    # line the operator sits on.
    tests_divisibility = bool(_TESTS_DIVISIBILITY.search(bare))
    for sentence in sentences(prose):
        claim = _unquoted(sentence)
        if not recurses and MENTIONS_RECURSION.search(claim):
            if not DESCRIBES_REMOVAL.search(claim):
                report.contradictions.append(Claim("recursion", sentence))
        if not tests_divisibility and CLAIMS_DIVISIBILITY.search(claim):
            report.contradictions.append(Claim("no divisibility test in the code", sentence))
        for name, (in_code, in_prose) in STRUCTURES.items():
            if name in report.structures:
                continue
            text = _CALL_STACK.sub(" ", claim) if name == "stack" else claim
            if in_prose.search(text):
                report.contradictions.append(Claim(f"no {name} in the code", sentence))
    return report


def filter_comments(
    code: str, comments: list[dict[str, object]]
) -> tuple[list[dict[str, object]], list[Claim]]:
    """Drop comments the line they are attached to contradicts.

    Checked against the single quoted line rather than the whole file, because a
    comment describes that line. `// BFS queue for flood-filling` on
    ``stack<pair<int,int>> pending;`` is wrong even though the file elsewhere is
    a legitimate depth-first search.
    """
    kept, dropped = [], []
    for item in comments:
        line = str(item.get("code", ""))
        note = str(item.get("comment", ""))
        if not line.strip() or not note.strip():
            kept.append(item)
            continue
        # Only the structure claims apply per line: whether the *file* recurses
        # cannot be read off one line of it.
        declared = {name for name, (in_code, _) in STRUCTURES.items() if in_code.search(line)}
        claim = _CALL_STACK.sub(" ", _unquoted(note))
        conflict = next(
            (
                name
                for name, (in_code, in_prose) in STRUCTURES.items()
                if in_prose.search(claim) and declared and name not in declared
            ),
            None,
        )
        if conflict:
            dropped.append(Claim(f"line declares {sorted(declared)[0]}, comment says {conflict}", note))
        else:
            kept.append(item)
    return kept, dropped


#: Loop nodes tree-sitter reports for C++. `for_range_loop` is the range-for.
_LOOP_NODES = {"for_statement", "while_statement", "do_statement", "for_range_loop"}

#: The nesting depth a label needs before plain loops could produce it. Labels
#: absent here are not checked: `O(n log n)` comes from an algorithm rather than
#: from nesting, so counting loops says nothing about whether it is right.
_DEPTH_REQUIRED = {
    "O(n²)": 2, "O(n^2)": 2,
    "O(n³)": 3, "O(n^3)": 3,
    "O(n² log n)": 2, "O(n²log n)": 2,
}


def max_loop_depth(code: str) -> int:
    """Deepest nesting of loops in ``code``, or 0 if it does not parse."""
    try:
        import tree_sitter_cpp
        from tree_sitter import Language, Parser
    except ImportError:  # pragma: no cover - depends on the install
        return 0
    root = Parser(Language(tree_sitter_cpp.language())).parse(code.encode()).root_node
    best = 0

    def walk(node: Any, depth: int) -> None:
        nonlocal best
        here = depth + (1 if node.type in _LOOP_NODES else 0)
        best = max(best, here)
        for child in node.children:
            walk(child, here)

    walk(root, 0)
    return best


def complexity_contradicted(code: str, time_label: str | None) -> bool:
    """Is this time complexity impossible for the structure that is written?

    A necessary condition, never a sufficient one. Three nested loops do not
    prove `O(n³)` - they may run over constants, or over three different
    sizes - but *fewer than three* means plain loops cannot produce it, and
    recursion is the only remaining way. So this returns True only when the
    depth falls short **and** nothing recurses.

    Measured over the 1,293 rows the corpus labels `O(n³)` or `O(n² log n)`:

        depth sufficient                              288  (22.3%)
        depth short but recursive, cannot rule out     56  ( 4.3%)
        depth short and not recursive, contradicted   949  (73.4%)

    That 73.4% is why those labels were distrusted, and the 22.3% is why
    distrusting them by name was the wrong instrument: it deleted every
    `O(n³)` row, so the adapter could not emit the label even where it is right.
    """
    required = _DEPTH_REQUIRED.get((time_label or "").strip())
    if required is None:
        return False
    if max_loop_depth(code) >= required:
        return False
    return not recursive_functions(code)


def complexity_corroborated(code: str, time_label: str | None) -> bool:
    """Does the written nesting positively support this time complexity?

    The mirror of :func:`complexity_contradicted`, and used for a different
    purpose: not to distrust a label, but to restore one the annotator itself
    was unsure of. Only labels whose mechanism *is* nesting are answerable this
    way - `O(n log n)` and `O(1)` come from an algorithm, so loop depth has
    nothing to say about them and this returns False rather than guessing.

    The corpus labels 1,602 functions `O(n²)`, of which 1,510 carry
    `low_complexity_confidence` and so never reach training - leaving 92. Of
    those 1,510, **624 are written with two or more nested loops**. Low
    annotator confidence is a real signal and is kept everywhere else; where the
    code visibly does the thing the label says, it is corroboration the
    annotator did not have.
    """
    required = _DEPTH_REQUIRED.get((time_label or "").strip())
    if required is None:
        return False
    return max_loop_depth(code) >= required
