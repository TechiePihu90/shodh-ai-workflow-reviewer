
from src.schemas.workflow import Workflow
from src.parser.condition_parser import evaluate_condition


class WorkflowExecutionError(ValueError):
    pass


def route_ticket(workflow: Workflow, ticket: dict) -> str:
    nodes = {node.node_id: node for node in workflow.nodes}

    if len(nodes) != len(workflow.nodes):
        raise WorkflowExecutionError("Duplicate node IDs found.")

    start_nodes = [
        node for node in workflow.nodes
        if node.node_type.lower() == "start"
    ]

    if len(start_nodes) != 1:
        raise WorkflowExecutionError(
            "Workflow must have exactly one start node."
        )

    current_node = start_nodes[0]
    visited = set()

    while True:
        if current_node.node_id in visited:
            raise WorkflowExecutionError("Workflow cycle detected.")

        visited.add(current_node.node_id)

        if current_node.node_type.lower() == "end":
            return current_node.node_id

        next_node_id = None

        if current_node.node_type.lower() == "start":
            next_node_id = current_node.destination

        else:
            fallback = None

            for branch in current_node.branches:
                if branch.condition is None:
                    fallback = branch.target_node
                    continue

                expression = branch.condition.get("expression")

                if not isinstance(expression, str):
                    raise WorkflowExecutionError(
                        "Invalid branch condition."
                    )

                if evaluate_condition(expression, ticket):
                    next_node_id = branch.target_node
                    break

            if next_node_id is None:
                next_node_id = fallback

            if next_node_id is None:
                next_node_id = current_node.destination

        if next_node_id is None:
            raise WorkflowExecutionError(
                f"No matching route from node {current_node.node_id}."
            )

        if next_node_id not in nodes:
            raise WorkflowExecutionError(
                f"Unknown workflow node: {next_node_id}"
            )

        current_node = nodes[next_node_id]
