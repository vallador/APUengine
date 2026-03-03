import sqlite3
from app.core.config import DB_ENGINE, DB_DESTINO

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=(), commit=False):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in {self.db_path}: {e}")
            return None

    def execute_lastrowid(self, query, params=()):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error in {self.db_path}: {e}")
            return None

    def fetch_one(self, query, params=()):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error in {self.db_path}: {e}")
            return None

# Singleton instances
engine_db = DBManager(DB_ENGINE)
destino_db = DBManager(DB_DESTINO)
