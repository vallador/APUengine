from app.database.db_manager import engine_db

class YieldMotor:
    @staticmethod
    def get_base_yield(variante_id):
        query = "SELECT produccion_por_hora FROM rendimientos_base WHERE variante_id = ?"
        result = engine_db.fetch_one(query, (variante_id,))
        return result[0] if result else 1.0

    @staticmethod
    def get_adjustment_factors(variante_id):
        query = "SELECT f_altura, f_acceso, f_riesgo FROM factores_ajuste WHERE variante_id = ?"
        result = engine_db.fetch_one(query, (variante_id,))
        if result:
            return {'f_altura': result[0], 'f_acceso': result[1], 'f_riesgo': result[2]}
        return {'f_altura': 1.0, 'f_acceso': 1.0, 'f_riesgo': 1.0}

    @staticmethod
    def calculate_final_yield(variante_id):
        base = YieldMotor.get_base_yield(variante_id)
        factors = YieldMotor.get_adjustment_factors(variante_id)
        # Note Phase 3 requirement: Mutually exclusive location factors handled in GUI/Logic
        final_yield = base * (factors['f_altura'] * factors['f_acceso'] * factors['f_riesgo'])
        return final_yield

    @staticmethod
    def set_base_yield(variante_id, yield_value):
        query = "INSERT OR REPLACE INTO rendimientos_base (variante_id, produccion_por_hora) VALUES (?, ?)"
        engine_db.execute_query(query, (variante_id, yield_value), commit=True)

    @staticmethod
    def set_factors(variante_id, f_altura=1.0, f_acceso=1.0, f_riesgo=1.0):
        query = "INSERT OR REPLACE INTO factores_ajuste (variante_id, f_altura, f_acceso, f_riesgo) VALUES (?, ?, ?, ?)"
        engine_db.execute_query(query, (variante_id, f_altura, f_acceso, f_riesgo), commit=True)
