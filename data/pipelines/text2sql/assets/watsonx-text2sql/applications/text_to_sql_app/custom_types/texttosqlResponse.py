from typing import Any
from pydantic import BaseModel


class TextToSQLResponse(BaseModel):
    response: dict[str, Any]
