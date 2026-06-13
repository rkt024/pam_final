# DOLMA Office Portal

> **Streamlit dashboard for Nepal's land management system** — `public.dolma.gov.np`

A production-ready internal portal for Department of Land Management and Archive (DOLMA) office staff. Handles authentication, registration data browsing, and quick actions (Transfer, Return, Verify) with SQLite-based tracking.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/rkt024/pam_final.git
cd pam_final

# Build and run with Docker Compose
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

The app opens at **http://localhost:8501**

Data is persisted in a Docker volume (`pam_final_data`) — survives container rebuilds.

### Option 2: Local Python Development

```bash
# Clone the repository
git clone https://github.com/rkt024/pam_final.git
cd pam_final

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (see Configuration below)

# Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 🐳 Docker Deployment

### Single Container (Docker Compose)

```bash
# Build image
docker compose build

# Start in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f pam_final

# Stop and remove
docker compose down

# Stop and remove WITH data volume (⚠️ deletes tracking.db)
docker compose down -v
```

### Manual Docker Commands

```bash
# Build image
docker build -t pam_final .

# Run with persistent volume
docker run -d \
  --name pam_final \
  -p 8501:8501 \
  -v pam_final_data:/app/data \
  -e VERIFY_SSL=false \
  pam_final

# View logs
docker logs -f pam_final

# Stop
docker stop pam_final
```

### Production Deployment Tips

| Concern | Recommendation |
|---------|----------------|
| **SSL** | Set `VERIFY_SSL=true` and use reverse proxy (nginx/Traefik) with HTTPS |
| **Secrets** | Use Docker secrets or `.env` file (not in image) |
| **Port** | Change `8501:8501` to `80:8501` or `443:8501` behind proxy |
| **Data** | Bind mount to host path: `-v /opt/pam_final/data:/app/data` |
| **Auto-restart** | Add `restart: unless-stopped` (already in compose) |
| **Health checks** | Built-in (`/_stcore/health`) — monitored by Docker |

### Environment Variables for Docker

```yaml
# docker-compose.yml overrides
environment:
  - VERIFY_SSL=false
  - DATA_DIR=/app/data
  - TRACKING_DB_PATH=/app/data/tracking.db
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
```

---

## ⚙️ Configuration

Create `.env` from `.env.example`:

```env
# Database (SQLite for tracking verified references)
# In Docker, this defaults to /app/data/tracking.db (persisted via volume)
TRACKING_DB_PATH=tracking.db

# Data directory (Docker: /app/data, Local: ./data)
DATA_DIR=./data

# SSL verification (set to true in production)
VERIFY_SSL=false
```

| Variable | Required | Default (Local) | Default (Docker) | Description |
|----------|----------|-----------------|------------------|-------------|
| `TRACKING_DB_PATH` | No | `./data/tracking.db` | `/app/data/tracking.db` | Path to SQLite tracking database |
| `DATA_DIR` | No | `./data` | `/app/data` | Directory for persistent data |
| `VERIFY_SSL` | No | `false` | `false` | Enable SSL cert verification for API calls |

**Note**: DOLMA credentials (username/password) are entered at **login time**, not stored in `.env`.

---

## 📁 Project Structure

```
pam_final/
├── app.py                 # Entry point, routing, global styles
├── config.py              # Constants: BASE_URL, PROCESS_IDS, PAGES
├── .env.example           # Environment template
├── .gitignore             # Ignores .env, *.db, __pycache__, venv, data/
├── .dockerignore          # Excludes build artifacts from Docker context
├── Dockerfile             # Multi-stage production image
├── docker-compose.yml     # Easy deployment with persistent volume
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Dev tools (ruff, mypy, pytest)
├── run_pam_app.bat        # Windows launcher
├── .streamlit/
│   └── config.toml        # Streamlit theme config
├── data/                  # Persistent data (gitignored, Docker volume)
│   └── tracking.db        # SQLite: user-marked verified references
├── components/
│   ├── sidebar.py         # Navigation, theme toggle, logout
│   └── table.py           # Data tables with actions
├── pages/
│   ├── login.py           # Login form + API auth
│   ├── dashboard.py       # Quick Transfer/Return actions
│   └── check_ref_status.py # Detailed reference lookup + timeline
├── services/
│   ├── data_service.py    # API calls: fetch, transfer, return, verify
│   └── tracking_db_service.py # SQLite: mark checked/verified
└── utils/
    ├── api.py             # HTTP layer with auto re-login on 401/403
    └── state.py           # Session state init + flash messages
```

---

## 🎯 Features

### Pages

| Page | Purpose |
|------|---------|
| **Login** | Secure authentication with token auto-refresh |
| **Dashboard** | Quick actions: Transfer (Rokka/Fukuwa/Others), Return with remarks |
| **Check Ref Status** | Full reference lookup — timeline, status codes, LRIMS mapping |
| **Process Tables** (11 tabs) | Paginated, searchable lists per process type with CSV export |

### Supported Processes

| Process | ID | Notes |
|---------|-----|-------|
| Rokka/Fukuwa | `8,15` | Dual-process, agency tracking |
| Likhat Parit | `1` | |
| Jagga Darta | `2` | |
| Namsari | `3` | |
| Dakhil Kharej | `4` | |
| Samsodan | `5` | |
| Halsabik | `7` | |
| Apartment | `16` | |
| Pratilipi | `21` | |
| Guthi Adhinastha | `22` | |

### Actions Available

| Action | Pages | Description |
|--------|-------|-------------|
| **Transfer** | Dashboard, Tables, Detail | Forward reference to next stage (Rokka/Fukuwa/Others) |
| **Return** | Dashboard, Tables, Detail | Send back with mandatory remarks |
| **Verify** | Detail (Fukuwa only) | Mark as verified |
| **Mark Verified** | Tables (Rokka/Fukuwa) | Local SQLite tracking (green ✅ indicator) |
| **Export CSV** | All Tables | Download filtered/sorted data |

---

## 🔐 Authentication Flow

1. User enters **DOLMA username/password** at login
2. App calls `POST /pam/api/auth/login` → receives `accessToken`
3. Token stored in **session state only** (not persisted)
4. All API calls include `Authorization: Bearer ***`
5. On **401/403**, app auto-re-logs in silently and **retries once**

---

## 🗄️ Tracking Database (SQLite)

Local `tracking.db` (in `data/` or Docker volume) stores **user-marked verified references**:

```sql
CREATE TABLE checked_rows (
    reference_no TEXT,
    checked_at TEXT,      -- ISO timestamp
    checked_by TEXT,      -- username
    PRIMARY KEY (reference_no, checked_by)  -- per-user isolation
);
```

- Only used for **Rokka/Fukuwa** process
- Green ✅ badge in tables for verified refs
- **Per-user isolation**: Each user sees only their own verified refs
- Auto-migrates from old schema on first run

---

## 🛠️ Development

### Install Dev Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Lint & format
ruff check . && ruff format .

# Type check
mypy .

# Run tests
pytest -v
```

### Pre-commit (Optional)

```bash
pip install pre-commit
pre-commit install
```

### Run with Docker (Development)

```bash
# Mount source for live reload
docker run -d \
  --name pam_final_dev \
  -p 8501:8501 \
  -v $(pwd):/app \
  -v pam_final_data:/app/data \
  pam_final
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.57.0 | Web app framework |
| `requests` | 2.33.1 | HTTP client |
| `pandas` | 3.0.2 | Data manipulation |
| `python-dotenv` | 1.2.2 | Environment loading |
| `urllib3` | 2.6.3 | HTTP with SSL control |

Dev: `ruff`, `mypy`, `pytest`, `pytest-mock`, `pytest-cov`

---

## 🔧 Common Issues

| Issue | Solution |
|-------|----------|
| SSL errors | Set `VERIFY_SSL=true` in `.env` or ensure certs are valid |
| "No valid role" | User must have at least one role assigned in DOLMA |
| Token expired | App auto-refreshes; if stuck, log out and back in |
| Empty tables | Check process ID mapping in `config.py` |
| Data lost on rebuild | Use Docker volume (`pam_final_data`) or bind mount |
| Permission denied (Docker) | Ensure `data/` dir exists and is writable by `appuser` (UID 1000) |

---

## 📜 License

Internal tool for Department of Land Management and Archive, Nepal. Not for public distribution.

---

## 👤 Author

**Raju Tamang** — [@rkt024](https://github.com/rkt024)