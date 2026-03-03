from app.database.db_manager import engine_db

from app.core.config import LABOR_FACTOR

class LaborModule:
    @staticmethod
    def set_labor_config(nivel, salario_base, factor_social=LABOR_FACTOR):
        valor_hora = (salario_base * factor_social) / 240
        query = """
            INSERT OR REPLACE INTO config_mano_de_obra (nivel, salario_base, factor_social, valor_hora)
            VALUES (?, ?, ?, ?)
        """
        return engine_db.execute_query(query, (nivel, salario_base, factor_social, valor_hora), commit=True)

    @staticmethod
    def get_labor_cost(nivel):
        query = "SELECT valor_hora FROM config_mano_de_obra WHERE nivel = ?"
        result = engine_db.fetch_one(query, (nivel,))
        return result[0] if result else 0.0

    @staticmethod
    def list_labor_configs():
        return engine_db.execute_query("SELECT * FROM config_mano_de_obra")
