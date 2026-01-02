# PyQt6 Warehouse System 🏭

Desktop industrial mini-ERP built with Python and PyQt6, following a strict MVP architecture.  Features PostgreSQL integration, role-based permissions, secure user management, audit-ready design, and clean separation of concerns.

![Python](https://img.shields.io/badge/Python-97.7%25-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
<!-- ![License](https://img.shields.io/badge/license-MIT-green.svg) -->

---

## ✨ Features

- 🔐 **Secure Authentication** - Password hashing and role-based access control (RBAC)
- 📦 **Inventory Management** - Real-time stock tracking and product cataloging
- 🏗️ **MVP Architecture** - Clean separation of concerns for maintainability and scalability
- 📊 **Audit Trail** - Complete logging of user actions for compliance
- 🎨 **Modern UI** - Professional interface built with PyQt6 and custom CSS

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Miniconda (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/joeescarcega8879/PyQt6-Warehouse-System.git
cd PyQt6-Warehouse-System

# Create environment (Option 1: Conda)
conda env create -f environment.yml
conda activate warehouse-system

# Or (Option 2: pip)
pip install -r requirements.txt

# Configure environment
cp .env.example . env
# Edit .env with your database credentials

# Run application
python main_application.py
```

---

## 📁 Project Structure

```
PyQt6-Warehouse-System/
├── main.py                    # Entry point
├── src/
│   ├── models/               # Data layer (PostgreSQL)
│   ├── views/                # UI layer (PyQt6)
│   ├── presenters/           # Business logic
│   ├── utils/                # Security, validation, logging
│   └── resources/            # CSS styles & icons
├── scripts/                  # DB setup scripts
├── tests/                    # Unit tests
└── docs/                     # Documentation
```

---

## 🛠️ Technologies

**Core Stack:**
- **Python 3.12** - Programming language
- **PyQt6** - Desktop GUI framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **bcrypt** - Password hashing

**Key Libraries:**
```
PyQt6==6.6.0
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
bcrypt==4.1.2
python-dotenv==1.0.0
```

---

## 🏛️ Architecture

**MVP Pattern** (Model-View-Presenter):
- **Model**: PostgreSQL database and data management
- **View**: PyQt6 UI components
- **Presenter**: Business logic and coordination

Benefits:  Testability, maintainability, scalability, and clean separation of concerns.

---

## 🔒 Security

- Password hashing with bcrypt
- Role-based access control (Admin, Manager, User)
- SQL injection prevention (parameterized queries)
- Session management with timeout
- Audit logging for compliance

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src tests/
```

---

## 🗺️ Roadmap

**v1.0** (Current)
- ✅ User authentication & RBAC
- ✅ Inventory management
- ✅ Audit logging

**v1.1** (Planned)
- [ ] Advanced reports & analytics
- [ ] Export to Excel/PDF
- [ ] Barcode scanner integration

**v2.0** (Future)
- [ ] Multi-warehouse support
- [ ] REST API for mobile
- [ ] Dashboard with charts

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Code Style:** Follow PEP 8, use type hints, write docstrings and tests.

---

<!-- ## 📄 License -->

<!-- MIT License - see [LICENSE](LICENSE) file for details. -->

<!-- --- -->

## 👤 Author

**Joe Escarcega**
- GitHub: [@joeescarcega8879](https://github.com/joeescarcega8879)
- Email: jose.escarcega8879@gmail.com

---

## 💡 Support

- 🐛 [Report Issues](https://github.com/joeescarcega8879/PyQt6-Warehouse-System/issues)
- ⭐ Star this repo if you find it helpful!

---

<div align="center">
Made with ❤️ and Python
</div>