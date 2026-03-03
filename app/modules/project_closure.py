from app.database.db_manager import engine_db
from app.core.yield_motor import YieldMotor

class ProjectClosure:
    @staticmethod
    def close_project_item(proyecto_nombre, variante_id, horas, cantidad):
        rendimiento_real = cantidad / horas if horas > 0 else 0
        rendimiento_teorico = YieldMotor.calculate_final_yield(variante_id)
        query = "INSERT INTO cierre_proyectos (proyecto_nombre, variante_id, horas_hombre_invertidas, cantidad_ejecutada, rendimiento_real) VALUES (?, ?, ?, ?, ?)"
        engine_db.execute_query(query, (proyecto_nombre, variante_id, horas, cantidad, rendimiento_real), commit=True)
        deviation = abs(rendimiento_real - rendimiento_teorico) / rendimiento_teorico if rendimiento_teorico > 0 else 0
        return {'rendimiento_real': rendimiento_real, 'rendimiento_teorico': rendimiento_teorico, 'deviation': deviation, 'alert': deviation > 0.15}

    @staticmethod
    def get_closure_history(variante_id=None):
        if variante_id: return engine_db.execute_query("SELECT * FROM cierre_proyectos WHERE variante_id = ? ORDER BY fecha_cierre DESC", (variante_id,))
        return engine_db.execute_query("SELECT * FROM cierre_proyectos ORDER BY fecha_cierre DESC")
