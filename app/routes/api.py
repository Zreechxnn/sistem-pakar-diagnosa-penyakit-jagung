from flask import Blueprint, request, jsonify
from app.services.disease_repo import DiseaseRepository
from app.services.knowledge_base import KnowledgeBase
from app.services.inference import InferenceEngine
from config import Config

api_bp = Blueprint('api', __name__)

# Instansiasi service (singleton)
repo = DiseaseRepository()
kb = KnowledgeBase(Config.KNOWLEDGE_BASE_PATH)
engine = InferenceEngine()

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
    """
    data = request.get_json()
    if not data or 'symptoms' not in data:
        return jsonify({'error': 'Harap sertakan "symptoms" dalam body.'}), 400

    selected_codes = set(data['symptoms'])
    if not selected_codes:
        return jsonify({'error': 'Minimal satu gejala harus dipilih.'}), 400

    # ✅ Dapatkan semua kode valid langsung dari repo
    valid_codes = {item['code'] for item in repo.get_all_symptoms_with_codes()}
    invalid = selected_codes - valid_codes
    if invalid:
        return jsonify({'error': f'Kode gejala tidak valid: {", ".join(sorted(invalid))}'}), 400

    # Forward chaining
    inferred = engine.forward_chain(kb.get_rules(), selected_codes)

    # Filter hanya penyakit (kode P)
    penyakit_codes = sorted([k for k in inferred if k.startswith('P')])

    # Bangun respons
    hasil = []
    for code in penyakit_codes:
        info = repo.get_disease_info(code)
        hasil.append({
            'code': code,
            'nama': info['nama'],
            'deskripsi': info['deskripsi'],
            'rekomendasi': info['rekomendasi']
        })

    # Gejala yang dikirim user beserta deskripsinya
    reported_symptoms = [
        {'code': c, 'description': repo.get_gejala_description(c)}
        for c in sorted(selected_codes)
    ]

    response = {
        'reported_symptoms': reported_symptoms,
        'diagnosis': hasil,
        'total_penyakit_terdeteksi': len(penyakit_codes)
    }
    return jsonify(response)