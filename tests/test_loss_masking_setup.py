"""Guards for the supervision setup.

The failure these protect against is silent: with the wrong dataset shape the
loss covers the instruction and the input code, the curve still falls, and the
model learns to reproduce prompts. See the `loss-masking-verify` skill.
"""

import json

import pytest

from qwen_cpp_review.config import AppConfig, DataConfig, ModelConfig, TrainingConfig
from qwen_cpp_review.dataset import prepare_sft_dataset
from qwen_cpp_review.prompt import build_prompt_completion
from qwen_cpp_review.trainer import check_supervision_setup

ROW = {
    "code": "int add(int a, int b)\n{\n  return a + b;\n}",
    "language": "cpp",
    "task": "line_comments",
    "line_comments": [{"line": 3, "code": "return a + b;", "comment": "sum them"}],
}


class FakeTokenizer:
    """Mirrors the marker structure of the Qwen chat template."""

    def apply_chat_template(self, conversation, *, tokenize, add_generation_prompt):
        text = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in conversation)
        if add_generation_prompt:
            text += "<|im_start|>assistant\n"
        return text


def config_for(train_on_inputs: bool, *, packing: bool = False, flash: bool = False) -> AppConfig:
    return AppConfig(
        model=ModelConfig(flash_attention=flash),
        data=DataConfig(train_on_inputs=train_on_inputs),
        training=TrainingConfig(packing=packing),
    )


# --- prompt/completion split ------------------------------------------------ #


def test_chat_prompt_ends_where_generation_begins():
    prompt, completion = build_prompt_completion(
        ROW, [], style="chat", tokenizer=FakeTokenizer()
    )

    assert prompt.endswith("<|im_start|>assistant\n")
    assert "line_comments" not in prompt or "Line-by-line" in prompt
    assert json.loads(completion) == {"line_comments": ROW["line_comments"]}


def test_completion_holds_no_prompt_text():
    _, completion = build_prompt_completion(ROW, [], style="chat", tokenizer=FakeTokenizer())

    assert "Analyze the following C++ code" not in completion
    assert "int add(int a, int b)" not in completion


def test_instruction_style_prompt_ends_at_the_response_marker():
    prompt, completion = build_prompt_completion(ROW, [], style="instruction")

    assert prompt.endswith("### Response\n\n")
    assert completion.lstrip().startswith("{")


def test_prompt_and_completion_do_not_overlap():
    prompt, completion = build_prompt_completion(ROW, [], style="chat", tokenizer=FakeTokenizer())

    assert completion not in prompt


# --- dataset shape follows the setting -------------------------------------- #


def test_completion_only_config_renders_prompt_completion_columns():
    from datasets import Dataset, DatasetDict

    dataset = DatasetDict({"train": Dataset.from_list([ROW])})
    config = DataConfig(train_on_inputs=False, preprocessing_num_proc=1)

    rendered = prepare_sft_dataset(dataset, config, FakeTokenizer())

    assert sorted(rendered["train"].column_names) == ["completion", "prompt"]


def test_train_on_inputs_config_renders_a_text_column():
    from datasets import Dataset, DatasetDict

    dataset = DatasetDict({"train": Dataset.from_list([ROW])})
    config = DataConfig(train_on_inputs=True, preprocessing_num_proc=1)

    rendered = prepare_sft_dataset(dataset, config, FakeTokenizer())

    assert rendered["train"].column_names == ["text"]


# --- the guard --------------------------------------------------------------- #


def test_completion_only_loss_rejects_a_text_dataset():
    with pytest.raises(ValueError, match="prompt-completion columns"):
        check_supervision_setup(config_for(False), ["text"])


def test_train_on_inputs_rejects_a_prompt_completion_dataset():
    with pytest.raises(ValueError, match="needs a 'text' column"):
        check_supervision_setup(config_for(True), ["prompt", "completion"])


def test_matching_shapes_pass():
    check_supervision_setup(config_for(False), ["prompt", "completion"])
    check_supervision_setup(config_for(True), ["text"])


def test_train_on_inputs_warns_that_metrics_are_inflated(caplog):
    check_supervision_setup(config_for(True), ["text"])

    assert "loss covers the instruction" in caplog.text


def test_packing_without_flash_attention_is_refused():
    with pytest.raises(ValueError, match="requires model.flash_attention"):
        check_supervision_setup(config_for(False, packing=True), ["prompt", "completion"])


def test_packing_with_flash_attention_is_allowed():
    check_supervision_setup(config_for(False, packing=True, flash=True), ["prompt", "completion"])
