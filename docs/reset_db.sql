-- =============================================================================
-- PyQt6 Warehouse System — Reset de Base de Datos
-- =============================================================================
-- Descripcion : Elimina todas las tablas existentes y las recrea desde cero
--               aplicando el schema completo (schema.sql).
--
-- USO:
--   Solo reset (BD limpia, sin datos):
--     psql -h <host> -U <user> -d <dbname> -f reset_db.sql
--
--   Reset + datos de prueba:
--     psql -h <host> -U <user> -d <dbname> -f reset_db.sql
--     psql -h <host> -U <user> -d <dbname> -f seed_data.sql
--
-- ADVERTENCIA: Este script ELIMINA TODOS LOS DATOS irreversiblemente.
--              Ejecutar solo en entornos de desarrollo/pruebas.
-- =============================================================================

SET client_min_messages = warning;
SET client_encoding = 'UTF8';

-- =============================================================================
-- PASO 1: Eliminar tablas en orden inverso (respetando FK dependencies)
-- =============================================================================

DROP TABLE IF EXISTS public.audit_log                 CASCADE;
DROP TABLE IF EXISTS public.login_attempts            CASCADE;
DROP TABLE IF EXISTS public.production_request_items  CASCADE;
DROP TABLE IF EXISTS public.production_requests       CASCADE;
DROP TABLE IF EXISTS public.supplier_receipts         CASCADE;
DROP TABLE IF EXISTS public.suppliers                 CASCADE;
DROP TABLE IF EXISTS public.materials                 CASCADE;
DROP TABLE IF EXISTS public.production_lines          CASCADE;
DROP TABLE IF EXISTS public.users                     CASCADE;

-- =============================================================================
-- PASO 2: Eliminar sequences huerfanas (si quedaron despues del DROP CASCADE)
-- =============================================================================

DROP SEQUENCE IF EXISTS public.audit_log_audit_id_seq                  CASCADE;
DROP SEQUENCE IF EXISTS public.login_attempts_id_seq                   CASCADE;
DROP SEQUENCE IF EXISTS public.materials_material_id_seq               CASCADE;
DROP SEQUENCE IF EXISTS public.production_lines_line_id_seq            CASCADE;
DROP SEQUENCE IF EXISTS public.production_request_items_item_id_seq    CASCADE;
DROP SEQUENCE IF EXISTS public.production_requests_request_id_seq      CASCADE;
DROP SEQUENCE IF EXISTS public.supplier_receipts_receipt_id_seq        CASCADE;
DROP SEQUENCE IF EXISTS public.suppliers_supplier_id_seq               CASCADE;
DROP SEQUENCE IF EXISTS public.users_user_id_seq                       CASCADE;

-- =============================================================================
-- PASO 3: Recrear toda la estructura limpia
-- =============================================================================

\i schema.sql

-- =============================================================================
-- FIN DEL RESET
-- =============================================================================

\echo ''
\echo '>>> Reset completado exitosamente.'
\echo '>>> Para cargar datos de prueba ejecuta:'
\echo '>>>   psql -h <host> -U <user> -d <dbname> -f seed_data.sql'
\echo ''
