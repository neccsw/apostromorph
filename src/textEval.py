import re

from src import morphEval, apostropheEval
from src.apostropheEval import APOSTROPHES

LETTERS = "А-ЩЬЮЯЄІЇҐа-щьюяєіїґ"
TOKEN = re.compile(r"[\w'’ʼ-]+")
WORD = re.compile(rf"[{LETTERS}]+(?:['’ʼ-][{LETTERS}]+)*")
MAX_TEXT_LENGTH = 10_000

class TextValidationError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def scan_words(text):
    matches = []
    issues = []
    evidence = {}
    for token in TOKEN.finditer(text):
        raw = token.group()
        word = raw.strip(APOSTROPHES)
        if not WORD.fullmatch(word):
            continue

        leading_quotes = len(raw) - len(raw.lstrip(APOSTROPHES))
        start = token.start() + leading_quotes
        occurrence = {"word": word, "start": start, "end": start + len(word)}
        issue = apostropheEval.check_word(word, evidence)
        if issue:
            occurrence["code"] = issue["code"]
            occurrence["suggestions"] = issue["suggestions"]
            issues.append(occurrence)
        else:
            for char in word:
                if char in APOSTROPHES:
                    matches.append(occurrence)
                    break
    return {"words": matches, "issues": issues}


def find_apostrophe_words(text):
    result = scan_words(text)
    return result["words"]


def analyze_text(text, include_morphology = True):
    if not isinstance(text, str) or not text.strip():
        raise TextValidationError("empty", "Введіть текст для аналізу.")
    if len(text) > MAX_TEXT_LENGTH:
        raise TextValidationError("too_long", "Текст має містити не більше 10 000 символів.")

    scanned = scan_words(text)
    words = scanned["words"]
    for word in words:
        if include_morphology:
            word["morphology"] = morphEval.analyze_word(word["word"])
        else:
            word["morphology"] = None
    return {
        "source_text": text,
        "count": len(words),
        "words": words,
        "issues": scanned["issues"],
    }
