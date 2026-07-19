from app.db import Database
from typing import List
from config import Config

class Rule:
    """Merepresentasikan satu aturan: IF antecedents THEN consequent."""
    def __init__(self, antecedents: List[str], consequent: str, rule_id: int = None):
        self.id = rule_id
        self.antecedents = antecedents
        self.consequent = consequent

    def get_antecedents(self) -> List[str]:
        return self.antecedents

    def get_consequent(self) -> str:
        return self.consequent


class KnowledgeBase:
    """Membaca dan menyimpan aturan dari database SQLite/PostgreSQL."""
    def __init__(self, file_path: str = None):
        # file_path parameter kept for backward compatibility if instantiated elsewhere
        pass

    def get_rules(self) -> List[Rule]:
        rules = []
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, antecedents, consequent FROM rules ORDER BY id ASC")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                antecedents = [a.strip() for a in row['antecedents'].split(',') if a.strip()]
                rules.append(Rule(antecedents, row['consequent'], row['id']))
        except Exception as e:
            print(f"Error loading rules from db: {e}")
        return rules

    # API CRUD Helper Methods
    def add_rule(self, antecedents: str, consequent: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rules (antecedents, consequent) VALUES (?, ?)",
                (antecedents, consequent)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding rule: {e}")
            return False

    def update_rule(self, rule_id: int, antecedents: str, consequent: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rules SET antecedents = ?, consequent = ? WHERE id = ?",
                (antecedents, consequent, rule_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating rule: {e}")
            return False

    def delete_rule(self, rule_id: int) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting rule: {e}")
            return False