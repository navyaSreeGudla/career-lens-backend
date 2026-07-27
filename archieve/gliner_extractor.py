import re
from pathlib import Path
import pandas as pd
from gliner import GLiNER


class SkillExtractor:
    """
    Career Lens Skill Extraction Engine

    Pipeline:

    Text
        ↓
    GLiNER
        ↓
    Enrichment Layer
        ↓
    Normalization
        ↓
    Categorization
        ↓
    Final Skill Set
    """

    MIN_SCORE = 0.60

    LABELS = [
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

    def __init__(self):

        print("Loading GLiNER model...")

        self.model = GLiNER.from_pretrained(
            "urchade/gliner_large-v2.1"
        )

        print("Loading Knowledge Base...")

        base_dir = Path(__file__).resolve().parent.parent
        kb_dir = base_dir / "knowledge_base"
        skills_df = pd.read_csv(
            kb_dir / "master_skills.csv"
        )

        self.alias_dict = {}
        self.category_dict = {}
        self.parent_dict = {}

        for _, row in skills_df.iterrows():

            canonical = str(row["skill"]).strip()
            category = str(row["category"]).strip()

            self.alias_dict[canonical.casefold()] = canonical
            self.category_dict[canonical] = category

            if pd.notna(row["aliases"]):

                aliases = str(row["aliases"]).split(",")

                for alias in aliases:

                    alias = alias.strip()

                    if alias:
                        self.alias_dict[
                            alias.casefold()
                        ] = canonical
            if pd.notna(row["parent"]):

               parent = str(row["parent"]).strip()

               if parent:
                   self.parent_dict[canonical] = parent
        # Used by Job Description extraction
        self.known_skills = set(self.category_dict.keys())

        print("Skill Extractor Ready!")

    # -------------------------------------------------

    def normalize_skill(self, skill):

        original = skill.strip()

        return self.alias_dict.get(
            original.casefold(),
            original,
        )

    # -------------------------------------------------

    def get_category(self, skill):

        return self.category_dict.get(
            skill,
            "Uncategorized",
        )

    # -------------------------------------------------

    def _extract_pipeline(self, text):

        entities = self.model.predict_entities(
            text,
            self.LABELS,
        )

        extracted = {}

        # -----------------------------
        # GLiNER Extraction
        # -----------------------------

        for entity in entities:

            if entity["score"] < self.MIN_SCORE:
                continue

            canonical = self.normalize_skill(
                entity["text"]
            )

            if canonical not in extracted:

                extracted[canonical] = {

                    "skill": canonical,

                    "matched_text": entity["text"],

                    "category": self.get_category(
                        canonical
                    ),

                    "score": round(
                        entity["score"],
                        2,
                    ),

                    "source": "GLiNER",

                    "label": entity["label"],
                }

            else:

                if (
                    entity["score"]
                    > extracted[canonical]["score"]
                ):

                    extracted[canonical].update(

                        {

                            "matched_text": entity["text"],

                            "score": round(
                                entity["score"],
                                2,
                            ),

                            "label": entity["label"],
                        }

                    )

        # -----------------------------
        # Enrichment Layer
        # -----------------------------
        # Knowledge Base Lookup

        lower_text = text.casefold()

        for alias, canonical in self.alias_dict.items():

          pattern = re.compile(
        rf"(?<!\w){re.escape(alias)}(?!\w)",
        re.IGNORECASE,
    )

          if pattern.search(lower_text):

             if canonical not in extracted:

                extracted[canonical] = {

                "skill": canonical,

                "matched_text": alias,

                "category": self.get_category(canonical),

                "score": 1.00,

                "source": "Knowledge Base",

                "label": "skill",
            }
        # -----------------------------
        # Concept expansion
        # -----------------------------
        expanded = extracted.copy()

        for skill in list(extracted.values()):

          parent = self.parent_dict.get(skill["skill"])

          if parent and parent not in expanded:

           expanded[parent] = {

            "skill": parent,

            "matched_text": skill["skill"],

            "category": self.get_category(parent),

            "score": skill["score"],

            "source": "Concept Expansion",

            "label": "concept",
        }
        # -----------------------------
        # Final Sorting
        # -----------------------------   
        return sorted(
    expanded.values(),
    key=lambda x: (x["category"], x["skill"])
)
                       



    # -------------------------------------------------
    # Resume Skill Extraction
    # -------------------------------------------------

    def extract_resume(self, text):
        """
        Extract every skill found in a resume.
        """
        return self._extract_pipeline(text)

    # -------------------------------------------------
    # Job Description Skill Extraction
    # -------------------------------------------------

    def extract_job_description(self, text):
        """
        Extract only skills present in the Knowledge Base.
        """

        skills = self._extract_pipeline(text)

        technical_skills = [

            skill

            for skill in skills

            if skill["skill"] in self.known_skills

        ]

        return technical_skills


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    extractor = SkillExtractor()

    text = """
    Designed and implemented a microservices-based backend
    using Spring Boot, Kafka, Redis, Docker and Kubernetes.

    Deployed applications on AWS using EC2 and S3.

    Built CI/CD pipelines with GitHub Actions and Jenkins.
    """

    skills = extractor.extract_resume(text)

    print("\nDetected Skills\n")

    for skill in skills:
        print(skill)