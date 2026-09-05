"""Build a verified recursion-to-iteration dataset by generating and throwing most of it away.

The corpus cannot supply this. Of the 736 recursive functions whose signature the
driver can drive, **614 - 83% - carry an `improved_code` that still recurses**.
The targets were written without being executed, so they tidied the code and left
the algorithm alone, and a model trained on them does the same. Filtering the
corpus yields about 55 usable rows, which is not a dataset.

So the rows are generated instead, and the gate decides which ones exist:

    1. take a recursive function from the corpus, with its author's identifiers
    2. ask the model for an iterative version, several times, sampled not greedy
    3. keep an attempt only if it compiles, runs, and prints exactly what the
       original printed on the same generated inputs
    4. everything else is discarded without being looked at

A single attempt succeeds about 17% of the time. That is a poor generator and a
perfectly good *proposer*, because correctness is not being trusted - it is being
tested. Every kept row is executable evidence rather than an opinion, which is
the property the original 19,033 rows never had.

    uv run python scripts/build_optimize_dataset.py --limit 300 --samples 6

Use ``--task auto`` to route each recursive function first: direct recursion is
sent to the iteration prompt, while branching recursive returns are sent to the
memoisation / DP prompt.

Two generation backends, because the bottleneck is throughput and not the gate:

    --backend llama   llama-server on CPU. ~120s per function at 6 samples,
                      so 582 functions is about nineteen hours.
    --backend hf      transformers on a GPU, generating a whole function's
                      samples in one batch. Built for a Colab or Kaggle T4.

The GPU does not improve the yield - it is the same weights giving the same
answers - it makes attempts cheap enough to afford more of them. That matters
because the failures are correlated: a function the model will not de-recurse
tends not to be de-recursed on the next sample either, so the gain from more
samples is real but sublinear.

Resumable: finished functions are skipped on the next run, so this can be
stopped and restarted without losing work or repeating calls.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from itertools import cycle
from pathlib import Path

from qwen_cpp_review.claim_checks import recursive_functions
from qwen_cpp_review.optimization_routing import select_optimization_task
from qwen_cpp_review.prompt import TASK_FIELD_HINTS
from qwen_cpp_review.verification import parse_signature, verify

SYSTEM = (
    "You are a senior C++ code review assistant. Produce accurate, structured, "
    "actionable review output for the given source code."
)

#: Read from the registry rather than copied, so the dataset is built with the
#: instruction that will be used to serve it.
#:
#: Which transformation to ask for. `optimize` is the default because the probe
#: measured it: trained wording 0/3, this wording 3/3. `iterate` asks for an
#: explicit std::stack, which is a mechanical rewrite of the same complexity -
#: a 5.8 GPU-hour run produced 2 rows from 130 attempts and both were stack
#: simulations that made nothing faster.
TASK = "optimize"


def build_instruction(code: str, task: str = TASK) -> tuple[str, str]:
    """The system and user halves, before either backend wraps them.

    Split out so the API backend can send real chat roles rather than posting
    Qwen's template markers as message text, while asking for exactly the same
    thing. The wording stays the product's, so a pair a teacher produces here is
    a pair the small model was asked for in the same words.
    """
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"Generate:\n- Improved code ({TASK_FIELD_HINTS[task]['improved_code']})\n\n"
        "Return a single JSON object using the requested field names."
    )
    return SYSTEM, f"{instruction}\n\n### Code\n\n```cpp\n{code}\n```"


def build_prompt(code: str, task: str = TASK) -> str:
    system, user = build_instruction(code, task)
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


class APIGenerator:
    """Propose rewrites with a hosted model instead of the local one.

    The gate does not change and neither does the prompt: only who is asked.
    That is the point - a stronger proposer raises the yield without weakening
    the guarantee, because a pair still only exists if it compiled, ran, and
    printed what the original printed.

    Credentials come from the same ``.env`` ``probe_teacher.py`` reads, so a
    provider that works for the probe works here. Calls are spaced rather than
    parallelised: the free tiers throttle at around ten a minute, and a 429
    costs the call as well as the wait.
    """

    def __init__(self, env: Path, provider: str, model: str, rpm: int, task: str):
        config = load_provider_config(env, provider)
        self.base = config["baseUrl"].rstrip("/")
        self.model = config.get("model") or model
        self.provider = provider
        self.task = task
        self.azure = "azure" in self.base
        self.headers = {"Content-Type": "application/json"}
        if self.azure:
            self.headers["api-key"] = config["apiKey"]
        else:
            self.headers["Authorization"] = f"Bearer {config['apiKey']}"
        self.gap = 60.0 / max(1, rpm)
        self.last = 0.0

    def _wait(self) -> None:
        pause = self.gap - (time.monotonic() - self.last)
        if pause > 0:
            time.sleep(pause)
        self.last = time.monotonic()

    def _one(
        self, code: str, budget: int, temperature: float, task: str | None = None,
        retries: int = 5,
    ) -> str:
        system, user = build_instruction(code, task or self.task)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "top_p": 0.95,
        }
        # Azure reasoning models want max_completion_tokens; the rest want max_tokens.
        payload["max_completion_tokens" if self.azure else "max_tokens"] = budget

        last = ""
        for attempt in range(retries):
            self._wait()
            try:
                request = urllib.request.Request(
                    self.base + "/chat/completions",
                    data=json.dumps(payload).encode(), headers=self.headers,
                )
                with urllib.request.urlopen(request, timeout=600) as response:
                    message = json.load(response)["choices"][0]["message"]
                # Reasoning models split the answer from their working; prefer
                # the answer, but a model that put everything in one field still
                # gets read rather than discarded.
                return message.get("content") or message.get("reasoning_content") or ""
            except Exception as exc:  # noqa: BLE001 - retried, then given up on
                last = f"{type(exc).__name__}: {exc}"
                time.sleep(min(64, 2 ** attempt))
        print(f"    api gave up: {last}")
        return ""

    def samples(
        self, code: str, count: int, budget: int, temperature: float, task: str | None = None
    ) -> list[str]:
        return [self._one(code, budget, temperature, task) for _ in range(count)]


def load_provider_config(env: Path, provider: str) -> dict[str, str]:
    """Read provider credentials from the first JSON object in ``env``."""
    text = env.read_text(encoding="utf-8")
    config, _ = json.JSONDecoder().raw_decode(text.lstrip())
    try:
        return config["providers"][provider]
    except KeyError as exc:
        known = sorted(config.get("providers", {}))
        raise KeyError(f"provider {provider!r} not found in {env}; known providers: {known}") from exc


def provider_names(provider: str, providers: list[str] | None) -> list[str]:
    """The API provider keys to use, preserving command-line order."""
    names = providers or [provider]
    return list(dict.fromkeys(names))


#: A fenced block, with or without a language tag.
_FENCE = re.compile(r"```(?:[A-Za-z+]*)\n(.*?)```", re.S)
#: The first balanced-looking JSON object in a longer reply.
_EMBEDDED = re.compile(r"\{.*\}", re.S)


def extract_candidate(text: str) -> str:
    """The rewritten C++ in a reply, however the model chose to wrap it.

    The fine-tune emits a bare JSON object because that is what it was trained
    to emit. The base model does not - the ablation measured 0/20 usable JSON
    from it - and insisting on JSON here would reject every one of its answers
    for the wrong reason. Format compliance is not what a proposer is for; the
    gate decides whether the code is right, and the code is what has to be
    found.

    Order matters. A fenced block inside a JSON string is still JSON, so JSON is
    tried first and fences only when parsing fails.
    """
    text = text.strip()
    if not text:
        return ""

    for candidate in (text, *(m.group(0) for m in [_EMBEDDED.search(text)] if m)):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            value = parsed.get("improved_code")
            if isinstance(value, str) and value.strip():
                return value

    blocks = [block.strip() for block in _FENCE.findall(text) if block.strip()]
    if blocks:
        # The longest, because a reply often fences the original for contrast
        # before fencing the rewrite, and the rewrite is the longer of the two.
        return max(blocks, key=len)

    # Unfenced but plainly C++: better than discarding an answer the gate could
    # have judged in a second.
    if re.search(r"\b(?:int|void|bool|long|double|string|auto)\b[^\n]*\(", text):
        return text
    return ""


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


def complete(port: int, prompt: str, n_predict: int, temperature: float, seed: int) -> str:
    """One sample. Temperature is above zero on purpose.

    Greedy decoding gives the same wrong answer every time, so a second attempt
    at the same function would cost a call and add nothing. Sampling is what
    makes several attempts worth making.
    """
    payload = json.dumps({
        "prompt": prompt, "n_predict": n_predict, "temperature": temperature,
        "top_p": 0.95, "seed": seed, "cache_prompt": False,
    }).encode()
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/completion", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["content"]


class HFGenerator:
    """Batched sampling on a GPU: one function's attempts in a single forward pass.

    Left-padded, because a decoder-only model continues from the last position
    and right padding would have it continue from the padding instead of the
    prompt.
    """

    def __init__(self, base: str, adapter: str | None, dtype: str = "float16",
                 batch: int = 4):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        source = adapter or base
        self.tokenizer = AutoTokenizer.from_pretrained(source, padding_side="left")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            base, dtype=getattr(torch, dtype), device_map="auto"
        )
        if adapter:
            from peft import PeftModel

            self.model = PeftModel.from_pretrained(self.model, adapter)
        self.model.eval()
        self.torch = torch
        self.batch = batch

    def _generate(self, prompt: str, count: int, n_predict: int, temperature: float) -> list[str]:
        batch = self.tokenizer([prompt] * count, return_tensors="pt", padding=True).to(
            self.model.device
        )
        with self.torch.no_grad():
            out = self.model.generate(
                **batch, max_new_tokens=n_predict, do_sample=True,
                temperature=temperature, top_p=0.95,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        width = batch["input_ids"].shape[1]
        return [self.tokenizer.decode(row[width:], skip_special_tokens=True) for row in out]

    def samples(self, prompt: str, count: int, n_predict: int, temperature: float) -> list[str]:
        """`count` samples, in sub-batches small enough to fit.

        Sixteen sequences of a long function plus 700 new tokens each is a large
        KV cache, and a T4 has 15GB. Running out of it raises inside CUDA and
        takes the process with it, which looks exactly like the run "stopping by
        itself" partway through - no traceback worth reading, no partial result
        beyond what was already flushed to disk.

        So the batch is bounded, and halved again on the first failure. Slower
        than one big batch by a little, and it finishes.
        """
        produced: list[str] = []
        size = min(count, self.batch)
        while len(produced) < count:
            want = min(size, count - len(produced))
            try:
                produced += self._generate(prompt, want, n_predict, temperature)
            except Exception as error:                    # noqa: BLE001 - torch OOM types vary
                if "out of memory" not in str(error).lower() or want == 1:
                    raise
                self.torch.cuda.empty_cache()
                size = max(1, want // 2)
                print(f"    (out of memory at batch {want}, retrying at {size})", flush=True)
        return produced[:count]


def recursive_call_count(code: str) -> int:
    """How many times the function calls itself.

    One call is linear recursion - a countdown, a list walk - where the answer
    is computed once and memoisation has nothing to remember. Two or more is
    the branching shape (`f(n-1) + f(n-2)`) where subproblems overlap and a
    table turns exponential into linear. Measured on the corpus: 218 of 582
    functions are the first kind, and attempting them spends GPU time to learn
    a rewrite that cannot be faster.
    """
    match = re.search(r"\b\w+[\s*&]+(\w+)\s*\(", code)
    if not match:
        return 0
    return len(re.findall(rf"\b{re.escape(match.group(1))}\s*\(", code)) - 1


def task_for_code(code: str, requested: str) -> str:
    """Resolve ``--task auto`` for one function."""
    return select_optimization_task(code) if requested == "auto" else requested


def drivable_recursive(corpus: Path, max_lines: int) -> list[str]:
    """Corpus functions that recurse and whose signature the driver can supply."""
    found = []
    for line in corpus.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        code = json.loads(line).get("code") or ""
        if not code.strip() or len(code.splitlines()) > max_lines:
            continue
        if not recursive_functions(code):
            continue
        signature = parse_signature(code)
        if signature is not None and signature.supported:
            found.append(code)
    # De-duplicated: the corpus repeats popular problems, and the same function
    # generated twice is one row of information counted twice.
    return list(dict.fromkeys(found))


def judge(original: str, candidate: str, timeout: float) -> str | None:
    """Why this attempt cannot be kept, or None if it is verified."""
    if not candidate.strip():
        return "empty"
    if recursive_functions(candidate):
        return "still recursive"
    report = verify(original, candidate, timeout=timeout)
    if report.error:
        return f"unchecked: {report.error[:60]}"
    if not report.compiled_optimized:
        return "does not compile"
    if not report.equivalent:
        return "different output"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--corpus", type=Path, default=Path("cleaned/merged_cleaned.jsonl"))
    parser.add_argument("--out", type=Path,
                        default=Path("my_data_annotation/recursion_optimization/verified.jsonl"))
    parser.add_argument("--limit", type=int, default=300, help="functions to attempt")
    parser.add_argument("--samples", type=int, default=6, help="attempts per function")
    parser.add_argument("--max-lines", type=int, default=40)
    parser.add_argument("--task", choices=("optimize", "iterate", "auto"), default=TASK)
    parser.add_argument(
        "--min-calls", type=int, default=2,
        help="Skip functions with fewer recursive calls. Memoisation only pays "
             "where subproblems overlap, and a single tail call has none: 218 of "
             "582 corpus functions are that shape and can gain nothing.",
    )
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--port", type=int, default=8101)
    parser.add_argument("--n-predict", type=int, default=700)
    parser.add_argument("--backend", choices=("llama", "hf", "api"), default="llama")
    parser.add_argument("--env", type=Path, default=Path(".env"),
                        help="api backend: provider credentials, same file probe_teacher reads")
    parser.add_argument("--provider", default="azure-saffi",
                        help="api backend: provider key inside --env")
    parser.add_argument("--providers", nargs="+",
                        help="api backend: provider keys to rotate across, e.g. gemini gemini2")
    parser.add_argument("--model", default="gpt-oss-120b",
                        help="api backend: model id to ask")
    parser.add_argument("--rpm", type=int, default=10,
                        help="api backend: calls per minute, matched to the tier's throttle")
    parser.add_argument("--batch", type=int, default=4,
                        help="hf backend: sequences per forward pass, halved on OOM")
    parser.add_argument("--base", default="Qwen/Qwen2.5-Coder-1.5B-Instruct",
                        help="hf backend: base model the adapter was trained on")
    parser.add_argument("--adapter", default=None,
                        help="hf backend: LoRA adapter directory, or omit for the base model")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Retry functions recorded in OUT.attempted.json but not verified")
    args = parser.parse_args()

    functions = drivable_recursive(args.corpus, args.max_lines)
    if args.min_calls > 1 and args.task == "optimize":
        before = len(functions)
        functions = [f for f in functions if recursive_call_count(f) >= args.min_calls]
        print(f"{before - len(functions)} functions dropped: fewer than "
              f"{args.min_calls} recursive calls, so nothing to memoise")
    functions = functions[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if args.out.exists():
        for line in args.out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["code"])
    attempted = args.out.with_suffix(".attempted.json")
    tried: set[str] = set(json.loads(attempted.read_text())) if attempted.exists() else set()
    failures = args.out.with_suffix(".failures.jsonl")

    skipped = set() if args.retry_failed else tried
    todo = [code for code in functions if code not in done and code not in skipped]
    print(f"{len(functions)} drivable recursive functions, {len(done)} already verified, "
          f"{len(tried) - len(done)} already failed -> {len(todo)} to attempt")
    if not todo:
        return

    process = None
    generator = None
    api_generators: list[APIGenerator] = []
    api_cycle = None
    if args.backend == "hf":
        generator = HFGenerator(args.base, args.adapter, batch=args.batch)
    elif args.backend == "api":
        providers = provider_names(args.provider, args.providers)
        api_generators = [
            APIGenerator(args.env, provider, args.model, args.rpm, TASK)
            for provider in providers
        ]
        api_cycle = cycle(api_generators)
        total_rpm = args.rpm * len(api_generators)
        model_names = ", ".join(f"{item.provider}:{item.model}" for item in api_generators)
        print(f"proposing via {model_names}, "
              f"{args.rpm}/min each ({total_rpm}/min total)")
    else:
        process = subprocess.Popen(
            ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
             "-t", "8", "--no-warmup"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    def attempts(code: str, task: str) -> list[str]:
        """This function's raw samples, however they were produced.

        The GPU backend generates the whole batch up front rather than stopping
        at the first success. Sampling `args.samples` in one pass costs about
        what one costs, so an early exit would save nothing and complicate the
        only part of this that has to stay obvious.
        """
        if api_cycle is not None:
            # Takes the source, not the rendered prompt: it sends real chat
            # roles rather than posting Qwen's template markers as message text.
            return [
                next(api_cycle)._one(code, args.n_predict, args.temperature, task)
                for _ in range(args.samples)
            ]
        if generator is not None:
            return generator.samples(
                build_prompt(code, task), args.samples, args.n_predict, args.temperature
            )
        return [
            complete(args.port, build_prompt(code, task), args.n_predict, args.temperature, seed=n)
            for n in range(args.samples)
        ]

    kept = 0
    try:
        if process is not None:
            wait_for_server(args.port)
        for index, code in enumerate(todo):
            task = task_for_code(code, args.task)
            reasons = []
            produced = attempts(code, task) if generator is not None or api_cycle is not None else None
            for sample in range(args.samples):
                if produced is not None:
                    text = produced[sample]
                else:
                    text = complete(args.port, build_prompt(code, task), args.n_predict,
                                    args.temperature, seed=sample)
                candidate = extract_candidate(text)
                if not candidate:
                    reasons.append("no code found")
                    continue
                problem = judge(code, candidate, args.timeout)
                if problem is None:
                    with args.out.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps({
                            "task": task, "language": "cpp",
                            "code": code, "improved_code": candidate,
                            "verified": "compiled and ran with identical output",
                            "attempt": sample,
                        }, ensure_ascii=False) + "\n")
                    kept += 1
                    reasons.append("KEPT")
                    break                      # one verified rewrite per function is enough
                reasons.append(problem)
            tried.add(code)
            # Written every function, so a kill does not lose the record of what
            # was already paid for.
            attempted.write_text(json.dumps(sorted(tried)), encoding="utf-8")
            mark = "KEPT" if reasons and reasons[-1] == "KEPT" else reasons[-1] if reasons else "-"
            if mark != "KEPT":
                with failures.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({
                        "task": task, "code": code, "reasons": reasons, "final": mark,
                    }, ensure_ascii=False) + "\n")
            print(f"  [{index + 1:>4}/{len(todo)}] kept {kept:>4}  {mark}")
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=30)

    print(f"\n{'=' * 72}")
    print(f"verified rows written: {kept}  (total in {args.out}: {len(done) + kept})")
    print("Every row compiled, ran, and printed what the recursive version printed.")


if __name__ == "__main__":
    main()
