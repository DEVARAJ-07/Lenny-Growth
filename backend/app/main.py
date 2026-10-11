"""
FastAPI application entrypoint for The Lenny Growth Assistant.
"""
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.logging import setup_logging, logger
from app.errors import (
    AppError,
    app_error_handler,
    validation_error_handler,
    generic_error_handler
)
from app.db.session import init_db
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chats import router as chats_router
from app.api.messages import router as messages_router
from app.api.artifacts import router as artifacts_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("starting_lenny_growth_assistant_backend", version="1.0.0")
    await init_db()
    yield
    logger.info("shutting_down_lenny_growth_assistant_backend")


app = FastAPI(
    title="The Lenny Growth Assistant API",
    description="Grounded AI assistant powered by Lenny's Podcast transcripts with hybrid search and artifact rendering.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and Latency Middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    duration_ms = int((time.time() - start_time) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)

    # Don't log health spam
    if not request.url.path.startswith("/health"):
        logger.info(
            "http_request_processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id
        )

    return response


# Register structured error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Include API Routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(artifacts_router)
app.include_router(admin_router)
