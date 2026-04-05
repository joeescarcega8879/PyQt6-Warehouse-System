-- =============================================================================
-- PyQt6 Warehouse System — Schema DDL
-- =============================================================================
-- Descripcion : Crea la estructura completa de la base de datos desde cero.
-- Uso         : psql -h <host> -U <user> -d <dbname> -f schema.sql
-- Nota        : Este script asume una base de datos VACIA. Para limpiar una
--               base de datos existente, ejecuta primero reset_db.sql.
-- =============================================================================

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;

-- =============================================================================
-- TABLAS (en orden de dependencias — sin FKs primero)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- users
-- -----------------------------------------------------------------------------
CREATE TABLE public.users (
    user_id       SERIAL                      NOT NULL,
    username      CHARACTER VARYING(50)       NOT NULL,
    password_hash CHARACTER VARYING(255)      NOT NULL,
    full_name     CHARACTER VARYING(100),
    user_role     CHARACTER VARYING(20)       DEFAULT 'operator'::CHARACTER VARYING,
    is_active     BOOLEAN                     DEFAULT TRUE,
    created_at    TIMESTAMP WITH TIME ZONE    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey         PRIMARY KEY (user_id),
    CONSTRAINT users_username_key UNIQUE      (username),
    CONSTRAINT users_user_role_check CHECK (
        (user_role)::TEXT = ANY (
            ARRAY[
                'admin'::CHARACTER VARYING,
                'supervisor'::CHARACTER VARYING,
                'leader'::CHARACTER VARYING,
                'operator'::CHARACTER VARYING,
                'viewer'::CHARACTER VARYING
            ]::TEXT[]
        )
    )
);

-- -----------------------------------------------------------------------------
-- materials
-- -----------------------------------------------------------------------------
CREATE TABLE public.materials (
    material_id   SERIAL                  NOT NULL,
    material_name CHARACTER VARYING(255)  NOT NULL,
    description   TEXT,
    stock_quantity NUMERIC(10,2)          DEFAULT 0,
    unit_of_measure CHARACTER VARYING(50) NOT NULL,
    CONSTRAINT materials_pkey             PRIMARY KEY (material_id),
    CONSTRAINT materials_material_name_key UNIQUE (material_name),
    CONSTRAINT uq_material_name           UNIQUE (material_name),
    CONSTRAINT materials_stock_quantity_check CHECK (stock_quantity >= (0)::NUMERIC)
);

-- -----------------------------------------------------------------------------
-- production_lines
-- -----------------------------------------------------------------------------
CREATE TABLE public.production_lines (
    line_id     SERIAL                  NOT NULL,
    line_name   CHARACTER VARYING(100)  NOT NULL,
    description TEXT,
    is_active   BOOLEAN                 DEFAULT TRUE,
    CONSTRAINT production_lines_pkey          PRIMARY KEY (line_id),
    CONSTRAINT production_lines_line_name_key UNIQUE (line_name)
);

-- -----------------------------------------------------------------------------
-- suppliers  (FK -> users)
-- -----------------------------------------------------------------------------
CREATE TABLE public.suppliers (
    supplier_id         SERIAL                  NOT NULL,
    supplier_name       CHARACTER VARYING(255)  NOT NULL,
    contact_department  CHARACTER VARYING(255),
    phone               CHARACTER VARYING(50),
    email               CHARACTER VARYING(255),
    address             TEXT,
    notes               TEXT,
    created_by          INTEGER,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    is_active           BOOLEAN                 DEFAULT TRUE,
    CONSTRAINT suppliers_pkey              PRIMARY KEY (supplier_id),
    CONSTRAINT suppliers_supplier_name_key UNIQUE (supplier_name)
);

-- -----------------------------------------------------------------------------
-- supplier_receipts  (FK -> users, suppliers, materials)
-- -----------------------------------------------------------------------------
CREATE TABLE public.supplier_receipts (
    receipt_id         SERIAL                      NOT NULL,
    material_id        INTEGER                     NOT NULL,
    supplier_id        INTEGER                     NOT NULL,
    quantity_received  NUMERIC(10,2)               NOT NULL,
    receipt_timestamp  TIMESTAMP WITH TIME ZONE    DEFAULT CURRENT_TIMESTAMP,
    notes              TEXT,
    created_by         INTEGER,
    CONSTRAINT supplier_receipts_pkey                    PRIMARY KEY (receipt_id),
    CONSTRAINT supplier_receipts_quantity_received_check CHECK (quantity_received > (0)::NUMERIC)
);

-- -----------------------------------------------------------------------------
-- production_requests  (FK -> production_lines, users)
-- -----------------------------------------------------------------------------
CREATE TABLE public.production_requests (
    request_id   SERIAL                      NOT NULL,
    line_id      INTEGER                     NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE    DEFAULT CURRENT_TIMESTAMP,
    status       CHARACTER VARYING(20)       DEFAULT 'DRAFT'::CHARACTER VARYING,
    requested_by INTEGER,
    approved_by  INTEGER,
    approved_at  TIMESTAMP WITH TIME ZONE,
    is_active    BOOLEAN                     DEFAULT TRUE NOT NULL,
    CONSTRAINT production_requests_pkey PRIMARY KEY (request_id)
);

-- -----------------------------------------------------------------------------
-- production_request_items  (FK -> production_requests, materials)
-- -----------------------------------------------------------------------------
CREATE TABLE public.production_request_items (
    item_id    SERIAL          NOT NULL,
    request_id INTEGER         NOT NULL,
    material_id INTEGER        NOT NULL,
    quantity   NUMERIC(12,3)   NOT NULL,
    unit       CHARACTER VARYING(10) NOT NULL,
    CONSTRAINT production_request_items_pkey PRIMARY KEY (item_id)
);

-- -----------------------------------------------------------------------------
-- login_attempts
-- -----------------------------------------------------------------------------
CREATE TABLE public.login_attempts (
    id           SERIAL                          NOT NULL,
    username     CHARACTER VARYING(255)          NOT NULL,
    success      BOOLEAN                         DEFAULT FALSE NOT NULL,
    ip_address   CHARACTER VARYING(45)           DEFAULT 'unknown'::CHARACTER VARYING,
    attempt_time TIMESTAMP WITHOUT TIME ZONE     DEFAULT NOW() NOT NULL,
    CONSTRAINT login_attempts_pkey PRIMARY KEY (id)
);

COMMENT ON TABLE  public.login_attempts                IS 'Tracks login attempts for rate limiting and security monitoring';
COMMENT ON COLUMN public.login_attempts.username       IS 'Username that attempted to log in';
COMMENT ON COLUMN public.login_attempts.success        IS 'Whether the login attempt was successful';
COMMENT ON COLUMN public.login_attempts.ip_address     IS 'IP address of the login attempt (for audit purposes)';
COMMENT ON COLUMN public.login_attempts.attempt_time   IS 'Timestamp of the login attempt';

-- -----------------------------------------------------------------------------
-- audit_log  (FK -> users, pero se deja como referencia suave para no bloquear)
-- -----------------------------------------------------------------------------
CREATE TABLE public.audit_log (
    audit_id   BIGSERIAL                       NOT NULL,
    user_id    INTEGER                         NOT NULL,
    action     CHARACTER VARYING(64)           NOT NULL,
    entity     CHARACTER VARYING(64),
    entity_id  INTEGER,
    success    BOOLEAN                         NOT NULL,
    meta       JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE     DEFAULT NOW() NOT NULL,
    CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id)
);

-- =============================================================================
-- FOREIGN KEYS
-- =============================================================================

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT fk_suppliers_created_by
        FOREIGN KEY (created_by) REFERENCES public.users(user_id) ON DELETE SET NULL;

ALTER TABLE ONLY public.supplier_receipts
    ADD CONSTRAINT fk_supplier_receipts_supplier
        FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY public.supplier_receipts
    ADD CONSTRAINT fk_supplier_receipts_created_by
        FOREIGN KEY (created_by) REFERENCES public.users(user_id) ON DELETE SET NULL;

ALTER TABLE ONLY public.supplier_receipts
    ADD CONSTRAINT supplier_receipts_material_id_fkey
        FOREIGN KEY (material_id) REFERENCES public.materials(material_id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.production_requests
    ADD CONSTRAINT production_requests_line_id_fkey
        FOREIGN KEY (line_id) REFERENCES public.production_lines(line_id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.production_requests
    ADD CONSTRAINT production_requests_requested_by_fkey
        FOREIGN KEY (requested_by) REFERENCES public.users(user_id);

ALTER TABLE ONLY public.production_requests
    ADD CONSTRAINT production_requests_approved_by_fkey
        FOREIGN KEY (approved_by) REFERENCES public.users(user_id);

ALTER TABLE ONLY public.production_request_items
    ADD CONSTRAINT production_request_items_request_id_fkey
        FOREIGN KEY (request_id) REFERENCES public.production_requests(request_id) ON DELETE CASCADE;

ALTER TABLE ONLY public.production_request_items
    ADD CONSTRAINT production_request_items_material_id_fkey
        FOREIGN KEY (material_id) REFERENCES public.materials(material_id);

-- =============================================================================
-- INDICES
-- =============================================================================

-- login_attempts
CREATE INDEX idx_username_time  ON public.login_attempts  USING btree (username, attempt_time);
CREATE INDEX idx_attempt_time   ON public.login_attempts  USING btree (attempt_time);

-- audit_log
CREATE INDEX idx_audit_user     ON public.audit_log USING btree (user_id);
CREATE INDEX idx_audit_entity   ON public.audit_log USING btree (entity, entity_id);
CREATE INDEX idx_audit_action   ON public.audit_log USING btree (action);

-- suppliers
CREATE INDEX idx_suppliers_name         ON public.suppliers USING btree (supplier_name);
CREATE INDEX idx_suppliers_is_active    ON public.suppliers USING btree (is_active);
CREATE INDEX idx_suppliers_created_by   ON public.suppliers USING btree (created_by);

-- supplier_receipts
CREATE INDEX idx_supplier_receipts_supplier_id  ON public.supplier_receipts USING btree (supplier_id);
CREATE INDEX idx_supplier_receipts_created_by   ON public.supplier_receipts USING btree (created_by);

-- production_requests
CREATE INDEX idx_prod_req_line      ON public.production_requests       USING btree (line_id);
CREATE INDEX idx_prod_req_status    ON public.production_requests       USING btree (status);
CREATE INDEX idx_prod_req_items_req ON public.production_request_items  USING btree (request_id);

-- =============================================================================
-- FIN DEL SCHEMA
-- =============================================================================
