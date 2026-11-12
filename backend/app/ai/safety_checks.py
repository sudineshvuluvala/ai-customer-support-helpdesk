import re

MAX_INPUT = 1500
MAX_OUTPUT = 2000

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")
_INJECTION = re.compile(r"ignore (all|any|previous|the above)|system prompt|you are now|disregard .*instructions", re.I)


def sanitize_for_provider(text):
    """Mask personal data and clip length before anything leaves the server."""
    text = (text or "")[:MAX_INPUT]
    text = _EMAIL.sub("[email]", text)
    text = _CARD.sub("[number]", text)
    text = _PHONE.sub("[phone]", text)
    return text.strip()


def looks_like_injection(text):
    return bool(_INJECTION.search(text or ""))


def validate_question(text):
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()[:MAX_INPUT]


def validate_output(text):
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text or len(text) > MAX_OUTPUT or text.upper().startswith("NO_ANSWER"):
        return None
    return text
