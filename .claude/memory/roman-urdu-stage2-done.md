---
name: roman-urdu-stage2-done
description: "Roman Urdu stage 2 is trained and measured — t5-stage2-c is the only model kept, chrF 76.14 with 100% placeholder retention"
metadata: 
  type: project
---

Stage 2 finished 2026-08-28. **`urdu_output/roman-model/t5-stage2-c` is the only
Urdu model kept** — everything else was deleted (11 GB freed, 233 MB left).

Measured on the held-out test split (62 pairs, 56 placeholders) with
`roman_urdu/compare_models.py`:

| | chrF | placeholders | register probes |
| --- | ---: | ---: | ---: |
| stage 1 | 51.34 | 87.5% | 4/5 |
| **stage2-c** (20ep, batch 16, lr 3e-4) | **76.14** | **100%** | **5/5** |

**Why:** +24.8 chrF *and* placeholder retention to 100%. The failure mode to
guard against was chrF rising while the `⟦0⟧` identifiers got mangled — the
product depends on those surviving. It did not happen.

**Speed** (61M params, this CPU, 8 threads, 20 sentences):
beam=4 median **1,144 ms**/sentence (43.6 tok/s); greedy median **708 ms**
(68.6 tok/s); model loads in 0.2s. The quality numbers above used beam=4, so a
greedy deployment is a different measurement.

**How to apply:**
- Trained from 1,249 hand-annotated pairs in
  `my_data_annotation/roman_urdu/data/` (1,125 / 62 / 62).
- It is a full T5, not an adapter — runs with stage 1 deleted.
- Stage 1 survives only as `dist/urdu-stage1-model.zip` (215 MB) and the Kaggle
  dataset `urdu-model01`. A future stage-2 run fine-tunes **from that**, so do
  not delete the zip; retraining stage 1 from ERUPD is an hour of GPU.
- Checkpoints downloaded fresh from Kaggle need `extra_special_tokens`,
  `backend` and `is_local` removed from `tokenizer_config.json` — saved as a
  list where transformers 4.57 wants a dict, so they will not load otherwise.
  The `<extra_id_N>` sentinels are native to T5, nothing is lost.
- Two corrections worth not re-deriving: `3e-4` beat the gentler `1e-4`
  (1,125 rows over 20 epochs is too little training to overwrite stage 1), and
  the old note that stage 1 says *tayyar karta hai* / *saaf karta hai* was a
  **greedy-decoding artefact** — with beams it keeps the English verb.

**Next, if wanted:** `roman_urdu/corpus/batch_003.txt` holds 1,000 more
un-annotated drafts. But stage 2 already works at 1,249 pairs, so measure before
spending the hours — the next thousand would have to beat 76.14 chrF at 100%
placeholders to be worth it.

Related: [[write-the-fyp-report]], [[wire-best-of-into-backend]]
