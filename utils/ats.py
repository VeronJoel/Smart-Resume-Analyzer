import json
import os
import re


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROLES_FILE = os.path.join(BASE_DIR, "data", "roles.json")
ALIASES_FILE = os.path.join(BASE_DIR, "data", "skill_aliases.json")

MIN_JOB_DESCRIPTION_CHARACTERS = 80
MIN_JOB_DESCRIPTION_WORDS = 12

# Aliases that are too ambiguous to match as standalone skills.
# The full canonical skill name can still be matched normally.
AMBIGUOUS_ALIASES = {"node"}


# ---------------------------------------------------------
# JSON HELPERS
# ---------------------------------------------------------

def load_json_file(filepath, default=None):
    """Safely load a JSON object from a file."""
    if default is None:
        default = {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else default

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def load_roles():
    return load_json_file(ROLES_FILE, {})


def load_aliases():
    return load_json_file(ALIASES_FILE, {})


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text):
    """Normalize text while preserving useful skill punctuation."""
    if not text:
        return ""

    text = str(text).lower()
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill(skill):
    """Normalize a skill name for comparisons."""
    return normalize_text(skill).strip(" .,;:()[]{}")


def contains_phrase(text, phrase):
    """
    Match a complete word or phrase, not an arbitrary substring.

    Examples:
    - SQL does not match NoSQL.
    - Java does not match JavaScript.
    - C++ can match C++.
    """
    text = normalize_text(text)
    phrase = normalize_skill(phrase)

    if not text or not phrase:
        return False

    # Avoid interpreting ambiguous aliases as reliable skill evidence.
    if phrase in AMBIGUOUS_ALIASES:
        return False

    # Word boundaries are unsuitable for some programming-language
    # names, so use explicit alphanumeric boundaries instead.
    pattern = (
        r"(?<![a-zA-Z0-9])"
        + re.escape(phrase)
        + r"(?![a-zA-Z0-9])"
    )

    return re.search(pattern, text, flags=re.IGNORECASE) is not None


# ---------------------------------------------------------
# SKILL ALIASES
# ---------------------------------------------------------

def get_skill_variants(skill):
    """Return a skill and its configured aliases."""
    aliases = load_aliases()
    normalized_skill = normalize_skill(skill)

    if not normalized_skill:
        return set()

    variants = {normalized_skill}

    for canonical, alias_list in aliases.items():
        canonical_normalized = normalize_skill(canonical)

        if not isinstance(alias_list, list):
            alias_list = []

        normalized_aliases = {
            normalize_skill(alias)
            for alias in alias_list
            if normalize_skill(alias)
        }

        group = normalized_aliases | {canonical_normalized}

        if normalized_skill in group:
            variants.update(group)

    return variants


def skill_exists(text, skill):
    """Check whether a skill or one of its aliases occurs in text."""
    if not text or not skill:
        return False

    for variant in get_skill_variants(skill):
        if contains_phrase(text, variant):
            return True

    return False


def get_canonical_skill(skill):
    """Convert a configured alias to its canonical name."""
    normalized_skill = normalize_skill(skill)

    if not normalized_skill:
        return ""

    aliases = load_aliases()

    for canonical, alias_list in aliases.items():
        if not isinstance(alias_list, list):
            alias_list = []

        group = {
            normalize_skill(canonical),
            *(
                normalize_skill(alias)
                for alias in alias_list
                if normalize_skill(alias)
            ),
        }

        if normalized_skill in group:
            return canonical.strip()

    return str(skill).strip()


def skills_are_equivalent(first, second):
    """Return True when two skill names share an alias group."""
    first_normalized = normalize_skill(first)
    second_normalized = normalize_skill(second)

    if not first_normalized or not second_normalized:
        return False

    return bool(
        get_skill_variants(first_normalized)
        & get_skill_variants(second_normalized)
    )


def deduplicate_skills(skills):
    """Remove duplicate skills and configured aliases."""
    unique_skills = []

    for skill in skills:
        skill = str(skill).strip()

        if not skill:
            continue

        if any(
            skills_are_equivalent(skill, existing)
            for existing in unique_skills
        ):
            continue

        unique_skills.append(skill)

    return unique_skills


# ---------------------------------------------------------
# ROLE SKILLS
# ---------------------------------------------------------

def get_role_skills(job_role):
    """Get the configured skills for a selected job role."""
    roles = load_roles()
    role_data = roles.get(job_role, {})

    if not isinstance(role_data, dict):
        return []

    skills = role_data.get("skills", [])

    if not isinstance(skills, list):
        return []

    return deduplicate_skills(skills)


# ---------------------------------------------------------
# ROLE SKILL WEIGHTS
# ---------------------------------------------------------

def get_skill_weights(skills):
    """
    Assign higher weights to skills listed earlier in roles.json.

    This is a configurable heuristic, not an actual employer's
    ranking of skills.
    """
    weights = {}
    total_skills = len(skills)

    for index, skill in enumerate(skills):
        if index < max(3, total_skills // 4):
            weight = 3
        elif index < total_skills // 2:
            weight = 2
        else:
            weight = 1

        weights[skill] = weight

    return weights


# ---------------------------------------------------------
# WEIGHTED ATS SCORE
# ---------------------------------------------------------

def calculate_ats_score(resume_text, job_role):
    """Calculate weighted ATS compatibility for a selected role."""
    role_skills = get_role_skills(job_role)

    if not role_skills:
        return {
            "ats_score": 0,
            "found_skills": [],
            "missing_skills": [],
            "required_skills": [],
            "matched_weight": 0,
            "total_weight": 0,
        }

    skill_weights = get_skill_weights(role_skills)

    found_skills = []
    missing_skills = []
    matched_weight = 0
    total_weight = 0

    for skill in role_skills:
        weight = skill_weights.get(skill, 1)
        total_weight += weight

        if skill_exists(resume_text, skill):
            found_skills.append(skill)
            matched_weight += weight
        else:
            missing_skills.append(skill)

    ats_score = (
        round((matched_weight / total_weight) * 100)
        if total_weight
        else 0
    )

    return {
        "ats_score": ats_score,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "required_skills": role_skills,
        "matched_weight": matched_weight,
        "total_weight": total_weight,
    }


# ---------------------------------------------------------
# ATS ANALYSIS
# ---------------------------------------------------------

def analyze_ats(resume_text, job_role):
    """Perform complete ATS analysis for a selected role."""
    result = calculate_ats_score(resume_text, job_role)

    required_count = len(result["required_skills"])
    found_count = len(result["found_skills"])

    result["required_count"] = required_count
    result["found_count"] = found_count
    result["skill_match_percentage"] = (
        round((found_count / required_count) * 100)
        if required_count
        else 0
    )

    return result


# ---------------------------------------------------------
# JOB DESCRIPTION VALIDATION
# ---------------------------------------------------------

def validate_job_description(job_description):
    """Check whether a job description is long enough to analyze."""
    description = str(job_description or "").strip()
    words = re.findall(r"\b[\w+#.-]+\b", description)

    if not description:
        return {
            "is_valid": False,
            "message": (
                "No job description was provided. Paste a job posting "
                "to calculate a job match."
            ),
        }

    if (
        len(description) < MIN_JOB_DESCRIPTION_CHARACTERS
        or len(words) < MIN_JOB_DESCRIPTION_WORDS
    ):
        return {
            "is_valid": False,
            "message": (
                "This job description is too short for a reliable "
                "comparison. Paste the full job posting, including "
                "responsibilities and required qualifications."
            ),
        }

    return {
        "is_valid": True,
        "message": "Job description is long enough to analyze.",
    }


# ---------------------------------------------------------
# JOB DESCRIPTION SKILL CATALOG
# ---------------------------------------------------------

def get_all_known_skills():
    """
    Build a deduplicated catalog from roles.json and
    skill_aliases.json.
    """
    roles = load_roles()
    aliases = load_aliases()
    skills = []

    for role_data in roles.values():
        if not isinstance(role_data, dict):
            continue

        role_skills = role_data.get("skills", [])

        if isinstance(role_skills, list):
            skills.extend(role_skills)

    for canonical, alias_list in aliases.items():
        skills.append(canonical)

        if isinstance(alias_list, list):
            skills.extend(alias_list)

    return deduplicate_skills(skills)


def extract_skills_from_job_description(job_description):
    """Identify unique known skills mentioned in a job description."""
    detected = []

    for skill in get_all_known_skills():
        if skill_exists(job_description, skill):
            detected.append(skill)

    return deduplicate_skills(detected)


# ---------------------------------------------------------
# JOB DESCRIPTION ANALYSIS
# ---------------------------------------------------------

def analyze_job_description(resume_text, job_description):
    """
    Compare resume skills with recognized skills in a job description.

    Existing result keys are preserved for compatibility with
    app.py, result.html, feedback.py, and report generation.
    """
    validation = validate_job_description(job_description)

    if not validation["is_valid"]:
        return {
            "job_description_score": 0,
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "required_count": 0,
            "matched_count": 0,
            "missing_count": 0,
            "is_valid": False,
            "message": validation["message"],
        }

    required_skills = extract_skills_from_job_description(
        job_description
    )

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill_exists(resume_text, skill):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    required_count = len(required_skills)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    if required_count:
        job_description_score = round(
            (matched_count / required_count) * 100
        )

        message = (
            "The match score is based on recognized skills found in "
            "the job description. Review the matched and missing "
            "lists before drawing conclusions."
        )
    else:
        job_description_score = 0

        message = (
            "The description was long enough to analyze, but no "
            "skills from the current skill catalog were recognized. "
            "Try a fuller job posting or expand the skill catalog."
        )

    return {
        "job_description_score": job_description_score,
        "required_skills": sorted(required_skills, key=str.lower),
        "matched_skills": sorted(matched_skills, key=str.lower),
        "missing_skills": sorted(missing_skills, key=str.lower),
        "required_count": required_count,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "is_valid": True,
        "message": message,
    }


# ---------------------------------------------------------
# ATS SUMMARY
# ---------------------------------------------------------

def get_ats_summary(ats_analysis):
    """Generate a short human-readable ATS summary."""
    score = ats_analysis.get("ats_score", 0)

    if score >= 80:
        return (
            "Excellent ATS compatibility. Your resume contains "
            "most of the important skills for this role."
        )

    if score >= 60:
        return (
            "Good ATS compatibility. Your resume matches many "
            "relevant skills, but some improvements are possible."
        )

    if score >= 40:
        return (
            "Moderate ATS compatibility. Several important "
            "role-specific skills are missing."
        )

    return (
        "Low ATS compatibility. Your resume should be better "
        "aligned with the target role."
    )