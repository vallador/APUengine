from app.database.db_manager import engine_db

rows = engine_db.execute_query(
    "SELECT id, nombre, categoria, unidad_base FROM procesos ORDER BY categoria, nombre"
)
print(f"Total procesos: {len(rows)}\n")
for r in rows:
    print(f"[{r[0]:3}] {r[2]:28} | {r[3]:4} | {r[1][:80]}")
