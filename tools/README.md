# Documentation tools

Run commands from the TeachTrack folder using its virtual environment:

```powershell
.\.venv\Scripts\python.exe tools/build_documentation.py
.\.venv\Scripts\python.exe tools/export_documentation_pdf.py
.\.venv\Scripts\python.exe tools/check_documentation.py
```

`build_documentation.py` forces an isolated in-memory SQLite configuration and a
build-only secret. It inspects models, URLs, unbound form variants and source test
methods; it does not migrate or query account data. It rebuilds the database,
form, route, test and colour references, diagrams, JSON colour inventory and offline
HTML handbook. Both `app.css` and `theme.css` are included, retaining token selector
scope so light and dark definitions are distinguishable.

`export_documentation_pdf.py` prints the rebuilt HTML to the existing PDF using
Playwright and an installed Edge/Chromium browser. It blocks external HTTP requests
and never starts Django or connects to Aiven. Playwright is an optional local
documentation dependency, not a production dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
# If Edge is not installed, install a local Chromium browser:
.\.venv\Scripts\python.exe -m playwright install chromium
```

An explicit executable is supported with `--browser-executable PATH`.

`check_documentation.py` checks maintained Markdown/HTML links and generated
profile/reset references. It excludes the historical ORIGINAL_README.md. It does
not check external URLs or claim a production deployment is healthy.

Authored chapters must be edited before rebuilding: PROJECT_DOCUMENTATION.md,
DESIGN_SYSTEM.md, CONFIGURATION_REFERENCE.md, RECENT_CHANGES.md, deployment guides
and test/review notes. Generated files should be refreshed through the builder
rather than edited directly. Re-export the PDF after any handbook change.
