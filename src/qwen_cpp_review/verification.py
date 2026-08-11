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
SCALAR_TYPES = {"int", "long", "long long", "size_t", "unsigned", "double", "float", "bool"}

SIGNATURE_RE = re.compile(
    r"^\s*(?P<ret>[A-Za-z_][\w:<>,\s*&]*?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^)]*)\)\s*\{?",
    re.MULTILINE,
)

STANDARD_HEADERS = (
    "#include <bits/stdc++.h>\n" if Path("/usr/include/bits/stdc++.h").exists() else
    "#include <iostream>\n#include <vector>\n#include <string>\n#include <map>\n"
    "#include <unordered_map>\n#include <algorithm>\n#include <climits>\n#include <cmath>\n"
)


@dataclass(frozen=True)
class Parameter:
    type: str
    name: str
    is_array: bool = False


@dataclass(frozen=True)
class Signature:
    return_type: str
    name: str
    params: tuple[Parameter, ...]

    @property
    def supported(self) -> bool:
        """Whether a driver can be generated for this shape."""
        if self.return_type.strip() == "void":
            return False
        for parameter in self.params:
            base = parameter.type.replace("const", "").replace("&", "").strip()
            if base not in SCALAR_TYPES:
                return False
        return bool(self.params)


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


def parse_signature(code: str) -> Signature | None:
    """Read the first function definition out of ``code``."""
    for match in SIGNATURE_RE.finditer(code):
        name = match.group("name")
        if name in {"main", "if", "for", "while", "switch", "return", "sizeof"}:
            continue
        raw_params = match.group("params").strip()
        params: list[Parameter] = []
        if raw_params and raw_params != "void":
            for piece in raw_params.split(","):
                piece = piece.strip()
                is_array = "[" in piece
                piece = re.sub(r"\[\s*\]", "", piece).strip()
                bits = piece.replace("&", " ").replace("*", " ").split()
                if len(bits) < 2:
                    return None
                params.append(Parameter(type=" ".join(bits[:-1]), name=bits[-1], is_array=is_array))
        return Signature(
            return_type=match.group("ret").strip(), name=name, params=tuple(params)
        )
    return None


def build_driver(signature: Signature, cases: list[tuple[int, ...]], repeats: int) -> str:
    """A main() that calls the function on each case and prints the results.

    Every case is printed, so a disagreement names the input that caused it
    rather than only reporting that something differed.
    """
    calls = []
    for values in cases:
        arguments = ", ".join(str(value) for value in values)
        calls.append(
            f'  {{ auto r = {signature.name}({arguments}); '
            f'std::cout << "{arguments}" << " => " << r << "\\n"; }}'
        )
    body = "\n".join(calls)
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
        capture_output=True, text=True, timeout=timeout,
    )
    if build.returncode != 0:
        return RunResult(ok=False, error=build.stderr[-800:])
    best = float("inf")
    run = None
    for _ in range(max(1, runs)):
        started = time.perf_counter()
        try:
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=timeout)
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
        report.error = (
            f"unsupported signature {signature.return_type} {signature.name}"
            f"({', '.join(p.type + ' ' + p.name for p in signature.params)}) - "
            "the driver generator handles scalar arguments and a non-void return"
        )
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


def default_cases(signature: Signature) -> list[tuple[int, ...]]:
    """Small inputs, chosen to run fast under either implementation.

    Correctness and speed need different inputs. These cover base cases and
    boundaries cheaply; :func:`default_timing_case` supplies the large input
    that makes a speedup visible.
    """
    width = len(signature.params)
    if width == 1:
        return [(n,) for n in (0, 1, 2, 3, 5, 10, 15, 20)]
    if width == 2:
        return [(a, b) for a, b in ((1, 1), (1, 5), (2, 3), (4, 4), (6, 5), (10, 8))]
    return [tuple(1 for _ in range(width)), tuple(3 for _ in range(width)), tuple(5 for _ in range(width))]


def default_timing_case(signature: Signature) -> tuple[int, ...]:
    """One input large enough that an exponential implementation is felt.

    Small inputs cannot separate the two versions: naive fib(20) finishes in
    well under a millisecond, so the measurement is process start-up rather
    than the algorithm. These values are slow exponentially and trivial once
    memoised, which is exactly the gap being measured.
    """
    width = len(signature.params)
    if width == 1:
        return (42,)
    if width == 2:
        return (20, 18)
    return tuple(11 for _ in range(width))
