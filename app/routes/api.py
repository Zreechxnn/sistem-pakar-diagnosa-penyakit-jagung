from flask import Blueprint, request, jsonify, session
import sqlite3
import json
from app.services.disease_repo import DiseaseRepository
from app.services.knowledge_base import KnowledgeBase
from app.services.inference import InferenceEngine
from app.services.ml_model import MLDiseaseClassifier
from config import Config
import os

api_bp = Blueprint('api', __name__)

# Instansiasi service (singleton)
repo = DiseaseRepository()
kb = KnowledgeBase(Config.KNOWLEDGE_BASE_PATH)
engine = InferenceEngine()

# ML Classifier — dilatih dari CSV
_csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'training_data.csv')
ml_classifier = MLDiseaseClassifier(_csv_path)

# Mapping label ML → kode penyakit
_LABEL_TO_CODE = {
    'Bulai':       'P001',
    'Blight':      'P002',
    'Leaf Rust':   'P003',
    'Burn':        'P004',
    'Stem Borer':  'P005',
    'Cob Borer':   'P006',
}

@api_bp.route('/symptoms', methods=['GET'])
def get_symptoms():
    """Mengembalikan semua gejala yang bisa dipilih, dikelompokkan per penyakit."""
    groups = []
    kode = 1
    for disease_name, symptoms in repo.get_symptom_groups():
        symptoms_list = []
        for symptom in symptoms:
            symptoms_list.append({
                'code': f'G{kode}',
                'description': symptom
            })
            kode += 1
        groups.append({
            'disease': disease_name,
            'symptoms': symptoms_list
        })
    return jsonify(groups)


@api_bp.route('/diagnose', methods=['POST'])
def diagnose():
    """
    Menerima JSON dengan key 'symptoms' berisi list kode gejala (string).
    Contoh body: { "symptoms": ["G1", "G4", "G10"] }
    Menggunakan ML (Random Forest) untuk diagnosis dengan confidence score.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Akses ditolak. Anda harus login terlebih dahulu untuk melakukan diagnosa.'}), 401

    data = request.get_json()
    if not data or 'symptoms' not in data:
        return jsonify({'error': 'Harap sertakan "symptoms" dalam body.'}), 400

    selected_codes = set(data['symptoms'])
    if not selected_codes:
        return jsonify({'error': 'Minimal satu gejala harus dipilih.'}), 400

    # Validasi kode gejala
    valid_codes = {item['code'] for item in repo.get_all_symptoms_with_codes()}
    invalid = selected_codes - valid_codes
    if invalid:
        return jsonify({'error': f'Kode gejala tidak valid: {", ".join(sorted(invalid))}'}), 400

    # ✅ Gunakan ML Classifier
    if not ml_classifier.is_trained:
        return jsonify({'error': f'Model ML tidak siap: {ml_classifier.training_error}'}), 500

    ml_results = ml_classifier.predict(selected_codes)

    # Bangun respons diagnosis dengan info penyakit + confidence
    hasil = []
    for pred in ml_results:
        label = pred['label']
        confidence = pred['confidence']
        code = _LABEL_TO_CODE.get(label)
        if not code:
            continue
        info = repo.get_disease_info(code)
        hasil.append({
            'code': code,
            'nama': info['nama'],
            'deskripsi': info['deskripsi'],
            'rekomendasi': info['rekomendasi'],
            'confidence': confidence,
            'label': label
        })

    # Juga jalankan forward chaining sebagai fallback/tambahan
    inferred = engine.forward_chain(kb.get_rules(), selected_codes)
    penyakit_fc = sorted([k for k in inferred if k.startswith('P')])

    # Gejala yang dikirim user beserta deskripsinya
    reported_symptoms = [
        {'code': c, 'description': repo.get_gejala_description(c)}
        for c in sorted(selected_codes)
    ]

    response = {
        'reported_symptoms': reported_symptoms,
        'diagnosis': hasil,
        'total_penyakit_terdeteksi': len(hasil),
        'forward_chain_codes': penyakit_fc,
        'ml_active': ml_classifier.is_trained
    }

    # Simpan riwayat jika user sudah login
    if 'user_id' in session:
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diagnoses (user_id, symptoms, result) VALUES (?, ?, ?)",
                (session['user_id'], json.dumps(reported_symptoms), json.dumps(hasil))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving diagnosis: {e}")

    return jsonify(response)


@api_bp.route('/diagnoses', methods=['GET'])
def get_diagnoses():
    """Mengembalikan daftar riwayat diagnosa user yang sedang login."""
    if 'user_id' not in session:
        return jsonify({'error': 'Akses ditolak. Harap login terlebih dahulu.'}), 401
    
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, symptoms, result, created_at FROM diagnoses WHERE user_id = ? ORDER BY created_at DESC",
            (session['user_id'],)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for r in rows:
            history.append({
                'id': r['id'],
                'symptoms': json.loads(r['symptoms']),
                'result': json.loads(r['result']),
                'created_at': r['created_at']
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': f'Gagal mengambil riwayat: {str(e)}'}), 500


@api_bp.route('/diagnoses/<int:diagnose_id>', methods=['DELETE'])
def delete_diagnose(diagnose_id):
    """Menghapus entri riwayat diagnosa."""
    if 'user_id' not in session:
        return jsonify({'error': 'Akses ditolak. Harap login terlebih dahulu.'}), 401
        
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Pastikan data milik user tersebut
        cursor.execute("SELECT id FROM diagnoses WHERE id = ? AND user_id = ?", (diagnose_id, session['user_id']))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Riwayat tidak ditemukan atau tidak memiliki akses.'}), 404
            
        cursor.execute("DELETE FROM diagnoses WHERE id = ? AND user_id = ?", (diagnose_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Riwayat diagnosa berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': f'Gagal menghapus riwayat: {str(e)}'}), 500


@api_bp.route('/ml-status', methods=['GET'])
def ml_status():
    """Cek status ML model."""
    return jsonify({
        'is_trained': ml_classifier.is_trained,
        'error': ml_classifier.training_error
    })


# =====================================================================
# ADMIN PANEL ENDPOINTS
# =====================================================================

def is_admin():
    return 'user_id' in session and session.get('role') == 'admin'

# 1. Kelola Gejala (Symptoms)
@api_bp.route('/admin/symptoms', methods=['GET'])
def admin_get_symptoms():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, description, disease_name FROM symptoms ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/symptoms', methods=['POST'])
def admin_add_symptom():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'code' not in data or 'description' not in data or 'disease_name' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    code = data['code'].strip().upper()
    description = data['description'].strip()
    disease_name = data['disease_name'].strip()

    if not code or not description or not disease_name:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if repo.add_symptom(code, description, disease_name):
        return jsonify({'message': 'Gejala berhasil ditambahkan.'}), 201
    return jsonify({'error': 'Gagal menambahkan gejala. Kode mungkin sudah terdaftar.'}), 400

@api_bp.route('/admin/symptoms/<string:code>', methods=['PUT'])
def admin_update_symptom(code):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'description' not in data or 'disease_name' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    description = data['description'].strip()
    disease_name = data['disease_name'].strip()

    if not description or not disease_name:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if repo.update_symptom(code, description, disease_name):
        return jsonify({'message': 'Gejala berhasil diperbarui.'})
    return jsonify({'error': 'Gagal memperbarui gejala.'}), 400

@api_bp.route('/admin/symptoms/<string:code>', methods=['DELETE'])
def admin_delete_symptom(code):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    if repo.delete_symptom(code):
        return jsonify({'message': 'Gejala berhasil dihapus.'})
    return jsonify({'error': 'Gagal menghapus gejala.'}), 400


# 2. Kelola Penyakit (Diseases)
@api_bp.route('/admin/diseases', methods=['GET'])
def admin_get_diseases():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, description, recommendation FROM diseases ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/diseases', methods=['POST'])
def admin_add_disease():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'code' not in data or 'name' not in data or 'description' not in data or 'recommendation' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    code = data['code'].strip().upper()
    name = data['name'].strip()
    description = data['description'].strip()
    recommendation = data['recommendation'].strip()

    if not code or not name or not description or not recommendation:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if repo.add_disease(code, name, description, recommendation):
        return jsonify({'message': 'Penyakit berhasil ditambahkan.'}), 201
    return jsonify({'error': 'Gagal menambahkan penyakit. Kode mungkin sudah terdaftar.'}), 400

@api_bp.route('/admin/diseases/<string:code>', methods=['PUT'])
def admin_update_disease(code):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data or 'recommendation' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    name = data['name'].strip()
    description = data['description'].strip()
    recommendation = data['recommendation'].strip()

    if not name or not description or not recommendation:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if repo.update_disease(code, name, description, recommendation):
        return jsonify({'message': 'Penyakit berhasil diperbarui.'})
    return jsonify({'error': 'Gagal memperbarui penyakit.'}), 400

@api_bp.route('/admin/diseases/<string:code>', methods=['DELETE'])
def admin_delete_disease(code):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    if repo.delete_disease(code):
        return jsonify({'message': 'Penyakit berhasil dihapus.'})
    return jsonify({'error': 'Gagal menghapus penyakit.'}), 400


# 3. Kelola Aturan (Rules)
@api_bp.route('/admin/rules', methods=['GET'])
def admin_get_rules():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, antecedents, consequent FROM rules ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/rules', methods=['POST'])
def admin_add_rule():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'antecedents' not in data or 'consequent' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    antecedents = data['antecedents'].strip()
    consequent = data['consequent'].strip().upper()

    if not antecedents or not consequent:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if kb.add_rule(antecedents, consequent):
        return jsonify({'message': 'Aturan berhasil ditambahkan.'}), 201
    return jsonify({'error': 'Gagal menambahkan aturan.'}), 400

@api_bp.route('/admin/rules/<int:rule_id>', methods=['PUT'])
def admin_update_rule(rule_id):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'antecedents' not in data or 'consequent' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    antecedents = data['antecedents'].strip()
    consequent = data['consequent'].strip().upper()

    if not antecedents or not consequent:
        return jsonify({'error': 'Field tidak boleh kosong.'}), 400

    if kb.update_rule(rule_id, antecedents, consequent):
        return jsonify({'message': 'Aturan berhasil diperbarui.'})
    return jsonify({'error': 'Gagal memperbarui aturan.'}), 400

@api_bp.route('/admin/rules/<int:rule_id>', methods=['DELETE'])
def admin_delete_rule(rule_id):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    if kb.delete_rule(rule_id):
        return jsonify({'message': 'Aturan berhasil dihapus.'})
    return jsonify({'error': 'Gagal menghapus aturan.'}), 400


# 4. Tampilkan data user dan hasil diagnosa tiap user
@api_bp.route('/admin/user-diagnoses', methods=['GET'])
def admin_get_user_diagnoses():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT d.id, d.user_id, u.username, d.symptoms, d.result, d.created_at 
               FROM diagnoses d 
               JOIN users u ON d.user_id = u.id 
               ORDER BY d.created_at DESC"""
        )
        rows = cursor.fetchall()
        conn.close()
        
        diagnoses = []
        for r in rows:
            diagnoses.append({
                'id': r['id'],
                'user_id': r['user_id'],
                'username': r['username'],
                'symptoms': json.loads(r['symptoms']),
                'result': json.loads(r['result']),
                'created_at': r['created_at']
            })
        return jsonify(diagnoses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/user-diagnoses/<int:diagnose_id>', methods=['DELETE'])
def admin_delete_user_diagnose(diagnose_id):
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diagnoses WHERE id = ?", (diagnose_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Hasil diagnosa user berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Batch deletion endpoints
@api_bp.route('/admin/symptoms/delete-batch', methods=['POST'])
def admin_delete_symptoms_batch():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'codes' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    codes = data['codes']
    if not isinstance(codes, list):
        return jsonify({'error': 'Format data salah.'}), 400
        
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM symptoms WHERE code = ?", [(c,) for c in codes])
        conn.commit()
        conn.close()
        return jsonify({'message': f'{len(codes)} gejala berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/admin/diseases/delete-batch', methods=['POST'])
def admin_delete_diseases_batch():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'codes' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    codes = data['codes']
    if not isinstance(codes, list):
        return jsonify({'error': 'Format data salah.'}), 400
        
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM diseases WHERE code = ?", [(c,) for c in codes])
        conn.commit()
        conn.close()
        return jsonify({'message': f'{len(codes)} penyakit berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/admin/rules/delete-batch', methods=['POST'])
def admin_delete_rules_batch():
    if not is_admin():
        return jsonify({'error': 'Akses ditolak. Hanya untuk Admin.'}), 403
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({'error': 'Data tidak lengkap.'}), 400
    
    ids = data['ids']
    if not isinstance(ids, list):
        return jsonify({'error': 'Format data salah.'}), 400
        
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM rules WHERE id = ?", [(rid,) for rid in ids])
        conn.commit()
        conn.close()
        return jsonify({'message': f'{len(ids)} aturan berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500