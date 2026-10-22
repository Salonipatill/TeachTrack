# Testing and verification

Run from the TeachTrack folder using the project virtual environment. The current
source defines **116 test methods**, listed in [TEST_CATALOGUE.md](TEST_CATALOGUE.md).
Tests use a separate database, in-memory storage for most uploads and temporary
media directories for local-disk tests. Existing application data is not needed.

## Verification record: 22 October 2026

The complete final ClassApp suite passed on both database engines using Windows
and Python 3.14.5 from `.venv\Scripts\python.exe`:

| Database | Final result | Test runtime |
| --- | --- | --- |
| Isolated in-memory SQLite | 116/116 passed | 96.981 seconds |
| Disposable local MySQL 8.0.46, loopback, TLS disabled | 116/116 passed | 167.222 seconds |

Django's system check reported no issues in both runs. The unique MySQL test
database was destroyed, the owned MySQL process stopped, and the checked
workspace scratch directory removed. No existing local service data or
production records were modified. Expected Forbidden/Not Found logs come from
permission, CSRF and missing-file checks and are not test failures.

The first MySQL run exposed redundant `response.close()` calls after the test
client's streaming iterator had already closed two download responses. The
second close emitted request-finished cleanup again and invalidated MySQL's
test transaction, causing cascading connection errors. Removing those two
redundant test-only calls preserved automatic stream/file closure. Both complete
90-test suites passed after that correction. The subsequent resource-download
repair added four regression cases. Private Blob integration added 22 more;
the final 116-test suites above include all of them.
The SQLite rerun used a fast test-only password hasher; MySQL used normal settings.

Additional source checks passed: `pip check`, Django `check`,
`makemigrations --check --dry-run`, JavaScript syntax checks and
`python -m compileall -q ClassApp Classroom tools`. A synthetic production
`check --deploy --fail-level WARNING` passed with a placeholder PostgreSQL URL,
disabled uploads and fake host/secret; this did not connect to a database or
perform a deployment.

These results cover the checked-out source. They do not verify the deployed
website, configured PC MySQL credentials, Google Cloud permissions or production
records. Earlier cloud/browser records are historical and do not establish that
the current deployment was retested.

A separate read-only check of the saved PC MySQL configuration still returned
**1045 (Access denied)**. Update that local account/password before running the
application on the existing PC service. The disposable-server pass establishes
engine compatibility and does not fix or verify the configured credentials.

## Safe SQLite run

Use a fresh PowerShell terminal so these overrides stay separate from normal
local MySQL work. Select an intentionally nonexistent env file to avoid loading
private configuration:

```powershell
$env:TEACHTRACK_ENV_FILE = '.env.isolated-tests-unused'
$env:DATABASE_URL = 'sqlite:///:memory:'
$env:DEBUG = 'True'
$env:SECRET_KEY = 'test-only-isolated-suite-secret-for-22-October-2026'
$env:UPLOAD_STORAGE = 'local'
$env:GS_BUCKET_NAME = ''
.\.venv\Scripts\python.exe manage.py test ClassApp --noinput
```

Ensure `.env.isolated-tests-unused` does not exist. Close this terminal after the
run, or use the environment-restoring procedure in
[handbook section 15](PROJECT_DOCUMENTATION.md#15-testing-and-acceptance).
Use the same interpreter for Django and migration subprocesses.

## Resource download repair

Migration 0012 and ResourceFile preserve local resource bytes in the database.
New regression cases verify fallback when the local file is missing, downloads
with local storage disabled, rejection of a stored copy for a different file key,
and dry-run/apply behavior of the existing-file preservation command. Original
filename, authentication and download statistics remain covered. The database
repair for the reported existing image required explicit owner approval; code
redeployment is a separate operational action.

## Post-deployment workflow review (22 October 2026)

The full 94-test suites were repeated after deployment commit `2a42ed6` and
passed on both engines as recorded above. No application failure was found in
the exercised workflows. Additional checks passed:

- **139 real HTTP browser assertions** in one standalone workflow test, using
  a disposable Django test server and SQLite/media (60.242 seconds on the final rerun). The browser
  signed in as director, faculty and student and exercised real form submissions,
  authenticated downloads after removing their local file, quiz creation/grading,
  feedback, doubt replies, complaint resolution/history, announcements,
  notifications, account creation/deactivation, exports, profiles, registration,
  password change and mobile navigation. No live records were created.
- **59 offline feature UI assertions** across 1440/768/390/360px, using current
  templates, local assets and synthetic account context.
- **68 live read-only/public assertions** against the deployed site: public
  pages, authentication redirects, deployment status, theme persistence,
  carousel photos, all 13 campus images, Maps destination, mobile widths through
  320px and absence of browser JavaScript errors. No live form was submitted and
  no signed-in production workflow was performed.
- Dependency, Python/JavaScript syntax and documentation checks passed again.
- **16 private Blob browser assertions** passed in 30.468 seconds with a disposable
  loopback storage service, including private upload headers, a full 30 MiB direct
  upload/download, exact bytes, failure/retry and application bodies below 4 KB.
- The pushed Blob implementation commit `a951666` has a successful Vercel status;
  the public homepage returns 200 but still reports uploads disabled. The private
  store has not been connected/verified by this session. Final local documentation
  and private-header changes still need publishing with the intended release.

At the read-only live check, the page declared `data-uploads-enabled="false"`.
Private Vercel Blob direct uploads have since been implemented and tested in
isolated environments. Live activation still requires connecting a private store
and deploying this source; no live Blob credentials, uploads or downloads were
verified. Local uploads and preserved database-backed downloads remain supported.
The separate Blob browser workflow verifies 30 MiB direct upload/download and
failed-upload retry using a disposable loopback storage service, real Django
forms and CSRF. It does not prove Vercel account configuration. See
[deployment storage limits](VERCEL_DEPLOYMENT.md#files-and-email).

Repeat the isolated browser workflow check with:

```powershell
.\.venv\Scripts\python.exe tools/check_workflows_ui.py
```

## Automated coverage

- Role dashboards/modules, anonymous redirects, original role URLs, password
  hashing, role-injection rejection and director bootstrap.
- Login throttle/cooldown, CSRF, POST-only logout, password changes, removed public
  password-reset routes, deactivation and session revocation.
- Profile edits for all roles, duplicate account details, student academic fields
  and staff creation forms.
- Public headers: the logo targets Home; WORKSPACE targets the dashboard on
  Campus life/Contact and is initially hidden on Home. Features uses
  `/#features`; its visibility behavior also requires JavaScript browser checks.
- Campus life stays internal. Its Google Maps link names Sri Aurobindo Institute
  of Technology, Indore, and opens a separate tab.
- Resource upload/search/filter/download, private file access, download counts,
  unavailable files and absence of a public media route.
- Local notes without Google Cloud; PDF/TXT/DOCX/PPTX and JPG/JPEG/PNG validation;
  valid 30 MB text/PNG boundary uploads; oversized/invalid-file rejection.
  The code's per-file limit is 30 x 1024 x 1024 bytes.
- Custom categories, whitespace normalization, existing-name reuse,
  100-character validation and reuse in later uploads/library filters.
- Quiz creation with 2-26 options, minimum/maximum boundaries, required option
  text, removed-option rejection and single/multiple correct answers.
- Quiz timing/publication, required student details, option membership, exact-set
  multi-select scoring (missing or extra incorrect selections fail), duplicate
  attempts, ownership and delayed solutions.
- Original answer/detail tables, invalid legacy quizzes and original score URLs.
- Private notifications, mark-read actions, unsafe redirects and announcement
  audiences/documents.
- Complaint assignment/status/history, doubt reply permissions and private
  original attachments.
- Feedback/rating constraints, CSV ordering/formula protection, legacy importer
  dry runs/password hashing and removal of plaintext pw fields.

## MySQL verification

[Database setup](DATABASE_SETUP.md) describes configured-server connectivity and
the helper that creates a uniquely named temporary test database. For local
engine compatibility without PC service credentials:

```powershell
.\.venv\Scripts\python.exe tools/verify_local_mysql.py --server-executable "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
```

This helper uses `--no-defaults`, a temporary data directory, a random loopback
port, disabled MySQL X protocol/TLS and an owned server process. It supplies its
own connection file, creates/drops a unique `test_teachtrack_...` database, stops
that process and removes temporary files. It does not use the existing MySQL
service's data directory or configured credentials.

## Populated original-schema migration test

An isolated SQLite subprocess migrates to original schema 0006, populates legacy
students/faculty/directors, existing Django accounts, username conflicts,
question images/options, repeated submissions with answer/detail M2M relations,
repeated ratings, attachments, an announcement and a replied complaint. It applies
every current migration, including 0011, and verifies:

- Original IDs, relationships, file paths, images and selected answers remain.
- Legacy passwords become hashes; existing hashes work; conflicting legacy names
  do not take over Django users.
- Role profiles/logins and student academic fields remain usable.
- Repeated records remain stored; one newest record receives each unique
  authenticated link.
- Complaint text, teacher reply, status and timeline remain.
- Old sessions/OTPs are cleared and plaintext password columns are removed.

This historical upgrade regression remains on SQLite during a MySQL suite run.
A passing MySQL suite verifies current schema migrations/workflows; it does not
establish a populated production-MySQL upgrade rehearsal.

## Browser checks

The current offline Edge/Playwright check passed **59 assertions** at 1440, 768,
390 and 360 px:

```powershell
.\.venv\Scripts\python.exe tools/check_feature_ui.py
```

It renders the current templates with synthetic faculty/guest context and loads
the real application JavaScript/CSS. It checks the Home/Features/Campus
life/Contact logo and WORKSPACE behavior, hash navigation, the Maps link target,
2-26 quiz option controls, automatic multiple-answer selection, removed-answer
cleanup, adding a question, custom-category controls/100-character limit and
30 MB help text. Maps navigation is intercepted. No running application server,
database, real login or external network is used, so this complements the Django
suite without claiming deployed end-to-end acceptance.

Previous local Edge reviews covered public pages at 390/768/1440 px, role
navigation, faculty creation, quiz submission/results, keyboard access and theme
persistence. Earlier homepage/campus checks covered carousel controls, local
images and narrow layouts. These historical observations were not repeated as a
live HTTP audit in the 22 October automated suite. Firefox, Safari, real devices
and the protected live deployment require separate acceptance checks.

## Documentation checks

After editing authored documentation:

```powershell
.\.venv\Scripts\python.exe tools/build_documentation.py
.\.venv\Scripts\python.exe tools/export_documentation_pdf.py
.\.venv\Scripts\python.exe tools/check_documentation.py
```

The builder uses isolated SQLite and source metadata to rebuild references,
diagrams and the offline HTML handbook. It does not query user records or run
the suite. The exporter refreshes the PDF with a local browser while blocking
external HTTP. The checker validates local links, not external URLs. See
[tools/README.md](../tools/README.md).

## Manual acceptance and release checks

1. Check Home, `/#features`, Campus life and Contact as a guest and after login;
   follow the logo, WORKSPACE and campus Maps link.
2. Create test accounts for every role; check profiles, original role logins,
   deactivation and private access.
3. Upload documents/pictures through 30 MB, add/reuse custom categories and check
   filtering, downloads and counts. Back up media with the database.
4. Create quizzes with 2/26 options and multiple answers. Check option removal,
   student details, exact-set grading, duplicates and delayed review.
5. Exercise announcement documents, private doubts, feedback, complaint statuses,
   director reports and CSV exports.
6. Rehearse populated upgrades on a separate copy of the actual MySQL database;
   review migrated accounts, unlinked records and old media paths.
7. Extract release packages into a fresh directory; check migrations/drift, demo
   seeding, static collection and role logins on a new database. Synthetic
   production `check --deploy` checks configuration only.
8. After deployment, check the actual URL, intended database, static assets,
   HTTPS cookies, CSRF, health endpoint and persistent private storage.
9. Verify proxy body limits including streamed requests, cloud permissions,
   intended user-count load and login-throttle behavior behind the real proxy.
