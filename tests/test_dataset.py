import json
from pathlib import Path

from qwen_cpp_review.config import DataConfig
from qwen_cpp_review.dataset import load_review_dataset, prepare_sft_dataset


class FakeTokenizer:
    def apply_chat_template(self, conversation, *, tokenize, add_generation_prompt):
        assert tokenize is False
        assert add_generation_prompt is False
        return "\n".join(message["content"] for message in conversation)


def test_dataset_loads_jsonl_and_renders_text(tmp_path: Path, monkeypatch):
    data_file = tmp_path / "data.jsonl"
    row = {
        "code": "int main(){return 0;}",
        "language": "cpp",
        "comments": "comment",
        "explanation": "explain",
        "improved_code": "int main() { return 0; }",
        "complexity_analysis": {"time": "O(1)", "space": "O(1)"},
    }
    data_file.write_text(json.dumps(row) + "\n")
    monkeypatch.chdir(tmp_path)

    config = DataConfig(
        data_files=["data.jsonl"],
        validation_split_ratio=0.0,
        preprocessing_num_proc=1,
        cache_dir=str(tmp_path / ".cache"),
    )
    dataset = load_review_dataset(config)
    rendered = prepare_sft_dataset(dataset, config, FakeTokenizer())

    assert len(rendered["train"]) == 1
    assert "int main" in rendered["train"][0]["text"]
    assert "complexity_analysis" in rendered["train"][0]["text"]


def test_identifier_augmentation_expands_training_split(tmp_path: Path, monkeypatch):
    data_file = tmp_path / "data.jsonl"
    row = {
        "code": "int sum(int first, int second) { int total = first + second; return total; }",
        "language": "cpp",
        "comments": "comment",
        "explanation": "explain",
        "improved_code": "int sum(int first, int second) { return first + second; }",
        "complexity_analysis": {"time": "O(1)", "space": "O(1)"},
    }
    data_file.write_text(json.dumps(row) + "\n")
    monkeypatch.chdir(tmp_path)

    config = DataConfig(
        data_files=["data.jsonl"],
        validation_split_ratio=0.0,
        preprocessing_num_proc=1,
        cache_dir=str(tmp_path / ".cache"),
        identifier_augmentation=True,
        identifier_augmentation_copies=1,
    )
    dataset = load_review_dataset(config)
    rendered = prepare_sft_dataset(dataset, config, FakeTokenizer())

    assert len(rendered["train"]) == 2
    assert any("int a" in item["text"] or "int b" in item["text"] for item in rendered["train"])
