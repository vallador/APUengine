from app.database.db_manager import engine_db

def verify_templates():
    print("Verifying Standardized Templates...")
    count = engine_db.fetch_one("SELECT COUNT(*) FROM referentes_descripciones")[0]
    print(f"Total templates in DB: {count}")
    
    sample = engine_db.fetch_one("SELECT titulo, contenido_estandar FROM referentes_descripciones LIMIT 1")
    if sample:
        print(f"Sample Title: {sample[0]}")
        print(f"Sample Content Length: {len(sample[1])}")
        print("Success!")
    else:
        print("Error: No templates found in DB.")

if __name__ == "__main__":
    verify_templates()
