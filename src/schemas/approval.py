from pydantic import BaseModel, Field
from typing import Any, Optional


class ApprovalRecord(BaseModel):

    approval_id: str
    rule_id: str

    target_path: str

    old_value: Any
    new_value: Any

    approved: bool
    approved_by: Optional[str] = None

    version: int = Field(default=1, ge=1)
    revision_order: int = Field(default=1, ge=1)

    source_location: str