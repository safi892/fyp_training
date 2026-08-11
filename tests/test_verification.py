"""Tests for the execution-based equivalence check.

These compile and run real C++, so they are slower than the rest of the suite
and are skipped where no compiler exists.
"""

import shutil

import pytest

from qwen_cpp_review.verification import (
    VerificationReport,
    default_cases,
    default_timing_case,
    parse_signature,
    verify,
)

pytestmark = pytest.mark.skipif(shutil.which("c++") is None, reason="needs a C++ compiler")

NAIVE_FIB = "int fib(int n)\n{\n  if (n <= 1)\n    return n;\n  return fib(n - 1) + fib(n - 2);\n}"

MEMOISED_FIB = """int fib(int n)
{
    static std::vector<int> memo(1000, -1);
    if (memo[n] != -1) return memo[n];
    if (n <= 1) return n;
    memo[n] = fib(n - 1) + fib(n - 2);
    return memo[n];
}"""

SMALL_CASES = [(0,), (1,), (5,), (10,)]
SMALL_TIMING = (18,)


# --- signature parsing -------------------------------------------------------- #


def test_parses_a_simple_signature():
    signature = parse_signature(NAIVE_FIB)

    assert signature is not None
    assert (signature.return_type, signature.name) == ("int", "fib")
    assert [(p.type, p.name) for p in signature.params] == [("int", "n")]
    assert signature.supported


def test_main_is_not_mistaken_for_the_function_under_test():
    signature = parse_signature("int main()\n{\n  return 0;\n}\nint f(int n) { return n; }")

    assert signature is not None and signature.name == "f"


def test_void_and_argumentless_functions_are_unsupported():
    assert not parse_signature("void run(int n) { }").supported
    assert not parse_signature("int seed() { return 4; }").supported


def test_non_scalar_arguments_are_unsupported():
    """A driver cannot invent a vector, so say so instead of guessing."""
    assert not parse_signature("int total(std::vector<int> xs) { return 0; }").supported


def test_unparseable_input_returns_none():
    assert parse_signature("not c++ at all") is None


# --- equivalence -------------------------------------------------------------- #


def test_a_correct_rewrite_is_equivalent():
    report = verify(NAIVE_FIB, MEMOISED_FIB, cases=SMALL_CASES, timing_case=SMALL_TIMING)

    assert report.equivalent, report.summary()
    assert report.agreed == report.cases == len(SMALL_CASES)


def test_a_wrong_rewrite_is_caught():
    wrong = NAIVE_FIB.replace("fib(n - 1) + fib(n - 2)", "fib(n - 1) + fib(n - 2) + 1")

    report = verify(NAIVE_FIB, wrong, cases=SMALL_CASES, timing_case=SMALL_TIMING)

    assert not report.equivalent
    assert report.disagreements


def test_code_that_does_not_compile_fails_rather_than_passing():
    report = verify(NAIVE_FIB, "int fib(int n) { return fib(n-1) }", cases=SMALL_CASES,
                    timing_case=SMALL_TIMING)

    assert not report.equivalent
    assert "optimized" in report.error


def test_an_unsupported_signature_is_reported_not_silently_skipped():
    report = verify("void go(std::vector<int>& xs) { }", "void go(std::vector<int>& xs) { }")

    assert not report.equivalent
    assert "unsupported signature" in report.error


# --- timing honesty ----------------------------------------------------------- #


def test_an_unchanged_program_is_not_reported_as_faster():
    """The control that makes the speedup number trustworthy."""
    report = verify(NAIVE_FIB, NAIVE_FIB, cases=SMALL_CASES, timing_case=(40,), timeout=120)

    assert report.equivalent
    assert report.timing_reliable, "fib(40) should be well above the noise floor"
    assert 0.7 <= report.speedup <= 1.4, f"unchanged code reported {report.speedup:.2f}x"


def test_work_below_the_floor_is_called_inconclusive_rather_than_guessed():
    report = verify(NAIVE_FIB, MEMOISED_FIB, cases=SMALL_CASES, timing_case=(5,))

    assert report.equivalent
    assert not report.timing_reliable
    assert "inconclusive" in report.summary()


def test_speedup_is_a_lower_bound_when_the_rewrite_is_too_fast_to_time():
    report = verify(NAIVE_FIB, MEMOISED_FIB, cases=SMALL_CASES, timing_case=(40,), timeout=120)

    assert report.equivalent
    assert report.speedup > 1
    assert ">" in report.summary(), "a bound should be marked as one"


# --- report arithmetic (no compiler needed) ------------------------------------ #


def test_startup_is_removed_from_the_measured_work():
    report = VerificationReport(
        compiled_original=True, compiled_optimized=True, cases=1, agreed=1,
        original_seconds=1.5, optimized_seconds=0.6, baseline_seconds=0.5,
    )

    assert report.original_work == pytest.approx(1.0)
    assert report.optimized_work == pytest.approx(0.1)
    assert report.speedup == pytest.approx(10.0)


def test_default_cases_stay_small_and_the_timing_case_does_not():
    signature = parse_signature(NAIVE_FIB)

    assert max(case[0] for case in default_cases(signature)) <= 20
    assert default_timing_case(signature)[0] > 30
