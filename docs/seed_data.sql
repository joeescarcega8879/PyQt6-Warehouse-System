-- =============================================================================
-- seed_data.sql
-- Datos de prueba para el sistema de almacen (PyQt6 Warehouse System)
-- Estrategia: ON CONFLICT DO NOTHING — idempotente, no sobreescribe datos existentes.
-- Contrasena de todos los usuarios: Admin1234!
-- =============================================================================
-- Total: 15 usuarios, 40 materiales, 8 lineas, 20 proveedores,
--        80 recepciones, 35 ordenes de produccion, ~70 items de orden
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. USERS
--    Columnas: user_id, username, password_hash, full_name, user_role, is_active
--    Roles validos: admin, supervisor, leader, operator, viewer
-- -----------------------------------------------------------------------------
INSERT INTO users (user_id, username, password_hash, full_name, user_role, is_active) VALUES
  (1,  'admin',            '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'System Administrator',  'admin',      TRUE),
  (2,  'supervisor_ana',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Ana Martinez',          'supervisor', TRUE),
  (3,  'supervisor_bob',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Bob Ramirez',           'supervisor', TRUE),
  (4,  'leader_carlos',    '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Carlos Herrera',        'leader',     TRUE),
  (5,  'leader_diana',     '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Diana Lopez',           'leader',     TRUE),
  (6,  'leader_edgar',     '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Edgar Fuentes',         'leader',     TRUE),
  (7,  'operator_fanny',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Fanny Torres',          'operator',   TRUE),
  (8,  'operator_gil',     '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Gil Mendoza',           'operator',   TRUE),
  (9,  'viewer_hector',    '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Hector Navarro',        'viewer',     TRUE),
  (10, 'viewer_iris',      '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Iris Castillo',         'viewer',     FALSE),
  (11, 'supervisor_jorge', '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Jorge Ibarra',          'supervisor', TRUE),
  (12, 'leader_karina',    '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Karina Vega',           'leader',     TRUE),
  (13, 'operator_luis',    '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Luis Pena',             'operator',   TRUE),
  (14, 'operator_marta',   '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Marta Solis',           'operator',   TRUE),
  (15, 'viewer_noel',      '$2b$12$ZviFBK.4rUJHy1nkhJ3.4OWOxDOYm1WQmu9vLWQ1wTswpMf25kYYW', 'Noel Guerrero',         'viewer',     TRUE)
ON CONFLICT (username) DO NOTHING;

SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));

-- -----------------------------------------------------------------------------
-- 2. MATERIALS
--    Columnas: material_id, material_name, description, unit_of_measure
--    stock_quantity queda en 0 (default)
-- -----------------------------------------------------------------------------
INSERT INTO materials (material_id, material_name, description, unit_of_measure) VALUES
  -- Metales y laminas
  (1,  'Acero laminado en frio',         'Lamina de acero para estructuras',                   'kg'),
  (2,  'Acero laminado en caliente',     'Lamina estructural HR para fabricacion pesada',       'kg'),
  (3,  'Placa de aluminio 3mm',          'Placa de aluminio serie 6061',                        'kg'),
  (4,  'Placa de aluminio 6mm',          'Placa gruesa aluminio 6061-T6',                       'kg'),
  (5,  'Tubo cuadrado acero 2x2',        'Tubo estructural acero negro 2x2 calibre 14',         'ml'),
  (6,  'Angulo de acero 1.5 pulgadas',   'Angulo estructural acero A36',                        'ml'),
  (7,  'Varilla roscada 3/8"',           'Varilla roscada acero inoxidable 304',                'ml'),
  -- Tornilleria y fijaciones
  (8,  'Tornillo hexagonal M8',          'Tornillo de acero inoxidable M8x25mm',                'pza'),
  (9,  'Tornillo hexagonal M10',         'Tornillo de acero inoxidable M10x30mm',               'pza'),
  (10, 'Tornillo allen M6',              'Tornillo allen cabeza cilindrica M6x20mm',             'pza'),
  (11, 'Tuerca hexagonal M8',            'Tuerca acero inoxidable M8',                          'pza'),
  (12, 'Rondana plana M8',               'Rondana plana acero M8',                              'pza'),
  -- Pinturas y recubrimientos
  (13, 'Pintura epoxica gris',           'Pintura anticorrosiva para metal',                    'lt'),
  (14, 'Pintura epoxica negra',          'Pintura anticorrosiva negro mate',                    'lt'),
  (15, 'Pintura poliuretano blanco',     'Acabado industrial blanco brillante',                  'lt'),
  (16, 'Fondo anticorrosivo rojo',       'Primer epoxido para imprimacion',                     'lt'),
  (17, 'Silicona industrial RTV',        'Sellador de alta temperatura',                        'pza'),
  (18, 'Resina poliester',               'Resina para recubrimientos industriales',              'kg'),
  -- Electricos y cables
  (19, 'Cable electrico AWG 12',         'Cable de cobre calibre 12 negro',                     'ml'),
  (20, 'Cable electrico AWG 14',         'Cable de cobre calibre 14 blanco',                    'ml'),
  (21, 'Cable electrico AWG 10',         'Cable de cobre calibre 10 para cuadros',               'ml'),
  (22, 'Cinta aislante 3M',              'Cinta de vinilo para instalaciones electricas',        'rollo'),
  (23, 'Terminal tipo pala 1/4"',        'Terminal de cobre estanada 14-16 AWG',                 'pza'),
  (24, 'Breaker bipolar 20A',            'Interruptor termomagnetico 20A 240V',                  'pza'),
  -- Tuberias y conexiones
  (25, 'Tubo PVC 2 pulgadas',            'Tubo rigido de PVC para instalaciones hidraulicas',    'ml'),
  (26, 'Tubo PVC 3 pulgadas',            'Tubo rigido de PVC drenaje sanitario',                 'ml'),
  (27, 'Codo PVC 2" 90 grados',          'Codo de PVC para union de tubos',                     'pza'),
  (28, 'Valvula de bola 1/2"',           'Valvula de cierre rapido acero inox',                  'pza'),
  (29, 'Valvula de bola 1"',             'Valvula industrial de paso completo acero inox',       'pza'),
  -- Lubricantes y quimicos
  (30, 'Lubricante industrial ISO 68',   'Aceite lubricante para maquinaria ISO 68',             'lt'),
  (31, 'Lubricante hidraulico ISO 46',   'Aceite hidraulico para sistemas de presion',           'lt'),
  (32, 'Grasa de litio #2',              'Grasa multiproposito para rodamientos',                'kg'),
  (33, 'Desengrasante industrial',       'Solvente desengrasante para limpieza de piezas',       'lt'),
  -- Consumibles de soldadura
  (34, 'Soldadura MIG ER70S-6',          'Alambre de soldadura MIG 0.9mm',                       'kg'),
  (35, 'Soldadura TIG ER308L',           'Varilla TIG acero inoxidable 2.4mm',                   'kg'),
  (36, 'Electrodo 6013 3/32"',           'Electrodo para soldadura SMAW acero suave',            'kg'),
  -- Instrumentacion y sensores
  (37, 'Sensor de temperatura PT100',    'Sonda RTD para medicion industrial',                   'pza'),
  (38, 'Rodamiento SKF 6205',            'Rodamiento de bolas de precision',                     'pza'),
  (39, 'Filtro de aire HEPA H13',        'Filtro de alta eficiencia para polvo fino',            'pza'),
  -- EPP y seguridad
  (40, 'Guante de nitrilo talla M',      'Guante desechable para manejo quimico',                'par'),
  (41, 'Guante de nitrilo talla L',      'Guante desechable para manejo quimico talla L',        'par'),
  (42, 'Casco de seguridad ABS',         'Casco con suspension de 4 puntos clase E',             'pza'),
  (43, 'Lente de seguridad claro',       'Lente antiimpacto transparente ANSI Z87.1',            'pza'),
  -- Herramientas y consumibles
  (44, 'Broca HSS 10mm',                 'Broca de acero rapido para metal',                     'pza'),
  (45, 'Broca HSS 6mm',                  'Broca de acero rapido para metal',                     'pza'),
  (46, 'Disco de corte 4.5"',            'Disco abrasivo para amoladora angular',                'pza'),
  (47, 'Disco de desbaste 4.5"',         'Disco abrasivo grueso para desbaste de metal',         'pza'),
  -- Empaque y logistica
  (48, 'Banda transportadora 5"',        'Banda de hule para lineas de produccion',               'ml'),
  (49, 'Cinta de embalaje transparente', 'Cinta adhesiva para empaque de cajas',                  'rollo'),
  (50, 'Zunchos de plastico 1/2"',       'Flejes de polipropileno para empacado',                 'kg')
ON CONFLICT (material_name) DO NOTHING;

SELECT setval('materials_material_id_seq', (SELECT MAX(material_id) FROM materials));

-- -----------------------------------------------------------------------------
-- 3. PRODUCTION LINES
--    Columnas: line_id, line_name, description, is_active
-- -----------------------------------------------------------------------------
INSERT INTO production_lines (line_id, line_name, description, is_active) VALUES
  (1, 'Linea A - Ensamble',          'Linea principal de ensamble de componentes mecanicos',    TRUE),
  (2, 'Linea B - Pintura',           'Linea de aplicacion de recubrimientos y pintura',          TRUE),
  (3, 'Linea C - Soldadura',         'Linea de soldadura MIG/TIG y SMAW',                        TRUE),
  (4, 'Linea D - Empaque',           'Linea de empaque, etiquetado y zunchado',                  TRUE),
  (5, 'Linea E - Control Calidad',   'Inspeccion, pruebas y control de calidad final',           TRUE),
  (6, 'Linea F - Mantenimiento',     'Mantenimiento preventivo y correctivo de equipos',         FALSE),
  (7, 'Linea G - Prefabricado',      'Corte, doblez y preparacion de materiales',                TRUE),
  (8, 'Linea H - Instrumentacion',   'Instalacion y calibracion de instrumentos y sensores',    TRUE)
ON CONFLICT (line_name) DO NOTHING;

SELECT setval('production_lines_line_id_seq', (SELECT MAX(line_id) FROM production_lines));

-- -----------------------------------------------------------------------------
-- 4. SUPPLIERS
--    Columnas: supplier_id, supplier_name, contact_department, phone, email,
--              address, notes, is_active, created_by
-- -----------------------------------------------------------------------------
INSERT INTO suppliers (supplier_id, supplier_name, contact_department, phone, email, address, notes, is_active, created_by) VALUES
  (1,  'Aceros del Norte S.A.',        'Compras',              '811-555-0101', 'ventas@acerosnorte.mx',         'Av. Industrial 100, Monterrey, NL',          'Proveedor principal de lamina y perfiles estructurales',        TRUE,  1),
  (2,  'Ferreteria Central',           'Atencion a Clientes',  '55-5555-0202', 'pedidos@ferreteriacentral.mx',  'Calle 5 de Mayo 45, CDMX',                   'Tornilleria, herrajes y herramientas en general',              TRUE,  1),
  (3,  'Pinturas Industriales MX',     'Ventas',               '33-5555-0303', 'info@pinturasmx.com',           'Blvd. Tecnologico 200, Guadalajara, JAL',     'Especialistas en pinturas epoxicas y poliuretano',             TRUE,  2),
  (4,  'Electricos Profesionales',     'Ventas',               '55-5555-0404', 'ventas@electricos.mx',          'Norte 45 No.100, CDMX',                       'Cables, breakers y materiales electricos industriales',        TRUE,  2),
  (5,  'Plasticos y Tubos SA',         'Exportaciones',        '664-555-0505', 'export@plasticostubos.com',     'Zona Industrial, Tijuana, BC',                'PVC, polietileno y conexiones hidraulicas',                    TRUE,  1),
  (6,  'Lubricantes Premier',          'Distribucion',         '81-5555-0606', 'dist@lubricantespremier.mx',    'Parque Industrial MTY Nave 8, Monterrey, NL', 'Lubricantes, aceites industriales y grasas',                   TRUE,  3),
  (7,  'SKF Mexico',                   'Ventas Industriales',  '55-5555-0707', 'rodamientos@skf.com.mx',        'Lago Zurich 219, CDMX',                       'Rodamientos y elementos de transmision de potencia',          TRUE,  1),
  (8,  'Soldaduras ESAB Mexico',       'Tecnicos',             '81-5555-0808', 'soporte@esab.mx',               'San Nicolas de los Garza, NL',                'Consumibles de soldadura MIG, TIG y SMAW',                    TRUE,  2),
  (9,  'Seguridad Industrial HD',      'Compras Corporativo',  '55-5555-0909', 'seguridad@hdindustrial.mx',     'Insurgentes Sur 1234, CDMX',                  'EPP y equipo de proteccion personal certificado',             TRUE,  1),
  (10, 'Sensores y Control SA',        'Soporte Tecnico',      '33-5555-1010', 'soporte@sensorescontrol.mx',    'Av. Patria 888, Guadalajara, JAL',            'Instrumentacion y sensores industriales — proveedor inactivo', FALSE, 3),
  (11, 'Aluminio y Perfiles del Baj',  'Ventas',               '477-555-1111', 'ventas@aluminiosbajio.mx',      'Blvd. Torres Urdapilleta 500, Leon, GTO',     'Perfiles y placas de aluminio estructural',                    TRUE,  1),
  (12, 'Herrajes y Suministros NL',    'Logistica',            '81-5555-1212', 'logistica@herrajesnl.mx',       'Apodaca Industrial Sur Local 22, NL',          'Herrajes, fijaciones y suministros industriales variados',     TRUE,  2),
  (13, 'Chem-Quim Industrial',         'Asesorias',            '55-5555-1313', 'asesoria@chemquim.mx',          'Vallejo 333, CDMX',                           'Quimicos industriales, solventes y desengrasantes',           TRUE,  1),
  (14, 'Valvulas y Conexiones MX',     'Ventas Tecnicas',      '81-5555-1414', 'tecnico@valvulasmx.com',        'Carretera a Laredo Km 12, Monterrey, NL',     'Valvulas industriales y conexiones de alta presion',           TRUE,  3),
  (15, 'Distribuidora Electrica GDL',  'Comercial',            '33-5555-1515', 'comercial@electrica-gdl.mx',    'Lopez Mateos Sur 780, Guadalajara, JAL',      'Distribucion de materiales electricos y automatizacion',       TRUE,  2),
  (16, 'Abrasivos y Herr. Tijuana',    'Ventas',               '664-555-1616', 'ventas@abrasivostj.mx',         'Otay Industrial Bodega 5, Tijuana, BC',       'Discos de corte, desbaste y brocas HSS',                       TRUE,  1),
  (17, 'Empaques y Flejes del Norte',  'Servicio al Cliente',  '81-5555-1717', 'cliente@empaques-norte.mx',     'Parque Industrial Stiva Nave 3, Apodaca, NL', 'Cintas, zunchos y materiales de embalaje industrial',          TRUE,  2),
  (18, 'Instrumentacion Avanzada',     'Soporte',              '55-5555-1818', 'soporte@instrumavanzada.mx',    'Periferico Norte 4500, CDMX',                 'Sensores, transmisores y calibracion industrial',              TRUE,  1),
  (19, 'Metal-Cut Monterrey',          'Ventas Industriales',  '81-5555-1919', 'industrial@metalcut.mx',        'Av. Ruiz Cortines 900, Monterrey, NL',        'Corte y suministro de lamina, tubo y perfiles metalicos',      TRUE,  3),
  (20, 'Cauchos y Bandas SA',          'Distribucion',         '33-5555-2020', 'dist@cauchosbandas.mx',         'Periferico Manuel Gomez Morin 1500, GDL',     'Bandas transportadoras y productos de caucho industrial',      FALSE, 1)
ON CONFLICT (supplier_name) DO NOTHING;

SELECT setval('suppliers_supplier_id_seq', (SELECT MAX(supplier_id) FROM suppliers));

-- -----------------------------------------------------------------------------
-- 5. SUPPLIER RECEIPTS
--    Columnas: receipt_id, material_id, supplier_id, quantity_received,
--              notes, created_by, receipt_timestamp
-- -----------------------------------------------------------------------------
INSERT INTO supplier_receipts (receipt_id, material_id, supplier_id, quantity_received, notes, created_by, receipt_timestamp) VALUES
  -- Semana 13 atras (~90 dias)
  (1,  1,  1,  600.00,  'Lote trimestral lamina fria calibre 18 — entrega 1/2',         4, NOW() - INTERVAL '90 days'),
  (2,  8,  2,  1000.00, 'Caja 1000 piezas tornillo M8x25 inox',                         4, NOW() - INTERVAL '89 days'),
  (3,  13, 3,  80.00,   'Pintura epoxica gris 4 cubetas 20lt — lote Q1',                5, NOW() - INTERVAL '88 days'),
  (4,  19, 4,  400.00,  'Rollo 300m cable AWG-12 negro — orden anual',                  5, NOW() - INTERVAL '87 days'),
  (5,  25, 5,  200.00,  'Tubo PVC 2" en varillas 6m — lote enero',                      4, NOW() - INTERVAL '86 days'),
  (6,  34, 8,  50.00,   'Alambre MIG ER70S-6 carrete 15kg x 3 — lote inicial',          6, NOW() - INTERVAL '85 days'),
  (7,  30, 6,  60.00,   'Aceite ISO 68 bidones 20lt x 3',                               6, NOW() - INTERVAL '84 days'),
  (8,  39, 9,  30.00,   'Filtros HEPA H13 para cabinas de pintura',                     4, NOW() - INTERVAL '83 days'),
  (9,  48, 20, 300.00,  'Banda transportadora 5" ancho — lote planta nueva',            5, NOW() - INTERVAL '82 days'),
  (10, 38, 7,  60.00,   'Rodamientos SKF 6205 caja 10 pzas x 6',                        6, NOW() - INTERVAL '81 days'),
  -- Semana 12 atras (~84 dias)
  (11, 3,  11, 300.00,  'Placa aluminio 3mm 1.2x2.4m — lote estructura',                4, NOW() - INTERVAL '80 days'),
  (12, 35, 8,  20.00,   'Varilla TIG ER308L 2.4mm caja 5kg x 4',                        5, NOW() - INTERVAL '78 days'),
  (13, 17, 3,  25.00,   'Cartucho 300ml silicona RTV rojo temperatura',                 4, NOW() - INTERVAL '77 days'),
  (14, 44, 2,  150.00,  'Brocas HSS 10mm unitarias — reposicion anual',                 6, NOW() - INTERVAL '76 days'),
  (15, 22, 4,  60.00,   'Cinta aislante 3M 19mm x 18m — caja 60 rollos',               4, NOW() - INTERVAL '75 days'),
  (16, 28, 14, 40.00,   'Valvulas bola 1/2" inox con certificado NSF',                  5, NOW() - INTERVAL '74 days'),
  (17, 37, 18, 20.00,   'Sensores PT100 clase A — primera entrega',                     6, NOW() - INTERVAL '73 days'),
  (18, 40, 9,  250.00,  'Caja 100 pares guante nitrilo M — reposicion',                 4, NOW() - INTERVAL '72 days'),
  (19, 42, 9,  60.00,   'Cascos ABS con logotipo empresa — alta inicial',               5, NOW() - INTERVAL '71 days'),
  (20, 1,  1,  800.00,  'Lote trimestral lamina fria calibre 18 — entrega 2/2',         4, NOW() - INTERVAL '70 days'),
  -- Semana 11 atras (~70 dias)
  (21, 9,  2,  600.00,  'Tornillo M10x30 inox — reposicion stock',                      6, NOW() - INTERVAL '69 days'),
  (22, 31, 6,  30.00,   'Aceite hidraulico ISO 46 bidones 20lt x 1.5',                  5, NOW() - INTERVAL '68 days'),
  (23, 38, 7,  40.00,   'Rodamientos SKF urgencia por paro de linea',                   4, NOW() - INTERVAL '67 days'),
  (24, 14, 3,  30.00,   'Pintura epoxica negra — proyecto especial herreria',           6, NOW() - INTERVAL '66 days'),
  (25, 20, 4,  150.00,  'Cable AWG-14 blanco para tablero nuevo',                       5, NOW() - INTERVAL '65 days'),
  (26, 35, 8,  15.00,   'Alambre TIG ER308L para tanques inox',                         4, NOW() - INTERVAL '64 days'),
  (27, 39, 9,  15.00,   'Filtros HEPA recambio cabina pintura linea B',                 5, NOW() - INTERVAL '63 days'),
  (28, 18, 3,  30.00,   'Resina gelcoat blanco — proyecto fibra de vidrio',             4, NOW() - INTERVAL '62 days'),
  (29, 4,  11, 120.00,  'Placa aluminio 6mm para proyecto especial',                    6, NOW() - INTERVAL '61 days'),
  (30, 40, 9,  300.00,  'Guantes nitrilo M para auditoria de seguridad',               5, NOW() - INTERVAL '60 days'),
  -- Semana 10 atras (~56 dias)
  (31, 5,  19, 200.00,  'Tubo cuadrado acero 2x2 calibre 14 — lote estructura',        4, NOW() - INTERVAL '58 days'),
  (32, 46, 16, 200.00,  'Discos de corte 4.5" caja 50 pzas x 4',                        7, NOW() - INTERVAL '57 days'),
  (33, 47, 16, 100.00,  'Discos de desbaste 4.5" caja 25 pzas x 4',                     7, NOW() - INTERVAL '56 days'),
  (34, 32, 6,  25.00,   'Grasa litio #2 cubeta 20kg',                                   6, NOW() - INTERVAL '55 days'),
  (35, 23, 4,  500.00,  'Terminales pala 1/4" caja 500 piezas',                         5, NOW() - INTERVAL '54 days'),
  (36, 27, 5,  80.00,   'Codos PVC 2" 90 grados — proyecto ampliacion',                4, NOW() - INTERVAL '53 days'),
  (37, 10, 2,  400.00,  'Tornillo allen M6x20 caja 400 pzas',                           4, NOW() - INTERVAL '52 days'),
  (38, 15, 3,  20.00,   'Pintura poliuretano blanco — linea de empaque',               5, NOW() - INTERVAL '51 days'),
  (39, 36, 8,  30.00,   'Electrodo 6013 3/32" caja 10kg x 3',                           6, NOW() - INTERVAL '50 days'),
  (40, 33, 13, 40.00,   'Desengrasante industrial bidones 20lt x 2',                    7, NOW() - INTERVAL '49 days'),
  -- Semana 9 atras (~42 dias)
  (41, 2,  1,  500.00,  'Acero laminado caliente — segunda entrega trimestre',          4, NOW() - INTERVAL '47 days'),
  (42, 6,  19, 150.00,  'Angulo acero A36 1.5" — reposicion stock taller',             4, NOW() - INTERVAL '46 days'),
  (43, 11, 12, 300.00,  'Tuerca M8 inox caja 300 piezas x 1',                           5, NOW() - INTERVAL '45 days'),
  (44, 12, 12, 400.00,  'Rondana plana M8 caja 400 piezas',                             5, NOW() - INTERVAL '44 days'),
  (45, 43, 9,  80.00,   'Lente seguridad claro ANSI Z87.1 — reposicion EPP',           6, NOW() - INTERVAL '43 days'),
  (46, 24, 15, 15.00,   'Breaker bipolar 20A para tablero ampliacion',                  7, NOW() - INTERVAL '42 days'),
  (47, 29, 14, 20.00,   'Valvula bola 1" paso completo para cabina presion',           6, NOW() - INTERVAL '41 days'),
  (48, 49, 17, 100.00,  'Cinta embalaje transparente — reposicion almacen',            4, NOW() - INTERVAL '40 days'),
  (49, 50, 17, 50.00,   'Zunchos plastico 1/2" caja 20kg',                              5, NOW() - INTERVAL '39 days'),
  (50, 45, 16, 150.00,  'Brocas HSS 6mm unitarias — reposicion taller',               7, NOW() - INTERVAL '38 days'),
  -- Semana 8 atras (~28 dias)
  (51, 1,  1,  700.00,  'Lamina fria calibre 16 — pedido urgente proyecto',            4, NOW() - INTERVAL '35 days'),
  (52, 34, 8,  25.00,   'Alambre MIG reposicion urgente linea soldadura',              5, NOW() - INTERVAL '34 days'),
  (53, 30, 6,  40.00,   'Aceite ISO 68 — reposicion mensual',                          6, NOW() - INTERVAL '33 days'),
  (54, 16, 3,  25.00,   'Fondo anticorrosivo rojo — imprimacion lote nuevas piezas',  4, NOW() - INTERVAL '32 days'),
  (55, 7,  19, 100.00,  'Varilla roscada 3/8" — suministro proyecto maquinaria',      4, NOW() - INTERVAL '31 days'),
  (56, 19, 4,  200.00,  'Cable AWG-12 — reposicion cuadros electricos',               5, NOW() - INTERVAL '30 days'),
  (57, 21, 15, 100.00,  'Cable AWG-10 negro para cuadro principal ampliacion',        7, NOW() - INTERVAL '29 days'),
  (58, 38, 7,  20.00,   'Rodamientos SKF reposicion preventiva — prog. mant.',        6, NOW() - INTERVAL '28 days'),
  (59, 37, 18, 10.00,   'Sensores PT100 reposicion instrumentacion',                  6, NOW() - INTERVAL '27 days'),
  (60, 48, 20, 150.00,  'Banda transportadora 5" segunda entrega',                    5, NOW() - INTERVAL '26 days'),
  -- Semana 7 atras (~21 dias)
  (61, 8,  2,  800.00,  'Tornillo M8x25 — reposicion general almacen',               4, NOW() - INTERVAL '25 days'),
  (62, 13, 3,  40.00,   'Pintura epoxica gris — segunda entrega trimestre',           5, NOW() - INTERVAL '24 days'),
  (63, 40, 9,  150.00,  'Guantes nitrilo M — reposicion mensual',                    4, NOW() - INTERVAL '23 days'),
  (64, 46, 16, 100.00,  'Discos de corte 4.5" reposicion linea C',                   7, NOW() - INTERVAL '22 days'),
  (65, 32, 6,  15.00,   'Grasa litio #2 — reposicion rodamientos en servicio',       6, NOW() - INTERVAL '21 days'),
  -- Semana reciente (~14 dias)
  (66, 3,  11, 150.00,  'Placa aluminio 3mm — pedido especial proyecto cliente',     4, NOW() - INTERVAL '14 days'),
  (67, 25, 5,  100.00,  'Tubo PVC 2" reposicion — ampliacion red hidraulica',        5, NOW() - INTERVAL '13 days'),
  (68, 35, 8,  10.00,   'Varilla TIG ER308L — urgente proyecto depositos inox',      4, NOW() - INTERVAL '12 days'),
  (69, 33, 13, 20.00,   'Desengrasante — limpieza programada de lineas',             7, NOW() - INTERVAL '11 days'),
  (70, 41, 9,  100.00,  'Guantes nitrilo L — primer pedido talla L',                 5, NOW() - INTERVAL '10 days'),
  -- Ultima semana
  (71, 1,  1,  400.00,  'Lamina fria — cierre de trimestre entrega final',           4, NOW() - INTERVAL '7 days'),
  (72, 9,  2,  300.00,  'Tornillo M10x30 — reposicion stock critico',                6, NOW() - INTERVAL '6 days'),
  (73, 22, 4,  40.00,   'Cinta aislante — reposicion almacen general',               5, NOW() - INTERVAL '5 days'),
  (74, 39, 9,  12.00,   'Filtros HEPA — cambio programado mensual',                  4, NOW() - INTERVAL '4 days'),
  (75, 4,  11, 80.00,   'Placa aluminio 6mm — segunda entrega proyecto',             6, NOW() - INTERVAL '3 days'),
  (76, 36, 8,  20.00,   'Electrodo 6013 — reposicion consumibles soldadura',         4, NOW() - INTERVAL '2 days'),
  (77, 14, 3,  15.00,   'Pintura epoxica negra — retoque y acabados finales',        5, NOW() - INTERVAL '1 day'),
  (78, 28, 14, 20.00,   'Valvulas bola 1/2" — reposicion stock valvuleria',          6, NOW() - INTERVAL '12 hours'),
  (79, 43, 9,  50.00,   'Lentes seguridad claro — auditoria seguridad',              7, NOW() - INTERVAL '4 hours'),
  (80, 50, 17, 30.00,   'Zunchos plastico — cierre de mes suministros empaque',      4, NOW())
ON CONFLICT (receipt_id) DO NOTHING;

SELECT setval('supplier_receipts_receipt_id_seq', (SELECT MAX(receipt_id) FROM supplier_receipts));

-- -----------------------------------------------------------------------------
-- 6. PRODUCTION REQUESTS
--    Columnas: request_id, line_id, requested_by, status, requested_at,
--              approved_by, approved_at, is_active
--    Estados: DRAFT, SUBMITTED, APPROVED, REJECTED, CANCELLED
-- -----------------------------------------------------------------------------
INSERT INTO production_requests (request_id, line_id, requested_by, status, requested_at, approved_by, approved_at, is_active) VALUES
  -- Ordenes antiguas APPROVED (base solida de historico)
  (1,  1, 4,  'APPROVED',  NOW() - INTERVAL '85 days', 2, NOW() - INTERVAL '84 days', TRUE),
  (2,  2, 5,  'APPROVED',  NOW() - INTERVAL '80 days', 2, NOW() - INTERVAL '79 days', TRUE),
  (3,  3, 6,  'APPROVED',  NOW() - INTERVAL '75 days', 1, NOW() - INTERVAL '74 days', TRUE),
  (4,  7, 12, 'APPROVED',  NOW() - INTERVAL '70 days', 3, NOW() - INTERVAL '69 days', TRUE),
  (5,  8, 4,  'APPROVED',  NOW() - INTERVAL '65 days', 2, NOW() - INTERVAL '64 days', TRUE),
  (6,  1, 5,  'APPROVED',  NOW() - INTERVAL '60 days', 1, NOW() - INTERVAL '59 days', TRUE),
  (7,  4, 6,  'APPROVED',  NOW() - INTERVAL '55 days', 3, NOW() - INTERVAL '54 days', TRUE),
  (8,  5, 12, 'APPROVED',  NOW() - INTERVAL '50 days', 2, NOW() - INTERVAL '49 days', TRUE),
  (9,  3, 4,  'APPROVED',  NOW() - INTERVAL '45 days', 1, NOW() - INTERVAL '44 days', TRUE),
  (10, 2, 5,  'APPROVED',  NOW() - INTERVAL '40 days', 2, NOW() - INTERVAL '39 days', TRUE),
  -- Ordenes REJECTED (historico de rechazos)
  (11, 4, 6,  'REJECTED',  NOW() - INTERVAL '78 days', 2, NOW() - INTERVAL '77 days', TRUE),
  (12, 1, 5,  'REJECTED',  NOW() - INTERVAL '35 days', 1, NOW() - INTERVAL '34 days', TRUE),
  (13, 7, 4,  'REJECTED',  NOW() - INTERVAL '20 days', 3, NOW() - INTERVAL '19 days', TRUE),
  -- Ordenes CANCELLED
  (14, 1, 6,  'CANCELLED', NOW() - INTERVAL '72 days', NULL, NULL,                    TRUE),
  (15, 3, 12, 'CANCELLED', NOW() - INTERVAL '48 days', NULL, NULL,                    TRUE),
  -- Ordenes desactivadas (is_active = FALSE — cerradas por admin)
  (16, 2, 4,  'APPROVED',  NOW() - INTERVAL '90 days', 1, NOW() - INTERVAL '89 days', FALSE),
  (17, 5, 5,  'APPROVED',  NOW() - INTERVAL '88 days', 2, NOW() - INTERVAL '87 days', FALSE),
  -- Ordenes SUBMITTED (en espera de aprobacion)
  (18, 1, 4,  'SUBMITTED', NOW() - INTERVAL '25 days', NULL, NULL,                    TRUE),
  (19, 2, 12, 'SUBMITTED', NOW() - INTERVAL '18 days', NULL, NULL,                    TRUE),
  (20, 3, 5,  'SUBMITTED', NOW() - INTERVAL '15 days', NULL, NULL,                    TRUE),
  (21, 7, 6,  'SUBMITTED', NOW() - INTERVAL '10 days', NULL, NULL,                    TRUE),
  (22, 8, 4,  'SUBMITTED', NOW() - INTERVAL '8 days',  NULL, NULL,                    TRUE),
  (23, 4, 12, 'SUBMITTED', NOW() - INTERVAL '5 days',  NULL, NULL,                    TRUE),
  -- Ordenes DRAFT (en preparacion)
  (24, 1, 5,  'DRAFT',     NOW() - INTERVAL '30 days', NULL, NULL,                    TRUE),
  (25, 3, 6,  'DRAFT',     NOW() - INTERVAL '22 days', NULL, NULL,                    TRUE),
  (26, 5, 4,  'DRAFT',     NOW() - INTERVAL '16 days', NULL, NULL,                    TRUE),
  (27, 2, 12, 'DRAFT',     NOW() - INTERVAL '12 days', NULL, NULL,                    TRUE),
  (28, 7, 5,  'DRAFT',     NOW() - INTERVAL '9 days',  NULL, NULL,                    TRUE),
  (29, 8, 6,  'DRAFT',     NOW() - INTERVAL '6 days',  NULL, NULL,                    TRUE),
  (30, 1, 4,  'DRAFT',     NOW() - INTERVAL '4 days',  NULL, NULL,                    TRUE),
  (31, 3, 12, 'DRAFT',     NOW() - INTERVAL '3 days',  NULL, NULL,                    TRUE),
  (32, 4, 5,  'DRAFT',     NOW() - INTERVAL '2 days',  NULL, NULL,                    TRUE),
  (33, 6, 6,  'DRAFT',     NOW() - INTERVAL '1 day',   NULL, NULL,                    TRUE),
  (34, 7, 4,  'DRAFT',     NOW() - INTERVAL '12 hours',NULL, NULL,                    TRUE),
  (35, 8, 12, 'DRAFT',     NOW(),                       NULL, NULL,                    TRUE)
ON CONFLICT (request_id) DO NOTHING;

SELECT setval('production_requests_request_id_seq', (SELECT MAX(request_id) FROM production_requests));

-- -----------------------------------------------------------------------------
-- 7. PRODUCTION REQUEST ITEMS
--    Columnas: item_id, request_id, material_id, quantity, unit
-- -----------------------------------------------------------------------------
INSERT INTO production_request_items (item_id, request_id, material_id, quantity, unit) VALUES
  -- Request 1 (APPROVED - Linea A Ensamble)
  (1,  1,  8,   300, 'pza'),
  (2,  1,  38,   20, 'pza'),
  (3,  1,  10,  150, 'pza'),
  -- Request 2 (APPROVED - Linea B Pintura)
  (4,  2,  13,   40, 'lt'),
  (5,  2,  18,   20, 'kg'),
  (6,  2,  16,   15, 'lt'),
  -- Request 3 (APPROVED - Linea C Soldadura)
  (7,  3,  34,   15, 'kg'),
  (8,  3,  1,   150, 'kg'),
  (9,  3,  36,   10, 'kg'),
  -- Request 4 (APPROVED - Linea G Prefabricado)
  (10, 4,  46,  100, 'pza'),
  (11, 4,  44,   50, 'pza'),
  (12, 4,  5,   100, 'ml'),
  -- Request 5 (APPROVED - Linea H Instrumentacion)
  (13, 5,  37,   10, 'pza'),
  (14, 5,  22,   20, 'rollo'),
  -- Request 6 (APPROVED - Linea A Ensamble)
  (15, 6,  8,   500, 'pza'),
  (16, 6,  11,  300, 'pza'),
  (17, 6,  12,  300, 'pza'),
  -- Request 7 (APPROVED - Linea D Empaque)
  (18, 7,  49,   50, 'rollo'),
  (19, 7,  50,   20, 'kg'),
  (20, 7,  40,  100, 'par'),
  -- Request 8 (APPROVED - Linea E Control Calidad)
  (21, 8,  39,   10, 'pza'),
  (22, 8,  37,    5, 'pza'),
  (23, 8,  43,   30, 'pza'),
  -- Request 9 (APPROVED - Linea C Soldadura)
  (24, 9,  34,   20, 'kg'),
  (25, 9,  35,   10, 'kg'),
  -- Request 10 (APPROVED - Linea B Pintura)
  (26, 10, 14,   20, 'lt'),
  (27, 10, 17,   15, 'pza'),
  -- Request 11 (REJECTED - Linea D Empaque)
  (28, 11, 22,   30, 'rollo'),
  (29, 11, 40,  150, 'par'),
  -- Request 12 (REJECTED - Linea A)
  (30, 12, 9,   400, 'pza'),
  (31, 12, 30,   20, 'lt'),
  -- Request 13 (REJECTED - Linea G)
  (32, 13, 47,   80, 'pza'),
  (33, 13, 45,  100, 'pza'),
  -- Request 14 (CANCELLED - Linea A)
  (34, 14, 19,   80, 'ml'),
  -- Request 15 (CANCELLED - Linea C)
  (35, 15, 34,   10, 'kg'),
  (36, 15, 36,   15, 'kg'),
  -- Request 16 (APPROVED desactivada - Linea B)
  (37, 16, 13,   30, 'lt'),
  (38, 16, 15,   10, 'lt'),
  -- Request 17 (APPROVED desactivada - Linea E)
  (39, 17, 39,   15, 'pza'),
  (40, 17, 37,    8, 'pza'),
  -- Request 18 (SUBMITTED - Linea A)
  (41, 18, 8,   600, 'pza'),
  (42, 18, 44,   60, 'pza'),
  (43, 18, 30,   15, 'lt'),
  -- Request 19 (SUBMITTED - Linea B)
  (44, 19, 13,   25, 'lt'),
  (45, 19, 16,   20, 'lt'),
  -- Request 20 (SUBMITTED - Linea C)
  (46, 20, 34,   30, 'kg'),
  (47, 20, 1,   200, 'kg'),
  -- Request 21 (SUBMITTED - Linea G)
  (48, 21, 46,  150, 'pza'),
  (49, 21, 5,   120, 'ml'),
  (50, 21, 6,    80, 'ml'),
  -- Request 22 (SUBMITTED - Linea H)
  (51, 22, 37,   12, 'pza'),
  (52, 22, 23,  200, 'pza'),
  -- Request 23 (SUBMITTED - Linea D)
  (53, 23, 49,   80, 'rollo'),
  (54, 23, 41,  120, 'par'),
  -- Request 24 (DRAFT - Linea A)
  (55, 24, 9,   300, 'pza'),
  (56, 24, 32,   10, 'kg'),
  -- Request 25 (DRAFT - Linea C)
  (57, 25, 35,   15, 'kg'),
  (58, 25, 34,   25, 'kg'),
  -- Request 26 (DRAFT - Linea E)
  (59, 26, 39,   20, 'pza'),
  (60, 26, 43,   40, 'pza'),
  -- Request 27 (DRAFT - Linea B)
  (61, 27, 14,   30, 'lt'),
  (62, 27, 17,   20, 'pza'),
  -- Request 28 (DRAFT - Linea G)
  (63, 28, 47,  100, 'pza'),
  (64, 28, 3,   100, 'kg'),
  -- Request 29 (DRAFT - Linea H)
  (65, 29, 37,    8, 'pza'),
  -- Request 30 (DRAFT - Linea A)
  (66, 30, 8,   400, 'pza'),
  (67, 30, 11,  200, 'pza'),
  -- Request 31 (DRAFT - Linea C)
  (68, 31, 36,   20, 'kg'),
  -- Request 32 (DRAFT - Linea D)
  (69, 32, 50,   25, 'kg'),
  (70, 32, 49,   60, 'rollo'),
  -- Request 33 (DRAFT - Linea F Mantenimiento)
  (71, 33, 38,   15, 'pza'),
  (72, 33, 33,   10, 'lt'),
  -- Request 34 (DRAFT - Linea G)
  (73, 34, 46,   80, 'pza'),
  (74, 34, 44,   40, 'pza'),
  -- Request 35 (DRAFT - Linea H)
  (75, 35, 23,  300, 'pza'),
  (76, 35, 24,   10, 'pza')
ON CONFLICT (item_id) DO NOTHING;

SELECT setval('production_request_items_item_id_seq', (SELECT MAX(item_id) FROM production_request_items));

-- =============================================================================
-- FIN DEL SCRIPT
-- Total: 15 usuarios, 50 materiales, 8 lineas, 20 proveedores,
--        80 recepciones, 35 ordenes de produccion, 76 items de orden
-- Contrasena de todos los usuarios: Admin1234!
-- =============================================================================
