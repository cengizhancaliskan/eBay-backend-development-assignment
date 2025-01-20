from typing import Any, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status_code, detail={"message": message, "details": details}
        )


class DatabaseError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Database error: {message}",
        )


class ValidationError(BaseAPIException):
    def __init__(self, message: str, errors: Optional[list[dict]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Validation error: {message}",
            details=errors,
        )
