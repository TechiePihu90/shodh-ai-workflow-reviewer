
import ast

from src.schemas.requirement import Requirement
from src.schemas.specification import Specification


def normalize_condition(condition: dict) -> str:
    """Normalize supported expressions for structural comparison."""

    expression = condition.get("expression")

    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Missing or invalid condition expression")

    tree = ast.parse(expression, mode="eval")

    def normalize(node):
        if isinstance(node, ast.Compare):
            left = normalize(node.left)
            comparators = [normalize(item) for item in node.comparators]

            # Equality is symmetric: a == b and b == a
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                left, right = sorted([left, comparators[0]])
                return ("Compare", "Eq", left, right)

            return (
                "Compare",
                tuple(type(op).__name__ for op in node.ops),
                left,
                tuple(comparators),
            )

        if isinstance(node, ast.BoolOp):
            values = sorted(normalize(item) for item in node.values)
            return (type(node.op).__name__, tuple(values))

        if isinstance(node, ast.UnaryOp):
            return (type(node.op).__name__, normalize(node.operand))

        if isinstance(node, ast.Name):
            return ("Name", node.id)

        if isinstance(node, ast.Constant):
            return ("Constant", repr(node.value))

        raise ValueError(
            f"Unsupported condition expression: {type(node).__name__}"
        )

    return repr(normalize(tree.body))


def check_specification(
    requirements: list[Requirement],
    specification: Specification,
) -> dict:
    findings = []

    requirement_map = {
        requirement.rule_id: requirement
        for requirement in requirements
    }

    specification_map = {
        rule.rule_id: rule
        for rule in specification.rules
    }

    # Check missing requirements
    for requirement in requirements:
        rule_id = requirement.rule_id

        if rule_id not in specification_map:
            findings.append({
                "type": "MISSING_REQUIREMENT",
                "rule_id": rule_id,
                "message": f"Requirement {rule_id} is missing from specification.",
                "source_location": requirement.source_location,
            })
            continue

        spec_rule = specification_map[rule_id]

        # Check conditions
        try:
            expected = normalize_condition(requirement.condition)
            actual = normalize_condition(spec_rule.condition)

            if expected != actual:
                findings.append({
                    "type": "CONDITION_MISMATCH",
                    "rule_id": rule_id,
                    "message": "Specification condition differs from requirement.",
                    "source_location": requirement.source_location,
                })

        except (ValueError, SyntaxError) as exc:
            findings.append({
                "type": "UNSUPPORTED_CONDITION",
                "rule_id": rule_id,
                "message": str(exc),
                "source_location": requirement.source_location,
            })

        # Check action
        if requirement.action != spec_rule.action:
            findings.append({
                "type": "ACTION_MISMATCH",
                "rule_id": rule_id,
                "message": (
                    f"Expected action {requirement.action}, "
                    f"found {spec_rule.action}."
                ),
                "source_location": requirement.source_location,
            })

    # Check precedence using source requirement order
    expected_order = [
        requirement.rule_id
        for requirement in requirements
        if requirement.rule_id in specification_map
    ]

    actual_order = [
        rule.rule_id
        for rule in sorted(
            specification.rules,
            key=lambda item: item.priority
        )
        if rule.rule_id in requirement_map
    ]

    if expected_order != actual_order:
        findings.append({
            "type": "PRECEDENCE_MISMATCH",
            "rule_id": None,
            "message": (
                f"Expected rule order {expected_order}, "
                f"found {actual_order}."
            ),
            "source_location": "specification.rules",
        })

    return {
        "valid": len(findings) == 0,
        "findings": findings,
        "checked_requirements": len(requirements),
        "checked_specification_rules": len(specification.rules),
    }
