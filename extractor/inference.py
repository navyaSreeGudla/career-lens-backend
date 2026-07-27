from collections import defaultdict

class SkillInference:

    def __init__(self, kb):

        self.kb = kb
        self.graph = kb.inference_graph
    
    def infer(self, skills):
        implied = set()
        required = set()
        
        for skill in skills:
            relations = self.graph.get(skill, {})
            
            implied.update(
            relations.get("implies", [])
            )
            required.update(
            relations.get("requires", [])
            )
            
        return {

        "implies": implied,

        "requires": required

    }