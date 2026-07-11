import json
import logging
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.errors import (
    build_error_body,
    error_code_for_status,
)
from app.core.request_context import clear_request_id, set_request_id
from app.middlewares.logging import REQUEST_ID_HEADER, resolve_request_id
from app.platform.auth.exceptions import UnauthorizedError
from app.platform.exceptions import ApplicationError, error_code_from_class_name
from starlette.requests import Request


def test_error_code_from_class_name() -> None:
    assert error_code_from_class_name("UnauthorizedError") == "UNAUTHORIZED"
    assert error_code_from_class_name("InvalidAuthCodeError") == "INVALID_AUTH_CODE"
    assert error_code_from_class_name("Error") == "ERROR"


def test_application_error_sets_default_error_code() -> None:
    exc = UnauthorizedError()
    assert exc.error_code == "UNAUTHORIZED"
    assert exc.status_code == 401


def test_application_error_allows_explicit_error_code() -> None:
    exc = ApplicationError("Nope", status_code=409, error_code="CUSTOM_CONFLICT")
    assert exc.error_code == "CUSTOM_CONFLICT"


def test_build_error_body_includes_request_id() -> None:
    set_request_id("req-test-12345")
    try:
        body = build_error_body(message="fail", error_code="BAD_REQUEST")
        assert body == {
            "error_code": "BAD_REQUEST",
            "message": "fail",
            "request_id": "req-test-12345",
        }
    finally:
        clear_request_id()


def test_error_code_for_status() -> None:
    assert error_code_for_status(422) == "VALIDATION_ERROR"
    assert error_code_for_status(503) == "SERVICE_UNAVAILABLE"
    assert error_code_for_status(418) == "HTTP_418"


def test_resolve_request_id_accepts_valid_incoming() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [(b"x-request-id", b"client-req-abc123")],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)
    assert resolve_request_id(request) == "client-req-abc123"


def test_resolve_request_id_rejects_unsafe_incoming() -> None:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [(b"x-request-id", b"bad id with spaces!!!")],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)
    generated = resolve_request_id(request)
    assert generated != "bad id with spaces!!!"
    assert len(generated) >= 8


def test_health_returns_request_id_header(monkeypatch: pytest.MonkeyPatch) -> None:
    import main as main_module
    from app.core.config import Settings

    # Avoid DB/startup side effects that need a live database.
    monkeypatch.setattr(main_module, "log_startup_diagnostics", lambda: None)

    local = Settings(
        ENVIRONMENT="local",
        ENABLE_DEV_LOGIN=False,
        COOKIE_SECURE=False,
        JWT_SECRET_KEY="test-secret-key-at-least-32-chars!!",
    )
    monkeypatch.setattr(main_module, "settings", local)

    app = main_module.create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    assert len(response.headers[REQUEST_ID_HEADER]) >= 8


def test_health_echoes_incoming_request_id(monkeypatch: pytest.MonkeyPatch) -> None:
    import main as main_module

    monkeypatch.setattr(main_module, "log_startup_diagnostics", lambda: None)
    app = main_module.create_app()
    client = TestClient(app)
    rid = f"e2e-{uuid4().hex[:16]}"
    response = client.get("/health", headers={"X-Request-ID": rid})
    assert response.headers[REQUEST_ID_HEADER] == rid


def test_application_error_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    import main as main_module
    from fastapi import APIRouter

    monkeypatch.setattr(main_module, "log_startup_diagnostics", lambda: None)
    app = main_module.create_app()

    router = APIRouter()

    @router.get("/__test/boom")
    def boom() -> None:
        raise UnauthorizedError("nope")

    app.include_router(router)
    client = TestClient(app)
    response = client.get("/__test/boom")
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] == "UNAUTHORIZED"
    assert body["message"] == "nope"
    assert body["request_id"]
    assert response.headers[REQUEST_ID_HEADER] == body["request_id"]
    assert "traceback" not in json.dumps(body).lower()
    assert "stack" not in json.dumps(body).lower()


def test_validation_error_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    import main as main_module
    from fastapi import APIRouter
    from pydantic import BaseModel

    monkeypatch.setattr(main_module, "log_startup_diagnostics", lambda: None)
    app = main_module.create_app()

    class Payload(BaseModel):
        name: str

    router = APIRouter()

    @router.post("/__test/validate")
    def validate(payload: Payload) -> dict[str, str]:
        return {"name": payload.name}

    app.include_router(router)
    client = TestClient(app)
    response = client.post("/__test/validate", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert "message" in body
    assert body["request_id"]


def test_structured_request_log_emitted(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    import main as main_module

    monkeypatch.setattr(main_module, "log_startup_diagnostics", lambda: None)
    app = main_module.create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="placementos.request"):
        client.get("/health")

    matching = [
        record
        for record in caplog.records
        if record.name == "placementos.request" and "http.request" in record.getMessage()
    ]
    assert matching
    payload = json.loads(matching[-1].getMessage())
    assert payload["event"] == "http.request"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status"] == 200
    assert "duration_ms" in payload
    assert "request_id" in payload
