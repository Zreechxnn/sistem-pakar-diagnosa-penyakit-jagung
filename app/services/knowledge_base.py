from typing import List

class Rule:
    """Merepresentasikan satu aturan: IF antecedents THEN consequent."""
    def __init__(self, antecedents: List[str], consequent: str):
        self.antecedents = antecedents
        self.consequent = consequent

    def get_antecedents(self) -> List[str]:
        return self.antecedents

    def get_consequent(self) -> str:
        return self.consequent


class KnowledgeBase:
    """Membaca dan menyimpan aturan dari file teks."""
    def __init__(self, file_path: str):
        self.rules: List[Rule] = self._load_rules(file_path)

    def _load_rules(self, file_path: str) -> List[Rule]:
        rules = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Abaikan baris kosong dan komentar
                    if not line or line.startswith('#'):
                        continue
                    # Format: antecedent1,antecedent2-consequent
                    if '-' not in line:
                        continue
                    ant_part, cons = line.split('-', 1)
                    antecedents = [a.strip() for a in ant_part.split(',') if a.strip()]
                    consequent = cons.strip()
                    if antecedents and consequent:
                        rules.append(Rule(antecedents, consequent))
        except FileNotFoundError:
            print(f"Warning: Knowledge base file '{file_path}' not found.")
        return rules

    def get_rules(self) -> List[Rule]:
        return self.rules