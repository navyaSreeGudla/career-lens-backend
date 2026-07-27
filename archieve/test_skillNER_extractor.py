import spacy
from spacy.matcher import PhraseMatcher

from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor

# Load spaCy model
nlp = spacy.load("en_core_web_lg")

# Initialize SkillNER
skill_extractor = SkillExtractor(
    nlp,
    SKILL_DB,
    PhraseMatcher
)

# -------------------------
# Test text
# -------------------------

text = """
Designed and implemented a microservices-based backend using Spring Boot, Kafka, Redis, Docker and Kubernetes. Deployed applications on AWS using EC2 and S3. Built CI/CD pipelines with GitHub Actions and Jenkins.
"""

# -------------------------
# Extract skills
# -------------------------

annotations = skill_extractor.annotate(text)

print("\nDetected Skills\n")

results = annotations["results"]

for category in results:
    print(f"\n{category.upper()}")

    for skill in results[category]:
        print("-", skill["doc_node_value"])