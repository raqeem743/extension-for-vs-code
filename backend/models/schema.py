
from pydantic import BaseModel, Field


class ErrorRequest(BaseModel):
    error: str = Field(min_length=1)
    code: str = ""
    file_name: str = "unknown"
    language: str = "unknown"


class ErrorResponse(BaseModel):
    explanation: str
    cause: str
    fix: str
