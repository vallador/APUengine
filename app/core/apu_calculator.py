from app.core.config import LABOR_FACTOR, AIU_DEFAULTS
from app.database.db_manager import engine_db, destino_db
from app.modules.engineering_module import EngineeringModule
from app.modules.labor_module import LaborModule
from app.core.yield_motor import YieldMotor

class APUCalculator:
    @staticmethod
    def calculate_technical_cost(variante_id, crew_id=None, manual_yield=None):
        matriz = EngineeringModule.get_matriz(variante_id)
        costo_directo = 0.0
        has_matrix_labor = False
        
        # 1. Base Matrix Items
        for item in (matriz or []):
        # item ahora tiene 9 columnas en lugar de 5
            (insumo_id, nombre, tipo_item, rend_act, _,p_v, dto, cont, desp) = item
            rend_act = rend_act or 1.0
            
            # p_real = p_v * (1 - dto / 100.0) # User clarified: Use Sales Price for APU
            
            if tipo_item == 'Material':
                # Consumo unitario (L/m2) + Desperdicio
                unit_cons = (1.0 / max(rend_act, 0.001)) * (1 + desp / 100.0)
                # Cantidad in presentation unit (e.g. gal/m2)
                cant_m2 = unit_cons / max(cont, 0.001)
                item_cost_m2 = p_v * cant_m2
            else:
                # Direct formula for Equipment, Labor, etc. (Price / Yield)
                item_cost_m2 = p_v / max(rend_act, 0.001)
            
            if tipo_item == 'Mano de Obra': 
                has_matrix_labor = True
            
            costo_directo += item_cost_m2
            
        # 2. Add Crew Cost if selected AND no manual labor exists in the matrix
        if crew_id and not has_matrix_labor:
            crew_items = engine_db.execute_query("SELECT nivel_mo, cantidad FROM cuadrilla_items WHERE cuadrilla_id = ?", (crew_id,))
            costo_hora_crew = 0.0
            for nivel, qty in (crew_items or []):
                costo_hora_crew += LaborModule.get_labor_cost(nivel) * qty
            
            # Use manual yield if provided, else calculate from motor
            if manual_yield:
                rendimiento = manual_yield
            else:
                rendimiento = YieldMotor.calculate_final_yield(variante_id)
            
            horas_por_unidad = 1.0 / rendimiento if rendimiento > 0 else 0
            costo_directo += (costo_hora_crew * horas_por_unidad)
            
        return costo_directo

    @staticmethod
    def get_aiu_factors():
        query = "SELECT administracion, imprevistos, utilidad FROM aiu_values LIMIT 1"
        result = destino_db.fetch_one(query)
        if result:
            return {'admin': result[0] / 100.0, 'impr': result[1] / 100.0, 'util': result[2] / 100.0}
        return AIU_DEFAULTS

    @staticmethod
    def calculate_commercial_price(variante_id, crew_id=None, manual_yield=None):
        costo_tecnico = APUCalculator.calculate_technical_cost(variante_id, crew_id, manual_yield)
        aiu = APUCalculator.get_aiu_factors()
        total_aiu_factor = 1.0 + aiu['admin'] + aiu['impr'] + aiu['util']
        return costo_tecnico * total_aiu_factor
