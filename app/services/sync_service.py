from app.database.db_manager import destino_db, engine_db
from app.core.apu_calculator import APUCalculator
from app.services.version_control import VersionControl
from app.core.description_generator import DescriptionGenerator

class SyncService:
    @staticmethod
    def update_destino_db():
        variants = engine_db.execute_query("SELECT id, nombre FROM variantes_proceso")
        for var in variants:
            v_id, nombre = var
            precio_antiguo = VersionControl.get_latest_price_engine(v_id)
            precio_comercial = APUCalculator.calculate_commercial_price(v_id)
            especificacion = DescriptionGenerator.generate_technical_description(v_id)
            query = "UPDATE actividades SET valor_unitario = ?, descripcion = ? WHERE id_actividad = ?"
            destino_db.execute_query(query, (precio_comercial, especificacion, v_id), commit=True)
            if abs(precio_antiguo - precio_comercial) > 0.01:
                VersionControl.create_snapshot(v_id, precio_antiguo, precio_comercial)
        return True
