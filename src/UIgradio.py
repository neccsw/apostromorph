import gradio as gr

from src import textEval, textSamples
from src.textEval import TextValidationError
from src.textSamples import SampleLoadError

POS = {
    "NOUN": "Іменник", "ADJF": "Прикметник", "ADJS": "Короткий прикметник",
    "COMP": "Вищий ступінь", "VERB": "Дієслово", "INFN": "Інфінітив",
    "PRTF": "Дієприкметник", "PRTS": "Короткий дієприкметник",
    "GRND": "Дієприслівник", "NUMR": "Числівник", "ADVB": "Прислівник",
    "NPRO": "Займенник", "PRED": "Предикатив", "PREP": "Прийменник",
    "CONJ": "Сполучник", "PRCL": "Частка", "INTJ": "Вигук",
}
FEATURE_NAMES = {
    "gender": "Рід", "number": "Число", "case": "Відмінок", "tense": "Час",
    "person": "Особа", "aspect": "Вид", "mood": "Спосіб", "voice": "Стан",
    "animacy": "Істотність", "transitivity": "Перехідність",
}
VALUES = {
    "masc": "чоловічий", "femn": "жіночий", "neut": "середній",
    "ms-f": "спільний", "sing": "однина", "plur": "множина",
    "nomn": "називний", "gent": "родовий", "datv": "давальний",
    "accs": "знахідний", "ablt": "орудний", "loct": "місцевий",
    "voct": "кличний", "gen1": "родовий", "gen2": "другий родовий",
    "acc2": "другий знахідний", "loc1": "місцевий", "loc2": "другий місцевий",
    "pres": "теперішній", "past": "минулий", "futr": "майбутній",
    "1per": "перша", "2per": "друга", "3per": "третя",
    "perf": "доконаний", "impf": "недоконаний", "indc": "дійсний",
    "impr": "наказовий", "actv": "активний", "pssv": "пасивний",
    "anim": "істота", "inan": "неістота", "tran": "перехідне", "intr": "неперехідне",
}
STATUSES = {
    "dictionary": "Зі словника", "predicted": "Прогноз", "unknown": "Невідомо",
    "error": "Помилка аналізу",
}
ISSUE_REASONS = {
    "before_iotated": "У звичайних словах апостроф пишемо лише перед я, ю, є, ї.",
    "after_consonant": "Перед я, ю, є, ї апостроф відокремлює попередній твердий приголосний, а не голосний, й чи ь.",
    "boundary": "Тут апостроф не підтверджений правилами для кореня, префікса чи складного слова.",
    "unnecessary": "У цьому слові апостроф зайвий: нормативне написання не потребує роздільної вимови.",
    "missing": "Пропущено апостроф: словник і правила підтверджують наведене написання.",
    "multiple": "У частинах складного слова виявлено кілька різних помилок вживання апострофа.",
}


def get_occurrence_start(item):
    occurrence, label = item
    return occurrence["start"]


def format_result(result):
    rows = []
    issue_rows = []
    spans = []
    for match in result["words"]:
        morphology = match["morphology"]
        lemma = ""
        part_of_speech = ""
        features = ""
        status = "Вимкнено"
        if morphology:
            if morphology["lemma"]:
                lemma = morphology["lemma"]
            part_of_speech = POS.get(morphology["part_of_speech"], "")
            feature_parts = []
            for key, value in morphology["features"].items():
                if value is not None:
                    feature_name = FEATURE_NAMES[key]
                    feature_value = VALUES.get(value, "невідомо")
                    feature_parts.append(f"{feature_name}: {feature_value}")
            features = "; ".join(feature_parts)
            status = STATUSES[morphology["status"]]
        rows.append([match["word"], lemma, part_of_speech, features, status])
    issues = result.get("issues", [])
    for issue in issues:
        issue_rows.append([
            issue["word"], ISSUE_REASONS[issue["code"]],
            "; ".join(issue["suggestions"]),
        ])
    occurrences = []
    for match in result["words"]:
        occurrences.append((match, "Знайдене слово"))
    for issue in issues:
        occurrences.append((issue, "Помилка апострофа"))
    occurrences.sort(key = get_occurrence_start)
    source_text = result["source_text"]
    cursor = 0
    for occurrence, label in occurrences:
        if occurrence["start"] > cursor:
            spans.append((source_text[cursor:occurrence["start"]], None))
        spans.append((occurrence["word"], label))
        cursor = occurrence["end"]
    if cursor < len(source_text):
        spans.append((source_text[cursor:], None))
    message = f"Знайдено слів: {result['count']}"
    if not result['words']:
        message += ". Слів з апострофом не знайдено."
    issue_count = f"Помилок апострофа: {len(issues)}"
    if not issues:
        issue_count += ". Підтверджених помилок не знайдено."
    return message, rows, spans, issue_count, issue_rows


def handle_analyze(text, include_morphology):
    try:
        result = textEval.analyze_text(text, include_morphology)
    except TextValidationError as error:
        return str(error), [], [], "Помилок апострофа: 0", []
    return format_result(result)


def load_sample(filename):
    if filename is None:
        return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
    try:
        text = textSamples.load_text(filename)
    except SampleLoadError:
        gr.Warning("Не вдалося завантажити тестовий текст. Перевірте файл і кодування UTF-8.")
        return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
    return text, "Знайдено слів: 0", [], [], "Помилок апострофа: 0", []


def create_ui():
    with gr.Blocks(title = "ApostroMorph UA", analytics_enabled = False) as app:
        gr.Markdown("# ApostroMorph UA\nАналіз українських слів з апострофом")
        sample_input = gr.Dropdown(
            choices = textSamples.list_files(), value = None,
            label = "Тестовий текст", allow_custom_value = False, interactive = True
        )
        text_input = gr.Textbox(
            label = "Текст", lines = 7,
            placeholder = "На подвір’ї з’явився бур’ян."
        )
        morphology_checkbox = gr.Checkbox(label = "Виконати морфологічний аналіз", value = True)
        gr.Markdown("Підтримуються апострофи ' ’ ʼ. Максимум — 10 000 символів. Перевірка апострофів працює і без морфологічного аналізу. Помилки позначено червоним; виправлення подано як підказки без зміни тексту. Неоднозначні пропуски апострофів не позначаються. «Прогноз» — припущення для слова поза словником без урахування контексту речення.")
        btn_analyze = gr.Button("Аналізувати", variant = "primary")
        count_output = gr.Markdown("Знайдено слів: 0")
        results_table = gr.Dataframe(
            headers = ["Слово", "Лема", "Частина мови", "Морфологічні ознаки", "Статус"],
            datatype = ["str"] * 5,
            interactive = False, label = "Результати", type = "array"
        )
        issue_count_output = gr.Markdown("Помилок апострофа: 0")
        issues_table = gr.Dataframe(
            headers = ["Слово", "Пояснення", "Варіанти виправлення"], datatype = ["str"] * 3,
            interactive = False, label = "Помилки вживання апострофа", type = "array",
            wrap = True, column_widths = ["18%", "54%", "28%"]
        )
        highlighted_text = gr.HighlightedText(
            label = "Знайдені слова в тексті", show_legend = True, show_inline_category = False,
            color_map = {"Знайдене слово": "#bfdbfe", "Помилка апострофа": "#fecaca"}
        )
        result_outputs = [
            count_output, results_table, highlighted_text, issue_count_output, issues_table
        ]
        btn_analyze.click(
            fn = handle_analyze, inputs = [text_input, morphology_checkbox],
            outputs = result_outputs, api_name = False,
            concurrency_id = "text_operations", concurrency_limit = 1
        )
        sample_input.input(
            fn = load_sample, inputs = sample_input,
            outputs = [text_input] + result_outputs, api_name = False,
            concurrency_id = "text_operations", concurrency_limit = 1
        )
    return app
