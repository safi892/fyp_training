from __future__ import annotations

import random
import re
from typing import Iterable

CPP_KEYWORDS = {
    "auto",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "delete",
    "do",
    "double",
    "else",
    "enum",
    "false",
    "float",
    "for",
    "if",
    "inline",
    "int",
    "long",
    "namespace",
    "new",
    "nullptr",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "template",
    "this",
    "true",
    "typedef",
    "typename",
    "unsigned",
    "using",
    "virtual",
    "void",
    "while",
}

COMMON_NAMES = {
    "std",
    "cin",
    "cout",
    "cerr",
    "endl",
    "vector",
    "string",
    "map",
    "set",
    "queue",
    "stack",
    "deque",
    "pair",
    "max",
    "min",
    "sort",
    "swap",
    "main",
    "scanf",
    "printf",
}

BAD_NAMES = ["a", "b", "c", "x", "y", "z", "i", "j", "k", "n", "m", "f", "g", "tmp", "val"]
GOOD_NAMES = [
    "count",
    "index",
    "result",
    "current",
    "total",
    "limit",
    "value",
    "answer",
    "left",
    "right",
    "number",
    "is_valid",
    "position",
    "length",
]

TOKEN_RE = re.compile(
    r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|\b[A-Za-z_][A-Za-z0-9_]*\b",
    re.DOTALL,
)
DECL_RE = re.compile(
    r"\b(?:int|long|short|float|double|bool|char|string|auto|size_t|long\s+long|vector\s*<[^;(){}]+>)\s+([^;(){}]+)[;)]"
)
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def collect_declared_identifiers(code: str) -> list[str]:
    names: list[str] = []
    for declaration in DECL_RE.finditer(code):
        for name in IDENT_RE.findall(declaration.group(1)):
            if should_rename(name):
                names.append(name)
    return sorted(set(names), key=names.index)


def should_rename(name: str) -> bool:
    return name not in CPP_KEYWORDS and name not in COMMON_NAMES and not name.startswith("__")


def rename_identifiers(code: str, mapping: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith(("//", "/*", '"', "'")):
            return token
        return mapping.get(token, token)

    return TOKEN_RE.sub(replace, code)


def make_mapping(names: Iterable[str], pool: list[str], rng: random.Random) -> dict[str, str]:
    mapping: dict[str, str] = {}
    used = set(names)
    for index, name in enumerate(names):
        candidate = pool[index % len(pool)]
        if candidate in used:
            candidate = f"{candidate}_{index}"
        mapping[name] = candidate
        used.add(candidate)
    items = list(mapping.items())
    rng.shuffle(items)
    return dict(items)


def augment_row(row: dict, rng: random.Random) -> list[dict]:
    code = row.get("code")
    if not isinstance(code, str) or not code.strip():
        return [row]
    names = collect_declared_identifiers(code)
    if not names:
        return [row]

    variants = [row]
    for label, pool in [("bad_variable_names", BAD_NAMES), ("descriptive_variable_names", GOOD_NAMES)]:
        clone = dict(row)
        clone["code"] = rename_identifiers(code, make_mapping(names, pool, rng))
        clone["augmentation"] = label
        variants.append(clone)
    return variants
