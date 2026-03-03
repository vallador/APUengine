from app.database.db_manager import engine_db

def seed_phase3_fixed():
    print("Re-seeding Phase 3 - Procedural Data...")
    try:
        # Check if already seeded
        chk = engine_db.fetch_one("SELECT COUNT(*) FROM cuadrillas")
        if chk and chk[0] > 0:
            print("Crews already exist.")
            return

        c1_id = engine_db.execute_lastrowid("INSERT INTO cuadrillas (nombre, descripcion) VALUES (?, ?)", 
                                         ("Cuadrilla AA (Oficial + Ayudante)", "Cuadrilla básica de obra"))
        c2_id = engine_db.execute_lastrowid("INSERT INTO cuadrillas (nombre, descripcion) VALUES (?, ?)", 
                                         ("Cuadrilla BB (2 Ayudantes)", "Cuadrilla de apoyo / limpieza"))
        
        engine_db.execute_query("INSERT INTO cuadrilla_items (cuadrilla_id, nivel_mo, cantidad) VALUES (?, ?, ?)", (c1_id, "Oficial", 1.0), commit=True)
        engine_db.execute_query("INSERT INTO cuadrilla_items (cuadrilla_id, nivel_mo, cantidad) VALUES (?, ?, ?)", (c1_id, "Ayudante", 1.0), commit=True)
        engine_db.execute_query("INSERT INTO cuadrilla_items (cuadrilla_id, nivel_mo, cantidad) VALUES (?, ?, ?)", (c2_id, "Ayudante", 2.0), commit=True)
        print("Phase 3 Seeding Complete.")
    except Exception as e:
        print(f"Seeding error: {e}")

if __name__ == "__main__":
    seed_phase3_fixed()
