
from src.schemas.requirement import Requirement
from src.schemas.workflow import Workflow
from src.schemas.approval import ApprovalRecord

from src.workflow.behavior_checker import route_ticket
from src.parser.condition_parser import evaluate_condition
from src.requirements.effective_requirements import (
    derive_effective_requirements
)


def check_requirement_workflow_consistency(
    requirements: list[Requirement],
    workflow: Workflow,
    approvals: list[ApprovalRecord] | None = None
) -> dict:

    findings = []

    # Apply approved changes only.
    try:
        effective_requirements = derive_effective_requirements(
            requirements,
            approvals or []
        )
    except Exception as exc:
        return {
            "valid": False,
            "status": "INCOMPLETE",
            "findings": [{
                "type": "APPROVAL_ERROR",
                "message": str(exc)
            }],
            "cases_checked": 0,
            "verification_type": "sampled"
        }

    # Test cases.
    test_cases = [
        {
            "name": "missing_category",
            "ticket": {
                "urgent": False,
                "waiting_minutes": 10
            }
        },
        {
            "name": "missing_category_and_urgent",
            "ticket": {
                "urgent": True,
                "waiting_minutes": 60
            }
        },
        {
            "name": "urgent_ticket",
            "ticket": {
                "category": "billing",
                "urgent": True,
                "waiting_minutes": 10
            }
        },
        {
            "name": "urgent_and_waiting_35_minutes",
            "ticket": {
                "category": "billing",
                "urgent": True,
                "waiting_minutes": 35
            }
        },
        {
            "name": "waiting_24_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 24
            }
        },
        {
            "name": "waiting_25_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 25
            }
        },
        {
            "name": "waiting_26_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 26
            }
        },
        {
            "name": "waiting_29_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 29
            }
        },
        {
            "name": "waiting_30_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 30
            }
        },
        {
            "name": "waiting_31_minutes",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 31
            }
        },
        {
            "name": "normal_ticket",
            "ticket": {
                "category": "billing",
                "urgent": False,
                "waiting_minutes": 10
            }
        }
    ]

    # Compare expected and actual routes.
    for case in test_cases:
        ticket = case["ticket"]

        try:
            expected = None

            for requirement in effective_requirements:
                expression = requirement.condition.get("expression")

                if not isinstance(expression, str):
                    raise ValueError(
                        f"Invalid condition in {requirement.rule_id}"
                    )

                if evaluate_condition(expression, ticket):
                    expected = requirement.action
                    break

            if expected is None:
                expected = "normal_queue"

            actual = route_ticket(workflow, ticket)

        except Exception as exc:
            findings.append({
                "type": "INCOMPLETE",
                "test_case": case["name"],
                "ticket": ticket,
                "message": str(exc)
            })
            continue

        if actual != expected:
            findings.append({
                "type": "ROUTE_MISMATCH",
                "test_case": case["name"],
                "ticket": ticket,
                "expected": expected,
                "actual": actual,
                "counterexample": ticket
            })

    # Determine status.
    has_incomplete = any(
        item["type"] in ("INCOMPLETE", "APPROVAL_ERROR")
        for item in findings
    )

    if has_incomplete:
        status = "INCOMPLETE"
    elif findings:
        status = "CHANGES_REQUIRED"
    else:
        status = "PASS"

    return {
        "valid": status == "PASS",
        "status": status,
        "findings": findings,
        "cases_checked": len(test_cases),
        "verification_type": "sampled"
    }
