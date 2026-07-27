from sentence_transformers import SentenceTransformer, util
# Load once when Flask starts
model = SentenceTransformer("intfloat/e5-base-v2")


MATCH_THRESHOLD = 0.85
PARTIAL_THRESHOLD = 0.60


def semantic_skill_match(resume_skills, jd_skills):
    """
    Performs semantic matching between resume skills and JD skills.

    Returns:
    {
        matched,
        missing,
        extra,
        score,
        matches,
        requirement_analysis
    }
    """

    if not resume_skills or not jd_skills:

        return {
            "matched": [],
            "missing": [],
            "extra": [],
            "score": 0,
            "matches": [],
            "requirement_analysis": [],
        }

    # ---------------------------------------
    # Extract skill names
    # ---------------------------------------

    resume_names = [
        skill["skill"]
        for skill in resume_skills
    ]

    jd_names = [
        skill["skill"]
        for skill in jd_skills
    ]

    # ---------------------------------------
    # Encode once
    # ---------------------------------------

    resume_embeddings = model.encode(
        ["passage: " + skill for skill in resume_names],
        convert_to_tensor=True,
    )

    jd_embeddings = model.encode(
        ["query: " + skill for skill in jd_names],
        convert_to_tensor=True,
    )

    similarity_matrix = util.cos_sim(
        jd_embeddings,
        resume_embeddings,
    )
    similarity_matrix = similarity_matrix.cpu().numpy()
    matched = []
    partial = []
    missing = []
    matches = []
    requirement_analysis = []

    matched_resume_indices = set()

    similarity_sum = 0

    # ---------------------------------------
    # Compare each JD skill
    # ---------------------------------------

    for i, jd_skill in enumerate(jd_skills):

        similarities = similarity_matrix[i]

        best_index = similarities.argmax().item()

        similarity = similarities[best_index].item()

        resume_skill = resume_skills[best_index]

        if similarity >= MATCH_THRESHOLD:

            status = "matched"

            matched.append(jd_skill["skill"])

            matched_resume_indices.add(best_index)

            similarity_sum += similarity

        elif similarity >= PARTIAL_THRESHOLD:

            status = "partial"
            partial.append(jd_skill["skill"])
            matched_resume_indices.add(best_index)
            similarity_sum += similarity

        else:

            status = "missing"

            missing.append(jd_skill["skill"])

        matches.append(
            {
                "resume_skill": resume_skill["skill"],
                "jd_skill": jd_skill["skill"],
                "score": round(similarity, 2),
            }
        )

        requirement_analysis.append(
            {
                "requirement": jd_skill["skill"],
                "matched_with": (
                    resume_skill["skill"]
                    if similarity >= PARTIAL_THRESHOLD
                    else "-"
                ),
                "status": status,
                "found_in": (
                    resume_skill["category"]
                    if similarity >= PARTIAL_THRESHOLD
                    else "-"
                ),
                "confidence": round(similarity * 100),
            }
        )

    # ---------------------------------------
    # Extra skills
    # ---------------------------------------

    extra = []

    for index, skill in enumerate(resume_skills):

        if index not in matched_resume_indices:

            extra.append(skill["skill"])

    # ---------------------------------------
    # Overall semantic score
    # ---------------------------------------

    score = round(
        len(matched) / len(jd_skills) * 100,
        2,
    )

    return {

        "matched": sorted(matched),

        "partial":sorted(partial),

        "missing": sorted(missing),

        "extra": sorted(extra),

        "score": score,

        "matches": matches,

        "requirement_analysis": requirement_analysis,
    }


def semantic_section_match(section_text, job_description):

    if not section_text.strip():
        return 0

    section_embedding = model.encode(
        "passage: " + section_text,
        convert_to_tensor=True,
    )

    jd_embedding = model.encode(
        "query: " + job_description,
        convert_to_tensor=True,
    )

    similarity = util.cos_sim(
        section_embedding,
        jd_embedding,
    )

    return round(
        similarity.item() * 100,
        2,
    )
