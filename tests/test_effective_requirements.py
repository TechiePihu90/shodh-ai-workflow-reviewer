import pytest

from src.schemas.requirement import Requirement
from src.schemas.approval import ApprovalRecord

from src.requirements.effective_requirements import (
    derive_effective_requirements,
    ApprovalConflictError
)


def make_requirement():

    return Requirement(
        rule_id="R3",
        description="Escalate after 30 minutes",
        condition={
            "field": "waiting_minutes",
            "operator": ">=",
            "value": 30
        },
        action="escalation",
        source_location="policy.pdf:page1"
    )


def make_approval(old, new, approved, order=1):

    return ApprovalRecord(
        approval_id=f"A{order}",
        rule_id="R3",
        target_path="value",
        old_value=old,
        new_value=new,
        approved=approved,
        approved_by="Manager" if approved else None,
        revision_order=order,
        source_location="approval.json"
    )


def test_approved_change_applied():

    requirement = make_requirement()

    approval = make_approval(30, 25, True)

    result = derive_effective_requirements(
        [requirement], [approval]
    )

    assert result[0].condition["value"] == 25


def test_unapproved_change_ignored():

    requirement = make_requirement()

    approval = make_approval(30, 20, False)

    result = derive_effective_requirements(
        [requirement], [approval]
    )

    assert result[0].condition["value"] == 30


def test_conflicting_approval_rejected():

    requirement = make_requirement()

    approvals = [
        make_approval(30, 25, True, 1),
        make_approval(30, 20, True, 1)
    ]

    with pytest.raises(ApprovalConflictError):

        derive_effective_requirements(
            [requirement], approvals
        )


def test_sequential_approved_changes():

    requirement = make_requirement()

    approvals = [
        make_approval(30, 25, True, 1),
        make_approval(25, 20, True, 2)
    ]

    result = derive_effective_requirements(
        [requirement], approvals
    )

    assert result[0].condition["value"] == 20


def test_original_requirement_not_modified():

    requirement = make_requirement()

    approval = make_approval(30, 25, True)

    derive_effective_requirements(
        [requirement], [approval]
    )

    assert requirement.condition["value"] == 30