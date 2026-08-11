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


def test_a_call_with_nothing_to_compare_is_unsupported():
    """The dangerous shape: no return, and every argument taken by value.

    Two such functions produce two empty strings, which compare equal, so
    accepting them would report every one of them as verified. Refusing is the
    difference between "not checked" and a check that always passes.
    """
    assert not parse_signature("void run(int n) { }").supported
    assert not parse_signature("int seed() { return 4; }").supported
    assert not parse_signature("void look(const std::vector<int>& v) { }").supported


def test_sequences_and_void_returns_are_supported():
    """The common shape in this corpus: fill a buffer, return nothing."""
    assert parse_signature("int total(std::vector<int> xs) { return 0; }").supported
    assert parse_signature("void sortValues(int data[], int n) { }").supported
    assert parse_signature("void twice(int& x) { }").supported


def test_a_written_argument_is_recognised_as_the_output():
    signature = parse_signature("void sortValues(int data[], int n) { }")

    assert signature.params[0].is_output, "the array is where the answer lands"
    assert not signature.params[1].is_output, "a by-value length is an input"


def test_a_template_comma_does_not_split_the_parameter_list():
    """`std::map<int, int> c` is one parameter, not two nonsense ones."""
    signature = parse_signature("int tally(std::map<int, int> counts, int k) { return k; }")

    assert [p.name for p in signature.params] == ["counts", "k"]


def test_a_nested_sequence_is_refused_under_its_real_name():
    """Reading the inner type non-greedily invents `vector<int`, which is not a type.

    The refusal is right either way; what matters is that it is refused for
    being a nested sequence, not because a mangled name missed a lookup.
    """
    signature = parse_signature("int sum(std::vector<std::vector<int>> grid) { return 0; }")

    assert signature.params[0].element_type == "std::vector<int>"
    assert not signature.supported


def test_the_same_scalar_spelled_differently_is_still_that_scalar():
    """`std::size_t` and `size_t` are one type; so are `ll` and `long long`."""
    for declaration in ("std::size_t n", "unsigned int n", "ll n", "char c"):
        signature = parse_signature(f"int f({declaration}) {{ return 0; }}")
        assert signature.supported, declaration


def test_the_length_argument_is_taken_from_the_sequence():
    """Inventing it independently indexes past the end and measures the sanitiser."""
    signature = parse_signature("void sortValues(int data[], int n) { }")

    for values in default_cases(signature):
        assert values[1] == len(values[0]), values


# --- driving the shapes the corpus is actually made of ------------------------- #


def test_a_string_rewrite_is_checked_by_running_it():
    reverse_by_index = (
        "std::string flip(std::string s) {\n"
        "  std::string r; for (int i = s.size() - 1; i >= 0; --i) r += s[i]; return r; }"
    )
    reverse_by_iterator = "std::string flip(std::string s) { return std::string(s.rbegin(), s.rend()); }"
    identity = "std::string flip(std::string s) { return s; }"

    assert verify(reverse_by_index, reverse_by_iterator).equivalent
    assert not verify(reverse_by_index, identity).equivalent


def test_text_written_through_a_reference_is_read_back():
    """Another void function whose whole answer is in its argument."""
    by_range = "void upper(std::string& s) { for (auto& c : s) c = toupper(c); }"
    by_index = "void upper(std::string& s) { for (size_t i = 0; i < s.size(); ++i) s[i] = toupper(s[i]); }"
    does_nothing = "void upper(std::string& s) { }"

    assert verify(by_range, by_index).equivalent
    assert not verify(by_range, does_nothing).equivalent


def test_an_empty_sequence_is_among_the_cases():
    """Where `size() - 1` on an unsigned type wraps, so it has to be tried."""
    signature = parse_signature("bool isAscending(std::vector<int> v) { return true; }")

    assert any(values[0] == () for values in default_cases(signature))


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
    report = verify("void go(int n) { }", "void go(int n) { }")

    assert not report.equivalent
    assert "unsupported signature" in report.error
    assert "nothing to compare" in report.error, "say why, not just that it was refused"


def test_a_rewrite_that_corrupts_an_array_is_caught_by_running_it():
    """The measured case: a bubble sort whose swap has no temporary.

    Nothing about this is visible in a return value - the function returns
    none. It is caught only because the array is read back after the call.
    """
    correct = (
        "void sortValues(int d[], int n) {\n"
        "  for (int i = 0; i < n - 1; i++)\n"
        "    for (int j = 0; j < n - i - 1; j++)\n"
        "      if (d[j] > d[j+1]) { int t = d[j]; d[j] = d[j+1]; d[j+1] = t; }\n"
        "}"
    )
    broken = correct.replace("int t = d[j]; d[j] = d[j+1]; d[j+1] = t;", "d[j] = d[j+1]; d[j+1] = d[j];")

    assert verify(correct, correct).equivalent, "the control must pass"
    report = verify(correct, broken)
    assert not report.equivalent
    assert report.disagreements


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
