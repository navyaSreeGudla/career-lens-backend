from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSkillMatcher:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )
        self.embedding_cache = {}
    
   
    def get_embedding(self, skill):
        if skill not in self.embedding_cache:
            self.embedding_cache[skill] = self.model.encode(
                f"Skill: {skill}",
                convert_to_numpy=True
            )

        return self.embedding_cache[skill]

    def match(self, resume_skills, jd_skills, threshold=0.82, section: str | None = None):

        if not jd_skills:
            return {
        "matched": [],
        "partial":[],
        "missing": [],
        "extra": resume_skills,
        "match_percentage": 0}

        resume_vectors = [{
        "skill": s,
        "embedding": self.get_embedding(s)}for s in resume_skills]

        jd_vectors = [{
        "skill": s,
        "embedding": self.get_embedding(s)}for s in jd_skills]

        matched = []
        partial = []
        missing = []

        used_resume = set()

        for jd in jd_vectors:

            best = None
            best_score = -1

            for resume in resume_vectors:
                if resume["skill"] in used_resume:
                    continue

                if jd["skill"] == resume["skill"]:
                      score = 1.0
                else:
                    score = cosine_similarity([jd["embedding"]],[resume["embedding"]])[0][0]
                if score > best_score:
                    best = resume
                    best_score = score
            if best is None:
                missing.append(jd["skill"])
                continue

            if best_score >= threshold:
                entry = {
                    "jd_skill": jd["skill"],
                    "resume_skill": best["skill"],
                    "similarity": round(float(best_score), 3),
                    "status": "matched"
                }
                if section:
                    entry["found_in"] = section
                matched.append(entry)
                used_resume.add(best["skill"])
            
            elif best_score >= 0.60:
                entry = {
                    "jd_skill": jd["skill"],
                    "resume_skill": best["skill"],
                    "similarity": round(float(best_score), 3),
                    "status": "partial"
                }
                if section:
                    entry["found_in"] = section
                partial.append(entry)
                used_resume.add(best["skill"])
                
            else:
                missing.append(jd["skill"])
        return {

            "matched": matched,
            "partial":partial,
            "missing": missing,
            "extra": [s for s in resume_skills if s not in used_resume],
            "match_percentage":
    float(round((len(matched)+0.5*len(partial)) / len(jd_skills) * 100, 2))

        }