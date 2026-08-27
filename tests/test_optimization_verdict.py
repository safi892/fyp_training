"""A table the sample already had is not a table the rewrite introduced.

`binary_search` takes a parameter named `table`, and the verdict scanned the
rewrite alone - so a textbook iterative binary search was reported as
TABULATED and scored zero against wants=("ITERATIVE",). The sample could not
pass whatever the model wrote. Same shape as the keyword-in-a-comment mistake
already recorded in CLAUDE.md: a name matched where a concept was meant.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("po", ROOT / "scripts" / "probe_optimization.py")
po = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(po)

BINARY_SEARCH = (
    "int search(const int* table, int low, int high, int wanted)\n"
    "{\n"
    "  if (low > high) return -1;\n"
    "  int probe = low + (high - low) / 2;\n"
    "  if (table[probe] == wanted) return probe;\n"
    "  return search(table, probe + 1, high, wanted);\n"
    "}"
)
ITERATIVE_SEARCH = (
    "int search(const int* table, int low, int high, int wanted)\n"
    "{\n"
    "  while (low <= high) {\n"
    "    int mid = low + (high - low) / 2;\n"
    "    if (table[mid] == wanted) return mid;\n"
    "    if (table[mid] < wanted) low = mid + 1; else high = mid - 1;\n"
    "  }\n"
    "  return -1;\n"
    "}"
)
FIB = "int fib(int n)\n{\n  if (n <= 1) return n;\n  return fib(n-1) + fib(n-2);\n}"


def test_inherited_table_name_does_not_make_a_loop_tabulated():
    verdict, _ = po.classify(BINARY_SEARCH, ITERATIVE_SEARCH)
    assert verdict.startswith("ITERATIVE"), verdict


def test_a_genuinely_new_table_is_still_reported():
    memoised = (
        "int fib(int n)\n{\n  static std::vector<int> memo(100, -1);\n"
        "  if (n <= 1) return n;\n  if (memo[n] != -1) return memo[n];\n"
        "  return memo[n] = fib(n-1) + fib(n-2);\n}"
    )
    verdict, _ = po.classify(FIB, memoised)
    assert verdict.startswith("MEMOISED"), verdict


def test_bottom_up_table_is_still_reported():
    tabulated = (
        "int fib(int n)\n{\n  std::vector<int> dp(n+1);\n  dp[0]=0; dp[1]=1;\n"
        "  for (int i=2;i<=n;++i) dp[i]=dp[i-1]+dp[i-2];\n  return dp[n];\n}"
    )
    verdict, _ = po.classify(FIB, tabulated)
    assert verdict.startswith("TABULATED"), verdict


def test_an_unchanged_recursive_answer_is_not_credited():
    verdict, _ = po.classify(FIB, FIB)
    assert verdict == "unchanged algorithm", verdict
