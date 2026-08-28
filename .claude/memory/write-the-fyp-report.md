---
name: write-the-fyp-report
description: The report is the actual FYP deliverable and every measurement it needs already exists — no further training is required
metadata: 
  type: project
---

The report is what remains. `docs/WRITEUP_GUIDE.md` maps every chapter to the
file already holding its material; `docs/DETECTABILITY.md` is a written chapter
waiting to be placed. **No further training run is required for it.**

**Why:** measurements keep being deferred behind "one more run", and the runs
keep returning p = 1.0. As of 2026-08-28 there are nine measured findings, four
of which did not exist the day before.

**How to apply — the findings, with where each lives:**

1. Fine-tuning bought format, not comprehension — 0/20 to 20/20 valid JSON,
   defect finding flat (`test_results/ablation_v2.md`)
2. **159 execution-verified rows moved algorithmic rewriting 17% to 42%**,
   p = 5.2e-04, from 1.9% of the mixture, where 18,935 asserted `improve` rows
   holding 37% of the loss budget did not
3. **Scaling those to 253 pairs did nothing**, p = 1.0000 — the gain came from
   *introducing* verification, not scaling it (`model_improvement/REPORT.md`)
4. **A prompt change doubles defect finding for free** — 8/55 to 16/55, and
   *reduces* defects invented in correct code from 1 to 0
   (`model_improvement/step3_prompt/`)
5. **best_of sampling removes 83% of false statements** — 24 to 4 objections,
   6/20 to 16/20 clean, p = 4.88e-04 (`model_improvement/best_of/`)
6. Renaming every variable misleadingly costs 0 points; single letters cost 12
7. The remaining gap is one transformation, not four data shapes: `stack` 3/20
   against `table` 12/20 and `accumulator` 14/28
8. **Roman Urdu stage 2**: 1,249 hand-annotated pairs took the translator from
   chrF 51.34 to **76.14** with placeholder retention **87.5% → 100%** on a
   held-out split (`test_results/roman_urdu_stage2_comparison.json`)
9. Greedy decoding is not reproducible across machines — the same weights score
   7/55 on the Mac and 9/55 on Linux, which is larger than most effects measured

**Traps to avoid:**
- Do not promise bug detection in Chapter 1. The report does not deliver it,
  says so, and is stronger for it — but only if Chapter 1 never claimed it.
- Do not write "with more time and data we would have improved accuracy". You
  know more data would not have: 159 to 253 gave p = 1.0.
- Say "no detectable improvement (n=55)", not "no improvement".
- Cite `arXiv:2509.20837` for its verification-ceiling argument, not as
  "unverified data is bad" — that is not what the paper says.
- Do not conclude 1.5B is too small; R2Vul refutes it. The constraint was the
  training signal.

Related: [[wire-best-of-into-backend]], [[cpu-only-local-machine]]
