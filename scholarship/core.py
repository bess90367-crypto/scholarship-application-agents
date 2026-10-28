from decimal import Decimal, InvalidOperation


def identifier(value):
    """Identifiers must arrive as text; numeric coercion has already lost zeros."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError('identifier must be nonempty text; do not coerce numbers')
    return value.strip()


def course_key(name, term):
    """Preserve upper/lower and term distinctions; do not infer equivalence."""
    if not isinstance(name, str) or not name.strip() or not isinstance(term, str) or not term.strip():
        raise ValueError('course name and term required for mapping')
    return (name.strip(), term.strip())


def unique_mapping(rows):
    """Reject ambiguous duplicate mapping keys rather than silently overwrite."""
    result = {}
    for row in rows:
        key = course_key(row.get('name'), row.get('term'))
        if key in result:
            raise ValueError('duplicate course mapping key; review attempts/source rows')
        result[key] = row
    return result


def number(value, label):
    if value is None or isinstance(value, bool):
        raise ValueError(f'{label}: missing or invalid number')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f'{label}: invalid number') from exc
    if not result.is_finite():
        raise ValueError(f'{label}: non-finite number')
    return result


def evidence(item, label):
    if item.get('status') != 'confirmed':
        raise ValueError(f'{label}: evidence is not confirmed')
    source = item.get('source', {})
    if not source.get('document_id') or not isinstance(source.get('page'), int) or isinstance(source.get('page'), bool) or source['page'] < 1:
        raise ValueError(f'{label}: document_id and positive page required')
    if not source.get('locator'):
        raise ValueError(f'{label}: source locator required')


def score(document):
    if document.get('rules', {}).get('status') != 'confirmed' or not document.get('rules', {}).get('id'):
        raise ValueError('confirmed rules with stable id required')
    credits = Decimal(0)
    weighted = Decimal(0)
    seen = set()
    included = 0
    for row in document.get('courses', []):
        key = row.get('id')
        if not key or key in seen:
            raise ValueError('missing or duplicate course id')
        seen.add(key)
        if not isinstance(row.get('include'), bool):
            raise ValueError(f'{key}: inclusion decision missing')
        if not row['include']:
            if not row.get('exclusion_reason'):
                raise ValueError(f'{key}: exclusion reason required')
            continue
        evidence(row, key)
        credit = number(row.get('credits'), key + '.credits')
        grade = number(row.get('score'), key + '.score')
        if credit < 0 or not 0 <= grade <= 100:
            raise ValueError(f'{key}: credits/percentage score outside range')
        if credit == 0:
            continue
        credits += credit
        weighted += credit * grade
        included += 1
    if not credits:
        raise ValueError('no positive included credits')
    return {'rules_id': document['rules']['id'], 'included_courses': included,
            'credits': str(credits), 'weighted_points': str(weighted),
            'average': str(weighted / credits), 'rounding': 'unrounded Decimal; display rounding is separate'}


def validate_rank(rank):
    evidence(rank, 'rank')
    if not rank.get('scope') or not rank.get('period'):
        raise ValueError('rank scope and period required')
    position = number(rank.get('position'), 'position')
    population = number(rank.get('population'), 'population')
    if position != position.to_integral_value() or population != population.to_integral_value() or not 1 <= position <= population:
        raise ValueError('rank must be integer within population')
    return {'scope': rank['scope'], 'period': rank['period'],
            'position_fraction': str(position / population),
            'interpretation': 'position/population; not percentile or eligibility'}


def discrepancies(document):
    result = []
    for field in document.get('comparisons', []):
        if field.get('application_value') != field.get('transcript_value'):
            result.append(field)
    return result
