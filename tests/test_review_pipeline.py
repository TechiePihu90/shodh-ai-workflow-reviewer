
from src.model.review_pipeline import run_model_review
from src.model.model_client import FakeModelClient


def sample_data():
    requirements = [{
        "rule_id": "R1",
        "description": "Missing category goes to manual review",
        "condition": {"expression": "category is None"},
        "action": "manual_review",
        "source_location": "policy.txt:R1"
    }]

    specification = {
        "rules": [{
            "rule_id": "R1",
            "condition": {"expression": "category is None"},
            "action": "manual_review",
            "priority": 1
        }]
    }

    workflow = {"nodes": []}

    return requirements, specification, workflow


def test_valid_model_review():
    requirements, specification, workflow = sample_data()

    client = FakeModelClient({
        "status": "PASS",
        "summary": "Review completed.",
        "findings": []
    })

    result = run_model_review(
        client, requirements, specification, workflow
    )

    assert result["status"] == "PASS"
    assert result["findings"] == []


def test_model_changes_required():
    requirements, specification, workflow = sample_data()

    client = FakeModelClient({
        "status": "CHANGES_REQUIRED",
        "summary": "A mismatch was found.",
        "findings": [{
            "type": "ACTION_MISMATCH",
            "message": "Wrong action detected.",
            "evidence": "Expected manual_review.",
            "rule_id": "R1",
            "source_location": "policy.txt:R1"
        }]
    })

    result = run_model_review(
        client, requirements, specification, workflow
    )

    assert result["status"] == "CHANGES_REQUIRED"


def test_model_failure_returns_incomplete():
    requirements, specification, workflow = sample_data()

    class BrokenClient:
        def review(self, prompt):
            raise RuntimeError("Model unavailable")

    result = run_model_review(
        BrokenClient(), requirements, specification, workflow
    )

    assert result["status"] == "INCOMPLETE"
    assert result["findings"][0]["type"] == "MODEL_CALL_FAILED"


def test_invalid_model_response_returns_incomplete():
    requirements, specification, workflow = sample_data()

    client = FakeModelClient({
        "status": "UNKNOWN",
        "summary": "Invalid response.",
        "findings": []
    })

    result = run_model_review(
        client, requirements, specification, workflow
    )

    assert result["status"] == "INCOMPLETE"
    assert result["findings"][0]["type"] == "INVALID_MODEL_RESPONSE"


def test_unknown_rule_reference_returns_incomplete():
    requirements, specification, workflow = sample_data()

    client = FakeModelClient({
        "status": "CHANGES_REQUIRED",
        "summary": "An issue was found.",
        "findings": [{
            "type": "ACTION_MISMATCH",
            "message": "Unknown rule detected.",
            "evidence": "Some evidence.",
            "rule_id": "R99"
        }]
    })

    result = run_model_review(
        client, requirements, specification, workflow
    )

    assert result["status"] == "INCOMPLETE"
