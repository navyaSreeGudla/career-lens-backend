

class RecommendationEngine:
    """
    Generates learning recommendations for missing skills.
    """

    def __init__(self, kb):
        self.kb = kb

    # -------------------------------------------------

    def generate(self, missing_skills):

        recommendations = []

        for skill in missing_skills:

            # Resolve aliases to canonical skill names
            canonical = self.kb.resolve(skill) or skill

            category = (
                self.kb.get_skill_category(canonical)
                or "Uncategorized"
            )

            resource = self.kb.get_resource(canonical)

            recommendations.append(
                {
                    "skill": canonical,
                    "category": category,
                    "advice": self.generate_advice(
                        canonical,
                        category
                    ),
                    "resource": resource
                    or {
                        "type": "Documentation",
                        "url": None
                    },
                }
            )

        return recommendations

    # -------------------------------------------------

    def generate_advice(self, skill, category):

        advice = {

            "Programming Language":
                f"Strengthen your knowledge of {skill} through coding practice and solving algorithmic problems.",

            "Frontend Framework":
                f"Build responsive web applications and reusable UI components using {skill}.",

            "Backend Framework":
                f"Develop RESTful APIs and scalable backend services using {skill}.",

            "Database":
                f"Practice schema design, indexing, joins, and query optimization with {skill}.",

            "Cloud Platform":
                f"Deploy and manage real-world applications on {skill}.",

            "Cloud Service":
                f"Learn how {skill} integrates into cloud-native architectures.",

            "DevOps":
                f"Automate builds, deployments, and CI/CD pipelines using {skill}.",

            "AI/ML":
                f"Build machine learning and deep learning projects using {skill}.",

            "Data Engineering":
                f"Create scalable ETL pipelines and data workflows using {skill}.",

            "Testing":
                f"Write unit, integration, and automated tests using {skill}.",

            "API":
                f"Practice designing and consuming RESTful APIs with {skill}.",

        }

        return advice.get(
            category,
            f"Learn the fundamentals of {skill} through hands-on projects."
        )