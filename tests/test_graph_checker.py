
import pytest

from src.schemas.workflow import Workflow
from src.workflow.graph_checker import (
    check_workflow_graph,
    build_workflow_graph,
    WorkflowGraphError,
)


def test_valid_workflow():
    workflow = Workflow(nodes=[
        {"node_id": "start", "node_type": "start",
         "destination": "process"},
        {"node_id": "process", "node_type": "task",
         "destination": "end"},
        {"node_id": "end", "node_type": "end"},
    ])

    result = check_workflow_graph(workflow)

    assert result["valid"] is True
    assert result["unreachable_nodes"] == []


def test_unreachable_node():
    workflow = Workflow(nodes=[
        {"node_id": "start", "node_type": "start",
         "destination": "end"},
        {"node_id": "end", "node_type": "end"},
        {"node_id": "unused", "node_type": "task"},
    ])

    result = check_workflow_graph(workflow)

    assert result["valid"] is False
    assert "unused" in result["unreachable_nodes"]


def test_missing_start_node():
    workflow = Workflow(nodes=[
        {"node_id": "task", "node_type": "task"},
        {"node_id": "end", "node_type": "end"},
    ])

    result = check_workflow_graph(workflow)

    assert result["valid"] is False
    assert "exactly one start node" in result["errors"][0]


def test_invalid_destination():
    workflow = Workflow(nodes=[
        {"node_id": "start", "node_type": "start",
         "destination": "missing"},
    ])

    with pytest.raises(WorkflowGraphError):
        build_workflow_graph(workflow)


def test_invalid_branch_target():
    workflow = Workflow(nodes=[
        {
            "node_id": "start",
            "node_type": "start",
            "branches": [
                {"condition": {"urgent": True},
                 "target_node": "missing"}
            ]
        }
    ])

    with pytest.raises(WorkflowGraphError):
        build_workflow_graph(workflow)


def test_duplicate_node_ids():
    workflow = Workflow(nodes=[
        {"node_id": "start", "node_type": "start"},
        {"node_id": "start", "node_type": "task"},
    ])

    with pytest.raises(WorkflowGraphError):
        build_workflow_graph(workflow)
