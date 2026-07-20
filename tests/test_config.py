from pathlib import Path

from qwen_cpp_review.config import AppConfig


def test_config_loads_nested_yaml(tmp_path: Path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """
model:
  model_name_or_path: local-model
data:
  max_seq_length: 512
training:
  learning_rate: 0.0001
lora:
  r: 8
"""
    )

    config = AppConfig.from_yaml(path)

    assert config.model.model_name_or_path == "local-model"
    assert config.data.max_seq_length == 512
    assert config.training.learning_rate == 0.0001
    assert config.lora.r == 8

