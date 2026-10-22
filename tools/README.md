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
profile/reset and current feature references, and compares the generated test
catalogue count with source discovery. It excludes the historical ORIGINAL_README.md. It does
not check external URLs or claim a production deployment is healthy.

## Offline feature browser checks

```powershell
.\.venv\Scripts\python.exe tools/check_feature_ui.py
```

This optional Playwright/Edge check renders current templates with synthetic
faculty/guest context and serves their real local CSS/JavaScript through
intercepted browser requests. It verifies Home/Features WORKSPACE visibility,
Campus life/Contact navigation, the institute's Maps link, 2-26 quiz options,
multiple answers, new question controls, custom category input and upload help
at desktop/mobile widths. All external requests are blocked or intercepted,
including the Maps destination. It does not start Django's server, submit forms,
query account data or test live deployment/Google Maps behavior. Server-side
form, database and scoring behavior belongs to the full application test suite.
Use `--browser-executable PATH` for another installed Chromium browser.

## Real HTTP workflow browser checks

```powershell
.\.venv\Scripts\python.exe tools/check_workflows_ui.py
```

This optional Edge/Playwright check starts a disposable Django test server with
an isolated SQLite database, synthetic accounts for every role, and temporary
media under the checked workspace cache. It submits real CSRF-protected forms:
login/registration, image upload/custom category, download without the local
file, single/multiple-answer quizzes, feedback, doubts, complaints/resolution,
announcements, notifications, director account creation/deactivation, CSV exports,
profiles and password change. It also checks mobile module navigation. All
external browser requests are blocked. ORM reads use a dedicated synchronous
thread rather than disabling Django's async-safety checks.

The test server, database, users and media are temporary. The command does not
log into the live site, use saved database credentials or create live records.
Requires installed Microsoft Edge and Playwright. This is a separate browser
workflow test, in addition to the ClassApp test catalogue and offline UI check.

Authored chapters must be edited before rebuilding: PROJECT_DOCUMENTATION.md,
DESIGN_SYSTEM.md, CONFIGURATION_REFERENCE.md, RECENT_CHANGES.md, deployment guides
and test/review notes. Generated files should be refreshed through the builder
rather than edited directly. Re-export the PDF after any handbook change.

## MySQL verification

`python tools/verify_mysql.py --env-file .env.local-mysql` checks the selected
MySQL connection and reports whether TLS is active without showing credentials.
Use `--run-tests` only with permission to create/drop a unique temporary database.
It runs the complete ClassApp suite in a randomly named test_teachtrack_ database,
not the application's database. The account needs CREATE/DROP DATABASE permission.
See [database setup](../docs/DATABASE_SETUP.md). No fixed test database is reused.

A disposable local server can be used without knowing the credentials of an
existing MySQL service:

```powershell
.\.venv\Scripts\python.exe tools/verify_local_mysql.py --server-executable "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
```

This initializes a temporary data directory and starts MySQL on a random loopback
port with SSL disabled, runs the isolated suite, shuts down only that owned server,
and removes temporary data. It does not use the PC service's data directory or
change its accounts. Requires a compatible installed MySQL server executable.
