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
│   │   ├── base_presenter.py    # Patron base: status, busqueda, edit-mode, validaciones
│   │   ├── login_presenter.py   # Autenticacion + rate limiting
│   │   ├── main_presenter.py    # Navegacion principal + permisos de menu
│   │   ├── material_presenter.py          # Logica de materiales
│   │   ├── user_presenter.py              # Logica de usuarios
│   │   ├── production_line_presenter.py   # Logica de lineas de produccion
│   │   ├── supplier_presenter.py          # Logica de proveedores
│   │   ├── supplier_receipt_presenter.py  # Logica de recepciones
│   │   ├── change_password_presenter.py   # Cambio de contrasena (hereda BasePresenter)
│   │   ├── production_request_presenter.py # Logica de ordenes de produccion (parcial)
│   │   └── generic_presenter.py           # Selector generico de entidades
│   │
│   ├── views/                   # Capa de UI (PyQt6 Widgets)
│   │   ├── login_view.py        # Pantalla de login
│   │   ├── main_view.py         # Ventana principal MDI con panel lateral scrollable
│   │   ├── material_view.py     # Formulario de materiales
│   │   ├── user_view.py         # Formulario de usuarios
│   │   ├── line_view.py         # Formulario de lineas de produccion
│   │   ├── supplier_view.py     # Formulario de proveedores
│   │   ├── receipt_view.py      # Formulario de recepciones
│   │   ├── production_request_view.py  # Formulario de ordenes de produccion (parcial)
│   │   ├── change_password_view.py     # Dialog de cambio de contrasena
│   │   ├── generic_view.py      # Vista selector generica (dialog)
│   │   └── ui/                  # Archivos .ui de Qt Designer
│   │       ├── login_view.ui
│   │       ├── main_view.ui
│   │       ├── material_view.ui
│   │       ├── user_view.ui
│   │       ├── line_view.ui
│   │       ├── supplier_view.ui
│   │       ├── receipt_view.ui
│   │       ├── production_request_view.ui
│   │       ├── change_password.ui
│   │       └── generic_view.ui
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
│   │   ├── format.py            # Helpers de formateo de datos (FormatComponents)
│   │   ├── model_adapter.py     # Adaptador de tuples de modelo a QStandardItemModel
│   │   └── entity_config.py     # Configuracion generica de entidades (EntityType enum)
│   │
│   ├── database/                # Capa de acceso a datos
│   │   ├── connection.py        # Conexion PostgreSQL via QSqlDatabase
│   │   ├── query_helper.py      # Wrapper de QSqlQuery (fetch_all, fetch_one, execute)
│   │   └── migrations/
│   │       ├── README.md
│   │       ├── 001_create_login_attempts.sql
│   │       └── 002_refactor_supplier_receipts.sql
│   │
│   ├── assets/                  # Recursos estaticos
│   │   ├── styles.css           # Estilos globales QSS — tema oscuro gris neutro
│   │   └── icons/               # Iconos de la aplicacion (PNG)
│   │                            # Pendiente: IMG-Settings.png
│   │
│   └── config/                  # Configuracion de la aplicacion
│       ├── settings.py          # DatabaseConfig / AppConfig / SecurityConfig (dotenv)
│       └── logger_config.py     # Configuracion de logging con rotacion de archivos
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
├── logs/                        # Logs rotativos por fecha (app_YYYYMMDD.log)
│
├── docs/                        # Archivos SQL de base de datos
│   ├── schema.sql               # DDL completo — crea toda la estructura desde cero
│   ├── reset_db.sql             # DROP + schema.sql — limpieza para desarrollo/pruebas
│   └── seed_data.sql            # Datos de prueba idempotentes (ON CONFLICT DO NOTHING)
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

### Jerarquia de Presenters

Todos los presenters de modulo heredan de `BasePresenter`:

```
BasePresenter
├── MaterialPresenter
├── UserPresenter
├── ProductionLinePresenter
├── SupplierPresenter
├── SupplierReceiptPresenter
├── ChangePasswordPresenter
├── ProductionRequestPresenter
├── GenericPresenter
├── LoginPresenter
└── MainPresenter
```

`BasePresenter` provee: `_emit_error`, `_emit_success`, `_enter_edit_mode`, `_exit_edit_mode`,
`_clear_form_and_reset_state`, `_load_user_information_to_view`, `_handle_search_with_id_and_name`,
`_validate_required_field`, `_validate_required_fields`. El ID de la entidad en edicion se
almacena siempre en `_current_entity_id` (no en variables especificas por modulo).

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
- [x] Listado con tabla
- [x] Busqueda por ID (numerico) y por nombre (ILIKE)
- [x] Crear material (nombre, descripcion, unidad)
- [x] Editar material seleccionado
- [x] Eliminar material seleccionado
- [x] Auditoria de create / edit / delete

### Modulo Proveedores
- [x] Listado con tabla
- [x] Busqueda por ID y por nombre
- [x] Crear proveedor (nombre, departamento, telefono, email, direccion, notas)
- [x] Editar proveedor (incluye activar/desactivar via campo `is_active`)
- [x] Eliminar proveedor — **decision de diseno: no aplica**. El alta/baja se gestiona mediante `is_active`
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
- [ ] Cambio de contrasena — el usuario comun NO puede cambiar su propia contrasena desde la UI; debe solicitarlo a un `admin` o `supervisor`, quienes pueden resetear la contrasena de cualquier usuario seleccionado
- [x] Auditoria de create / edit / password change

### Modulo Ordenes de Produccion — Vista
- [x] Archivo `.ui` (`production_request_view.ui`) con layout completo
- [x] Signals declarados: `save_requested`, `submit_requested`, `approve_requested`, `reject_requested`, `deactivate_requested`, `cancel_requested`, `close_requested`, `selected_line`, `selected_material`, `add_item_requested`, `remove_item_requested`
- [x] `btn_save`, `btn_cancel`, `btn_close`, `btn_select_line`, `btn_select_material`, `btn_add_item`, `btn_remove_item` conectados
- [x] `display_selected_material(material)` y `display_selected_line(line)` implementados
- [x] `get_selected_material_and_line_info()` — retorna dict con `material_id`, `line_id`, `quantity` (None si vacio), `unit`
- [x] `display_added_item(item)` — agrega fila a `tableItems` eficientemente (solo la fila nueva)
- [x] `tableItems` configurado con 4 columnas: Line ID, Material ID, Quantity, Unit
- [x] `self.material_id`, `self.line_id`, `self.items` inicializados en `__init__`
- [x] `get_index_from_selected_item()` — retorna indice de fila seleccionada en `tableItems`
- [x] `remove_item_from_table(index)` — elimina fila de `tableItems` y del lista `items`
- [x] `load_user_information(user_info)` — muestra nombre y rol en `label_user_name` / `label_user_role`
- [ ] `btn_submit`, `btn_approve`, `btn_reject`, `btn_deactivate` — comentados, sin conectar (lineas 51–54)
- [ ] `clear_form()` — parcial: limpia inputs pero NO resetea `material_id`, `line_id`, `items` ni `tableItems`
- [ ] `get_form_data()` — pendiente (retornar `line_id` e `items` para el presenter)
- [ ] `load_requests(requests)` — pendiente (poblar `tableWidget` con lista de ordenes)
- [ ] `get_selected_request_data()` — pendiente (leer fila seleccionada de `tableWidget`)
- [ ] `enable_submit(v)`, `enable_approve_reject(v)`, `enable_deactivate(v)` — pendientes (para `_apply_permissions`)

### Modulo Ordenes de Produccion — Presenter
- [x] Clase `ProductionRequestPresenter` creada, hereda `BasePresenter`
- [x] Registrado en `main_application.py` — `open_request_form()` implementado
- [x] `_connect_signals()` — conecta `selected_material`, `selected_line`, `add_item_requested`, `remove_item_requested`
- [x] `_handling_selected_material()` — verifica permiso, abre GenericView para material
- [x] `_handling_selected_line()` — verifica permiso, abre GenericView para linea
- [x] `_on_selected_material()` — callback de GenericView: guarda en `_selected_material` y llama `display_selected_material`
- [x] `_on_selected_line()` — callback de GenericView: guarda en `_selected_line` y llama `display_selected_line`
- [x] `_on_add_item_requested()` — verifica permiso, lee datos de view, valida, llama `display_added_item`
- [x] `_on_remove_item_requested()` — verifica permiso, obtiene indice seleccionado, llama `remove_item_from_table`
- [x] `_selected_material` y `_selected_line` como atributos de estado (`dict | None`) — correctamente asignados en callbacks
- [x] `_clear_form()` — resetea `_selected_material`, `_selected_line` y llama `view.clear_form()`
- [x] `_load_user_information_to_view()` — llamado en `__init__`
- [ ] `_connect_signals()` — faltan: `save_requested`, `cancel_requested`, `submit_requested`, `approve_requested`, `reject_requested`, `deactivate_requested`
- [ ] `_load_init_data()` — pendiente (cargar lista de ordenes al abrir el formulario)
- [ ] `_handle_save()` — pendiente (crear DRAFT con items; retorno del modelo es `tuple[bool, str|None, int|None]`)
- [ ] `_handle_submit()` — pendiente (DRAFT → SUBMITTED)
- [ ] `_handle_approve()` — pendiente (SUBMITTED → APPROVED con `approved_by`)
- [ ] `_handle_reject()` — pendiente (SUBMITTED → REJECTED)
- [ ] `_handle_deactivate()` — pendiente (confirmacion + marcar `is_active = FALSE`)
- [ ] `_handle_cancel()` — pendiente (limpiar form + `_exit_edit_mode`)
- [ ] `_apply_permissions()` — pendiente (ocultar botones segun rol via `enable_*` en la vista)

### Modulo Ordenes de Produccion — Modelo
- [x] `create_request` (con items, transaccion atomica) — completo
- [x] `update_status_request` (DRAFT → SUBMITTED → APPROVED / REJECTED / CANCELLED) — completo
- [x] `deactivate_request` — completo
- [x] `get_all_requests` / `get_request_by_id` — completos

### Selector Generico
- [x] Dialog reutilizable para seleccionar Material, Proveedor o Linea de Produccion
- [x] Configuracion via `EntityType` enum (columnas, metodos, campo ID/nombre)
- [x] Signal `item_selected` al confirmar seleccion

### Auditoria
- [x] Modelo de auditoria con escritura a BD
- [x] Definiciones de eventos auditables (`AuditDefinition`) — completas para todos los modulos
- [x] Integrado en presenters de: materiales, usuarios, lineas, recepciones, proveedores
- [x] Eventos de production requests: CREATED, EDITED, SUBMITTED, APPROVED, REJECTED, CANCELED, VIEWED, DEACTIVATED, DENIED
- [x] Evento generico `GENERIC_ENTITY_DENIED` para accesos denegados reutilizable
- [ ] Auditoria de production requests integrada en presenter (pendiente junto con handlers)

### Permisos — Production Requests
- [x] `PRODUCTION_REQUESTS_VIEW` — ADMIN, SUPERVISOR, LEADER, VIEWER
- [x] `PRODUCTION_REQUESTS_CREATE` — ADMIN, SUPERVISOR, LEADER
- [x] `PRODUCTION_REQUESTS_EDIT` — ADMIN, SUPERVISOR, LEADER
- [x] `PRODUCTION_REQUESTS_SUBMIT` — ADMIN, SUPERVISOR, LEADER
- [x] `PRODUCTION_REQUESTS_APPROVE` — ADMIN, SUPERVISOR (cubre tambien REJECT)
- [x] `PRODUCTION_REQUESTS_DEACTIVATE` — ADMIN, SUPERVISOR

### Infraestructura
- [x] Conexion PostgreSQL via `QSqlDatabase` (QPSQL driver)
- [x] `QueryHelper`: wrapper de QSqlQuery con `fetch_all`, `fetch_one`, `execute`, transacciones
- [x] Configuracion via `.env` (dotenv) con validacion al inicio
- [x] Logging rotativo por fecha (`logs/app_YYYYMMDD.log`)
- [x] Estilos globales QSS cargados desde `src/assets/styles.css`
- [x] `StatusBarController`: mensajes de estado coloreados (SUCCESS / ERROR / WARNING)
- [x] MDI: cada formulario abre como `QMdiSubWindow`

### UI — Tema Visual
- [x] Tema oscuro gris neutro (`#2d2d2d` base, `#383838` surface, `#4a9eff` acento azul acero)
- [x] Botones flat con borde sutil — semantica por color (primario, peligro, positivo, advertencia)
- [x] `btn_save` / `btn_login` — azul acero solido (accion principal)
- [x] `btn_approve` / `btn_submit` — verde sutil
- [x] `btn_reject` — ambar
- [x] `btn_delete` / `btn_deactivate` — rojo sutil
- [x] Status bar coherente con el tema: SUCCESS verde oscuro, ERROR rojo oscuro, WARNING ambar oscuro
- [x] Scrollbars delgadas (8px) estilo moderno

### UI — Panel Lateral (main_view)
- [x] Panel lateral con `QScrollArea` — scroll vertical aparece automaticamente si hay overflow
- [x] Scroll horizontal desactivado siempre
- [x] `btn_toggle` fuera del scroll — siempre visible al colapsar/expandir
- [x] Botones organizados en 3 categorias con labels: **Produccion**, **Almacen**, **Administracion**
- [x] Labels de categoria se ocultan al colapsar el panel (modo icono)
- [x] `btn_settings` agregado en categoria Administracion con signal `form_settings_signal`
- [x] Toggle refactorizado con `_BUTTON_LABELS` y `_CATEGORY_LABELS` (DRY, sin repeticion)
- [x] Estilos CSS para labels de categoria (gris oscuro, 8pt, letra espaciada)
- [x] Color del `QMdiArea` actualizado a `#2d2d2d` coherente con el tema oscuro
- [ ] Vista/Presenter de Settings — pendiente (signal declarado, no conectado en `main_application.py`)
- [ ] Icono `IMG-Settings.png` — pendiente de agregar en `src/assets/icons/`

---

## Funcionalidades Pendientes / Incompletas

### Fase 1 — Production Requests (completar modulo)

#### Vista (`production_request_view.py`)
- [ ] **V1** Descomentar y corregir conexiones de `btn_submit`, `btn_approve`, `btn_reject`, `btn_deactivate` (lineas 51–54) — cambiar por `clicked.connect(signal.emit)` directo
- [ ] **V2** Completar `clear_form()` — agregar reset de `self.material_id = None`, `self.line_id = None`, `self.items = []`, `self.tableItems.setRowCount(0)`
- [ ] **V3** Agregar `get_form_data()` — retorna `{"line_id": self.line_id, "items": self.items}`
- [ ] **V4** Agregar `load_requests(requests)` — pobla `tableWidget` con la lista de ordenes via `FormatComponents`
- [ ] **V5** Agregar `get_selected_request_data()` — lee fila seleccionada de `tableWidget`, retorna dict con `request_id` y `status`
- [ ] **V6** Agregar `enable_submit(v)`, `enable_approve_reject(v)`, `enable_deactivate(v)` — para `_apply_permissions()` del presenter

#### Presenter (`production_request_presenter.py`)
- [ ] **P1** Completar `_connect_signals()` — agregar `save_requested`, `cancel_requested`, `submit_requested`, `approve_requested`, `reject_requested`, `deactivate_requested`
- [ ] **P2** Agregar `_load_init_data()` — llama `ProductionRequestModel.get_all_requests()`, pasa resultado a `view.load_requests()`
- [ ] **P3** Agregar `_handle_cancel()` — llama `_clear_form()` y `_exit_edit_mode()`
- [ ] **P4** Agregar `_apply_permissions()` — 3 checks de permiso → llama `enable_submit()`, `enable_approve_reject()`, `enable_deactivate()` en la vista
- [ ] **P5** Agregar `_handle_save()` — valida `line_id` e `items` no vacios, construye payload desde `view.items` (cada item ya tiene `unit`), llama `model.create_request()` desempacando **3 valores** `(success, error, request_id)`, audita `PRODUCTION_REQUESTS_CREATED`
- [ ] **P6** Agregar `_handle_submit()` — obtiene seleccion via `get_selected_request_data()`, llama `model.update_status_request(id, "SUBMITTED")`, audita `PRODUCTION_REQUESTS_SUBMITTED`
- [ ] **P7** Agregar `_handle_approve()` — igual que P6 con `"APPROVED"` y `approved_by=self.current_user.id`, audita `PRODUCTION_REQUESTS_APPROVED`
- [ ] **P8** Agregar `_handle_reject()` — igual que P6 con `"REJECTED"`, audita `PRODUCTION_REQUESTS_REJECTED`
- [ ] **P9** Agregar `_handle_deactivate()` — `QMessageBox` de confirmacion + `model.deactivate_request(id)`, audita `PRODUCTION_REQUESTS_DEACTIVATED`

#### Dominio (`permissions.py`)
- [ ] **D1** Agregar `UserRole.OPERATOR` a `PRODUCTION_REQUESTS_VIEW` (linea 13) — solo VIEW, sin CREATE ni ninguna otra accion

### Fase 2 — Inventario Real

> El campo `stock_quantity` existe en la tabla `materials` pero ningun modelo lo lee ni lo escribe.
> Las recepciones y las ordenes aprobadas no tienen impacto en el stock. No existe tabla de movimientos.

- [ ] **I1** Migracion SQL `003_inventory.sql` — agregar `min_stock NUMERIC(10,2) DEFAULT 0` a `materials`, agregar `category VARCHAR(100)` a `materials`, crear tabla `inventory_movements` (tipo ENTRY/EXIT, `material_id`, `quantity`, `reference_id`, `reference_type`, `created_by`, `created_at`)
- [ ] **I2** Conectar recepciones → stock — al guardar una recepcion: `stock_quantity += quantity_received` en `materials` y registrar fila en `inventory_movements` (tipo ENTRY, `reference_id = receipt_id`)
- [ ] **I3** Conectar production requests → stock — al aprobar una orden: `stock_quantity -= quantity` por cada item en `production_request_items`, con validacion de stock suficiente antes de aprobar, y registro en `inventory_movements` (tipo EXIT, `reference_id = request_id`)
- [ ] **I4** Mostrar `stock_quantity` en la vista de materiales — agregar columna en `MaterialModel.COLUMNS`, mostrarla en la tabla, resaltar en rojo si `stock_quantity < min_stock`

### Fase 3 — Reportes

- [ ] **R1** Reporte de stock actual — tabla con todos los materiales, stock actual, minimo, y alerta visual; exportable a PDF
- [ ] **R2** Reporte de movimientos por periodo — filtro por fecha inicio/fin, lista de entradas y salidas con referencia; exportable a PDF
- [ ] **R3** Reporte de recepciones por proveedor — agrupado por proveedor con totales por material

### Fase 4 — Pulido para Venta

- [ ] **Q1** Categorias de materiales — agregar filtro por `category` en la vista de materiales (depende de I1)
- [ ] **Q2** Dashboard con KPIs en pantalla principal — stock total valorizado, movimientos del dia, ordenes pendientes de aprobacion
- [ ] **Q3** Exportacion a Excel de cualquier tabla (materiales, recepciones, ordenes)
- [ ] **Q4** Empaquetado con Docker — `Dockerfile` + `docker-compose.yml` con PostgreSQL + app para instalacion limpia en cliente

### Pendientes Existentes (sin cambio de prioridad)

#### Modulo Settings
- [ ] Vista de configuracion — pendiente de crear (View + Presenter + `.ui`)
- [ ] Selector de tema (dark/light) con recarga de estilos en caliente via `StyleManager`
- [ ] Registrar `open_settings_form()` en `main_application.py`
- [ ] Icono `IMG-Settings.png` pendiente en `src/assets/icons/`

#### Modulo Recepciones
- [ ] Eliminar recepcion — metodo en modelo existe pero sin boton ni handler en vista/presenter

#### Modulo Usuarios
- [ ] Cambio de contrasena — el usuario comun NO puede cambiar su propia contrasena desde la UI; debe solicitarlo a un `admin` o `supervisor`, quienes pueden resetear la contrasena de cualquier usuario seleccionado

#### Pruebas
- [ ] Tests de presenters (ningun presenter tiene cobertura de tests)
- [ ] Tests de vistas
- [ ] Tests de integracion (carpeta `tests/integration/` existe pero vacia)
- [ ] Tests para `ProductionRequestModel`
- [ ] Tests para `SupplierReceiptModel`
- [ ] Tests para `ProductionLineModel`

---

## Bugs Resueltos (historial)

- [x] Typo `_conect_signals` (una `n`) en `ProductionRequestPresenter` — corregido a `_connect_signals`
- [x] `handling_selected_material` sin prefijo `_` — corregido a `_handling_selected_material`
- [x] Audit log de permiso denegado usaba `PRODUCTION_REQUESTS_CREATED` — corregido a `PRODUCTION_REQUESTS_DENIED`
- [x] `AuditDefinition` con nombres inconsistentes (`REQUEST` singular vs `REQUESTS` plural) — corregidos a plural
- [x] `PRODUCTION_REQUESTS_CANCELED` alineado a `canceled` (string value) — consistente con el resto
- [x] `SUPPLIER_*` corregidos a `SUPPLIERS_*` (plural) y agregado `SUPPLIERS_DELETED`
- [x] `PRODUCTION_REQUESTS_SUBMIT` y `PRODUCTION_REQUESTS_EDIT` sin roles en `permissions.py` — corregido
- [x] `tableItems` sin columnas configuradas — corregido con `setColumnCount(4)` en `initialize_components` (4 columnas: Line ID, Material ID, Quantity, Unit)
- [x] `display_added_item` repintaba toda la tabla en cada item — refactorizado para agregar solo la fila nueva
- [x] `getattr` innecesario en `get_selected_material_and_line_info` — simplificado a acceso directo
- [x] `quantity` retornaba `"N/A"` en lugar de `None` cuando el campo estaba vacio — corregido a `None`
- [x] `_on_selected_material` y `_on_selected_line` no asignaban estado al presenter — corregido, ahora guardan en `self._selected_material` y `self._selected_line`
- [x] `btn_remove_item` no estaba conectado en la vista — corregido, conectado a `remove_item_requested.emit` (linea 64)
- [x] `self.items` no se inicializaba en `__init__` — corregido, `self.items: list[dict] = []` en linea 36
- [x] `get_index_from_selected_item` y `remove_item_from_table` faltaban en la vista — implementados (lineas 84–97)

---

## Mejoras de Arquitectura Aplicadas

- [x] Todos los presenters de modulo migrados a `BasePresenter` — incluido `ChangePasswordPresenter` y `ProductionRequestPresenter`
- [x] Variable `_current_entity_id` unificada en todos los presenters
- [x] `python-dotenv` en `requirements.txt` (version 1.1.0)
- [x] `schema.sql` creado con DDL completo del esquema
- [x] `reset_db.sql` creado para limpieza y recreacion de BD en desarrollo/pruebas
- [x] Migracion `002_refactor_supplier_receipts.sql` documentada en `src/database/migrations/README.md`
- [x] Toggle del panel lateral refactorizado con diccionarios (DRY) en lugar de lineas repetidas
- [x] Permiso `PRODUCTION_REQUESTS_DEACTIVATE` agregado con roles ADMIN, SUPERVISOR
- [x] Evento `GENERIC_ENTITY_DENIED` en `AuditDefinition` para accesos denegados reutilizables
- [x] `tableItems` actualizado a 4 columnas (Line ID, Material ID, Quantity, Unit) — unit heredado del material seleccionado
- [x] `_on_selected_material` y `_on_selected_line` en el presenter ahora guardan estado en `_selected_material` / `_selected_line` correctamente

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

## Flujo de Estados — Ordenes de Produccion

```
DRAFT  ──submit──>  SUBMITTED  ──approve──>  APPROVED
                        │
                        └──reject──>   REJECTED
DRAFT / SUBMITTED / APPROVED  ──deactivate──>  is_active = FALSE
Cualquier estado               ──cancelled──>  CANCELLED
```

---

## Notas para Desarrolladores

- Los modelos retornan `tuple[bool, str | None]` para operaciones de escritura y `list[tuple]` para consultas. Los presenters deben desempaquetar correctamente.
- El `QueryHelper` centraliza toda interaccion con QSqlQuery. No usar QSqlQuery directamente en modelos.
- Para agregar un nuevo modulo: crear Model → Presenter → View → `.ui` → registrar en `main_application.py`.
- El `GenericPresenter` + `EntityType` enum permite crear selectores de entidad sin duplicar codigo.
- Los archivos `.ui` de Qt Designer se cargan en runtime via `uic.loadUi()` en las vistas. La ruta se construye con `Path(__file__).resolve().parent / "ui" / "nombre.ui"`.
- Todos los presenters de modulo deben heredar `BasePresenter` y usar `_current_entity_id` para almacenar el ID de la entidad en edicion.
- Los iconos de la aplicacion viven en `src/assets/icons/`. El helper `_icon(filename)` disponible en cada vista construye el `QIcon` con la ruta correcta.
- Para agregar un nuevo boton al panel lateral: agregarlo en `main_view.ui` dentro de `scroll_content`, declarar su signal en `MainView`, agregarlo a `_BUTTON_LABELS` en `main_view.py` y conectarlo en `initializeComponents`.
- Para agregar una nueva categoria al panel lateral: agregar un `QLabel` con `objectName` `lbl_cat_<nombre>` en el `.ui` y registrarlo en `_CATEGORY_LABELS` en `main_view.py`.
- El tema visual se carga desde `src/assets/styles.css` via `StyleManager`. Para cambiar el tema en caliente recargar el stylesheet con `StyleManager.load_global_styles()` + `StyleManager.apply_to_app(app)`.

---

## Datos de Prueba y Reseteo de BD

### Reseteo completo (limpia todo y recarga estructura)

```bash
# Solo estructura limpia (sin datos)
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/reset_db.sql

# Estructura + datos de prueba
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/reset_db.sql
psql -h localhost -U <DB_USER> -d <DB_NAME> -f docs/seed_data.sql
```

### Archivos SQL en la carpeta docs/

| Archivo | Proposito |
|---|---|
| `docs/schema.sql` | DDL completo — crea todas las tablas, sequences, constraints e indices desde cero |
| `docs/reset_db.sql` | DROP CASCADE de todas las tablas + `\i schema.sql` — uso en desarrollo/pruebas |
| `docs/seed_data.sql` | Datos de prueba idempotentes (`ON CONFLICT DO NOTHING`) |

### Contenido del seed

Script SQL idempotente. Cada seccion termina con `SELECT setval(...)` para sincronizar las secuencias seriales.

| Tabla | Registros | Detalle |
|---|---|---|
| `users` | 15 | 1 admin, 3 supervisors, 4 leaders, 4 operators, 3 viewers. `viewer_iris` inactiva. |
| `materials` | 50 | Metales, tornilleria, pinturas, electricos, tuberias, lubricantes, soldadura, instrumentacion, EPP, herramientas y empaque. |
| `production_lines` | 8 | Lineas A–E y G–H activas. Linea F (Mantenimiento) inactiva. |
| `suppliers` | 20 | Proveedores mexicanos con diversidad geografica. 2 inactivos. |
| `supplier_receipts` | 80 | Distribuidas en los ultimos 90 dias. |
| `production_requests` | 35 | Mix de DRAFT/SUBMITTED/APPROVED/REJECTED/CANCELLED. 2 desactivadas (is_active=FALSE). |
| `production_request_items` | 76 | 2–3 items por orden en promedio, referenciando materiales reales. |

**Contrasena de todos los usuarios:** `Admin1234!`

### Notas tecnicas del seed
- `users`: `ON CONFLICT (username) DO NOTHING`
- `materials`: `ON CONFLICT (material_name) DO NOTHING`
- `production_lines`: `ON CONFLICT (line_name) DO NOTHING`
- `suppliers`: `ON CONFLICT (supplier_name) DO NOTHING`
- `supplier_receipts`: `ON CONFLICT (receipt_id) DO NOTHING` (PK serial)
- `production_requests`: `ON CONFLICT (request_id) DO NOTHING` (PK serial)
- `production_request_items`: `ON CONFLICT (item_id) DO NOTHING` (PK serial `item_id`)
