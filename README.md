# PyQt6 Warehouse System

Desktop mini-ERP/warehouse app built with Python + PyQt6 using an MVP architecture. Uses PostgreSQL, includes authentication (bcrypt), role-based permissions (RBAC), and audit logging.

![Python](https://img.shields.io/badge/Python-97.7%25-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)

---

## Features

- Secure authentication with bcrypt
- Password complexity validation
- Login rate limiting and brute force protection
- Session timeout for security
- Role-based access control (RBAC) with 5 roles: admin, supervisor, leader, operator, viewer
- Audit trail for all critical operations
- Materials, suppliers, production lines, supplier receipts, and production request management
- MDI interface — each module opens as a subwindow

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- PyQt6

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/joeescarcega8879/PyQt6-Warehouse-System.git
   cd PyQt6-Warehouse-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Set up the database**
   ```bash
   # Create schema from scratch
   psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/schema.sql

   # (Optional) Load test data
   psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/seed_data.sql
   ```

5. **Run the application**
   ```bash
   python main_application.py
   ```

---

## Database Management

| File | Purpose |
|---|---|
| `docs/schema.sql` | Full DDL — creates all tables, sequences, constraints and indexes |
| `docs/reset_db.sql` | DROP CASCADE all tables + recreate schema — for development/testing |
| `docs/seed_data.sql` | Idempotent test data (`ON CONFLICT DO NOTHING`) |

```bash
# Full reset + reload structure
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/reset_db.sql

# Full reset + structure + test data
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/reset_db.sql
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/seed_data.sql
```

**Test data password (all users):** `Admin1234!`

---

## Configuration

All sensitive configuration is managed through environment variables in the `.env` file:

| Variable | Description | Default |
|---|---|---|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | (required) |
| `DB_USER` | Database username | (required) |
| `DB_PASSWORD` | Database password | (required) |
| `DB_SSL_MODE` | SSL mode | `prefer` |
| `APP_ENV` | Environment (`development`/`production`) | `production` |
| `SESSION_TIMEOUT_MINUTES` | Inactivity timeout in minutes | `30` |
| `MAX_LOGIN_ATTEMPTS` | Max failed logins before lockout | `5` |
| `LOGIN_LOCKOUT_MINUTES` | Lockout duration in minutes | `30` |
| `PASSWORD_MIN_LENGTH` | Minimum password length | `8` |

**IMPORTANT:** Never commit the `.env` file to version control.

---

## Project Structure

```
PyQt6-Warehouse-System/
├── main_application.py      # Entry point + navigation controller
├── src/
│   ├── models/              # Data layer (QSqlQuery via QueryHelper)
│   ├── presenters/          # Business logic (MVP Presenter)
│   ├── views/               # UI layer (PyQt6 widgets)
│   │   └── ui/              # Qt Designer .ui files
│   ├── domain/              # Business rules (permissions, audit, password policy)
│   ├── common/              # Shared utilities (session, status bar, formatting)
│   ├── database/            # DB connection + QueryHelper + migrations
│   ├── assets/              # QSS styles + icons
│   └── config/              # Settings (dotenv) + logger config
├── tests/                   # Unit tests (pytest)
├── docs/                    # SQL files
│   ├── schema.sql
│   ├── reset_db.sql
│   └── seed_data.sql
├── logs/                    # Rotating log files (app_YYYYMMDD.log)
├── .env.example             # Environment template
└── requirements.txt
```

---

## Architecture

MVP (Model-View-Presenter):

- **Model** — `src/models/`: database access only, returns `tuple[bool, str|None]` or `list[tuple]`
- **View** — `src/views/` + `src/views/ui/`: PyQt6 widgets, passive — emits signals only
- **Presenter** — `src/presenters/`: business logic, connects view signals to model calls
- **Domain** — `src/domain/`: pure policies (permissions, password rules, rate limiting)
- **Common** — `src/common/`: shared utilities (session manager, status bar, formatting)

All module presenters inherit from `BasePresenter`. All module models inherit from `BaseModel`.

---

## Testing

```bash
pytest tests/                        # Run all tests
pytest tests/ --cov                  # With coverage report
pytest tests/unit/models/ -v         # Specific module, verbose
```

---

## Author

Joe Escarcega

## Support

Report issues: https://github.com/joeescarcega8879/PyQt6-Warehouse-System/issues
