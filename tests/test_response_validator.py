
import pytest

from src.model.response_validator import (
    validate_model_response,
    ModelResponseValidationError
)


def test_valid_pass_response():
    response = {
        "status": "PASS",
        "findings": [],
        "summary": "All checks passed."
    }

    result = validate_model_response(response)

    assert result["status"] == "PASS"


def test_valid_changes_required_response():
    response = {
        "status": "CHANGES_REQUIRED",
        "findings": [{
            "type": "ACTION_MISMATCH",
            "message": "Wrong action detected.",
            "evidence": "Expected escalation but found normal_queue.",
            "rule_id": "R3",
            "source_location": "policy.txt:R3"
        }],
        "summary": "An issue was detected."
    }

    result = validate_model_response(
        response,
        known_rule_ids={"R1", "R2", "R3"},
        known_source_locations={"policy.txt:R3"}
    )

    assert result["status"] == "CHANGES_REQUIRED"


def test_invalid_status_rejected():
    response = {
        "status": "UNKNOWN",
        "findings": [],
        "summary": "Test"
    }

    with pytest.raises(ModelResponseValidationError):
        validate_model_response(response)


def test_pass_with_findings_rejected():
    response = {
        "status": "PASS",
        "findings": [{
            "type": "ERROR",
            "message": "Issue found.",
            "evidence": "Evidence"
        }],
        "summary": "Test"
    }

    with pytest.raises(ModelResponseValidationError):
        validate_model_response(response)


def test_finding_without_evidence_rejected():
    response = {
        "status": "CHANGES_REQUIRED",
        "findings": [{
            "type": "ERROR",
            "message": "Issue found."
        }],
        "summary": "Test"
    }

    with pytest.raises(ModelResponseValidationError):
        validate_model_response(response)


def test_unknown_rule_reference_rejected():
    response = {
        "status": "CHANGES_REQUIRED",
        "findings": [{
            "type": "ERROR",
            "message": "Issue found.",
            "evidence": "Some evidence",
            "rule_id": "R99"
        }],
        "summary": "Test"
    }

    with pytest.raises(ModelResponseValidationError):
        validate_model_response(
            response,
            known_rule_ids={"R1", "R2", "R3"}
        )


def test_incomplete_response_allowed():
    response = {
        "status": "INCOMPLETE",
        "findings": [],
        "summary": "Some checks could not be completed."
    }

    result = validate_model_response(response)

    assert result["status"] == "INCOMPLETE"
