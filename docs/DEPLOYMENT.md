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

| Variable                | Value / notes                                                            |
| ----------------------- | ------------------------------------------------------------------------ |
| `DATABASE_URL`          | Neon connection string                                                   |
| `JWT_SECRET_KEY`        | Long random secret (never use the code default)                          |
| `COOKIE_SECURE`         | `true`                                                                   |
| `ENABLE_DEV_LOGIN`      | `false` for real prod; `true` only for demos                             |
| `FRONTEND_URL`          | Your Vercel URL, e.g. `https://placementops.vercel.app`                  |
| `CORS_ORIGINS`          | Same as `FRONTEND_URL`                                                   |
| `GOOGLE_CLIENT_ID`      | Google OAuth client ID (if using Google login)                           |
| `GOOGLE_CLIENT_SECRET`  | Google OAuth secret                                                      |
| `GOOGLE_REDIRECT_URI`   | `https://<your-render-service>.onrender.com/api/v1/auth/google/callback` |
| `CLOUDINARY_CLOUD_NAME` | Optional until uploads are enabled                                       |
| `CLOUDINARY_API_KEY`    | Optional                                                                 |
| `CLOUDINARY_API_SECRET` | Optional                                                                 |

After deploy, open: `https://<service>.onrender.com/health` → should return `{"status":"ok"}`.

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

1. Create a free Cloudinary account.
2. Add `CLOUDINARY_*` on Render when you enable uploads.

---

## 5. Google OAuth (optional)

In Google Cloud Console → Credentials:

- Authorized redirect URI:  
  `https://<render-api>.onrender.com/api/v1/auth/google/callback`
- Authorized JavaScript origins:  
  `https://<your-app>.vercel.app`

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
