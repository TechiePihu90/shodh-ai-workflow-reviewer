from pydantic import BaseModel, Field
from typing import Any


class SpecificationRule(BaseModel):
    rule_id: str
    condition: dict[str, Any]
    action: str
    priority: int = Field(ge=1)


class Specification(BaseModel):
    version: int = Field(default=1, ge=1)
    rules: list[SpecificationRule]