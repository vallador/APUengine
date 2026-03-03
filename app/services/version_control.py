from app.database.db_manager import engine_db

class VersionControl:
    @staticmethod
    def create_snapshot(variante_id, precio_antiguo, precio_nuevo, motivo="Update DB Sync"):
        query = "INSERT INTO snapshots_apu (variante_id, precio_antiguo, precio_nuevo, motivo_cambio) VALUES (?, ?, ?, ?)"
        return engine_db.execute_query(query, (variante_id, precio_antiguo, precio_nuevo, motivo), commit=True)

    @staticmethod
    def get_version_history(variante_id):
        return engine_db.execute_query("SELECT * FROM snapshots_apu WHERE variante_id = ? ORDER BY fecha DESC", (variante_id,))

    @staticmethod
    def get_latest_price_engine(variante_id):
        result = engine_db.fetch_one("SELECT precio_nuevo FROM snapshots_apu WHERE variante_id = ? ORDER BY fecha DESC LIMIT 1", (variante_id,))
        return result[0] if result else 0.0
