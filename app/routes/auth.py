import sqlite3
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username dan password wajib diisi.'}), 400
        
    username = data['username'].strip()
    password = data['password']
    
    if not username or not password:
        return jsonify({'error': 'Username dan password tidak boleh kosong.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Periksa apakah username sudah ada
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username sudah terdaftar.'}), 400
        
    # Buat user baru
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, 'user')
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Registrasi berhasil! Silakan login.'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username dan password wajib diisi.'}), 400
        
    username = data['username'].strip()
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Username atau password salah.'}), 401
        
    # Set session
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    return jsonify({
        'message': 'Login berhasil!',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout berhasil!'})

@auth_bp.route('/session', methods=['GET'])
def get_session():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    return jsonify({'logged_in': False})

@auth_bp.route('/users', methods=['GET'])
def get_users():
    # Proteksi admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    
    users_list = []
    for u in users:
        users_list.append({
            'id': u['id'],
            'username': u['username'],
            'role': u['role'],
            'created_at': u['created_at']
        })
        
    return jsonify(users_list)
