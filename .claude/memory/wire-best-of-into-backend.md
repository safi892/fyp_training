---
name: wire-best-of-into-backend
description: best_of sampling is measured and working in the training repo but the backend does not call it — pending work for a backend session
metadata: 
  node_type: memory
  type: project
  originSessionId: 35610843-d5fd-4636-a739-e08b0471bd46
  modified: 2026-08-28T03:22:53.955Z
---

`best_of` in `src/qwen_cpp_review/checked_response.py` (training repo, branch
`language`, commit `ea8a6ad`) samples the model several times and lets the
checks pick which answer ships. **Measured 2026-08-27** over the twenty
out-of-distribution seed programs, five samples each, sample 0 at temperature 0
so the baseline is what serving does today:

    total objections   24 -> 4
    clean answers    6/20 -> 16/20
    improved 12, unchanged 8, worse 0, McNemar p = 4.88e-04

**The backend does not use it.** Until it does, this is true of the repository
and not of the product — the same status `check_response` itself has.

**Why:** 83% of false statements removed on the hardest set available, with no
training, no API and no GPU. Sample 0 was the best answer only 6/20 times, so in
fourteen cases the deployed answer was not the best one the model produced.

**How to apply:**
- Do this in the **backend repo** (`fyp_backend`), in its own session.
  `CLAUDE.md` is explicit that holding both repos at once leads to proposing
  training changes for serving bugs.
- Cost is 5x inference. The model is 940 MB at ~12 tok/s on CPU, which is what
  makes that affordable.
- Two design points that a reimplementation would get wrong: discarding samples
  that said nothing must come **before** ranking on objections, or the empty
  answer wins every time; and `needs_review` still ships flawed output with a
  warning, so serving nothing is worse than serving something flagged.
- Four of the twenty stayed flawed with an objection in *every* sample. Sampling
  cannot reach a persistent error, so this is a filter, not a fix.

Related: [[cpu-only-local-machine]], [[write-the-fyp-report]]
