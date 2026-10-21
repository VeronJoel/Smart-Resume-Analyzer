import os
import json
import uuid
import html

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response
)

from werkzeug.utils import secure_filename

from pypdf import PdfReader

from docx import Document

from utils.scorer import calculate_resume_score

from utils.ats import (
    analyze_ats,
    analyze_job_description
)

from utils.feedback import generate_feedback

from utils.extractor import (
    extract_resume_information
)

from utils.improvement_assistant import improve_bullet_point


from utils.database import (
    init_database,
    save_analysis,
    get_all_analyses,
    get_analysis,
    delete_analysis
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Ensure the database schema exists for local runs and WSGI deployments.
init_database()


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

ROLES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "roles.json"
)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = (
    MAX_FILE_SIZE
)


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# LOAD JOB ROLES
# =========================================================

def load_roles():

    try:

        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return {}


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(filepath):

    text = []

    reader = PdfReader(
        filepath
    )

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text.append(
                page_text
            )

    return "\n".join(text)


# =========================================================
# DOCX TEXT EXTRACTION
# =========================================================

def extract_docx_text(filepath):

    document = Document(
        filepath
    )

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            paragraphs.append(
                paragraph.text
            )

    return "\n".join(
        paragraphs
    )


# =========================================================
# GENERIC TEXT EXTRACTION
# =========================================================

def extract_text(filepath):

    extension = filepath.rsplit(
        ".",
        1
    )[1].lower()


    if extension == "pdf":

        return extract_pdf_text(
            filepath
        )


    if extension == "docx":

        return extract_docx_text(
            filepath
        )


    return ""


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    roles = load_roles()

    return render_template(
        "index.html",
        roles=roles
    )


# =========================================================
# ANALYZE RESUME
# =========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    file = request.files.get(
        "resume"
    )


    job_role = request.form.get(
        "job_role",
        "AI Engineer"
    ).strip()


    job_description = request.form.get(
        "job_description",
        ""
    ).strip()


    # -----------------------------------------------------
    # VALIDATE FILE
    # -----------------------------------------------------

    if not file:

        return render_template(
            "index.html",
            roles=load_roles(),
            error="Please upload a resume."
        )


    if file.filename == "":

        return render_template(
            "index.html",
            roles=load_roles(),
            error="Please select a resume file."
        )


    if not allowed_file(
        file.filename
    ):

        return render_template(
            "index.html",
            roles=load_roles(),
            error=(
                "Only PDF and DOCX files "
                "are supported."
            )
        )


    # -----------------------------------------------------
    # SAVE FILE
    # -----------------------------------------------------

    safe_name = secure_filename(file.filename)
    stem, extension = os.path.splitext(safe_name)
    filename = f"{stem}_{uuid.uuid4().hex[:8]}{extension.lower()}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    file.save(
        filepath
    )


    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    try:

        resume_text = extract_text(
            filepath
        )

    except Exception as error:

        return render_template(
            "index.html",
            roles=load_roles(),
            error=(
                "Could not read the resume: "
                f"{error}"
            )
        )


    if not resume_text.strip():

        return render_template(
            "index.html",
            roles=load_roles(),
            error=(
                "No readable text was found "
                "in the uploaded resume."
            )
        )


    # -----------------------------------------------------
    # RESUME INFORMATION
    # -----------------------------------------------------

    resume_information = (
        extract_resume_information(
            resume_text
        )
    )


    # -----------------------------------------------------
    # RESUME SCORE
    # -----------------------------------------------------

    analysis = calculate_resume_score(
        resume_text,
        job_role
    )


    # -----------------------------------------------------
    # ATS
    # -----------------------------------------------------

    ats_analysis = analyze_ats(
        resume_text,
        job_role
    )


    # -----------------------------------------------------
    # JOB MATCH
    # -----------------------------------------------------

    job_match = None


    if job_description:

        job_match = (
            analyze_job_description(
                resume_text,
                job_description
            )
        )


    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    feedback = generate_feedback(
        analysis,
        ats_analysis,
        job_match
    )


    # -----------------------------------------------------
    # JOB MATCH VALUES
    # -----------------------------------------------------

    job_description_score = 0

    job_matched_skills = []

    job_missing_skills = []


    if job_match:

        job_description_score = (
            job_match.get(
                "job_description_score",
                0
            )
        )


        job_matched_skills = (
            job_match.get(
                "matched_skills",
                []
            )
        )


        job_missing_skills = (
            job_match.get(
                "missing_skills",
                []
            )
        )


    # -----------------------------------------------------
    # SAVE DATABASE
    # -----------------------------------------------------

    analysis_id = save_analysis(

        filename=filename,

        job_role=job_role,

        resume_score=analysis.get(
            "total_score",
            analysis.get(
                "total",
                0
            )
        ),

        ats_score=ats_analysis.get(
            "ats_score",
            0
        ),

        found_skills=ats_analysis.get(
            "found_skills",
            []
        ),

        missing_skills=ats_analysis.get(
            "missing_skills",
            []
        ),

        feedback=feedback,

        job_description_score=(
            job_description_score
        ),

        job_matched_skills=(
            job_matched_skills
        ),

        job_missing_skills=(
            job_missing_skills
        )
    )


    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    return render_template(

        "result.html",

        analysis=analysis,

        ats_analysis=ats_analysis,

        feedback=feedback,

        filename=filename,

        job_role=job_role,

        analysis_id=analysis_id,

        resume_information=(
            resume_information
        ),

        resume_sections=(
            resume_information.get(
                "sections",
                {}
            )
        ),

        section_status=(
            resume_information.get(
                "section_status",
                {}
            )
        ),

        job_match=job_match
    )
    

# =========================================================
# AI RESUME IMPROVEMENT ASSISTANT
# =========================================================

@app.route("/improve", methods=["GET", "POST"])
def improve_resume():
    """Improve a resume bullet using transparent, rule-based guidance."""
    result = None
    error = None

    original_text = ""
    job_role = "AI Engineer"
    focus = "impact"

    roles = load_roles()

    if request.method == "POST":
        original_text = request.form.get(
            "bullet_text",
            ""
        ).strip()

        job_role = request.form.get(
            "job_role",
            "AI Engineer"
        ).strip()

        focus = request.form.get(
            "focus",
            "impact"
        ).strip()

        if not original_text:
            error = (
                "Paste a resume bullet or project "
                "description first."
            )

        elif len(original_text) > 2000:
            error = (
                "Please keep the text under "
                "2,000 characters."
            )

        elif len(original_text.split()) < 3:
            error = (
                "Please enter a complete sentence or "
                "bullet with at least 3 words."
            )

        else:
            result = improve_bullet_point(
                original_text,
                job_role=job_role,
                focus=focus
            )

    return render_template(
        "improvement_assistant.html",
        roles=roles,
        result=result,
        error=error,
        original_text=original_text,
        job_role=job_role,
        focus=focus
    )


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    analyses = get_all_analyses()

    if analyses:

        total = len(
            analyses
        )

        resume_scores = [

            float(
                item.get(
                    "resume_score",
                    0
                ) or 0
            )

            for item in analyses

        ]

        ats_scores = [

            float(
                item.get(
                    "ats_score",
                    0
                ) or 0
            )

            for item in analyses

        ]

        job_scores = [

            float(
                item.get(
                    "job_description_score",
                    0
                ) or 0
            )

            for item in analyses

        ]

        statistics = {

            "total_analyses":
                total,

            "best_resume_score":
                round(
                    max(resume_scores),
                    1
                ),

            "best_ats_score":
                round(
                    max(ats_scores),
                    1
                ),

            "average_resume_score":
                round(
                    sum(resume_scores)
                    / total,
                    1
                ),

            "average_ats_score":
                round(
                    sum(ats_scores)
                    / total,
                    1
                ),

            "best_job_description_score":
                round(
                    max(job_scores),
                    1
                ),

            "average_job_description_score":
                round(
                    sum(job_scores)
                    / total,
                    1
                )
        }

    else:

        statistics = {

            "total_analyses": 0,

            "best_resume_score": 0,

            "best_ats_score": 0,

            "average_resume_score": 0,

            "average_ats_score": 0,

            "best_job_description_score": 0,

            "average_job_description_score": 0
        }

    return render_template(
        "history.html",
        analyses=analyses,
        statistics=statistics
    )


# =========================================================
# HISTORY DETAIL
# =========================================================

@app.route(
    "/history/<int:analysis_id>"
)
def history_detail(
    analysis_id
):

    analysis = get_analysis(
        analysis_id
    )

    if not analysis:

        return redirect(
            url_for("history")
        )

    return render_template(
        "history_detail.html",
        analysis=analysis
    )


# =========================================================
# DELETE HISTORY
# =========================================================

@app.route(
    "/history/delete/<int:analysis_id>",
    methods=["POST"]
)
def delete_history(
    analysis_id
):

    delete_analysis(
        analysis_id
    )

    return redirect(
        url_for("history")
    )


# =========================================================
# DOWNLOAD / PRINT REPORT
# =========================================================

@app.route(
    "/report/<int:analysis_id>"
)
def report(
    analysis_id
):

    analysis = get_analysis(
        analysis_id
    )

    if not analysis:

        return redirect(
            url_for("history")
        )

    resume_score = analysis.get(
        "resume_score",
        0
    )

    ats_score = analysis.get(
        "ats_score",
        0
    )

    job_score = analysis.get(
        "job_description_score",
        0
    )

    found_skills = analysis.get(
        "found_skills",
        []
    )

    missing_skills = analysis.get(
        "missing_skills",
        []
    )

    job_matched_skills = analysis.get(
        "job_matched_skills",
        []
    )

    job_missing_skills = analysis.get(
        "job_missing_skills",
        []
    )

    feedback = analysis.get(
        "feedback",
        []
    )

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Smart Resume Analyzer Report
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    color: #222;
}}

h1 {{
    margin-bottom: 5px;
}}

.subtitle {{
    color: #666;
    margin-bottom: 30px;
}}

.scores {{
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
}}

.score {{
    border: 1px solid #ddd;
    padding: 20px;
    border-radius: 10px;
    min-width: 160px;
}}

.score h2 {{
    margin: 0;
    font-size: 30px;
}}

.score p {{
    color: #666;
}}

.section {{
    margin-top: 30px;
}}

.skills {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}

.skill {{
    display: inline-block;
    background: #e5e7eb;
    padding: 7px 10px;
    border-radius: 15px;
    margin: 3px;
}}

.missing {{
    background: #fee2e2;
}}

.matched {{
    background: #dcfce7;
}}

li {{
    margin-bottom: 10px;
}}

.print-button {{
    padding: 10px 18px;
    border: none;
    background: #2563eb;
    color: white;
    border-radius: 7px;
    cursor: pointer;
    margin-bottom: 30px;
}}

@media print {{
    .print-button {{
        display: none;
    }}
}}

</style>

</head>

<body>


<button
    class="print-button"
    onclick="window.print()"
>
    Print / Save as PDF
</button>


<h1>
Smart Resume Analyzer Report
</h1>


<div class="subtitle">

Resume:
{html.escape(str(analysis.get("filename", "Unknown")))}

<br>

Target Role:
{html.escape(str(analysis.get("job_role", "Unknown")))}

<br>

Analyzed:
{html.escape(str(analysis.get("created_at", "")))}

</div>


<div class="scores">


<div class="score">

<p>
Resume Score
</p>

<h2>
{resume_score}/100
</h2>

</div>


<div class="score">

<p>
ATS Score
</p>

<h2>
{ats_score}/100
</h2>

</div>


<div class="score">

<p>
Job Match
</p>

<h2>
{job_score}%
</h2>

</div>


</div>


<div class="section">

<h2>
Detected Skills
</h2>

<div class="skills">

{
"".join(
    f'<span class="skill">{html.escape(str(skill))}</span>'
    for skill in found_skills
)
}

</div>

</div>


<div class="section">

<h2>
Missing Role Skills
</h2>

<div class="skills">

{
"".join(
    f'<span class="skill missing">{html.escape(str(skill))}</span>'
    for skill in missing_skills
)
}

</div>

</div>


<div class="section">

<h2>
Job Description — Matched Skills
</h2>

<div class="skills">

{
"".join(
    f'<span class="skill matched">{html.escape(str(skill))}</span>'
    for skill in job_matched_skills
)
}

</div>

</div>


<div class="section">

<h2>
Job Description — Missing Skills
</h2>

<div class="skills">

{
"".join(
    f'<span class="skill missing">{html.escape(str(skill))}</span>'
    for skill in job_missing_skills
)
}

</div>

</div>


<div class="section">

<h2>
Improvement Recommendations
</h2>

<ul>

{
"".join(
    f'<li>{html.escape(str(item))}</li>'
    for item in feedback
)
}

</ul>

</div>


</body>

</html>
"""

    response = make_response(
        html
    )

    response.headers[
        "Content-Type"
    ] = "text/html; charset=utf-8"

    return response


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "index.html",
        roles=load_roles(),
        error=(
            "File is too large. "
            "Maximum allowed size is 10 MB."
        )
    ), 413


# =========================================================
# PAGE NOT FOUND
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return redirect(
        url_for("index")
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )