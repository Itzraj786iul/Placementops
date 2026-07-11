# Staging Deployment Report — EPIC-019

**Project:** PlacementOS (Placementops)  
**Epic:** EPIC-019 — Staging Deployment & Production Validation  
**Date:** 2026-07-11  
**Scope:** Deployment configuration, environment hardening, cloud integrations, security, and validation playbooks. **No new business features.**

---

## 1. Deployment architecture

```text
┌─────────────────────┐         HTTPS          ┌──────────────────────────┐
│  Vercel (Next.js 15)│ ─────────────────────► │ Render (FastAPI / Uvicorn)│
│  apps/web           │   NEXT_PUBLIC_API_URL  │ apps/api                  │
│  + BFF /api/v1/*    │   INTERNAL_API_URL     │ /health  /ready           │
└─────────────────────┘                        └────────────┬─────────────┘
         │                                                  │
         │ Google OAuth (browser)                           │ pooled SQL
         ▼                                                  ▼
┌─────────────────────┐                        ┌──────────────────────────┐
│ Google Cloud OAuth  │ ◄── callback ───────── │ Neon PostgreSQL          │
└─────────────────────┘                        └──────────────────────────┘
                                                         │
              ┌──────────────────┬───────────────────────┘
              ▼                  ▼
     ┌────────────────┐  ┌────────────────┐
     │ Cloudinary     │  │ Resend email   │
     │ (uploads)      │  │ (notifications)│
     └────────────────┘  └────────────────┘
```

| Layer    | Platform   | Config entry points                              |
| -------- | ---------- | ------------------------------------------------ |
| Frontend | Vercel     | `apps/web/vercel.json`, env dashboard            |
| Backend  | Render     | `render.yaml`, start: alembic + uvicorn          |
| Database | Neon       | `DATABASE_URL` (prefer pooled connection)        |
| Auth     | Google     | OAuth web client + `GOOGLE_*` on Render          |
| Storage  | Cloudinary | `CLOUDINARY_*`                                   |
| Email    | Resend     | `RESEND_API_KEY`, `EMAIL_FROM`, `EMAIL_PROVIDER` |

Obsolete: **Railway** (`apps/api/railway.toml` removed). Hosting is Vercel + Render + Neon only.

---

## 2. Files modified (this epic)

| File                                                             | Change                                                        |
| ---------------------------------------------------------------- | ------------------------------------------------------------- |
| `apps/api/railway.toml`                                          | **Removed** (obsolete)                                        |
| `apps/web/vercel.json`                                           | **Added** monorepo install/build commands                     |
| `render.yaml`                                                    | Staging defaults (`ENVIRONMENT=staging`), email vars retained |
| `apps/api/app/core/config.py`                                    | Staging+production fail-fast; OAuth/CORS/DB/HTTPS gates       |
| `apps/api/app/core/startup.py`                                   | Cloudinary/Resend startup warnings                            |
| `apps/api/app/api/health.py`                                     | `/api/v1/ready` readiness probe                               |
| `apps/api/main.py`                                               | Root `/ready` probe                                           |
| `apps/api/app/middlewares/maintenance.py`                        | Allow `/ready` during maintenance                             |
| `apps/api/app/database/session.py`                               | Neon-friendly pool (`pool_recycle=280`, smaller pool)         |
| `apps/api/tests/test_security_hardening.py`                      | Staging/deployed config tests                                 |
| `scripts/staging_smoke.py`                                       | **Added** remote smoke checker                                |
| `docs/DEPLOYMENT.md`                                             | Staging/readiness/smoke updates                               |
| `docs/STAGING_DEPLOYMENT_REPORT.md`                              | **This report**                                               |
| `.env.example`, `apps/api/.env.example`, `apps/web/.env.example` | Deploy var documentation                                      |

---

## 3. Environment variables required

### Backend (Render)

| Variable                | Required for boot (staging/prod) | Notes                                  |
| ----------------------- | -------------------------------- | -------------------------------------- |
| `DATABASE_URL`          | **Yes**                          | Neon URL; localhost rejected           |
| `JWT_SECRET_KEY`        | **Yes**                          | ≥32 chars; not code default            |
| `ENVIRONMENT`           | **Yes**                          | `staging` or `production`              |
| `COOKIE_SECURE`         | **Yes**                          | Must be `true`                         |
| `ENABLE_DEV_LOGIN`      | **Yes**                          | Must be `false`                        |
| `ENABLE_API_DOCS`       | Recommended `false`              | Auto-disabled when deployed if unset   |
| `FRONTEND_URL`          | **Yes**                          | Must be `https://…`                    |
| `CORS_ORIGINS`          | **Yes**                          | Must include `FRONTEND_URL`            |
| `GOOGLE_CLIENT_ID`      | **Yes**                          | Real client (not placeholder)          |
| `GOOGLE_CLIENT_SECRET`  | **Yes**                          | ≥16 chars                              |
| `GOOGLE_REDIRECT_URI`   | **Yes**                          | Public Render callback (not localhost) |
| `CLOUDINARY_CLOUD_NAME` | Strongly recommended             | Uploads 503 if missing                 |
| `CLOUDINARY_API_KEY`    | Strongly recommended             |                                        |
| `CLOUDINARY_API_SECRET` | Strongly recommended             |                                        |
| `RESEND_API_KEY`        | Recommended                      | Email SKIPPED if missing               |
| `EMAIL_FROM`            | Recommended                      |                                        |
| `EMAIL_PROVIDER`        | Recommended                      | Default `resend`                       |

### Frontend (Vercel)

| Variable                       | Required              | Notes                                      |
| ------------------------------ | --------------------- | ------------------------------------------ |
| `NEXT_PUBLIC_API_URL`          | **Yes**               | Render origin (no trailing path)           |
| `INTERNAL_API_URL`             | **Yes**               | Same as API URL for BFF / auth exchange    |
| `NEXT_PUBLIC_ENABLE_DEV_LOGIN` | Must be unset/`false` |                                            |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Not required          | OAuth starts on API (`/auth/google/login`) |

---

## 4. Deployment URLs (fill after provision)

| Service         | URL                                         | Status                     |
| --------------- | ------------------------------------------- | -------------------------- |
| Web (Vercel)    | `https://________.vercel.app`               | Pending operator deploy    |
| API (Render)    | `https://________.onrender.com`             | Pending operator deploy    |
| API health      | `…/health`                                  | Validate with smoke script |
| API ready       | `…/ready`                                   | Validate with smoke script |
| Neon            | Project dashboard                           | Pending                    |
| Google redirect | `https://<api>/api/v1/auth/google/callback` | Must match Console         |

> This repository cannot create cloud resources or set dashboard secrets. Operators must create Neon / Render / Vercel / Google / Cloudinary / Resend projects, then paste URLs above.

---

## 5. Configuration verification (code-level)

| Check                                            | Result                     |
| ------------------------------------------------ | -------------------------- |
| `render.yaml` present & Python 3.12 pinned       | Pass                       |
| `apps/web/vercel.json` monorepo build            | Pass                       |
| Railway leftovers removed                        | Pass                       |
| Startup diagnostics (`startup.diagnostics` JSON) | Pass                       |
| Liveness `/health`                               | Pass                       |
| Readiness `/ready` (DB)                          | Pass                       |
| Alembic on start (`alembic upgrade head`)        | Pass (Render startCommand) |
| Docs disabled when deployed                      | Pass (`is_deployed`)       |
| Dev login blocked when deployed                  | Pass (fail-fast)           |
| Secure cookies required when deployed            | Pass                       |
| Structured logs + `X-Request-ID`                 | Pass (prior EPIC-018)      |

---

## 6. Integration verification playbooks

### 6.1 Google OAuth (Phase 3)

Manual checklist after staging is live:

- [ ] Student (`@nitrr.ac.in`) login → lands in student workspace
- [ ] Placement Convener login (role assigned by admin)
- [ ] Placement Cell login
- [ ] Super Admin login
- [ ] Cookies: `access_token` / `refresh_token` HttpOnly + Secure + SameSite=Lax
- [ ] Refresh continues session after access expiry
- [ ] Logout clears cookies
- [ ] Non-`nitrr.ac.in` Google account rejected
- [ ] Redirect URI exact match (no http / no trailing slash mismatch)

### 6.2 Cloudinary (Phase 4)

- [ ] Resume upload returns `https://res.cloudinary.com/…` URL
- [ ] Document upload + replace + delete
- [ ] Profile photo upload
- [ ] Oversized file rejected (10 MB docs / 5 MB images)
- [ ] Unsupported MIME rejected (magic-byte validation)
- [ ] With Cloudinary unset: multipart endpoints return **503** (startup warning logged)

### 6.3 Email / Resend (Phase 5)

- [ ] Application submitted notification (in-app + email when configured)
- [ ] Application status changed email
- [ ] Offer released email
- [ ] Profile submitted staff email (`PROFILE_SUBMITTED`)
- [ ] Without `RESEND_API_KEY`: in-app notification created, `delivery_status=SKIPPED`
- [ ] Resend HTTP failure: notification retained, `delivery_status=FAILED` (no request crash)

### 6.4 Database (Phase 6)

- [ ] Neon connection via pooled `DATABASE_URL`
- [ ] `alembic current` == `015_profile_submit_notifications`
- [ ] `/ready` returns `database: ok`
- [ ] Admin system-health (super admin) shows DB + migration version
- [ ] Pool: `pool_pre_ping=True`, `pool_recycle=280`

### 6.5 Security (Phase 7)

- [ ] HTTPS only for cookies (`COOKIE_SECURE=true`)
- [ ] CORS limited to Vercel origin(s)
- [ ] `/docs`, `/redoc`, `/openapi.json` → 404
- [ ] Dev login UI/API disabled
- [ ] JWT rejects missing claims / invalid `sub` / refresh without `jti`
- [ ] Responses include `X-Request-ID`; access logs structured JSON

---

## 7. Performance observations (Phase 8)

| Metric                    | Expected on free tier                     | How to measure              |
| ------------------------- | ----------------------------------------- | --------------------------- |
| Cold start (Render sleep) | 30–60s first `/health`                    | `scripts/staging_smoke.py`  |
| Warm `/health`            | Typically &lt; 200 ms                     | Smoke script after warm     |
| Warm `/ready`             | Neon wake may add 1–5s if suspended       | Smoke script                |
| OAuth round-trip          | Dominated by Google + cold API            | Browser DevTools            |
| Upload latency            | Network + Cloudinary; often 1–5s          | Student resume step         |
| Notification email        | Async best-effort; Resend usually &lt; 2s | Resend dashboard            |
| Largest queries           | Admin list / export endpoints             | Render logs + Neon insights |

**Recommendation:** For a live placement week, move Render off free (no sleep) and keep Neon compute from suspending.

Local E2E rehearsal (prior epic) recorded workflow pass **29/29** — see `docs/VALIDATION_REPORT.md`. Those timings are local, not staging.

---

## 8. Production workflow validation (Phase 9)

Against **deployed** staging (after secrets are set):

```bash
# 1) Infrastructure smoke
python scripts/staging_smoke.py https://<render-api>.onrender.com

# 2) Full placement drive workflow (needs DATABASE_URL + staging actors)
cd apps/api
python -m pytest tests/e2e -v
```

Workflow coverage (existing harness): company → opportunity publish → student onboarding → resume → application → eligibility → export → shortlist import → offer → notifications → audit → health.

Mark results here after the first staging run:

| Area                                   | Pass? | Notes |
| -------------------------------------- | ----- | ----- |
| Smoke `/health` `/ready` docs lockdown | ☐     |       |
| OAuth all roles                        | ☐     |       |
| Cloudinary uploads                     | ☐     |       |
| Resend emails                          | ☐     |       |
| E2E 29-step suite                      | ☐     |       |
| Profile submit endpoint                | ☐     |       |

---

## 9. Known issues

| Issue                                         | Severity          | Mitigation                                                  |
| --------------------------------------------- | ----------------- | ----------------------------------------------------------- |
| Render free-tier sleep                        | High for live day | Upgrade plan or keep-alive; warn users of cold start        |
| Neon compute suspend                          | Medium            | Use pooled URL; expect `/ready` delay after idle            |
| Cloudinary/Resend optional at boot            | Low               | Startup warnings; uploads 503 / email SKIPPED               |
| Cross-site cookies rely on SameSite=Lax + BFF | Medium            | Keep web and API on HTTPS; set `INTERNAL_API_URL` correctly |
| Staging URLs not provisioned in-repo          | N/A               | Operator action required                                    |

### Resolved in this epic

- Railway leftover config removed
- Missing Vercel monorepo build file added
- Staging treated with production-grade security fail-fast
- Readiness probe added for DB
- Pool recycle tuned for Neon
- Smoke validation script added

---

## 10. Go-live checklist

- [ ] Staging smoke green for ≥24h
- [ ] Flip Render `ENVIRONMENT=production` (same gates)
- [ ] Confirm Google Console production redirect URIs
- [ ] Confirm Resend production sender domain (not only `resend.dev` if required)
- [ ] Confirm Cloudinary folder quotas
- [ ] Neon backup / branch strategy understood
- [ ] Rollback owners identified (Vercel / Render / Neon)
- [ ] Placement Cell runbook: cold-start expectation communicated

### Rollback procedure

1. **Frontend:** Vercel → Deployments → Promote previous successful deployment.
2. **API:** Render → Events → Redeploy previous successful deploy (or pin prior commit).
3. **DB:** Prefer forward-fix migrations. If destructive migration shipped, restore Neon branch / PITR backup to pre-release timestamp, then redeploy matching API commit.
4. Re-run `python scripts/staging_smoke.py <api-url>` after rollback.

---

## 11. Final Go / No-Go recommendation

| Gate                                       | Status                                              |
| ------------------------------------------ | --------------------------------------------------- |
| Code & config ready for staging deploy     | **GO**                                              |
| Local E2E workflow (prior)                 | **GO** (29/29)                                      |
| Cloud resources provisioned & smoke-tested | **NO-GO until operators complete §4–§8 checklists** |
| Live placement week on free tier           | **NO-GO** without Render/Neon always-on upgrades    |

**Verdict:** PlacementOS is **ready to deploy to staging** from this repository. Treat the first cloud deploy as a controlled RC: provision Neon → Render → Vercel → OAuth/Cloudinary/Resend, run `staging_smoke.py`, then the E2E suite against staging. **Do not declare production go-live** until the Phase 3–9 checklists above are signed off on real staging URLs.
