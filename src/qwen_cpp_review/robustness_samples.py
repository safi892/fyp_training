"""Held-out C++ samples for the identifier-robustness evaluation.

These are written for this evaluation rather than drawn from the training
corpus, so a good score cannot come from having memorised the answer.

Each sample carries ``concepts``: groups of words, any one of which counts as
naming that idea. A correct explanation should hit most groups whatever the
identifiers are called, which makes the score comparable across renamings. The
words are deliberately chosen not to appear as identifiers in the source, so
the model cannot earn a point by echoing a name it was handed.
"""

from __future__ import annotations

from typing import Any

SAMPLES: list[dict[str, Any]] = [
    {
        "name": "digit_count",
        "difficulty": "easy",
        "code": (
            "int howMany(int first, int second)\n"
            "{\n"
            "  int total = first + second;\n"
            "  int tally = 0;\n"
            "  while (total != 0)\n"
            "  {\n"
            "    total /= 10;\n"
            "    tally++;\n"
            "  }\n"
            "  return tally;\n"
            "}"
        ),
        "concepts": [
            ["add", "sum", "addition", "adds", "adding", "plus"],
            ["digit", "digits"],
            ["divide", "division", "dividing", "divides", "/= 10", "by 10", "ten"],
            ["loop", "repeat", "iterate", "until", "keeps going"],
        ],
    },
    {
        "name": "reverse_in_place",
        "difficulty": "easy",
        "code": (
            "void reverseArray(int values[], int size)\n"
            "{\n"
            "  int left = 0;\n"
            "  int right = size - 1;\n"
            "  while (left < right)\n"
            "  {\n"
            "    int spare = values[left];\n"
            "    values[left] = values[right];\n"
            "    values[right] = spare;\n"
            "    left++;\n"
            "    right--;\n"
            "  }\n"
            "}"
        ),
        "concepts": [
            ["revers", "backward", "opposite order"],
            ["swap", "exchange", "swapping", "swaps"],
            ["two pointer", "both ends", "start and end", "inward", "towards each other", "toward each other"],
            ["temporary", "temp", "hold", "placeholder"],
        ],
    },
    {
        "name": "binary_search",
        "difficulty": "medium",
        "code": (
            "int findIndex(int table[], int length, int wanted)\n"
            "{\n"
            "  int low = 0;\n"
            "  int high = length - 1;\n"
            "  while (low <= high)\n"
            "  {\n"
            "    int probe = low + (high - low) / 2;\n"
            "    if (table[probe] == wanted)\n"
            "      return probe;\n"
            "    if (table[probe] < wanted)\n"
            "      low = probe + 1;\n"
            "    else\n"
            "      high = probe - 1;\n"
            "  }\n"
            "  return -1;\n"
            "}"
        ),
        "concepts": [
            ["binary search", "halv", "half", "divide and conquer", "bisect"],
            ["sorted", "ordered"],
            ["middle", "midpoint", "mid"],
            ["not found", "-1", "absent", "missing"],
        ],
    },
    {
        "name": "gcd_euclid",
        "difficulty": "medium",
        "code": (
            "int greatestCommon(int alpha, int beta)\n"
            "{\n"
            "  while (beta != 0)\n"
            "  {\n"
            "    int leftover = alpha % beta;\n"
            "    alpha = beta;\n"
            "    beta = leftover;\n"
            "  }\n"
            "  return alpha;\n"
            "}"
        ),
        "concepts": [
            ["greatest common", "gcd", "common divisor", "common factor", "hcf"],
            ["euclid", "remainder", "modul", "modulo", "%"],
            ["loop", "repeat", "iterate", "until", "keeps going"],
            ["zero", "0"],
        ],
    },
    {
        "name": "bubble_sort",
        "difficulty": "medium",
        "code": (
            "void arrange(int items[], int count)\n"
            "{\n"
            "  for (int stage = 0; stage < count - 1; stage++)\n"
            "  {\n"
            "    for (int scan = 0; scan < count - stage - 1; scan++)\n"
            "    {\n"
            "      if (items[scan] > items[scan + 1])\n"
            "      {\n"
            "        int keep = items[scan];\n"
            "        items[scan] = items[scan + 1];\n"
            "        items[scan + 1] = keep;\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}"
        ),
        "concepts": [
            ["sort", "sorting", "ascending", "order"],
            ["bubble", "adjacent", "neighbour", "neighbor", "next element", "pairs"],
            ["swap", "exchange", "swapping"],
            ["nested", "two loop", "inner", "outer"],
        ],
    },
    {
        "name": "matrix_transpose",
        "difficulty": "hard",
        "code": (
            "void rework(int grid[][100], int height, int width)\n"
            "{\n"
            "  for (int one = 0; one < height; one++)\n"
            "  {\n"
            "    for (int two = one + 1; two < width; two++)\n"
            "    {\n"
            "      int stash = grid[one][two];\n"
            "      grid[one][two] = grid[two][one];\n"
            "      grid[two][one] = stash;\n"
            "    }\n"
            "  }\n"
            "}"
        ),
        "concepts": [
            ["transpos", "flip", "mirror", "diagonal"],
            ["row", "rows"],
            ["column", "cols", "columns"],
            ["swap", "exchange", "in-place", "in place"],
        ],
    },
]
