import re
from app.database.db_manager import engine_db

class SmartProcessor:
    @staticmethod
    def extract_activity_name(text):
        # Case normalization and clean up
        match = re.search(r'(?:SUMINISTRO|EJECUCIÓN|LAVADO|DESMANCHE|ELABORACIÓN|REPARACIÓN|CONSTRUCCIÓN|INSTALACIÓN)\s+(?:Y\s+)?(?:EJECUCIÓN|INSTALACIÓN|COLOCACION|PREPARACION)?\s*DE\s+(.*?)(?:\.|\n|INCLUYE|COMPRENDE|,|$)', text, re.I)
        if match:
            raw_name = match.group(1).strip()
        else:
            raw_name = text.split('\n')[0][:100].strip()
        
        # Normalize to Title Case and fix common acronyms/caps
        name = raw_name.lower().title()
        return name

    @staticmethod
    def get_category(name, text):
        content = (name + " " + text).lower()
        if any(w in content for w in ["fachada", "muro"]): return "Fachadas y Muros"
        if any(w in content for w in ["placa", "losa", "piso"]): return "Placas y Pisos"
        if any(w in content for w in ["impermeabiliza", "sika", "manto"]): return "Impermeabilización"
        if any(w in content for w in ["cubierta", "teja", "techo"]): return "Cubiertas"
        if any(w in content for w in ["pintura", "estuco", "resane"]): return "Pintura y Acabados"
        return "Otros / Estándar"

    @staticmethod
    def get_unit(name, text):
        content = (name + " " + text).lower()
        # Area based
        if any(w in content for w in ["fachada", "muro", "placa", "losa", "piso", "pintura", "impermeabiliza", "aplicacion"]): 
            return "m2"
        # Volume based (Liquids)
        if any(w in content for w in ["sika", "litros", "liquido", "resina", "sikaflex", "inyec", "aditivo"]): 
            return "L"
        # Length based
        if any(w in content for w in ["metro lineal", "ml", "viga", "bordillo", "junta", "dilata"]):
            return "ML"
        return "GL"

    @staticmethod
    def proceduralize_description(text):
        # Normalize incoming text case
        text_lines = [line.strip() for line in text.split('\n') if line.strip()]
        normalized_text = "\n".join(text_lines)

        # 1. Replace dynamic list sections with placeholders
        p_text = normalized_text
        
        # Replace materials list if found
        p_text = re.sub(r'(?:Insumos|Materiales|Insumo|Material|Productos?):\s*(.*?)(?:\.|\n|NO INCLUYE|$)', r'{{materiales}}.\n', p_text, flags=re.I | re.S)
        
        # Replace labor/crew if found
        p_text = re.sub(r'(?:Cobra|Mano de obra|Cuadrilla|Personal):\s*(.*?)(?:\.|\n|NO INCLUYE|$)', r'{{cuadrilla}}.\n', p_text, flags=re.I | re.S)
        
        # Replace equipment/tools if found
        p_text = re.sub(r'(?:Equipos|Herramientas|Equipo|Herramienta|Adicionales?):\s*(.*?)(?:\.|\n|NO INCLUYE|$)', r'{{equipos_y_herramientas}}.\n', p_text, flags=re.I | re.S)
        
        # Replace exclusions
        p_text = p_text.replace('{{EXCLUSIONES}}', '{{exclusiones}}')
        
        prefix = "Actividad: {{proceso}} ({{variante}}). Sitio: {{sitio}}.\n"
        if not p_text.startswith("Actividad:"):
            p_text = prefix + p_text
            
        return p_text

    @staticmethod
    def create_entities_from_excel(df):
        count_p, count_v = 0, 0
        for _, row in df.iterrows():
            orig = str(row['Descripcion_Original'])
            std = str(row['Descripcion_Estandarizada'])
            name = SmartProcessor.extract_activity_name(orig)
            category = SmartProcessor.get_category(name, std)
            unit = SmartProcessor.get_unit(name, std)
            
            # Create Proceso
            exists_p = engine_db.fetch_one("SELECT id FROM procesos WHERE nombre = ?", (name,))
            if not exists_p:
                p_id = engine_db.execute_lastrowid("INSERT INTO procesos (nombre, categoria, unidad_base) VALUES (?, ?, ?)", (name, category, unit))
                count_p += 1
            else:
                # Update category and unit
                p_id = exists_p[0]
                engine_db.execute_query("UPDATE procesos SET categoria = ?, unidad_base = ? WHERE id = ?", (category, unit, p_id), commit=True)
                
            # Create Variante
            variant_name = "Proceso Estándar"
            exists_v = engine_db.fetch_one("SELECT id FROM variantes_proceso WHERE proceso_id = ? AND nombre = ?", (p_id, variant_name))
            if not exists_v:
                engine_db.execute_query("INSERT INTO variantes_proceso (proceso_id, nombre) VALUES (?, ?)", (p_id, variant_name), commit=True)
                count_v += 1
                
        return count_p, count_v
