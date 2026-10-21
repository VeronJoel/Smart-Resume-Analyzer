import json
import os
import sqlite3
from datetime import datetime


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE_PATH = os.path.join(
    DATA_DIR,
    "resume_analyzer.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():
    """
    Create the database table if required.

    Also upgrades older versions of the database
    by adding newly required columns.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # CREATE TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL,

            job_role TEXT NOT NULL,

            resume_score REAL DEFAULT 0,

            ats_score REAL DEFAULT 0,

            job_description_score REAL DEFAULT 0,

            found_skills TEXT DEFAULT '[]',

            missing_skills TEXT DEFAULT '[]',

            job_matched_skills TEXT DEFAULT '[]',

            job_missing_skills TEXT DEFAULT '[]',

            feedback TEXT DEFAULT '[]',

            created_at TIMESTAMP NOT NULL

        )
        """
    )

    connection.commit()


    # -----------------------------------------------------
    # CHECK EXISTING COLUMNS
    # -----------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(analyses)"
    )

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }


    # -----------------------------------------------------
    # ADD MISSING COLUMNS
    # -----------------------------------------------------

    new_columns = {

        "job_description_score":
            "REAL DEFAULT 0",

        "job_matched_skills":
            "TEXT DEFAULT '[]'",

        "job_missing_skills":
            "TEXT DEFAULT '[]'"

    }


    for column_name, column_definition in new_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"""
                ALTER TABLE analyses
                ADD COLUMN {column_name}
                {column_definition}
                """
            )


    # -----------------------------------------------------
    # FIX OLD NULL CREATED_AT VALUES
    # -----------------------------------------------------

    cursor.execute(
        """
        UPDATE analyses

        SET created_at = ?

        WHERE created_at IS NULL
        """,

        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
    )


    connection.commit()

    connection.close()


# =========================================================
# SAVE ANALYSIS
# =========================================================

def save_analysis(
    filename,
    job_role,
    resume_score,
    ats_score,
    found_skills,
    missing_skills,
    feedback,
    job_description_score=0,
    job_matched_skills=None,
    job_missing_skills=None
):
    """
    Save a new resume analysis.
    """

    if job_matched_skills is None:

        job_matched_skills = []


    if job_missing_skills is None:

        job_missing_skills = []


    # -----------------------------------------------------
    # MAKE SURE DATABASE IS READY
    # -----------------------------------------------------

    init_database()


    connection = get_connection()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # CURRENT DATE/TIME
    # -----------------------------------------------------

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # -----------------------------------------------------
    # INSERT ANALYSIS
    # -----------------------------------------------------

    cursor.execute(
        """
        INSERT INTO analyses (

            filename,

            job_role,

            resume_score,

            ats_score,

            job_description_score,

            found_skills,

            missing_skills,

            job_matched_skills,

            job_missing_skills,

            feedback,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (

            filename,

            job_role,

            resume_score,

            ats_score,

            job_description_score,

            json.dumps(
                found_skills or []
            ),

            json.dumps(
                missing_skills or []
            ),

            json.dumps(
                job_matched_skills or []
            ),

            json.dumps(
                job_missing_skills or []
            ),

            json.dumps(
                feedback or []
            ),

            created_at

        )
    )


    analysis_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return analysis_id


# =========================================================
# CONVERT DATABASE ROW
# =========================================================

def _convert_analysis(row):
    """
    Convert a SQLite Row into a normal Python dictionary.
    """

    if row is None:

        return None


    data = dict(row)


    json_fields = [

        "found_skills",

        "missing_skills",

        "job_matched_skills",

        "job_missing_skills",

        "feedback"

    ]


    for field in json_fields:

        value = data.get(
            field
        )


        if not value:

            data[field] = []

            continue


        try:

            data[field] = json.loads(
                value
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            data[field] = []


    return data


# =========================================================
# GET ALL ANALYSES
# =========================================================

def get_all_analyses():
    """
    Return all saved analyses.
    Newest analyses appear first.
    """

    init_database()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM analyses

        ORDER BY created_at DESC
        """
    )


    rows = cursor.fetchall()


    connection.close()


    return [

        _convert_analysis(row)

        for row in rows

    ]


# =========================================================
# GET SINGLE ANALYSIS
# =========================================================

def get_analysis(analysis_id):
    """
    Return one analysis by its ID.
    """

    init_database()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM analyses

        WHERE id = ?
        """,

        (
            analysis_id,
        )
    )


    row = cursor.fetchone()


    connection.close()


    return _convert_analysis(
        row
    )


# =========================================================
# DELETE ANALYSIS
# =========================================================

def delete_analysis(analysis_id):
    """
    Delete an analysis.
    """

    init_database()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM analyses

        WHERE id = ?
        """,

        (
            analysis_id,
        )
    )


    connection.commit()

    connection.close()


# =========================================================
# STATISTICS
# =========================================================

def get_statistics():
    """
    Return overall analysis statistics.
    """

    init_database()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

            COUNT(*) AS total_analyses,

            COALESCE(
                MAX(resume_score),
                0
            ) AS best_resume_score,

            COALESCE(
                MAX(ats_score),
                0
            ) AS best_ats_score,

            COALESCE(
                AVG(resume_score),
                0
            ) AS average_resume_score,

            COALESCE(
                AVG(ats_score),
                0
            ) AS average_ats_score,

            COALESCE(
                MAX(job_description_score),
                0
            ) AS best_job_description_score,

            COALESCE(
                AVG(job_description_score),
                0
            ) AS average_job_description_score

        FROM analyses
        """
    )


    row = cursor.fetchone()


    connection.close()


    if not row:

        return {

            "total_analyses": 0,

            "best_resume_score": 0,

            "best_ats_score": 0,

            "average_resume_score": 0,

            "average_ats_score": 0,

            "best_job_description_score": 0,

            "average_job_description_score": 0

        }


    return {

        "total_analyses":
            row["total_analyses"],

        "best_resume_score":
            round(
                row["best_resume_score"],
                1
            ),

        "best_ats_score":
            round(
                row["best_ats_score"],
                1
            ),

        "average_resume_score":
            round(
                row["average_resume_score"],
                1
            ),

        "average_ats_score":
            round(
                row["average_ats_score"],
                1
            ),

        "best_job_description_score":
            round(
                row["best_job_description_score"],
                1
            ),

        "average_job_description_score":
            round(
                row["average_job_description_score"],
                1
            )

    }