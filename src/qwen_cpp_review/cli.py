from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Iterable

import torch
from torch import nn
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from trl import SFTTrainer

from qwen_cpp_review.config import AppConfig
from qwen_cpp_review.dataset import load_review_dataset, prepare_sft_dataset
from qwen_cpp_review.logging_utils import configure_logging
from qwen_cpp_review.metrics import perplexity
from qwen_cpp_review.model import create_bnb_config, load_model_for_qlora
from qwen_cpp_review.prompt import format_prompt_without_response
from qwen_cpp_review.resume import (
    MODE_SCRATCH,
    VALID_MODES,
    check_lora_compatibility,
    inspect_checkpoint,
    list_checkpoints,
    resolve_resume_plan,
)
from qwen_cpp_review.tokenizer import load_tokenizer
from qwen_cpp_review.trainer import build_sft_config, build_trainer, train

LOGGER = logging.getLogger(__name__)


def train_main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune Qwen2.5-Coder with QLoRA.")
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    parser.add_argument(
        "--resume-mode",
        choices=VALID_MODES,
        default=None,
        help=(
            "Override training.resume_mode. auto=strongest mode the checkpoint supports, "
            "exact=require full optimizer state, state=keep step/LR but reset the optimizer, "
            "adapter=weights only, scratch=start at step 0."
        ),
    )
    parser.add_argument(
        "--resume-from",
        default=None,
        help="Checkpoint directory to continue from (default: newest under output_dir).",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Start from step 0 and archive anything already in output_dir.",
    )
    args = parser.parse_args()
    configure_logging()
    config = AppConfig.from_yaml(args.config)
    if args.resume_mode:
        config.training.resume_mode = args.resume_mode
    if args.resume_from:
        config.training.resume_from_checkpoint = args.resume_from
    if args.fresh:
        config.training.resume_mode = MODE_SCRATCH
        config.training.resume_from_checkpoint = None
        config.training.initial_adapter_path = None
        config.training.overwrite_output_dir = True
    tokenizer = load_tokenizer(config.model)
    train(config, tokenizer)


def resume_status_main() -> None:
    """Print the resume decision without loading a model or touching a GPU."""
    parser = argparse.ArgumentParser(description="Show how the next run would resume.")
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    args = parser.parse_args()
    configure_logging()
    config = AppConfig.from_yaml(args.config)

    output_dir = Path(config.training.output_dir)
    checkpoints = list_checkpoints(output_dir)
    print(f"Output dir : {output_dir}")
    print(f"Checkpoints: {[path.name for path in checkpoints] or 'none'}")
    for path in checkpoints:
        info = inspect_checkpoint(path)
        print(
            f"  {path.name:>18}  step={info.resume_step:<6} adapter={info.has_adapter} "
            f"state={info.has_trainer_state} optim={info.has_optimizer} "
            f"sched={info.has_scheduler} written_with_optim={info.optim}"
        )
    plan = resolve_resume_plan(config, dry_run=True)
    check_lora_compatibility(plan, config.lora)
    print(plan.banner())


def evaluate_main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a QLoRA checkpoint.")
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    parser.add_argument("--adapter", default=None)
    args = parser.parse_args()
    configure_logging()
    config = AppConfig.from_yaml(args.config)
    tokenizer = load_tokenizer(config.model)
    if args.adapter:
        dataset = prepare_sft_dataset(load_review_dataset(config.data), config.data, tokenizer)
        model = load_model_for_qlora(config.model, config.training.gradient_checkpointing)
        model = PeftModel.from_pretrained(model, args.adapter)
        eval_dataset = dataset["validation"] if "validation" in dataset else dataset["train"]
        trainer = SFTTrainer(
            model=model,
            args=build_sft_config(config),
            eval_dataset=eval_dataset,
            processing_class=tokenizer,
        )
    else:
        trainer = build_trainer(config, tokenizer)
    metrics = trainer.evaluate()
    if "eval_loss" in metrics:
        metrics["perplexity"] = perplexity(metrics["eval_loss"])
    LOGGER.info(json.dumps(metrics, indent=2))


def inference_main() -> None:
    parser = argparse.ArgumentParser(description="Generate C++ review output.")
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    parser.add_argument("--model", default=None, help="Merged model path or base model path.")
    parser.add_argument("--adapter", default=None, help="LoRA adapter path.")
    parser.add_argument("--code-file", default=None)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--batch-jsonl", default=None)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()
    configure_logging()
    config = AppConfig.from_yaml(args.config)
    model_name = args.model or config.model.model_name_or_path
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = _load_inference_model(model_name, args.adapter)
    model.eval()

    generation_kwargs = {
        "max_new_tokens": args.max_new_tokens or config.generation.max_new_tokens,
        "temperature": args.temperature or config.generation.temperature,
        "top_p": args.top_p or config.generation.top_p,
        "top_k": args.top_k or config.generation.top_k,
        "repetition_penalty": config.generation.repetition_penalty,
        "do_sample": (args.temperature or config.generation.temperature) > 0,
        "pad_token_id": tokenizer.pad_token_id,
    }

    for code in _iter_inputs(args):
        prompt = format_prompt_without_response(
            code,
            config.data.output_fields,
            style=config.data.prompt_style,
            tokenizer=tokenizer,
        )
        if args.stream:
            _stream_generate(model, tokenizer, prompt, generation_kwargs)
        else:
            print(_generate(model, tokenizer, prompt, generation_kwargs))


def merge_main() -> None:
    parser = argparse.ArgumentParser(description="Merge a LoRA adapter into the base model.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    configure_logging()
    tokenizer = AutoTokenizer.from_pretrained(args.adapter, trust_remote_code=True, use_fast=True)
    # Merging is arithmetic on the weights and needs no GPU, so it must work on
    # a machine without one. torch.cuda.is_bf16_supported() raises rather than
    # returning False when torch has no CUDA at all, and float16 on CPU is both
    # slow and lossy, so pick per device.
    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        device_map = "auto"
    else:
        dtype = torch.float32
        device_map = None
    LOGGER.info("merging on %s in %s", "cuda" if device_map else "cpu", dtype)
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=dtype,
        device_map=device_map,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, args.adapter)
    merged = model.merge_and_unload()
    merged.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)
    LOGGER.info("saved merged model to %s", args.output_dir)


def export_onnx_main() -> None:
    parser = argparse.ArgumentParser(description="Export a merged causal LM to ONNX.")
    parser.add_argument("--model", required=True, help="Merged model directory or HF model id.")
    parser.add_argument("--output", default="outputs/model.onnx")
    parser.add_argument("--opset", type=int, default=17)
    parser.add_argument("--max-length", type=int, default=128)
    args = parser.parse_args()
    configure_logging()

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
    )
    model.eval()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    inputs = tokenizer(
        "Analyze this C++ code:\nint main(){return 0;}",
        return_tensors="pt",
        truncation=True,
        max_length=args.max_length,
    )
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    export_model = CausalLMOnnxWrapper(model).eval()

    torch.onnx.export(
        export_model,
        (inputs["input_ids"], inputs["attention_mask"]),
        output,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "logits": {0: "batch", 1: "sequence"},
        },
        opset_version=args.opset,
        do_constant_folding=True,
    )
    LOGGER.info("saved ONNX model to %s", output)


class CausalLMOnnxWrapper(nn.Module):
    def __init__(self, model: nn.Module) -> None:
        super().__init__()
        self.model = model

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        return self.model(input_ids=input_ids, attention_mask=attention_mask).logits


def _load_inference_model(model_name: str, adapter: str | None):
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=create_bnb_config() if torch.cuda.is_available() else None,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
    )
    if adapter:
        model = PeftModel.from_pretrained(model, adapter)
    return model


def _iter_inputs(args: argparse.Namespace) -> Iterable[str]:
    if args.batch_jsonl:
        with Path(args.batch_jsonl).open() as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)["code"]
        return
    if args.code_file:
        yield Path(args.code_file).read_text()
        return
    if args.prompt:
        yield args.prompt
        return
    raise SystemExit("Provide --code-file, --prompt, or --batch-jsonl.")


def _generate(model, tokenizer, prompt: str, generation_kwargs: dict) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, **generation_kwargs)
    generated = output[0, inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(generated, skip_special_tokens=True)


def _stream_generate(model, tokenizer, prompt: str, generation_kwargs: dict) -> None:
    import threading

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    thread = threading.Thread(
        target=model.generate,
        kwargs={**inputs, **generation_kwargs, "streamer": streamer},
    )
    thread.start()
    for token in streamer:
        print(token, end="", flush=True)
    print()
    thread.join()


def export_eval_dataset_main() -> None:
    parser = argparse.ArgumentParser(description="Render the configured dataset to SFT text.")
    parser.add_argument("--config", default="configs/train_qlora.yaml")
    parser.add_argument("--output", default="outputs/rendered_dataset")
    args = parser.parse_args()
    config = AppConfig.from_yaml(args.config)
    tokenizer = load_tokenizer(config.model)
    dataset = prepare_sft_dataset(load_review_dataset(config.data), config.data, tokenizer)
    dataset.save_to_disk(args.output)
