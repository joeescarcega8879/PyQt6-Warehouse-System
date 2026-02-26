# PyQt6 Warehouse System

Desktop mini-ERP/warehouse app built with Python + PyQt6 using an MVP architecture (Model-View-Presenter). Uses PostgreSQL via Qt's SQL driver (`QPSQL`), includes authentication (bcrypt), role-based permissions (RBAC), and audit logging.

![Python](https://img.shields.io/badge/Python-97.7%25-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)

---

## Features

- Secure authentication (bcrypt)
- Role-based access control (RBAC)
- Audit trail (DB-based audit_log)
- Materials and production lines modules
- MDI interface (forms open as subwindows)

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- PyQt6

### Install

Option A: Conda

```bash
conda env create -f environment.yml
conda activate warehouse-system
```

Option B: Pip

```bash
python3 -m pip install -r requirements.txt
```

### Run

```bash
python3 main_application.py
```

---

## Project Structure

This repository does not use a `src/` layout. The current structure is:

```
PyQt6-Warehouse-System/
├── assets/                     # Images and styles
├── common/                     # UI helpers (formatting, styles, status bar)
├── config/                     # App logging configuration
├── database/                   # DB connection + query helper (QSqlQuery)
├── domain/                     # Permissions, roles, audit definitions
├── logs/                       # Runtime logs (generated)
├── models/                     # Data layer (SQL queries)
├── presenters/                 # Presenter layer (business logic)
├── ui/                         # Qt Designer .ui files
├── views/                      # View layer (PyQt6 widgets, load .ui)
├── main_application.py         # Entry point
├── requirements.txt
├── environment.yml
└── README.md
```

---

## Architecture

MVP (Model-View-Presenter):

- Model: `models/` + `database/` (PostgreSQL access through `QueryHelper`)
- View: `views/` + `ui/` (PyQt6 widgets + Qt Designer UI)
- Presenter: `presenters/` (coordinates view events and model calls)

---

## Database Notes

- The app connects using Qt's PostgreSQL driver: `QPSQL`.
- Database credentials are currently hardcoded in `database/connection.py`.
  - Recommended next step: move DB settings to environment variables or a `.env` file.

---

## Modules (Current)

- Users: `models/user_model.py`, `views/user_view.py`, `presenters/user_presenter.py`
- Materials: `models/material_model.py`, `views/material_view.py`, `presenters/material_presenter.py`
- Production Lines: `models/production_line_model.py`, `views/line_view.py`, `presenters/production_line_presenter.py`
- Audit Log: `models/audit_model.py`, `domain/audit_service.py`
- Supplier Receipts (model only for now): `models/supplier_receipt_model.py`

---

## Troubleshooting

- If you see `QPSQL driver not loaded`, install the Qt SQL PostgreSQL driver for your OS.
- If `import PyQt6` fails, install PyQt6 in your environment.

---

## Author

Joe Escarcega

## Support

- Report issues: https://github.com/joeescarcega8879/PyQt6-Warehouse-System/issues
