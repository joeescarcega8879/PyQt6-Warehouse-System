# PyQt6 Warehouse System — Context Document

## Descripcion General

Mini-ERP / sistema de almacen de escritorio construido con **Python 3.12+ + PyQt6**.
Permite gestionar materiales, proveedores, lineas de produccion, ordenes de recepcion
y usuarios, con autenticacion segura, control de acceso por roles (RBAC) y bitacora
de auditoria. La base de datos es **PostgreSQL 14+** y la interfaz utiliza un patron
**MDI (Multiple Document Interface)** donde cada modulo se abre como sub-ventana.

**Punto de entrada:** `main_application.py`
**Patron de arquitectura:** MVP (Model – View – Presenter)

---

## Estructura del Proyecto

```
PyQt6-Warehouse-System/
│
├── main_application.py          # Entry point + controlador de navegacion
│
├── src/                         # Codigo fuente principal (MVP)
│   ├── models/                  # Capa de datos (SQL via PyQt6 QSqlQuery)
│   │   ├── base_model.py        # Patron base con helpers CRUD reutilizables
│   │   ├── audit_model.py       # Persistencia de eventos de auditoria
│   │   ├── material_model.py    # CRUD de materiales
│   │   ├── production_line_model.py     # CRUD de lineas de produccion
│   │   ├── production_request_model.py  # CRUD de ordenes de produccion
│   │   ├── supplier_model.py    # CRUD de proveedores
│   │   ├── supplier_receipt_model.py    # CRUD de recepciones de proveedor
│   │   └── user_model.py        # CRUD de usuarios + autenticacion (bcrypt)
│   │
│   ├── presenters/              # Capa de logica de negocio (MVP Presenter)
│   │   ├── base_presenter.py    # Patron base: status, busqueda, edit-mode
│   │   ├── login_presenter.py   # Autenticacion + rate limiting
│   │   ├── main_presenter.py    # Navegacion principal + permisos de menu
│   │   ├── material_presenter.py          # Logica de materiales
│   │   ├── user_presenter.py              # Logica de usuarios
│   │   ├── production_line_presenter.py   # Logica de lineas de produccion
│   │   ├── supplier_presenter.py          # Logica de proveedores
│   │   ├── supplier_receipt_presenter.py  # Logica de recepciones
│   │   ├── change_password_presenter.py   # Cambio de contrasena
│   │   └── generic_presenter.py           # Selector generico de entidades
│   │
│   ├── views/                   # Capa de UI (PyQt6 Widgets)
│   │   ├── login_view.py        # Pantalla de login
│   │   ├── main_view.py         # Ventana principal MDI
│   │   ├── material_view.py     # Formulario de materiales
│   │   ├── user_view.py         # Formulario de usuarios
│   │   ├── line_view.py         # Formulario de lineas de produccion
│   │   ├── supplier_view.py     # Formulario de proveedores
│   │   ├── receipt_view.py      # Formulario de recepciones
│   │   ├── change_password_view.py   # Dialog de cambio de contrasena
│   │   └── generic_view.py      # Vista selector generica (dialog)
│   │
│   ├── domain/                  # Reglas de negocio / politicas de seguridad
│   │   ├── roles.py                     # Enum UserRole (admin/supervisor/leader/operator/viewer)
│   │   ├── permissions.py               # Logica de evaluacion de permisos
│   │   ├── permissions_definitions.py   # Constantes de permisos (Permission.*)
│   │   ├── permissions_service.py       # Servicio de verificacion de permisos
│   │   ├── audit_definitions.py         # Enum AuditDefinition (eventos auditables)
│   │   ├── audit_service.py             # Servicio de escritura de auditoria
│   │   ├── password_policy.py           # Validacion de complejidad de contrasena
│   │   ├── login_attempt_tracker.py     # Rate limiting de intentos de login
│   │   └── production_request_status.py # Enum de estados de orden de produccion
│   │
│   ├── common/                  # Utilidades compartidas
│   │   ├── enums.py             # StatusType (SUCCESS / ERROR / WARNING)
│   │   ├── styles.py            # Estilos de status bar (dict por StatusType)
│   │   ├── style_manager.py     # Carga y aplica estilos globales QSS
│   │   ├── status_bar_controller.py  # Controlador de barra de estado
│   │   ├── session_manager.py   # Manejo de timeout de sesion (QTimer)
│   │   ├── error_messages.py    # Mensajes de error centralizados + log
│   │   ├── format.py            # Helpers de formateo de datos
│   │   ├── model_adapter.py     # Adaptador de tuples de modelo a QStandardItemModel
│   │   └── entity_config.py     # Configuracion generica de entidades (EntityType enum)
│   │
│   ├── database/                # Capa de acceso a datos
│   │   ├── connection.py        # Conexion PostgreSQL via QSqlDatabase
│   │   ├── query_helper.py      # Wrapper de QSqlQuery (fetch_all, fetch_one, execute)
│   │   └── migrations/
│   │       └── 001_create_login_attempts.sql
│   │
│   └── config/                  # Configuracion de la aplicacion
│       ├── settings.py          # DatabaseConfig / AppConfig / SecurityConfig (dotenv)
│       └── logger_config.py     # Configuracion de logging con rotacion de archivos
│
├── ui/                          # Archivos .ui de Qt Designer
│   ├── login_view.ui
│   ├── main_view.ui
│   ├── material_view.ui
│   ├── user_view.ui
│   ├── line_view.ui
│   ├── supplier_view.ui
│   ├── receipt_view.ui
│   ├── change_password.ui
│   └── generic_view.ui
│
├── tests/                       # Suite de pruebas (pytest)
│   ├── conftest.py
│   ├── unit/
│   │   ├── models/
│   │   │   ├── test_material_model.py
│   │   │   └── test_user_model.py
│   │   ├── domain/
│   │   │   ├── test_password_policy.py
│   │   │   └── test_login_attempt_tracker.py
│   │   └── common/
│   │       ├── test_error_messages.py
│   │       └── test_session_manager.py
│   └── integration/             # (vacio - pendiente)
│       └── __init__.py
│
├── assets/
│   ├── styles.css               # Estilos globales QSS
│   └── Images/                  # Imagenes de la aplicacion
│
├── logs/                        # Logs rotativos por fecha (app_YYYYMMDD.log)
│
├── .env.example                 # Plantilla de variables de entorno
├── .env                         # Variables de entorno locales (NO commitear)
├── requirements.txt             # Dependencias Python
├── environment.yml              # Entorno conda
├── pytest.ini                   # Configuracion de pytest
├── .coveragerc                  # Configuracion de coverage
└── README.md
```

---

## Tecnologias y Dependencias

| Tecnologia | Uso |
|---|---|
| Python 3.12+ | Lenguaje principal |
| PyQt6 | Framework de UI (widgets, QSql, QTimer, signals) |
| PostgreSQL 14+ | Base de datos relacional |
| bcrypt | Hash seguro de contrasenas |
| python-dotenv | Carga de variables de entorno |
| pytest | Framework de pruebas |
| pytest-cov | Cobertura de codigo |

---

## Arquitectura MVP

```
View  <──signals──>  Presenter  <──calls──>  Model
 │                       │                     │
PyQt6 Widget         Logica de negocio     SQL / DB
(pasivo)             + validaciones        (sin estado UI)
```

- **View**: Solo renderiza y emite signals. No contiene logica.
- **Presenter**: Recibe signals de la view, llama al model, actualiza la view.
- **Model**: Solo acceso a datos. Retorna `tuple[bool, str|None]` o listas de tuplas.
- **Domain**: Politicas puras (permisos, contrasenas, rate limiting) sin dependencias UI.
- **BaseModel / BasePresenter**: Clases base con patrones reutilizables (DRY).

---

## Funcionalidades Implementadas

### Autenticacion y Seguridad
- [x] Login con validacion de credenciales (bcrypt)
- [x] Rate limiting: bloqueo tras N intentos fallidos (`LoginAttemptTracker`)
- [x] Politica de complejidad de contrasenas (longitud, mayusculas, digitos, especiales)
- [x] Cambio de contrasena con validacion de politica
- [x] Session timeout por inactividad (`SessionManager` con QTimer)
- [x] Advertencia de sesion proxima a expirar (signal `session_warning`)
- [x] Cierre de sesion automatico al expirar (regresa a login)
- [x] Event filter para detectar actividad del usuario (mouse / teclado)

### Control de Acceso por Roles (RBAC)
- [x] 5 roles definidos: `admin`, `supervisor`, `leader`, `operator`, `viewer`
- [x] Permisos granulares por modulo (materials, users, lines, receipts, supplier, production)
- [x] Ocultacion de botones en UI segun permisos del usuario actual
- [x] Servicio de verificacion centralizado (`PermissionsService`)

### Modulo Materiales
- [x] Listado con tabla paginable
- [x] Busqueda por ID (numerico) y por nombre (ILIKE)
- [x] Crear material (nombre, descripcion, unidad)
- [x] Editar material seleccionado
- [x] Eliminar material seleccionado
- [x] Auditoria de create / edit / delete

### Modulo Proveedores
- [x] Listado con tabla
- [x] Busqueda por ID y por nombre
- [x] Crear proveedor (nombre, departamento, telefono, email, direccion, notas)
- [x] Editar proveedor
- [ ] Eliminar proveedor (sin implementar: no hay boton, ni handler, ni metodo en modelo)
- [x] Auditoria de create / edit

### Modulo Recepciones de Proveedor
- [x] Listado de recepciones
- [x] Crear recepcion (asociada a proveedor, material, cantidad)
- [x] Editar recepcion
- [ ] Eliminar recepcion (metodo en modelo existe, auditoria definida, pero sin boton ni handler)
- [x] Apertura de selector generico para elegir proveedor/material
- [x] Auditoria de create / edit / delete (definido, parcialmente conectado)

### Modulo Lineas de Produccion
- [x] Listado con tabla
- [x] Busqueda por ID y por nombre
- [x] Crear linea (nombre, descripcion, estado activo)
- [x] Editar linea
- [x] Auditoria de create / edit

### Modulo Usuarios
- [x] Listado de usuarios
- [x] Busqueda por ID y por nombre
- [x] Crear usuario (username, email, rol, contrasena)
- [x] Editar usuario
- [x] Cambio de contrasena del usuario actual
- [ ] Cambio de contrasena de un usuario seleccionado (el ID del usuario seleccionado esta comentado, siempre abre para el usuario actual)
- [x] Auditoria de create / edit / password change

### Selector Generico
- [x] Dialog reutilizable para seleccionar Material, Proveedor o Linea de Produccion
- [x] Configuracion via `EntityType` enum (columnas, metodos, campo ID/nombre)
- [x] Signal `item_selected` al confirmar seleccion

### Auditoria
- [x] Modelo de auditoria con escritura a BD
- [x] Definiciones de eventos auditables (`AuditDefinition`)
- [x] Integrado en presenters de: materiales, usuarios, lineas, recepciones, proveedores

### Infraestructura
- [x] Conexion PostgreSQL via `QSqlDatabase` (QPSQL driver)
- [x] `QueryHelper`: wrapper de QSqlQuery con `fetch_all`, `fetch_one`, `execute`, transacciones
- [x] Configuracion via `.env` (dotenv) con validacion al inicio
- [x] Logging rotativo por fecha (`logs/app_YYYYMMDD.log`)
- [x] Estilos globales QSS cargados desde `assets/styles.css`
- [x] `StatusBarController`: mensajes de estado coloreados (SUCCESS / ERROR)
- [x] MDI: cada formulario abre como `QMdiSubWindow`

---

## Funcionalidades Pendientes / Incompletas

### Modulo Ordenes de Produccion (Production Requests)
- [ ] **Sin vista ni presenter implementados** — el modelo (`ProductionRequestModel`) esta completo con:
  - `create_request` (con items, transaccion atomica)
  - `update_status_request` (DRAFT → SUBMITTED → APPROVED / REJECTED / CANCELLED)
  - `deactivate_request`
  - `get_all_requests` / `get_request_by_id`
- [ ] Los permisos estan definidos (`PRODUCTION_REQUESTS_*`)
- [ ] Los eventos de auditoria estan definidos (`PRODUCTION_REQUESTS_CREATED`, etc.)
- [ ] El enum de estados esta definido (`ProductionRequestStatus`)
- [ ] **Falta:** vista, presenter, boton en menu principal, integracion completa

### Modulo Proveedores
- [ ] **Activar / Desactivar proveedor** — no se eliminara, solo se cambiara el estado `is_active`. Falta:
  - Metodo `toggle_active_supplier` (o similar) en `supplier_model.py`
  - Boton y handler en `supplier_view.py` y `supplier_presenter.py`
  - Auditoria del evento

### Bugs Conocidos
- Todos los bugs documentados anteriormente fueron corregidos.

### Pruebas
- [ ] Tests de presenters (ningun presenter tiene cobertura de tests)
- [ ] Tests de vistas
- [ ] Tests de integracion (carpeta `tests/integration/` existe pero vacia)
- [ ] Tests para `ProductionRequestModel`
- [ ] Tests para `SupplierReceiptModel`
- [ ] Tests para `ProductionLineModel`

### Mejoras de Arquitectura
- [ ] `UserPresenter`, `LinePresenter`, `SupplierPresenter`, `SupplierReceiptPresenter` no heredan de `BasePresenter` — codigo duplicado de `_emit_error`/`_emit_success` y manejo de edit-mode
  - `BasePresenter.__init__` ya fue actualizado para aceptar `**kwargs` (asigna `main_app` y otros extras automaticamente via `setattr`)
  - Pendiente: migrar los 4 presenters para que hereden de `BasePresenter`
- [x] `python-dotenv` agregado a `requirements.txt` (version 1.1.0)
- [ ] Falta migracion SQL completa del esquema (solo existe `001_create_login_attempts.sql`; las tablas principales no tienen script de creacion incluido)

---

## Variables de Entorno (.env)

| Variable | Descripcion | Default |
|---|---|---|
| `DB_HOST` | Host PostgreSQL | `localhost` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | *requerido* |
| `DB_USER` | Usuario de BD | *requerido* |
| `DB_PASSWORD` | Contrasena de BD | *requerido* |
| `DB_SSL_MODE` | Modo SSL | `prefer` |
| `APP_ENV` | Entorno (`development`/`production`) | `production` |
| `APP_DEBUG` | Modo debug | `false` |
| `LOG_LEVEL` | Nivel de log | `INFO` |
| `SESSION_TIMEOUT_MINUTES` | Minutos de inactividad para expirar sesion | `30` |
| `MAX_LOGIN_ATTEMPTS` | Intentos fallidos antes de bloqueo | `5` |
| `LOGIN_LOCKOUT_MINUTES` | Minutos de bloqueo tras intentos fallidos | `30` |
| `PASSWORD_MIN_LENGTH` | Longitud minima de contrasena | `8` |
| `PASSWORD_REQUIRE_UPPERCASE` | Requiere mayusculas | `true` |
| `PASSWORD_REQUIRE_LOWERCASE` | Requiere minusculas | `true` |
| `PASSWORD_REQUIRE_DIGIT` | Requiere digitos | `true` |
| `PASSWORD_REQUIRE_SPECIAL` | Requiere caracteres especiales | `true` |

---

## Flujo de Inicio

```
main() 
  └─> connect_db()          # Valida .env y abre conexion PostgreSQL
  └─> MainApplication()
        └─> LoginView + LoginPresenter
              └─> on_login_success(user)
                    └─> MainView (MDI)
                    └─> SessionManager.start()
                    └─> app.installEventFilter()  # Track mouse/keyboard activity
```

## Flujo de Sesion

```
Actividad de usuario  →  eventFilter  →  SessionManager.reset()
Inactividad (N min)   →  session_warning signal  →  muestra aviso en status bar
Inactividad total     →  session_expired signal  →  cierra MainView  →  LoginView
```

---

## Notas para Desarrolladores

- Los modelos retornan `tuple[bool, str | None]` para operaciones de escritura y `list[tuple]` para consultas. Los presenters deben desempaquetar correctamente.
- El `QueryHelper` centraliza toda interaccion con QSqlQuery. No usar QSqlQuery directamente en modelos.
- Para agregar un nuevo modulo: crear Model → Presenter → View → .ui file → registrar en `main_application.py`.
- El `GenericPresenter` + `EntityType` enum permite crear selectores de entidad sin duplicar codigo.
- Los archivos `.ui` de Qt Designer se cargan en runtime via `uic.loadUi()` en las vistas.
