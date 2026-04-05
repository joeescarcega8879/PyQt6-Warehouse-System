-- =============================================================================
-- seed_data.sql
-- Datos de prueba para el sistema de almacen (PyQt6 Warehouse System)
-- Estrategia: ON CONFLICT DO NOTHING — idempotente, no sobreescribe datos existentes.
-- Contrasena de todos los usuarios: Admin1234!
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. USERS
--    Columnas: user_id, username, password_hash, full_name, user_role, is_active
--    Roles validos: admin, supervisor, leader, operator, viewer
-- -----------------------------------------------------------------------------
INSERT INTO users (user_id, username, password_hash, full_name, user_role, is_active) VALUES
  (1,  'admin',          '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'System Administrator',  'admin',      TRUE),
  (2,  'supervisor_ana', '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Ana Martinez',          'supervisor', TRUE),
  (3,  'supervisor_bob', '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Bob Ramirez',           'supervisor', TRUE),
  (4,  'leader_carlos',  '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Carlos Herrera',        'leader',     TRUE),
  (5,  'leader_diana',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Diana Lopez',           'leader',     TRUE),
  (6,  'leader_edgar',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Edgar Fuentes',         'leader',     TRUE),
  (7,  'operator_fanny', '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Fanny Torres',          'operator',   TRUE),
  (8,  'operator_gil',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Gil Mendoza',           'operator',   TRUE),
  (9,  'viewer_hector',  '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Hector Navarro',        'viewer',     TRUE),
  (10, 'viewer_iris',    '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Iris Castillo',         'viewer',     FALSE)
ON CONFLICT (username) DO NOTHING;

-- Sync sequence so next INSERT auto-assigns correct IDs
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));

-- -----------------------------------------------------------------------------
-- 2. MATERIALS
--    Columnas: material_id, material_name, description, unit_of_measure
-- -----------------------------------------------------------------------------
INSERT INTO materials (material_id, material_name, description, unit_of_measure) VALUES
  (1,  'Acero laminado en frio',     'Lamina de acero para estructuras',         'kg'),
  (2,  'Tornillo hexagonal M8',       'Tornillo de acero inoxidable M8x25mm',     'pza'),
  (3,  'Pintura epoxica gris',        'Pintura anticorrosiva para metal',          'lt'),
  (4,  'Cable electrico AWG 12',      'Cable de cobre calibre 12',                'm'),
  (5,  'Tubo PVC 2 pulgadas',         'Tubo rigido de PVC para instalaciones',    'm'),
  (6,  'Resina poliester',            'Resina para recubrimientos industriales',   'kg'),
  (7,  'Lubricante industrial',       'Aceite lubricante para maquinaria',         'lt'),
  (8,  'Filtro de aire HEPA',         'Filtro de alta eficiencia para polvo',      'pza'),
  (9,  'Banda transportadora',        'Banda de hule para lineas de produccion',   'm'),
  (10, 'Rodamiento SKF 6205',         'Rodamiento de bolas de precision',          'pza'),
  (11, 'Placa de aluminio 3mm',       'Placa de aluminio serie 6061',              'kg'),
  (12, 'Soldadura MIG ER70S-6',       'Alambre de soldadura MIG 0.9mm',            'kg'),
  (13, 'Silicona industrial RTV',     'Sellador de alta temperatura',              'pza'),
  (14, 'Compresor de aire 50L',       'Compresor de pistones 2HP',                 'pza'),
  (15, 'Broca HSS 10mm',              'Broca de acero rapido para metal',          'pza'),
  (16, 'Cinta aislante 3M',           'Cinta de vinilo para instalaciones',        'rollo'),
  (17, 'Valvula de bola 1/2"',        'Valvula de cierre rapido acero inox',       'pza'),
  (18, 'Sensor de temperatura PT100', 'Sonda RTD para medicion industrial',        'pza'),
  (19, 'Guante de nitrilo talla M',   'Guante desechable para manejo quimico',     'par'),
  (20, 'Casco de seguridad ABS',      'Casco con suspension de 4 puntos',          'pza')
ON CONFLICT (material_name) DO NOTHING;

-- Sync sequence
SELECT setval('materials_material_id_seq', (SELECT MAX(material_id) FROM materials));

-- -----------------------------------------------------------------------------
-- 3. PRODUCTION LINES
--    Columnas: line_id, line_name, description, is_active
-- -----------------------------------------------------------------------------
INSERT INTO production_lines (line_id, line_name, description, is_active) VALUES
  (1, 'Linea A - Ensamble',        'Linea principal de ensamble de componentes',   TRUE),
  (2, 'Linea B - Pintura',         'Linea de aplicacion de recubrimientos',         TRUE),
  (3, 'Linea C - Soldadura',       'Linea de soldadura MIG/TIG',                    TRUE),
  (4, 'Linea D - Empaque',         'Linea de empaque y etiquetado',                 TRUE),
  (5, 'Linea E - Control Calidad', 'Inspeccion y control de calidad final',         TRUE),
  (6, 'Linea F - Mantenimiento',   'Linea de mantenimiento preventivo (inactiva)',  FALSE)
ON CONFLICT (line_name) DO NOTHING;

-- Sync sequence
SELECT setval('production_lines_line_id_seq', (SELECT MAX(line_id) FROM production_lines));

-- -----------------------------------------------------------------------------
-- 4. SUPPLIERS
--    Columnas: supplier_id, supplier_name, contact_department, phone, email,
--              address, notes, is_active, created_by
--    FK: created_by -> users(user_id)
-- -----------------------------------------------------------------------------
INSERT INTO suppliers (supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active, created_by) VALUES
  (1,  'Aceros del Norte S.A.',     'Compras',            '811-555-0101', 'ventas@acerosnorte.mx',       'Av. Industrial 100, Monterrey',     'Proveedor principal de lamina',           TRUE,  1),
  (2,  'Ferreteria Central',        'Atencion a Clientes','55-5555-0202', 'pedidos@ferreteriacentral.mx','Calle 5 de Mayo 45, CDMX',          'Tornilleria y herrajes en general',       TRUE,  1),
  (3,  'Pinturas Industriales MX',  'Ventas',             '33-5555-0303', 'info@pinturasmx.com',         'Blvd. Tecnologico 200, Guadalajara','Especialistas en pinturas epoxicas',      TRUE,  2),
  (4,  'Electricos Profesionales',  'Ventas',             '55-5555-0404', 'ventas@electricos.mx',        'Norte 45 No.100, CDMX',             'Cables y materiales electricos',          TRUE,  2),
  (5,  'Plasticos y Tubos SA',      'Exportaciones',      '664-555-0505', 'export@plasticostubos.com',   'Zona Industrial Tijuana Local 12',  'PVC y polietileno',                       TRUE,  1),
  (6,  'Lubricantes Premier',       'Distribucion',       '81-5555-0606', 'dist@lubricantespremier.mx',  'Parque Industrial MTY Nave 8',      'Lubricantes y aceites industriales',      TRUE,  3),
  (7,  'SKF Mexico',                'Ventas Industriales','55-5555-0707', 'rodamientos@skf.com.mx',      'Lago Zurich 219, CDMX',             'Rodamientos y elementos de transmision',  TRUE,  1),
  (8,  'Soldaduras ESAB Mexico',    'Tecnicos',           '81-5555-0808', 'soporte@esab.mx',             'San Nicolas de los Garza, NL',      'Consumibles de soldadura',                TRUE,  2),
  (9,  'Seguridad Industrial HD',   'Compras Corporativo','55-5555-0909', 'seguridad@hdindustrial.mx',   'Insurgentes Sur 1234, CDMX',        'EPP y equipo de proteccion',              TRUE,  1),
  (10, 'Sensores y Control SA',     'Soporte Tecnico',    '33-5555-1010', 'soporte@sensorescontrol.mx',  'Av. Patria 888, Guadalajara',       'Instrumentacion y sensores industriales', FALSE, 3)
ON CONFLICT (supplier_name) DO NOTHING;

-- Sync sequence
SELECT setval('suppliers_supplier_id_seq', (SELECT MAX(supplier_id) FROM suppliers));

-- -----------------------------------------------------------------------------
-- 5. SUPPLIER RECEIPTS
--    Columnas: receipt_id, material_id, supplier_id, quantity_received,
--              notes, created_by, receipt_timestamp
--    FK: material_id -> materials, supplier_id -> suppliers, created_by -> users
--    Sin UNIQUE constraint — se usa ON CONFLICT (receipt_id) DO NOTHING sobre PK
-- -----------------------------------------------------------------------------
INSERT INTO supplier_receipts (receipt_id, material_id, supplier_id, quantity_received, notes, created_by, receipt_timestamp) VALUES
  (1,  1,  1,  500.00,  'Lote de enero, lamina calibre 18',            4, NOW() - INTERVAL '60 days'),
  (2,  2,  2,  1000.00, 'Caja de 1000 piezas M8x25',                   4, NOW() - INTERVAL '58 days'),
  (3,  3,  3,  80.00,   '4 cubetas de 20 lt c/u',                      5, NOW() - INTERVAL '55 days'),
  (4,  4,  4,  300.00,  'Rollo de 300m calibre 12 negro',              5, NOW() - INTERVAL '52 days'),
  (5,  5,  5,  150.00,  'Tubo en varillas de 6m',                      4, NOW() - INTERVAL '50 days'),
  (6,  6,  3,  60.00,   'Resina baja viscosidad lote 2024-A',          6, NOW() - INTERVAL '48 days'),
  (7,  7,  6,  40.00,   'Aceite ISO 68 en bidones de 20lt',            6, NOW() - INTERVAL '45 days'),
  (8,  8,  9,  25.00,   'Filtros HEPA clase H13',                      4, NOW() - INTERVAL '43 days'),
  (9,  9,  1,  200.00,  'Banda 5 pulgadas de ancho',                   5, NOW() - INTERVAL '40 days'),
  (10, 10, 7,  50.00,   'Rodamientos en caja de 10 pzas',              6, NOW() - INTERVAL '38 days'),
  (11, 11, 1,  250.00,  'Placa 3mm x 1.2m x 2.4m',                    4, NOW() - INTERVAL '35 days'),
  (12, 12, 8,  30.00,   'Carrete 15kg alambre MIG',                    5, NOW() - INTERVAL '33 days'),
  (13, 13, 3,  20.00,   'Cartucho 300ml sellador RTV rojo',            4, NOW() - INTERVAL '30 days'),
  (14, 15, 2,  100.00,  'Brocas unitarias en bolsa',                   6, NOW() - INTERVAL '28 days'),
  (15, 16, 4,  50.00,   '50 rollos cinta 19mm x 18m',                  4, NOW() - INTERVAL '25 days'),
  (16, 17, 5,  30.00,   'Valvulas con certificado NSF',                5, NOW() - INTERVAL '23 days'),
  (17, 18, 10, 15.00,   'Sensores PT100 clase A',                      6, NOW() - INTERVAL '20 days'),
  (18, 19, 9,  200.00,  'Caja de 100 pares talla M',                   4, NOW() - INTERVAL '18 days'),
  (19, 20, 9,  50.00,   'Cascos con logotipo empresa',                 5, NOW() - INTERVAL '15 days'),
  (20, 1,  1,  750.00,  'Segunda entrega lamina enero',                4, NOW() - INTERVAL '12 days'),
  (21, 2,  2,  500.00,  'Reposicion tornilleria',                      6, NOW() - INTERVAL '10 days'),
  (22, 7,  6,  20.00,   'Aceite hidraulico ISO 46',                    5, NOW() - INTERVAL '8 days'),
  (23, 10, 7,  30.00,   'Rodamientos de repuesto urgente',             4, NOW() - INTERVAL '7 days'),
  (24, 3,  3,  40.00,   'Pintura color amarillo seguridad',            6, NOW() - INTERVAL '5 days'),
  (25, 4,  4,  100.00,  'Cable calibre 10 para cuadro electrico',      5, NOW() - INTERVAL '4 days'),
  (26, 12, 8,  15.00,   'Alambre TIG ER308L acero inox',               4, NOW() - INTERVAL '3 days'),
  (27, 8,  9,  10.00,   'Filtros de recambio para cabina pintura',     5, NOW() - INTERVAL '2 days'),
  (28, 6,  3,  25.00,   'Resina gelcoat blanco',                       4, NOW() - INTERVAL '1 day'),
  (29, 11, 1,  100.00,  'Placa aluminio 5mm para proyecto especial',   6, NOW() - INTERVAL '12 hours'),
  (30, 19, 9,  300.00,  'Guantes para auditoria de seguridad',         5, NOW())
ON CONFLICT (receipt_id) DO NOTHING;

-- Sync sequence
SELECT setval('supplier_receipts_receipt_id_seq', (SELECT MAX(receipt_id) FROM supplier_receipts));

-- -----------------------------------------------------------------------------
-- 6. PRODUCTION REQUESTS
--    Columnas: request_id, line_id, requested_by, status, requested_at,
--              approved_by, approved_at, is_active
--    FK: line_id -> production_lines, requested_by -> users, approved_by -> users
--    Estados: DRAFT, SUBMITTED, APPROVED, REJECTED, CANCELLED
-- -----------------------------------------------------------------------------
INSERT INTO production_requests (request_id, line_id, requested_by, status, requested_at, approved_by, approved_at, is_active) VALUES
  (1,  1, 4, 'APPROVED',  NOW() - INTERVAL '50 days', 1, NOW() - INTERVAL '49 days', TRUE),
  (2,  2, 5, 'APPROVED',  NOW() - INTERVAL '45 days', 2, NOW() - INTERVAL '44 days', TRUE),
  (3,  3, 6, 'APPROVED',  NOW() - INTERVAL '40 days', 1, NOW() - INTERVAL '39 days', TRUE),
  (4,  4, 4, 'REJECTED',  NOW() - INTERVAL '35 days', 2, NOW() - INTERVAL '34 days', TRUE),
  (5,  1, 5, 'SUBMITTED', NOW() - INTERVAL '30 days', NULL, NULL,                    TRUE),
  (6,  2, 6, 'SUBMITTED', NOW() - INTERVAL '25 days', NULL, NULL,                    TRUE),
  (7,  3, 4, 'DRAFT',     NOW() - INTERVAL '20 days', NULL, NULL,                    TRUE),
  (8,  5, 5, 'DRAFT',     NOW() - INTERVAL '15 days', NULL, NULL,                    TRUE),
  (9,  1, 6, 'CANCELLED', NOW() - INTERVAL '10 days', NULL, NULL,                    TRUE),
  (10, 4, 4, 'APPROVED',  NOW() - INTERVAL '8 days',  1,    NOW() - INTERVAL '7 days',    TRUE),
  (11, 5, 5, 'APPROVED',  NOW() - INTERVAL '6 days',  2,    NOW() - INTERVAL '5 days',    TRUE),
  (12, 2, 6, 'SUBMITTED', NOW() - INTERVAL '4 days',  NULL, NULL,                    TRUE),
  (13, 3, 4, 'DRAFT',     NOW() - INTERVAL '2 days',  NULL, NULL,                    TRUE),
  (14, 1, 5, 'REJECTED',  NOW() - INTERVAL '1 day',   1,    NOW() - INTERVAL '12 hours',  TRUE),
  (15, 4, 6, 'DRAFT',     NOW(),                       NULL, NULL,                    TRUE)
ON CONFLICT (request_id) DO NOTHING;

-- Sync sequence
SELECT setval('production_requests_request_id_seq', (SELECT MAX(request_id) FROM production_requests));

-- -----------------------------------------------------------------------------
-- 7. PRODUCTION REQUEST ITEMS
--    Columnas: item_id, request_id, material_id, quantity, unit
--    FK: request_id -> production_requests, material_id -> materials
--    PK: item_id (SERIAL) — ON CONFLICT sobre PK
-- -----------------------------------------------------------------------------
INSERT INTO production_request_items (item_id, request_id, material_id, quantity, unit) VALUES
  -- Request 1 (APPROVED - Linea A Ensamble)
  (1,  1,  2,  200, 'pza'),
  (2,  1,  10,  20, 'pza'),
  -- Request 2 (APPROVED - Linea B Pintura)
  (3,  2,  3,   30, 'lt'),
  (4,  2,  6,   15, 'kg'),
  -- Request 3 (APPROVED - Linea C Soldadura)
  (5,  3,  12,  10, 'kg'),
  (6,  3,  1,  100, 'kg'),
  -- Request 4 (REJECTED - Linea D Empaque)
  (7,  4,  16,  20, 'rollo'),
  (8,  4,  19, 100, 'par'),
  -- Request 5 (SUBMITTED - Linea A)
  (9,  5,  2,  500, 'pza'),
  (10, 5,  15,  50, 'pza'),
  -- Request 6 (SUBMITTED - Linea B)
  (11, 6,  3,   20, 'lt'),
  (12, 6,  13,  10, 'pza'),
  -- Request 7 (DRAFT - Linea C)
  (13, 7,  12,   5, 'kg'),
  -- Request 8 (DRAFT - Linea E)
  (14, 8,  8,   10, 'pza'),
  (15, 8,  18,   5, 'pza'),
  -- Request 9 (CANCELLED - Linea A)
  (16, 9,  4,   50, 'm'),
  -- Request 10 (APPROVED - Linea D)
  (17, 10, 16,  30, 'rollo'),
  (18, 10, 20,  15, 'pza'),
  -- Request 11 (APPROVED - Linea E)
  (19, 11, 18,  10, 'pza'),
  (20, 11, 8,    5, 'pza'),
  -- Request 12 (SUBMITTED - Linea B)
  (21, 12, 3,   25, 'lt'),
  -- Request 13 (DRAFT - Linea C)
  (22, 13, 1,  200, 'kg'),
  (23, 13, 11,  50, 'kg'),
  -- Request 14 (REJECTED - Linea A)
  (24, 14, 9,   30, 'm'),
  (25, 14, 7,   10, 'lt'),
  -- Request 15 (DRAFT - Linea D)
  (26, 15, 2,  300, 'pza'),
  (27, 15, 16,  10, 'rollo')
ON CONFLICT (item_id) DO NOTHING;

-- Sync sequence
SELECT setval('production_request_items_item_id_seq', (SELECT MAX(item_id) FROM production_request_items));

-- =============================================================================
-- FIN DEL SCRIPT
-- Total: 10 usuarios, 20 materiales, 6 lineas, 10 proveedores,
--        30 recepciones, 15 ordenes de produccion, 27 items de orden
-- Contrasena de todos los usuarios: Admin1234!
-- =============================================================================
