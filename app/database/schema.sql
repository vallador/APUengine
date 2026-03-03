-- APU Engine technical Database Schema (engine.db)

-- 1. Insumos (Master Catalog)
CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    marca TEXT,
    unidad_compra TEXT,
    unidad_uso TEXT,
    factor_conversion REAL DEFAULT 1.0,
    tipo_item TEXT CHECK(tipo_item IN ('Material', 'Mano de Obra', 'Equipo', 'Herramienta'))
);

-- 2. Historial de Precios
CREATE TABLE IF NOT EXISTS historial_precios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER,
    precio_real REAL NOT NULL, -- Costo directo
    precio_comercial REAL,      -- Precio con margen (opcional aquí, usualmente calculado)
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fuente_url TEXT,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 3. Scraper Configuration
CREATE TABLE IF NOT EXISTS scraper_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER,
    url TEXT NOT NULL,
    selector_css TEXT,
    xpath TEXT,
    frecuencia_dias INTEGER DEFAULT 7,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 4. Procesos y Variantes
CREATE TABLE IF NOT EXISTS procesos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    unidad_base TEXT,
    categoria TEXT
);

CREATE TABLE IF NOT EXISTS variantes_proceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER,
    nombre TEXT NOT NULL,
    especificacion_tecnica TEXT,
    FOREIGN KEY (proceso_id) REFERENCES procesos(id)
);

-- 5. Matriz APU (The Pivot Table)
CREATE TABLE IF NOT EXISTS matriz_apu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER,
    insumo_id INTEGER,
    consumo_unitario REAL NOT NULL,
    FOREIGN KEY (variante_id) REFERENCES variantes_proceso(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- 6. Rendimientos Dinámicos
CREATE TABLE IF NOT EXISTS rendimientos_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER UNIQUE,
    produccion_por_hora REAL NOT NULL,
    FOREIGN KEY (variante_id) REFERENCES variantes_proceso(id)
);

CREATE TABLE IF NOT EXISTS factores_ajuste (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER UNIQUE,
    f_altura REAL DEFAULT 1.0,
    f_acceso REAL DEFAULT 1.0,
    f_riesgo REAL DEFAULT 1.0,
    FOREIGN KEY (variante_id) REFERENCES variantes_proceso(id)
);

-- 7. Snapshots and Versioning
CREATE TABLE IF NOT EXISTS snapshots_apu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER,
    precio_antiguo REAL,
    precio_nuevo REAL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo_cambio TEXT,
    FOREIGN KEY (variante_id) REFERENCES variantes_proceso(id)
);

-- 9. Configuration: Mano de Obra (Salaries & Benefits)
CREATE TABLE IF NOT EXISTS config_mano_de_obra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel TEXT NOT NULL, -- e.g., 'Oficial', 'Ayudante'
    salario_base REAL NOT NULL,
    factor_social REAL DEFAULT 1.75, -- Factores de seguridad social y demas (1.75 = 75% prestaciones)
    valor_hora REAL, -- Calculado (Salario * Factor / 240 horas laborables mes)
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 10. Configuration: Herramientas y Equipos (Wear/Desgaste)
CREATE TABLE IF NOT EXISTS config_desgaste (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('Herramienta', 'Equipo')),
    costo_dia REAL,
    factor_desgaste REAL DEFAULT 0.05, -- 5% de desgaste estandar
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 11. Relación Actividad-Insumo (Variabilidad)
-- (Ya tenemos matriz_apu, pero ampliaremos para incluir MO y Herramientas si se prefiere separar)
-- Se mantendrá en matriz_apu usando el campo tipo_item.

-- 12. Dynamic Descriptions & Scope
CREATE TABLE IF NOT EXISTS alcances_actividad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variante_id INTEGER,
    alcance TEXT NOT NULL,
    FOREIGN KEY (variante_id) REFERENCES variantes_proceso(id)
);

-- 13. Scraper Metadata Extension
ALTER TABLE scraper_config ADD COLUMN last_scraped_price REAL;
ALTER TABLE scraper_config ADD COLUMN status TEXT DEFAULT 'Pending';

-- 14. Cuadrillas (Labor Crews)
CREATE TABLE IF NOT EXISTS cuadrillas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS cuadrilla_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cuadrilla_id INTEGER,
    nivel_mo TEXT, -- Links to config_mano_de_obra.nivel
    cantidad REAL DEFAULT 1.0, -- e.g. 1 Oficial, 2 Ayudantes
    FOREIGN KEY (cuadrilla_id) REFERENCES cuadrillas(id)
);
