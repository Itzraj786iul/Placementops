# Deployment Guide (Free Tier)

PlacementOS deploys on **free** managed services. No Railway required.

## Architecture

| Component    | Platform                             | Free tier notes                                  |
| ------------ | ------------------------------------ | ------------------------------------------------ |
| Frontend     | [Vercel](https://vercel.com)         | Hobby plan — free for personal projects          |
| Backend      | [Render](https://render.com)         | Free web service (spins down after ~15 min idle) |
| Database     | [Neon](https://neon.tech)            | Free Postgres (compute suspends when idle)       |
| File storage | [Cloudinary](https://cloudinary.com) | Free plan for resumes / documents                |

**Cold starts:** Render free dynos sleep when idle. The first API request after sleep can take 30–60s. Neon may also wake slowly. Fine for demos; not ideal for a live placement day without upgrading.

**Python version:** The API is pinned to **Python 3.12** (`render.yaml` + `apps/api/.python-version`). Do not use 3.14 on Render — packages like `pydantic-core` / `psycopg2` will compile from source and the build can hang or fail.

**Alternatives (also free-ish):** [Koyeb](https://www.koyeb.com), [Fly.io](https://fly.io) (limited free allowance), [Google Cloud Run](https://cloud.google.com/run) (always-free quota).

---

## 1. Database — Neon (free)

1. Sign up at [neon.tech](https://neon.tech) → create a project.
2. Copy the connection string (prefer the **pooled** URL if Neon shows one).
3. You will set this as `DATABASE_URL` on Render.

Run migrations once the API env is ready (from your machine or Render shell):

```bash
cd apps/api
# set DATABASE_URL to the Neon URL
alembic upgrade head
```

Or let the Render start command run migrations (see below).

---

## 2. Backend — Render (free)

### Option A — Blueprint (recommended)

1. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect [Itzraj786iul/Placementops](https://github.com/Itzraj786iul/Placementops).
3. Render reads `render.yaml` at the repo root.
4. Fill in the env vars listed in the Blueprint (especially `DATABASE_URL`, `JWT_SECRET_KEY`).

### Option B — Manual Web Service

1. **New** → **Web Service** → connect the GitHub repo.
2. Settings:
   - **Root Directory:** `apps/api`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free
3. Health check path: `/health`

### Environment variables (Render)

| Variable                | Value / notes                                                                  |
| ----------------------- | ------------------------------------------------------------------------------ |
| `DATABASE_URL`          | Neon connection string                                                         |
| `ENVIRONMENT`           | `production` (required for RC hardening — disables docs, enforces flags)       |
| `JWT_SECRET_KEY`        | Long random secret (never use the code default; ≥32 chars)                     |
| `COOKIE_SECURE`         | `true` (required when `ENVIRONMENT=production`)                                |
| `ENABLE_DEV_LOGIN`      | `false` (required when `ENVIRONMENT=production`; API will not start otherwise) |
| `ENABLE_API_DOCS`       | `false` in production (Swagger/ReDoc/OpenAPI disabled)                         |
| `FRONTEND_URL`          | Your Vercel URL, e.g. `https://placementops.vercel.app`                        |
| `CORS_ORIGINS`          | Same as `FRONTEND_URL`                                                         |
| `GOOGLE_CLIENT_ID`      | Google OAuth client ID (if using Google login)                                 |
| `GOOGLE_CLIENT_SECRET`  | Google OAuth secret                                                            |
| `GOOGLE_REDIRECT_URI`   | `https://<your-render-service>.onrender.com/api/v1/auth/google/callback`       |
| `CLOUDINARY_CLOUD_NAME` | Required for file uploads (resumes, documents, images)                         |
| `CLOUDINARY_API_KEY`    | From Cloudinary dashboard → API Keys                                           |
| `CLOUDINARY_API_SECRET` | Keep secret; never commit                                                      |

The API **refuses to start** in production if `ENABLE_DEV_LOGIN=true`, `COOKIE_SECURE=false`, or `JWT_SECRET_KEY` is missing/weak/default.

After deploy, open: `https://<service>.onrender.com/health` → should return `{"status":"ok"}`.  
Confirm `/docs` and `/redoc` return **404** in production.

---

## 3. Frontend — Vercel (free)

1. [vercel.com](https://vercel.com) → **Add New Project** → import `Placementops`.
2. Configure:
   - **Root Directory:** `apps/web`
   - **Framework Preset:** Next.js
   - **Build Command:** `npm run build` (from `apps/web`)  
     or from monorepo root: `cd ../.. && npm install && npm run build --workspace=@placementos/web`
3. Environment variables:

| Variable                       | Value                                           |
| ------------------------------ | ----------------------------------------------- |
| `NEXT_PUBLIC_API_URL`          | `https://<your-render-service>.onrender.com`    |
| `INTERNAL_API_URL`             | Same Render URL (used by the Next.js BFF proxy) |
| `NEXT_PUBLIC_ENABLE_DEV_LOGIN` | Leave **unset** / `false` in production         |

4. Deploy. Note your Vercel URL, then go back to Render and set `FRONTEND_URL` + `CORS_ORIGINS` to that URL. Redeploy the API if needed.

### Monorepo tip

If the Vercel build fails resolving `@placementos/types`, set Root Directory to the **repo root** and:

- Build Command: `npm install && npm run build --workspace=@placementos/web`
- Output: Next.js default for `apps/web` (or set “Root Directory” back to `apps/web` after installing from root — Vercel’s monorepo docs also support `apps/web` with install from root via project settings).

Simplest path that usually works:

- Root Directory: `apps/web`
- Install Command: `cd ../.. && npm install`
- Build Command: `cd ../.. && npm run build --workspace=@placementos/web`

---

## 4. File Storage — Cloudinary (free)

1. Create a free Cloudinary account at [cloudinary.com](https://cloudinary.com).
2. Copy **Cloud name**, **API Key**, and **API Secret** from the dashboard.
3. Set on Render (and locally in `apps/api/.env`):

```env
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

Uploads (resumes, student/company/opportunity documents) return a secure `file_url` stored in Postgres. Without these vars, multipart upload endpoints return **503**.

**Limits:** resumes/documents 10 MB; images (e.g. photo) 5 MB. Types: PDF, DOC, DOCX, PNG, JPG, JPEG.

---

## 4b. Email — Resend (free tier)

Notifications use a provider abstraction; the default provider is **Resend**.

1. Create an account at [resend.com](https://resend.com) and create an API key.
2. Set on Render / local `.env`:

```env
RESEND_API_KEY=re_...
EMAIL_FROM=PlacementOS <onboarding@resend.dev>
EMAIL_PROVIDER=resend
```

Without `RESEND_API_KEY`, in-app notifications still work; email delivery is skipped (`delivery_status=SKIPPED`).

---

## 5. Google OAuth (required for Sign in / Sign up with Google)

Students **sign up automatically** on first successful Google login (JIT). Only
`@nitrr.ac.in` emails are accepted. Staff roles are assigned by admins.

### Google Cloud Console

1. Create an OAuth 2.0 **Web application** client.
2. **Authorized redirect URI** (must match Render exactly):
   ```
   https://<your-render-api>.onrender.com/api/v1/auth/google/callback
   ```
3. **Authorized JavaScript origins**:
   ```
   https://<your-app>.vercel.app
   https://<your-render-api>.onrender.com
   ```

### Render env vars

| Variable               | Value                                                           |
| ---------------------- | --------------------------------------------------------------- |
| `GOOGLE_CLIENT_ID`     | From Google Cloud Console                                       |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console                                       |
| `GOOGLE_REDIRECT_URI`  | `https://<render-api>.onrender.com/api/v1/auth/google/callback` |
| `FRONTEND_URL`         | `https://<your-app>.vercel.app`                                 |
| `CORS_ORIGINS`         | Same as `FRONTEND_URL`                                          |
| `COOKIE_SECURE`        | `true`                                                          |

### Vercel env vars

| Variable              | Value                                    |
| --------------------- | ---------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `https://<your-render-api>.onrender.com` |
| `INTERNAL_API_URL`    | Same Render URL                          |

Redeploy Render and Vercel after saving. Then use **Sign up** or **Sign in with Google**
with an `@nitrr.ac.in` account (personal Gmail will be rejected).

---

## 6. Suggested order

1. Create **Neon** DB → copy `DATABASE_URL`
2. Deploy **Render** API with env vars → confirm `/health`
3. Deploy **Vercel** web with `NEXT_PUBLIC_API_URL` / `INTERNAL_API_URL`
4. Point Render `FRONTEND_URL` + `CORS_ORIGINS` at Vercel
5. (Optional) Google OAuth + Cloudinary

---

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) still runs lint, typecheck, build, and API tests on push/PR. Hosting deploys are triggered by Vercel/Render when they are connected to `main`.

---

## Rollback

- **Vercel:** Redeploy a previous deployment from the dashboard.
- **Render:** Redeploy a previous deploy from service history.
- **Neon:** Use branching / PITR if enabled on your plan.

---

## Cost reality check

| Service    | Free? | Main limit                        |
| ---------- | ----- | --------------------------------- |
| Vercel     | Yes   | Bandwidth / build minutes         |
| Render     | Yes   | Sleeps when idle; slow cold start |
| Neon       | Yes   | Storage + compute hours; suspends |
| Cloudinary | Yes   | Transformations / storage quota   |

For a college demo or small pilot this stack is enough. For a live placement week, upgrade Render (always-on) and Neon compute so the API does not sleep mid-session.

---

## Production security checklist (RC)

Before a live placement season:

- [ ] `ENVIRONMENT=production`
- [ ] `ENABLE_DEV_LOGIN=false` (API will not start otherwise)
- [ ] `COOKIE_SECURE=true`
- [ ] Strong `JWT_SECRET_KEY` (≥32 characters, not the example default)
- [ ] `ENABLE_API_DOCS=false` (or omit — docs auto-disable in production)
- [ ] Frontend: `NEXT_PUBLIC_ENABLE_DEV_LOGIN` unset or `false`
- [ ] Confirm `/docs` and `/openapi.json` return 404
- [ ] Google OAuth redirect URI matches the live API URL
- [ ] Cloudinary credentials set (uploads return 503 without them)
- [ ] Run placement drive E2E: `cd apps/api && python -m pytest tests/e2e -v` (writes `docs/VALIDATION_REPORT.md`)
