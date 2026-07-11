from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.errors import (
    build_error_body,
    error_code_for_exception,
    error_code_for_status,
)
from app.core.logging import configure_logging
from app.core.request_context import get_request_id
from app.core.startup import log_startup_diagnostics
from app.middlewares import MaintenanceMiddleware, RequestLoggingMiddleware
from app.middlewares.logging import REQUEST_ID_HEADER
from app.platform.exceptions import ApplicationError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log_startup_diagnostics()
    yield


def create_app() -> FastAPI:
    settings.assert_production_security()
    configure_logging()

    docs_url = "/docs" if settings.api_docs_enabled else None
    redoc_url = "/redoc" if settings.api_docs_enabled else None
    openapi_url = "/openapi.json" if settings.api_docs_enabled else None

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.JWT_SECRET_KEY,
        same_site="lax",
        https_only=settings.COOKIE_SECURE,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[REQUEST_ID_HEADER],
    )
    # Maintenance inside request logging so 503s still get X-Request-ID + access logs.
    application.add_middleware(MaintenanceMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.include_router(api_router, prefix="/api/v1")

    def _request_id(request: Request) -> str | None:
        return getattr(request.state, "request_id", None) or get_request_id()

    def _error_headers(request: Request) -> dict[str, str]:
        rid = _request_id(request)
        return {REQUEST_ID_HEADER: rid} if rid else {}

    @application.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_body(
                message=exc.message,
                error_code=error_code_for_exception(exc),
                request_id=_request_id(request),
            ),
            headers=_error_headers(request),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Keep message user-safe; do not dump raw validator internals.
        message = "Request validation failed"
        if exc.errors():
            first = exc.errors()[0]
            loc = ".".join(str(part) for part in first.get("loc", ()) if part != "body")
            detail = first.get("msg")
            if loc and detail:
                message = f"{loc}: {detail}"
            elif detail:
                message = str(detail)
        return JSONResponse(
            status_code=422,
            content=build_error_body(
                message=message,
                error_code="VALIDATION_ERROR",
                request_id=_request_id(request),
            ),
            headers=_error_headers(request),
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, str):
            message = detail
        else:
            message = error_code_for_status(exc.status_code).replace("_", " ").title()
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_body(
                message=message,
                error_code=error_code_for_status(exc.status_code),
                request_id=_request_id(request),
            ),
            headers=_error_headers(request),
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        # Never leak stack traces to clients.
        import logging

        from app.core.logging import get_logger, log_json

        log_json(
            get_logger("placementos.error"),
            logging.ERROR,
            event="http.unhandled_exception",
            request_id=_request_id(request),
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content=build_error_body(
                message="An unexpected error occurred. Please try again",
                error_code="INTERNAL_ERROR",
                request_id=_request_id(request),
            ),
            headers=_error_headers(request),
        )

    @application.get("/health")
    async def root_health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/ready", response_model=None)
    async def root_ready() -> JSONResponse:
        from sqlalchemy import text

        from app.database.session import SessionLocal

        try:
            db = SessionLocal()
            try:
                db.execute(text("SELECT 1"))
            finally:
                db.close()
            return JSONResponse(
                status_code=200,
                content={"status": "ready", "database": "ok"},
            )
        except Exception as exc:  # noqa: BLE001
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "database": "error",
                    "detail": type(exc).__name__,
                },
            )

    return application


app = create_app()


def main() -> None:
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )


if __name__ == "__main__":
    main()
