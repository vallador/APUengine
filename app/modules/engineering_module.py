from app.database.db_manager import engine_db

class EngineeringModule:
    @staticmethod
    def add_proceso(nombre, unidad_base, categoria):
        query = "INSERT INTO procesos (nombre, unidad_base, categoria) VALUES (?, ?, ?)"
        return engine_db.execute_lastrowid(query, (nombre, unidad_base, categoria))

    @staticmethod
    def add_variante(proceso_id, nombre, especificacion_tecnica):
        query = "INSERT INTO variantes_proceso (proceso_id, nombre, especificacion_tecnica) VALUES (?, ?, ?)"
        return engine_db.execute_lastrowid(query, (proceso_id, nombre, especificacion_tecnica))

    @staticmethod
    def add_to_matriz(variante_id, insumo_id, rendimiento, consumo_unitario=1.0):
        query = "INSERT INTO matriz_apu (variante_id, insumo_id, rendimiento, consumo_unitario) VALUES (?, ?, ?, ?)"
        return engine_db.execute_lastrowid(query, (variante_id, insumo_id, rendimiento, consumo_unitario))

    @staticmethod
    def get_matriz(variante_id):
        query = """
            SELECT 
                m.insumo_id, i.nombre, i.tipo_item, m.rendimiento, m.consumo_unitario,
                -- Traemos los datos de precio y presentación aquí para evitar el bucle
                COALESCE(i.precio_venta, 0.0),
                COALESCE(i.descuento_porcentaje, 0.0),
                COALESCE(i.contenido_presentacion, 1.0),
                COALESCE(i.desperdicio_porcentaje, 0.0)
            FROM matriz_apu m
            JOIN insumos i ON m.insumo_id = i.id
            WHERE m.variante_id = ?
        """
        return engine_db.execute_query(query, (variante_id,))
    @staticmethod
    def get_variante_details(variante_id):
        query = """
            SELECT v.id, v.nombre, v.especificacion_tecnica, p.nombre as proceso_nombre, p.unidad_base
            FROM variantes_proceso v
            JOIN procesos p ON v.proceso_id = p.id
            WHERE v.id = ?
        """
        return engine_db.fetch_one(query, (variante_id,))

    @staticmethod
    def save_variante_matriz(variante_id, items):
        # items: list of (insumo_id, rendimiento)
        engine_db.execute_query("DELETE FROM matriz_apu WHERE variante_id = ?", (variante_id,), commit=True)
        for ins_id, rend in items:
            EngineeringModule.add_to_matriz(variante_id, ins_id, rend)
        return True

    @staticmethod
    def update_variante_desc(variante_id, text):
        query = "UPDATE variantes_proceso SET especificacion_tecnica = ? WHERE id = ?"
        engine_db.execute_query(query, (text, variante_id), commit=True)
