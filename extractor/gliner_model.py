from gliner import GLiNER
import re


class GLiNERExtractor:

    SPECIAL_SKILLS = [
        "C++",
        "C#",
        ".NET",
        "ASP.NET",
        "Node.js",
        "React.js",
        "Next.js",
        "Express.js",
        "Vue.js",
        "Nuxt.js",
        "NestJS",
    ]

    def __init__(self, model_name="urchade/gliner_medium-v2.1"):

        self.model = GLiNER.from_pretrained(model_name)

        self.labels = [
            "programming language",
            "framework",
            "database",
            "cloud platform",
            "cloud service",
            "developer tool",
            "technology",
            "software",
            "skill",
        ]

    def extract(self, text):

        entities = self.model.predict_entities(
            text,
            self.labels,
            threshold=0.4
        )

        skills = {e["text"] for e in entities}

        # Recover punctuation-heavy skills
        for skill in self.SPECIAL_SKILLS:

            if re.search(re.escape(skill), text, re.IGNORECASE):

                skills.add(skill)

        return [{"text": skill} for skill in skills]

    def extract_skill_names(self, text):

        return [
            entity["text"]
            for entity in self.extract(text)
        ]