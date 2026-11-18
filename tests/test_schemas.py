from src.schemas.requirement import Requirement
from src.schemas.specification import Specification
from src.schemas.workflow import Workflow
from src.schemas.code_snippet import CodeSnippet
from src.schemas.approval import ApprovalRecord


def test_requirement():

    data = Requirement(
        rule_id="R1",
        description="Missing category",
        condition={
            "field": "category",
            "operator": "missing"
        },
        action="manual_review",
        source_location="policy.pdf:page1"
    )

    assert data.rule_id == "R1"


def test_approval():

    data = ApprovalRecord(
        approval_id="A1",
        rule_id="R3",
        target_path="value",
        old_value=30,
        new_value=25,
        approved=True,
        approved_by="Manager",
        source_location="approval.json"
    )

    assert data.new_value == 25
    assert data.approved is True
    assert data.target_path == "value"