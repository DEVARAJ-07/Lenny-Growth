"""
Standardized structured error models and exception handlers.
Contract: { "error": { "code": str, "message": str, "request_id": str, "hint": str } }
"""
import uuid
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from app.logging import logger


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    hint: str


class StructuredErrorResponse(BaseModel):
    error: ErrorDetail


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        hint: str,
        status_code: int = 400
    ):
        self.code = code
        self.message = message
        self.hint = hint
        self.status_code = status_code
        super().__init__(message)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(
        "application_error",
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        hint=exc.hint,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
                "hint": exc.hint,
            }
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    error_msgs = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()])
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Request validation failed: {error_msgs}",
                "request_id": request_id,
                "hint": "Check request payload against API contract schema.",
            }
        }
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception("unhandled_exception", error=str(exc), request_id=request_id)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "request_id": request_id,
                "hint": "Check backend structured logs for trace details.",
            }
        }
    )
