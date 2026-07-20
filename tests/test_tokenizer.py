from qwen_cpp_review.tokenizer import load_tokenizer
from qwen_cpp_review.config import ModelConfig


class FakeAutoTokenizer:
    pad_token = None
    eos_token = "<eos>"
    padding_side = "left"

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()


def test_load_tokenizer_sets_pad_token(monkeypatch):
    monkeypatch.setattr("qwen_cpp_review.tokenizer.AutoTokenizer", FakeAutoTokenizer)

    tokenizer = load_tokenizer(ModelConfig(model_name_or_path="fake"))

    assert tokenizer.pad_token == "<eos>"
    assert tokenizer.padding_side == "right"

