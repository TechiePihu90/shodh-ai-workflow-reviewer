
from typing import Any

from src.model.prompt_builder import build_review_prompt
from src.model.response_validator import (
    validate_model_response,
    ModelResponseValidationError
)


def _get_value(item: Any, key: str):
    """Read a field from a dictionary or Pydantic object."""
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _to_jsonable(item: Any):
    """Convert Pydantic models and nested data into JSON-compatible data."""
    if hasattr(item, "model_dump"):
        return item.model_dump(mode="json")

    if isinstance(item, list):
        return [_to_jsonable(value) for value in item]

    if isinstance(item, dict):
        return {
            key: _to_jsonable(value)
            for key, value in item.items()
        }

    return item


def _incomplete_report(error_type: str, message: str, evidence: str):
    return {
        "status": "INCOMPLETE",
        "summary": message,
        "findings": [{
            "type": error_type,
            "message": message,
            "evidence": evidence
        }]
    }


def run_model_review(
    client,
    requirements,
    specification,
    workflow,
    code_snippets=None,
    approvals=None
) -> dict:

    code_snippets = code_snippets or []
    approvals = approvals or []

    # Convert input data into JSON-compatible objects.
    requirements_data = _to_jsonable(requirements)
    specification_data = _to_jsonable(specification)
    workflow_data = _to_jsonable(workflow)
    snippets_data = _to_jsonable(code_snippets)
    approvals_data = _to_jsonable(approvals)

    # Build the review prompt.
    try:
        prompt = build_review_prompt(
            requirements=requirements_data,
            specification=specification_data,
            workflow=workflow_data,
            code_snippets=snippets_data,
            approvals=approvals_data
        )
    except Exception as exc:
        return _incomplete_report(
            "PROMPT_BUILD_FAILED",
            "Could not build the review prompt.",
            str(exc)
        )

    # Ask the model to review the supplied data.
    try:
        response = client.review(prompt)
    except Exception as exc:
        return _incomplete_report(
            "MODEL_CALL_FAILED",
            "The model review could not be completed.",
            f"{type(exc).__name__}: {exc}"
        )

    # Collect valid rule IDs and source locations.
    known_rule_ids = {
        _get_value(item, "rule_id")
        for item in requirements
    }

    known_rule_ids.update(
        _get_value(item, "rule_id")
        for item in _get_value(specification, "rules") or []
    )

    known_rule_ids.discard(None)

    known_source_locations = {
        _get_value(item, "source_location")
        for item in requirements
    }

    known_source_locations.update(
        _get_value(item, "source_location")
        for item in code_snippets
    )

    known_source_locations.update(
        _get_value(item, "source_location")
        for item in approvals
    )

    known_source_locations.discard(None)

    # Validate the model response before returning it.
    try:
        validated_response = validate_model_response(
            response,
            known_rule_ids=known_rule_ids,
            known_source_locations=known_source_locations
        )
    except (ModelResponseValidationError, Exception) as exc:
        return _incomplete_report(
            "INVALID_MODEL_RESPONSE",
            "The model returned an invalid or unsupported response.",
            f"{type(exc).__name__}: {exc}"
        )

    return {
        "status": validated_response["status"],
        "summary": validated_response["summary"],
        "findings": validated_response["findings"]
    }
