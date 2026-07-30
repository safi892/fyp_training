from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

DEFAULT_MODEL = "/kaggle/input/datasets/saffiullah892/qwen2-5-01/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/checkpoint-750"
DEFAULT_OUTPUT = "/kaggle/working/outputs/model_test_predictions.jsonl"
DEFAULT_OUTPUT_FIELDS = ["comments", "explanation", "improved_code", "complexity_analysis"]
DEFAULT_PROMPT_STYLE = "chat"

SYSTEM_PROMPT = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)
FIELD_TITLES = {
    "comments": "Line-by-line comments",
    "explanation": "Explanation",
    "improved_code": "Improved code",
    "complexity_analysis": "Complexity analysis",
}

DECL_RE = re.compile(
    r"\b(?:int|long|short|float|double|bool|char|string|auto|size_t|long\s+long|vector\s*<[^;(){}]+>)\s+([^;(){}]+)[;)]"
)
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
TOKEN_RE = re.compile(
    r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|\b[A-Za-z_][A-Za-z0-9_]*\b",
    re.DOTALL,
)
CPP_SKIP_NAMES = {
    "auto",
    "bool",
    "char",
    "cin",
    "cout",
    "double",
    "endl",
    "float",
    "int",
    "long",
    "main",
    "max",
    "min",
    "return",
    "size_t",
    "sort",
    "std",
    "string",
    "swap",
    "vector",
    "void",
}
BAD_NAMES = ["a", "b", "c", "x", "y", "z", "i", "j", "k", "n", "m", "f", "tmp"]

BUILTIN_EXAMPLES = [
    {
        "source": "builtin",
        "difficulty": "easy",
        "name": "simple_sum_bad_names",
        "focus": "basic readability, variable naming, simple complexity",
        "language": "cpp",
        "code": "int add(int a, int b) {\n    int x = a + b;\n    return x;\n}",
    },
    {
        "source": "builtin",
        "difficulty": "easy",
        "name": "max_value_empty_vector_bug",
        "focus": "empty-input edge case, safer initialization, naming",
        "language": "cpp",
        "code": (
            "#include <vector>\n"
            "using namespace std;\n\n"
            "int f(vector<int>& a) {\n"
            "    int x = a[0];\n"
            "    for (int i = 1; i < a.size(); i++) {\n"
            "        if (a[i] > x) x = a[i];\n"
            "    }\n"
            "    return x;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "easy",
        "name": "string_count_case_sensitivity",
        "focus": "clear naming, char handling, case-sensitivity behavior",
        "language": "cpp",
        "code": (
            "#include <string>\n"
            "using namespace std;\n\n"
            "int cnt(string s, char c) {\n"
            "    int a = 0;\n"
            "    for (int i = 0; i < s.size(); i++) {\n"
            "        if (s[i] == c) a++;\n"
            "    }\n"
            "    return a;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "medium",
        "name": "binary_search_overflow_mid",
        "focus": "binary search correctness, overflow-safe midpoint, naming",
        "language": "cpp",
        "code": (
            "#include <vector>\n"
            "using namespace std;\n\n"
            "int f(vector<int>& a, int x) {\n"
            "    int l = 0, r = a.size() - 1;\n"
            "    while (l <= r) {\n"
            "        int m = (l + r) / 2;\n"
            "        if (a[m] == x) return m;\n"
            "        if (a[m] < x) l = m + 1;\n"
            "        else r = m - 1;\n"
            "    }\n"
            "    return -1;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "medium",
        "name": "prime_count_sqrt_loop",
        "focus": "nested-loop complexity, prime edge cases, helper extraction",
        "language": "cpp",
        "code": (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "int countPrime(vector<int> a) {\n"
            "    int b = 0;\n"
            "    for (int i = 0; i < a.size(); i++) {\n"
            "        bool f = true;\n"
            "        for (int j = 2; j * j <= a[i]; j++) {\n"
            "            if (a[i] % j == 0) {\n"
            "                f = false;\n"
            "                break;\n"
            "            }\n"
            "        }\n"
            "        if (a[i] > 1 && f) b++;\n"
            "    }\n"
            "    return b;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "medium",
        "name": "sliding_window_off_by_one",
        "focus": "off-by-one bug, window invariant, edge cases",
        "language": "cpp",
        "code": (
            "#include <vector>\n"
            "using namespace std;\n\n"
            "int maxSum(vector<int>& a, int k) {\n"
            "    int s = 0, ans = 0;\n"
            "    for (int i = 0; i < k; i++) s += a[i];\n"
            "    for (int i = k; i <= a.size(); i++) {\n"
            "        ans = max(ans, s);\n"
            "        s += a[i];\n"
            "        s -= a[i - k];\n"
            "    }\n"
            "    return ans;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "medium",
        "name": "recursive_fibonacci_exponential",
        "focus": "exponential time, recursion, dynamic programming improvement",
        "language": "cpp",
        "code": (
            "int fib(int n) {\n"
            "    if (n <= 1) return n;\n"
            "    return fib(n - 1) + fib(n - 2);\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "medium",
        "name": "integer_overflow_average",
        "focus": "integer overflow, numeric types, precision",
        "language": "cpp",
        "code": (
            "#include <vector>\n"
            "using namespace std;\n\n"
            "double avg(vector<int>& a) {\n"
            "    int s = 0;\n"
            "    for (int x : a) s += x;\n"
            "    return s / a.size();\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "hard",
        "name": "dijkstra_adjacency_matrix",
        "focus": "graph complexity, priority queue use, unreachable nodes",
        "language": "cpp",
        "code": (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "int solve(vector<vector<int>>& g) {\n"
            "    int n = g.size();\n"
            "    vector<int> d(n, 1e9), vis(n);\n"
            "    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;\n"
            "    d[0] = 0;\n"
            "    pq.push({0, 0});\n"
            "    while (!pq.empty()) {\n"
            "        auto p = pq.top(); pq.pop();\n"
            "        int u = p.second;\n"
            "        if (vis[u]) continue;\n"
            "        vis[u] = 1;\n"
            "        for (int v = 0; v < n; ++v) {\n"
            "            if (g[u][v] && d[v] > d[u] + g[u][v]) {\n"
            "                d[v] = d[u] + g[u][v];\n"
            "                pq.push({d[v], v});\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    return d[n - 1];\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "hard",
        "name": "topological_sort_missing_cycle_check",
        "focus": "cycle detection, graph correctness, queue invariant",
        "language": "cpp",
        "code": (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "vector<int> topo(int n, vector<pair<int,int>> e) {\n"
            "    vector<vector<int>> g(n);\n"
            "    vector<int> in(n), ans;\n"
            "    for (auto p : e) {\n"
            "        g[p.first].push_back(p.second);\n"
            "        in[p.second]++;\n"
            "    }\n"
            "    queue<int> q;\n"
            "    for (int i = 0; i < n; i++) if (in[i] == 0) q.push(i);\n"
            "    while (!q.empty()) {\n"
            "        int u = q.front(); q.pop();\n"
            "        ans.push_back(u);\n"
            "        for (int v : g[u]) {\n"
            "            in[v]--;\n"
            "            if (in[v] == 0) q.push(v);\n"
            "        }\n"
            "    }\n"
            "    return ans;\n"
            "}"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "hard",
        "name": "dsu_recursive_find_no_compression",
        "focus": "DSU optimization, path compression, union by rank",
        "language": "cpp",
        "code": (
            "#include <vector>\n"
            "using namespace std;\n\n"
            "struct DSU {\n"
            "    vector<int> p;\n"
            "    DSU(int n) { for (int i = 0; i < n; i++) p.push_back(i); }\n"
            "    int find(int x) {\n"
            "        if (p[x] == x) return x;\n"
            "        return find(p[x]);\n"
            "    }\n"
            "    void unite(int a, int b) {\n"
            "        a = find(a);\n"
            "        b = find(b);\n"
            "        if (a != b) p[a] = b;\n"
            "    }\n"
            "};"
        ),
    },
    {
        "source": "builtin",
        "difficulty": "hard",
        "name": "raw_pointer_memory_leak",
        "focus": "memory safety, RAII, ownership, leaks",
        "language": "cpp",
        "code": (
            "#include <iostream>\n"
            "using namespace std;\n\n"
            "int* makeArray(int n) {\n"
            "    int* a = new int[n];\n"
            "    for (int i = 0; i < n; i++) a[i] = i * i;\n"
            "    return a;\n"
            "}\n\n"
            "int main() {\n"
            "    int* x = makeArray(1000);\n"
            "    cout << x[10] << endl;\n"
            "    return 0;\n"
            "}"
        ),
    },
]


def read_rows(path: Path, limit: int) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
            if len(rows) >= limit:
                break
    return rows


def build_instruction(language: str, output_fields: list[str]) -> str:
    requested = "\n".join(f"- {FIELD_TITLES.get(field, field.replace('_', ' ').title())}" for field in output_fields)
    return (
        "Analyze the following C++ code.\n\n"
        f"Language: {language}\n\n"
        "Generate:\n"
        f"{requested}\n\n"
        "Return a single JSON object using the requested field names."
    )


def format_prompt_without_response(
    code: str,
    output_fields: list[str],
    *,
    style: str,
    tokenizer,
    language: str = "cpp",
) -> str:
    instruction = build_instruction(language, output_fields)
    if style == "instruction":
        return f"### Instruction\n\n{instruction}\n\n### Code\n\n{code}\n\n### Response\n\n"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def augment_row(row: dict, rng: random.Random) -> list[dict]:
    names: list[str] = []
    for match in DECL_RE.finditer(row.get("code", "")):
        for name in IDENT_RE.findall(match.group(1)):
            if name not in CPP_SKIP_NAMES and not name.startswith("__"):
                names.append(name)
    names = sorted(set(names), key=names.index)
    if not names:
        return [row]

    mapping = {}
    used = set(names)
    for index, name in enumerate(names):
        candidate = BAD_NAMES[index % len(BAD_NAMES)]
        if candidate in used:
            candidate = f"{candidate}_{index}"
        mapping[name] = candidate
        used.add(candidate)
    items = list(mapping.items())
    rng.shuffle(items)
    mapping = dict(items)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith(("//", "/*", '"', "'")):
            return token
        return mapping.get(token, token)

    renamed = dict(row)
    renamed["source"] = row.get("source", "builtin")
    renamed["code"] = TOKEN_RE.sub(replace, row["code"])
    renamed["variant_note"] = "bad_variable_names"
    return [row, renamed]


def extract_json(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def load_model(model_path: str, adapter_path: str | None):
    import torch
    from peft import PeftConfig, PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    path = Path(model_path)
    inferred_adapter = adapter_path
    base_model = model_path
    if inferred_adapter is None and (path / "adapter_config.json").exists():
        inferred_adapter = model_path
        base_model = PeftConfig.from_pretrained(model_path).base_model_name_or_path

    quantization_config = None
    if torch.cuda.is_available():
        try:
            import bitsandbytes  # noqa: F401
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )
            print("Loading model with bitsandbytes 4-bit quantization")
        except ImportError:
            print("bitsandbytes not found; loading model without 4-bit quantization")

    tokenizer = AutoTokenizer.from_pretrained(
        inferred_adapter or base_model,
        trust_remote_code=True,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=quantization_config,
        device_map="auto" if torch.cuda.is_available() else None,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
    )
    if inferred_adapter:
        disable_incompatible_torchao()
        model = PeftModel.from_pretrained(model, inferred_adapter)
    model.eval()
    return model, tokenizer


def disable_incompatible_torchao() -> None:
    try:
        import peft.import_utils
        import peft.tuners.lora.torchao
    except Exception:
        return
    peft.import_utils.is_torchao_available = lambda: False
    peft.tuners.lora.torchao.is_torchao_available = lambda: False


def generate(model, tokenizer, prompt: str, max_new_tokens: int, temperature: float) -> str:
    import torch

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.pad_token_id,
        )
    generated = output[0, inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(generated, skip_special_tokens=True)


def score(parsed: dict | None, required_fields: list[str]) -> dict[str, bool]:
    return {
        "valid_json": parsed is not None,
        "has_required_fields": bool(parsed) and all(field in parsed for field in required_fields),
        "has_improved_code": bool(parsed) and bool(str(parsed.get("improved_code", "")).strip()),
        "has_complexity": bool(parsed) and "complexity_analysis" in parsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test a merged model or LoRA adapter on JSONL code examples.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Merged model dir, base model id, or LoRA adapter dir.")
    parser.add_argument("--adapter", default=None, help="Optional LoRA adapter dir when --model is the base model.")
    parser.add_argument("--dataset", default=None, help="Optional JSONL file with extra code examples.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--builtin-examples",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run easy/medium/hard built-in examples before dataset rows.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--print-results", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--rename-check",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Also test one bad-variable-name variant per row.",
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        print(f"Ignoring notebook launcher args: {unknown_args}")

    model, tokenizer = load_model(args.model, args.adapter)
    output_fields = DEFAULT_OUTPUT_FIELDS
    prompt_style = DEFAULT_PROMPT_STYLE
    rows = []
    if args.builtin_examples:
        rows.extend(BUILTIN_EXAMPLES)
    if args.dataset:
        rows.extend(read_rows(Path(args.dataset), args.limit))
    print(f"Loaded {len(rows)} examples")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    totals = {"valid_json": 0, "has_required_fields": 0, "has_improved_code": 0, "has_complexity": 0}
    tested = 0
    with output_path.open("w", encoding="utf-8") as target:
        for index, row in enumerate(rows):
            variants = [("original", row)]
            if args.rename_check:
                augmented = augment_row(dict(row), __import__("random").Random(index))
                if len(augmented) > 1:
                    variants.append(("renamed", augmented[1]))

            for variant_name, variant in variants:
                prompt = format_prompt_without_response(
                    variant["code"],
                    output_fields,
                    style=prompt_style,
                    tokenizer=tokenizer,
                    language=variant.get("language", "cpp"),
                )
                text = generate(model, tokenizer, prompt, args.max_new_tokens, args.temperature)
                parsed = extract_json(text)
                item_score = score(parsed, output_fields)
                for key, value in item_score.items():
                    totals[key] += int(value)
                tested += 1
                target.write(
                    json.dumps(
                        {
                            "index": index,
                            "source": row.get("source", "dataset"),
                            "difficulty": row.get("difficulty"),
                            "name": row.get("name"),
                            "focus": row.get("focus"),
                            "variant": variant_name,
                            "score": item_score,
                            "prediction": text,
                            "parsed": parsed,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                print(f"{index}:{variant_name} {item_score}")
                if args.print_results:
                    print("=" * 80)
                    print(f"difficulty: {row.get('difficulty')}")
                    print(f"name: {row.get('name')}")
                    print(f"focus: {row.get('focus')}")
                    print(f"variant: {variant_name}")
                    print("-" * 80)
                    print(text.strip())
                    print("=" * 80)

    summary = {key: f"{value}/{tested}" for key, value in totals.items()}
    print(json.dumps({"tested": tested, "summary": summary, "predictions": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
