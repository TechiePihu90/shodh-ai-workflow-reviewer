
import json
from pathlib import Path

from src.schemas.requirement import Requirement
from src.schemas.workflow import Workflow
from src.schemas.approval import ApprovalRecord

from src.reviewer.consistency_checker import (
    check_requirement_workflow_consistency
)


def load_fixture():
    path = (
        Path(__file__).parent.parent
        / "fixtures"
        / "valid_basic.json"
    )

    with open(path, encoding="utf-8") as file:
        return json.load(file)


def test_valid_requirement_workflow_consistency():
    data = load_fixture()

    requirements = [
        Requirement.model_validate(item)
        for item in data["requirements"]
    ]

    workflow = Workflow.model_validate(data["workflow"])

    result = check_requirement_workflow_consistency(
        requirements, workflow
    )

    assert result["valid"] is True
    assert result["findings"] == []
    assert result["cases_checked"] == 11
    assert result["status"] == "PASS"
    assert result["verification_type"] == "sampled"


def test_workflow_mismatch_is_detected():
    data = load_fixture()

    requirements = [
        Requirement.model_validate(item)
        for item in data["requirements"]
    ]

    # Intentionally change the missing-category route.
    for node in data["workflow"]["nodes"]:
        if node["node_id"] == "check_missing":
            node["branches"][0]["target_node"] = "normal_queue"

    workflow = Workflow.model_validate(data["workflow"])

    result = check_requirement_workflow_consistency(
        requirements, workflow
    )

    assert result["valid"] is False
    assert any(
        finding["type"] == "ROUTE_MISMATCH"
        for finding in result["findings"]
    )


def test_unapproved_change_is_ignored():
    data = load_fixture()

    requirements = [
        Requirement.model_validate(item)
        for item in data["requirements"]
    ]

    workflow = Workflow.model_validate(data["workflow"])

    approval = ApprovalRecord(
        approval_id="A1",
        rule_id="R3",
        target_path="expression",
        old_value="waiting_minutes >= 30",
        new_value="waiting_minutes >= 25",
        approved=False,
        source_location="approval.json:A1"
    )

    result = check_requirement_workflow_consistency(
        requirements,
        workflow,
        approvals=[approval]
    )

    assert result["status"] == "PASS"
    assert result["valid"] is True


def test_approved_change_is_detected():
    data = load_fixture()

    requirements = [
        Requirement.model_validate(item)
        for item in data["requirements"]
    ]

    workflow = Workflow.model_validate(data["workflow"])

    approval = ApprovalRecord(
        approval_id="A2",
        rule_id="R3",
        target_path="expression",
        old_value="waiting_minutes >= 30",
        new_value="waiting_minutes >= 25",
        approved=True,
        source_location="approval.json:A2"
    )

    result = check_requirement_workflow_consistency(
        requirements,
        workflow,
        approvals=[approval]
    )

    assert result["status"] == "CHANGES_REQUIRED"
    assert result["valid"] is False

    assert any(
        finding["type"] == "ROUTE_MISMATCH"
        for finding in result["findings"]
    )
