# PlacementOS — Placement Drive Validation Report

**Run ID:** `41eb3f0b`  
**Started:** 2026-07-11T10:46:24.023276+00:00  
**Finished:** 2026-07-11T10:46:29.375277+00:00  
**Result:** PASS  
**Steps:** 29 passed / 0 failed / 29 total  
**Wall time (sum of steps):** 5350.3 ms

## 1. Validation Report

| Phase             | Step                         | Result | Duration (ms) | Detail                                                                                                                 |
| ----------------- | ---------------------------- | ------ | ------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 1. Super Admin    | System health                | PASS   | 1537.4        | overall=warning                                                                                                        |
| 1. Super Admin    | Feature flags ready          | PASS   | 61.2          | flags=13                                                                                                               |
| 1. Super Admin    | Maintenance disabled         | PASS   | 83.3          | maintenance disabled                                                                                                   |
| 1. Super Admin    | Department active            | PASS   | 59.0          | department=CSE41EB                                                                                                     |
| 1. Super Admin    | Season active                | PASS   | 77.4          | season active id=c957df08-8032-4c61-a6fd-ae1f8cb8de16                                                                  |
| 2. Placement Cell | Create company + handler     | PASS   | 67.9          | company=2fb2b081-2b4a-41db-b022-d7940f85983a                                                                           |
| 2. Placement Cell | Add HR contact               | PASS   | 45.1          | HR contact created                                                                                                     |
| 2. Placement Cell | Update pipeline              | PASS   | 43.4          | pipeline=INTERESTED                                                                                                    |
| 2. Placement Cell | Log communication            | PASS   | 31.5          | communication logged                                                                                                   |
| 3. Convener       | Create hiring opportunity    | PASS   | 62.1          | opportunity=09984302-df8c-42d4-a674-5e4d59ccfd60                                                                       |
| 3. Convener       | Configure eligibility        | PASS   | 40.0          | eligibility configured                                                                                                 |
| 3. Convener       | Upload JD                    | PASS   | 27.9          | JD attached                                                                                                            |
| 3. Convener       | Publish opportunity          | PASS   | 60.9          | published                                                                                                              |
| 4. Student        | Login /auth/me               | PASS   | 8.4           | me=student.41eb3f0b@nitrr.ac.in                                                                                        |
| 4. Student        | Complete profile             | PASS   | 300.3         | profile=0ecad3c5-3e2c-4ab7-8db1-81e02ff013ad                                                                           |
| 4. Student        | Upload documents + resume    | PASS   | 248.9         | docs+resume uploaded                                                                                                   |
| 4. Student        | Check eligibility            | PASS   | 27.1          | eligible=true                                                                                                          |
| 4. Student        | Apply                        | PASS   | 704.8         | application=df1b2b67-42fb-4453-a489-eb40c02de87c                                                                       |
| 4. Student        | Snapshot created             | PASS   | 25.0          | snapshot present                                                                                                       |
| 5. Convener       | View applications            | PASS   | 18.2          | count=1                                                                                                                |
| 5. Convener       | Eligibility screening        | PASS   | 27.2          | screening summary ok                                                                                                   |
| 5. Convener       | Export CSV/XLSX              | PASS   | 78.8          | csv=289B xlsx=5098B                                                                                                    |
| 5. Convener       | Import shortlist             | PASS   | 560.9         | updated=1                                                                                                              |
| 5. Convener       | Release offer                | PASS   | 980.4         | OFFER_RELEASED                                                                                                         |
| 6. Student        | Notification received        | PASS   | 27.4          | notifications=4                                                                                                        |
| 6. Student        | Offer status visible         | PASS   | 25.1          | offer visible to student                                                                                               |
| 7. Audit          | Critical actions logged      | PASS   | 93.5          | audit_actions=['APPLY', 'CREATE', 'EXPORT_GENERATED', 'PUBLISH', 'SHORTLIST_IMPORTED', 'STATUS_CHANGED'] entity_logs=3 |
| 8. Health         | Root health                  | PASS   | 8.5           | root health ok                                                                                                         |
| 8. Health         | Authorization still enforced | PASS   | 18.5          | student blocked (403)                                                                                                  |

## 2. Pass / Fail

**Overall: PASS**

## 3. Performance observations

- All workflow steps completed under 2s in this environment.

Slowest steps:

- 1. Super Admin / System health: 1537.4 ms
- 5. Convener / Release offer: 980.4 ms
- 4. Student / Apply: 704.8 ms
- 5. Convener / Import shortlist: 560.9 ms
- 4. Student / Complete profile: 300.3 ms

## 4. Architecture observations

- Validation uses FastAPI TestClient against mounted `/api/v1` routers.
- Actors are seeded once via UserRepository/AuthService, then all business steps use HTTP APIs.
- File uploads use URL-based create endpoints (Cloudinary optional); upload-path security remains covered by unit tests.

## 5. Bugs discovered

- None in this run (PASS).

### Bugs found during Phase 3 rehearsal (fixed before PASS)

1. **Season activate `NameError`** — `SEASON_STATUS_ARCHIVED` was used in `AdminOrgService.activate_season` but not imported → 500 on activate.
2. **Maintenance audit IntegrityError** — new `system_settings` rows were audited before flush, so `entity_id` was NULL.
3. **Application snapshot staff-only** — students received 403 on `GET /applications/{id}/snapshot` for their own applications; now uses `ensure_application_read_access`.

## 6. Recommendations before v1.0

- Run this suite on staging with ENVIRONMENT=production flags before each placement season.
- Enable Cloudinary + Resend on staging and add a smoke check for multipart upload + email delivery.
- Keep ENABLE_DEV_LOGIN=false in production; E2E bootstrap uses AuthService.create_tokens only.
- Investigate admin system-health cold latency (~2s) before live placement week.
- Add a CI job (or keep in API tests) that requires Postgres so this rehearsal cannot silently skip.

---

### How to re-run

```bash
cd apps/api
# PostgreSQL must be reachable via DATABASE_URL
python -m pytest tests/e2e/test_placement_drive_workflow.py -v
# Report: docs/VALIDATION_REPORT.md
```
