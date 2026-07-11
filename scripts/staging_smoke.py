"""Staging / production smoke checks against a deployed API base URL.

Usage:
  python scripts/staging_smoke.py https://placementos-api.onrender.com

Exit code 0 = all required checks passed.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request


REQUIRED_PATHS = (
    ("/health", 200),
    ("/ready", 200),
    ("/api/v1/health", 200),
    ("/api/v1/ready", 200),
)

MUST_BE_404 = (
    "/docs",
    "/redoc",
    "/openapi.json",
)


def _get(url: str, timeout: float = 60.0) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status, headers, body


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/staging_smoke.py <api-base-url>", file=sys.stderr)
        return 2

    base = argv[1].rstrip("/")
    failures: list[str] = []
    results: list[dict[str, object]] = []

    print(f"Staging smoke against {base}")
    print("-" * 60)

    # Cold-start aware first probe
    t0 = time.perf_counter()
    try:
        status, headers, body = _get(f"{base}/health")
        cold_ms = (time.perf_counter() - t0) * 1000
        results.append(
            {
                "check": "cold_health",
                "status": status,
                "latency_ms": round(cold_ms, 1),
                "request_id": headers.get("x-request-id"),
            },
        )
        print(f"GET /health (cold) -> {status} in {cold_ms:.0f}ms")
        if status != 200:
            failures.append(f"/health returned {status}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"/health unreachable: {exc}")
        print(f"GET /health FAILED: {exc}")

    for path, expected in REQUIRED_PATHS:
        if path == "/health":
            continue  # already probed
        t1 = time.perf_counter()
        try:
            status, headers, body = _get(f"{base}{path}")
            ms = (time.perf_counter() - t1) * 1000
            print(f"GET {path} -> {status} in {ms:.0f}ms")
            results.append(
                {
                    "check": path,
                    "status": status,
                    "latency_ms": round(ms, 1),
                    "request_id": headers.get("x-request-id"),
                },
            )
            if status != expected:
                failures.append(f"{path} expected {expected}, got {status}")
            if path.endswith("/ready") and status == 200:
                try:
                    payload = json.loads(body.decode("utf-8"))
                    if payload.get("status") != "ready":
                        failures.append(f"{path} body status != ready")
                except json.JSONDecodeError:
                    failures.append(f"{path} returned non-JSON body")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path} unreachable: {exc}")
            print(f"GET {path} FAILED: {exc}")

    for path in MUST_BE_404:
        try:
            status, _, _ = _get(f"{base}{path}")
            print(f"GET {path} -> {status} (expect 404)")
            if status != 404:
                failures.append(f"{path} should be 404 in staging, got {status}")
        except urllib.error.HTTPError as exc:
            print(f"GET {path} -> {exc.code} (expect 404)")
            if exc.code != 404:
                failures.append(f"{path} should be 404 in staging, got {exc.code}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path} check failed: {exc}")
            print(f"GET {path} FAILED: {exc}")

    print("-" * 60)
    if failures:
        print("FAIL")
        for item in failures:
            print(f"  - {item}")
        print(json.dumps({"ok": False, "results": results, "failures": failures}, indent=2))
        return 1

    print("PASS — liveness, readiness, and docs lockdown look good.")
    print(json.dumps({"ok": True, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
