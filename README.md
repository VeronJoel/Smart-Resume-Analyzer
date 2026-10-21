# Smart Resume Analyzer

A Flask web application that reviews resume content, scores key sections, matches skills to a target role or job description, provides improvement suggestions, and stores analysis history in SQLite.

## Features
- PDF and DOCX resume text extraction
- Resume section scoring and completeness feedback
- Role-based ATS-style skill matching
- Optional job-description matching
- Analysis history and printable reports
- Rule-based resume bullet improvement assistant

## Local setup
1. Install Python 3.12.
2. Open a terminal in the project root.
3. Create and activate a virtual environment:
   - Windows: `python -m venv venv`
   - PowerShell: `venv\\Scripts\\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000`.

The application accepts PDF and DOCX files up to 10 MB. Resume scores are heuristic guidance and do not guarantee ATS compatibility or hiring outcomes.

## Project structure
- `app.py` — Flask routes and request handling
- `utils/` — scoring, ATS matching, extraction, feedback, database, and improvement logic
- `templates/` — HTML pages
- `static/css/style.css` — styles
- `data/roles.json` — role skill definitions
- `data/skill_aliases.json` — skill synonyms
- `uploads/` — local uploaded resumes
- `data/resume_analyzer.db` — local analysis database

## Privacy and deployment notes
Do not commit real resumes, environment secrets, the virtual environment, or the local database. For production deployment, use persistent storage for uploaded files and SQLite or move to a managed database. Consider adding authentication, upload retention controls, CSRF protection, and production security configuration before public release.
