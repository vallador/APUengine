"""
Smart Data Corrector — Phase 10
Fixes: categories, units, and action verb in the nombre for all procesos.
"""
from app.database.db_manager import engine_db

# ─────────────────────────────────────────────────────────────
# RULE TABLES
# ─────────────────────────────────────────────────────────────

# (keyword_in_name_or_variant, correct_category, correct_unit)
RULES = [
    # === IMPERMEABILIZACIÓN ===
    (["impermeabiliz", "manto", "bituminoso", "tela asfaltica",
      "sikatop", "sikaflex", "sika transparent", "sikagard"],
     "Impermeabilización", "m2"),

    # Inyecciones con Sika → por longitud o global
    (["inyecci", "sika inject"],
     "Impermeabilización", "ML"),

    # === FACHADAS Y MUROS ===
    (["fachada", "revest", "estuco", "pañete", "empañete",
      "enchape", "ladrillo", "mosaico", "emboquillado", "mampostería"],
     "Fachadas y Muros", "m2"),

    # === PISOS Y PLACAS ===
    (["piso", "placa", "losa", "concreto", "mortero", "nivelacion",
      "contrapiso", "alistado"],
     "Placas y Pisos", "m2"),

    # === CUBIERTAS ===
    (["cubierta", "teja", "techo", "alero", "canaleta"],
     "Cubiertas", "m2"),

    # === PINTURA Y ACABADOS ===
    (["pintura", "esmalte", "latex", "corona", "pintuco",
      "pintuco", "recubrimiento", "barniz"],
     "Pintura y Acabados", "m2"),

    # === ESTRUCTURA / ACERO ===
    (["acero", "varilla", "hierro", "estructura metalica", "soldadura"],
     "Estructuras", "Kg"),

    # === DESMONTE / DEMOLICION ===
    (["desmonte", "demolicion", "retiro", "descapote"],
     "Desmonte y Demolición", "GL"),

    # === ASEO / LIMPIEZA ===
    (["aseo", "limpieza", "lavado"],
     "Aseo y Limpieza", "GL"),
]

# Wrong action verbs for surface/application work → should NOT start with "Suministro e instalación"
SURFACE_VERBS_WRONG = [
    "suministro e instalacion",
    "suministro e instalación",
    "suministro e ejecucion",
    "suministro e ejecución",
]

# Categories that are definitely surface/application (no "supply and install")
SURFACE_CATEGORIES = {
    "Impermeabilización", "Fachadas y Muros", "Placas y Pisos",
    "Pintura y Acabados", "Cubiertas", "Aseo y Limpieza", "Desmonte y Demolición"
}

# Proper verb replacements by category
VERB_MAP = {
    "Impermeabilización":     "Aplicación de",
    "Fachadas y Muros":       "Ejecución de",
    "Placas y Pisos":         "Ejecución de",
    "Pintura y Acabados":     "Aplicación de",
    "Cubiertas":              "Instalación de",
    "Aseo y Limpieza":        "Aseo y limpieza de",
    "Desmonte y Demolición":  "Desmonte de",
    "Estructuras":            "Suministro e instalación de",
}

# ─────────────────────────────────────────────────────────────
# CORRECTION FUNCTION
# ─────────────────────────────────────────────────────────────

def determine_cat_unit(nombre, cat_actual, unit_actual):
    text = nombre.lower()
    for keywords, cat, unit in RULES:
        if any(kw in text for kw in keywords):
            return cat, unit
    # fallback: keep existing but normalise obvious GL mismatches
    return cat_actual, unit_actual


def fix_nombre(nombre, categoria):
    """Remove wrong intro verbs and add the correct one if the name is bare."""
    n = nombre.strip()
    n_lower = n.lower()

    # Remove bad verbs at start
    for bad in SURFACE_VERBS_WRONG:
        if n_lower.startswith(bad):
            n = n[len(bad):].strip(" ,-:")
            break

    # Ensure name starts with correct verb for surface categories
    correct_verb = VERB_MAP.get(categoria)
    if correct_verb:
        verbs_present = any(n.lower().startswith(v.lower()) for v in VERB_MAP.values())
        if not verbs_present:
            n = correct_verb + " " + n[0].lower() + n[1:]

    # Title-case cleanup (first letter capital only)
    return n[0].upper() + n[1:] if n else nombre


# ─────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────

rows = engine_db.execute_query("SELECT id, nombre, categoria, unidad_base FROM procesos")
updates = 0
print(f"Processing {len(rows)} procesos...\n")

for pid, nombre, cat, unit in rows:
    new_cat, new_unit = determine_cat_unit(nombre, cat, unit)
    new_nombre = fix_nombre(nombre, new_cat)

    changed = (new_cat != cat) or (new_unit != unit) or (new_nombre != nombre)
    if changed:
        engine_db.execute_query(
            "UPDATE procesos SET nombre=?, categoria=?, unidad_base=? WHERE id=?",
            (new_nombre, new_cat, new_unit, pid), commit=True
        )
        print(f"[{pid:3}] BEFORE: {cat:25} | {unit:4} | {nombre[:50]}")
        print(f"      AFTER:  {new_cat:25} | {new_unit:4} | {new_nombre[:50]}")
        print()
        updates += 1

print(f"\n✅ Updated {updates} / {len(rows)} procesos.")
