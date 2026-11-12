"""Evidence-backed Word summary values and batch-scoped application checks."""
from decimal import Decimal, ROUND_HALF_UP


YEAR_NUMERALS = {
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
}


def score_text(value):
    if value is None or value == "" or value == "--":
        raise ValueError("Missing score is not zero")
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError("Score must be finite")
    return str(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def authoritative_word_score(spreadsheet_value=None, independent_value=None):
    """Return a verified score for Word; application-form self reports are never inputs."""
    if spreadsheet_value in (None, "", "--") and independent_value in (None, "", "--"):
        raise ValueError("No verified score source")
    if spreadsheet_value not in (None, "", "--") and independent_value not in (None, "", "--"):
        sheet = score_text(spreadsheet_value)
        independent = score_text(independent_value)
        if sheet != independent:
            raise ValueError("Spreadsheet and independent calculation conflict")
        return independent
    if independent_value not in (None, "", "--"):
        return score_text(independent_value)
    return score_text(spreadsheet_value)


def mixed_average(required, previous_year):
    score_text(required)
    score_text(previous_year)
    return score_text((Decimal(str(required)) + Decimal(str(previous_year))) / 2)


def previous_year_cell(year_level):
    if isinstance(year_level, bool) or year_level not in range(2, 8):
        raise ValueError("Unresolved year level")
    return f"M{year_level + 6}"


def derive_year_level(enrollment_academic_year, target_academic_year):
    """Derive study year from ROC academic-year enrollment and target academic year."""
    if isinstance(enrollment_academic_year, bool) or isinstance(target_academic_year, bool):
        raise ValueError("Academic years must be integers")
    if not isinstance(enrollment_academic_year, int) or not isinstance(target_academic_year, int):
        raise ValueError("Academic years must be integers")
    level = target_academic_year - enrollment_academic_year + 1
    if level not in YEAR_NUMERALS:
        raise ValueError("Derived year level is out of supported range")
    return level


def suggested_year_label(program, enrollment_academic_year, target_academic_year):
    level = derive_year_level(enrollment_academic_year, target_academic_year)
    if program == "碩士班":
        prefix = "碩"
    elif program == "博士班":
        prefix = "博"
    elif program == "大學部":
        prefix = ""
    else:
        raise ValueError("Unsupported program")
    return f"{prefix}{YEAR_NUMERALS[level]}" if prefix else f"{YEAR_NUMERALS[level]}年級"


def year_resolution_options(program, enrollment_academic_year, target_academic_year, source_label=None):
    """Return the enrollment-derived suggestion plus source label when they conflict."""
    suggested = suggested_year_label(program, enrollment_academic_year, target_academic_year)
    if source_label in (None, "", suggested):
        return {"suggested": suggested, "conflict": False, "options": [suggested]}
    return {
        "suggested": suggested,
        "conflict": True,
        "options": [suggested, str(source_label)],
    }


def no_other_award(student_id, records, complete=False, unresolved=False):
    """True/False/None within the explicitly reviewed application batch only."""
    if not student_id or unresolved:
        return None
    matching = [r for r in records if r.get("student_id") == student_id]
    awards = {r.get("scholarship") for r in matching if r.get("scholarship")}
    if len(awards) > 1:
        return False
    if not complete or not matching or any(not r.get("scholarship") for r in matching):
        return None
    return True
