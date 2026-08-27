"""A divisibility claim needs an operator that can decide divisibility.

`sum_digits_tree` accumulates `carried * 10 + value` and was described as
counting paths "divisible by 10". Nothing in it tests divisibility - there is no
`%` anywhere - so the purpose was invented rather than misread, and that is
decidable from the source.

The negative cases matter more than the positive ones. This check earns its
place only if it stays silent on correct prose: it fired on "recursively
reverses the remainder" during development - the rest of a stack, not a modulo -
which is the same two-meanings mistake as reading "stack overflow" as a
`std::stack`. `remainder` was removed for it.
"""

from __future__ import annotations

from qwen_cpp_review.claim_checks import check_claims

NO_MODULO = (
    "int paths(Node* node, int carried) {\n"
    "  if (node == nullptr) return 0;\n"
    "  carried = carried * 10 + node->value;\n"
    "  return paths(node->left, carried) + paths(node->right, carried);\n"
    "}"
)
WITH_MODULO = (
    "int paths(Node* node, int carried) {\n"
    "  if (node == nullptr) return 0;\n"
    "  carried = carried * 10 + node->value;\n"
    "  if (carried % 10 == 0) return 1;\n"
    "  return paths(node->left, carried) + paths(node->right, carried);\n"
    "}"
)
PARITY_BY_MASK = "bool odd(int n) { return (n & 1) != 0; }"


def kinds(code: str, prose: str) -> list[str]:
    return [c.kind for c in check_claims(code, prose).contradictions]


def test_divisibility_claimed_with_no_operator_to_decide_it():
    assert "no divisibility test in the code" in kinds(
        NO_MODULO, "Counts root-to-leaf paths whose value is divisible by 10."
    )


def test_multiple_of_a_number_is_the_same_claim():
    assert "no divisibility test in the code" in kinds(
        NO_MODULO, "Counts paths forming a number that is a multiple of 10."
    )


def test_the_claim_stands_when_the_code_can_decide_it():
    assert kinds(WITH_MODULO, "Counts paths whose value is divisible by 10.") == []


def test_parity_written_as_a_bit_mask_counts_as_a_test():
    """`n & 1` decides parity without a percent sign; flagging it would be wrong."""
    assert kinds(PARITY_BY_MASK, "Returns true for odd numbers.") == []


def test_the_rest_of_a_container_is_not_a_modulo_remainder():
    """Caught firing on real output: 'recursively reverses the remainder'."""
    stack_code = (
        "void reverseStack(stack<int>& st) {\n"
        "  if (st.empty()) return;\n"
        "  int top = st.top(); st.pop();\n"
        "  reverseStack(st);\n"
        "  insertAtBottom(st, top);\n"
        "}"
    )
    assert kinds(stack_code, "Pops the top element and recursively reverses the remainder.") == []


def test_partitioning_prose_is_not_an_arithmetic_claim():
    assert kinds(NO_MODULO, "Divide the array into two halves and recurse on each.") == []


def test_multiple_without_a_number_is_not_a_claim_about_arithmetic():
    assert kinds(NO_MODULO, "The helper is called a multiple of times per node.") == []
