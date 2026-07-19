from app.db import Database
from typing import List, Tuple, Dict
from config import Config

class DiseaseRepository:
    def __init__(self):
        # Fallback/cache details in case DB queries fail or during init
        self._disease_details = {
            'P001': {
                'nama': 'Bulai',
                'deskripsi': 'Penyakit bulai disebabkan oleh jamur Peronosclerospora spp. Menyerang daun muda, menyebabkan klorosis sistemik, pertumbuhan terhambat, dan dapat menyebabkan gagal panen jika tidak dikendalikan.',
                'rekomendasi': 'Gunakan varietas tahan bulai. Aplikasi fungisida sistemik berbahan aktif metalaksil pada benih. Lakukan pergiliran tanaman dan sanitasi lahan.'
            },
            'P002': {
                'nama': 'Blight (Hawar Daun)',
                'deskripsi': 'Hawar daun disebabkan oleh jamur Helminthosporium atau Bipolaris. Menyebabkan bercak memanjang pada daun, daun mengering, dan mengurangi fotosintesis.',
                'rekomendasi': 'Aplikasi fungisida berbahan aktif mancozeb atau propikonazol. Atur jarak tanam untuk sirkulasi udara, hindari kelembaban tinggi.'
            },
            'P003': {
                'nama': 'Leaf Rust (Karat Daun)',
                'deskripsi': 'Karat daun disebabkan oleh jamur Puccinia sorghi. Muncul bercak kecil berwarna coklat atau kuning, daun mengering, menghasilkan serbuk spora.',
                'rekomendasi': 'Semprot fungisida triazole. Tanam varietas tahan, hindari pemupukan nitrogen berlebihan.'
            },
            'P004': {
                'nama': 'Burn (Busuk Tongkol/Gosong)',
                'deskripsi': 'Penyakit gosong atau busuk tongkol disebabkan oleh jamur Ustilago maydis. Menyebabkan pembengkakan pada biji dan tongkol, mengeluarkan spora hitam.',
                'rekomendasi': 'Cabut dan musnahkan tanaman terinfeksi. Hindari luka pada tanaman. Aplikasi fungisida jika diperlukan, gunakan varietas tahan.'
            },
            'P005': {
                'nama': 'Stem Borer (Penggerek Batang)',
                'deskripsi': 'Penggerek batang adalah hama larva ngengat Ostrinia furnacalis. Menyebabkan lubang pada batang, patahnya tassel, dan mengurangi hasil.',
                'rekomendasi': 'Gunakan insektisida sistemik. Lakukan pemantauan rutin, tanam varietas Bt, dan musnahkan sisa tanaman.'
            },
            'P006': {
                'nama': 'Cob Borer (Penggerek Tongkol)',
                'deskripsi': 'Penggerek tongkol biasanya disebabkan oleh Helicoverpa armigera. Menyebabkan lubang pada tongkol, rambut tongkol mengering, dan ditemukan larva.',
                'rekomendasi': 'Aplikasi insektisida kontak. Gunakan perangkap feromon, tanam varietas tahan, dan panen tepat waktu.'
            }
        }

    def _get_conn(self):
        return Database.get_connection()

    def get_symptom_groups(self) -> List[Tuple[str, List[str]]]:
        """Mengembalikan semua gejala dikelompokkan per penyakit."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT code, description, disease_name FROM symptoms ORDER BY id ASC")
            rows = cursor.fetchall()
            conn.close()

            # Group by disease name
            groups_dict = {}
            for r in rows:
                d_name = r['disease_name']
                desc = r['description']
                if d_name not in groups_dict:
                    groups_dict[d_name] = []
                groups_dict[d_name].append(desc)

            return list(groups_dict.items())
        except Exception as e:
            print(f"Error fetching symptom groups: {e}")
            # Fallback jika terjadi error
            return []

    def get_gejala_description(self, kode: str) -> str:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM symptoms WHERE code = ?", (kode,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row['description']
        except Exception as e:
            print(f"Error fetching symptom description: {e}")
        return f"Gejala tidak dikenal ({kode})"

    def get_disease_info(self, kode: str) -> dict:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT name, description, recommendation FROM diseases WHERE code = ?", (kode,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'nama': row['name'],
                    'deskripsi': row['description'],
                    'rekomendasi': row['recommendation']
                }
        except Exception as e:
            print(f"Error fetching disease info: {e}")
        return self._disease_details.get(kode, {
            'nama': kode,
            'deskripsi': 'Informasi tidak tersedia.',
            'rekomendasi': 'Silakan konsultasikan dengan ahli.'
        })

    def get_all_symptoms_with_codes(self) -> List[Dict[str, str]]:
        """Mengembalikan daftar semua gejala dengan kode dan deskripsinya."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT code, description FROM symptoms ORDER BY id ASC")
            rows = cursor.fetchall()
            conn.close()
            return [{'code': r['code'], 'description': r['description']} for r in rows]
        except Exception as e:
            print(f"Error fetching all symptoms: {e}")
            return []

    # API CRUD Helper Methods
    def add_symptom(self, code: str, description: str, disease_name: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO symptoms (code, description, disease_name) VALUES (?, ?, ?)",
                (code, description, disease_name)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding symptom: {e}")
            return False

    def update_symptom(self, code: str, description: str, disease_name: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE symptoms SET description = ?, disease_name = ? WHERE code = ?",
                (description, disease_name, code)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating symptom: {e}")
            return False

    def delete_symptom(self, code: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM symptoms WHERE code = ?", (code,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting symptom: {e}")
            return False

    def add_disease(self, code: str, name: str, description: str, recommendation: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diseases (code, name, description, recommendation) VALUES (?, ?, ?, ?)",
                (code, name, description, recommendation)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding disease: {e}")
            return False

    def update_disease(self, code: str, name: str, description: str, recommendation: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE diseases SET name = ?, description = ?, recommendation = ? WHERE code = ?",
                (name, description, recommendation, code)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating disease: {e}")
            return False

    def delete_disease(self, code: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM diseases WHERE code = ?", (code,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting disease: {e}")
            return False