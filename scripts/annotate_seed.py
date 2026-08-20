"""Ask the model to comment and explain the seed pairs, and check what can be checked.

The seed set is unusual for this project: twenty programs whose ground truth is
known exactly, in matched pairs. Each pair is the same algorithm written twice,
once recursively and once with an explicit stack or queue. That makes two claims
mechanically checkable rather than arguable:

    does the model call the iterative version recursive?
    does it name the container the code actually uses?

Both are cheap to get right by reading the code and easy to get wrong by reading
the function name, which is identical in both halves of every pair. A model
describing what a function is *named after* rather than what it *does* will say
"recursively traverses" over a while loop, and that is the 50%-false-description
failure showing up somewhere it can be counted.

    uv run python scripts/annotate_seed.py

Everything else in the output - whether the prose is actually a good explanation
- is printed with the sentence that produced it and left to a reader, because
this project has been wrong three times about scoring prose automatically and
every one of those was in the model's favour.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from qwen_cpp_review.line_anchoring import repair_anchors
from qwen_cpp_review.prompt import format_prompt_without_response

from qwen_cpp_review.claim_checks import STRUCTURES, check_claims, sentences

from probe_optimization import complete, wait_for_server
from verify_optimization_pairs import load_pairs, recursive_functions

#: Ground truth read from the code, and the word the prose uses for it. Both come
#: from the shared table so a structure added there is checked here too.
IN_CODE = {name: pair[0] for name, pair in STRUCTURES.items()}
IN_PROSE = {name: pair[1] for name, pair in STRUCTURES.items()}

# The patterns live in `claim_checks` so the report and the serving layer cannot
# disagree about what counts as a false claim. Two copies drifted once already:
# the report was still scoring with a closed list of verbs after the shared one
# had been widened, and printed a number that was known to be wrong.
split_sentences = sentences


def evidence(text: str, pattern: re.Pattern[str]) -> list[str]:
    """Every sentence matching `pattern`, so a score can be read rather than trusted."""
    return [s for s in split_sentences(text) if pattern.search(s)]


def containers_in(code: str) -> set[str]:
    """Every container the program declares, not just the first one found.

    `tree_invert` holds a queue in the traversal and a stack in the printing loop,
    so "the" container does not exist for it. Picking one would make a correct
    description score as wrong half the time, depending on dict order.
    """
    return {name for name, pattern in IN_CODE.items() if pattern.search(code)}


def harvest(raw: str, field: str) -> tuple[object, bool, bool]:
    """Return (value, parsed, truncated).

    Output that stops mid-string has hit `--n-predict`, which says how big the
    budget was and nothing about whether the model can produce valid JSON. These
    programs are around 45 lines against a training corpus whose median is 14, so
    the budget runs out here and never did on the corpus. Counting that as a
    format failure would report a measurement setting as a model property.
    """
    try:
        return (json.loads(raw) or {}).get(field), True, False
    except json.JSONDecodeError as error:
        truncated = "Unterminated" in str(error) or "Expecting" in str(error)
        return None, False, truncated


def as_text(value: object) -> str:
    """Flatten either output field to plain prose for phrase matching."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(
            item.get("comment", "") if isinstance(item, dict) else str(item) for item in value
        )
    return ""


def assess(code: str, is_recursive: bool, comments: object, explanation: object) -> dict:
    """What the model said about this one program, with the sentence behind each call."""
    anchors = comments if isinstance(comments, list) else []
    report = repair_anchors(code, anchors)
    prose = f"{as_text(comments)} {as_text(explanation)}"

    # One call rather than a second implementation: the same function serving uses.
    report_claims = check_claims(code, prose)
    said_recursion = [c.sentence for c in report_claims.contradictions if c.kind == "recursion"]
    present = containers_in(code)
    named, wrong_container = [], []
    for name, pattern in IN_PROSE.items():
        hits = evidence(prose, pattern)
        if name in present:
            named += hits
        else:
            wrong_container += hits

    return {
        "anchors_total": report.total,
        "anchors_exact": report.exact,
        "anchors_repaired": report.repaired,
        "anchors_dropped": report.dropped,
        "containers_present": sorted(present),
        "has_container": bool(present),
        "container_named": bool(named),
        "container_evidence": named[:2],
        "wrong_container_evidence": wrong_container[:2],
        # The one unambiguous error: a loop described as calling itself.
        "false_recursion_claim": (not is_recursive) and bool(said_recursion),
        "recursion_evidence": said_recursion[:2],
        "prose": prose.strip(),
    }


def write_report(records: list[dict], path: Path, pairs: dict[str, dict] | None = None) -> None:
    """The model's actual output, next to the code it was given.

    Written to be read rather than skimmed: every comment is shown against the
    line it attached to, and every check is followed by the sentence that decided
    it. A number in this project is only worth as much as the phrase behind it.
    """
    pairs = pairs or {}
    loops = [r for r in records if not r["is_recursive"]]
    holders = [r for r in records if r["has_container"]]
    intact = [r for r in records if not r["truncated"]]
    anchors = sum(r["anchors_total"] for r in records)
    dropped = sum(r["anchors_dropped"] for r in records)

    out = [
        "# What the model wrote about each program",
        "",
        "Each pair is one algorithm written twice, recursively and with an explicit",
        "container, under the **same function name**. A description that follows the",
        "name rather than the code says the same thing about both halves, and is",
        "therefore wrong about one of them.",
        "",
        "## Totals",
        "",
        "| | |",
        "| --- | ---: |",
        f"| programs | {len(records)} |",
        f"| valid JSON, of output that finished | {sum(r['json_ok'] for r in intact)}/{len(intact)} |",
        f"| ran past the token budget | {sum(r['truncated'] for r in records)}/{len(records)} |",
        f"| anchors quoting a real line | {anchors - dropped}/{anchors}"
        f"{f' ({(anchors - dropped) / anchors:.0%})' if anchors else ''} |",
        f"| named a container the code declares | {sum(r['container_named'] for r in holders)}/{len(holders)} |",
        f"| named a container that is not there | {sum(bool(r['wrong_container_evidence']) for r in records)}/{len(records)} |",
        f"| loops described as recursive | {sum(r['false_recursion_claim'] for r in loops)}/{len(loops)} |",
        "",
        "Whether an explanation is *correct overall* is not scored here. That needs a",
        "known-truth label for each program; these are the checks that can be made",
        "without one. Read the prose below before quoting any number above.",
        "",
        "---",
        "",
    ]

    for record in records:
        half = "recursive" if record["is_recursive"] else "iterative"
        out += [f"## {record['name']} — {half}", ""]

        flags = []
        if record["false_recursion_claim"]:
            flags.append("**describes this loop as recursive**")
        if record["wrong_container_evidence"]:
            flags.append("**names a container the code does not use**")
        if record["truncated"]:
            flags.append("output hit the token budget and was cut off")
        if flags:
            out += ["> " + "  \n> ".join(flags), ""]

        out += [
            f"- anchors: {record['anchors_exact']} exact, {record['anchors_repaired']} relocated, "
            f"**{record['anchors_dropped']} quoting a line that is not in the file**, "
            f"of {record['anchors_total']}",
            f"- containers in the code: {', '.join(record['containers_present']) or 'none'}",
            "",
        ]
        for label, key in (("recursion claim", "recursion_evidence"),
                           ("container named", "container_evidence"),
                           ("container NOT in the code", "wrong_container_evidence")):
            for line in record.get(key) or []:
                out.append(f"  - *{label}*: {line}")
        if any(record.get(k) for k in ("recursion_evidence", "container_evidence",
                                       "wrong_container_evidence")):
            out.append("")

        source = pairs.get(record["name"], {}).get(
            "code" if record["is_recursive"] else "improved_code", "")
        if source:
            out += ["<details><summary>the code it was given</summary>", "",
                    "```cpp", source.rstrip(), "```", "", "</details>", ""]

        comments = _parse_field(record["raw"].get("line_comments"), "line_comments")
        if isinstance(comments, list) and comments:
            out += ["| line | code | comment |", "| ---: | --- | --- |"]
            for item in comments:
                if not isinstance(item, dict):
                    continue
                code_cell = str(item.get("code", "")).replace("|", "\\|").strip()
                note = str(item.get("comment", "")).replace("|", "\\|").strip()
                out.append(f"| {item.get('line', '?')} | `{code_cell}` | {note} |")
            out.append("")
        else:
            out += ["*no usable line comments (output was cut off or malformed)*", ""]

        explanation = _parse_field(record["raw"].get("explanation"), "explanation")
        out += ["**Explanation**", ""]
        out += [as_text(explanation).strip() or "*none produced*", "", "---", ""]

    path.write_text("\n".join(out), encoding="utf-8")


def _parse_field(raw: object, field: str) -> object:
    if not isinstance(raw, str):
        return None
    try:
        return (json.loads(raw) or {}).get(field)
    except json.JSONDecodeError:
        return None


def select_pairs(directory: Path, only: str, limit: int) -> list[dict]:
    """The pairs a run covers, named.

    Both the run and `--report-only` call this, because they must agree on the
    names. Naming before filtering rather than after makes `dataset.jsonl#0`
    resolve to a different pair in each path, and a report then prints one
    program's source beside another program's comments.
    """
    pairs = load_pairs(directory)
    if only:
        pairs = [p for p in pairs if p["source"] == only]
    if limit:
        # Evenly spaced rather than the first N, so a file whose easy samples were
        # collected first does not become the whole result.
        step = max(1, len(pairs) // limit)
        pairs = pairs[::step][:limit]
    for index, pair in enumerate(pairs):
        pair.setdefault("name", f"{pair['source']}#{index}")
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dir", type=Path,
                        default=Path("my_data_annotation/recursion_optimization"),
                        help="directory of pairs; reads seed.jsonl, DATASET.json and dataset.jsonl")
    parser.add_argument("--only", default="", help="restrict to one source file name")
    parser.add_argument("--limit", type=int, default=0, help="0 for every pair")
    parser.add_argument("--gguf", default="models/gguf/qwen-cpp-review-q4_k_m.gguf")
    parser.add_argument("--tokenizer", default="models/qwen-cpp-review-merged")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--n-predict", type=int, default=2400)
    parser.add_argument("--output", default="test_results/seed_annotation")
    parser.add_argument("--report-only", action="store_true",
                        help="rewrite the markdown from a saved run, without calling the model")
    args = parser.parse_args()

    if args.report_only:
        out = Path(args.output)
        saved = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
        known = {p["name"]: p for p in select_pairs(args.dir, args.only, args.limit)}

        # Re-assessed rather than replayed. The saved fields carry whatever the
        # scorer believed on the day, and this scorer has been corrected since -
        # a report that reprints a number known to be wrong is worse than no
        # report. The model's own output never changes; only the reading of it does.
        missing = [r["name"] for r in saved if r["name"] not in known]
        if missing:
            raise SystemExit(
                f"{len(missing)} saved records name pairs this selection does not "
                f"contain, starting with {missing[0]!r}. Pass the same --only/--limit "
                "the run used, or the report would show the wrong source."
            )
        for record in saved:
            pair = known[record["name"]]
            code = pair["code" if record["is_recursive"] else "improved_code"]
            comments = _parse_field(record["raw"].get("line_comments"), "line_comments")
            explanation = _parse_field(record["raw"].get("explanation"), "explanation")
            record.update(assess(code, record["is_recursive"], comments, explanation))

        write_report(saved, out.with_suffix(".md"), known)
        print(f"rewrote {out.with_suffix('.md')} from {len(saved)} saved records, re-scored")
        return

    pairs = select_pairs(args.dir, args.only, args.limit)
    if not pairs:
        raise SystemExit(f"no pairs in {args.dir}")
    print(f"{len(pairs)} pairs -> {len(pairs) * 2} programs, "
          f"{len(pairs) * 4} model calls\n")

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    process = subprocess.Popen(
        ["llama-server", "-m", args.gguf, "--port", str(args.port), "-c", "4096",
         "-t", "8", "--no-warmup"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    records = []
    try:
        wait_for_server(args.port)
        for pair in pairs:
            print(f"=== {pair['name']} ===")
            for half, is_recursive in (("code", True), ("improved_code", False)):
                # The pair's own halves decide the ground truth: whatever the
                # collector labelled, only a half that really self-calls counts as
                # recursive, so a mislabelled pair cannot manufacture a false claim.
                code = pair[half]
                is_recursive = bool(recursive_functions(code))
                outputs = {}
                for task in ("line_comments", "explanation"):
                    prompt = format_prompt_without_response(
                        code, [], style="chat", tokenizer=tokenizer, task=task
                    )
                    outputs[task] = complete(args.port, prompt, args.n_predict)
                comments, ok_c, cut_c = harvest(outputs["line_comments"], "line_comments")
                explanation, ok_e, cut_e = harvest(outputs["explanation"], "explanation")
                result = assess(code, is_recursive, comments, explanation)
                flags = []
                if result["false_recursion_claim"]:
                    flags.append("CALLS A LOOP RECURSIVE")
                if result["wrong_container_evidence"]:
                    flags.append("WRONG CONTAINER")
                label = "recursive" if is_recursive else "iterative"
                valid = result["anchors_total"] - result["anchors_dropped"]
                if cut_c or cut_e:
                    flags.append("TRUNCATED")
                print(f"  {label:<10} json {int(ok_c) + int(ok_e)}/2  "
                      f"anchors {valid}/{result['anchors_total']}  "
                      f"container {'named' if result['container_named'] else 'missed'}"
                      f"{'   <- ' + ', '.join(flags) if flags else ''}")
                records.append({
                    "name": pair["name"], "is_recursive": is_recursive,
                    "json_ok": ok_c and ok_e, "truncated": cut_c or cut_e,
                    **result, "raw": outputs,
                })
    finally:
        process.terminate()
        process.wait(timeout=30)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_report(records, out.with_suffix(".md"), {p["name"]: p for p in pairs})

    loops = [r for r in records if not r["is_recursive"]]
    anchors = sum(r["anchors_total"] for r in records)
    dropped = sum(r["anchors_dropped"] for r in records)
    print(f"\n{'=' * 72}")
    cut = sum(r["truncated"] for r in records)
    intact = [r for r in records if not r["truncated"]]
    print(f"valid JSON, of output that finished: "
          f"{sum(r['json_ok'] for r in intact)}/{len(intact)}")
    print(f"ran past --n-predict={args.n_predict}          : {cut}/{len(records)}"
          " (a budget result, not a format result)")
    print(f"anchors attached to a real line   : {anchors - dropped}/{anchors}"
          f"{f'  ({(anchors - dropped) / anchors:.0%})' if anchors else ''}")
    # Only the rewritten halves declare a container, so they are the denominator.
    holders = [r for r in records if r["has_container"]]
    print(f"named a container the code declares: "
          f"{sum(r['container_named'] for r in holders)}/{len(holders)}")
    print(f"named a container that is not there: "
          f"{sum(bool(r['wrong_container_evidence']) for r in records)}/{len(records)}")
    print(f"loops described as calling itself : "
          f"{sum(r['false_recursion_claim'] for r in loops)}/{len(loops)}")
    print("\nEvery call above is printed with the sentence that produced it in")
    print(f"{out.with_suffix('.md')}. Read it before quoting any of these numbers.")


if __name__ == "__main__":
    main()
