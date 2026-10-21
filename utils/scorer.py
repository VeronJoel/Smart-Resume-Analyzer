import re


# =========================================================
# GENERAL TECHNICAL SKILLS
# =========================================================

TECHNICAL_SKILLS = [
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript",
    "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Flask",
    "Django", "Spring", "Flutter", "Dart", "Kotlin", "Android",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Firebase", "Git",
    "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Jenkins", "Terraform", "Linux", "Artificial Intelligence",
    "Machine Learning", "Deep Learning", "Natural Language Processing",
    "Computer Vision", "TensorFlow", "PyTorch", "Scikit-learn",
    "NumPy", "Pandas", "Matplotlib", "Seaborn", "OpenCV",
    "Power BI", "Tableau", "Data Analysis", "Data Science",
    "Statistics", "REST API", "API", "Cybersecurity",
    "Network Security", "Excel", "CI/CD", "Ethical Hacking",
    "Penetration Testing", "SIEM", "Firewalls", "Cryptography",
    "Risk Assessment"
]


# =========================================================
# ROLE-SPECIFIC SKILLS
# =========================================================

ROLE_SKILLS = {
    "AI Engineer": [
        "Python", "Machine Learning", "Deep Learning",
        "Artificial Intelligence", "TensorFlow", "PyTorch",
        "Scikit-learn", "Natural Language Processing",
        "Computer Vision", "NumPy", "Pandas", "Git", "Docker", "SQL"
    ],
    "ML Engineer": [
        "Python", "Machine Learning", "Deep Learning", "TensorFlow",
        "PyTorch", "Scikit-learn", "NumPy", "Pandas", "Docker",
        "Kubernetes", "AWS", "Git", "SQL"
    ],
    "Data Scientist": [
        "Python", "Machine Learning", "Statistics", "Pandas",
        "NumPy", "Scikit-learn", "Matplotlib", "Seaborn", "SQL",
        "Data Analysis", "Data Science", "Git"
    ],
    "Data Analyst": [
        "SQL", "Python", "Excel", "Power BI", "Tableau",
        "Data Analysis", "Statistics", "Pandas", "NumPy"
    ],
    "Web Developer": [
        "HTML", "CSS", "JavaScript", "TypeScript", "React",
        "Angular", "Node.js", "Flask", "Django", "SQL",
        "MongoDB", "REST API", "Git", "GitHub"
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript", "TypeScript", "React",
        "Angular", "Vue", "Git", "GitHub", "REST API"
    ],
    "Backend Developer": [
        "Python", "Java", "Node.js", "Flask", "Django", "Spring",
        "SQL", "PostgreSQL", "MongoDB", "REST API", "Docker",
        "Git", "GitHub"
    ],
    "Software Engineer": [
        "Python", "Java", "C++", "JavaScript", "SQL", "Git",
        "GitHub", "REST API", "Docker"
    ],
    "Mobile App Developer": [
        "Flutter", "Dart", "Android", "Java", "Kotlin",
        "Firebase", "REST API", "Git", "GitHub"
    ],
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS", "Azure",
        "CI/CD", "Git", "GitHub", "Jenkins", "Terraform", "Python"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Linux", "Terraform", "Python", "Git", "CI/CD"
    ],
    "Cybersecurity Analyst": [
        "Cybersecurity", "Network Security", "Linux", "Python",
        "Ethical Hacking", "Penetration Testing", "SIEM",
        "Firewalls", "Cryptography", "Risk Assessment"
    ]
}


# =========================================================
# PROJECT QUALITY KEYWORDS
# =========================================================

ACTION_WORDS = [
    "developed", "built", "created", "designed", "implemented",
    "engineered", "deployed", "optimized", "improved", "automated",
    "integrated", "analyzed", "trained", "tested", "configured",
    "managed", "led", "develop", "build", "create", "design",
    "implement", "deploy", "optimize", "improve", "automate",
    "integrate", "analyze", "train", "test", "programmed",
    "launched", "reduced", "increased", "achieved", "generated",
    "streamlined", "refactored", "evaluated", "processed"
]

PROJECT_KEYWORDS = [
    "project", "projects", "application", "app", "website",
    "system", "model", "platform", "software", "tool",
    "dashboard", "prototype", "solution", "product"
]

SECTION_HEADINGS = [
    "education", "academic background", "technical skills",
    "skills", "work experience", "professional experience",
    "experience", "employment", "internship", "certifications",
    "certificates", "achievements", "awards", "languages",
    "publications", "interests", "references", "summary",
    "professional summary", "career objective", "objective"
]

MEASUREMENT_PATTERNS = [
    r"\b\d+(?:\.\d+)?\s*%",
    r"\b\d+(?:\.\d+)?\s+percent\b",
    r"\b\d+(?:\.\d+)?\s*(?:x|times)\b",
    r"\b\d+\+?\s+(?:users|customers|projects|records|requests|"
    r"downloads|transactions|employees|students|clients|"
    r"images|files|tests|datasets|samples|products)\b",
    r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds|seconds|minutes|hours)\b",
    r"\b\d+(?:\.\d+)?\s*(?:gb|mb|tb)\b",
    r"\b(?:reduced|increased|improved|decreased|saved|achieved|"
    r"boosted|cut|grew)\b.{0,60}\b\d+(?:\.\d+)?"
]


# =========================================================
# TEXT HELPERS
# =========================================================

def normalize_text(text):
    """Normalize text for consistent keyword matching."""
    if not text:
        return ""

    text = str(text).lower()
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text).strip()


def contains_keyword(text, keyword):
    """Check whether a keyword appears as a separate term."""
    text = normalize_text(text)
    keyword = normalize_text(keyword)

    if not text or not keyword:
        return False

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + re.escape(keyword)
        + r"(?![a-zA-Z0-9])"
    )

    return bool(re.search(pattern, text, re.IGNORECASE))


def count_keywords(text, keywords):
    """Count distinct keywords present in text."""
    return sum(1 for keyword in keywords if contains_keyword(text, keyword))


def find_keywords(text, keywords):
    """Return the distinct keywords found in text."""
    return [
        keyword for keyword in keywords
        if contains_keyword(text, keyword)
    ]


# =========================================================
# PROJECT SECTION EXTRACTION
# =========================================================

def extract_project_section(text):
    """
    Extract the Projects section when a recognizable heading exists.

    If no Projects heading is found, return the full text to preserve
    compatibility with resumes that do not use standard headings.
    """
    if not text:
        return ""

    lines = str(text).splitlines()
    project_start = None
    project_lines = []

    for index, line in enumerate(lines):
        heading = normalize_text(line).strip(" :-\t|")

        if re.match(r"^(projects|personal projects|academic projects|"
                    r"key projects|selected projects|project experience)$",
                    heading):
            project_start = index + 1
            break

    if project_start is None:
        return str(text)

    for line in lines[project_start:]:
        heading = normalize_text(line).strip(" :-\t|")

        if heading in SECTION_HEADINGS:
            break

        if re.match(
            r"^(professional summary|career objective|work experience|"
            r"technical skills|education|certifications|achievements)$",
            heading
        ):
            break

        project_lines.append(line)

    return "\n".join(project_lines).strip()


# =========================================================
# CONTACT SCORE — 10
# =========================================================

def score_contact(text):
    """Email = 5 points; phone = 5 points."""
    text = str(text or "")

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    phone_pattern = r"(?:\+\d{1,3}[\s.-]?)?(?:\d[\d\s().-]{7,}\d)"

    score = 0

    if re.search(email_pattern, text):
        score += 5

    if re.search(phone_pattern, text):
        score += 5

    return min(score, 10)


# =========================================================
# EDUCATION SCORE — 15
# =========================================================

def score_education(text):
    """Evaluate whether education-related information is present."""
    education_keywords = [
        "education", "bachelor", "b.tech", "btech", "b.e",
        "master", "m.tech", "mtech", "m.e", "degree",
        "university", "college", "school", "gpa", "cgpa",
        "b.sc", "bca", "mca", "phd", "diploma"
    ]

    found = count_keywords(text, education_keywords)
    score = 0

    if found >= 1:
        score += 5
    if found >= 2:
        score += 5
    if found >= 4:
        score += 5

    return min(score, 15)


# =========================================================
# SKILLS SCORE — 20
# =========================================================

def score_skills(text, job_role):
    """
    General technical skills contribute up to 8 points.
    Role-specific skills contribute up to 12 points.
    """
    general_found = find_keywords(text, TECHNICAL_SKILLS)
    role_skills = ROLE_SKILLS.get(job_role, [])
    role_found = find_keywords(text, role_skills)

    general_score = min(len(general_found) * 0.8, 8)

    role_score = (
        (len(role_found) / len(role_skills)) * 12
        if role_skills else 0
    )

    score = round(min(general_score + role_score, 20), 1)

    return score, general_found, role_found


# =========================================================
# PROJECT QUALITY ANALYSIS
# =========================================================

def analyze_project_quality(text):
    """
    Analyze project descriptions for technical detail, action verbs,
    measurable results, and descriptive content.

    Returns an explainable heuristic score out of 20.
    """
    project_text = extract_project_section(text)
    normalized = normalize_text(project_text)

    if not normalized or not any(
        contains_keyword(normalized, keyword)
        for keyword in PROJECT_KEYWORDS
    ):
        return {
            "score": 0,
            "max_score": 20,
            "project_found": False,
            "action_verbs": [],
            "technical_skills": [],
            "has_measurable_results": False,
            "description_length": 0,
            "suggestions": [
                "Add a Projects section with at least one project.",
                "Describe what you built, how you built it, and the result."
            ],
            "summary": "No clear project description was detected."
        }

    action_verbs = find_keywords(normalized, ACTION_WORDS)
    technical_skills = find_keywords(normalized, TECHNICAL_SKILLS)

    has_measurement = any(
        re.search(pattern, normalized, re.IGNORECASE)
        for pattern in MEASUREMENT_PATTERNS
    )

    word_count = len(re.findall(r"\b[\w+#.-]+\b", normalized))

    # Four independently explainable checks, each worth up to 5 points.
    action_score = min(len(action_verbs), 3) / 3 * 5
    technical_score = min(len(technical_skills), 3) / 3 * 5
    measurement_score = 5 if has_measurement else 0
    detail_score = min(word_count / 40, 1) * 5

    score = round(
        action_score
        + technical_score
        + measurement_score
        + detail_score,
        1
    )

    suggestions = []

    if not action_verbs:
        suggestions.append(
            "Start project bullet points with clear action verbs, "
            "such as Built, Developed, Designed, or Implemented."
        )

    if len(technical_skills) < 2:
        suggestions.append(
            "Mention the actual technologies, frameworks, or tools "
            "you used in the project."
        )

    if not has_measurement:
        suggestions.append(
            "Add a truthful measurable result where possible, such as "
            "users served, processing time, accuracy, or performance gains."
        )

    if word_count < 40:
        suggestions.append(
            "Expand the project description to explain the problem, "
            "your implementation, and the outcome."
        )

    if not suggestions:
        suggestions.append(
            "Your project descriptions contain useful technical detail. "
            "Keep the information specific and accurate."
        )

    if score >= 16:
        summary = "Strong project descriptions detected."
    elif score >= 10:
        summary = "Your projects show some useful detail, with room to improve."
    else:
        summary = "Your project descriptions need more specific evidence."

    return {
        "score": score,
        "max_score": 20,
        "project_found": True,
        "action_verbs": action_verbs,
        "technical_skills": technical_skills,
        "has_measurable_results": has_measurement,
        "description_length": word_count,
        "suggestions": suggestions,
        "summary": summary
    }


def score_projects(text):
    """Return the project-quality score out of 20."""
    return analyze_project_quality(text)["score"]


# =========================================================
# STRUCTURE SCORE — 15
# =========================================================

def score_structure(text):
    """Evaluate whether important resume sections exist."""
    sections = {
        "summary": ["summary", "profile", "objective"],
        "education": ["education", "academic background"],
        "skills": ["skills", "technical skills", "technologies"],
        "projects": [
            "projects", "personal projects", "academic projects",
            "selected projects"
        ],
        "experience": [
            "experience", "work experience", "employment", "internship"
        ],
        "certifications": ["certifications", "certificates"]
    }

    found_sections = 0

    for aliases in sections.values():
        if any(contains_keyword(text, alias) for alias in aliases):
            found_sections += 1

    score = 0

    if found_sections >= 2:
        score += 5
    if found_sections >= 4:
        score += 5
    if found_sections >= 6:
        score += 5

    return min(score, 15)


# =========================================================
# COMPLETENESS SCORE — 20
# =========================================================

def score_completeness(text):
    """Evaluate the overall completeness of the resume."""
    checks = [
        ["summary", "profile", "objective"],
        ["education", "university", "college"],
        ["skills", "technical skills"],
        ["projects", "project"],
        ["experience", "work experience", "internship"],
        ["certifications", "certificate"],
        ["achievements", "achievement", "awards"],
        ["languages", "language"]
    ]

    found = 0

    for group in checks:
        if any(contains_keyword(text, keyword) for keyword in group):
            found += 1

    return round(min((found / len(checks)) * 20, 20), 1)


# =========================================================
# MAIN RESUME SCORE
# =========================================================

def calculate_resume_score(text, job_role="AI Engineer"):
    """
    Calculate the complete resume score out of 100.

    Contact       = 10
    Education     = 15
    Skills        = 20
    Projects      = 20
    Structure     = 15
    Completeness  = 20
    """
    if not text:
        return {
            "total": 0,
            "contact": 0,
            "education": 0,
            "skills": 0,
            "projects": 0,
            "structure": 0,
            "completeness": 0,
            "total_score": 0,
            "contact_score": 0,
            "education_score": 0,
            "skills_score": 0,
            "projects_score": 0,
            "structure_score": 0,
            "completeness_score": 0,
            "found_skills": [],
            "role_skills": [],
            "role": job_role,
            "project_analysis": analyze_project_quality("")
        }

    contact_score = score_contact(text)
    education_score = score_education(text)

    skills_score, general_found, role_found = score_skills(
        text, job_role
    )

    project_analysis = analyze_project_quality(text)
    projects_score = project_analysis["score"]

    structure_score = score_structure(text)
    completeness_score = score_completeness(text)

    total = round(min(
        contact_score
        + education_score
        + skills_score
        + projects_score
        + structure_score
        + completeness_score,
        100
    ), 1)

    all_found_skills = list(dict.fromkeys(general_found + role_found))

    return {
        # Original keys
        "total": total,
        "contact": contact_score,
        "education": education_score,
        "skills": skills_score,
        "projects": projects_score,
        "structure": structure_score,
        "completeness": completeness_score,

        # Template-compatible keys
        "total_score": total,
        "contact_score": contact_score,
        "education_score": education_score,
        "skills_score": skills_score,
        "projects_score": projects_score,
        "structure_score": structure_score,
        "completeness_score": completeness_score,

        # Skill information
        "found_skills": all_found_skills,
        "role_skills": role_found,

        # Project-quality details
        "project_analysis": project_analysis,

        # Selected role
        "role": job_role
    }