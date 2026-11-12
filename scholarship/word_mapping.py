"""Evidence-backed Word summary values and batch-scoped application checks."""
from decimal import Decimal, ROUND_HALF_UP


def score_text(value):
    if value is None or value == "" or value == "--":
        raise ValueError("Missing score is not zero")
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError("Score must be finite")
    return str(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def mixed_average(required, previous_year):
    score_text(required)
    score_text(previous_year)
    return score_text((Decimal(str(required)) + Decimal(str(previous_year))) / 2)


def previous_year_cell(year_level):
    if isinstance(year_level, bool) or year_level not in range(2, 8):
        raise ValueError("Unresolved year level")
    return f"M{year_level + 6}"


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
