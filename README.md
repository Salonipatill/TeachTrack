# TeachTrack

TeachTrack is a Django academic workspace for **students, faculty and directors**.
It brings quizzes, resources, announcements, notifications, doubts, feedback,
complaints and director reporting into one campus website.

## Current features

- Public home, campus and Contact pages with shared navigation/header/footer.
- The TeachTrack logo opens Home. Signed-in users get a **WORKSPACE** dashboard
  shortcut on Features (`/#features`), Campus life and Contact; it is hidden on
  the main Home view. Campus life stays within TeachTrack and offers a Google
  Maps location search for Sri Aurobindo Institute of Technology, Indore.
- Separate role sign-in pages; login uses a **username**, not an email address.
- **My profile**: click the name/role in the sidebar footer to correct your own
  account details. Students also manage enrollment, year, semester, section and batch.
- Quiz creation automatically applies publication/identity defaults. Student
  attempts autofill account details and show academic fields separately.
- Each quiz question supports **2–26 options** with Add option/Remove last option
  controls and one or more correct answers. Selecting multiple correct answers
  enables multiple-answer mode; grading requires the exact correct set.
- Resource uploads accept PDF, TXT, DOCX, PPTX, JPG/JPEG and PNG up to **30 MB**
  per file, within a **32 MB** total request limit. Staff can add custom resource
  categories of up to 100 characters and reuse them in uploads and filters.
- Explicit quiz launch/deadline and submission timestamps in IST, question numbers
  inside cards, scoring, delayed answer reviews and responsive result details.
- Persistent light/dark mode on shared pages, mobile navigation, keyboard skip
  links, reduced-motion support and submit/search progress feedback.
- Director account management/reporting and role/object authorization.

**Current limits:** Public password reset, email/SMS OTP and SMTP sending are
removed. Signed-in users can still change their password using the old password.
Upload storage can be local, GCS, disabled or chosen automatically; local files
work with PC MySQL without Google Cloud. Contact submissions are stored in the database and visible in
Django admin, with no automatic email or director-dashboard inbox.

## Run locally on Windows

From the folder containing manage.py, keep your existing private .env and environment:

```powershell
cd "C:\Users\Zamanuddin Khan\Downloads\Coding Area\TeachTrack"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Local runserver loads the selected environment file with override enabled. Set TEACHTRACK_ENV_FILE to choose a private file such as .env.local-mysql; it defaults to .env. Other
commands and deployed entry points give process environment variables precedence.
For a new setup, copy .env.example to .env and fill private values. Never commit
.env, passwords, private keys or database dumps.

Blank DATABASE_URL selects local SQLite. PostgreSQL and MySQL Connector are in the
main requirements. Both local MySQL and Aiven use mysql.connector.django. SSL is configurable: MYSQL_SSL_MODE=DISABLED for trusted local development, or VERIFY_IDENTITY (the default) for Aiven with MYSQL_SSL_CA=certs/aiven-ca.pem. See [database setup](docs/DATABASE_SETUP.md) for environment examples and isolated verification.
requirements-mysql.txt is retained as a compatibility include of the main set.
Before upgrading a populated original database, follow [UPGRADE.md](docs/UPGRADE.md).
Migration 0010 adds batch and separate quiz academic snapshots; it does not guess
missing historical values. Migration 0011 enables custom resource categories while
retaining existing values. Schema migrations do not transfer data between engines.

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
$env:TEACHTRACK_ENV_FILE = '.env.isolated-tests-unused'
$env:SECRET_KEY = 'test-only-isolated-suite-secret-22-October-2026'
$env:UPLOAD_STORAGE = 'local'
$env:GS_BUCKET_NAME = ''
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

See [testing](docs/TESTING.md) for current verification results and the
[test catalogue](docs/TEST_CATALOGUE.md) for all discovered test methods. Historical
database checks are recorded in [database verification](docs/DATABASE_SETUP.md#historical-verification-record-21-october-2026).
Earlier local Edge checks covered
public mobile/tablet/desktop pages, role navigation, faculty creation, quiz attempts,
result layouts, keyboard navigation and actual dark colours. This is not a claim
of zero bugs or independent verification of protected Vercel deployments,
Safari/Firefox, external content or production load.

## Deploy

See [Vercel + Aiven](docs/VERCEL_DEPLOYMENT.md) for current environment variables,
certificate/migration requirements and deployed-commit troubleshooting. The
[Google Cloud guide](docs/DEPLOYMENT.md) covers the optional container/GCS route.
Set DEBUG=False and a private SECRET_KEY in production. For PC MySQL, set
UPLOAD_STORAGE=local to save notes and attachments in media/ without Google Cloud.
This explicitly selects local files independently of DEBUG and the database engine.
MySQL stores resource metadata, while media/ stores the file bytes. Back up both.
UPLOAD_STORAGE=auto selects GCS when GS_BUCKET_NAME is set; otherwise it selects
local files with DEBUG=True and disables uploads with DEBUG=False. Hosted services
without persistent disk should use GCS or disabled uploads; gcs requires a bucket.

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
