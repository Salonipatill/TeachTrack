# Website quality review - 22 October 2026

This review covers the checked-out source and isolated local verification. The
current ClassApp suite has **90 tests**, all passing on isolated SQLite and a
disposable local MySQL 8.0.46 server. The saved PC MySQL login still returns
**1045 (Access denied)**. This review does not certify the deployed Vercel website
or validate that saved account/password.

The current offline Edge/Playwright UI check also passed **59 assertions** at
1440/768/390/360 px using rendered templates, real JavaScript/CSS and synthetic
faculty/guest context. It does not start an app server, use a database or log in.
The Maps destination is intercepted and external network access is not used.

| Area | Implementation and verification |
| --- | --- |
| Public navigation | The logo targets Home. Signed-in users get WORKSPACE on Campus life/Contact; Home hides it initially and `/#features` uses JavaScript to reveal it. Guests get sign-in/registration links. Rendered navigation is tested. |
| Campus life | Campus life remains internal. The location button opens a Google Maps search for Sri Aurobindo Institute of Technology, Indore, with `noopener noreferrer`. Tests verify the target without contacting Google Maps. |
| Quizzes | Questions support 2-26 options and multiple correct answers. Tests cover boundaries, text/membership, single-choice validation and exact-set grading. |
| Resource uploads | Local mode saves private files under `media/` without Google Cloud. Documents and JPG/JPEG/PNG are accepted through 30 MB per file; valid boundary and invalid/oversized files are tested. MySQL stores paths/metadata. |
| Categories | Staff can add custom categories and reuse them in uploads/filters. Tests cover normalization, existing names, blank/reserved values and the 100-character limit. |
| Accounts/access | Tests cover role dashboards, profiles, role injection, private files, CSRF, sessions and password changes. This is not an independent security audit. |
| Academic workflows | Announcements, quizzes, complaints, doubts, feedback, notifications and reports are covered, including original tables and legacy migration relationships. |
| Design/accessibility | Shared themes, responsive styles, skip links, focus states, image alternatives and reduced-motion rules are implemented. Historical Edge checks covered keyboard access/theme persistence. No complete WCAG review was performed. |
| Mobile layouts | Current offline UI assertions run at 1440/768/390/360 px. Earlier live-local Edge checks also covered narrow campus layouts. These do not establish real-device or production behavior. |
| Storage/deployment | `UPLOAD_STORAGE=local` supports PCs/persistent writable disks. Hosted uploads need persistent storage; Vercel's filesystem does not preserve them. Behavior depends on configuration. |
| Browsers | Current offline installed Edge checks cover option controls, multi-answer behavior, removed-answer cleanup, add-question, custom categories/limits, 30 MB help and header/hash navigation. Firefox/Safari and real mobile devices were not run. |
| Loading/performance | Local images, dimensions/lazy loading, compressed static storage and deferred JavaScript are implemented. Production latency/load benchmarks were not performed. |
| Content | Institutional details are local content. External link availability and campus facts need periodic owner review. |

## Repeatable checks before deployment

Use a separate terminal and isolated environment from [TESTING.md](TESTING.md):

```powershell
.\.venv\Scripts\python.exe manage.py test ClassApp --noinput
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe tools/check_feature_ui.py
.\.venv\Scripts\python.exe -m compileall -q ClassApp Classroom tools
node --check ClassApp/static/ClassApp/app.js
node --check ClassApp/static/ClassApp/theme.js
```

The isolated environment is required: a default terminal may select a configured
MySQL server. Database engine checks use the disposable-server helper documented
there. Documentation generation, PDF export and link checking are separate checks.

For production, run deployment checks with explicit production settings, collect
static files and verify the actual release after deployment. Source checks or a
Git push do not verify the live website.

The dependency, Django system, migration-drift, JavaScript syntax and Python
compilation checks passed on 22 October. A production deployment check passed
using synthetic configuration only; no deployment or database connection was
performed by that check.

## Remaining acceptance and operational checks

- Recheck release navigation, WORKSPACE visibility, mobile layout, theme assets
  and the Maps destination.
- Verify actual local MySQL credentials separately; engine compatibility does not
  validate the PC service's account/password.
- Check persistent private storage, backups, 30 MB ingress limits and cloud
  permissions on the deployment platform.
- Check deployed login, faculty creation, resource upload/download, custom
  categories, quiz option controls, student attempts and results.
- Recheck Firefox/Safari, real devices, keyboard access and performance.
- Keep production debug disabled and use the intended database/allowed hosts.
  Public email password resets remain removed; signed-in users can use Password.

See [TESTING.md](TESTING.md) for exact dated results and their limits.
