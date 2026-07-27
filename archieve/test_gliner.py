from gliner import GLiNER

# Load model
model = GLiNER.from_pretrained(
    "urchade/gliner_large-v2.1"
)

text = """
Designed and implemented a microservices-based backend using Spring Boot,
Kafka, Redis, Docker and Kubernetes.
Deployed applications on AWS using EC2 and S3.
Built CI/CD pipelines with GitHub Actions and Jenkins.
"""

# Labels to detect
labels = [
    "programming language",
    "framework",
    "database",
    "cloud platform",
    "cloud service",
    "developer tool",
    "technology",
    "software",
    "skill"
]

entities = model.predict_entities(text, labels)

print("\nDetected Entities:\n")

for entity in entities:
    print(entity)