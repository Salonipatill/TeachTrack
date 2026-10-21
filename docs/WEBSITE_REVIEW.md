# Website quality review — 21 October 2026

This review covers the checked-out source and an isolated local installation. It
does not certify the protected Vercel deployment or change Aiven records.

| Area | Implementation and verification |
| --- | --- |
| Clear purpose | Homepage explains resources, quizzes and campus conversations, with role-based sign-in links. Added a shared page description. |
| Consistent design | Shared stylesheet, templates, form controls, spacing and persistent light/dark themes. Quiz question numbering and result detail grid are shared components. |
| Mobile layouts | Real headless Edge checks at 390, 768 and 1440 pixels: public pages had no horizontal overflow. Added mobile form and toolbar improvements. |
| Loading | Existing lazy-loaded secondary campus images, explicit image dimensions, compressed static storage and deferred application JavaScript. Added asynchronous image decoding. No production latency or load benchmark was performed. |
| Navigation | Role-based menus, public navigation, profile link, current-page indicators and a keyboard skip link. |
| Readability | Improved shared muted-text contrast, explicit date labels, individual student academic fields and clear account headings. |
| Features | All 57 Django tests pass. Browser flows additionally verified role login, module navigation, student quiz submission and director creating a faculty account. |
| Actions | Existing named action buttons retained. Submission and search buttons now provide progress feedback and guard against duplicate submissions. |
| Feedback | Existing validation/success/error messages retained. Added busy states and clear unavailable-upload messages before submission. |
| Accessibility | Skip-to-content works by keyboard, focus outlines exist, theme button has accessible state/name, images have descriptive alternatives, reduced-motion preferences are respected. This is not a complete WCAG certification. |
| Security | Production Django deployment checks pass. Existing TLS, CSRF, secure cookies, role restrictions, password hashing and Aiven certificate verification retained. Vercel defaults to debug off unless explicitly configured otherwise. |
| Relevant features | Academic workspace features retained. Uploads remain unavailable in production without persistent storage, with an explanatory message. |
| Browser compatibility | Headless installed Microsoft Edge verified; responsive CSS and native form controls used. Firefox and Safari were not executed. |
| Content and links | Local route/render coverage comes from the suite and browser checks. Added favicon. External institutional facts and third-party link availability need periodic owner review. |
| Maintenance | This record distinguishes verified checks from remaining operational checks. See the commands below and the existing testing/deployment documentation. |

## Checks before deployment

Use the project virtual environment. For automated tests, explicitly select an
isolated database; do not run the suite against the production database.

```powershell
$env:DEBUG = 'True'
$env:DATABASE_URL = 'sqlite:///:memory:'
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
node --check ClassApp/static/ClassApp/app.js
node --check ClassApp/static/ClassApp/theme.js
```

These environment overrides apply to that terminal; close it before resuming
normal database work. Browser checks used temporary local accounts and databases,
not production credentials. Playwright was installed locally as an audit tool;
it is not a runtime dependency.

For a production configuration, also run `manage.py check --deploy` and collect
static assets. Confirm Vercel serves the intended commit, and test its actual
production URL after deployment. A successful GitHub push alone does not verify
the live site.

## Remaining operational checks

- Keep `DEBUG=False` on Vercel and use the intended database and allowed domains.
- Check the deployed site's theme assets, login, faculty creation, quiz attempt,
  result layout and mobile navigation after publishing.
- Configure SMTP before relying on delivered password-reset emails; the local
  console email backend does not deliver mail.
- Configure persistent private storage before enabling uploads.
- Recheck Safari/Firefox, real mobile devices, external campus links and production
  performance separately. Deployment protection prevented independent live inspection.
