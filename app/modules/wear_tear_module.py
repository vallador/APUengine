from app.database.db_manager import engine_db

class WearTearModule:
    @staticmethod
    def set_wear_config(nombre, tipo, costo_dia, factor_desgaste=0.05):
        query = "INSERT OR REPLACE INTO config_desgaste (nombre, tipo, costo_dia, factor_desgaste) VALUES (?, ?, ?, ?)"
        return engine_db.execute_query(query, (nombre, tipo, costo_dia, factor_desgaste), commit=True)

    @staticmethod
    def get_usage_cost(nombre):
        query = "SELECT costo_dia, factor_desgaste FROM config_desgaste WHERE nombre = ?"
        result = engine_db.fetch_one(query, (nombre,))
        if result:
            costo_dia, factor = result
            return (costo_dia * (1 + factor)) / 8
        return 0.0

    @staticmethod
    def list_wear_configs():
        return engine_db.execute_query("SELECT * FROM config_desgaste")
