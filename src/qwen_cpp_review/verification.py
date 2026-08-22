"""Compile two versions of a function, run both, and compare.

An optimisation is only an optimisation if it still computes the same thing.
The `improve` targets in the training corpus were never executed, which is how
the model came to learn tidying instead of speed - so anything generated here
is checked by running it rather than by reading it.

The check is behavioural, not formal: identical outputs on generated inputs
prove agreement on those inputs and nothing more. That is the same standard the
PIE line of work uses, and it is enough to reject a rewrite that changes the
answer, which is the failure that matters.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

#: Parameter types the driver generator knows how to supply values for.
SCALAR_TYPES = {
    "int", "long", "long long", "size_t", "unsigned", "double", "float", "bool",
    "char", "unsigned char", "short", "unsigned long",
}

#: Spellings of the same scalar. Competitive-programming C++ is full of these,
#: and treating `std::size_t` as a different type from `size_t` refuses a
#: function over its author's choice of prefix.
TYPE_ALIASES = {
    "std::size_t": "size_t", "unsigned int": "unsigned", "signed int": "int",
    "ll": "long long", "ull": "long long", "int64_t": "long long",
    "std::string": "string", "uint": "unsigned", "lli": "long long",
}

#: Handled as sequences of characters rather than numbers, so a case list is
#: words instead of integers.
STRING_TYPES = {"string"}

#: One argument for one call: a scalar, the contents of a sequence, or text.
Value = int | tuple[int, ...] | str

SIGNATURE_RE = re.compile(
    r"^\s*(?P<ret>[A-Za-z_][\w:<>,\s*&]*?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^)]*)\)\s*\{?",
    re.MULTILINE,
)

STANDARD_HEADERS = (
    "#include <bits/stdc++.h>\n" if Path("/usr/include/bits/stdc++.h").exists() else
    "#include <iostream>\n#include <vector>\n#include <string>\n#include <map>\n"
    "#include <unordered_map>\n#include <algorithm>\n#include <climits>\n#include <cmath>\n"
) + (
    # Competitive-programming submissions are written inside `using namespace
    # std`, so they say `vector<int>` and not `std::vector<int>`. Without this
    # line the *original* fails to compile and the attempt is discarded before
    # the rewrite is ever looked at - measured on 80 corpus functions, 32%
    # compiled without it and 92% with it, so two thirds of every verification
    # run was being thrown away for a missing declaration.
    "using namespace std;\n"
    # Tree and list problems pass node pointers and never define the struct,
    # because the judge supplied it.
    "struct TreeNode { int val; TreeNode *left, *right;\n"
    "  TreeNode(int x = 0) : val(x), left(nullptr), right(nullptr) {} };\n"
    "struct ListNode { int val; ListNode *next;\n"
    "  ListNode(int x = 0) : val(x), next(nullptr) {} };\n"
)


@dataclass(frozen=True)
class Parameter:
    type: str
    name: str
    is_array: bool = False
    is_reference: bool = False
    is_const: bool = False

    @property
    def is_vector(self) -> bool:
        return "vector" in self.type

    @property
    def is_buffer(self) -> bool:
        """Whether this parameter is a numeric sequence rather than one value.

        A ``std::string`` is a sequence too, but it is filled with words rather
        than numbers and prints itself, so it is driven separately.
        """
        return (self.is_array or self.is_vector) and not self.is_string

    @property
    def element_type(self) -> str:
        """The scalar type a value of this parameter is made of.

        A ``std::vector<int>`` and an ``int[]`` are both filled with ints; the
        driver needs that name to declare the backing store.

        The inner match is greedy on purpose. Stopping at the first ``>`` reads
        ``std::vector<std::vector<int>>`` as being made of ``vector<int`` — a
        type that does not exist, which then fails the scalar check for the
        wrong reason and reports a nonsense name. Greedy yields
        ``std::vector<int>``, which is correctly rejected as a nested sequence.
        """
        inner = re.search(r"<\s*(.+)\s*>", self.type)
        base = inner.group(1) if inner else self.type
        cleaned = base.replace("const", "").replace("&", "").replace("*", "").strip()
        return TYPE_ALIASES.get(cleaned, cleaned)

    @property
    def is_string(self) -> bool:
        return self.element_type in STRING_TYPES

    @property
    def is_output(self) -> bool:
        """Whether the callee can write through this parameter.

        This is what makes a ``void`` function checkable at all: the answer is
        not returned, so it has to be read back out of the arguments.
        """
        if self.is_const:
            return False
        return self.is_array or (self.is_reference and not self.is_const)

    @property
    def drivable(self) -> bool:
        return self.element_type in SCALAR_TYPES or self.is_string


@dataclass(frozen=True)
class Signature:
    return_type: str
    name: str
    params: tuple[Parameter, ...]

    @property
    def returns_value(self) -> bool:
        return self.return_type.strip() != "void"

    @property
    def observable(self) -> bool:
        """Whether calling this produces anything the driver can compare.

        A ``void`` function whose arguments are all taken by value has no
        effect this harness can see, and comparing two of them compares two
        empty strings — which passes. Refusing them is the difference between
        "not checked" and a verification that always succeeds, and the second
        is far more dangerous than the first.
        """
        return self.returns_value or any(p.is_output for p in self.params)

    @property
    def supported(self) -> bool:
        """Whether a driver can be generated for this shape."""
        if not self.params:
            return False
        if not all(parameter.drivable for parameter in self.params):
            return False
        return self.observable


@dataclass
class RunResult:
    ok: bool
    output: str = ""
    error: str = ""
    seconds: float = 0.0


@dataclass
class VerificationReport:
    """What happened when the two versions were built and run."""

    compiled_original: bool = False
    compiled_optimized: bool = False
    cases: int = 0
    agreed: int = 0
    disagreements: list[str] = field(default_factory=list)
    original_seconds: float = 0.0
    optimized_seconds: float = 0.0
    #: Process start-up measured on this machine, subtracted from both timings.
    baseline_seconds: float = 0.0
    error: str = ""

    @property
    def equivalent(self) -> bool:
        return (
            self.compiled_original
            and self.compiled_optimized
            and self.cases > 0
            and self.agreed == self.cases
            and not self.disagreements
        )

    #: Work below this, after start-up is removed, is too small to time here.
    NOISE_FLOOR = 0.05

    @property
    def original_work(self) -> float:
        return max(0.0, self.original_seconds - self.baseline_seconds)

    @property
    def optimized_work(self) -> float:
        return max(0.0, self.optimized_seconds - self.baseline_seconds)

    @property
    def timing_reliable(self) -> bool:
        """Whether the original did enough work for a ratio to mean anything.

        Launching a process costs a fixed half-second or so on this machine,
        which is far more than a small input takes. Comparing totals then
        measures the operating system, and an unchanged program duly reports a
        spurious speedup.
        """
        return self.original_work >= self.NOISE_FLOOR

    @property
    def speedup(self) -> float:
        """How much faster, or a lower bound when the new version is too fast to time."""
        if not self.timing_reliable:
            return 0.0
        return self.original_work / max(self.optimized_work, self.NOISE_FLOOR)

    def summary(self) -> str:
        if self.error:
            return f"FAILED: {self.error}"
        if not (self.compiled_original and self.compiled_optimized):
            which = "original" if not self.compiled_original else "optimized"
            return f"FAILED: {which} did not compile"
        if not self.equivalent:
            return f"DIFFERENT: agreed on {self.agreed}/{self.cases} cases"
        if not self.timing_reliable:
            return (
                f"EQUIVALENT on {self.cases} cases, speed inconclusive "
                f"(original did {self.original_work * 1000:.0f}ms of work, "
                f"below the {self.NOISE_FLOOR * 1000:.0f}ms floor)"
            )
        bound = ">" if self.optimized_work < self.NOISE_FLOOR else ""
        return f"EQUIVALENT on {self.cases} cases, {bound}{self.speedup:.1f}x faster"


def split_params(raw: str) -> list[str]:
    """Split a parameter list on commas that separate parameters.

    ``std::map<int, int> counts`` contains a comma that belongs to the template
    argument list, and splitting on it produces two nonsense parameters that
    then parse as plausible ones. Depth tracking keeps the split where it
    belongs.
    """
    pieces: list[str] = []
    depth = 0
    current = ""
    for character in raw:
        if character in "<([":
            depth += 1
        elif character in ">)]":
            depth -= 1
        if character == "," and depth == 0:
            pieces.append(current)
            current = ""
            continue
        current += character
    if current.strip():
        pieces.append(current)
    return pieces


def parse_signature(code: str) -> Signature | None:
    """Read the first function definition out of ``code``."""
    for match in SIGNATURE_RE.finditer(code):
        name = match.group("name")
        if name in {"main", "if", "for", "while", "switch", "return", "sizeof"}:
            continue
        raw_params = match.group("params").strip()
        params: list[Parameter] = []
        if raw_params and raw_params != "void":
            for piece in split_params(raw_params):
                piece = piece.strip()
                is_array = "[" in piece
                is_reference = "&" in piece or "*" in piece
                is_const = bool(re.match(r"\bconst\b", piece))
                piece = re.sub(r"\[[^\]]*\]", "", piece).strip()
                bits = piece.replace("&", " ").replace("*", " ").split()
                if len(bits) < 2:
                    return None
                params.append(
                    Parameter(
                        type=" ".join(bits[:-1]),
                        name=bits[-1],
                        is_array=is_array,
                        is_reference=is_reference,
                        is_const=is_const,
                    )
                )
        return Signature(
            return_type=match.group("ret").strip(), name=name, params=tuple(params)
        )
    return None


def render_case(signature: Signature, values: tuple[Value, ...], index: int) -> str:
    """One block that sets up the arguments, calls, and prints what came back.

    Sequence arguments are always backed by a ``std::vector`` even when the
    parameter is a C array, because ``vector`` carries its own length, can be
    empty without becoming an illegal zero-sized array, and hands a plain
    pointer to an ``int[]`` parameter through ``.data()``. One representation
    covers both shapes.

    Everything the call could have changed is printed, not just the return
    value: a ``void`` function's whole answer is in its arguments, and a
    function that both returns and mutates would otherwise be half-checked.
    """
    setup: list[str] = []
    arguments: list[str] = []
    label: list[str] = []

    for position, (parameter, value) in enumerate(zip(signature.params, values)):
        local = f"a{index}_{position}"
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            setup.append(f'    std::string {local} = "{escaped}";')
            arguments.append(local)
            # Single quotes: the label is itself pasted inside a C++ double-quoted
            # literal, so a double quote here ends that literal early and the
            # driver stops compiling for a reason that has nothing to do with
            # the code under test.
            label.append(f"'{value}'")
        elif isinstance(value, tuple):
            literal = ", ".join(str(item) for item in value)
            setup.append(
                f"    std::vector<{parameter.element_type}> {local} = {{{literal}}};"
            )
            arguments.append(local if parameter.is_vector else f"{local}.data()")
            label.append("[" + ",".join(str(item) for item in value) + "]")
        else:
            setup.append(f"    {parameter.element_type} {local} = {value};")
            arguments.append(local)
            label.append(str(value))

    call = f"{signature.name}({', '.join(arguments)})"
    lines = [*setup]
    if signature.returns_value:
        lines.append(f"    auto r = {call};")
    else:
        lines.append(f"    {call};")

    printed = f'    std::cout << "{" | ".join(label)}" << " => ";'
    lines.append(printed)
    if signature.returns_value:
        lines.append('    std::cout << r << " ; ";')
    # Read back every argument the callee could have written through. Doing
    # this after the call is the entire point: before it, they are the inputs.
    for position, parameter in enumerate(signature.params):
        if not parameter.is_output:
            continue
        local = f"a{index}_{position}"
        if isinstance(values[position], tuple):
            lines.append(f'    for (auto v : {local}) std::cout << v << ",";')
            lines.append('    std::cout << " ; ";')
        else:
            # A string prints itself; so does a scalar. Both read back the same.
            lines.append(f'    std::cout << {local} << " ; ";')
    lines.append('    std::cout << "\\n";')
    return "  {\n" + "\n".join(lines) + "\n  }"


def build_driver(signature: Signature, cases: list[tuple[Value, ...]], repeats: int) -> str:
    """A main() that calls the function on each case and prints the results.

    Every case is printed, so a disagreement names the input that caused it
    rather than only reporting that something differed.
    """
    body = "\n".join(render_case(signature, values, index) for index, values in enumerate(cases))
    return (
        "\n\nint main() {\n"
        f"  for (int rep = 0; rep < {repeats}; ++rep) {{\n"
        "    if (rep + 1 < " + str(repeats) + ") { std::cout.setstate(std::ios::failbit); }\n"
        "    else { std::cout.clear(); }\n"
        f"{body}\n"
        "  }\n"
        "  return 0;\n}\n"
    )


def compile_and_run(source: str, timeout: float, workdir: Path, tag: str, runs: int = 3) -> RunResult:
    """Build once, run ``runs`` times, and report the fastest run.

    Timing a single run measures whatever else the machine was doing. The
    minimum is the standard robust estimator here: noise can only ever make a
    run slower, never faster.
    """
    path = workdir / f"{tag}.cpp"
    binary = workdir / tag
    path.write_text(source, encoding="utf-8")
    build = subprocess.run(
        ["c++", "-std=c++17", "-O2", "-o", str(binary), str(path)],
        # errors="replace": a submission that prints a raw byte would otherwise
        # kill the whole run with a UnicodeDecodeError, losing every function
        # after it. The comparison only needs the two outputs to be decoded the
        # same way, not correctly.
        capture_output=True, text=True, errors="replace", timeout=timeout,
    )
    if build.returncode != 0:
        return RunResult(ok=False, error=build.stderr[-800:])
    best = float("inf")
    run = None
    for _ in range(max(1, runs)):
        started = time.perf_counter()
        try:
            run = subprocess.run(
                [str(binary)], capture_output=True, text=True,
                errors="replace", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return RunResult(ok=False, error=f"ran longer than {timeout}s", seconds=timeout)
        best = min(best, time.perf_counter() - started)
        if run.returncode != 0:
            return RunResult(ok=False, error=f"exit {run.returncode}: {run.stderr[-400:]}", seconds=best)
    return RunResult(ok=True, output=run.stdout, seconds=best)


def verify(
    original: str,
    optimized: str,
    *,
    cases: list[tuple[int, ...]] | None = None,
    timing_case: tuple[int, ...] | None = None,
    timeout: float = 20.0,
    repeats: int = 1,
) -> VerificationReport:
    """Compile both, run both on the same inputs, and compare the outputs.

    ``repeats`` runs the whole case list several times so the timing is not
    dominated by process start-up; only the final pass prints, so the compared
    output stays the same.
    """
    report = VerificationReport()
    signature = parse_signature(original)
    if signature is None:
        report.error = "could not read a function signature from the original"
        return report
    if not signature.supported:
        shape = (
            f"{signature.return_type} {signature.name}"
            f"({', '.join(p.type + ' ' + p.name for p in signature.params)})"
        )
        if signature.params and not signature.observable:
            why = (
                "it returns nothing and takes every argument by value, so a call "
                "leaves nothing to compare"
            )
        elif not signature.params:
            why = "it takes no arguments, so there is nothing to vary"
        else:
            why = (
                "the driver supplies scalars, arrays and vectors of "
                f"{', '.join(sorted(SCALAR_TYPES))}"
            )
        report.error = f"unsupported signature {shape} - {why}"
        return report

    if cases is None:
        cases = default_cases(signature)
    if not cases:
        report.error = "no test cases could be generated"
        return report
    report.cases = len(cases)

    driver = build_driver(signature, cases, repeats)
    timing_driver = build_driver(signature, [timing_case or default_timing_case(signature)], 1)
    with tempfile.TemporaryDirectory() as directory:
        workdir = Path(directory)
        first = compile_and_run(STANDARD_HEADERS + original + driver, timeout, workdir, "original")
        if not first.ok:
            report.error = f"original: {first.error}"
            return report
        report.compiled_original = True

        second = compile_and_run(STANDARD_HEADERS + optimized + driver, timeout, workdir, "optimized")
        if not second.ok:
            report.error = f"optimized: {second.error}"
            return report
        report.compiled_optimized = True

        # Timed separately on one large input: the correctness cases are
        # deliberately small, so timing them measures process start-up.
        # Launching a process is not free, and on some machines costs more
        # than a small input does. Measure it so it can be removed.
        empty = compile_and_run(STANDARD_HEADERS + "\nint main() { return 0; }\n", timeout, workdir, "empty")
        report.baseline_seconds = empty.seconds if empty.ok else 0.0

        slow = compile_and_run(STANDARD_HEADERS + original + timing_driver, timeout, workdir, "slow")
        fast = compile_and_run(STANDARD_HEADERS + optimized + timing_driver, timeout, workdir, "fast")
        report.original_seconds = slow.seconds
        report.optimized_seconds = fast.seconds
        if slow.ok and fast.ok and slow.output.strip() != fast.output.strip():
            report.disagreements.append(
                f"timing case disagreed: {slow.output.strip()!r} vs {fast.output.strip()!r}"
            )
            report.agreed = -1  # force `equivalent` false

    expected = first.output.strip().split("\n")
    actual = second.output.strip().split("\n")
    for index, line in enumerate(expected):
        if index < len(actual) and actual[index] == line:
            report.agreed += 1
        else:
            got = actual[index] if index < len(actual) else "<missing>"
            report.disagreements.append(f"expected {line!r}, got {got!r}")
    return report


#: Sequence inputs worth trying, in the order a reviewer would try them: empty,
#: single, already sorted, reversed, duplicates, negatives. The empty case earns
#: its place - it is where ``size() - 1`` on an unsigned type wraps.
BUFFER_CASES: tuple[tuple[int, ...], ...] = (
    (),
    (7,),
    (1, 2, 3, 4),
    (4, 3, 2, 1),
    (5, 1, 5, 1, 5),
    (-3, 8, 0, -1, 2),
)


#: Text inputs, chosen the way the numeric ones were: empty, single character,
#: a palindrome, mixed case, repeats, and a space that a naive tokeniser trips on.
STRING_CASES: tuple[str, ...] = ("", "a", "abc", "racecar", "Hello World", "aabbcc")


def has_buffer(signature: Signature) -> bool:
    return any(parameter.is_buffer for parameter in signature.params)


def has_string(signature: Signature) -> bool:
    return any(parameter.is_string for parameter in signature.params)


def _fill(
    signature: Signature,
    buffer: tuple[int, ...],
    scalar: int,
    text: str = "abc",
) -> tuple[Value, ...]:
    """Build one argument tuple, sizing any length parameter from its sequence.

    An integer parameter directly after a sequence is that sequence's length -
    ``f(int arr[], int n)`` is close to universal in this corpus, and a length
    invented independently would index past the end, where the comparison stops
    measuring the code and starts measuring undefined behaviour.

    Misreading the convention is safe in the direction that matters. If that
    integer was really something else, both versions still receive the same
    small value, so the check stays sound; only the input becomes less
    interesting. Guessing too *large* is the failure that would matter, and
    deriving it from the sequence cannot do that.
    """
    values: list[Value] = []
    previous_length: int | None = None
    for parameter in signature.params:
        if parameter.is_string:
            values.append(text)
            previous_length = len(text)
        elif parameter.is_buffer:
            values.append(buffer)
            previous_length = len(buffer)
        elif previous_length is not None and parameter.element_type != "double":
            values.append(previous_length)
            previous_length = None
        else:
            values.append(scalar)
    return tuple(values)


def default_cases(signature: Signature) -> list[tuple[Value, ...]]:
    """Small inputs, chosen to run fast under either implementation.

    Correctness and speed need different inputs. These cover base cases and
    boundaries cheaply; :func:`default_timing_case` supplies the large input
    that makes a speedup visible.
    """
    if has_buffer(signature) or has_string(signature):
        return [
            _fill(signature, buffer, 2, text)
            for buffer, text in zip(BUFFER_CASES, STRING_CASES)
        ]

    width = len(signature.params)
    if width == 1:
        return [(n,) for n in (0, 1, 2, 3, 5, 10, 15, 20)]
    if width == 2:
        return [(a, b) for a, b in ((1, 1), (1, 5), (2, 3), (4, 4), (6, 5), (10, 8))]
    return [tuple(1 for _ in range(width)), tuple(3 for _ in range(width)), tuple(5 for _ in range(width))]


def default_timing_case(signature: Signature) -> tuple[Value, ...]:
    """One input large enough that an exponential implementation is felt.

    Small inputs cannot separate the two versions: naive fib(20) finishes in
    well under a millisecond, so the measurement is process start-up rather
    than the algorithm. These values are slow exponentially and trivial once
    memoised, which is exactly the gap being measured.

    For sequence arguments the same logic applies to the *length*: a quadratic
    sort and a linearithmic one are indistinguishable on four elements. The
    values are generated rather than sorted so a best-case early exit does not
    stand in for the general case.
    """
    if has_buffer(signature) or has_string(signature):
        large = tuple((index * 7919) % 2003 for index in range(1500))
        return _fill(signature, large, 2, "abcdefghij" * 150)

    width = len(signature.params)
    if width == 1:
        return (42,)
    if width == 2:
        return (20, 18)
    return tuple(11 for _ in range(width))
