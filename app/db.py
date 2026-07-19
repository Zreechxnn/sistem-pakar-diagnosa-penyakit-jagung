import os
import sqlite3
from config import Config

# Coba impor psycopg2 untuk PostgreSQL
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class DictRowWrapper:
    """Wrapper untuk row hasil query agar kompatibel dengan sqlite3.Row (akses indeks & key)"""
    def __init__(self, data_dict):
        self._dict = data_dict
        self._tuple = tuple(data_dict.values())
        self._keys = list(data_dict.keys())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tuple[key]
        return self._dict[key]

    def keys(self):
        return self._keys

    def __repr__(self):
        return repr(self._dict)

class CursorWrapper:
    def __init__(self, cursor, is_pg):
        self._cursor = cursor
        self._is_pg = is_pg

    def execute(self, sql, params=None):
        if self._is_pg:
            # Ubah ? ke %s untuk query parameter PostgreSQL
            sql = sql.replace('?', '%s')
            if params is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, params)
        else:
            if params is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, params)
        return self

    def executemany(self, sql, seq_of_parameters):
        if self._is_pg:
            sql = sql.replace('?', '%s')
        self._cursor.executemany(sql, seq_of_parameters)
        return self

    def executescript(self, script_sql):
        if self._is_pg:
            # PostgreSQL menggunakan execute() untuk menjalankan banyak statement SQL
            # Terlebih dahulu, lakukan penyesuaian tipe data schema dari SQLite ke PostgreSQL
            script_sql = script_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            script_sql = script_sql.replace("DATETIME", "TIMESTAMP")
            self._cursor.execute(script_sql)
        else:
            self._cursor.executescript(script_sql)
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._is_pg:
            return DictRowWrapper(row)
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._is_pg:
            return [DictRowWrapper(r) for r in rows]
        return rows

    def __getattr__(self, name):
        return getattr(self._cursor, name)

class ConnectionWrapper:
    def __init__(self, conn, is_pg):
        self._conn = conn
        self._is_pg = is_pg
        self.row_factory = None

    def cursor(self):
        if self._is_pg:
            raw_cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return CursorWrapper(raw_cursor, is_pg=True)
        else:
            raw_cursor = self._conn.cursor()
            return CursorWrapper(raw_cursor, is_pg=False)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)

class Database:
    @staticmethod
    def is_postgres():
        db_url = Config.DATABASE_URL
        return db_url is not None and db_url.startswith(("postgresql://", "postgres://"))

    @staticmethod
    def get_connection():
        if Database.is_postgres():
            if not PSYCOPG2_AVAILABLE:
                raise ImportError(
                    "psycopg2 tidak terinstall. Pastikan psycopg2-binary ditambahkan ke requirements.txt "
                    "dan telah diinstall menggunakan: pip install psycopg2-binary"
                )
            db_url = Config.DATABASE_URL
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            
            conn = psycopg2.connect(db_url)
            return ConnectionWrapper(conn, is_pg=True)
        else:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            return ConnectionWrapper(conn, is_pg=False)
