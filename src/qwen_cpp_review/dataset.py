from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

from datasets import Dataset, DatasetDict, load_dataset

from qwen_cpp_review.config import DataConfig
from qwen_cpp_review.identifier_augmentation import augment_row
from qwen_cpp_review.prompt import build_prompt_completion, format_prompt


def load_review_dataset(config: DataConfig) -> DatasetDict:
    if config.dataset_name:
        dataset = load_dataset(
            config.dataset_name,
            config.dataset_config_name,
            cache_dir=config.cache_dir,
        )
        if isinstance(dataset, Dataset):
            dataset = DatasetDict({"train": dataset})
    else:
        data_files = _resolve_data_files(config.data_files)
        suffixes = {Path(path).suffix.lower() for path in data_files}
        if suffixes <= {".json", ".jsonl"}:
            dataset = load_dataset("json", data_files=data_files, cache_dir=config.cache_dir)
        elif suffixes <= {".arrow"}:
            dataset = load_dataset("arrow", data_files=data_files, cache_dir=config.cache_dir)
        else:
            raise ValueError(f"Unsupported dataset file extensions: {sorted(suffixes)}")

    if not isinstance(dataset, DatasetDict):
        dataset = DatasetDict({"train": dataset})
    return _ensure_splits(dataset, config)


def prepare_sft_dataset(dataset: DatasetDict, config: DataConfig, tokenizer: Any) -> DatasetDict:
    """Render the dataset into the columns TRL expects.

    With ``train_on_inputs`` false the output carries ``prompt`` and
    ``completion`` columns, which is the only shape for which TRL applies
    completion-only loss: a language-modeling dataset with a single text column
    is supervised over the whole sequence, instruction and input code included.
    """
    if config.identifier_augmentation:
        dataset = _augment_training_split(dataset, config)

    def render_prompt_completion(example: dict[str, Any]) -> dict[str, str]:
        prompt, completion = build_prompt_completion(
            example,
            config.output_fields,
            style=config.prompt_style,
            tokenizer=tokenizer,
        )
        return {"prompt": prompt, "completion": completion}

    def render_text(example: dict[str, Any]) -> dict[str, str]:
        return {
            "text": format_prompt(
                example,
                config.output_fields,
                style=config.prompt_style,
                tokenizer=tokenizer,
            )
        }

    render = render_text if config.train_on_inputs else render_prompt_completion
    columns = dataset["train"].column_names
    return dataset.map(
        render,
        remove_columns=columns,
        num_proc=config.preprocessing_num_proc,
        desc="Rendering prompts",
    )


def _augment_training_split(dataset: DatasetDict, config: DataConfig) -> DatasetDict:
    import random

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(dataset["train"]):
        rng = random.Random(config.identifier_augmentation_copies + index)
        variants = augment_row(dict(row), rng=rng)
        rows.append(variants[0])
        rows.extend(variants[1 : 1 + config.identifier_augmentation_copies])
    dataset["train"] = Dataset.from_list(rows)
    return dataset


def _resolve_data_files(patterns: list[str]) -> list[str]:
    files: list[str] = []
    for pattern in patterns:
        matched = sorted(glob.glob(pattern))
        files.extend(matched or [pattern])
    missing = [path for path in files if not Path(path).exists()]
    if missing:
        raise FileNotFoundError(f"Dataset files not found: {missing}")
    return files


def _ensure_splits(dataset: DatasetDict, config: DataConfig) -> DatasetDict:
    if "train" not in dataset:
        first_split = next(iter(dataset.keys()))
        dataset["train"] = dataset[first_split]

    if "validation" not in dataset and config.validation_split_ratio > 0:
        split = dataset["train"].train_test_split(
            test_size=config.validation_split_ratio,
            seed=42,
            shuffle=True,
        )
        dataset["train"] = split["train"]
        dataset["validation"] = split["test"]

    if "test" not in dataset and config.test_split_ratio > 0:
        split = dataset["train"].train_test_split(
            test_size=config.test_split_ratio,
            seed=43,
            shuffle=True,
        )
        dataset["train"] = split["train"]
        dataset["test"] = split["test"]
    return dataset
