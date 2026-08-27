"""One entry point serving can call: a model response, checked against the code.

The three checks it composes already existed and were each used alone. Nothing
put them on the same response, so a served answer had its anchors repaired while
its `improved_code` went out unverified and its prose went out unread.

    anchors        `line_anchoring.repair_anchors`  - a quoted line must be in the file
    improved_code  `verification.verify`            - compile both, run both, compare
    prose          `claim_checks.check_claims`      - the code must not say otherwise

What this is for is worth being exact about. It does not make the model better.
Measured on 60 real submissions, the best prompt turns 17% of recursive
functions into loops; on twenty programs of tree and graph code the explanations
were fluent and wrong about 45% of the time. Neither number moves here. What
moves is what reaches a user: a rewrite that changes the answer is not shown, a
comment contradicting its own line is not shown, and an explanation the source
refutes is flagged rather than believed.

That trade is deliberate. Recall drops, precision rises. For a review tool the
second is the one that matters, because a confident wrong comment is worse than
no comment - it is read, believed, and acted on.

`needs_review` keeps its name and type; an Android client reads it. Everything
added here is additive.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .claim_checks import Claim, check_claims, filter_comments, sentences
from .line_anchoring import repair_anchors


@dataclass
class CheckedResponse:
    """A response with everything unverifiable removed or marked."""

    line_comments: list[dict[str, Any]] = field(default_factory=list)
    explanation: str | None = None
    improved_code: str | None = None

    #: Anchors quoting a line that is not in the submission.
    dropped_anchors: int = 0
    #: Comments a line's own declaration contradicts.
    dropped_comments: list[Claim] = field(default_factory=list)
    #: Sentences of the explanation the source contradicts. Kept, not deleted -
    #: removing half a paragraph leaves prose that reads as whole and is not.
    explanation_conflicts: list[Claim] = field(default_factory=list)
    #: Why `improved_code` was withheld, or None if it was not.
    improved_code_rejected: str | None = None

    @property
    def needs_review(self) -> bool:
        """True when anything was dropped, withheld or flagged."""
        return bool(
            self.dropped_anchors
            or self.dropped_comments
            or self.explanation_conflicts
            or self.improved_code_rejected
        )


def check_response(
    code: str,
    response: dict[str, Any],
    *,
    verify_improved: bool = True,
    timeout: float = 20.0,
) -> CheckedResponse:
    """Check a model response against the code it was produced from.

    ``verify_improved`` compiles and runs both versions, which costs seconds and
    needs a compiler. Turning it off keeps every other check, so a deployment
    without a toolchain degrades rather than fails.
    """
    checked = CheckedResponse()

    raw = response.get("line_comments")
    if isinstance(raw, list):
        report = repair_anchors(code, raw)
        checked.dropped_anchors = report.dropped
        anchored = [
            {"line": a.line, "code": a.code, "comment": a.comment} for a in report.anchors
        ]
        checked.line_comments, checked.dropped_comments = filter_comments(code, anchored)

    explanation = response.get("explanation")
    if isinstance(explanation, str) and explanation.strip():
        checked.explanation = explanation
        checked.explanation_conflicts = check_claims(code, explanation).contradictions

    improved = response.get("improved_code")
    if isinstance(improved, str) and improved.strip():
        checked.improved_code = improved
        if verify_improved:
            problem = _reject_reason(code, improved, timeout)
            if problem:
                checked.improved_code = None
                checked.improved_code_rejected = problem
    return checked


def _reject_reason(code: str, improved: str, timeout: float) -> str | None:
    """Why this rewrite must not be shown, or None if it agrees with the original.

    A signature the driver cannot supply arguments for is *not* a rejection. The
    rewrite is unproven either way, and refusing every function with an
    unsupported shape would withhold most correct answers to avoid a few wrong
    ones. Only a demonstrated disagreement withholds.
    """
    from .verification import verify

    try:
        report = verify(code, improved, timeout=timeout)
    except OSError:                             # no compiler on this machine
        return None

    if report.error:                            # signature the driver cannot drive
        return None
    if report.compiled_original and not report.compiled_optimized:
        # The original builds and the rewrite does not, so the rewrite is the
        # broken one. Not showing it needs no further argument.
        return "the rewritten version does not compile"
    if report.cases > 0 and not report.equivalent:
        first = report.disagreements[0] if report.disagreements else ""
        return (
            "the rewritten version does not produce the same output as the original"
            + (f" ({first})" if first else "")
        )
    return None


def objection_count(checked: CheckedResponse) -> int:
    """How much the checks had to object to. Lower is better, 0 is clean."""
    return (
        checked.dropped_anchors
        + len(checked.dropped_comments)
        + len(checked.explanation_conflicts)
        + (1 if checked.improved_code_rejected else 0)
    )


def content_size(checked: CheckedResponse) -> int:
    """How much survived, so a clean answer is not rewarded for saying nothing."""
    explanation = checked.explanation or ""
    return len(checked.line_comments) + len(sentences(explanation))


def best_of(
    code: str,
    responses: list[dict[str, Any]],
    *,
    verify_improved: bool = True,
    timeout: float = 20.0,
) -> tuple[CheckedResponse, int]:
    """Check several answers to the same code and return the best, with its index.

    The model is sampled more than once and the checks decide which sample is
    served. This is the answer to the boundary in `docs/DETECTABILITY.md`: a
    claim the source cannot refute stays unrefuted however hard one check
    tries, but a *second sample* of the same question often makes a claim the
    source **can** refute, and then the clean sample is the one to serve.

    **The scoring is not "fewest objections".** That optimum is the empty
    answer, which objects to nothing and would win every time - best-of-N would
    quietly make the product worse the more samples it was given. Two filters
    close that direction, in this order:

    1. discard samples that said nothing, unless every sample said nothing;
    2. of what remains, keep the samples with no objections at all;
    3. among those, serve the one that said the most.

    Step 1 has to come first, and a test pins it: an empty answer *is* clean, so
    ranking on objections alone serves the empty one over a flagged answer that
    said something. That is the wrong trade for this product. `needs_review`
    exists precisely so flawed output can be served with a warning, while a
    response with nothing in it is a failure the caller cannot flag their way
    out of.

    Ties are broken towards the earlier sample, which at temperature 0 is the
    one a single-sample deployment would have served anyway.
    """
    if not responses:
        return CheckedResponse(), -1

    checked = [
        check_response(code, response, verify_improved=verify_improved, timeout=timeout)
        for response in responses
    ]
    scored = [(objection_count(c), content_size(c), index) for index, c in enumerate(checked)]

    spoke = [entry for entry in scored if entry[1] > 0]
    pool = spoke or scored
    clean = [entry for entry in pool if entry[0] == 0]
    pool = clean or pool
    # -content so more content sorts first; index last so ties go to the earliest.
    _, _, best = min(pool, key=lambda entry: (entry[0], -entry[1], entry[2]))
    return checked[best], best
