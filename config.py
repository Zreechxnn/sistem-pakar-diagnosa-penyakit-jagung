import os
import shutil
from dotenv import load_dotenv

# Muat variabel lingkungan dari .env.local jika ada (untuk pengembangan lokal)
# Kemudian .env sebagai fallback
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env.local'))
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, 'knowledge_base.txt')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-sistem-pakar-secret-key-123')
    
    # URL Koneksi PostgreSQL (misal Supabase)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Konfigurasi path database untuk Vercel (read-only filesystem)
    # Salin database ke /tmp (yang writable) saat dijalankan di Vercel.
    # Catatan: /tmp bersifat ephemeral (sementara) dan datanya akan ter-reset saat cold start.
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        DATABASE_PATH = '/tmp/sistem_pakar.db'
        original_db_path = os.path.join(BASE_DIR, 'sistem_pakar.db')
        if os.path.exists(original_db_path) and not os.path.exists(DATABASE_PATH):
            try:
                shutil.copy2(original_db_path, DATABASE_PATH)
            except Exception as e:
                print(f"Gagal menyalin database ke /tmp: {e}")
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, 'sistem_pakar.db')