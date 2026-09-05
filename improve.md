Do it in this order. Do not jump straight to more fine-tuning.

**Phase 1: Finish Training Repo Proof**
You already started this in:

```bash
cd /Volumes/Data/fyp8th_clean
```

Run current tests:

```bash
.venv/bin/python -m pytest tests/test_optimization_routing.py tests/test_optimization_pairs.py tests/test_prompt.py tests/test_task_prompt.py -q
.venv/bin/python -m ruff check src/qwen_cpp_review/optimization_routing.py src/qwen_cpp_review/prompt.py scripts/build_optimize_dataset.py
```

Then generate more verified optimization data:

```bash
.venv/bin/python scripts/build_optimize_dataset.py \
  --task auto \
  --limit 100 \
  --samples 5 \
  --backend api \
  --model gemini-3.5-flash-lite
```

Only keep rows that pass verification.

**Phase 2: Improve Comments And Explanation Data**
For comments/explanation, clean training examples before training:

```text
keep:
- comments attached to real submitted code lines
- explanations that match code behavior
- short, clear explanations

remove:
- invented comments
- wrong recursion claims
- wrong stack/queue/map claims
- fake complexity claims
- long generic explanations
```

You already have checkers for this area:

```bash
.venv/bin/python -m pytest \
  tests/test_checked_response.py \
  tests/test_line_anchoring.py \
  tests/test_anchor_repair.py \
  tests/test_best_of.py -q
```

Use those same rules when preparing new data.

**Phase 3: Train Separate Tasks**
Do not mix everything blindly.

Use task names like:

```text
line_comments
explanation
optimize
iterate
```

For optimization data:

```json
{
  "task": "iterate",
  "language": "cpp",
  "code": "...recursive code...",
  "improved_code": "...verified loop code..."
}
```

For explanation:

```json
{
  "task": "explanation",
  "language": "cpp",
  "code": "...",
  "explanation": "This function..."
}
```

For comments:

```json
{
  "task": "line_comments",
  "language": "cpp",
  "code": "...",
  "line_comments": [
    {
      "line": 3,
      "code": "sum += arr[i];",
      "comment": "Adds the current element to the running total."
    }
  ]
}
```

**Phase 4: Evaluate Before Using In FastAPI**
Make one eval file with hard examples:

```text
factorial
GCD
count digits
sum to n
Fibonacci
binary search
linked list traversal
tree traversal
flood fill
backtracking
misleading variable names
noise variable names
```

Pass condition:

```text
comments/explanation: no false claims
optimization: compile + run + same output
recursion-to-loop: no self-call remains
```

**Phase 5: Port To FastAPI**
Only after training repo passes.

In backend `/optimize`:

```text
detect recursion
-> choose prompt
-> generate candidate
-> reject if still recursive
-> compile original + candidate
-> run same tests
-> compare output exactly
-> return candidate only if verified
```

In backend `/analyze`:

```text
model output
-> anchor comments by quoted code
-> drop invented comments
-> check false claims
-> return only input_code, commented_code, explanation, needs_review
```

Most important rule:

```text
Model suggests.
Backend verifies.
Only verified output is trusted.
```

Your next practical step should be: generate 100 `--task auto` candidates and see how many verified rows you get.