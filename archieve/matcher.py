# matcher/skill_matcher.py
def get_skill_names(skills):
    """
    Extract only the canonical skill names from the extractor output.
    """

    return {
        item["skill"]
        for item in skills
    }

def match_skills(resume_skills, jd_skills):

    resume = get_skill_names(resume_skills)

    jd = get_skill_names(jd_skills)

    matched = resume & jd
    missing = jd - resume
    extra = resume - jd

    score = 0

    if jd:
        score = round((len(matched) / len(jd)) * 100, 2)

    return {

        "matched": sorted(matched),

        "missing": sorted(missing),

        "extra": sorted(extra),

        "score": score
    }