import pytest

from src import textEval
from src import morphEval


def test_words_and_offsets():
    text = "😀 «бур'ян», бур’ян бурʼян м’ясо-молочний бур'ян"
    matches = textEval.find_apostrophe_words(text)
    found_words = []
    for match in matches:
        found_words.append(match["word"])
        start = match["start"]
        end = match["end"]
        assert text[start:end] == match["word"]
    assert found_words == ["бур'ян", 'бур’ян', 'бурʼян', 'м’ясо-молочний', "бур'ян"]
    first_match = matches[0]
    assert first_match["start"] == 3


def test_invalid_tokens():
    words = ["abcбур'ян", "бур''ян", "м'ясо--молочний"]
    for word in words:
        result = textEval.analyze_text(word, False)
        assert result['words'] == [], word
        assert result['issues'] == [], word


def test_dictionary_and_normalization():
    result = morphEval.analyze_word("бур'ян")
    assert result["status"] == 'dictionary'
    assert result["lemma"] == "бур'ян"
    assert result["part_of_speech"] == 'NOUN'
    assert morphEval.analyze_word('БУР’ЯН') == result
    assert morphEval.analyze_word('бурʼян') == result


def test_validation():
    cases = [('', 'empty'), ('а' * 10001, 'too_long')]
    for text, code in cases:
        with pytest.raises(textEval.TextValidationError) as error:
            textEval.analyze_text(text)
        assert error.value.code == code, code


def test_disabled_morphology_keeps_spelling_checks(monkeypatch):
    text = 'мʼясо мяч'
    enabled = textEval.analyze_text(text)
    def fail(word):
        pytest.fail('Morphology must not run when disabled')
    monkeypatch.setattr(morphEval, 'analyze_word', fail)
    disabled = textEval.analyze_text(text, False)
    assert disabled['count'] == enabled['count']
    assert disabled['count'] == 1
    assert disabled['issues'] == enabled['issues']
    enabled_word = enabled['words'][0]
    disabled_word = disabled['words'][0]
    assert enabled_word['morphology'] is not None
    assert disabled_word['word'] == enabled_word['word']
    assert disabled_word['morphology'] is None
