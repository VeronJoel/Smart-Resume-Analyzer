import re


# =========================================================
# SECTION ALIASES
# =========================================================

SECTION_ALIASES = {

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career summary",
        "objective",
        "career objective",
        "about me"
    ],

    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "qualifications"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "technologies",
        "technical expertise",
        "skills & technologies",
        "skills and technologies"
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "major projects",
        "projects undertaken"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "internship",
        "internships"
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "courses",
        "courses & certifications"
    ],

    "achievements": [
        "achievements",
        "achievement",
        "awards",
        "honors",
        "honours",
        "accomplishments"
    ],

    "languages": [
        "languages",
        "language",
        "spoken languages"
    ],

    "interests": [
        "interests",
        "hobbies",
        "hobbies & interests",
        "personal interests"
    ]
}


# =========================================================
# TECHNICAL SKILLS
# =========================================================

TECHNICAL_SKILLS = [

    # Programming
    "Python",
    "Java",
    "C++",
    "C",
    "C#",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "PHP",
    "Ruby",

    # Web
    "HTML",
    "CSS",
    "React",
    "React.js",
    "ReactJS",
    "Angular",
    "Vue",
    "Vue.js",
    "Node.js",
    "Node JS",
    "Express.js",
    "Flask",
    "Django",
    "Spring",
    "Spring Boot",

    # Mobile
    "Flutter",
    "Dart",
    "Android",
    "Kotlin",
    "Swift",
    "React Native",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Postgres",
    "MongoDB",
    "Firebase",
    "SQLite",
    "Redis",

    # AI / ML
    "Artificial Intelligence",
    "AI",
    "Machine Learning",
    "ML",
    "Deep Learning",
    "DL",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "CV",
    "TensorFlow",
    "PyTorch",
    "Torch",
    "Scikit-learn",
    "Scikit Learn",
    "sklearn",
    "Keras",

    # Data
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "OpenCV",
    "Power BI",
    "Tableau",
    "Data Analysis",
    "Data Science",
    "Data Visualization",
    "Statistics",
    "Excel",
    "Jupyter",

    # Cloud
    "AWS",
    "Azure",
    "GCP",
    "Google Cloud",

    # DevOps
    "Docker",
    "Kubernetes",
    "Jenkins",
    "Terraform",
    "CI/CD",
    "Linux",
    "Shell Scripting",

    # Version Control
    "Git",
    "GitHub",
    "GitLab",

    # APIs
    "REST API",
    "REST APIs",
    "API",
    "APIs",
    "GraphQL",

    # Security
    "Cybersecurity",
    "Network Security",
    "Ethical Hacking",
    "Penetration Testing",
    "Cryptography",
    "SIEM",
    "Firewalls"
]


# =========================================================
# SKILL CANONICALIZATION
# =========================================================

SKILL_CANONICAL = {

    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",

    "ml": "Machine Learning",
    "machine learning": "Machine Learning",

    "dl": "Deep Learning",
    "deep learning": "Deep Learning",

    "nlp": "Natural Language Processing",
    "natural language processing":
        "Natural Language Processing",

    "cv": "Computer Vision",
    "computer vision": "Computer Vision",

    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",

    "pytorch": "PyTorch",
    "torch": "PyTorch",

    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",

    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",

    "javascript": "JavaScript",
    "js": "JavaScript",

    "typescript": "TypeScript",
    "ts": "TypeScript",

    "react": "React",
    "react.js": "React",
    "reactjs": "React",

    "node.js": "Node.js",
    "node js": "Node.js",

    "express.js": "Express.js",

    "vue.js": "Vue",
    "vue": "Vue",

    "api": "REST API",
    "apis": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",

    "c++": "C++",

    "c#": "C#"
}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text)

    text = text.replace(
        "\u2013",
        "-"
    )

    text = text.replace(
        "\u2014",
        "-"
    )

    text = text.replace(
        "\u2022",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# NORMALIZE HEADING
# =========================================================

def normalize_heading(heading):

    if not heading:
        return ""

    heading = heading.lower()

    heading = heading.strip()

    heading = re.sub(
        r"[:\-|]+$",
        "",
        heading
    )

    heading = re.sub(
        r"[^a-z0-9& ]",
        " ",
        heading
    )

    heading = re.sub(
        r"\s+",
        " ",
        heading
    )

    return heading.strip()


# =========================================================
# DETECT SECTION HEADING
# =========================================================

def detect_section_heading(line):

    if not line:
        return None

    normalized = normalize_heading(
        line
    )

    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            alias_normalized = normalize_heading(
                alias
            )

            if normalized == alias_normalized:

                return section

    return None


# =========================================================
# EXTRACT EMAIL
# =========================================================

def extract_email(text):

    if not text:
        return ""

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b",
        text
    )

    if match:
        return match.group(0)

    return ""


# =========================================================
# EXTRACT PHONE
# =========================================================

def extract_phone(text):

    if not text:
        return ""

    patterns = [

        r"\+\d{1,3}[\s.-]?"
        r"\(?\d{2,4}\)?[\s.-]?"
        r"\d{3,4}[\s.-]?"
        r"\d{3,4}",

        r"\b\d{10}\b",

        r"\b\d{3}[\s.-]\d{3}[\s.-]\d{4}\b"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return match.group(
                0
            ).strip()

    return ""


# =========================================================
# SKILL MATCHING
# =========================================================

def skill_found(
    text,
    skill
):

    if not text or not skill:
        return False

    text_lower = text.lower()

    skill_lower = skill.lower()

    # Special handling for symbols
    escaped = re.escape(
        skill_lower
    )

    # Flexible whitespace
    escaped = escaped.replace(
        r"\ ",
        r"\s+"
    )

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + escaped
        + r"(?![a-zA-Z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text_lower
        )
    )


# =========================================================
# EXTRACT SKILLS
# =========================================================

def extract_skills(text):

    if not text:
        return []

    text = normalize_text(
        text
    )

    detected = []

    for skill in TECHNICAL_SKILLS:

        if skill_found(
            text,
            skill
        ):

            normalized_skill = (
                SKILL_CANONICAL.get(
                    skill.lower(),
                    skill
                )
            )

            if normalized_skill not in detected:

                detected.append(
                    normalized_skill
                )

    return detected


# =========================================================
# EXTRACT SECTIONS
# =========================================================

def extract_sections(text):

    if not text:
        return {}

    lines = text.splitlines()

    sections = {}

    current_section = None

    current_content = []

    def save_current_section():

        nonlocal current_content

        if current_section:

            content = "\n".join(
                current_content
            ).strip()

            sections[
                current_section
            ] = content

        current_content = []


    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        detected_section = (
            detect_section_heading(
                stripped
            )
        )

        if detected_section:

            save_current_section()

            current_section = (
                detected_section
            )

            continue

        if current_section:

            current_content.append(
                stripped
            )


    save_current_section()

    return sections


# =========================================================
# SECTION STATUS
# =========================================================

def get_section_status(
    sections
):

    status = {}

    for section in SECTION_ALIASES.keys():

        content = sections.get(
            section,
            ""
        )

        status[section] = bool(
            content.strip()
        )

    return status


# =========================================================
# RESUME INFORMATION
# =========================================================

def extract_resume_information(
    text
):

    if not text:
        text = ""

    normalized_text = normalize_text(
        text
    )

    sections = extract_sections(
        text
    )

    section_status = get_section_status(
        sections
    )

    email = extract_email(
        text
    )

    phone = extract_phone(
        text
    )

    skills = extract_skills(
        text
    )

    return {

        "text": text,

        "normalized_text":
            normalized_text,

        "sections":
            sections,

        "section_status":
            section_status,

        "email":
            email,

        "phone":
            phone,

        "skills":
            skills

    }