"""Ask whether the model can already turn recursion into dynamic programming.

Before building a dataset for a capability, it is worth finding out whether the
model has it already and was only being asked badly. The trained `improve`
target was LLM-written and never executed, so it taught tidying rather than
algorithmic change - but the base model underneath has seen a great deal of
real C++, and the instruction may simply have been too vague.

Each recursive sample is sent with several phrasings, from the vague wording
the model was trained on to an explicit request for memoisation. The output is
classified by what it actually contains, not by whether it looks improved.

    uv run python scripts/probe_optimization.py --gguf models/gguf/qwen-cpp-review-q4_k_m.gguf

Runs against llama-server, so this takes minutes rather than hours.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from qwen_cpp_review.obfuscation import obfuscate

# Comments are stripped before any verdict is read: the model narrates what it
# is doing ("// cache next node") on code it did not change, and a keyword scan
# that sees the comment scores prose as a rewrite.
from verify_optimization_pairs import recursive_functions, strip_comments

#: Recursive functions with overlapping subproblems - the case where turning
#: recursion into a table changes the complexity class. Grid traversal and
#: backtracking are deliberately excluded: recursion is the right answer there,
#: and an explicit stack is worse code, not better.
SAMPLES = [
    {
        "name": "fibonacci",
        "kind": "table",
        "difficulty": "easy",
        "code": "int fib(int n)\n{\n  if (n <= 1)\n    return n;\n  return fib(n - 1) + fib(n - 2);\n}",
        "naive": "O(2^n)",
        "wants": ("MEMOISED", "TABULATED"),
    },
    {
        "name": "grid_paths",
        "kind": "table",
        "difficulty": "medium",
        "code": (
            "int paths(int rows, int cols)\n"
            "{\n"
            "  if (rows == 1 || cols == 1)\n"
            "    return 1;\n"
            "  return paths(rows - 1, cols) + paths(rows, cols - 1);\n"
            "}"
        ),
        "naive": "O(2^(n+m))",
        "wants": ("MEMOISED", "TABULATED"),
    },
    {
        "name": "coin_change",
        "kind": "table",
        "difficulty": "hard",
        "code": (
            "int ways(int coins[], int count, int amount)\n"
            "{\n"
            "  if (amount == 0)\n"
            "    return 1;\n"
            "  if (amount < 0 || count == 0)\n"
            "    return 0;\n"
            "  return ways(coins, count - 1, amount) + ways(coins, count, amount - coins[count - 1]);\n"
            "}"
        ),
        "naive": "O(2^n)",
        "wants": ("MEMOISED", "TABULATED"),
    },
    #: Linear recursion with no overlapping subproblems. A table would be
    #: pointless here - the win is losing the call stack, so the only correct
    #: rewrite is a loop, and "ITERATIVE (no table)" is the passing verdict.
    {
        "name": "factorial",
        "kind": "accumulator",
        "difficulty": "easy",
        "code": "long long fact(int n)\n{\n  if (n <= 1)\n    return 1;\n  return n * fact(n - 1);\n}",
        "naive": "O(n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "array_sum",
        "kind": "accumulator",
        "difficulty": "easy",
        "code": (
            "int total(const int arr[], int n)\n"
            "{\n"
            "  if (n == 0)\n"
            "    return 0;\n"
            "  return arr[n - 1] + total(arr, n - 1);\n"
            "}"
        ),
        "naive": "O(n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "reverse_list",
        "kind": "accumulator",
        "difficulty": "medium",
        "code": (
            "Node* reverse(Node* head, Node* prev = nullptr)\n"
            "{\n"
            "  if (head == nullptr)\n"
            "    return prev;\n"
            "  Node* next = head->next;\n"
            "  head->next = prev;\n"
            "  return reverse(next, head);\n"
            "}"
        ),
        "naive": "O(n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "inorder_walk",
        "kind": "stack",
        "difficulty": "hard",
        "code": (
            "void inorder(Node* node)\n"
            "{\n"
            "  if (node == nullptr)\n"
            "    return;\n"
            "  inorder(node->left);\n"
            "  visit(node->value);\n"
            "  inorder(node->right);\n"
            "}"
        ),
        "naive": "O(h) stack",
        "wants": ("ITERATIVE",),
    },
    # --- table: overlapping subproblems, the win is a cache -------------------
    {
        "name": "lcs",
        "kind": "table",
        "difficulty": "hard",
        "code": (
            "int lcs(const char* a, const char* b, int i, int j)\n"
            "{\n"
            "  if (i == 0 || j == 0)\n"
            "    return 0;\n"
            "  if (a[i - 1] == b[j - 1])\n"
            "    return 1 + lcs(a, b, i - 1, j - 1);\n"
            "  return max(lcs(a, b, i - 1, j), lcs(a, b, i, j - 1));\n"
            "}"
        ),
        "naive": "O(2^n)",
        "wants": ("MEMOISED", "TABULATED"),
    },
    {
        "name": "binomial",
        "kind": "table",
        "difficulty": "medium",
        "code": (
            "int choose(int n, int k)\n"
            "{\n"
            "  if (k == 0 || k == n)\n"
            "    return 1;\n"
            "  return choose(n - 1, k - 1) + choose(n - 1, k);\n"
            "}"
        ),
        "naive": "O(2^n)",
        "wants": ("MEMOISED", "TABULATED"),
    },
    # --- accumulator: linear recursion, a running variable replaces the stack --
    {
        "name": "gcd_euclid",
        "kind": "accumulator",
        "difficulty": "easy",
        "code": (
            "int gcd(int a, int b)\n"
            "{\n"
            "  if (b == 0)\n"
            "    return a;\n"
            "  return gcd(b, a % b);\n"
            "}"
        ),
        "naive": "O(log n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "count_digits",
        "kind": "accumulator",
        "difficulty": "easy",
        "code": (
            "int digits(long long n)\n"
            "{\n"
            "  if (n < 10)\n"
            "    return 1;\n"
            "  return 1 + digits(n / 10);\n"
            "}"
        ),
        "naive": "O(log n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "binary_search",
        "kind": "accumulator",
        "difficulty": "medium",
        "code": (
            "int search(const int* table, int low, int high, int wanted)\n"
            "{\n"
            "  if (low > high)\n"
            "    return -1;\n"
            "  int probe = low + (high - low) / 2;\n"
            "  if (table[probe] == wanted)\n"
            "    return probe;\n"
            "  if (table[probe] < wanted)\n"
            "    return search(table, probe + 1, high, wanted);\n"
            "  return search(table, low, probe - 1, wanted);\n"
            "}"
        ),
        "naive": "O(log n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "list_length",
        "kind": "accumulator",
        "difficulty": "medium",
        "code": (
            "int length(Node* head)\n"
            "{\n"
            "  if (head == nullptr)\n"
            "    return 0;\n"
            "  return 1 + length(head->next);\n"
            "}"
        ),
        "naive": "O(n) stack",
        "wants": ("ITERATIVE",),
    },
    # --- stack: two recursive calls, the call stack needs a real replacement ---
    {
        "name": "preorder_walk",
        "kind": "stack",
        "difficulty": "hard",
        "code": (
            "void preorder(Node* node)\n"
            "{\n"
            "  if (node == nullptr)\n"
            "    return;\n"
            "  visit(node->value);\n"
            "  preorder(node->left);\n"
            "  preorder(node->right);\n"
            "}"
        ),
        "naive": "O(h) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "tree_height",
        "kind": "stack",
        "difficulty": "hard",
        "code": (
            "int height(Node* node)\n"
            "{\n"
            "  if (node == nullptr)\n"
            "    return 0;\n"
            "  return 1 + max(height(node->left), height(node->right));\n"
            "}"
        ),
        "naive": "O(h) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "quicksort",
        "kind": "stack",
        "difficulty": "hard",
        "code": (
            "void quicksort(int* values, int low, int high)\n"
            "{\n"
            "  if (low >= high)\n"
            "    return;\n"
            "  int split = partition(values, low, high);\n"
            "  quicksort(values, low, split - 1);\n"
            "  quicksort(values, split + 1, high);\n"
            "}"
        ),
        "naive": "O(log n) stack",
        "wants": ("ITERATIVE",),
    },
    {
        "name": "flood_fill",
        "kind": "stack",
        "difficulty": "hard",
        "code": (
            "void fill(int** grid, int row, int col, int from, int to)\n"
            "{\n"
            "  if (row < 0 || col < 0 || grid[row][col] != from)\n"
            "    return;\n"
            "  grid[row][col] = to;\n"
            "  fill(grid, row + 1, col, from, to);\n"
            "  fill(grid, row - 1, col, from, to);\n"
            "  fill(grid, row, col + 1, from, to);\n"
            "  fill(grid, row, col - 1, from, to);\n"
            "}"
        ),
        "naive": "O(n) stack",
        "wants": ("ITERATIVE",),
    },
]

PHRASINGS = {
    "trained_wording": "Generate:\n- Improved code",
    "explicit_faster": "Generate:\n- Improved code (make it asymptotically faster; do not merely reformat)",
    "explicit_memo": (
        "Generate:\n- Improved code (this function recomputes the same subproblems many times. "
        "Rewrite it to store results so each subproblem is solved once, using memoisation or a "
        "dynamic-programming table. Keep the same signature and behaviour.)"
    ),
    "explicit_loop": (
        "Generate:\n- Improved code (rewrite this function so it uses a loop instead of calling "
        "itself. Keep the same signature and the same results. Do not add a table or cache - "
        "there are no repeated subproblems, the only goal is to remove the recursion.)"
    ),
}

#: Renaming is run only with the phrasing that already won on that sample. The
#: question in this phase is whether the capability survives bad names, not which
#: wording finds it - re-testing losing phrasings under obfuscation would only
#: report the wording failure twice.
BEST_PHRASING = {("MEMOISED", "TABULATED"): "explicit_memo", ("ITERATIVE",): "explicit_loop"}

#: `original` is the control and must stay first: every other strategy is read as
#: a delta against it. `misleading` is the diagnostic one - names that assert the
#: wrong behaviour, which a model reading identifiers rather than code will follow.
RENAME_STRATEGIES = ["original", "clear", "terse", "misleading", "noise"]

SYSTEM = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)


def build_prompt(code: str, generate_block: str) -> str:
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"{generate_block}\n\nReturn a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


#: Tokens that indicate stored results. Matched against the rewrite *minus* the
#: original, so a parameter the sample already had is not read as a new table.
_TABLE = re.compile(r"\b(memo|dp|cache|table|vector\s*<|map\s*<|unordered_map)", re.I)


def classify(original: str, improved: str) -> tuple[str, list[str]]:
    """Say what the rewrite actually did, in terms that can be checked."""
    improved = strip_comments(improved)
    signals = []
    # Whether anything still calls itself, rather than whether one guessed name
    # appears twice. The guess picked the first function-shaped token in the file,
    # which on a real submission is usually a helper, not the recursive function.
    still_recursive = bool(recursive_functions(improved))
    # Only tokens the rewrite *introduced* count as a table. `binary_search`
    # takes a parameter named `table`, so matching the improved code alone
    # reported a textbook iterative rewrite as TABULATED and scored it zero
    # against wants=("ITERATIVE",) - the sample could not pass whatever the
    # model wrote. Same shape as the keyword-in-a-comment mistake in
    # CLAUDE.md: a name matched where a concept was meant.
    introduced = _TABLE.findall(strip_comments(improved))
    inherited = _TABLE.findall(strip_comments(original))
    has_table = bool(
        {token.lower() for token in introduced} - {token.lower() for token in inherited}
    )
    has_loop = bool(re.search(r"\b(for|while)\s*\(", improved))
    has_static = bool(re.search(r"\bstatic\b", improved))

    if has_table:
        signals.append("stores results")
    if has_loop:
        signals.append("has a loop")
    if still_recursive:
        signals.append("still recursive")
    if has_static:
        signals.append("static storage")

    if has_table and still_recursive:
        return "MEMOISED (top-down)", signals
    if has_table and has_loop and not still_recursive:
        return "TABULATED (bottom-up)", signals
    if has_loop and not still_recursive:
        return "ITERATIVE (no table)", signals
    if still_recursive:
        return "unchanged algorithm", signals
    return "unclear", signals


def wait_for_server(port: int, timeout: float = 300.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
                if json.load(response).get("status") == "ok":
                    return
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError("llama-server did not become ready")


def complete(port: int, prompt: str, n_predict: int) -> str:
    payload = json.dumps(
        {"prompt": prompt, "n_predict": n_predict, "temperature": 0, "cache_prompt": False}
    ).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["content"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8097)
    parser.add_argument("--n-predict", type=int, default=450)
    parser.add_argument("--seed", type=int, default=0, help="identifier renaming seed")
    parser.add_argument("--draws", type=int, default=3, help="rename draws per strategy")
    parser.add_argument("--output", default="test_results/optimization_probe.json")
    args = parser.parse_args()

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096", "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    skipped: list[tuple[str, str]] = []
    try:
        wait_for_server(args.port)
        def ask(sample: dict, phrasing: str, code: str, strategy: str, draw: int = 0) -> dict:
            text = complete(args.port, build_prompt(code, PHRASINGS[phrasing]), args.n_predict)
            try:
                improved = (json.loads(text) or {}).get("improved_code") or ""
                parsed = True
            except json.JSONDecodeError:
                improved, parsed = text, False
            # Classified against the renamed source, so "still recursive" is judged
            # by the name the model was actually shown.
            verdict, signals = classify(code, improved)
            record = {
                "sample": sample["name"], "difficulty": sample["difficulty"],
                "kind": sample["kind"], "draw": draw,
                "phrasing": phrasing, "strategy": strategy, "verdict": verdict,
                "wanted": list(sample["wants"]), "signals": signals,
                "json_ok": parsed, "improved_code": improved,
            }
            records.append(record)
            return record

        print("PHASE 1 - which wording finds the capability, on the original names")
        for sample in SAMPLES:
            print(f"\n=== {sample['name']}  ({sample['difficulty']}, naive {sample['naive']}) ===")
            for label in PHRASINGS:
                got = ask(sample, label, sample["code"], "original")
                print(f"  {label:<18} -> {got['verdict']:<22} "
                      f"[{', '.join(got['signals']) or 'nothing detected'}]")

        print("\n\nPHASE 2 - does the winning wording survive renamed identifiers")
        # Several draws per strategy. Which names a strategy happens to pick is
        # itself a variable - one draw of `misleading` can land on a word that
        # fits the code by luck - so a single call per cell reports a coin flip
        # as a rate.
        for sample in SAMPLES:
            phrasing = BEST_PHRASING[sample["wants"]]
            print(f"\n=== {sample['name']}  ({sample['kind']}, {sample['difficulty']}) ===")
            for strategy in RENAME_STRATEGIES:
                if strategy == "original":
                    continue  # phase 1 already ran this exact call
                verdicts = []
                for draw in range(args.draws):
                    renamed = obfuscate(sample["code"], strategy, random.Random(args.seed + draw))
                    if renamed == sample["code"]:
                        skipped.append((sample["name"], strategy))
                        continue
                    got = ask(sample, phrasing, renamed, strategy, draw)
                    verdicts.append("PASS" if got["verdict"].startswith(sample["wants"]) else "fail")
                summary = f"{verdicts.count('PASS')}/{len(verdicts)}" if verdicts else "not renamed"
                print(f"  {strategy:<12} {summary:<8} {' '.join(verdicts)}")
    finally:
        process.terminate()
        process.wait(timeout=30)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(records, indent=2), encoding="utf-8")

    wanted = {sample["name"]: sample["wants"] for sample in SAMPLES}

    def won(record: dict) -> bool:
        return record["verdict"].startswith(wanted[record["sample"]])

    wins = [r for r in records if won(r)]
    print(f"\n{'=' * 72}")
    print(f"rewrites that actually changed the algorithm: {len(wins)}/{len(records)}")
    # Split by what the sample wanted: an explicit memoisation instruction
    # cannot win on a sample whose right answer is a plain loop, so a single
    # ratio over all six would understate both phrasings.
    groups = {"needs a table": ("MEMOISED", "TABULATED"), "needs a loop": ("ITERATIVE",)}
    for title, wants in groups.items():
        names = [s["name"] for s in SAMPLES if s["wants"] == wants]
        print(f"  {title} ({len(names)} samples)")
        for phrasing in PHRASINGS:
            # Phase 2 reuses the winning phrasing under renamed identifiers, so it
            # must not be counted here: this table is about wording alone.
            hits = [
                r for r in wins
                if r["phrasing"] == phrasing and r["sample"] in names
                and r["strategy"] == "original"
            ]
            print(f"    {phrasing:<18} {len(hits)}/{len(names)}")
    def best(record: dict) -> bool:
        return record["phrasing"] == BEST_PHRASING[wanted[record["sample"]]]

    def rate(rows: list[dict]) -> str:
        return f"{sum(1 for r in rows if won(r))}/{len(rows)}" if rows else "-"

    kinds = {sample["name"]: sample["kind"] for sample in SAMPLES}

    print("\nby what the rewrite needs, best wording, original names")
    for kind in ("table", "accumulator", "stack"):
        names = [s["name"] for s in SAMPLES if s["kind"] == kind]
        rows = [r for r in records if r["strategy"] == "original" and best(r) and kinds[r["sample"]] == kind]
        lost = sorted({r["sample"] for r in rows if not won(r)})
        print(f"  {kind:<12} {rate(rows):<8} of {len(names)} samples"
              f"{'   lost: ' + ', '.join(lost) if lost else ''}")

    print("\nby difficulty, best wording, original names")
    for level in ("easy", "medium", "hard"):
        rows = [r for r in records if r["strategy"] == "original" and best(r)
                and r["difficulty"] == level]
        print(f"  {level:<12} {rate(rows)}")

    print("\nby naming, best wording, all draws pooled  (original is the control)")
    print(f"  {'':<12}{'overall':<10}" + "".join(f"{k:<14}" for k in ("table", "accumulator", "stack")))
    for strategy in RENAME_STRATEGIES:
        rows = [r for r in records if r["strategy"] == strategy and best(r)]
        cells = "".join(
            f"{rate([r for r in rows if kinds[r['sample']] == kind]):<14}"
            for kind in ("table", "accumulator", "stack")
        )
        print(f"  {strategy:<12}{rate(rows):<10}{cells}")

    if skipped:
        pairs = sorted(set(skipped))
        print(f"\n{len(skipped)} rename attempts changed no identifier and were not scored:")
        for name, strategy in pairs:
            print(f"  {name} / {strategy}")

    print("\nIf the explicit phrasing wins, the capability is there and the")
    print("instruction was the problem. If nothing wins, it needs training data.")
    print("If renaming costs points, the model is reading identifiers, not code.")
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()
