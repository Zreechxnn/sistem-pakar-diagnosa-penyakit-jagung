import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import Config

def init_db():
    db_path = Config.DATABASE_PATH
    schema_path = os.path.join(Config.BASE_DIR, 'schema.sql')
    
    print(f"Menginisialisasi database di: {db_path}")
    print(f"Membaca skema dari: {schema_path}")
    
    if not os.path.exists(schema_path):
        print("Error: File schema.sql tidak ditemukan!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Jalankan schema.sql
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    
    # Seed default user jika belum ada
    # Admin
    cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', hashed_pw, 'admin')
        )
        print("User 'admin' berhasil dibuat (password: admin123).")
    else:
        print("User 'admin' sudah ada.")
        
    # Standard User
    cursor.execute("SELECT id FROM users WHERE username = ?", ('user',))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('user123')
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('user', hashed_pw, 'user')
        )
        print("User 'user' berhasil dibuat (password: user123).")
    else:
        print("User 'user' sudah ada.")
        
    conn.commit()
    conn.close()
    print("Inisialisasi database selesai!")

if __name__ == '__main__':
    init_db()
