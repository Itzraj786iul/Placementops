# Deployment Guide

PlacementOS uses a split deployment model with managed cloud services. No container orchestration is required in the repository.

## Architecture

| Component    | Platform                             | Notes                      |
| ------------ | ------------------------------------ | -------------------------- |
| Frontend     | [Vercel](https://vercel.com)         | Next.js 15 App Router      |
| Backend      | [Railway](https://railway.app)       | FastAPI + Uvicorn          |
| Database     | [Neon](https://neon.tech)            | Serverless PostgreSQL      |
| File storage | [Cloudinary](https://cloudinary.com) | Resumes, documents, assets |

---

## Frontend — Vercel

### Setup

1. Import the GitHub repository into Vercel.
2. Set **Root Directory** to `apps/web` (or deploy from monorepo root with appropriate build settings).
3. Configure build command: `npm run build --workspace=@placementos/web` (from repo root) or `npm run build` (from `apps/web`).
4. Set output directory to `.next` (default for Next.js).

### Environment variables

| Variable              | Value                                                         |
| --------------------- | ------------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | Your Railway API URL (e.g. `https://your-api.up.railway.app`) |

### Notes

- The Next.js BFF proxy at `/api/v1/*` forwards requests to the backend using `NEXT_PUBLIC_API_URL` as fallback.
- Enable production domain and HTTPS (automatic on Vercel).
- Configure OAuth redirect URLs in Google Cloud Console for your Vercel domain if using direct frontend auth flows.

---

## Backend — Railway

### Setup

1. Create a new Railway project and connect the GitHub repository.
2. Set **Root Directory** to `apps/api`.
3. Railway detects Python via Nixpacks; `railway.toml` defines the start command.
4. Add environment variables (see below).

### Environment variables

| Variable                | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `DATABASE_URL`          | Neon PostgreSQL connection string                      |
| `JWT_SECRET_KEY`        | Long random secret for JWT signing                     |
| `GOOGLE_CLIENT_ID`      | Google OAuth client ID                                 |
| `GOOGLE_CLIENT_SECRET`  | Google OAuth client secret                             |
| `GOOGLE_REDIRECT_URI`   | `https://<railway-domain>/api/v1/auth/google/callback` |
| `FRONTEND_URL`          | Vercel production URL                                  |
| `CORS_ORIGINS`          | Vercel production URL (comma-separated if multiple)    |
| `COOKIE_SECURE`         | `true` in production                                   |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name                                  |
| `CLOUDINARY_API_KEY`    | Cloudinary API key                                     |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret                                  |

### Deploy steps

1. Push to `main` — Railway auto-deploys on connected branch.
2. Run migrations after first deploy:
   ```bash
   railway run alembic upgrade head
   ```
   Or use Railway shell / one-off command from the dashboard.

### Health check

Railway uses `/health` (defined in `railway.toml`).

---

## Database — Neon PostgreSQL

1. Create a Neon project and database.
2. Copy the connection string (use pooled connection for serverless if recommended).
3. Set `DATABASE_URL` on Railway to the Neon connection string.
4. Run Alembic migrations against Neon before or immediately after first API deploy:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

---

## File Storage — Cloudinary

1. Create a Cloudinary account and cloud.
2. Add `CLOUDINARY_*` variables to Railway (and local `apps/api/.env` when testing uploads).
3. File upload features will consume these credentials when the storage integration is enabled.

---

## Google OAuth (production)

Update authorized redirect URIs in Google Cloud Console:

- `https://<railway-api-domain>/api/v1/auth/google/callback`

Update authorized JavaScript origins if needed:

- `https://<vercel-domain>`

Set on Railway:

- `GOOGLE_REDIRECT_URI=https://<railway-api-domain>/api/v1/auth/google/callback`
- `FRONTEND_URL=https://<vercel-domain>`

---

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:

- Install dependencies
- Lint & typecheck
- Build frontend
- Verify API imports
- Run backend tests (native PostgreSQL on runner)
- Health check against local API

No container builds are performed in CI.

---

## Rollback

- **Vercel:** Redeploy a previous deployment from the Vercel dashboard.
- **Railway:** Roll back to a previous deployment in Railway service history.
- **Neon:** Use Neon branching / point-in-time recovery for database rollback if enabled.
