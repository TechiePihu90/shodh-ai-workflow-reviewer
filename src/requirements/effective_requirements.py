from copy import deepcopy

from src.schemas.requirement import Requirement
from src.schemas.approval import ApprovalRecord


class ApprovalConflictError(ValueError):
    """Raised when approval records contradict each other."""


def get_nested_value(data, path):

    current = data

    for key in path.split("."):

        if not isinstance(current, dict) or key not in current:
            raise ApprovalConflictError(
                f"Invalid target path: {path}"
            )

        current = current[key]

    return current


def set_nested_value(data, path, value):

    keys = path.split(".")
    current = data

    for key in keys[:-1]:

        if key not in current or not isinstance(current[key], dict):
            raise ApprovalConflictError(
                f"Invalid target path: {path}"
            )

        current = current[key]

    if keys[-1] not in current:
        raise ApprovalConflictError(
            f"Invalid target path: {path}"
        )

    current[keys[-1]] = value


def derive_effective_requirements(
    requirements: list[Requirement],
    approvals: list[ApprovalRecord]
):

    effective = deepcopy(requirements)

    for requirement in effective:

        applicable = [
            approval
            for approval in approvals
            if approval.rule_id == requirement.rule_id
            and approval.approved is True
        ]

        # Apply changes in declared revision order
        applicable.sort(
            key=lambda item: (
                item.version,
                item.revision_order
            )
        )

        seen_orders = set()

        for approval in applicable:

            order = (approval.version, approval.revision_order)

            if order in seen_orders:
                raise ApprovalConflictError(
                    f"Duplicate revision order for {requirement.rule_id}"
                )

            seen_orders.add(order)

            current_value = get_nested_value(
                requirement.condition,
                approval.target_path
            )

            # The approved change must match the current value
            if current_value != approval.old_value:
                raise ApprovalConflictError(
                    f"Approval conflict for {requirement.rule_id}: "
                    f"expected old value {current_value}, "
                    f"received {approval.old_value}"
                )

            set_nested_value(
                requirement.condition,
                approval.target_path,
                approval.new_value
            )

    return effective