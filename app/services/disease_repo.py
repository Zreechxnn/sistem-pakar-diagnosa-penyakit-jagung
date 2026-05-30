from typing import List, Tuple, Dict

class DiseaseRepository:
    def __init__(self):
        self._symptom_groups: List[Tuple[str, List[str]]] = [
            ('Bulai', [
                'Daun jagung berubah menjadi warna klorotik',
                'Pertumbuhan tanaman mengalami hambatan',
                'Terdapat warna putih seperti tepung pada permukaan daun',
                'Daun menggulung dan terpuntir',
                'Pembentukan tongkol terganggu'
            ]),
            ('Blight', [
                'Daun terlihat layu',
                'Terdapat bercak kecil yang bersatu membentuk bercak yang lebih besar',
                'Bercak berwarna coklat muda dan berbentuk memanjang menyerupai kumparan atau perahu',
                'Terdapat bercak berwarna coklat berbentuk elips',
                'Daun terlihat kering'
            ]),
            ('Leaf Rust', [
                'Daun jagung terlihat kering',
                'Terdapat bercak-bercak kecil berwarna coklat atau kuning pada permukaan daun',
                'Terdapat bercak merah pada tulang daun',
                'Muncul benang tidak beraturan yang awalnya berwarna putih, lalu berubah menjadi coklat',
                'Daun mengeluarkan serbuk yang menyerupai tepung berwarna kuning kecoklatan'
            ]),
            ('Burn', [
                'Terdapat pembengkakan pada tongkol jagung',
                'Muncul jamur berwarna putih hingga hitam pada biji jagung',
                'Biji jagung terlihat menggembung',
                'Terdapat kelenjar yang terbentuk pada biji',
                'Kelobot (lapisan luar tongkol) terbuka, dan muncul banyak jamur berwarna putih hingga hitam'
            ]),
            ('Stem Borer', [
                'Terdapat lubang kecil pada daun',
                'Terdapat celah pada batang',
                'Bunga jantan atau pangkal tongkol terlihat rusak',
                'Batang dan tassel (bunga jantan) mudah patah',
                'Terdapat tumpukan tassel yang patah',
                'Bunga jantan tidak terbentuk',
                'Terdapat serbuk/dirt di sekitar pangkal tongkol',
                'Daun terlihat agak kuning'
            ]),
            ('Cob Borer', [
                'Terdapat lubang melintang pada daun saat fase vegetatif',
                'Rambut tongkol jagung terlihat terpotong atau mengering',
                'Ujung tongkol terlihat berlubang atau terdapat gerekan',
                'Sering ditemukan larva di sekitar tongkol'
            ])
        ]

        self._gejala_map: Dict[str, str] = {}
        idx = 1
        for _, symptoms in self._symptom_groups:
            for symptom in symptoms:
                self._gejala_map[f"G{idx}"] = symptom
                idx += 1

        self._disease_details: Dict[str, Dict[str, str]] = {
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

    def get_symptom_groups(self) -> List[Tuple[str, List[str]]]:
        return self._symptom_groups

    def get_gejala_description(self, kode: str) -> str:
        return self._gejala_map.get(kode, f"Gejala tidak dikenal ({kode})")

    def get_disease_info(self, kode: str) -> dict:
        return self._disease_details.get(kode, {
            'nama': kode,
            'deskripsi': 'Informasi tidak tersedia.',
            'rekomendasi': 'Silakan konsultasikan dengan ahli.'
        })

    def get_all_symptoms_with_codes(self) -> List[Dict[str, str]]:
        """Mengembalikan daftar semua gejala dengan kode dan deskripsinya."""
        return [{'code': k, 'description': v} for k, v in self._gejala_map.items()]