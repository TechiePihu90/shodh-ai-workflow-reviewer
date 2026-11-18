
import networkx as nx

from src.schemas.workflow import Workflow


class WorkflowGraphError(ValueError):
    """Raised when a workflow graph is invalid."""


def build_workflow_graph(workflow: Workflow) -> nx.DiGraph:
    graph = nx.DiGraph()

    # Add all workflow nodes
    for node in workflow.nodes:
        if node.node_id in graph:
            raise WorkflowGraphError(
                f"Duplicate node ID: {node.node_id}"
            )

        graph.add_node(node.node_id, node_type=node.node_type)

    # Add connections
    for node in workflow.nodes:

        if node.destination:
            if node.destination not in graph:
                raise WorkflowGraphError(
                    f"Unknown destination: {node.destination}"
                )

            graph.add_edge(node.node_id, node.destination)

        for branch in node.branches:
            if branch.target_node not in graph:
                raise WorkflowGraphError(
                    f"Unknown branch target: {branch.target_node}"
                )

            graph.add_edge(node.node_id, branch.target_node)

    return graph


def check_workflow_graph(workflow: Workflow) -> dict:
    graph = build_workflow_graph(workflow)

    if not workflow.nodes:
        return {
            "valid": False,
            "errors": ["Workflow has no nodes."],
            "unreachable_nodes": []
        }

    # Find entry node
    entry_nodes = [
        node.node_id
        for node in workflow.nodes
        if node.node_type.lower() == "start"
    ]

    if len(entry_nodes) != 1:
        return {
            "valid": False,
            "errors": [
                "Workflow must contain exactly one start node."
            ],
            "unreachable_nodes": []
        }

    start_node = entry_nodes[0]

    reachable = nx.descendants(graph, start_node)
    reachable.add(start_node)

    unreachable = [
        node.node_id
        for node in workflow.nodes
        if node.node_id not in reachable
    ]

    errors = []

    if unreachable:
        errors.append(
            f"Unreachable nodes found: {unreachable}"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "unreachable_nodes": unreachable
    }
