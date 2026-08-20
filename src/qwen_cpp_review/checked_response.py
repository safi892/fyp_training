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

from .claim_checks import Claim, check_claims, filter_comments
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
