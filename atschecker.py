import re

def calculate_ats_score(resume_text):

    score = 100
    feedback = []

    # Email
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        score -= 10
        feedback.append("Missing email address")

    # Phone
    if not re.search(r'\d{10}', resume_text):
        score -= 10
        feedback.append("Missing phone number")

    # LinkedIn
    if "linkedin" not in resume_text.lower():
        score -= 10
        feedback.append("LinkedIn profile not found")

    # GitHub
    if "github" not in resume_text.lower():
        score -= 10
        feedback.append("GitHub profile not found")

    return score, feedback