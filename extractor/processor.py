from extractor.gliner_model import GLiNERExtractor
from extractor.kb_lookup import KnowledgeBase
from extractor.normalizer import SkillNormalizer
from extractor.inference import SkillInference
from extractor.skill_identifier import SkillIdentifier
class Processor:

    def __init__(self):

        self.kb = KnowledgeBase()

        self.extractor = GLiNERExtractor()

        self.concepts = SkillIdentifier(self.kb)

        self.normalizer = SkillNormalizer(self.kb)

        self.inference = SkillInference(self.kb)

    
    def get_skills(self, text):
        entities = self.extractor.extract(text)
        raw_skills = [e["text"] for e in entities]
        normalized = self.normalizer.normalize_list(raw_skills)
        inferred = self.inference.infer(normalized)
        return normalized|inferred["implies"]
        
    
    def get_context_skills(self,text):
        entities = self.extractor.extract(text)
        raw_skills = [e["text"] for e in entities]
        concept = self.concepts.expand(raw_skills)
        normalized = self.normalizer.normalize_list(concept)
        inferred = self.inference.infer(normalized)
        return normalized|inferred["implies"]
    
    def get_resume_skills(self,skills_text,project_text,experience_text):
        explicit = self.get_skills(skills_text)
        project = self.get_context_skills(project_text)
        experience = self.get_context_skills(experience_text)
        return explicit | project | experience
    
    
    


    
    
