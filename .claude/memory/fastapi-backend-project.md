---
name: fastapi-backend-project
description: "The project has a separate FastAPI backend at /Volumes/Data/saffi/fyp_backend that serves the Android app; keep serving work separate from training work"
metadata:
  type: project
---

The FastAPI backend is a **separate repo** from this training project:

| repo | path | job |
| --- | --- | --- |
| training/evaluation | `/Volumes/Data/fyp8th_clean` | dataset building, QLoRA training, evaluation, GGUF conversion, Roman Urdu model training |
| backend/serving | `/Volumes/Data/saffi/fyp_backend` | FastAPI endpoints, auth, history, Android response contract, model serving orchestration |

Work in one repo at a time. Do not fix serving bugs by changing training code,
and do not fix training/evaluation problems by changing backend endpoints.

## What the backend does

It is a FastAPI backend for an Android C++ review app.

- `POST /analyze` takes C++ and publicly returns only `input_code`,
  `commented_code`, `explanation`, and `needs_review`. Deterministic static
  analysis, suggestions, documentation, optional diff analysis, optional Roman
  Urdu translation, line-comment records, anchor stats, and `verified_comments`
  are internal pipeline data and are not returned to the client. Public
  explanations also omit time and space complexity details.
- `POST /optimize` asks for a faster rewrite, then compiles and runs the rewrite
  beside the original. If equivalence cannot be proven, the user's original code
  is returned rather than unsafe code.
- `GET /analyze/history` returns paginated analysis history for the
  authenticated user.
- Auth endpoints are `/auth/register`, `/auth/login`, `/auth/me`, and
  `/auth/logout`.
- `GET /health` is cheap process liveness. `GET /ready` checks whether this
  machine can actually answer requests: model file, inference server, and C++
  compiler.

Auth and history are SQLite-backed. `app.db`, `.env`, `models/`, and `logs/`
are not committed.

## Serving architecture

The backend is two processes:

1. API process: `app.main:app`, normally on port `8080`.
2. llama.cpp server: `llama-server`, normally on port `8081`, holding the
   Qwen GGUF in memory.

The API does **not** load the Qwen weights in Python. For the current backend
(`MODEL_BACKEND=qwen_gguf`), `model_service.run_model()` calls
`qwen_service`, which POSTs to llama-server over HTTP using the standard
library. The legacy `codet5` backend is still present and is the code default,
but its checkpoint is no longer on this machine.

Useful backend commands:

```bash
cd /Volumes/Data/saffi/fyp_backend
uv sync
./run_model_server.sh --bg
PORT=8080 ./runserver.sh
curl -s localhost:8080/ready | python3 -m json.tool
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check app
.venv/bin/python -m mypy app
```

`runserver.sh` defaults to `PORT=8000`, while the docs and curl examples use
`8080`. Set `PORT=8080` or adjust the URL before assuming the server failed.

## The backend invariant

The model returns comments as records:

```json
{ "line": 6, "code": "total /= 10;", "comment": "Remove the least-significant digit." }
```

The backend renders `commented_code` by appending comments to the user's
submitted source. It should never show a model-reconstructed copy of the code.
Line numbers are unreliable, but quoted `code` text is reliable, so anchors are
relocated by quote and dropped when the quote is not in the submission.

This proves a comment is attached to a real submitted line. It does not prove
the comment is true. The backend also runs semantic comment validation for some
provably false claims, but free prose still needs caution.

## Analyze pipeline

`app/routers/analyze.py` orchestrates the request:

```text
static_analyze
  -> model_service.run_model
       qwen path: qwen_service -> llama-server -> anchored comments
  -> comment_service / explanation_service / review_service / documentation_service
  -> syntax gate when needed
  -> diff_service when old_code is present
  -> translation_service when output_language is roman_urdu
  -> record_history
```

The static facts feed the response and rule-based services. They are not
prepended to the Qwen prompt because the checkpoints were tuned on fixed prompt
wording and drift when extra facts are inserted.

## Android/API contract

The public `/analyze` response is intentionally small. Existing Android fields
must keep their shape and order:

- `input_code`
- `commented_code`
- `explanation`
- `needs_review`

Do not add internal/debug fields back to the public response without
coordinating the Android client.

`needs_review` keeps its name and boolean type because the Android client reads
it. It is used to flag output when anchors/comments were dropped or semantic
checks rejected something.

## Roman Urdu in the backend

The backend already has `output_language` support and a
`translation_service.to_roman_urdu` hook. As of 2026-08-29, it tries the
backend-local trained T5 model first:

```text
/Volumes/Data/saffi/fyp_backend/models/roman-model/t5-stage2-c
```

The model files match the training repo's
`urdu_output/roman-model/t5-stage2-c` weights and tokenizer. The backend serving
copy is intentionally trimmed to five inference files: `config.json`,
`generation_config.json`, `model.safetensors`, `tokenizer.json`, and
`tokenizer_config.json`. It should not contain `checkpoint-*` directories,
optimizer/scheduler/RNG state, `training_args.bin`, `.complete`, or `.DS_Store`.

The backend copy's `tokenizer_config.json` has the known bad download keys removed:
`extra_special_tokens`, `backend`, and `is_local`.

If the model is missing or errors, the backend falls back to the existing
rule/frame translator. If the model drops a protected placeholder, the masking
layer returns English rather than unsafe Roman Urdu.

Only translate prose fields such as `comment` and `explanation`. Do not let a
translation model touch `line` or quoted `code`, because anchor validity is the
core product guarantee.

## Known backend caveats

Read `/Volumes/Data/saffi/fyp_backend/docs/KNOWN_ISSUES.md` before reporting a
backend issue as new.

Current caveats from the backend handover:

- Tests: backend `CLAUDE.md` records about 90 tests. Some end-to-end tests need
  `llama-server` running; compiler-dependent tests skip if `c++` is absent.
- Ruff: `app` is expected to be clean.
- Mypy: strict mode has six known pre-existing errors in
  `equivalence.py`, `qwen_service.py`, `health.py`, and `model_service.py`.
- Python: use Python 3.11 for backend work. `torch==2.0.1` has no useful
  Python 3.12/3.13 path here, and NumPy must stay `<2` for the torch ABI.
- `@app.on_event` deprecation in `app/main.py` is known.
- The backend repo currently has a `.git/index.lock`; do not assume git
  operations there are clean until checking.

Related: [[wire-best-of-into-backend]], [[roman-urdu-stage2-done]],
[[recursion-optimization-routing]], [[cpu-only-local-machine]],
[[write-the-fyp-report]]
