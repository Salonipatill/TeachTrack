# TeachTrack

TeachTrack is a Django academic workspace for **students, faculty and directors**. It includes a public campus website, private resource library, quizzes, announcements, notifications, doubts, faculty feedback, complaints and director reporting.

## Complete documentation

**[Open the project handbook](docs/PROJECT_DOCUMENTATION.md)** or **[open the offline illustrated handbook](docs/TEACHTRACK_DOCUMENTATION.html)**. A printable snapshot is available at [TEACHTRACK_DOCUMENTATION.pdf](docs/TEACHTRACK_DOCUMENTATION.pdf).

| Reference | Contents |
| --- | --- |
| [Documentation index](docs/README.md) | Organized reading guide and all companion documents |
| [Project handbook](docs/PROJECT_DOCUMENTATION.md) | Setup, architecture, files, roles, every workflow, security, commands, operations and troubleshooting |
| [Design system](docs/DESIGN_SYSTEM.md) | Colour tokens/RGB, typography, spacing, component states, breakpoints and image index |
| [Complete colour index](docs/COLOUR_INDEX.md) | Every explicit active-stylesheet colour, opacity and selector/property usage |
| [Database reference](docs/DATABASE_REFERENCE.md) | All 24 project models, fields, defaults, relations, constraints and indexes |
| [Forms reference](docs/FORM_REFERENCE.md) | Every active form field, role variation and validation rule |
| [Route reference](docs/ROUTE_REFERENCE.md) | Current/original URL names, methods, access rules and query parameters |
| [Configuration reference](docs/CONFIGURATION_REFERENCE.md) | Every project environment variable and important fixed Django settings |
| [Testing guide](docs/TESTING.md) | Verification procedure and current test coverage |

## Run this existing Windows workspace

From the folder containing manage.py, keep your existing .env and virtual environment:

```powershell
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Open **http://127.0.0.1:8000/**. The local DEBUG override prevents an inherited IDE value from unintentionally enabling production mode. Configuration loading and precedence are explained in the handbook.

For a new installation, follow [handbook section 4](docs/PROJECT_DOCUMENTATION.md#4-installation-and-local-startup). The container baseline is Python 3.12; the existing workspace has also been exercised with Python 3.14.5. Install requirements using the same interpreter that runs manage.py. MySQL users additionally need requirements-mysql.txt.

Before migrating a populated original database, follow [UPGRADE.md](docs/UPGRADE.md). An existing database is not replaced by these startup commands. Blank DATABASE_URL selects db.sqlite3; a configured URL can select MySQL or PostgreSQL.

## Accounts and login

Login uses your **Django username**, rather than your email address. Role pages are available at `/student-login/`, `/faculty-login/` and `/director-login/`; the shared route is `/accounts/login/`.

Create the first director with a privately entered password:

```powershell
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe manage.py create_director --username director --email director@example.com --name "Campus Director"
```

There is no default password. An existing director creates faculty or additional director accounts through **Manage accounts → Create account**. Public registration creates students only. Enrollment, year, semester and section belong to student forms; faculty/director forms use staff details. Django superuser administration is separate from application director access.

## Source map

- `Classroom/`: settings, root routing and WSGI/ASGI entry points.
- `ClassApp/`: academic models, forms, views, authorization, services and tests.
- `ClassApp/Templates/`: current shared templates and retained original templates.
- `ClassApp/static/ClassApp/`: active CSS and vanilla JavaScript.
- `ClassApp/static/img/`: source campus images; `staticfiles/` is generated output.
- `docs/`: full handbook, references and operations guides.
- `tools/build_documentation.py`: reproducible documentation/reference builder.

## Verification and deployment

```powershell
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe tools/build_documentation.py
```

Use the [isolated test procedure](docs/TESTING.md) for the 53-test suite. The project includes a [Google Cloud deployment guide](docs/DEPLOYMENT.md); cloud resources, credentials, SMTP and production acceptance remain environment-specific. [Campus image/content sources](docs/CAMPUS_CONTENT.md) and the [original README](docs/ORIGINAL_README.md) are preserved.

Created for the TeachTrack academic workspace by **Zaman & Saloni**.
