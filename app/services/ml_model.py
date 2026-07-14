import os
import csv
from typing import List, Dict, Set, Optional

class MLDiseaseClassifier:
    """
    Klasifikasi penyakit jagung menggunakan Random Forest berbasis scikit-learn.
    Dilatih dari file CSV dengan fitur biner gejala G1–G31.
    """

    FEATURE_COLS = [f"G{i}" for i in range(1, 32)]
    LABEL_COL = "label"

    def __init__(self, csv_path: str):
        self._model = None
        self._label_encoder = None
        self._is_trained = False
        self._training_error: Optional[str] = None
        self._train(csv_path)

    def _train(self, csv_path: str):
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            import numpy as np

            X, y = [], []
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        features = [int(row[col]) for col in self.FEATURE_COLS]
                        label = row[self.LABEL_COL].strip()
                        X.append(features)
                        y.append(label)
                    except (KeyError, ValueError):
                        continue

            if not X:
                self._training_error = "Dataset CSV kosong atau format tidak valid."
                return

            self._label_encoder = LabelEncoder()
            y_enc = self._label_encoder.fit_transform(y)

            self._model = RandomForestClassifier(
                n_estimators=100,
                max_depth=None,
                random_state=42,
                class_weight="balanced"
            )
            self._model.fit(np.array(X), y_enc)
            self._is_trained = True

        except ImportError:
            self._training_error = "scikit-learn tidak terinstal. Jalankan: pip install scikit-learn"
        except FileNotFoundError:
            self._training_error = f"File dataset tidak ditemukan: {csv_path}"
        except Exception as e:
            self._training_error = f"Gagal melatih model: {str(e)}"

    def predict(self, selected_symptom_codes: Set[str]) -> List[Dict]:
        """
        Menerima set kode gejala aktif (misal {'G1','G3'}).
        Mengembalikan list dict {'label': str, 'confidence': float} urut descending.
        """
        if not self._is_trained:
            raise RuntimeError(self._training_error or "Model belum dilatih.")

        import numpy as np

        # Encode gejala ke vektor biner
        feature_vector = [
            1 if col in selected_symptom_codes else 0
            for col in self.FEATURE_COLS
        ]
        X = np.array([feature_vector])

        # Probabilitas per kelas
        proba = self._model.predict_proba(X)[0]
        classes = self._label_encoder.classes_

        results = []
        for label, conf in zip(classes, proba):
            if conf > 0.05:  # threshold minimum 5%
                results.append({
                    "label": str(label),  # convert np.str_ to plain str
                    "confidence": round(float(conf) * 100, 1)
                })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    @property
    def training_error(self) -> Optional[str]:
        return self._training_error
