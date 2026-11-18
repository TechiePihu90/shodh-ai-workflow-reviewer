
from typing import Any


ALLOWED_STATUSES = {
    "PASS",
    "CHANGES_REQUIRED",
    "INCOMPLETE"
}


class ModelResponseValidationError(ValueError):
    pass


def validate_model_response(
    response: dict[str, Any],
    known_rule_ids: set[str] | None = None,
    known_source_locations: set[str] | None = None
) -> dict[str, Any]:

    if not isinstance(response, dict):
        raise ModelResponseValidationError(
            "Model response must be a dictionary."
        )

    status = response.get("status")
    findings = response.get("findings")
    summary = response.get("summary")

    if status not in ALLOWED_STATUSES:
        raise ModelResponseValidationError(
            f"Invalid status: {status}"
        )

    if not isinstance(summary, str) or not summary.strip():
        raise ModelResponseValidationError(
            "Response summary must be a non-empty string."
        )

    if not isinstance(findings, list):
        raise ModelResponseValidationError(
            "Findings must be a list."
        )

    if status == "PASS" and findings:
        raise ModelResponseValidationError(
            "PASS response cannot contain findings."
        )

    if status == "CHANGES_REQUIRED" and not findings:
        raise ModelResponseValidationError(
            "CHANGES_REQUIRED must contain at least one finding."
        )

    for index, finding in enumerate(findings):

        if not isinstance(finding, dict):
            raise ModelResponseValidationError(
                f"Finding {index} must be a dictionary."
            )

        for field in ("type", "message", "evidence"):
            value = finding.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ModelResponseValidationError(
                    f"Finding {index} has invalid or missing {field}."
                )

        rule_id = finding.get("rule_id")

        if rule_id is not None:
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise ModelResponseValidationError(
                    f"Finding {index} has an invalid rule_id."
                )

            if (
                known_rule_ids is not None
                and rule_id not in known_rule_ids
            ):
                raise ModelResponseValidationError(
                    f"Unknown rule reference: {rule_id}"
                )

        source_location = finding.get("source_location")

        if source_location is not None:
            if (
                not isinstance(source_location, str)
                or not source_location.strip()
            ):
                raise ModelResponseValidationError(
                    f"Finding {index} has an invalid source_location."
                )

            if (
                known_source_locations is not None
                and source_location not in known_source_locations
            ):
                raise ModelResponseValidationError(
                    f"Unknown source location: {source_location}"
                )

    return response
