import re


def improve_bullet_point(
    original_text,
    job_role="",
    focus="impact"
):
    """
    Improve a resume bullet point without
    inventing achievements or metrics.
    """

    text = re.sub(
        r"\s+",
        " ",
        original_text.strip()
    )

    if not text:
        return {
            "original": original_text,
            "improved": "",
            "changes": [],
            "suggestions": []
        }

    improved = text
    changes = []

    replacements = {
        "worked on": "Contributed to",
        "helped with": "Collaborated on",
        "responsible for": "Managed",
        "made": "Developed",
        "created": "Built",
        "did": "Completed"
    }

    for old, new in replacements.items():
        if improved.lower().startswith(old):
            improved = (
                new
                + improved[len(old):]
            )

            changes.append(
                "Replaced a weak opening with "
                "a stronger action verb."
            )
            break

    if improved:
        improved = (
            improved[0].upper()
            + improved[1:]
        )

    if not improved.endswith((".", "!", "?")):
        improved += "."

    suggestions = []

    if focus == "impact":
        suggestions.append(
            "Add a measurable result, such as "
            "time saved or performance improved, "
            "if you have verified data."
        )

    elif focus == "technical":
        suggestions.append(
            "Mention the specific technologies, "
            "tools, frameworks, or algorithms used."
        )

    elif focus == "leadership":
        suggestions.append(
            "Describe your actual responsibilities, "
            "team contributions, or leadership."
        )

    elif focus == "concise":
        suggestions.append(
            "Remove unnecessary words and keep "
            "the bullet focused on one achievement."
        )

    if job_role:
        suggestions.append(
            f"Highlight skills relevant to {job_role} "
            "where they accurately describe your work."
        )

    suggestions.append(
        "Only include achievements and metrics "
        "that you can verify."
    )

    return {
        "original": original_text,
        "improved": improved,
        "changes": changes,
        "suggestions": suggestions
    }