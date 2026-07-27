import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from extractor.kb_lookup import KnowledgeBase
from recommendation.recomendation_engine import RecommendationEngine
from matchers.skillMatcher import SemanticSkillMatcher
from matchers.requirement_analysis import build_requirement_analysis
from parser import extract_sections
from extractor.processor import Processor

app = Flask(__name__)
CORS(app)

resume_processor = Processor()
kb = KnowledgeBase()

recommendation_engine = RecommendationEngine(kb)
matcher = SemanticSkillMatcher()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    return obj

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    save_path = None

    try:
        # -------------------------
        # Validate Request
        # -------------------------

        resume = request.files.get("resume")
        job_description = request.form.get("job_description")

        if resume is None:
            return jsonify({"error": "Resume file is required"}), 400

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        # -------------------------
        # Save Resume
        # -------------------------

        filename = secure_filename(resume.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        resume.save(save_path)

        # -------------------------
        # Extract Resume Sections
        # -------------------------

        sections = extract_sections(save_path)
        skills_text = sections.get("skills", "")
        projects_text = sections.get("projects", "")
        experience_text = sections.get("experience", "")

        # -------------------------
        # Extract Skills
        # -------------------------
        resume_skills_name = resume_processor.get_resume_skills(skills_text,projects_text,experience_text)
        jd_skills_name = resume_processor.get_skills(job_description)
        skill_skills_name = resume_processor.get_skills(skills_text)
        project_skills_name = resume_processor.get_context_skills(projects_text)
        experience_skills_name = resume_processor.get_context_skills(experience_text)

        result = matcher.match(
              resume_skills_name,
              jd_skills_name
            )
        skills_result = matcher.match(
            skill_skills_name,
              jd_skills_name,
            section="Skills"
            )
        experience_result = matcher.match(
                      experience_skills_name,
                      jd_skills_name,
                   section="Experience"
               ) 
        projects_result = matcher.match(
               project_skills_name,
               jd_skills_name,
               section="Projects"
            )
        # -------------------------
        # Semantic Matching
        # -------------------------

        project_score = projects_result["match_percentage"]
        experience_score = experience_result["match_percentage"]

        # -------------------------
        # Overall Score
        # -------------------------

        overall_score = round(
            (
                skills_result["match_percentage"] * 0.5 +project_score*0.3+experience_score*0.2
            ),
            2,
        )

        # -------------------------
        # Recommendations
        # -------------------------
        skill_needed = result["missing"] + [p["jd_skill"] for p in result["partial"]]
        recommendations = recommendation_engine.generate(skill_needed)

        # -------------------------
        # Logging
        # -------------------------

        app.logger.info(f"Resume Skills: {resume_skills_name}")
        app.logger.info(f"JD Skills: {jd_skills_name}")
        app.logger.info(f"Skill Score: {result['match_percentage']}")
        app.logger.info(f"Matched Skills: {result['matched']}")
        app.logger.info(f"Missing Skills: {result['missing']}")
        app.logger.info(f"Extra Skills: {result['extra']}")
        # -------------------------
        # Requirment analysis
        # -------------------------
        requirement_analysis = build_requirement_analysis(
             skills_result,
             experience_result,
             projects_result,
             jd_skills_name,
           )
        # -------------------------
        # Response
        # -------------------------

        response = {
            "jd_skills": jd_skills_name,
            "resume_skills": resume_skills_name,
            "matched": result["matched"],
            "missing": result["missing"],
            "extra": result["extra"],
            "overall_score": overall_score,
            "skill_match_score": skills_result["match_percentage"],
            "project_relevance": project_score,
            "experience_relevance": experience_score,
            "requirement_analysis": requirement_analysis,
            "recommendations": recommendations,
        }

        return jsonify(serialize(response))

    except Exception as e:

        app.logger.exception("Analysis failed")

        return jsonify(
            {
                "error": str(e)
            }
        ), 500

    finally:

        if save_path and os.path.exists(save_path):
            os.remove(save_path)


if __name__ == "__main__":
    app.run(debug=True)