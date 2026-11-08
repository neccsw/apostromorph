from src import morphEval

APOSTROPHES = "'’ʼ"
IOTATED = "яюєї"
CONSONANTS = "бвгґджзклмнпрстфхцчшщ"
ROOT_CONSONANTS = "бпвмфргґкхжчш"
PREFIXES = {
    "без", "від", "з", "із", "об", "під", "роз", "між", "над", "перед",
    "понад", "через", "ад", "ін", "кон", "диз", "дез", "пан", "напів",
    "дит", "мін", "двох", "трьох", "чотирьох",
}

NO_APOSTROPHE_LEMMAS = {
    "дзвякнути", "духмяний", "мавпячий", "медвяний", "морквяний", "різдвяний",
    "свято", "святий", "тьмяний", "цвях", "буряк", "буряний", "крякати",
    "рябий", "рябити", "рюмсати", "крюк", "бязь", "бюджет", "бюро", "кювет",
    "мюрид", "пюпітр", "пюре", "фюзеляж", "рюкзак", "рюш", "барбюс",
    "бюффон", "вюртемберг", "мюллер", "гюго",
}

MISSING_APOSTROPHE_LEMMAS = {
    "зєднання": "з'єднання", "зявитися": "з'явитися", "обєкт": "об'єкт",
    "звязок": "зв'язок", "розвязати": "розв'язати",
}


def dictionary_lemmas(word, evidence):
    normalized = morphEval.normalize_word(word)
    if normalized not in evidence:
        evidence[normalized] = morphEval.dictionary_lemmas(normalized)
    return evidence[normalized]


def apostrophe_error(word, evidence):
    normalized = morphEval.normalize_word(word)
    for index, char in enumerate(normalized):
        if char != "'":
            continue
        before = normalized[:index]
        after = normalized[index + 1:]
        if before in {"о", "д"} and after and after[0].isalpha():
            if word[index + 1].isupper() or dictionary_lemmas(word, evidence):
                continue
        if not after or after[0] not in IOTATED:
            return "before_iotated"
        if not before or before[-1] not in CONSONANTS:
            return "after_consonant"
        if before[-1] not in ROOT_CONSONANTS and before not in PREFIXES:
            if dictionary_lemmas(word, evidence) == set():
                return "boundary"

    plain = normalized.replace("'", "")
    if plain in NO_APOSTROPHE_LEMMAS:
        return "unnecessary"
    plain_lemmas = dictionary_lemmas(plain, evidence)
    if plain_lemmas:
        for lemma in plain_lemmas:
            if lemma in NO_APOSTROPHE_LEMMAS:
                return "unnecessary"
    original_lemmas = dictionary_lemmas(normalized, evidence)
    if original_lemmas == set() and plain_lemmas:
        return "unnecessary"
    return None


def check_component(word, evidence):
    normalized = morphEval.normalize_word(word)
    positions = []
    for index, char in enumerate(normalized):
        if char == "'":
            positions.append(index)

    if positions:
        code = apostrophe_error(word, evidence)
        if code:
            candidates = []
            for index in positions:
                candidate = word[:index] + word[index + 1:]
                candidates.append(candidate)
            plain = ""
            for char in word:
                if char not in APOSTROPHES:
                    plain += char
            candidates.append(plain)

            suggestions = []
            for candidate in candidates:
                candidate_lemmas = dictionary_lemmas(candidate, evidence)
                if not candidate_lemmas:
                    continue
                incorrect_entry = False
                for lemma in candidate_lemmas:
                    if lemma in MISSING_APOSTROPHE_LEMMAS:
                        incorrect_entry = True
                        break
                if incorrect_entry:
                    continue
                has_apostrophe = False
                for char in candidate:
                    if char in APOSTROPHES:
                        has_apostrophe = True
                        break
                if has_apostrophe and apostrophe_error(candidate, evidence):
                    continue
                if candidate not in suggestions:
                    suggestions.append(candidate)
            return {"code": code, "suggestions": suggestions}

    insertion_positions = []
    for index in range(1, len(word)):
        if normalized[index - 1] in CONSONANTS and normalized[index] in IOTATED:
            insertion_positions.append(index)
    if not insertion_positions:
        return None
    lemmas = dictionary_lemmas(word, evidence)
    if lemmas is None:
        return None
    required = set()
    for lemma in lemmas:
        if lemma in MISSING_APOSTROPHE_LEMMAS:
            required.add(MISSING_APOSTROPHE_LEMMAS[lemma])
    if lemmas and not required:
        return None

    suggestions = []
    apostrophe = "ʼ"
    for char in word:
        if char in APOSTROPHES:
            apostrophe = char
            break
    for index in insertion_positions:
        candidate = word[:index] + apostrophe + word[index:]
        candidate_lemmas = dictionary_lemmas(candidate, evidence)
        if not candidate_lemmas:
            continue
        if required:
            matches_required = False
            for lemma in candidate_lemmas:
                if lemma in required:
                    matches_required = True
                    break
            if not matches_required:
                continue
        if not apostrophe_error(candidate, evidence):
            suggestions.append(candidate)
    if suggestions:
        return {"code": "missing", "suggestions": suggestions}
    return None


def check_word(word, evidence = None):
    if evidence is None:
        evidence = {}
    components = word.split("-")
    codes = []
    choices = []
    can_suggest = True
    for component in components:
        check = check_component(component, evidence)
        if check:
            if check["code"] not in codes:
                codes.append(check["code"])
            choices.append(check["suggestions"])
            if not check["suggestions"]:
                can_suggest = False
        else:
            choices.append([component])
    if not codes:
        return None

    suggestions = []
    if can_suggest:
        combinations = [[]]
        for component_choices in choices:
            next_combinations = []
            for combination in combinations:
                for choice in component_choices:
                    next_combinations.append(combination + [choice])
                    if len(next_combinations) == 5:
                        break
                if len(next_combinations) == 5:
                    break
            combinations = next_combinations
        for combination in combinations:
            suggestions.append("-".join(combination))

    if len(codes) == 1:
        code = codes[0]
    else:
        code = "multiple"
    return {"code": code, "suggestions": suggestions}
