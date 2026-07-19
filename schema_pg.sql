-- Schema & Seed Data for Sistem Pakar Diagnosa Penyakit Jagung (PostgreSQL)

DROP TABLE IF EXISTS diagnoses CASCADE;
DROP TABLE IF EXISTS rules CASCADE;
DROP TABLE IF EXISTS diseases CASCADE;
DROP TABLE IF EXISTS symptoms CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Create Tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    disease_name VARCHAR(255) NOT NULL
);

CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL
);

CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    antecedents TEXT NOT NULL, -- Comma-separated symptom codes
    consequent VARCHAR(50) NOT NULL -- Disease code or symptom code
);

CREATE TABLE diagnoses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symptoms TEXT NOT NULL, -- JSON string of symptom codes
    result TEXT NOT NULL, -- JSON string of diagnosis result
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Seed Users
INSERT INTO users (id, username, password, role, created_at) VALUES
(1, 'admin', 'scrypt:32768:8:1$1acc8HYaf295PnzG$f7fe2ed7466581b90ffce8657675b4f3ca84ac3e579bbf1089bf874192f7e8244a7bb564f8fcb1bc4b6e77570250787d213d49dce3ad6763e652c5e8d4f595fb', 'admin', '2026-07-16 13:43:36'),
(2, 'user', 'scrypt:32768:8:1$NVZ7sywb5alltR8U$a6ae3b3db475239c06652193aa781abba62cda93b8f1f4b1965ec2681661c908467c8c73627075ef00d871107621482d6262ea17b4269bcbf4fbf36b8a3b7a44', 'user', '2026-07-16 13:43:36'),
(3, 'asep', 'scrypt:32768:8:1$x0OTPPzHTJcBhMhi$dcb714e05354a90433eb4b9a277b80f9cd44b810e19ba661469f8fbadda2955002f88372af93eb1d37091618447d1dc9e333d0940282e69341a8073bd3296313', 'user', '2026-07-17 13:34:22'),
(4, 'siti', 'scrypt:32768:8:1$IGT4SzD3vGYT6LjK$f7fd9138699768709241942d432f40781a344edcedb9199899ff9ce8f7880cafcb170e9129c8cc980e662b808a18525abf6ca879c078ce8d92b4c23520daa864', 'user', '2026-07-19 13:42:27');

-- 3. Seed Symptoms
INSERT INTO symptoms (id, code, description, disease_name) VALUES
(1, 'G1', 'Daun jagung berubah menjadi warna klorotik', 'Bulai'),
(2, 'G2', 'Pertumbuhan tanaman mengalami hambatan', 'Bulai'),
(3, 'G3', 'Terdapat warna putih seperti tepung pada permukaan daun', 'Bulai'),
(4, 'G4', 'Daun menggulung dan terpuntir', 'Bulai'),
(5, 'G5', 'Pembentukan tongkol terganggu', 'Bulai'),
(6, 'G6', 'Daun terlihat layu', 'Blight'),
(7, 'G7', 'Terdapat bercak kecil yang bersatu membentuk bercak yang lebih besar', 'Blight'),
(8, 'G8', 'Bercak berwarna coklat muda dan berbentuk memanjang menyerupai kumparan atau perahu', 'Blight'),
(9, 'G9', 'Terdapat bercak berwarna coklat berbentuk elips', 'Blight'),
(10, 'G10', 'Daun terlihat kering', 'Blight'),
(11, 'G11', 'Daun jagung terlihat kering', 'Leaf Rust'),
(12, 'G12', 'Terdapat bercak-bercak kecil berwarna coklat atau kuning pada permukaan daun', 'Leaf Rust'),
(13, 'G13', 'Terdapat bercak merah pada tulang daun', 'Leaf Rust'),
(14, 'G14', 'Muncul benang tidak beraturan yang awalnya berwarna putih, lalu berubah menjadi coklat', 'Leaf Rust'),
(15, 'G15', 'Daun mengeluarkan serbuk yang menyerupai tepung berwarna kuning kecoklatan', 'Leaf Rust'),
(16, 'G16', 'Terdapat pembengkakan pada tongkol jagung', 'Burn'),
(17, 'G17', 'Muncul jamur berwarna putih hingga hitam pada biji jagung', 'Burn'),
(18, 'G18', 'Biji jagung terlihat menggembung', 'Burn'),
(19, 'G19', 'Terdapat kelenjar yang terbentuk pada biji', 'Burn'),
(20, 'G20', 'Kelobot (lapisan luar tongkol) terbuka, dan muncul banyak jamur berwarna putih hingga hitam', 'Burn'),
(21, 'G21', 'Terdapat lubang kecil pada daun', 'Stem Borer'),
(22, 'G22', 'Terdapat celah pada batang', 'Stem Borer'),
(23, 'G23', 'Bunga jantan atau pangkal tongkol terlihat rusak', 'Stem Borer'),
(24, 'G24', 'Batang dan tassel (bunga jantan) mudah patah', 'Stem Borer'),
(25, 'G25', 'Terdapat tumpukan tassel yang patah', 'Stem Borer'),
(26, 'G26', 'Bunga jantan tidak terbentuk', 'Stem Borer'),
(27, 'G27', 'Terdapat serbuk/dirt di sekitar pangkal tongkol', 'Stem Borer'),
(28, 'G28', 'Daun terlihat agak kuning', 'Stem Borer'),
(29, 'G29', 'Terdapat lubang melintang pada daun saat fase vegetatif', 'Cob Borer'),
(30, 'G30', 'Rambut tongkol jagung terlihat terpotong atau mengering', 'Cob Borer'),
(31, 'G31', 'Ujung tongkol terlihat berlubang atau terdapat gerekan', 'Cob Borer'),
(32, 'G32', 'Sering ditemukan larva di sekitar tongkol', 'Cob Borer');

-- 4. Seed Diseases
INSERT INTO diseases (id, code, name, description, recommendation) VALUES
(1, 'P001', 'Bulai', 'Penyakit bulai disebabkan oleh jamur Peronosclerospora spp. Menyerang daun muda, menyebabkan klorosis sistemik, pertumbuhan terhambat, dan dapat menyebabkan gagal panen jika tidak dikendalikan.', 'Gunakan varietas tahan bulai. Aplikasi fungisida sistemik berbahan aktif metalaksil pada benih. Lakukan pergiliran tanaman dan sanitasi lahan.'),
(2, 'P002', 'Blight (Hawar Daun)', 'Hawar daun disebabkan oleh jamur Helminthosporium atau Bipolaris. Menyebabkan bercak memanjang pada daun, daun mengering, dan mengurangi fotosintesis.', 'Aplikasi fungisida berbahan aktif mancozeb atau propikonazol. Atur jarak tanam untuk sirkulasi udara, hindari kelembaban tinggi.'),
(3, 'P003', 'Leaf Rust (Karat Daun)', 'Karat daun disebabkan oleh jamur Puccinia sorghi. Muncul bercak kecil berwarna coklat atau kuning, daun mengering, menghasilkan serbuk spora.', 'Semprot fungisida triazole. Tanam varietas tahan, hindari pemupukan nitrogen berlebihan.'),
(4, 'P004', 'Burn (Busuk Tongkol/Gosong)', 'Penyakit gosong atau busuk tongkol disebabkan oleh jamur Ustilago maydis. Menyebabkan pembengkakan pada biji dan tongkol, mengeluarkan spora hitam.', 'Cabut dan musnahkan tanaman terinfeksi. Hindari luka pada tanaman. Aplikasi fungisida jika diperlukan, gunakan varietas tahan.'),
(5, 'P005', 'Stem Borer (Penggerek Batang)', 'Penggerek batang adalah hama larva ngengat Ostrinia furnacalis. Menyebabkan lubang pada batang, patahnya tassel, dan mengurangi hasil.', 'Gunakan insektisida sistemik. Lakukan pemantauan rutin, tanam varietas Bt, dan musnahkan sisa tanaman.'),
(6, 'P006', 'Cob Borer (Penggerek Tongkol)', 'Penggerek tongkol biasanya disebabkan oleh Helicoverpa armigera. Menyebabkan lubang pada tongkol, rambut tongkol mengering, dan ditemukan larva.', 'Aplikasi insektisida kontak. Gunakan perangkap feromon, tanam varietas tahan, dan panen tepat waktu.');

-- 5. Seed Rules
INSERT INTO rules (id, antecedents, consequent) VALUES
(1, 'G1', 'G3'),
(2, 'G2', 'G4'),
(3, 'G2,G5', 'G4'),
(4, 'G4', 'G1'),
(5, 'G3', 'P001'),
(6, 'G6,G10,G8', 'G9'),
(7, 'G7', 'G9'),
(8, 'G10', 'G7'),
(9, 'G0,G10', 'G8'),
(10, 'G9', 'G8'),
(11, 'G8', 'P002'),
(12, 'G10', 'G14'),
(13, 'G10,G12', 'G11'),
(14, 'G14', 'G12'),
(15, 'G12', 'G13'),
(16, 'G13', 'G11'),
(17, 'G11', 'P003'),
(18, 'G15', 'G16'),
(19, 'G16,G18', 'G19'),
(20, 'G16', 'G18'),
(21, 'G18', 'G17'),
(22, 'G17', 'G19'),
(23, 'G19', 'P004'),
(24, 'G20', 'G21'),
(25, 'G20,G27', 'G21'),
(26, 'G23', 'G20'),
(27, 'G24', 'G23'),
(28, 'G22,G25', 'G24'),
(29, 'G26', 'G22'),
(30, 'G21', 'P005'),
(31, 'G31', 'G29'),
(32, 'G29', 'G28'),
(33, 'G28', 'G30'),
(34, 'G30', 'P006');

-- 6. Seed Diagnoses
INSERT INTO diagnoses (id, user_id, symptoms, result, created_at) VALUES
(1, 3, '[{"code": "G7", "description": "Terdapat bercak kecil yang bersatu membentuk bercak yang lebih besar"}]', '[{"code": "P002", "nama": "Blight (Hawar Daun)", "deskripsi": "Hawar daun disebabkan oleh jamur Helminthosporium atau Bipolaris. Menyebabkan bercak memanjang pada daun, daun mengering, dan mengurangi fotosintesis.", "rekomendasi": "Aplikasi fungisida berbahan aktif mancozeb atau propikonazol. Atur jarak tanam untuk sirkulasi udara, hindari kelembaban tinggi.", "confidence": 50.0, "label": "Blight"}, {"code": "P006", "nama": "Cob Borer (Penggerek Tongkol)", "deskripsi": "Penggerek tongkol biasanya disebabkan oleh Helicoverpa armigera. Menyebabkan lubang pada tongkol, rambut tongkol mengering, dan ditemukan larva.", "rekomendasi": "Aplikasi insektisida kontak. Gunakan perangkap feromon, tanam varietas tahan, dan panen tepat waktu.", "confidence": 17.0, "label": "Cob Borer"}, {"code": "P004", "nama": "Burn (Busuk Tongkol/Gosong)", "deskripsi": "Penyakit gosong atau busuk tongkol disebabkan oleh jamur Ustilago maydis. Menyebabkan pembengkakan pada biji dan tongkol, mengeluarkan spora hitam.", "rekomendasi": "Cabut dan musnahkan tanaman terinfeksi. Hindari luka pada tanaman. Aplikasi fungisida jika diperlukan, gunakan varietas tahan.", "confidence": 9.0, "label": "Burn"}, {"code": "P003", "nama": "Leaf Rust (Karat Daun)", "deskripsi": "Karat daun disebabkan oleh jamur Puccinia sorghi. Muncul bercak kecil berwarna coklat atau kuning, daun mengering, menghasilkan serbuk spora.", "rekomendasi": "Semprot fungisida triazole. Tanam varietas tahan, hindari pemupukan nitrogen berlebihan.", "confidence": 9.0, "label": "Leaf Rust"}, {"code": "P005", "nama": "Stem Borer (Penggerek Batang)", "deskripsi": "Penggerek batang adalah hama larva ngengat Ostrinia furnacalis. Menyebabkan lubang pada batang, patahnya tassel, dan mengurangi hasil.", "rekomendasi": "Gunakan insektisida sistemik. Lakukan pemantauan rutin, tanam varietas Bt, dan musnahkan sisa tanaman.", "confidence": 8.0, "label": "Stem Borer"}, {"code": "P001", "nama": "Bulai", "deskripsi": "Penyakit bulai disebabkan oleh jamur Peronosclerospora spp. Menyerang daun muda, menyebabkan klorosis sistemik, pertumbuhan terhambat, dan dapat menyebabkan gagal panen jika tidak dikendalikan.", "rekomendasi": "Gunakan varietas tahan bulai. Aplikasi fungisida sistemik berbahan aktif metalaksil pada benih. Lakukan pergiliran tanaman dan sanitasi lahan.", "confidence": 7.0, "label": "Bulai"}]', '2026-07-17 13:34:36'),
(2, 1, '[{"code": "G30", "description": "Rambut tongkol jagung terlihat terpotong atau mengering"}]', '[{"code": "P006", "nama": "Cob Borer (Penggerek Tongkol)", "deskripsi": "Penggerek tongkol biasanya disebabkan oleh Helicoverpa armigera. Menyebabkan lubang pada tongkol, rambut tongkol mengering, dan ditemukan larva.", "rekomendasi": "Aplikasi insektisida kontak. Gunakan perangkap feromon, tanam varietas tahan, dan panen tepat waktu.", "confidence": 66.0, "label": "Cob Borer"}, {"code": "P002", "nama": "Blight (Hawar Daun)", "deskripsi": "Hawar daun disebabkan oleh jamur Helminthosporium atau Bipolaris. Menyebabkan bercak memanjang pada daun, daun mengering, dan mengurangi fotosintesis.", "rekomendasi": "Aplikasi fungisida berbahan aktif mancozeb atau propikonazol. Atur jarak tanam untuk sirkulasi udara, hindari kelembaban tinggi.", "confidence": 13.0, "label": "Blight"}, {"code": "P003", "nama": "Leaf Rust (Karat Daun)", "deskripsi": "Karat daun disebabkan oleh jamur Puccinia sorghi. Muncul bercak kecil berwarna coklat atau kuning, daun mengering, menghasilkan serbuk spora.", "rekomendasi": "Semprot fungisida triazole. Tanam varietas tahan, hindari pemupukan nitrogen berlebihan.", "confidence": 7.0, "label": "Leaf Rust"}, {"code": "P001", "nama": "Bulai", "deskripsi": "Penyakit bulai disebabkan oleh jamur Peronosclerospora spp. Menyerang daun muda, menyebabkan klorosis sistemik, pertumbuhan terhambat, dan dapat menyebabkan gagal panen jika tidak dikendalikan.", "rekomendasi": "Gunakan varietas tahan bulai. Aplikasi fungisida sistemik berbahan aktif metalaksil pada benih. Lakukan pergiliran tanaman dan sanitasi lahan.", "confidence": 6.0, "label": "Bulai"}, {"code": "P005", "nama": "Stem Borer (Penggerek Batang)", "deskripsi": "Penggerek batang adalah hama larva ngengat Ostrinia furnacalis. Menyebabkan lubang pada batang, patahnya tassel, dan mengurangi hasil.", "rekomendasi": "Gunakan insektisida sistemik. Lakukan pemantauan rutin, tanam varietas Bt, dan musnahkan sisa tanaman.", "confidence": 6.0, "label": "Stem Borer"}]', '2026-07-18 06:56:26');

-- 7. Reset Sequence values
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('symptoms_id_seq', (SELECT MAX(id) FROM symptoms));
SELECT setval('diseases_id_seq', (SELECT MAX(id) FROM diseases));
SELECT setval('rules_id_seq', (SELECT MAX(id) FROM rules));
SELECT setval('diagnoses_id_seq', (SELECT MAX(id) FROM diagnoses));
