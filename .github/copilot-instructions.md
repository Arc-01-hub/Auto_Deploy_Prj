# Copilot instructions for this repository

## Build, run, and deployment commands

### Local Python run
```bash
python -m venv env
source env/bin/activate  # Linux/macOS
python -m pip install -r requirements.txt
python app.py
```

### Docker Compose run (app + MySQL + phpMyAdmin)
```bash
docker compose up -d --build
```

### CI/CD deploy behavior (GitHub Actions)
The workflow in `.github/workflows/deploy.yaml` deploys on every push to `main` by SSH-ing into the server and running:
```bash
cd /home/arc/Auto_Deploy_Prj
git pull origin main
docker compose down
docker compose up -d --build
```

### Tests and linting
There are currently no project test or lint commands configured in this repository (and no project test suite files outside `env/` site-packages), so there is no single-test command at this time.

## High-level architecture

- This is a single-file Flask backend (`app.py`) with SQLAlchemy models (`User`, `Formation`, `Registration`), authentication (Flask-Login), HTML routes, and one JSON API route.
- UI rendering is split between Jinja templates and vanilla JavaScript:
  - `templates/index.html` provides page shell and injects `window.App.isAdmin`.
  - `static/js/app.js` fetches `/api/formations`, renders cards client-side, applies category filtering, and handles admin delete actions via fetch POST.
- Formation details and registration use server-rendered templates (`formation_detail.html`) and POST back to the same route for registration actions.
- Startup flow in `app.py`:
  1. `init_db()` retries `db.create_all()` (Docker/MySQL readiness handling).
  2. Ensures default admin account exists (`admin` / `password` on first boot).
  3. Seeds formations from `data/formations.json` only when the formations table is empty.

## Key repository conventions

- Admin authorization is username-based (`current_user.username == 'admin'`) across backend routes and template behavior; there is no separate role model/table.
- Seat counts are derived, not stored:
  - `Formation.reserved_seats` uses relationship count.
  - `Formation.available_seats` is computed from `total_seats - reserved_seats`.
- Formation API payload shape is fixed to:
  - `GET /api/formations` → `{ "formations": [Formation.to_dict(), ...] }`
  - Frontend code depends on these exact keys.
- Main catalog content is rendered entirely by `static/js/app.js` after API fetch; template changes to card layout usually require matching JS updates.
- Database configuration is environment-driven (`DATABASE_URL`), with container-friendly default host `mysql` in `app.py` and `docker-compose.yml`.

## MCP configuration

- Workspace MCP config lives at `.vscode/mcp.json`.
- Playwright MCP is configured as:
  - command: `npx`
  - args: `["@playwright/mcp@latest"]`
