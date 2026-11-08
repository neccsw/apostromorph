import logging
import unicodedata

from pymorphy3 import MorphAnalyzer

logger = logging.getLogger(__name__)
parser = None
FEATURES = (
    "gender", "number", "case", "tense", "person", "aspect", "mood",
    "voice", "animacy", "transitivity",
)


def get_parser():
    global parser
    if parser is None:
        parser = MorphAnalyzer(lang = "uk")
    return parser


def normalize_word(word):
    normalized = unicodedata.normalize("NFC", word)
    normalized = normalized.lower()
    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("ʼ", "'")
    return normalized


def dictionary_lemmas(word):
    normalized = normalize_word(word)
    try:
        analyzer = get_parser()
        if not analyzer.word_is_known(normalized, strict = True):
            return set()
        lemmas = set()
        for parsed in analyzer.parse(normalized):
            if parsed.is_known:
                lemmas.add(parsed.normal_form)
        return lemmas
    except Exception:
        logger.exception("Apostrophe dictionary lookup failed")
        return None


def analyze_word(word):
    normalized = normalize_word(word)
    result = {"status": "unknown", "lemma": None, "part_of_speech": None, "features": {}}
    try:
        analyzer = get_parser()
        parses = analyzer.parse(normalized)
        if parses and parses[0].tag.POS is not None:
            parsed = parses[0]
            if parsed.is_known:
                status = "dictionary"
            else:
                status = "predicted"
            features = {}
            for name in FEATURES:
                features[name] = getattr(parsed.tag, name, None)
            result = {
                "status": status,
                "lemma": parsed.normal_form,
                "part_of_speech": parsed.tag.POS,
                "features": features,
            }
    except Exception:
        logger.exception("Morphological analysis failed")
        result["status"] = "error"
    return result
