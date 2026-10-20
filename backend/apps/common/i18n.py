"""The site's two languages, and reading per-language fields off a record.

Translated content is stored as sibling columns (`title_fa`, `title_en`), so
every API answer picks one side by the `?language=` query parameter.
"""
from rest_framework.exceptions import ValidationError

LANGUAGES = ("fa", "en")
DEFAULT_LANGUAGE = "fa"


def get_language(request):
    """The `?language=` of an API request, `fa` when absent; 400 when unknown."""
    lang = request.query_params.get("language", DEFAULT_LANGUAGE)
    if lang not in LANGUAGES:
        raise ValidationError({"language": "Must be 'fa' or 'en'."})
    return lang


def pick(obj, base, lang):
    """`obj.<base>_<lang>`, or "" when it is blank or missing."""
    return getattr(obj, f"{base}_{lang}", "") or ""
