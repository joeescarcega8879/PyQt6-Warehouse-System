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
- Role-based access control (RBAC)
- Audit trail
- Materials, suppliers, and production management
- MDI interface (forms open as subwindows)

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

4. **Run database migrations**
   ```bash
   psql -U your_username -d inventory_production_db -f database/migrations/001_create_login_attempts.sql
   ```

5. **Run the application**
   ```bash
   python main_application.py
   ```

---

## Configuration

All sensitive configuration is managed through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | (required) |
| `DB_USER` | Database username | (required) |
| `DB_PASSWORD` | Database password | (required) |
| `SESSION_TIMEOUT_MINUTES` | Session timeout | 30 |
| `MAX_LOGIN_ATTEMPTS` | Max failed logins | 5 |
| `PASSWORD_MIN_LENGTH` | Min password length | 8 |

**IMPORTANT:** Never commit the `.env` file to version control.

---

## Project Structure

```
PyQt6-Warehouse-System/
├── common/                # Error handling, session manager
├── config/                # Configuration and logging
├── database/              # DB connection + migrations
├── domain/                # Business logic (permissions, audit, password policy)
├── models/                # Data layer (base_model.py + specific models)
├── presenters/            # Presenter layer (base_presenter.py + specific presenters)
├── views/                 # View layer (PyQt6 widgets)
├── ui/                    # Qt Designer .ui files
├── tests/                 # Unit tests (pytest)
├── .env.example           # Environment template
└── main_application.py    # Entry point
```

---

## Architecture

MVP (Model-View-Presenter):

- **Model**: `models/` - Database access using BaseModel pattern
- **View**: `views/` + `ui/` - PyQt6 widgets + Qt Designer UI
- **Presenter**: `presenters/` - Business logic using BasePresenter pattern
- **Domain**: `domain/` - Security policies and permissions
- **Common**: `common/` - Shared utilities

---

## Testing

Run tests with pytest:

```bash
pytest tests/                          # Run all tests
pytest tests/ --cov                    # With coverage report
pytest tests/unit/models/ -v           # Specific module with verbose output
```

---

## Author

Joe Escarcega

## Support

Report issues: https://github.com/joeescarcega8879/PyQt6-Warehouse-System/issues
