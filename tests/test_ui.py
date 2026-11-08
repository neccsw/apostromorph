from src import textEval
from src.UIgradio import format_result, handle_analyze


def test_tables_and_highlights():
    text = '<script>😀</script> мʼясо, мяч!'
    result = textEval.analyze_text(text, False)
    message, rows, spans, issue_count, issue_rows = format_result(result)
    assert message == 'Знайдено слів: 1'
    assert rows == [['мʼясо', '', '', '', 'Вимкнено']]
    assert issue_count == 'Помилок апострофа: 1'
    reason = 'Пропущено апостроф: словник і правила підтверджують наведене написання.'
    assert issue_rows == [['мяч', reason, 'мʼяч']]
    reconstructed_text = ''
    highlighted_spans = []
    for part, label in spans:
        reconstructed_text += part
        if label is not None:
            highlighted_spans.append((part, label))
    assert reconstructed_text == text
    assert highlighted_spans == [('мʼясо', 'Знайдене слово'), ('мяч', 'Помилка апострофа')]


def test_empty_input_error():
    message, rows, spans, issue_count, issue_rows = handle_analyze('', True)
    assert message == 'Введіть текст для аналізу.'
    assert rows == []
    assert spans == []
    assert issue_count == 'Помилок апострофа: 0'
    assert issue_rows == []
