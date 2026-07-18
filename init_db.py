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

    # Seed symptoms jika belum ada
    cursor.execute("SELECT COUNT(*) FROM symptoms")
    if cursor.fetchone()[0] == 0:
        try:
            from app.services.disease_repo import DiseaseRepository
            repo = DiseaseRepository()
            kode = 1
            for disease_name, symptoms in repo.get_symptom_groups():
                for symptom in symptoms:
                    cursor.execute(
                        "INSERT INTO symptoms (code, description, disease_name) VALUES (?, ?, ?)",
                        (f'G{kode}', symptom, disease_name)
                    )
                    kode += 1
            print("Data gejala (symptoms) berhasil di-seed.")
        except Exception as e:
            print(f"Gagal seeding symptoms: {e}")

    # Seed diseases jika belum ada
    cursor.execute("SELECT COUNT(*) FROM diseases")
    if cursor.fetchone()[0] == 0:
        try:
            from app.services.disease_repo import DiseaseRepository
            repo = DiseaseRepository()
            for code, info in repo._disease_details.items():
                cursor.execute(
                    "INSERT INTO diseases (code, name, description, recommendation) VALUES (?, ?, ?, ?)",
                    (code, info['nama'], info['deskripsi'], info['rekomendasi'])
                )
            print("Data penyakit (diseases) berhasil di-seed.")
        except Exception as e:
            print(f"Gagal seeding diseases: {e}")

    # Seed rules jika belum ada
    cursor.execute("SELECT COUNT(*) FROM rules")
    if cursor.fetchone()[0] == 0:
        try:
            from app.services.knowledge_base import KnowledgeBase
            kb = KnowledgeBase(Config.KNOWLEDGE_BASE_PATH)
            for r in kb.get_rules():
                antecedents_str = ",".join(r.get_antecedents())
                consequent = r.get_consequent()
                cursor.execute(
                    "INSERT INTO rules (antecedents, consequent) VALUES (?, ?)",
                    (antecedents_str, consequent)
                )
            print("Data aturan (rules) berhasil di-seed.")
        except Exception as e:
            print(f"Gagal seeding rules: {e}")
        
    conn.commit()
    conn.close()
    print("Inisialisasi database selesai!")

if __name__ == '__main__':
    init_db()
