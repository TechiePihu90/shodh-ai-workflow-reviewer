from pydantic import BaseModel, Field
from typing import Any, Optional


class Requirement(BaseModel):
    rule_id: str
    description: str

    condition: dict[str, Any]
    action: str

    source_location: str
    version: int = Field(default=1, ge=1)

    time_unit: Optional[str] = None