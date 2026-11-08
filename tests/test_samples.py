import json
from pathlib import Path

import pytest

from src import textEval
from src import textSamples
from src.UIgradio import load_sample

EXPECTED_PATH = Path(__file__).parent / 'data' / 'expected_words.json'
EXPECTED = json.loads(EXPECTED_PATH.read_text(encoding = 'utf-8'))
SAMPLES = textSamples.list_files()
if not SAMPLES:
    raise pytest.UsageError('test_data must contain at least one .txt sample')
missing = []
for filename in SAMPLES:
    if filename not in EXPECTED:
        missing.append(filename)
if missing:
    raise pytest.UsageError(f'Missing reviewed expectations for: {sorted(missing)}')


def test_sample_word_order():
    for filename in SAMPLES:
        text = textSamples.load_text(filename)
        result = textEval.analyze_text(text, False)
        found_words = []
        for word in result['words']:
            found_words.append(word['word'])
        assert found_words == EXPECTED[filename], filename
        assert result['count'] == len(EXPECTED[filename]), filename


def test_load_clears_results_outside_project_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    text, message, rows, spans, issue_count, issue_rows = load_sample('text_01.txt')
    assert text == textSamples.load_text('text_01.txt')
    assert text.startswith('На подвір')
    assert message == 'Знайдено слів: 0'
    assert rows == []
    assert spans == []
    assert issue_count == 'Помилок апострофа: 0'
    assert issue_rows == []


def test_missing_sample_preserves_ui(tmp_path, monkeypatch):
    warnings = []
    monkeypatch.setattr(textSamples, 'SAMPLE_FOLDER', tmp_path)
    monkeypatch.setattr('src.UIgradio.gr.Warning', warnings.append)
    updates = load_sample('missing.txt')
    assert len(updates) == 6
    for update in updates:
        assert update == {'__type__': 'update'}
    assert warnings == ['Не вдалося завантажити тестовий текст. Перевірте файл і кодування UTF-8.']
