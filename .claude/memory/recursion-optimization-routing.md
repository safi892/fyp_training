---
name: recursion-optimization-routing
description: "Training-side experiment for routing recursive C++ optimization prompts before porting anything to the FastAPI backend"
metadata:
  type: project
---

Recursion-to-loop optimization is being tested first in the training/evaluation
repo, not directly in the backend:

| repo | path | status |
| --- | --- | --- |
| training/evaluation | `/Volumes/Data/fyp8th_clean` | router and prompt experiment implemented |
| backend/serving | `/Volumes/Data/saffi/fyp_backend` | untouched until training-side result is proven |

## Implemented Training-Side

- Added `src/qwen_cpp_review/optimization_routing.py`.
- Added `--task auto` in `scripts/build_optimize_dataset.py`.
- Added tests in `tests/test_optimization_routing.py`.
- Added builder coverage in `tests/test_optimization_pairs.py`.
- Updated the `iterate` prompt in `src/qwen_cpp_review/prompt.py`.

Routing behavior:

- direct recursion such as factorial, GCD, count-digits, and binary-search
  shape routes to `iterate`.
- branching recursive return such as `fib(n - 1) + fib(n - 2)` routes to
  `optimize` for memoisation / DP.
- recursion mentioned only in comments does not trigger recursion routing.

Important rule: routing only changes the prompt. A rewrite is accepted only
after compile/run/equivalence verification. If verification cannot drive the
code safely, keep the original or mark the result unverified.

## Local GGUF Prompt Probe

First tested with the real local GGUF model on 5 examples: factorial, GCD,
count-digits, Fibonacci, and binary search.

| technique | verified | removed recursion |
| --- | ---: | ---: |
| old `optimize` | 3/5 | 4/5 |
| current `auto` routing | 4/5 | 5/5 |
| short loop prompt | 4/5 | 5/5 |
| step-by-step loop prompt | 3/5 | 5/5 |

Then tested harder renamed-variable cases using `original`, `terse`,
`misleading`, and `noise` names across GCD, count-digits, sum-to-n, and
Fibonacci.

| mode | verified | removed recursion |
| --- | ---: | ---: |
| old `optimize` | 5/16 | 9/16 |
| current `auto` routing | 11/16 | 16/16 |

By rename strategy:

| strategy | old `optimize` | current `auto` |
| --- | ---: | ---: |
| original | 3/4 | 4/4 |
| terse names | 0/4 | 2/4 |
| misleading names | 1/4 | 2/4 |
| noise names | 1/4 | 3/4 |

Findings:

- `auto` improved GCD: old prompt failed, auto generated a correct loop.
- `auto` improved binary-search shape: old prompt stayed recursive, auto
  generated a loop.
- In renamed-variable tests, `auto` improved verified results from 5/16 to
  11/16 and removed recursion in every case.
- Binary search could not be counted verified because the verifier failed on
  the array signature: `unchecked: original: exit -4`.
- `loop_steps` is worse: it introduced an off-by-one bug in `countDigits`, and
  the verifier caught it.
- Renamed GCD and renamed Fibonacci can still produce wrong output, so strict
  compile/run/equivalence verification is still mandatory.

Conclusion: keep `auto` routing. Do not use the step-by-step prompt. The
current `iterate` prompt is better than the old stack-heavy prompt because it
prefers normal `while`/`for` loops for direct recursion and only allows
`std::stack` / `std::queue` when traversal state really needs it.

## Verification Commands Used

```bash
.venv/bin/python -m pytest tests/test_optimization_routing.py tests/test_optimization_pairs.py tests/test_prompt.py tests/test_task_prompt.py -q
.venv/bin/python -m ruff check src/qwen_cpp_review/optimization_routing.py src/qwen_cpp_review/prompt.py scripts/build_optimize_dataset.py tests/test_optimization_routing.py tests/test_optimization_pairs.py
```

Observed result:

- `35 passed`
- Ruff passed

## Backend Porting Note

When porting this to `/Volumes/Data/saffi/fyp_backend`, keep the public
`/optimize` contract unchanged. Use routing only to select the prompt. The
backend must still reject candidates that still recurse, print extra output,
fail compile/run/equivalence, or cannot be safely verified.

Related: [[fastapi-backend-project]], [[wire-best-of-into-backend]]
