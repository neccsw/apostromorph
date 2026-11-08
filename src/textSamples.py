from pathlib import Path

SAMPLE_FOLDER = Path(__file__).resolve().parent.parent / 'test_data'

class SampleLoadError(ValueError):
    pass


def list_files():
    try:
        filenames = []
        for path in SAMPLE_FOLDER.glob('*.txt'):
            if path.is_file():
                filenames.append(path.name)
        return sorted(filenames)
    except OSError:
        return []


def load_text(filename):
    if not isinstance(filename, str) or filename not in list_files():
        raise SampleLoadError("Unknown sample file")
    path = SAMPLE_FOLDER / filename
    if path.resolve().parent != SAMPLE_FOLDER.resolve():
        raise SampleLoadError("Sample must be inside the sample folder")
    try:
        return path.read_text(encoding = 'utf-8')
    except (OSError, UnicodeError) as exception:
        raise SampleLoadError("Cannot read sample text") from exception
