from typing import Set, List
from .knowledge_base import Rule

class InferenceEngine:
    @staticmethod
    def forward_chain(rules: List[Rule], initial_facts: Set[str]) -> Set[str]:
        facts = initial_facts.copy()
        inferred = set()
        changed = True
        while changed:
            changed = False
            for rule in rules:
                if set(rule.get_antecedents()).issubset(facts) and rule.get_consequent() not in facts:
                    facts.add(rule.get_consequent())
                    inferred.add(rule.get_consequent())
                    changed = True
        return inferred