# Formation Manager

A clean, minimalist training catalog web app built with Flask, semantic HTML, vanilla CSS, and vanilla JavaScript. Now includes user authentication with MySQL database.

## Project structure

- `app.py` — Flask backend with authentication and API routes
- `data/formations.json` — static JSON data source for formations
- `templates/index.html` — main page template
- `templates/login.html` — login page template
- `static/css/styles.css` — styling for layout and cards
- `static/js/app.js` — fetch logic and dynamic rendering

## Setup

1. Install MySQL server (if not already installed)

2. Create a database:
   ```sql
   CREATE DATABASE formations_db;
   ```

3. Create and activate a virtual environment:

```powershell
python -m venv env
env\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configuration

The app uses environment variables for production-ready configuration:

- `SECRET_KEY` — a strong Flask secret key
- `DATABASE_URL` — SQLAlchemy connection string
- `FLASK_DEBUG` — set to `1` only for local debugging
- `PORT` — optional port, defaults to `5000`

Example (PowerShell):

```powershell
$env:SECRET_KEY="replace-with-secure-key"
$env:DATABASE_URL="mysql+pymysql://root:root@localhost:3306/formations_db"
$env:FLASK_DEBUG=0
$env:PORT=5000
python app.py
```

## Run locally

1. Start the app:

```powershell
python app.py
```

2. Open the browser at `http://127.0.0.1:5000`

3. Login with default credentials:
   - Username: `admin`
   - Password: `password`

## Production notes

- The app defaults to `DEBUG=False` unless `FLASK_DEBUG=1`
- Use a secure `SECRET_KEY` in production
- Use a MySQL database connection string in `DATABASE_URL`
- Tables and seed data are created automatically on first run

## Database

- Uses MySQL with PyMySQL driver
- Default DB URI fallback: `mysql+pymysql://root:root@192.168.11.238:3306/formations_db`
- Formations are seeded from `data/formations.json` when the database is empty
- Admin can create formations; users can view details and register while seats remain
