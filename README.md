# ApostroMorph UA

A Gradio application for checking Ukrainian apostrophes, finding words containing them, and optionally analyzing their morphology. It runs on your computer and provides a public share link. The interface is Ukrainian; documentation and code identifiers are English.

## Setup and launch

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from this repository:

```bash
uv run main.py
```

This command installs the project dependencies when needed and starts the application.

The project uses Python 3.14. On Apple Silicon, use native ARM Python. Virtual environments cannot be copied across architectures: recreate only the project's `.venv` if it contains an incompatible interpreter, then run `uv sync --locked`.

Controls, grammatical descriptions, statuses, validation messages, and sample texts are in Ukrainian.

Gradio prints a local URL and a public HTTPS share URL in the terminal and opens the app in your browser. It selects an available local port starting at 7860. Share the public URL so others can use the application over the Internet. Paste text, optionally disable morphology, and click **Аналізувати**.

Keep the application running and your computer connected to the Internet while using the public link; press **Ctrl+C** in the terminal to stop. The link is temporary and lasts up to one week, best effort; restarting creates a new link. See [Gradio's sharing guide](https://www.gradio.app/guides/sharing-your-app). Linguistic analysis runs on your computer using dictionaries installed with the dependencies. Gradio provides the sharing tunnel and manages its own server and internal web dependencies.

## Behavior

- Recognizes ASCII `'`, typographic `’`, and modifier `ʼ` apostrophes.
- Keeps duplicates, original spelling, source order, and character offsets.
- Includes complete compounds joined by ASCII hyphens, such as `м’ясо-молочний`.
- Requires Ukrainian letters around internal apostrophes and hyphens; rejects mixed scripts, digits, underscores, and doubled separators. Surrounding quotation marks are allowed.
- Accepts nonblank input up to 10,000 Python Unicode characters. No matches is a normal result.
- Shows a results table and highlights source spans using Gradio's native text component. Input markup is treated as text.
- Checks placement using [Ukrainian Orthography, §§7 and 138](https://www.ulif.org.ua/data/pravopus_ua_05.06/content.htm), including prefixes, loanwords, compounds, and foreign name particles. Blue highlights mark accepted apostrophe words; red highlights mark errors, which are excluded from the accepted-word count and morphology table.
- Shows a separate error count and **Слово / Пояснення / Варіанти виправлення** table. For example, `вʼша` has invalid placement and no guessed replacement, while `свʼято`, `пʼюре`, and `духмʼяного` suggest `свято`, `пюре`, and `духмяного`.
- Suggests missing apostrophes only when a single insertion per hyphenated component produces an exact dictionary match that passes placement checks: `мяч` → `мʼяч`, `зєднанням` → `зʼєднанням`. Words already valid as written remain unflagged when ambiguous. Inflections of a small documented set of verified dictionary mistakes are exceptions, including `зявився` and `зєднанням`.
- Uses explicit no-apostrophe examples and their dictionary lemmas ahead of dictionary acceptance: the dictionary incorrectly recognizes spellings such as `духмʼяний` and `бʼюджет`. Lexical coverage is limited to the installed dictionary and documented overrides, rather than a complete normative spelling dictionary.
- Suggestions preserve the word's case and existing apostrophe style; insertions in words without an apostrophe use `ʼ`. At most five compound suggestions are shown. Corrections are advisory and never rewrite source text.

The single cached `pymorphy3` Ukrainian analyzer receives lowercase, NFC-normalized words with ASCII apostrophes. The first parser-ranked morphology result is displayed; ties keep the parser's ordering. This is dictionary-based analysis without sentence-context disambiguation, general spelling correction, or a guarantee of linguistic correctness. Unfamiliar words with plausible apostrophe placement remain eligible for analysis and may receive a result labeled **Прогноз** (prediction). **Зі словника** denotes a dictionary match; **Невідомо** means no usable analysis. Missing grammatical features remain blank, and parser errors preserve the detected word with **Помилка аналізу**. Disabling morphology skips grammatical output; dictionary checks still run so spelling results remain identical. If the dictionary fails, deterministic placement checks continue, while unsupported lexical judgments and suggestions are skipped.

## Architecture

The root `main.py` configures logging, creates the interface, and launches the local Gradio server with public sharing. The flat `src` package uses plain functions: `textEval` handles detection and orchestration, `apostropheEval` checks rules and builds suggestions, `morphEval` handles normalization and dictionary access, `textSamples` lists and loads sample files, and `UIgradio` creates the interface and formats results. The code uses explicit loops and conditions. The morphology parser is created on first use and stored in a module variable for reuse; failed initialization can be retried. Dictionary evidence is reused within a submission. The UI stores no analysis state; Analyze and sample loading update their output components directly.

`textEval.analyze_text(text, include_morphology = True)` returns a dictionary with `source_text`, `count`, `words`, and `issues`. Accepted occurrences have `word`, `start`, `end`, and `morphology`; morphology is `None` when disabled, otherwise a dictionary with `status`, `lemma`, `part_of_speech`, and `features`. Each issue has `word`, `start`, `end`, an error `code`, and a `suggestions` list. `textEval.find_apostrophe_words()` returns accepted occurrences without morphology. Offsets use Python string indices, with an exclusive end. `format_result(result)` and `handle_analyze(text, include_morphology)` return `(message, rows, spans, issue_count, issue_rows)`. `load_sample(filename)` returns `(text, message, rows, spans, issue_count, issue_rows)`: successful loading clears results; a missing selection or loading failure returns six Gradio skip updates to preserve existing values. Importing modules never launches a server.

## Tests and examples

```bash
uv run pytest
```

The suite has 14 focused tests covering detection and offsets, representative apostrophe rules and corrections, a real Ukrainian dictionary result, normalization, validation, the morphology toggle, Ukrainian UI output, and sample loading. Detailed edge cases and failure variants are not covered exhaustively.

Choose a filename from **Тестовий текст** above the input box to load a UTF-8 file from `test_data`. Loading clears earlier results and messages but preserves the morphology setting. You can edit the loaded text and then press **Аналізувати**; the original file is never modified. If a file cannot be read, a Ukrainian warning appears and the current input and results are kept.

The six samples include short examples and longer texts: `text_01.txt` contains prose, `text_02.txt` demonstrates apostrophe styles and compounds, and `text_03.txt` exercises unusual and malformed input, unnecessary apostrophes, omissions, and ambiguous valid spellings.

Dependencies are declared in `pyproject.toml`; `uv.lock` records reproducible versions. Update them with uv rather than editing the lockfile manually. This version includes no custom REST API, permanent hosting configuration, or GitHub Actions workflow.

The sample list is discovered when the app starts; restart after adding a `.txt` file. Pytest discovers all samples and compares their exact detected word order against the reviewed lists in `tests/data/expected_words.json`, analyzing each file once with morphology disabled. Add a reviewed expectation for each new file; missing expectations or an empty sample folder fail test collection clearly. Sample tests also check loading outside the project directory, clearing results, and handling a missing file. Morphology settings, Ukrainian output, and highlighting are checked separately in the core and UI tests. Run the sample tests with `uv run pytest tests/test_samples.py -v`.
