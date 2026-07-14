from flask import Blueprint, request, jsonify
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
    return jsonify(response)


@api_bp.route('/ml-status', methods=['GET'])
def ml_status():
    """Cek status ML model."""
    return jsonify({
        'is_trained': ml_classifier.is_trained,
        'error': ml_classifier.training_error
    })