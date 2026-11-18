
from src.schemas.requirement import Requirement
from src.schemas.specification import Specification, SpecificationRule
from src.schemas.workflow import Workflow, WorkflowNode, WorkflowBranch
from src.model.model_client import FakeModelClient
from src.reviewer.review_engine import run_full_review


def make_test_data():

    requirements = [
        Requirement(
            rule_id="R1",
            description="Missing category goes to manual review",
            condition={"expression": "category is None"},
            action="manual_review",
            source_location="policy.txt:R1"
        ),
        Requirement(
            rule_id="R2",
            description="Urgent tickets go to priority queue",
            condition={"expression": "urgent == True"},
            action="priority_queue",
            source_location="policy.txt:R2"
        ),
        Requirement(
            rule_id="R3",
            description="Waiting 30 minutes goes to escalation",
            condition={"expression": "waiting_minutes >= 30"},
            action="escalation",
            source_location="policy.txt:R3"
        )
    ]

    specification = Specification(
        version=1,
        rules=[
            SpecificationRule(
                rule_id="R1",
                condition={"expression": "category is None"},
                action="manual_review",
                priority=1
            ),
            SpecificationRule(
                rule_id="R2",
                condition={"expression": "urgent == True"},
                action="priority_queue",
                priority=2
            ),
            SpecificationRule(
                rule_id="R3",
                condition={"expression": "waiting_minutes >= 30"},
                action="escalation",
                priority=3
            )
        ]
    )

    workflow = Workflow(
        version=1,
        nodes=[
            WorkflowNode(
                node_id="start",
                node_type="start",
                destination="check_missing"
            ),

            WorkflowNode(
                node_id="check_missing",
                node_type="condition",
                branches=[
                    WorkflowBranch(
                        condition={"expression": "category is None"},
                        target_node="manual_review"
                    ),
                    WorkflowBranch(
                        target_node="check_urgent"
                    )
                ]
            ),

            WorkflowNode(
                node_id="check_urgent",
                node_type="condition",
                branches=[
                    WorkflowBranch(
                        condition={"expression": "urgent == True"},
                        target_node="priority_queue"
                    ),
                    WorkflowBranch(
                        target_node="check_waiting"
                    )
                ]
            ),

            WorkflowNode(
                node_id="check_waiting",
                node_type="condition",
                branches=[
                    WorkflowBranch(
                        condition={"expression": "waiting_minutes >= 30"},
                        target_node="escalation"
                    ),
                    WorkflowBranch(
                        target_node="normal_queue"
                    )
                ]
            ),

            WorkflowNode(
                node_id="manual_review",
                node_type="end"
            ),

            WorkflowNode(
                node_id="priority_queue",
                node_type="end"
            ),

            WorkflowNode(
                node_id="escalation",
                node_type="end"
            ),

            WorkflowNode(
                node_id="normal_queue",
                node_type="end"
            )
        ]
    )

    return requirements, specification, workflow


def test_full_review_passes():

    requirements, specification, workflow = make_test_data()

    client = FakeModelClient()

    result = run_full_review(
        client,
        requirements,
        specification,
        workflow
    )

    assert result["status"] == "PASS"
    assert result["findings"] == []


def test_full_review_detects_specification_mismatch():

    requirements, specification, workflow = make_test_data()

    specification.rules[0].action = "normal_queue"

    client = FakeModelClient()

    result = run_full_review(
        client,
        requirements,
        specification,
        workflow
    )

    assert result["status"] == "CHANGES_REQUIRED"

    assert any(
        item["type"] == "ACTION_MISMATCH"
        for item in result["findings"]
    )


def test_full_review_handles_model_failure():

    requirements, specification, workflow = make_test_data()

    class BrokenClient:

        def review(self, prompt):
            raise RuntimeError("Model unavailable")

    result = run_full_review(
        BrokenClient(),
        requirements,
        specification,
        workflow
    )

    assert result["status"] == "INCOMPLETE"

    assert any(
        item["type"] == "MODEL_CALL_FAILED"
        for item in result["findings"]
    )
