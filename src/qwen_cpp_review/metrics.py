from __future__ import annotations

import math


def perplexity(eval_loss: float) -> float:
    try:
        return math.exp(eval_loss)
    except OverflowError:
        return float("inf")

