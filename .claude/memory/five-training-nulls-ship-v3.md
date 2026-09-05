---
name: five-training-nulls-ship-v3
description: Five training-data interventions have now returned no measurable gain; v3 (models/27aug01) is still the checkpoint to ship
metadata:
  type: project
---

As of 2026-09-05 there are **five** C++ checkpoints. v3 (`models/27aug01`) is
still the one to ship; v4 and v5 both returned nothing.

**v5 = `models/archive`**, trained on `task_mixture_auto_optimization.jsonl`,
68,058 rows (v4's 59,439 + 8,619), 10.5 GPU-hours, run completed. Measured on
this Linux box against same-machine v3/v4 baselines:

| | v3 | v4 | v5 | v3 → v5 |
| --- | ---: | ---: | ---: | --- |
| rewriting (68 paired cells) | 29/68 | 34/68 | 32/68 | p = 0.5811 |
| problems named | 11/55 | 10/55 | 11/55 | p = 1.0000 |
| truncated / false recursion | 0,1 /20 | 1,1 /20 | 1,1 /20 | p = 1.0000 |

**Why it matters:** the argument for the report is now five training-data nulls
against two inference-time wins (defect-aware prompt 8/55 → 16/55; `best_of`
24 → 4 objections). Do not run another training job hoping for a gain.

**How to apply:**
- Baselines live in `model_improvement/v3_eval/`, `v4_eval/`, `v5_eval/`, all
  measured on this machine. Never compare against `test_results/hard_examples.md`
  or `test_results/seed_annotation.json` — those are Mac-measured and have
  produced a false headline three times.
- `probe_optimization.py` gained a phase 2 after v3/v4 ran, so pair only the 68
  `strategy == "original"` cells across runs.
- **Eval loss is not a comparison across runs** (0.4120 / 0.4076 / 0.4004 for
  v3/v4/v5): each is a different 1% split of a different mixture.
- `merge_lora.py` imports `trl`, which is absent here — merge with
  `transformers` + `peft` directly.
- v5's mixture is not in the repo and no builder emits that name; if another run
  is ever done, commit the mixture or its task histogram first.

Related: [[write-the-fyp-report]], [[cpu-only-local-machine]]
