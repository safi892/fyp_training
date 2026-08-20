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
    for sentence in sentences(prose):
        claim = _unquoted(sentence)
        if not recurses and MENTIONS_RECURSION.search(claim):
            if not DESCRIBES_REMOVAL.search(claim):
                report.contradictions.append(Claim("recursion", sentence))
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
