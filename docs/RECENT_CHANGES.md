# Current features and recent changes

Updated 21 October 2026. This describes the current repository, not proof that an
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

## Production and storage

- Aiven MySQL uses mysql.connector.django and the committed public CA certificate;
  credentials remain private. PostgreSQL and local SQLite remain supported.
- Vercel-provided deployment, production and branch hostnames are added to host
  and CSRF-origin lists. No global wildcard is required.
- A GCS bucket is optional for startup. In production without a bucket, file
  uploads are disabled at the form, request and storage layers; text workflows
  remain available. There is no Supabase integration yet.
- Local `manage.py runserver` loads .env with override enabled. Other commands and
  deployed WSGI/ASGI use normal process-environment precedence.

## Verification record

The latest feature-removal run passed 57 Django tests. Earlier local Edge checks
covered public pages at 390/768/1440 pixels, role navigation, faculty creation,
quiz autofill/submission/results, keyboard access and actual dark colours.
Production checks, static collection and dependency checks passed during the
quality review. These observations do not certify a protected live Vercel site,
all browser engines, external content, production load or a bug-free application.
