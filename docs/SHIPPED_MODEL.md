# What the shipped GGUF was built from

_A copy of this lives at `models/27aug01/PROVENANCE.md`, beside the adapter.
`models/` is gitignored, so this tracked copy is the one that survives a clone._

`models/gguf/qwen-cpp-review-v3-q4_k_m.gguf` — the model the product runs — was
merged from:

    models/27aug01/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter
    global_step 750 of 877 · adapter_model.safetensors md5 60e5d43144d787d9

**Verified, not assumed** (2026-09-05). The directory held two different adapters
— `best_adapter` at step 750 and `last_adapter` at step 877 — and nothing on disk
recorded which one was merged. So `best_adapter` was re-merged (fp32, CPU),
converted to f16 GGUF and quantized Q4_K_M with the same pipeline, and the result
compared against the shipped file:

    tensor payload (last 900 MB, past all metadata)
      shipped  6790b33ccc7ab7cfe5aa5b56a104d942
      rebuilt  6790b33ccc7ab7cfe5aa5b56a104d942     identical

The two files differ by exactly 64 bytes, all of it in the header: GGUF stores
`general.name` from the merge directory, so the shipped file says "Merged v3"
and the rebuild said "Try Best". **Do not compare these files by whole-file
md5** — and do not compare a slice that starts inside the first ~5 MB either,
because GGUF keeps Qwen's 151,936-token vocabulary in the metadata block and a
slice reaching into it will differ for reasons that have nothing to do with the
weights. Compare the tail.

To rebuild the GGUF from this adapter (`merge_lora.py` needs `trl`, which is not
installed in a CPU-only checkout, so merge directly):

    python -c "
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    A='models/27aug01/outputs/qwen2.5-coder-1.5b-cpp-review-qlora/best_adapter'
    tok=AutoTokenizer.from_pretrained(A, trust_remote_code=True, use_fast=True)
    b=AutoModelForCausalLM.from_pretrained('models/Qwen2.5-Coder-1.5B-Instruct',
                                           torch_dtype=torch.float32, trust_remote_code=True)
    PeftModel.from_pretrained(b,A).merge_and_unload().save_pretrained('merged-v3')
    tok.save_pretrained('merged-v3')"
    python ../llama.cpp/convert_hf_to_gguf.py merged-v3 --outfile merged-v3/f16.gguf --outtype f16
    ../llama.cpp/build/bin/llama-quantize merged-v3/f16.gguf out-q4_k_m.gguf Q4_K_M

Name the directory `merged-v3` and the header matches too.

`last_adapter` (step 877) was deleted on 2026-09-05: never evaluated, never
shipped, not cited by the report. Optimizer, scheduler and RNG state were also
deleted — they exist only to resume training, and this project has five null
results saying not to.
