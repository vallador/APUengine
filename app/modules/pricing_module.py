from app.database.db_manager import engine_db

class PricingModule:
    @staticmethod
    def add_insumo(nombre, marca, unidad_compra, unidad_uso, factor_conversion, tipo_item):
        query = """
            INSERT INTO insumos (nombre, marca, unidad_compra, unidad_uso, factor_conversion, tipo_item)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return engine_db.execute_lastrowid(query, (nombre, marca, unidad_compra, unidad_uso, factor_conversion, tipo_item))

    @staticmethod
    def update_precio(insumo_id, precio_real, fuente_url=None):
        query_hist = """
            INSERT INTO historial_precios (insumo_id, precio_real, fuente_url)
            VALUES (?, ?, ?)
        """
        engine_db.execute_query(query_hist, (insumo_id, precio_real, fuente_url), commit=True)
        return True

    @staticmethod
    def get_latest_price(insumo_id):
        query = """
            SELECT precio_real FROM historial_precios 
            WHERE insumo_id = ? 
            ORDER BY fecha_actualizacion DESC LIMIT 1
        """
        result = engine_db.fetch_one(query, (insumo_id,))
        return result[0] if result else 0.0

    @staticmethod
    def list_insumos():
        query = "SELECT * FROM insumos"
        return engine_db.execute_query(query)

    @staticmethod
    def get_latest_price_by_name(nombre):
        query = """
            SELECT hp.precio_real FROM historial_precios hp
            JOIN insumos i ON hp.insumo_id = i.id
            WHERE i.nombre = ? 
            ORDER BY hp.fecha_actualizacion DESC LIMIT 1
        """
        result = engine_db.fetch_one(query, (nombre,))
        return result[0] if result else 0.0

    @staticmethod
    def get_insumo_id_by_name(nombre):
        query = "SELECT id FROM insumos WHERE nombre = ?"
        result = engine_db.fetch_one(query, (nombre,))
        return result[0] if result else None
