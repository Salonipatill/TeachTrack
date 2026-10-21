# Changes to the uploaded original

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
