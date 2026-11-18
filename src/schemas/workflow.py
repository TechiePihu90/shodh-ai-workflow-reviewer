from pydantic import BaseModel, Field
from typing import Optional, Any


class WorkflowBranch(BaseModel):
    condition: Optional[dict[str, Any]] = None
    target_node: str


class WorkflowNode(BaseModel):
    node_id: str
    node_type: str

    condition: Optional[dict[str, Any]] = None
    branches: list[WorkflowBranch] = Field(default_factory=list)

    destination: Optional[str] = None


class Workflow(BaseModel):
    version: int = Field(default=1, ge=1)
    nodes: list[WorkflowNode]