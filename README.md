# TeachTrack

TeachTrack is a Django academic workspace for **students, faculty and directors**.
It brings quizzes, resources, announcements, notifications, doubts, feedback,
complaints and director reporting into one campus website.

## Current features

- Public home, campus and Contact pages with shared navigation/header/footer.
- Separate role sign-in pages; login uses a **username**, not an email address.
- **My profile**: click the name/role in the sidebar footer to correct your own
  account details. Students also manage enrollment, year, semester, section and batch.
- Quiz creation automatically applies publication/identity defaults. Student
  attempts autofill account details and show academic fields separately.
- Explicit quiz launch/deadline and submission timestamps in IST, question numbers
  inside cards, scoring, delayed answer reviews and responsive result details.
- Persistent light/dark mode on shared pages, mobile navigation, keyboard skip
  links, reduced-motion support and submit/search progress feedback.
- Director account management/reporting and role/object authorization.

**Current limits:** Public password reset, email/SMS OTP and SMTP sending are
removed. Signed-in users can still change their password using the old password.
Production uploads are disabled without persistent private storage; text workflows
remain available. Contact submissions are stored in the database and visible in
Django admin, with no automatic email or director-dashboard inbox.

## Run locally on Windows

From the folder containing manage.py, keep your existing private .env and environment:

```powershell
cd "C:\Users\Zamanuddin Khan\Downloads\Coding Area\TeachTrack"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Local runserver loads .env with override enabled. Other
commands and deployed entry points give process environment variables precedence.
For a new setup, copy .env.example to .env and fill private values. Never commit
.env, passwords, private keys or database dumps.

Blank DATABASE_URL selects local SQLite. PostgreSQL and MySQL Connector are in the
main requirements. Aiven MySQL uses mysql.connector.django, a matching public CA
certificate at certs/aiven-ca.pem and TLS certificate/hostname verification.
requirements-mysql.txt is retained as a compatibility include of the main set.
Before upgrading a populated original database, follow [UPGRADE.md](docs/UPGRADE.md).
Migration 0010 adds batch and separate quiz academic snapshots; it does not guess
missing historical values. Schema migrations do not transfer data between engines.

## Accounts

Create the first director with a privately entered password:

```powershell
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe manage.py create_director --username director --email director@example.com --name "Campus Director"
```

There is no default password. Directors create faculty/additional directors through
Manage accounts. Public registration creates students only. Application director
access does not automatically grant Django admin access. A trusted administrator
can use Django's interactive changepassword command for a forgotten password.

## Verify safely

Use a separate terminal for isolated tests; close it before resuming normal database work:

```powershell
$env:DEBUG = 'True'
$env:DATABASE_URL = 'sqlite:///:memory:'
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

The latest feature-removal run passed **57 tests**. Local Edge checks also covered
public mobile/tablet/desktop pages, role navigation, faculty creation, quiz attempts,
result layouts, keyboard navigation and actual dark colours. This is not a claim
of zero bugs or independent verification of protected Vercel deployments,
Safari/Firefox, external content or production load.

## Deploy

See [Vercel + Aiven](docs/VERCEL_DEPLOYMENT.md) for current environment variables,
certificate/migration requirements and deployed-commit troubleshooting. The
[Google Cloud guide](docs/DEPLOYMENT.md) covers the optional container/GCS route.
Set DEBUG=False and a private SECRET_KEY in production. A GCS bucket is optional
for startup; provision storage and credentials before enabling uploads.

After pushing, verify Vercel's active commit and open that deployment's Visit URL.
Test the actual site, theme assets, login, profile, quiz result and intended roles.
Local .env edits do not configure Vercel. Email environment variables are unused.

## Documentation and tools

Start with the [documentation index](docs/README.md), [current changes](docs/RECENT_CHANGES.md)
or [project handbook](docs/PROJECT_DOCUMENTATION.md). The [offline HTML handbook](docs/TEACHTRACK_DOCUMENTATION.html)
and [PDF](docs/TEACHTRACK_DOCUMENTATION.pdf) include the current references and diagrams.

```powershell
.\.venv\Scripts\python.exe tools/build_documentation.py
.\.venv\Scripts\python.exe tools/export_documentation_pdf.py
.\.venv\Scripts\python.exe tools/check_documentation.py
```

The builder uses isolated metadata, not live account rows. PDF export needs the
optional local Playwright/browser dependency. See [tools/README.md](tools/README.md)
for installation and maintenance steps.

## Source map

- Classroom/: settings, routing and deployment entry points.
- ClassApp/: models, forms, views, services, authorization, migrations and tests.
- ClassApp/Templates/: current shared templates and retained historical pages.
- ClassApp/static/ClassApp/: active app/theme CSS and JavaScript, favicon.
- ClassApp/static/img/: campus images; staticfiles/ is generated output.
- docs/: guides, generated references, diagrams and offline handbook.
- tools/: documentation builder, PDF exporter, link checks and usage guide.

Created for TeachTrack by **Zaman & Saloni**.
