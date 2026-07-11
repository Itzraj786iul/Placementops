# PlacementOS

Campus Recruitment Management System — production-grade monorepo for engineering colleges.

## Tech Stack

| Layer    | Technology                                     |
| -------- | ---------------------------------------------- |
| Monorepo | Turborepo                                      |
| Frontend | Next.js 15, TypeScript, TailwindCSS, shadcn/ui |
| Backend  | FastAPI, SQLAlchemy, Alembic                   |
| Database | PostgreSQL (local dev / Neon in production)    |
| Tooling  | ESLint, Prettier, Husky, GitHub Actions        |

## Project Structure

```
placementos/
├── apps/
│   ├── web/                 # Next.js 15 frontend (App Router)
│   └── api/                 # FastAPI backend
├── packages/
│   ├── config/              # Shared ESLint, Prettier, TypeScript configs
│   └── types/               # Shared TypeScript types
├── scripts/                 # Native dev setup & start scripts
├── docs/                    # Deployment documentation
├── .github/workflows/       # CI pipelines
└── turbo.json               # Turborepo task orchestration
```

## Prerequisites

| Tool                                      | Version |
| ----------------------------------------- | ------- |
| [Node.js](https://nodejs.org/)            | 20+     |
| [Python](https://www.python.org/)         | 3.12+   |
| [PostgreSQL](https://www.postgresql.org/) | 16+     |
| [Git](https://git-scm.com/)               | Latest  |
| npm                                       | 10+     |

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd placementos
```

### 2. Environment setup

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Edit `apps/api/.env` and `apps/web/.env.local` with your local credentials.

### 3. Automated setup (recommended)

**Windows (PowerShell):**

```powershell
.\scripts\setup-dev.ps1
```

**Linux / macOS:**

```bash
chmod +x scripts/*.sh
./scripts/setup-dev.sh
```

This script will:

- Install Node.js dependencies (`npm install`)
- Create a Python virtual environment in `apps/api/.venv`
- Install Python dependencies
- Copy environment files if missing
- Verify PostgreSQL connectivity
- Run database migrations

### 4. Manual setup (alternative)

**Frontend:**

```bash
npm install
```

**Backend:**

```bash
cd apps/api
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**Database:**

1. Install and start PostgreSQL locally.
2. Create a database and user:

```sql
CREATE USER placementos WITH PASSWORD 'placementos';
CREATE DATABASE placementos OWNER placementos;
```

3. Set `DATABASE_URL` in `apps/api/.env`:

```
DATABASE_URL=postgresql://placementos:placementos@localhost:5432/placementos
```

4. Run migrations:

```bash
cd apps/api
alembic upgrade head
```

## Environment Variables

### Frontend (`apps/web/.env.local`)

| Variable              | Description                                        |
| --------------------- | -------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: `http://localhost:8000`) |

### Backend (`apps/api/.env`)

| Variable                | Description                   |
| ----------------------- | ----------------------------- |
| `DATABASE_URL`          | PostgreSQL connection string  |
| `JWT_SECRET_KEY`        | Secret for JWT token signing  |
| `GOOGLE_CLIENT_ID`      | Google OAuth client ID        |
| `GOOGLE_CLIENT_SECRET`  | Google OAuth client secret    |
| `GOOGLE_REDIRECT_URI`   | OAuth callback URL            |
| `FRONTEND_URL`          | Frontend origin for redirects |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name         |
| `CLOUDINARY_API_KEY`    | Cloudinary API key            |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret         |

See `apps/api/.env.example` for additional optional settings (CORS, cookie security, token expiry).

## Running Locally

### Option A — Separate terminals

**Windows:**

```powershell
.\scripts\start-api.ps1    # Terminal 1 — API on :8000
.\scripts\start-web.ps1    # Terminal 2 — Web on :3000
```

**Linux / macOS:**

```bash
./scripts/start-api.sh     # Terminal 1
./scripts/start-web.sh     # Terminal 2
```

### Option B — Turborepo (both apps)

From the repository root:

```bash
npm run dev
```

| Service  | URL                          |
| -------- | ---------------------------- |
| Web      | http://localhost:3000        |
| API      | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |
| Health   | http://localhost:8000/health |

## Available Scripts

| Command                                  | Description                        |
| ---------------------------------------- | ---------------------------------- |
| `npm run dev`                            | Start all apps in development mode |
| `npm run build`                          | Build all apps                     |
| `npm run lint`                           | Run ESLint across the monorepo     |
| `npm run typecheck`                      | Run TypeScript type checking       |
| `npm run format`                         | Format code with Prettier          |
| `npm run format:check`                   | Check code formatting              |
| `scripts/setup-dev.ps1` / `setup-dev.sh` | Full native dev setup              |
| `scripts/start-api.ps1` / `start-api.sh` | Start FastAPI with reload          |
| `scripts/start-web.ps1` / `start-web.sh` | Start Next.js dev server           |
| `scripts/verify-postgres.py`             | Test PostgreSQL connection         |

## Authentication

PlacementOS uses Google OAuth restricted to `@nitrr.ac.in` institutional emails.

### Google OAuth Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Identity services
3. Create OAuth 2.0 credentials (Web application)
4. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
5. Copy Client ID and Client Secret to `apps/api/.env`

### Auth Endpoints

| Method | Endpoint                       | Description                   |
| ------ | ------------------------------ | ----------------------------- |
| GET    | `/api/v1/auth/google/login`    | Initiate Google OAuth         |
| GET    | `/api/v1/auth/google/callback` | OAuth callback                |
| POST   | `/api/v1/auth/exchange`        | Exchange auth code for tokens |
| POST   | `/api/v1/auth/logout`          | Sign out                      |
| GET    | `/api/v1/auth/me`              | Current user profile          |
| GET    | `/api/v1/roles`                | List roles (authenticated)    |

### Default Roles

- `SUPER_ADMIN` — Full system access
- `PLACEMENT_CELL` — Placement cell staff
- `PLACEMENT_CONVENER` — Placement convener
- `STUDENT` — Default role for new users

## Deployment

Free-tier production stack:

- **Frontend:** Vercel (Hobby)
- **Backend:** Render (free web service)
- **Database:** Neon PostgreSQL (free)
- **File storage:** Cloudinary (free)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for step-by-step hosting (Vercel + Render + Neon). Staging RC checklist: [docs/STAGING_DEPLOYMENT_REPORT.md](docs/STAGING_DEPLOYMENT_REPORT.md).

## Troubleshooting

### PostgreSQL connection refused

- Ensure PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Verify `DATABASE_URL` in `apps/api/.env`
- Run `python scripts/verify-postgres.py` from the repo root

### `ModuleNotFoundError` in API

- Activate the virtual environment before running the API
- Re-run setup: `.\scripts\setup-dev.ps1` or `./scripts/setup-dev.sh`

### Port already in use

- Stop existing processes on ports 3000 or 8000
- Windows: `netstat -ano | findstr :8000` then `Stop-Process -Id <PID>`

### Migrations fail

```bash
cd apps/api
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
alembic upgrade head
```

### Frontend build fails (`.next` lock)

- Stop the dev server before running `npm run build`

## License

Proprietary — All rights reserved.
