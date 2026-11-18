import ast
import operator
from typing import Any


class ConditionError(ValueError):
    """Raised when a condition is invalid or unsupported."""


class _Missing:
    """Represents a field that does not exist in the input."""

    pass


MISSING = _Missing()


# Supported comparison operators
COMPARISON_OPERATORS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class ConditionParser:

    def evaluate(self, condition: str, data: dict[str, Any]) -> bool:
        """
        Parse and evaluate a condition against ticket data.
        Does not execute arbitrary Python code.
        """

        if not isinstance(condition, str) or not condition.strip():
            raise ConditionError("Condition must be a non-empty string.")

        if len(condition) > 2000:
            raise ConditionError("Condition is too long.")

        try:
            tree = ast.parse(condition, mode="eval")
        except SyntaxError as exc:
            raise ConditionError(
                f"Invalid condition syntax: {exc.msg}"
            ) from exc

        result = self._evaluate_node(tree.body, data)

        if not isinstance(result, bool):
            raise ConditionError(
                "Condition must produce a boolean result."
            )

        return result

    def _evaluate_node(self, node: ast.AST, data: dict) -> Any:

        # Constants: 30, True, False, "billing", None
        if isinstance(node, ast.Constant):
            return node.value

        # Field names: urgent, waiting_minutes, category
        if isinstance(node, ast.Name):

            if node.id == "missing":
                return MISSING

            return data.get(node.id, MISSING)

        # AND / OR
        if isinstance(node, ast.BoolOp):

            if isinstance(node.op, ast.And):
                for value in node.values:
                    if not self._evaluate_node(value, data):
                        return False
                return True

            if isinstance(node.op, ast.Or):
                for value in node.values:
                    if self._evaluate_node(value, data):
                        return True
                return False

        # NOT
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not self._evaluate_node(node.operand, data)

        # Comparisons
        if isinstance(node, ast.Compare):

            left = self._evaluate_node(node.left, data)

            for operation, comparator in zip(
                node.ops, node.comparators
            ):

                right = self._evaluate_node(comparator, data)

                if isinstance(operation, (ast.Is, ast.IsNot)):

                    if isinstance(operation, ast.Is):
                        result = left is right
                    else:
                        result = left is not right

                elif type(operation) in COMPARISON_OPERATORS:

                    # Explicit missing-value handling
                    if left is MISSING or right is MISSING:

                        if isinstance(operation, ast.Eq):
                            result = left is right

                        elif isinstance(operation, ast.NotEq):
                            result = left is not right

                        else:
                            result = False

                    else:
                        try:
                            result = COMPARISON_OPERATORS[
                                type(operation)
                            ](left, right)

                        except TypeError as exc:
                            raise ConditionError(
                                "Incompatible values in comparison."
                            ) from exc

                else:
                    raise ConditionError(
                        "Unsupported comparison operator."
                    )

                if not result:
                    return False

                left = right

            return True

        raise ConditionError(
            f"Unsupported expression: {type(node).__name__}"
        )


# Easy-to-use function
def evaluate_condition(
    condition: str,
    data: dict[str, Any]
) -> bool:

    parser = ConditionParser()
    return parser.evaluate(condition, data)