"""Tests for how the hard-example evaluation awards points.

These exist because the scoring has been wrong three times, each time in the
flattering direction, and each time it was found by reading the model's output
rather than by the harness noticing. A measurement that only its author can
check is a measurement that gets believed.

Every case below is a real phrase from a recorded run.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from eval_hard import SAMPLES, _find_outside_a_denial, normalise, score  # noqa: E402

OVERFLOW = {
    "finds": [r"overflow"],
    "false_claim": r"(avoid|prevent|safe|without|no risk of)\w*[^.]{0,30}overflow",
}


def test_a_concept_named_inside_a_denial_is_not_a_find():
    """"compute midpoint to avoid overflow", on an unguarded (low + high) / 2."""
    assert _find_outside_a_denial(r"overflow", "compute midpoint to avoid overflow") is None


def test_a_bare_negation_is_still_a_find():
    """"does not check for overflow" contains "not" and is a genuine catch."""
    assert _find_outside_a_denial(r"overflow", "does not check for overflow") is not None


def test_a_later_honest_mention_still_scores():
    """One denial must not suppress a real observation further along."""
    text = "computed to avoid overflow. in fact this overflows for large inputs"

    assert _find_outside_a_denial(r"overflow", text) is not None


def test_a_concept_inside_the_false_claim_does_not_score_it_away():
    """The whole sentence is the falsehood, so the word in it proves nothing."""
    result = score("compute midpoint to avoid overflow", OVERFLOW)

    assert result["found"] == 0
    assert result["false_claim"], "the falsehood must survive being noticed"


def test_naming_the_defect_and_the_intent_is_not_a_false_claim():
    """"attempts to swap, but the value is lost" is accurate, not misleading."""
    sample = {"finds": [r"lost|lose"], "false_claim": r"\bswaps?\b"}

    result = score("attempts to swap, but the value is lost", sample)

    assert result["found"] == 1
    assert not result["false_claim"]


def test_typographic_punctuation_does_not_cost_the_model_a_point():
    """The model writes "fall-through" with a non-breaking hyphen."""
    sample = {"finds": [r"fall(s|ing)?[ -]?through"], "false_claim": r"zzz-never-matches"}

    assert score("fall‑through: the default case runs", sample)["found"] == 1
    assert normalise("in‑place") == "in-place"


def test_every_point_carries_the_phrase_that_earned_it():
    result = score("this leads to an infinite loop", {"finds": [r"infinite"], "false_claim": r"zzz"})

    assert result["evidence"] and "infinite" in result["evidence"][0]


def test_no_sample_scores_on_a_word_from_its_own_code():
    """A pattern matching the code awards a point for echoing the line.

    This caught `delete`, which appears in the leak sample's own source, so a
    model repeating the line it was describing scored for noticing nothing.
    """
    for sample in SAMPLES:
        result = score(sample["code"], sample)
        assert result["found"] == 0, f"{sample['name']} scores on its own source"
