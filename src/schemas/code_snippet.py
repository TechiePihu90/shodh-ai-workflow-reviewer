from pydantic import BaseModel, Field


class CodeSnippet(BaseModel):
    snippet_id: str
    rule_id: str

    language: str = "python"
    code: str

    source_location: str
    version: int = Field(default=1, ge=1)