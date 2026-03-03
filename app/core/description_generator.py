from app.database.db_manager import engine_db


class DescriptionGenerator:
    @staticmethod
    def add_alcance(variante_id, alcance):
        query = "INSERT INTO alcances_actividad (variante_id, alcance) VALUES (?, ?)"
        return engine_db.execute_lastrowid(query, (variante_id, alcance))

    # ─── Category-specific templates ──────────────────────────────────────────
    _NARRATIVES = {
        "Impermeabilización": (
            "Suministro y aplicación de sistema de impermeabilización para "
            "{objeto}, garantizando estanqueidad, durabilidad y protección "
            "contra humedad según especificaciones del fabricante."
        ),
        "Fachadas y Muros": (
            "Preparación de superficies y ejecución de {objeto} sobre "
            "fachada o muro, asegurando verticalidad, adherencia y acabado homogéneo "
            "conforme a la norma técnica aplicable."
        ),
        "Placas y Pisos": (
            "Ejecución de {objeto} sobre superficie horizontal, con preparación "
            "de base, aplicación controlada y verificación de nivel y resistencia "
            "según especificaciones técnicas del proyecto."
        ),
        "Pintura y Acabados": (
            "Preparación y aplicación de {objeto} sobre la superficie indicada, "
            "con lijado, imprimación y mano(s) de acabado según el sistema "
            "especificado, garantizando cobertura uniforme y durabilidad."
        ),
        "Cubiertas": (
            "Suministro e instalación de {objeto} en cubierta, incluyendo "
            "fijaciones, sellados de juntas y verificación de pendientes para "
            "correcta evacuación de aguas lluvias."
        ),
        "Estructuras": (
            "Suministro, corte, doblado e instalación de {objeto} conforme a "
            "planos estructurales y NTC vigentes, con amarre, distanciadores "
            "y revisión de recubrimientos mínimos."
        ),
        "Desmonte y Demolición": (
            "Desmonte controlado de {objeto}, incluyendo retiro de escombros, "
            "protección de elementos adyacentes y disposición final en sitio autorizado."
        ),
        "Aseo y Limpieza": (
            "Limpieza a fondo de {objeto} mediante métodos manuales o mecánicos, "
            "retiro de residuos, materiales sobrantes y entrega de área en óptimas condiciones."
        ),
    }
    _NARRATIVE_DEFAULT = (
        "Ejecución de {objeto} conforme a especificaciones técnicas del proyecto, "
        "con control de calidad en materiales, proceso y acabado final."
    )

    @staticmethod
    def generate_technical_description(variante_id, crew_id=None, location="Normal"):
        # 1. Core data
        query_var = """
            SELECT v.nombre, p.nombre, p.unidad_base, p.categoria
            FROM variantes_proceso v
            JOIN procesos p ON v.proceso_id = p.id
            WHERE v.id = ?
        """
        var_data = engine_db.fetch_one(query_var, (variante_id,))
        if not var_data:
            return ""
        v_name, p_name, unit, category = var_data

        # 2. Materials
        query_mat = """
            SELECT i.nombre, i.marca, i.unidad_uso, m.rendimiento
            FROM matriz_apu m
            JOIN insumos i ON m.insumo_id = i.id
            WHERE m.variante_id = ? AND i.tipo_item = 'Material'
            LIMIT 4
        """
        mats = engine_db.execute_query(query_mat, (variante_id,))

        # 3. Crew
        crew_label = "mano de obra calificada"
        if crew_id:
            c = engine_db.fetch_one("SELECT nombre FROM cuadrillas WHERE id = ?", (crew_id,))
            if c:
                crew_label = f"cuadrilla especializada ({c[0]})"

        # 4. Location
        loc_map = {
            "Alturas": "trabajo en alturas con EPP y equipo de protección colectiva",
            "Piso":    "trabajo a nivel de piso con equipo de apoyo",
            "Acceso":  "zonas de difícil acceso con logística especial",
            "Normal":  "condiciones estándar de obra",
        }
        loc_label = loc_map.get(location, "condiciones estándar de obra")

        # 5. Build narrative using the right template
        template = DescriptionGenerator._NARRATIVES.get(
            category, DescriptionGenerator._NARRATIVE_DEFAULT
        )
        # "objeto" = short process name (strip leading verb if already in template)
        objeto = p_name
        for verb in ["Aplicación de ", "Ejecución de ", "Suministro y aplicación de ",
                     "Suministro e instalación de ", "Desmonte de ", "Aseo y limpieza de "]:
            if objeto.startswith(verb):
                objeto = objeto[len(verb):]
                break
        narrative = template.format(objeto=objeto.lower())

        # 6. Materials list
        if mats:
            mat_parts = []
            for m in mats:
                rend = m[3] or 1.0
                line = f"{m[0]}"
                if m[1] and m[1].strip():
                    line += f" ({m[1]})"
                if m[2]:
                    line += f" a {rend} {m[2]}/und"
                mat_parts.append(line)
            mat_line = ", ".join(mat_parts)
        else:
            mat_line = "insumos de primera calidad según especificación"

        # 7. Compose output
        return (
            f"ACTIVIDAD: {p_name.upper()}\n"
            f"VARIANTE : {v_name}\n"
            f"CATEGORÍA: {category}  |  UNIDAD: {unit}\n\n"
            f"DESCRIPCIÓN TÉCNICA:\n{narrative}\n\n"
            f"CONDICIÓN DE OBRA: {loc_label.capitalize()}.\n"
            f"EJECUCIÓN: A cargo de {crew_label}.\n"
            f"MATERIALES PRINCIPALES: {mat_line}.\n"
            f"NOTA: Se garantiza limpieza del área, cumplimiento de normas "
            f"técnicas colombianas y entrega con tolerancias del proyecto."
        )
