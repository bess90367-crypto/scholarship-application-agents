"""Preserve source application numbers; sort independently within each table."""
import unicodedata


def ordered_applications(records):
    def key(row):
        status = row.get('number_status')
        raw = row.get('application_number')
        if status == 'blank' and (raw is None or not str(raw).strip()):
            return (1, 0)
        if status != 'confirmed' or raw is None:
            raise ValueError('Application number has not been verified')
        number = unicodedata.normalize('NFKC', str(raw)).strip()
        if not number.isdecimal():
            raise ValueError('Unsupported application number requires review')
        return (0, int(number))
    return sorted(records, key=key)
