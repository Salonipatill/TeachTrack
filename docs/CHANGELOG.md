# Change log

## 22 October 2026 - resource download persistence repair

- Added migration 0012 and ResourceFile to preserve a private database copy of
  locally uploaded resources. Authenticated downloads use the matching copy when
  another app instance lacks the filesystem file, without loading binary content
  in library list queries.
- Added `preserve_resource_files --resource-id ID` with explicit `--apply` for
  existing local files. Added four regressions; all 94 tests passed on isolated
  SQLite and disposable MySQL 8.0.46.
- Documented Vercel's separate payload limits and the redeployment required for
  the new download view. Recovery of an existing image used explicit owner approval.

## 22 October 2026 - quiz controls, public navigation and resource uploads

- Added Add option/Remove last option controls for 2–26 choices per quiz question,
  starting with four. Removed choices are cleared from the correct-answer list;
  server validation checks option bounds, text and correct-answer membership.
- Added correct-answer checkboxes and automatic multiple-answer mode when several
  answers are selected. Exact-set grading remains in place without partial marks.
- Linked TeachTrack logos to the public Home page. Signed-in WORKSPACE header
  shortcuts appear on Campus life, Contact and `/#features`, and remain hidden on
  the main Home view.
- Kept Campus life navigation inside TeachTrack and removed official-site links
  from its descriptions. Added a Google Maps place search for Sri Aurobindo
  Institute of Technology, Indore, to the Find us in Indore panel.
- Added UPLOAD_STORAGE=auto/local/gcs/disabled. Explicit local storage works with
  PC MySQL without Google Cloud, independently of DEBUG; metadata stays in SQL and
  file bytes stay under media/. Auto retains bucket/DEBUG-based selection.
- Enabled validated JPG/JPEG/PNG resource uploads alongside PDF, TXT, DOCX and
  PPTX. Raised the per-file limit to 30 MiB and the declared request cap to 32 MiB;
  the interface labels these as MB.
- Added + Add custom category to resource uploads. Names support up to 100
  characters, normalize whitespace, reuse existing names case-insensitively and
  appear in later uploads and library filters once saved on a resource.
- Added migration 0011_resource_custom_category to widen the indexed category
  field and remove fixed model choices while preserving existing values.
- Updated maintained feature documentation; current test results and verification
  limits are recorded in TESTING.md and the generated test catalogue.
- Added six regression cases; all 90 tests passed on SQLite and disposable
  MySQL 8.0.46. Removed two redundant streaming-response closes from the test
  harness that broke MySQL test-transaction cleanup. Offline feature UI checks
  passed 59 assertions at four desktop/mobile widths. No deployed service or
  existing application database was modified during this verification.

## Local MySQL and Aiven environment switching

- Extracted database configuration into Classroom/database.py with strict environment
  parsing and a backward-compatible verified Aiven TLS default.
- Added explicit SSL modes, CA/client certificate paths, Connector implementation,
  connection timeout/lifetime and health-check settings.
- Added TEACHTRACK_ENV_FILE for private environment selection; runserver retains its
  intentional override behavior for the selected file.
- Added 14 configuration/environment regression checks and isolated MySQL test tools.
- Local MySQL 8.0.46 passed all 71 tests with SSL disabled in a disposable instance.
  SQLite passed 71 tests, plus the focused post-correction checks. Aiven 8.4.11 workflow coverage and all 15 focused compatibility rechecks passed with TLS active; detailed run accounting is in DATABASE_SETUP.md.
- Corrected the rating CHECK-constraint test for Connector/Python's DatabaseError
  classification, asserting MySQL error 3819 rather than weakening the constraint.

## 21 October 2026 - current updates

- Added own profile editing for students, faculty and directors from the sidebar footer.
- Added student batch and separate quiz academic snapshots in migration 0010.
- Automatically publish newly created quizzes and require identity/course details;
  removed the old five checkbox settings from creation.
- Autofill student attempts; split course/year/semester/section/batch inputs;
  label launch/deadline and submission timestamps in IST.
- Moved question numbers inside cards and aligned result metadata in a responsive grid.
- Added persistent light/dark themes, keyboard skip navigation, reduced motion,
  form progress/duplicate-submit handling, mobile refinements and a favicon.
- Kept Contact inside the public header/footer; submissions remain database records.
- Configured MySQL Connector/Aiven TLS and included only the public CA certificate.
- Accept exact Vercel-supplied hostnames; production without a bucket starts with
  uploads disabled and explanatory feedback. Text workflows remain available.
- Removed public password reset/OTP pages, SMTP setup, email credentials and
  check_email. Signed-in password changes remain available.
- Updated authored/generated documentation, light/dark colour inventory, diagrams,
  HTML/PDF handbook, documentation checks and repeatable PDF export tooling.
- The latest feature-removal test run passed 57 tests; local Edge checks covered
  mobile/desktop layouts, role flows, themes, faculty creation and quiz submission.

The following section records the original upgrade work; it is historical and
must not be read as a list of current reset/email features.

## Original upgrade history


- Kept ClassApp/Classroom, all original academic model names and relationships, migrations 0001–0006, original static assets and media.
- Added migrations 0007–0009; these extend and convert existing tables instead of creating a replacement database model set.
- Replaced custom plaintext/session login with Django authentication. Added hashed account migration, password change/reset, role checks, object checks and login throttling.
- Removed hardcoded secret, database and SMTP configuration. Added .env.example, local secret generation, optional MySQL requirements, PostgreSQL and private cloud media support.
- Continued writing Quiz, Question, Option, Submission, SubmissionAnswer and SubmissionDetail. Added code, publication/dates, strict single/multiple-choice grading, delayed answer review and leaderboard.
- Added Resource, Download, Notification, Profile, ComplaintEvent and LoginThrottle models.
- Extended original Doubt with answers/student links and retained its attachments; extended Announcement while retaining documents.
- Extended original Rating instead of adding a separate feedback table. Added one authenticated rating per student/faculty pair and range validation.
- Integrated original Complaint/AuthenticatedStudent/Teacher records with Django login and a status timeline.
- Added modern pages, responsive CSS/JavaScript, private attachment endpoints, director exports and account management. Kept original URL names routed with secure behavior.
- Recovered img/about-shadow.png from the original collected static directory to fix manifest static collection. Other source assets remain available. Active pages do not depend on the old jQuery/Modernizr scripts.
- Excluded the supplied inconsistent empty SQLite file, bundled virtual environment, editor settings, generated staticfiles, caches, secrets and demo/test databases from the deliverable. Original media remains included.
- Added setup, upgrade, deployment, contribution and testing documentation.

The upload's first six migration files are byte-for-byte unchanged. Its database configuration pointed to MySQL; access to that external database was not available and no live MySQL/Google Cloud migration is claimed.
