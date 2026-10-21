# =========================================================
# SMART RESUME FEEDBACK ENGINE
# =========================================================

def add_feedback(feedback, message):
    """Add feedback only when it is non-empty and not duplicated."""
    if message and message not in feedback:
        feedback.append(message)


def get_score(analysis, key, default=0):
    """Safely retrieve a score using either supported key format."""
    if not isinstance(analysis, dict):
        return default

    if key in analysis:
        return analysis.get(key, default) or default

    old_key = key.replace("_score", "")
    return analysis.get(old_key, default) or default


def add_skill_feedback(feedback, skills, prefix, limit=5):
    """Add a recommendation for missing skills without duplicating advice."""
    if not skills:
        return

    skill_text = ", ".join(str(skill) for skill in skills[:limit])

    add_feedback(
        feedback,
        f"{prefix}{skill_text}. Add these skills only if you genuinely "
        "have the relevant knowledge or experience."
    )


# =========================================================
# MAIN FEEDBACK GENERATOR
# =========================================================

def generate_feedback(analysis, ats_analysis, job_match=None):
    """
    Generate personalized resume recommendations.

    Recommendations use:
    - Overall resume score
    - Individual section scores
    - ATS compatibility and missing role skills
    - Project quality analysis
    - Job description match, when valid
    - Number of detected skills

    Returns a maximum of 10 recommendations.
    """

    feedback = []

    analysis = analysis if isinstance(analysis, dict) else {}
    ats_analysis = ats_analysis if isinstance(ats_analysis, dict) else {}
    job_match = job_match if isinstance(job_match, dict) else None

    # =====================================================
    # RESUME SCORES
    # =====================================================

    total_score = float(get_score(analysis, "total_score", 0))
    contact_score = float(get_score(analysis, "contact_score", 0))
    education_score = float(get_score(analysis, "education_score", 0))
    skills_score = float(get_score(analysis, "skills_score", 0))
    projects_score = float(get_score(analysis, "projects_score", 0))
    structure_score = float(get_score(analysis, "structure_score", 0))
    completeness_score = float(get_score(analysis, "completeness_score", 0))

    # =====================================================
    # ATS INFORMATION
    # =====================================================

    ats_score = float(ats_analysis.get("ats_score", 0) or 0)

    found_skills = ats_analysis.get("found_skills", []) or []
    missing_skills = ats_analysis.get("missing_skills", []) or []

    # =====================================================
    # JOB DESCRIPTION INFORMATION
    # =====================================================

    job_is_valid = bool(job_match and job_match.get("is_valid", True))

    job_missing_skills = []
    job_description_score = 0
    job_required_count = 0

    if job_is_valid:
        job_missing_skills = job_match.get("missing_skills", []) or []
        job_description_score = float(
            job_match.get("job_description_score", 0) or 0
        )
        job_required_count = int(
            job_match.get(
                "required_count",
                len(job_match.get("required_skills", []) or [])
            ) or 0
        )

    # =====================================================
    # 1. CONTACT INFORMATION
    # =====================================================

    if contact_score < 5:
        add_feedback(
            feedback,
            "Add clear contact information, including a professional email "
            "address and phone number."
        )
    elif contact_score < 10:
        add_feedback(
            feedback,
            "Check that your professional email address and phone number "
            "are complete and easy to find."
        )

    # =====================================================
    # 2. EDUCATION
    # =====================================================

    if education_score < 5:
        add_feedback(
            feedback,
            "Add a clearly labeled Education section with your degree, "
            "institution and relevant academic details."
        )
    elif education_score < 10:
        add_feedback(
            feedback,
            "Strengthen your Education section by including your degree, "
            "university, graduation year and relevant academic details."
        )

    # =====================================================
    # 3. TECHNICAL SKILLS
    # =====================================================

    if skills_score < 8:
        add_feedback(
            feedback,
            "Expand your technical skills section with relevant programming "
            "languages, tools, technologies and frameworks."
        )
    elif skills_score < 14:
        add_feedback(
            feedback,
            "Improve your skills section by organizing relevant technologies "
            "into categories and using standard industry terminology."
        )

    if missing_skills:
        add_skill_feedback(
            feedback,
            missing_skills,
            "For your selected role, consider developing or highlighting "
            "relevant missing skills such as "
        )

    # =====================================================
    # 4. PROJECT QUALITY ANALYSIS
    # =====================================================

    project_analysis = analysis.get("project_analysis", {})

    if not isinstance(project_analysis, dict):
        project_analysis = {}

    project_suggestions = project_analysis.get("suggestions", []) or []

    # Prefer specific project-analysis suggestions.
    # The score-based advice below acts as a fallback.
    for suggestion in project_suggestions:
        if isinstance(suggestion, str):
            add_feedback(feedback, suggestion)

    if projects_score < 5:
        add_feedback(
            feedback,
            "Add one or two relevant projects. Explain what you built, "
            "which technologies you used and what the result was."
        )
    elif projects_score < 12:
        add_feedback(
            feedback,
            "Improve your project descriptions by explaining your contribution, "
            "the technologies used and the problem each project solves."
        )
    elif projects_score < 17 and not project_suggestions:
        add_feedback(
            feedback,
            "Make project achievements more measurable by including truthful "
            "figures such as accuracy, processing time or performance gains."
        )

    # =====================================================
    # 5. RESUME STRUCTURE
    # =====================================================

    if structure_score < 5:
        add_feedback(
            feedback,
            "Improve your resume structure with clearly labeled sections such "
            "as Summary, Education, Skills, Projects and Experience."
        )
    elif structure_score < 10:
        add_feedback(
            feedback,
            "Use consistent section headings, spacing and formatting so "
            "recruiters and ATS systems can find important information easily."
        )

    # =====================================================
    # 6. RESUME COMPLETENESS
    # =====================================================

    if completeness_score < 8:
        add_feedback(
            feedback,
            "Your resume may be incomplete. Add relevant sections such as "
            "Experience, Certifications, Achievements or Languages where applicable."
        )
    elif completeness_score < 14:
        add_feedback(
            feedback,
            "Strengthen your resume with additional relevant sections and "
            "supporting details that demonstrate your qualifications."
        )

    # =====================================================
    # 7. ATS COMPATIBILITY
    # =====================================================

    if ats_score < 40:
        add_feedback(
            feedback,
            "Your ATS compatibility is low. Use standard section headings, "
            "relevant job keywords and a simple, text-friendly resume layout."
        )
    elif ats_score < 60:
        add_feedback(
            feedback,
            "Improve ATS compatibility by naturally incorporating relevant "
            "role-specific keywords throughout your resume."
        )
    elif ats_score < 80:
        add_feedback(
            feedback,
            "Your ATS compatibility is reasonable. Review the missing role "
            "skills and include relevant ones that match your actual experience."
        )

    # =====================================================
    # 8. DETECTED SKILLS
    # =====================================================

    if len(found_skills) < 5:
        add_feedback(
            feedback,
            "Your resume contains relatively few detectable technical skills. "
            "Clearly list relevant technologies that you actually know."
        )
    elif len(found_skills) < 10:
        add_feedback(
            feedback,
            "Consider expanding your skills section with additional relevant "
            "technologies you have genuinely used."
        )

    # =====================================================
    # 9. JOB DESCRIPTION MATCH
    # =====================================================

    if job_match:
        if not job_is_valid:
            # Do not interpret an invalid job description's 0 score
            # as a genuine mismatch.
            add_feedback(
                feedback,
                "Paste the full job description, including responsibilities "
                "and required qualifications, to get more useful job-specific "
                "matching recommendations."
            )

        elif job_required_count == 0:
            add_feedback(
                feedback,
                "The job description did not contain recognizable skills "
                "from the current skill catalog. Try a fuller job posting "
                "or expand the application's skill catalog."
            )

        else:
            if job_description_score < 40:
                add_feedback(
                    feedback,
                    "Your resume has a low match with the provided job "
                    "description. Review its key responsibilities and "
                    "required skills, then tailor your resume honestly."
                )
            elif job_description_score < 60:
                add_feedback(
                    feedback,
                    "Your resume has a moderate match with the job description. "
                    "Address relevant missing requirements that reflect your "
                    "actual skills and experience."
                )
            elif job_description_score < 80:
                add_feedback(
                    feedback,
                    "Your resume matches the job description reasonably well. "
                    "Review the remaining missing requirements and highlight "
                    "relevant experience more clearly."
                )
            else:
                add_feedback(
                    feedback,
                    "Your resume has a strong match with the recognized job "
                    "skills. Keep tailoring your project achievements and "
                    "experience to the specific position."
                )

            if job_missing_skills:
                add_skill_feedback(
                    feedback,
                    job_missing_skills,
                    "The job description includes skills not detected in "
                    "your resume, such as "
                )

    # =====================================================
    # 10. OVERALL RESUME SCORE
    # =====================================================

    if total_score < 40:
        add_feedback(
            feedback,
            "Your overall resume score is low. Prioritize the weakest "
            "sections and ensure your contact information, skills and "
            "projects are clearly presented."
        )
    elif total_score < 60:
        add_feedback(
            feedback,
            "Your resume has a starting foundation, but several areas need "
            "attention. Prioritize relevant skills, project descriptions "
            "and completeness."
        )
    elif total_score < 75:
        add_feedback(
            feedback,
            "Your resume is developing well. Focus on measurable project "
            "achievements, role-specific skills and clear formatting."
        )
    elif total_score >= 90:
        add_feedback(
            feedback,
            "Your resume has a strong overall score. Continue tailoring "
            "keywords and achievements to each specific job application."
        )

    # =====================================================
    # FALLBACK
    # =====================================================

    if not feedback:
        add_feedback(
            feedback,
            "Your resume is in good shape. Continue tailoring it to each "
            "job description and keep your achievements clear and measurable."
        )

    # =====================================================
    # RETURN UP TO 10 RECOMMENDATIONS
    # =====================================================

    return feedback[:10]