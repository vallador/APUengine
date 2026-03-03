import sqlite3

def get_specific_schemas(db_path, tables):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for table_name in tables:
            print(f"--- Table: {table_name} ---")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            if not columns:
                print("  Table not found.")
                continue
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get SQL CREATE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            sql = cursor.fetchone()
            if sql:
                print(f"  SQL: {sql[0]}")
            
            # Sample Data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
            rows = cursor.fetchall()
            print("  Sample Data:")
            for row in rows:
                print(f"    {row}")
            print("\n")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_specific_schemas('destino.db', ['actividades', 'aiu_values', 'insumos', 'precios'])
