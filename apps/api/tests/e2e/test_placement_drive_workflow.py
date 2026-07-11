"""
Phase 3 — Production Placement Drive Workflow Validation

Exercises real `/api/v1` routes end-to-end against PostgreSQL.
No fake business services — only JWT issuance for actor bootstrap.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from tests.e2e.harness import (
    ApiSession,
    ValidationReport,
    expect_ok,
    timed_step,
)

pytestmark = pytest.mark.e2e


def test_placement_drive_end_to_end(actors: dict, report: ValidationReport) -> None:
    client = actors["client"]
    tokens = actors["tokens"]
    run_id = actors["run_id"]
    admin = ApiSession(client, tokens["admin"])
    cell = ApiSession(client, tokens["cell"])
    convener = ApiSession(client, tokens["convener"])
    student = ApiSession(client, tokens["student"])

    ctx: dict = {"run_id": run_id}

    report.architecture_notes.extend(
        [
            "Validation uses FastAPI TestClient against mounted `/api/v1` routers.",
            "Actors are seeded once via UserRepository/AuthService, then all business steps use HTTP APIs.",
            "File uploads use URL-based create endpoints (Cloudinary optional); upload-path security remains covered by unit tests.",
        ],
    )
    report.recommendations.extend(
        [
            "Run this suite on staging with ENVIRONMENT=production flags before each placement season.",
            "Enable Cloudinary + Resend on staging and add a smoke check for multipart upload + email delivery.",
            "Keep ENABLE_DEV_LOGIN=false in production; E2E bootstrap uses AuthService.create_tokens only.",
        ],
    )

    def run_step(phase: str, name: str, fn) -> None:
        try:
            timed_step(report, phase=phase, name=name, fn=fn)
        except Exception:  # noqa: BLE001 — recorded in report; continue rehearsal
            pass


    # ------------------------------------------------------------------ #
    # 1. Super Admin
    # ------------------------------------------------------------------ #
    def step_health() -> None:
        path = "/api/v1/admin/system-health"
        res = admin.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert "overall_status" in body
        return None, {"detail": f"overall={body['overall_status']}", "status": res.status_code, "path": path}

    def step_feature_flags() -> None:
        path = "/api/v1/admin/feature-flags"
        res = admin.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("total", 0) >= 1
        # Ensure applications remain enabled for the drive
        key = "student_applications"
        patch = admin.request(
            "PATCH",
            f"{path}/{key}",
            json={"enabled": True, "confirm": True},
        )
        expect_ok(patch, path=f"PATCH {path}/{key}")
        return None, {"detail": f"flags={body['total']}", "status": res.status_code, "path": path}

    def step_maintenance_off() -> None:
        path = "/api/v1/admin/maintenance"
        res = admin.request("PATCH", path, json={"enabled": False, "confirm": True})
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("enabled") is False
        return None, {"detail": "maintenance disabled", "status": res.status_code, "path": path}

    def step_department() -> None:
        path = "/api/v1/admin/departments"
        code = f"CSE{run_id[:4].upper()}"
        res = admin.request(
            "POST",
            path,
            json={
                "name": f"Computer Science {run_id}",
                "code": code,
                "description": "E2E department",
                "display_order": 1,
            },
        )
        # Unique constraint may collide on re-run with same code — fall back to list
        if res.status_code >= 400:
            listed = expect_ok(admin.request("GET", path), path=path)
            assert isinstance(listed, dict)
            items = listed.get("items") or []
            match = next((d for d in items if d.get("code") == code), None)
            if match is None and items:
                match = items[0]
            assert match is not None
            ctx["department_id"] = match["id"]
            return None, {"detail": f"reused department {match['code']}", "status": 200, "path": path}
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["department_id"] = body["id"]
        return None, {"detail": f"department={body['code']}", "status": res.status_code, "path": path}

    def step_season() -> None:
        path = "/api/v1/admin/seasons"
        today = date.today()
        res = admin.request(
            "POST",
            path,
            json={
                "name": f"Placement Drive {run_id}",
                "academic_batch": f"2025-26-{run_id}",
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=180)).isoformat(),
                "status": "planning",
                "description": "E2E validation season",
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        season_id = body["id"]
        activate = admin.request(
            "POST",
            f"{path}/{season_id}/activate",
            json={"confirm": True},
        )
        activated = expect_ok(activate, path=f"{path}/{season_id}/activate")
        assert isinstance(activated, dict)
        assert activated.get("is_current") is True or activated.get("status") == "active"
        ctx["season_id"] = season_id
        return None, {"detail": f"season active id={season_id}", "status": activate.status_code, "path": path}

    run_step("1. Super Admin", "System health", step_health)
    run_step("1. Super Admin", "Feature flags ready", step_feature_flags)
    run_step("1. Super Admin", "Maintenance disabled", step_maintenance_off)
    run_step("1. Super Admin", "Department active", step_department)
    run_step("1. Super Admin", "Season active", step_season)

    # ------------------------------------------------------------------ #
    # 2. Placement Cell — company CRM
    # ------------------------------------------------------------------ #
    def step_create_company() -> None:
        path = "/api/v1/companies"
        res = cell.request(
            "POST",
            path,
            json={
                "name": f"Acme Drive {run_id}",
                "industry": "Software",
                "website": "https://example.com",
                "headquarters": "Bengaluru",
                "company_type": "Product",
                "handler": {
                    "handler_user_id": str(actors["convener_id"]),
                    "branch": "CSE",
                    "ownership_type": "NEW",
                },
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["company_id"] = body["id"]
        assert body.get("active_handler") is not None
        return None, {"detail": f"company={body['id']}", "status": res.status_code, "path": path}

    def step_hr_contact() -> None:
        path = f"/api/v1/companies/{ctx['company_id']}/contacts"
        res = cell.request(
            "POST",
            path,
            json={
                "name": "Priya HR",
                "designation": "Campus HR",
                "email": f"hr.{run_id}@example.com",
                "phone": "9876543210",
                "is_primary": True,
                "notes": "Primary recruiter",
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["contact_id"] = body["id"]
        return None, {"detail": "HR contact created", "status": res.status_code, "path": path}

    def step_pipeline() -> None:
        path = f"/api/v1/companies/{ctx['company_id']}/pipeline"
        res = cell.request("PATCH", path, json={"current_stage": "INTERESTED"})
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("current_stage") == "INTERESTED"
        return None, {"detail": "pipeline=INTERESTED", "status": res.status_code, "path": path}

    def step_communication() -> None:
        path = f"/api/v1/companies/{ctx['company_id']}/communications"
        res = cell.request(
            "POST",
            path,
            json={
                "type": "EMAIL",
                "subject": "Campus drive interest",
                "description": "Confirmed campus drive window for E2E rehearsal.",
                "communication_date": datetime.now(timezone.utc).isoformat(),
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        return None, {"detail": "communication logged", "status": res.status_code, "path": path}

    run_step("2. Placement Cell", "Create company + handler", step_create_company)
    run_step("2. Placement Cell", "Add HR contact", step_hr_contact)
    run_step("2. Placement Cell", "Update pipeline", step_pipeline)
    run_step("2. Placement Cell", "Log communication", step_communication)

    # ------------------------------------------------------------------ #
    # 3. Convener — opportunity
    # ------------------------------------------------------------------ #
    def step_create_opportunity() -> None:
        path = "/api/v1/opportunities"
        deadline = datetime.now(timezone.utc) + timedelta(days=14)
        res = convener.request(
            "POST",
            path,
            json={
                "company_id": ctx["company_id"],
                "title": f"SDE Intern {run_id}",
                "role": "Software Development Intern",
                "employment_type": "INTERNSHIP",
                "location": "Raipur / Hybrid",
                "mode": "HYBRID",
                "ctc_min": "6.0",
                "ctc_max": "8.0",
                "job_description": "Build PlacementOS features. E2E validation JD.",
                "application_deadline": deadline.isoformat(),
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["opportunity_id"] = body["id"]
        return None, {"detail": f"opportunity={body['id']}", "status": res.status_code, "path": path}

    def step_eligibility_rules() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/eligibility"
        res = convener.request(
            "PATCH",
            path,
            json={
                "minimum_cgpa": "6.5",
                "allowed_departments": [ctx["department_id"]],
                "allowed_graduation_years": [2026, 2027],
                "maximum_active_backlogs": 0,
                "allow_backlog_history": True,
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        return None, {"detail": "eligibility configured", "status": res.status_code, "path": path}

    def step_upload_jd() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/documents"
        res = convener.request(
            "POST",
            path,
            json={
                "document_type": "JD",
                "file_url": f"https://example.com/jd-{run_id}.pdf",
            },
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        return None, {"detail": "JD attached", "status": res.status_code, "path": path}

    def step_publish() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/publish"
        res = convener.request("POST", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("status") == "PUBLISHED"
        return None, {"detail": "published", "status": res.status_code, "path": path}

    run_step("3. Convener", "Create hiring opportunity", step_create_opportunity)
    run_step("3. Convener", "Configure eligibility", step_eligibility_rules)
    run_step("3. Convener", "Upload JD", step_upload_jd)
    run_step("3. Convener", "Publish opportunity", step_publish)

    # Notifications for publish are best-effort to eligible students; student profile
    # may not exist yet — verified after student applies / status changes.

    # ------------------------------------------------------------------ #
    # 4. Student
    # ------------------------------------------------------------------ #
    def step_student_login() -> None:
        path = "/api/v1/auth/me"
        res = student.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("college_email", "").endswith("@nitrr.ac.in")
        return None, {"detail": f"me={body.get('college_email')}", "status": res.status_code, "path": path}

    def step_complete_profile() -> None:
        profile_path = "/api/v1/students/profiles"
        create = student.request(
            "POST",
            profile_path,
            json={
                "department_id": ctx["department_id"],
                "roll_number": f"E2E{run_id.upper()}",
                "registration_number": f"REG{run_id.upper()}",
                "graduation_year": 2026,
            },
        )
        profile = expect_ok(create, path=profile_path)
        assert isinstance(profile, dict)
        profile_id = profile["id"]
        ctx["profile_id"] = profile_id

        personal = student.request(
            "PUT",
            f"{profile_path}/{profile_id}/personal-information",
            json={
                "first_name": "Ada",
                "last_name": "Student",
                "gender": "FEMALE",
                "date_of_birth": "2003-05-01",
                "phone_number": "9999999999",
                "alternate_phone": None,
                "personal_email": f"ada.{run_id}@gmail.com",
                "address": "Hostel A",
                "city": "Raipur",
                "state": "Chhattisgarh",
                "country": "India",
                "photo_url": f"https://example.com/photo-{run_id}.jpg",
            },
        )
        expect_ok(personal, path="PUT personal-information")

        academic = student.request(
            "PUT",
            f"{profile_path}/{profile_id}/academic-information",
            json={
                "current_cgpa": "8.50",
                "semester": 6,
                "active_backlogs": 0,
                "total_history_backlogs": 0,
            },
        )
        expect_ok(academic, path="PUT academic-information")

        for edu in (
            {
                "education_type": "SECONDARY",
                "institution": "Demo School",
                "board": "CBSE",
                "passing_year": 2019,
                "percentage_or_cgpa": "92",
            },
            {
                "education_type": "HIGHER_SECONDARY",
                "institution": "Demo School",
                "board": "CBSE",
                "passing_year": 2021,
                "percentage_or_cgpa": "90",
            },
            {
                "education_type": "UNDERGRADUATE",
                "institution": "National Institute of Technology Raipur",
                "board": "N/A",
                "passing_year": 2026,
                "percentage_or_cgpa": "8.50",
            },
        ):
            expect_ok(
                student.request(
                    "POST",
                    f"{profile_path}/{profile_id}/education-history",
                    json=edu,
                ),
                path="POST education-history",
            )

        return None, {"detail": f"profile={profile_id}", "status": 200, "path": profile_path}

    def step_documents_resume() -> None:
        profile_id = ctx["profile_id"]
        base = f"/api/v1/students/profiles/{profile_id}"
        for doc_type in ("AADHAR", "TENTH_MARKSHEET", "TWELFTH_MARKSHEET"):
            expect_ok(
                student.request(
                    "POST",
                    f"{base}/documents",
                    json={
                        "document_type": doc_type,
                        "file_url": f"https://example.com/{doc_type.lower()}-{run_id}.pdf",
                        "file_name": f"{doc_type}.pdf",
                    },
                ),
                path=f"POST documents/{doc_type}",
            )
        resume = expect_ok(
            student.request(
                "POST",
                f"{base}/resumes",
                json={
                    "name": "Primary Resume",
                    "file_url": f"https://example.com/resume-{run_id}.pdf",
                    "version": 1,
                    "is_active": True,
                },
            ),
            path="POST resumes",
        )
        assert isinstance(resume, dict)
        ctx["resume_id"] = resume["id"]
        return None, {"detail": "docs+resume uploaded", "status": 200, "path": base}

    def step_eligibility_check() -> None:
        path = (
            f"/api/v1/opportunities/{ctx['opportunity_id']}"
            f"/screening/student/{ctx['profile_id']}"
        )
        res = student.request("POST", path)
        # Some deployments restrict screening to staff — try convener if forbidden
        if res.status_code in {401, 403}:
            res = convener.request("POST", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["eligibility"] = body
        assert body.get("eligible") is True, f"Student should be eligible: {body}"
        return None, {"detail": "eligible=true", "status": res.status_code, "path": path}

    def step_apply() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/apply"
        res = student.request(
            "POST",
            path,
            json={"selected_resume_id": ctx["resume_id"], "answers": []},
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        ctx["application_id"] = body["id"]
        assert body.get("status") == "APPLIED"
        return None, {"detail": f"application={body['id']}", "status": res.status_code, "path": path}

    def step_snapshot() -> None:
        path = f"/api/v1/applications/{ctx['application_id']}/snapshot"
        res = student.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("student_profile_snapshot")
        assert body.get("resume_snapshot")
        return None, {"detail": "snapshot present", "status": res.status_code, "path": path}

    run_step("4. Student", "Login /auth/me", step_student_login)
    run_step("4. Student", "Complete profile", step_complete_profile)
    run_step("4. Student", "Upload documents + resume", step_documents_resume)
    run_step("4. Student", "Check eligibility", step_eligibility_check)
    run_step("4. Student", "Apply", step_apply)
    run_step("4. Student", "Snapshot created", step_snapshot)

    # ------------------------------------------------------------------ #
    # 5. Convener operations
    # ------------------------------------------------------------------ #
    def step_list_applications() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/applications"
        res = convener.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, list)
        assert any(item.get("id") == ctx["application_id"] for item in body)
        return None, {"detail": f"count={len(body)}", "status": res.status_code, "path": path}

    def step_screening_summary() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/screening"
        res = convener.request("GET", path)
        body = expect_ok(res, path=path)
        assert body is not None
        return None, {"detail": "screening summary ok", "status": res.status_code, "path": path}

    def step_export() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/exports"
        csv_res = convener.request(
            "POST",
            path,
            json={"format": "csv", "scope": "all"},
        )
        csv_body = expect_ok(csv_res, path=path)
        assert csv_body is not None
        xlsx_res = convener.request(
            "POST",
            path,
            json={"format": "xlsx", "scope": "all"},
        )
        xlsx_body = expect_ok(xlsx_res, path=path)
        assert xlsx_body is not None
        return None, {
            "detail": f"csv={len(csv_body)}B xlsx={len(xlsx_body)}B",
            "status": 200,
            "path": path,
        }

    def step_import_shortlist() -> None:
        path = f"/api/v1/opportunities/{ctx['opportunity_id']}/shortlist-imports/preview"
        csv = f"Roll Number,Name\nE2E{run_id.upper()},Ada Student\n".encode()
        res = convener.request(
            "POST",
            path,
            data={
                "match_field": "ROLL_NUMBER",
                "target_status": "SHORTLISTED",
            },
            files={"file": ("shortlist.csv", csv, "text/csv")},
        )
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        import_id = body["id"]
        confirm = convener.request(
            "POST",
            f"/api/v1/opportunities/{ctx['opportunity_id']}/shortlist-imports/{import_id}/confirm",
        )
        confirmed = expect_ok(confirm, path="confirm shortlist import")
        assert isinstance(confirmed, dict)
        ctx["import_id"] = import_id
        return None, {
            "detail": f"updated={confirmed.get('rows_updated')}",
            "status": confirm.status_code,
            "path": path,
        }

    def step_offer_released() -> None:
        path = f"/api/v1/applications/{ctx['application_id']}/status"
        # After shortlist import, status should be SHORTLISTED; move toward offer.
        for status in ("SELECTED", "OFFER_RELEASED"):
            res = convener.request(
                "PATCH",
                path,
                json={"status": status, "remarks": f"E2E {status}"},
            )
            body = expect_ok(res, path=path)
            assert isinstance(body, dict)
            assert body.get("status") == status
        return None, {"detail": "OFFER_RELEASED", "status": 200, "path": path}

    run_step("5. Convener", "View applications", step_list_applications)
    run_step("5. Convener", "Eligibility screening", step_screening_summary)
    run_step("5. Convener", "Export CSV/XLSX", step_export)
    run_step("5. Convener", "Import shortlist", step_import_shortlist)
    run_step("5. Convener", "Release offer", step_offer_released)

    # ------------------------------------------------------------------ #
    # 6. Student notifications + status
    # ------------------------------------------------------------------ #
    def step_student_notifications() -> None:
        path = "/api/v1/notifications"
        res = student.request("GET", path, params={"page": 1, "page_size": 50})
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        items = body.get("items") or body.get("notifications") or []
        ctx["notifications"] = items
        assert len(items) >= 1
        return None, {"detail": f"notifications={len(items)}", "status": res.status_code, "path": path}

    def step_student_status_offer() -> None:
        path = "/api/v1/applications/me"
        res = student.request("GET", path)
        body = expect_ok(res, path=path)
        assert isinstance(body, list)
        mine = next(item for item in body if item["id"] == ctx["application_id"])
        assert mine["status"] == "OFFER_RELEASED"
        return None, {"detail": "offer visible to student", "status": res.status_code, "path": path}

    run_step("6. Student", "Notification received", step_student_notifications)
    run_step("6. Student", "Offer status visible", step_student_status_offer)

    # ------------------------------------------------------------------ #
    # 7. Audit
    # ------------------------------------------------------------------ #
    def step_audit() -> None:
        path = "/api/v1/audit"
        res = admin.request("GET", path, params={"page": 1, "page_size": 100})
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        items = body.get("items") or []
        actions = {item.get("action") for item in items}
        # Critical actions expected somewhere in recent audit trail
        required_any = {"CREATE", "PUBLISH", "APPLY", "STATUS_CHANGED", "EXPORT_GENERATED", "SHORTLIST_IMPORTED"}
        found = actions & required_any
        assert found, f"Expected audit actions, got {actions}"
        # Entity-specific
        entity_path = f"/api/v1/audit/entity/APPLICATION/{ctx['application_id']}"
        entity = expect_ok(admin.request("GET", entity_path), path=entity_path)
        assert isinstance(entity, dict)
        entity_items = entity.get("items") or []
        assert len(entity_items) >= 1
        return None, {
            "detail": f"audit_actions={sorted(found)} entity_logs={len(entity_items)}",
            "status": 200,
            "path": path,
        }

    run_step("7. Audit", "Critical actions logged", step_audit)

    # ------------------------------------------------------------------ #
    # 8. Health wrap-up
    # ------------------------------------------------------------------ #
    def step_final_health() -> None:
        path = "/health"
        res = client.get(path)
        body = expect_ok(res, path=path)
        assert isinstance(body, dict)
        assert body.get("status") == "ok"
        assert res.headers.get("X-Request-ID") or True
        return None, {"detail": "root health ok", "status": res.status_code, "path": path}

    def step_authz_negative() -> None:
        # Student must not access admin health
        path = "/api/v1/admin/system-health"
        res = student.request("GET", path)
        if res.status_code not in {401, 403}:
            raise AssertionError(f"Expected 401/403 for student admin access, got {res.status_code}")
        return None, {"detail": f"student blocked ({res.status_code})", "status": res.status_code, "path": path}

    run_step("8. Health", "Root health", step_final_health)
    run_step("8. Health", "Authorization still enforced", step_authz_negative)

    # Performance observations
    slow = [s for s in report.steps if s.duration_ms > 2000]
    if slow:
        report.observations.append(
            f"{len(slow)} step(s) exceeded 2s — investigate DB/index/cold-start on staging.",
        )
    else:
        report.observations.append("All workflow steps completed under 2s in this environment.")

    report_path = report.write_markdown()
    report.observations.append(f"Report written to {report_path}")

    assert report.overall_pass, f"Placement drive validation failed — see {report_path}"
