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
from pathlib import Path

from qwen_cpp_review.claim_checks import recursive_functions
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


def build_prompt(code: str, task: str = TASK) -> str:
    instruction = (
        "Analyze the following C++ code.\n\nLanguage: cpp\n\n"
        f"Generate:\n- Improved code ({TASK_FIELD_HINTS[task]['improved_code']})\n\n"
        "Return a single JSON object using the requested field names."
    )
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\n\n### Code\n\n```cpp\n{code}\n```<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


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
    parser.add_argument("--task", choices=("optimize", "iterate"), default=TASK)
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
    parser.add_argument("--backend", choices=("llama", "hf"), default="llama")
    parser.add_argument("--batch", type=int, default=4,
                        help="hf backend: sequences per forward pass, halved on OOM")
    parser.add_argument("--base", default="Qwen/Qwen2.5-Coder-1.5B-Instruct",
                        help="hf backend: base model the adapter was trained on")
    parser.add_argument("--adapter", default=None,
                        help="hf backend: LoRA adapter directory, or omit for the base model")
    args = parser.parse_args()

    functions = drivable_recursive(args.corpus, args.max_lines)
    if args.min_calls > 1:
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

    todo = [code for code in functions if code not in done and code not in tried]
    print(f"{len(functions)} drivable recursive functions, {len(done)} already verified, "
          f"{len(tried) - len(done)} already failed -> {len(todo)} to attempt")
    if not todo:
        return

    process = None
    generator = None
    if args.backend == "hf":
        generator = HFGenerator(args.base, args.adapter, batch=args.batch)
    else:
        process = subprocess.Popen(
            ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
             "-t", "8", "--no-warmup"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    def attempts(code: str) -> list[str]:
        """This function's raw samples, however they were produced.

        The GPU backend generates the whole batch up front rather than stopping
        at the first success. Sampling `args.samples` in one pass costs about
        what one costs, so an early exit would save nothing and complicate the
        only part of this that has to stay obvious.
        """
        if generator is not None:
            return generator.samples(
                build_prompt(code), args.samples, args.n_predict, args.temperature
            )
        return [
            complete(args.port, build_prompt(code), args.n_predict, args.temperature, seed=n)
            for n in range(args.samples)
        ]

    kept = 0
    try:
        if process is not None:
            wait_for_server(args.port)
        for index, code in enumerate(todo):
            reasons = []
            produced = attempts(code) if generator is not None else None
            for sample in range(args.samples):
                if produced is not None:
                    text = produced[sample]
                else:
                    text = complete(args.port, build_prompt(code), args.n_predict,
                                    args.temperature, seed=sample)
                candidate = extract_candidate(text)
                if not candidate:
                    reasons.append("no code found")
                    continue
                problem = judge(code, candidate, args.timeout)
                if problem is None:
                    with args.out.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps({
                            "task": args.task, "language": "cpp",
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
