# Change log

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
