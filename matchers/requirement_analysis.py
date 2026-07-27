"""
Requirement Analysis Builder

Combines semantic matching results from:
- Skills
- Experience
- Projects

For each Job Description requirement, finds the best
resume match and reports where it was found.
"""


def build_requirement_analysis(
    skills_result,
    experience_result,
    projects_result,
    jd_skills,
):
    """
    Parameters
    ----------
    skills_result : dict
    experience_result : dict
    projects_result : dict
    jd_skills : list[str]

    Returns
    -------
    list[dict]
    """

    # -----------------------------------------
    # Combine matched + partial matches
    # -----------------------------------------

    all_matches = (
        skills_result["matched"]
        + skills_result["partial"]
        + experience_result["matched"]
        + experience_result["partial"]
        + projects_result["matched"]
        + projects_result["partial"]
    )

    # -----------------------------------------
    # Keep highest similarity for each JD skill
    # -----------------------------------------

    best_matches = {}

    for match in all_matches:

        jd_skill = match["jd_skill"]

        if (
            jd_skill not in best_matches
            or match["similarity"] > best_matches[jd_skill]["similarity"]
        ):
            best_matches[jd_skill] = match

    # -----------------------------------------
    # Build requirement analysis
    # -----------------------------------------

    requirement_analysis = []

    for jd_skill in jd_skills:

        if jd_skill in best_matches:

            match = best_matches[jd_skill]

            requirement_analysis.append(
                {
                    "requirement": jd_skill,
                    "status": match["status"],          # matched / partial
                    "found_in": match["found_in"],
                    "confidence": round(match["similarity"] * 100),
                }
            )

        else:

            requirement_analysis.append(
                {
                    "requirement": jd_skill,
                    "status": "missing",
                    "found_in": "-",
                    "confidence": 0,
                }
            )

    return requirement_analysis