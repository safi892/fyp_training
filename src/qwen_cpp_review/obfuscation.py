"""Rename identifiers to measure how much a model leans on names.

Identifier names are the easiest signal in source code, and a model can score
well on explanation tasks by reading them alone. Rewriting the names without
touching the structure separates the two: whatever survives is understanding of
the code, and whatever is lost was name-reading.

The strategies follow *When Names Disappear* (arXiv 2510.03178), which found
GPT-4o dropping from 87.3% to 58.7% on class-level summarisation under exactly
this treatment.

Renaming reuses the regex identifier pass from
:mod:`qwen_cpp_review.identifier_augmentation`. That pass is scope-blind, which
is acceptable for the short, single-function samples used for evaluation and is
the reason the eval set is curated rather than drawn at random.
"""

from __future__ import annotations

import random
import re

from qwen_cpp_review.identifier_augmentation import (
    CPP_KEYWORDS,
    collect_declared_identifiers,
    make_mapping,
    rename_identifiers,
)

#: A function name is usually the loudest hint in a snippet - `countDigits`
#: states the answer outright - so an evaluation that leaves it alone is not
#: measuring what it claims to. The declaration pass in
#: `identifier_augmentation` only finds variables, so function names are
#: collected separately here.
FUNCTION_RE = re.compile(
    r"\b(?:int|long|short|float|double|bool|char|void|string|auto|size_t)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*\(",
)

#: Renaming these would change what the program does, or read as nonsense.
PROTECTED_FUNCTIONS = {"main", "printf", "scanf", "malloc", "free", "sizeof"}

#: The declaration pass in `identifier_augmentation` cannot see a name whose
#: initialiser contains brackets - `int probe = low + (high - low) / 2;` - so
#: that name would keep its meaning through an obfuscation and quietly make the
#: model look more robust than it is. This catches the declaration directly.
DECLARED_RE = re.compile(
    r"\b(?:int|long|short|float|double|bool|char|void|string|auto|size_t|unsigned)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;|\[|,|\)|$)",
    re.MULTILINE,
)

#: Placeholder names carrying no meaning at all.
ALPHA_NAMES = [f"var{index}" for index in range(1, 21)]

#: Visually confusing names built from characters that are hard to tell apart.
#: These are still valid identifiers, so the code compiles unchanged.
NOISE_NAMES = [
    "lllIII", "IllIlI", "l1lIl1", "O0OoO0", "oO0Oo0", "II1lI1", "ll1I1l",
    "O0o0O0", "l1I1l1", "IlIlIl", "o0Oo0O", "lI1Il1",
    "OOO000", "iIiIiI", "jJjJjJ", "xXxXxX", "zZzZzZ", "qQqQqQ", "wWwWwW", "vVvVvV",
]

#: Short, uninformative names of the kind a hurried programmer writes.
TERSE_NAMES = ["a", "b", "c", "d", "e", "x", "y", "z", "n", "m", "p", "q", "t", "u", "v"]

#: Names that actively suggest the wrong behaviour. The most diagnostic case:
#: a model reading names rather than code will follow these into a wrong answer.
MISLEADING_NAMES = [
    "product", "average", "maximum", "minimum", "sorted_list", "is_prime",
    "buffer_size", "error_code", "timestamp", "hash_value", "file_handle",
    "temperature", "row_count", "checksum", "port_number", "retry_limit",
    "user_name", "byte_offset", "pixel_depth", "queue_head",
]

#: Ordinary, descriptive names - the control condition.
CLEAR_NAMES = [
    "total", "count", "index", "result", "current", "limit", "value", "buffer",
    "position", "length", "target", "source", "remainder", "accumulator",
    "candidate", "boundary", "counter", "element", "capacity", "offset",
]

STRATEGIES = {
    "original": None,
    "terse": TERSE_NAMES,
    "alpha": ALPHA_NAMES,
    "noise": NOISE_NAMES,
    "misleading": MISLEADING_NAMES,
    "clear": CLEAR_NAMES,
}


def collect_function_names(code: str) -> list[str]:
    """Function names defined in ``code``, excluding names that must not move."""
    found = [
        name
        for name in FUNCTION_RE.findall(code)
        if name not in CPP_KEYWORDS and name not in PROTECTED_FUNCTIONS
    ]
    return sorted(set(found), key=found.index)


def renameable(code: str) -> list[str]:
    """Every identifier an obfuscation may touch: variables and function names.

    Three passes are unioned because each misses cases the others catch, and a
    name left behind is a name the model can still read.
    """
    names = collect_function_names(code)
    for candidate in DECLARED_RE.findall(code) + collect_declared_identifiers(code):
        if (
            candidate not in names
            and candidate not in CPP_KEYWORDS
            and candidate not in PROTECTED_FUNCTIONS
        ):
            names.append(candidate)
    return names


def obfuscate(code: str, strategy: str, rng: random.Random) -> str:
    """Return ``code`` with its identifiers renamed by ``strategy``.

    ``original`` returns the input untouched, so it can be used as the control
    without special-casing at the call site.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; known: {sorted(STRATEGIES)}")
    pool = STRATEGIES[strategy]
    if pool is None:
        return code
    names = renameable(code)
    if not names:
        return code
    return rename_identifiers(code, make_mapping(names, list(pool), rng))


def mixed(code: str, rng: random.Random, clear_share: float = 0.5) -> str:
    """Rename some identifiers clearly and the rest to noise.

    The realistic middle case: part of a file is well named and part is not,
    so a model cannot rely on names being uniformly helpful or uniformly absent.
    """
    names = renameable(code)
    if not names:
        return code
    split = max(1, int(len(names) * clear_share))
    mapping: dict[str, str] = {}
    mapping.update(make_mapping(names[:split], list(CLEAR_NAMES), rng))
    mapping.update(make_mapping(names[split:], list(NOISE_NAMES), rng))
    return rename_identifiers(code, mapping)
