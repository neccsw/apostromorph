from src import textEval


def test_valid_apostrophes():
    words = ["зв'язок", "ін'єкція", "О'Коннор"]
    for word in words:
        result = textEval.analyze_text(word, False)
        assert result['count'] == 1, word
        first_word = result['words'][0]
        assert first_word['word'] == word, word
        assert result['issues'] == [], word


def test_placement_errors():
    cases = [
        ('вʼша', 'before_iotated'),
        ('аʼя', 'after_consonant'),
        ('нʼябв', 'boundary'),
    ]
    for word, code in cases:
        result = textEval.analyze_text(word, False)
        assert result['count'] == 0, word
        issues = result['issues']
        assert len(issues) == 1, word
        issue = issues[0]
        assert issue['code'] == code, word
        assert issue['suggestions'] == [], word


def test_corrections():
    cases = [
        ('свʼято', 'unnecessary', ['свято']),
        ('мяч', 'missing', ['мʼяч']),
        ('зєднанням', 'missing', ['зʼєднанням']),
        ('свʼято-мяч', 'multiple', ['свято-мʼяч']),
    ]
    for word, code, suggestions in cases:
        result = textEval.analyze_text(word, False)
        assert result['count'] == 0, word
        issues = result['issues']
        assert len(issues) == 1, word
        issue = issues[0]
        assert issue['code'] == code, word
        assert issue['suggestions'] == suggestions, word


def test_no_speculative_missing_apostrophes():
    for word in ['буря', 'пюре']:
        result = textEval.analyze_text(word, False)
        assert result['issues'] == [], word
