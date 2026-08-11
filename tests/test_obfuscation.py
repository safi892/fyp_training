import random
import re

import pytest

from qwen_cpp_review.obfuscation import STRATEGIES, mixed, obfuscate
from qwen_cpp_review.robustness_samples import SAMPLES

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

CODE = (
    "int countDigits(int first, int second)\n"
    "{\n"
    "  int total = first + second;\n"
    "  int digits = 0;\n"
    "  while (total != 0)\n"
    "  {\n"
    "    total /= 10;\n"
    "    digits++;\n"
    "  }\n"
    "  return digits;\n"
    "}"
)


def test_original_is_untouched():
    assert obfuscate(CODE, "original", random.Random(0)) == CODE


@pytest.mark.parametrize("strategy", [s for s in STRATEGIES if s != "original"])
def test_every_strategy_changes_the_names_but_not_the_shape(strategy):
    renamed = obfuscate(CODE, strategy, random.Random(0))

    assert renamed != CODE
    assert renamed.count("\n") == CODE.count("\n"), "line count must be preserved"
    for keyword in ("while", "return", "int", "/=", "!="):
        assert keyword in renamed, f"{strategy} destroyed {keyword!r}"


@pytest.mark.parametrize("pool_name", [s for s in STRATEGIES if STRATEGIES[s]])
def test_name_pools_are_valid_cpp_identifiers(pool_name):
    for name in STRATEGIES[pool_name]:
        assert IDENTIFIER_RE.match(name), f"{name!r} in {pool_name} is not a valid identifier"


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="unknown strategy"):
        obfuscate(CODE, "nope", random.Random(0))


def test_renaming_is_deterministic_for_a_seed():
    assert obfuscate(CODE, "noise", random.Random(7)) == obfuscate(CODE, "noise", random.Random(7))


def test_mixed_uses_both_pools():
    from qwen_cpp_review.obfuscation import CLEAR_NAMES, NOISE_NAMES

    result = mixed(CODE, random.Random(3))

    assert any(name in result for name in CLEAR_NAMES)
    assert any(name in result for name in NOISE_NAMES)


def test_code_without_declarations_is_returned_unchanged():
    assert obfuscate("return 0;", "noise", random.Random(0)) == "return 0;"


# --- the eval set itself ---------------------------------------------------- #


def test_every_sample_declares_concepts():
    for sample in SAMPLES:
        assert sample["concepts"], f"{sample['name']} has no concepts"
        for group in sample["concepts"]:
            assert group, f"{sample['name']} has an empty concept group"


def test_concept_words_are_not_identifiers_in_the_source():
    """A concept must not be earnable by echoing a name the model was handed."""
    for sample in SAMPLES:
        identifiers = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", sample["code"]))
        lowered = {name.lower() for name in identifiers}
        for group in sample["concepts"]:
            for word in group:
                assert word.lower() not in lowered, (
                    f"{sample['name']}: concept {word!r} is also an identifier, so it could be "
                    f"echoed rather than understood"
                )


def test_samples_survive_every_renaming():
    for sample in SAMPLES:
        for strategy in STRATEGIES:
            renamed = obfuscate(sample["code"], strategy, random.Random(1))
            assert renamed.count("\n") == sample["code"].count("\n")
