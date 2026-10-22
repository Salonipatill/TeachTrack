# Current features and recent changes

Updated 22 October 2026. This describes the current repository, not proof that an
older Vercel deployment serves the same commit.

## Accounts and profiles

- Students, faculty and directors open My profile by clicking their name/role in
  the sidebar footer. The route is `/accounts/profile/`.
- Name, username, email, department and phone are editable for the signed-in user.
  Students additionally edit enrollment, year, semester, section and batch.
- Updates synchronize the linked Student/Faculty/Director and complaint-wrapper
  names. Role, administrator flags and another user's identity cannot be edited
  through this form. Duplicate usernames/emails produce validation errors.
- Email/SMS OTP, Forgot password pages, public reset links, Gmail SMTP settings
  and the temporary check_email command have been removed. Outbound email uses
  Django's dummy backend. Signed-in password change still requires the old password.

## Quizzes

- Creation shows title, subject, launch time, deadline and the question builder.
  Publication and the four identity requirements are applied automatically.
  Publication can still be changed by the existing authorized toggle.
- Each question starts with four options and supports 2–26 options (A–Z). Use
  **Add option** or **Remove last option** to adjust the count; removed options
  are also removed from the selected correct answers. Every visible option needs text.
- Tick every correct answer. Selecting more than one automatically enables
  **Allow multiple correct options**. Turning that setting off keeps only the
  first selected correct answer. The server validates answer membership and
  requires exactly one answer for single-choice questions. Multiple-choice
  attempts earn the point only when the selected set exactly matches the correct set.
- Student attempts autofill name, enrollment and email from the account. Course,
  year, semester, section and batch have separate inputs, with existing values
  prefilled. Missing details can be completed before submission.
- Launch date/time and submission deadline are labelled explicitly in IST.
- Question numbers sit inside each card above the question. Panels and long
  options wrap within the form width.
- Results show score, an IST submission timestamp and an academic-detail grid
  that adapts to smaller screens. Answers remain hidden from students until close.
- Migration 0010 adds Student.batch and Submission.academic_details. The JSON
  snapshot preserves separate values; the older class_div field remains as a
  compatibility summary. Old attempts are not backfilled with guessed data.

## Shared website behavior

- TeachTrack logos open the public Home page, including after sign-in.
- Signed-in users see **WORKSPACE**, linking to their dashboard, on Features,
  Campus life and Contact. Features is the `/#features` view of Home; JavaScript
  follows hash changes to show the button there and hide it on the main Home view.
  Anonymous visitors retain Sign in/Get started navigation.
- Campus life opens the internal `/campus-life/` page. Its descriptions no longer
  link to Aurobindo's official website. **View location on Google Maps** in
  **Find us in Indore** opens a search for Sri Aurobindo Institute of Technology,
  Indore, Madhya Pradesh in a new tab. Telephone/email contact links remain.
- Sun/moon button at bottom-right on public, login and dashboard pages. The choice
  persists in browser local storage, syncs across tabs, and initially follows the
  device theme. Restricted local storage does not break the current page.
- Contact uses the public header/footer and navigation. Messages are saved in
  Contact and visible to authorized Django administrators, not role dashboards;
  submitting the form does not send email.
- Keyboard skip link, visible focus, reduced-motion support, clearer text contrast,
  mobile controls and explicit form actions are shared by current templates.
- Form navigation shows progress and prevents duplicate submissions. Image decoding
  is asynchronous; secondary campus photos retain lazy loading and image dimensions.

## Resource uploads and custom categories

- Faculty and directors can upload PDF, UTF-8 TXT, DOCX, PPTX, JPG/JPEG and PNG
  resources. Image content is verified with Pillow; an image filename alone is
  insufficient. Downloads remain authenticated.
- The per-file limit is **30 MB** (30 × 1,024 × 1,024 bytes). The declared request
  limit is **32 MB**, including multipart/form data and all files combined; adding
  several individually valid files can still exceed that total.
- Choose **+ Add custom category** in the upload form, then enter a name of up to
  100 characters. Saving a resource makes its category available in future uploads
  and library filters. Extra whitespace is collapsed, and names matching existing
  category values/labels are reused case-insensitively. Notes, PYQs and Assignments
  remain available.
- Migration **0011_resource_custom_category** widens the indexed Resource.category
  field to 100 characters and removes the fixed model choices; existing category
  values remain unchanged. Apply `manage.py migrate` to the intended database.

## Database and storage

- Aiven MySQL uses mysql.connector.django and the committed public CA certificate;
  credentials remain private. Local MySQL can explicitly disable SSL; other MySQL servers can use custom CA/client certificates. Timeouts, connection reuse and health checks are configurable. PostgreSQL and local SQLite remain supported.
- Vercel-provided deployment, production and branch hostnames are added to host
  and CSRF-origin lists. No global wildcard is required.
- **UPLOAD_STORAGE=local** saves uploaded files under `media/` without Google
  Cloud, independently of DEBUG and the database engine. PC MySQL stores the
  file metadata; local storage keeps the bytes. Back up both database and media.
- **UPLOAD_STORAGE=auto** is the default: use GCS if GS_BUCKET_NAME is set;
  otherwise use local files with DEBUG=True and disable uploads with DEBUG=False.
  **gcs** explicitly requires a bucket, while **disabled** rejects file uploads
  at the form, request and storage layers. Text workflows remain available.
  Persistent local disk is required when explicitly using local storage on a host.
  There is no Supabase integration yet.
- Local `manage.py runserver` loads the selected TEACHTRACK_ENV_FILE (default .env) with override enabled. Other commands and
  deployed WSGI/ASGI use normal process-environment precedence.

## Verification record

### Shared resource downloads

Migration 0012 adds ResourceFile, a private database copy of a locally uploaded
resource. When the filesystem file is missing on another instance, the existing
authenticated download view serves the matching database copy. Downloads retain
the original filename and normal count/history behavior. A copy for a different
file key is never served. File bytes stay out of resource list-page queries.

New local resource uploads preserve their copy automatically. For an existing
resource, run `python manage.py preserve_resource_files --resource-id ID` for a
dry-run on the machine holding the file; add `--apply` to save its database copy.
This command does not recreate an unavailable original or publish a public URL.
The Vercel code must be redeployed to use the fallback. Host-specific transfer
limits still apply even though the application accepts 30 MB files locally.

### Current download-fix verification

All 94 tests passed on isolated SQLite (34.533 seconds, fast test-only password
hasher) and disposable MySQL 8.0.46 (47.381 seconds). The four new cases cover
missing local files, disabled storage, stale file-key copies and preservation
commands. Migration 0012 and the approved existing-image copy are prepared for
the deployed app; the new download view requires a code redeploy.

### Earlier full verification

All 90 automated tests passed on both isolated SQLite and disposable MySQL 8.0.46
on 22 October 2026. Six new regression cases cover current navigation, Maps,
26-option quizzes, exact-size image uploads and extra-wrong-answer scoring.
Two redundant test-only streaming-response closes were removed after the first
MySQL run exposed them. Offline Edge checks passed 59 assertions across
1440/768/390/360px using rendered templates and local assets; the Maps target was
intercepted. No deployed application or existing application database was changed.

Detailed results and limits belong in [TESTING.md](TESTING.md), and discovered
cases are listed in [TEST_CATALOGUE.md](TEST_CATALOGUE.md). Database verification
is recorded in [DATABASE_SETUP.md](DATABASE_SETUP.md). Earlier local Edge checks
covered public pages at 390/768/1440 pixels, role navigation, faculty creation,
quiz autofill/submission/results, keyboard access and actual dark colours.
Current system, migration-drift, dependency, Python/JavaScript syntax and synthetic
production-configuration checks passed. Static collection is a historical review
result. The saved PC MySQL login still returns error 1045 and requires valid local
credentials. These observations do not certify a protected live Vercel site,
all browser engines, external content, production load or a bug-free application.
