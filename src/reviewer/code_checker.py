
import ast
from src.schemas.code_snippet import CodeSnippet
from src.schemas.requirement import Requirement


class CodeCheckError(ValueError):
    pass


def normalize_ast(node):
    if isinstance(node, ast.Compare):
        return (
            "Compare",
            normalize_ast(node.left),
            tuple(type(op).__name__ for op in node.ops),
            tuple(normalize_ast(item) for item in node.comparators)
        )

    if isinstance(node, ast.Name):
        return ("Name", node.id)

    if isinstance(node, ast.Constant):
        return ("Constant", node.value)

    if isinstance(node, ast.BoolOp):
        return (
            type(node.op).__name__,
            tuple(normalize_ast(item) for item in node.values)
        )

    if isinstance(node, ast.UnaryOp):
        return (type(node.op).__name__, normalize_ast(node.operand))

    if isinstance(node, ast.Is):
        return ("Is",)

    return (type(node).__name__,)


def check_code_snippet(
    snippet: CodeSnippet,
    requirement: Requirement | None = None
) -> dict:

    findings = []

    if snippet.language.lower() != "python":
        return {
            "valid": False,
            "findings": [{
                "type": "UNSUPPORTED_LANGUAGE",
                "message": f"Unsupported language: {snippet.language}",
                "source_location": snippet.source_location
            }]
        }

    try:
        tree = ast.parse(snippet.code)
    except SyntaxError as exc:
        return {
            "valid": False,
            "findings": [{
                "type": "SYNTAX_ERROR",
                "message": str(exc),
                "source_location": snippet.source_location
            }]
        }

    if not tree.body:
        return {
            "valid": False,
            "findings": [{
                "type": "EMPTY_CODE",
                "message": "Code snippet is empty.",
                "source_location": snippet.source_location
            }]
        }

    if requirement is None:
        return {
            "valid": False,
            "findings": [{
                "type": "REQUIREMENT_MISSING",
                "message": "Requirement must be provided for semantic checking.",
                "source_location": snippet.source_location
            }]
        }

    if snippet.rule_id != requirement.rule_id:
        findings.append({
            "type": "RULE_ID_MISMATCH",
            "message": "Snippet rule ID does not match requirement rule ID.",
            "source_location": snippet.source_location
        })

    # Check expected action
    action_found = any(
        isinstance(node, ast.Constant) and node.value == requirement.action
        for node in ast.walk(tree)
    )

    if not action_found:
        findings.append({
            "type": "CODE_ACTION_MISMATCH",
            "rule_id": requirement.rule_id,
            "message": f"Expected action '{requirement.action}' not found.",
            "source_location": snippet.source_location
        })

    # Check expected condition
    expression = requirement.condition.get("expression")

    if not isinstance(expression, str):
        findings.append({
            "type": "INVALID_REQUIREMENT_CONDITION",
            "rule_id": requirement.rule_id,
            "message": "Requirement condition must contain an expression.",
            "source_location": snippet.source_location
        })
    else:
        try:
            expected_tree = ast.parse(expression, mode="eval")
            expected_condition = normalize_ast(expected_tree.body)

            actual_conditions = [
                normalize_ast(node.test)
                for node in ast.walk(tree)
                if isinstance(node, ast.If)
            ]

            if expected_condition not in actual_conditions:
                findings.append({
                    "type": "CODE_CONDITION_MISMATCH",
                    "rule_id": requirement.rule_id,
                    "message": f"Expected condition '{expression}' not found.",
                    "source_location": snippet.source_location
                })

        except SyntaxError as exc:
            findings.append({
                "type": "INVALID_REQUIREMENT_CONDITION",
                "message": str(exc),
                "source_location": snippet.source_location
            })

    return {
        "valid": len(findings) == 0,
        "findings": findings
    }
