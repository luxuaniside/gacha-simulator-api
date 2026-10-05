from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: str
    details: Any | None = None
    status_code: int


class APIException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Any | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


async def api_exception_handler(
    request: Request,
    exc: Exception,
):
    if not isinstance(exc, APIException):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,
):
    if not isinstance(exc, RequestValidationError):
        raise exc

    return JSONResponse(
        status_code=422,
        content=APIError(
            code="validation_error",
            message="The request contains invalid data. Check the console for more details.",
            details=exc.errors(),
            status_code=422
        ).model_dump(),
    )