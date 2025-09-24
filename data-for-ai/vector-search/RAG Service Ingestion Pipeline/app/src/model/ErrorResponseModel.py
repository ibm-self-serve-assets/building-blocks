# Custom error response model for 400 and 500 errors
from typing import List
from pydantic import BaseModel, Field

class ErrorResponseModel(BaseModel):
    code: int
    message: str

# Custom error response model for validation errors without anyOf
class ValidationErrorResponseModel(BaseModel):
    msg: str = Field(description="Error message")
    type: str = Field(description="Type of the error")

class CustomValidationErrorResponse(BaseModel):
    code: int
    message: str
    errors: List[ValidationErrorResponseModel]