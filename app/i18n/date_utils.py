from datetime import datetime


DATE_FORMATS = {
    "pt": "%d/%m/%Y",
    "en": "%Y-%m-%d",
}

ISO_FORMAT = "%Y-%m-%d"
DICOM_FORMAT = "%Y%m%d"


def display_format_for_language(language):
    return DATE_FORMATS.get(language, DATE_FORMATS["en"])


def display_mask_for_language(language):
    return datetime(2001, 12, 31).strftime(display_format_for_language(language))


def parse_user_date(value, language):
    value = (value or "").strip()
    if not value:
        return None
    parsed = datetime.strptime(value, display_format_for_language(language))
    return parsed.strftime(ISO_FORMAT)


def format_iso_date(value, language):
    value = (value or "").strip()
    if not value:
        return ""
    parsed = datetime.strptime(value, ISO_FORMAT)
    return parsed.strftime(display_format_for_language(language))


def format_dicom_date(value, language):
    value = (value or "").strip()
    if len(value) != 8 or not value.isdigit():
        return value
    parsed = datetime.strptime(value, DICOM_FORMAT)
    return parsed.strftime(display_format_for_language(language))
